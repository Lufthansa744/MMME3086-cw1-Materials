"""Convert the existing scientific SVG geometry/text to a vector PDF without data remapping.

Restricted to the actual SVG vocabulary used in Figures 3-13. Unsupported SVG
features fail explicitly. Reads existing SVG/PNG and writes only print_assets.
No browser, raster tracing, Fluent access or LaTeX compilation is involved.
"""
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from PIL import Image
from pypdf import PdfReader
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import HexColor

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
FONT=Path('C:/Windows/Fonts/arial.ttf')
pdfmetrics.registerFont(TTFont('SourceArial',str(FONT)))
SYMBOL_FONT=Path('C:/Windows/Fonts/seguisym.ttf')
pdfmetrics.registerFont(TTFont('SourceSymbols',str(SYMBOL_FONT)))
NS='{http://www.w3.org/2000/svg}'
STYLE={'fill':'black','stroke':'none','stroke-width':'1','font-size':'16','font-family':'Arial,sans-serif','text-anchor':'start'}
NUM=r'[-+]?(?:\d*\.\d+|\d+\.?\d*)(?:[eE][-+]?\d+)?'
SLOTS={1:(48,1),2:(77,1),3:(46,1),4:(70,1),5:(68,1),6:(72,1),7:(38,1),8:(38,1),9:(38,1),10:(49,.485),11:(49,.485),12:(46,.485),13:(46,.485)}
NAMES={3:'fig03_sa_convergence',4:'fig04_rsm_vectors',5:'fig05_rsm_yplus',6:'fig06_enhanced_combined',7:'fig07_velocity_midchord',8:'fig08_velocity_trailingedge',9:'fig09_velocity_downstream',10:'fig10_pressure_pressure',11:'fig11_pressure_suction',12:'fig12_yplus_suction',13:'fig13_yplus_pressure'}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def number(v,total=None):
    if str(v).endswith('%'):
        if total is None:raise ValueError('Percentage has no viewport reference')
        return float(str(v)[:-1])*total/100
    return float(v)
def tag(e):return e.tag.removeprefix(NS)

