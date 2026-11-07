"""Compute actual includegraphics boxes from source, without running TeX."""
from pathlib import Path
import json,re,struct,xml.etree.ElementTree as ET,hashlib
root=Path(__file__).resolve().parents[1];p=root/'report/prepared/main.tex';tex=p.read_text(encoding='utf-8')
assets={x['report_asset']:x for x in json.loads((root/'report/prepared/asset_manifest.json').read_text())}
out=[]
for m in re.finditer(r'\\evidence\{([\d.]+)mm\}\{([^}]+)\}',tex):
    cap,name=float(m[1]),m[2];before=tex[:m.start()]
    inmini=before.rfind('\\begin{minipage}')>before.rfind('\\end{minipage}')
    available=165.1*(.485 if inmini else 1)
    png=root/'report/prepared'/name;w,h=struct.unpack('>II',png.read_bytes()[16:24]);ratio=w/h
    width=min(available,cap*ratio);height=width/ratio
    svg=root/Path(assets[name]['original']).with_suffix('.svg')
    r=ET.parse(svg).getroot();vb=list(map(float,r.attrib['viewBox'].split()));texts=[]
    def walk(el,size=16):
        size=float(el.attrib.get('font-size',size));style=el.attrib.get('style','');a=re.search(r'font-size:\s*([\d.]+)',style)
        if a:size=float(a[1])
        if el.tag.split('}')[-1]=='text' and ''.join(el.itertext()).strip():texts.append({'text':''.join(el.itertext()),'svg_font_px':size,'print_pt':size*width/vb[2]*72/25.4})
        for child in el:walk(child,size)
    walk(r)
    out.append({'figure':name,'PNG_pixels':[w,h],'available_width_mm':available,'height_cap_mm':cap,'actual_print_width_mm':width,'actual_print_height_mm':height,'raster_ppi':w/(width/25.4),'SVG':str(svg),'min_label_font_pt':min(t['print_pt'] for t in texts),'max_label_font_pt':max(t['print_pt'] for t in texts),'labels_below_8pt':[t for t in texts if t['print_pt']<8]})
result={'main_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'class_text_width_mm':165.1,'class_text_height_mm':228.6,'figures':out,'method':'Letterpaper minus 1 inch margins, exact source PNG aspect ratio, graphicx width AND height with keepaspectratio. SVG font-size inheritance converted at actual print width; no TeX compilation or rendered-page acceptance.'}
(root/'review/static_print_box_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps([{k:v for k,v in f.items() if k not in ['labels_below_8pt','SVG']} for f in out],indent=2))