class SVGVector:
    def __init__(self,root,c):
        self.root=root;self.c=c;self.w=float(root.attrib['width']);self.h=float(root.attrib['height'])
        self.clips={e.attrib['id']:e for e in root.iter() if tag(e)=='clipPath'}
        self.stats=Counter();self.text_runs=[]

    def path(self,d):
        tokens=re.findall('[A-Za-z]|'+NUM,d);i=0;p=self.c.beginPath();x=y=0
        while i<len(tokens):
            cmd=tokens[i];i+=1
            if cmd not in ['M','L','H','V','h']:raise ValueError('Unsupported exact source path command: '+cmd)
            n=2 if cmd in ['M','L'] else 1
            vals=list(map(float,tokens[i:i+n]));i+=n
            if cmd=='M':x,y=vals;p.moveTo(x,y)
            elif cmd=='L':x,y=vals;p.lineTo(x,y)
            elif cmd=='H':x=vals[0];p.lineTo(x,y)
            elif cmd=='V':y=vals[0];p.lineTo(x,y)
            else:x+=vals[0];p.lineTo(x,y)
        return p

    def style(self,s):
        for prop,setter in [('fill',self.c.setFillColor),('stroke',self.c.setStrokeColor)]:
            value=s.get(prop,'none')
            if value!='none':
                if value.startswith('#') and len(value)==4:value='#'+''.join(c*2 for c in value[1:])
                setter(HexColor(value) if value.startswith('#') else value)
        self.c.setLineWidth(float(s['stroke-width']));self.c.setLineCap(0);self.c.setLineJoin(0)
        dash=s.get('stroke-dasharray','')
        self.c.setDash(list(map(float,re.findall(NUM,dash))) if dash and dash!='none' else [])
        if 'fill-opacity' in s:self.c.setFillAlpha(float(s['fill-opacity']))

    def text(self,e,s):
        runs=[]
        if e.text:runs.append((e.text,float(s['font-size']),0))
        for child in e:
            if tag(child)!='tspan' or list(child):raise ValueError('Unsupported text subtree')
            cs={**s,**child.attrib};rise=.35*float(s['font-size']) if cs.get('baseline-shift')=='super' else 0
            if cs.get('baseline-shift') not in [None,'super']:raise ValueError('Unsupported text baseline shift')
            if child.text:runs.append((child.text,float(cs['font-size']),rise))
            if child.tail:runs.append((child.tail,float(s['font-size']),0))
        glyph_runs=[]
        for text,size,rise in runs:
            for char in text:
                font='SourceArial' if ord(char) in pdfmetrics.getFont('SourceArial').face.charWidths else 'SourceSymbols'
                if ord(char) not in pdfmetrics.getFont(font).face.charWidths:raise ValueError('No embedded font glyph for '+repr(char))
                if glyph_runs and glyph_runs[-1][1:]==(size,rise,font):glyph_runs[-1]=(glyph_runs[-1][0]+char,size,rise,font)
                else:glyph_runs.append((char,size,rise,font))
        width=sum(pdfmetrics.stringWidth(t,font,size) for t,size,rise,font in glyph_runs)
        x=float(e.attrib['x']);y=float(e.attrib['y']);anchor=s['text-anchor'];offset={'start':0,'middle':-width/2,'end':-width}[anchor]
        self.c.translate(x,y);self.c.scale(1,-1)
        for text,size,rise,font in glyph_runs:
            self.c.setFont(font,size);self.c.drawString(offset,rise,text);offset+=pdfmetrics.stringWidth(text,font,size)
            self.text_runs.append({'text':text,'font_size_svg':size,'rise_svg':rise,'embedded_font':font})

    def draw(self,e,inherited):
        t=tag(e)
        if t in ['defs','clipPath']:return
        if t not in ['svg','g','path','rect','polyline','polygon','text']:raise ValueError('Unsupported source SVG element: '+t)
        s={**inherited,**{k:v for k,v in e.attrib.items() if k in ['fill','stroke','stroke-width','stroke-dasharray','fill-opacity','font-size','font-family','text-anchor']}}
        self.c.saveState();self.style(s)
        if 'transform' in e.attrib:
            m=re.fullmatch(r'rotate\(('+NUM+'),('+NUM+'),('+NUM+r')\)',e.attrib['transform'])
            if not m:raise ValueError('Unsupported transform')
            angle,cx,cy=map(float,m.groups());self.c.translate(cx,cy);self.c.rotate(angle);self.c.translate(-cx,-cy)
        if 'clip-path' in e.attrib:
            match=re.fullmatch(r'url\(#([^)]*)\)',e.attrib['clip-path']);clip=self.clips[match.group(1)]
            if len(clip)!=1 or tag(clip[0])!='rect':raise ValueError('Unsupported clip shape')
            q=clip[0].attrib;p=self.c.beginPath();p.rect(float(q['x']),float(q['y']),float(q['width']),float(q['height']));self.c.clipPath(p,stroke=0,fill=0)
        stroke=int(s.get('stroke')!='none');fill=int(s.get('fill')!='none')
        if t in ['svg','g']:
            for child in e:self.draw(child,s)
        elif t=='path':self.c.drawPath(self.path(e.attrib['d']),stroke=stroke,fill=fill);self.stats['path']+=1
        elif t=='rect':
            a=e.attrib;self.c.rect(float(a.get('x',0)),float(a.get('y',0)),number(a['width'],self.w),number(a['height'],self.h),stroke=stroke,fill=fill);self.stats['rect']+=1
        elif t in ['polyline','polygon']:
            points=list(map(float,re.findall(NUM,e.attrib['points'])));p=self.c.beginPath();p.moveTo(*points[:2])
            for i in range(2,len(points),2):p.lineTo(*points[i:i+2])
            if t=='polygon':p.close()
            self.c.drawPath(p,stroke=stroke,fill=fill);self.stats[t]+=1
        elif t=='text':self.text(e,s);self.stats['text']+=1
        self.c.restoreState()

def font_sizes(root,scale):
    values=[];superscripts=[]
    def walk(e,parent):
        size=float(e.attrib.get('font-size',parent))
        if tag(e) in ['text','tspan'] and (e.text or '').strip():
            (superscripts if e.attrib.get('baseline-shift')=='super' else values).append(size*scale)
        for ch in e:walk(ch,size)
    walk(root,16)
    return {'minimum_base_text_pt':min(values),'maximum_base_text_pt':max(values),'base_sizes_pt':sorted(set(round(v,5) for v in values)),'superscript_sizes_pt':sorted(set(round(v,5) for v in superscripts))}

def main():
    manifest=json.loads((ROOT/'data/final_data_manifest.json').read_text());records=[]
    for key,item in manifest['report_figure_candidates'].items():
        n=int(key);png=Path(item['path']);svg=png.with_suffix('.svg');root=ET.parse(svg).getroot();w,h=map(float,[root.attrib['width'],root.attrib['height']])
        cap,fraction=SLOTS[n];physical_w=min(165.1*fraction,cap*w/h);physical_h=physical_w*h/w;scale=physical_w/25.4*72/w
        with Image.open(png) as image:px=list(image.size)
        record={'figure':n,'source_svg':str(svg),'svg_sha256':sha(svg),'source_png':str(png),'png_sha256_before':sha(png),'png_pixels':px,
                'source_viewbox':[w,h],'tex_width_limit_mm':165.1*fraction,'tex_height_cap_mm':cap,'actual_print_size_mm':[physical_w,physical_h],
                'effective_png_dpi':[px[0]/(physical_w/25.4),px[1]/(physical_h/25.4)],'fonts_at_actual_report_size':font_sizes(root,scale),'source_embedded_image_count':sum(tag(e)=='image' for e in root.iter())}
        if n>=3:
            target=OUT/(NAMES[n]+'.pdf');c=canvas.Canvas(str(target),pagesize=(w*scale,h*scale),invariant=True,pageCompression=1)
            c.setTitle(f'Figure {n}: source scientific SVG, vector export');c.setAuthor('MMME3086 data pipeline');c.translate(0,h*scale);c.scale(scale,-scale)
            renderer=SVGVector(root,c);renderer.draw(root,STYLE);c.showPage();c.save()
            reader=PdfReader(target);page=reader.pages[0];resources=page['/Resources'];xobjects=resources.get('/XObject',{})
            images=[name for name,obj in xobjects.items() if obj.get_object().get('/Subtype')=='/Image']
            if images:raise ValueError('Unexpected raster image in scientific PDF')
            fonts=[]
            for name,f in resources.get('/Font',{}).items():
                f=f.get_object();descriptor=f.get('/FontDescriptor');embedded=bool(descriptor and descriptor.get_object().get('/FontFile2'))
                fonts.append({'resource':name,'basefont':str(f.get('/BaseFont')),'subtype':str(f.get('/Subtype')),'embedded_truetype':embedded})
            if not any(f['embedded_truetype'] for f in fonts):raise ValueError('Source Arial is not embedded')
            content=page.get_contents().get_data();operator_counts={op:len(re.findall(rb'(?<!\S)'+op.encode()+rb'(?!\S)',content)) for op in ['m','l','re','Tj','Tf']}
            if operator_counts['Tj']==0 or len(page.extract_text().strip())<20:raise ValueError('PDF text did not remain extractable')
            record['pdf']={'path':str(target),'sha256':sha(target),'bytes':target.stat().st_size,'page_size_pt':[float(page.mediabox.width),float(page.mediabox.height)],'image_xobjects':images,'fonts':fonts,
                           'content_operator_counts':operator_counts,'source_draw_element_counts':dict(renderer.stats),'extractable_text_characters':len(page.extract_text()),'text_runs':renderer.text_runs,
                           'conversion':'Direct existing SVG coordinates, path vertices, colour values (including CSS 3-digit hex), dashes and text; embedded actual Arial TrueType with Segoe UI Symbol fallback for the proportionality glyph. SVG super baseline uses 0.35 parent em; no numeric samples remapped.'}
        record['png_unchanged']=sha(png)==record['png_sha256_before']
        if not record['png_unchanged']:raise ValueError('Original PNG changed')
        records.append(record)
    report={'scope':'Audit 13 existing report figures; vector PDF export of Figures 3-13 only. No LaTeX compilation or report-file mutation.',
            'layout_source':{'path':str(ROOT/'report/prepared/main.tex'),'sha256':sha(ROOT/'report/prepared/main.tex'),'class_path':str(ROOT/'report/prepared/new-aiaa.cls'),'class_sha256':sha(ROOT/'report/prepared/new-aiaa.cls'),'paper':'US letter; geometry margins 1 inch; text width 6.5 inches = 165.1 mm'},
            'renderer_script':{'path':str(Path(__file__)),'sha256':sha(Path(__file__))},'embedded_fonts':[{'path':str(p),'sha256':sha(p)} for p in [FONT,SYMBOL_FONT]],'figures':records}
    (OUT/'print_asset_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    with (OUT/'print_size_audit.csv').open('w',newline='',encoding='utf-8') as f:
        writer=csv.writer(f);writer.writerow(['figure','svg_width','svg_height','png_width','png_height','print_width_mm','print_height_mm','effective_dpi','min_base_font_pt','vector_pdf'])
        for r in records:writer.writerow([r['figure'],*r['source_viewbox'],*r['png_pixels'],*r['actual_print_size_mm'],r['effective_png_dpi'][0],r['fonts_at_actual_report_size']['minimum_base_text_pt'],r.get('pdf',{}).get('path','Not exported')])
    print('Audited 13 unchanged PNGs and exported 11 text/path vector PDFs.')

if __name__=='__main__':main()
