"""Exact five-cell post-annotation correction; previous centered files stay untouched.

External graphics are restricted to axes, text, leaders, scalar-bar labels and
five exact-cell identification outlines as explicit post-annotations. Those
five thin closed paths have no fill and do not replace the Fluent-native cell
colours. Scientific fills, contours, velocity vectors and mesh rendering are
never reconstructed. Native image placement is an equal-scale similarity;
the original scientific raster RGB remains unchanged in the PDF.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
from io import BytesIO
import numpy as np
from PIL import Image
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from pypdf import PdfReader,PdfWriter
from pypdf.generic import ContentStream,DecodedStreamObject,NameObject,NumberObject,FloatObject,ArrayObject,TextStringObject,ByteStringObject,DictionaryObject,RectangleObject

ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
PREVIOUS=ROOT/'data/native_figures_2026-11-10'
sys.path.insert(0,str(ROOT/'data/print_assets'))
from export_vector_figures import SVGVector,STYLE

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def text(c,x,y,value,size=8,anchor='start',colour=(.133,.133,.133),angle=0):
    c.saveState();c.setFillColorRGB(*colour);c.translate(x,y);c.rotate(angle);c.setFont('SourceArial',size)
    width=c.stringWidth(value,'SourceArial',size);c.drawString({'start':0,'middle':-width/2,'end':-width}[anchor],0,value);c.restoreState()
def stroke(c,x0,y0,x1,y1,width=.4,colour=(.133,.133,.133),dash=None):
    c.saveState();c.setStrokeColorRGB(*colour);c.setLineWidth(width)
    if dash:c.setDash(dash)
    c.line(x0,y0,x1,y1);c.restoreState()

def native_layer(c,image,calibration,panel,evidence):
    p=ROOT/image;cal=json.loads((OUT/calibration).read_text())
    if sha(p)!=cal['native_source']['sha256']:raise ValueError('Native calibration source hash has changed')
    if not cal.get('axis_aligned_native_camera_constraint'):raise ValueError('Final native sources must have axis-aligned camera; no external corrective rotation')
    if cal['outline_fit_error_pixels']['p95']>cal.get('calibration_acceptance_tolerance_pixels',1.5):raise ValueError('Native outline calibration is not sufficiently accurate')
    x,y,w,h=panel['form_box_bottom_left_pt'];lo,hi,bottom,top=panel['world_bounds_m'];kx=w/(hi-lo);ky=h/(top-bottom)
    if abs(kx-ky)/max(kx,ky)>1e-6:raise ValueError('Authority target viewport is not equal scale')
    scale=cal['scale_pixels_per_m'];bx,by=cal['world_to_pixel_offset'];im=Image.open(p);iw,ih=im.size;factor=kx/scale
    # Native image's lower-left corresponds to pixel (0,H). Clip to exact original plot box.
    tx=x-kx*lo-factor*bx;ty=y-kx*bottom+factor*(by-ih)
    c.saveState();clip=c.beginPath();clip.rect(x,y,w,h);c.clipPath(clip,stroke=0,fill=0)
    c.drawImage(ImageReader(im),tx,ty,width=iw*factor,height=ih*factor,mask=None);c.restoreState()
    evidence.append({'role':'Fluent-native scientific image','path':str(p),'sha256':sha(p),'source_pixels':[iw,ih],'calibration':str(OUT/calibration),'calibration_sha256':sha(OUT/calibration),
                     'pdf_image_position_size_pt':[tx,ty,iw*factor,ih*factor],'clip_rectangle_pt':[x,y,w,h],'uniform_scale_pt_per_pixel':factor,'effective_source_dpi':72/factor,
                     'RGB_processing':'Original native PNG embedded losslessly; no recolouring, sharpening, vector/cell reconstruction or data masks.'})

def native_colour_strip(donor,name,horizontal=False):
    p=ROOT/donor;im=Image.open(p).convert('RGB');rgb=np.asarray(im);chroma=rgb.max(2).astype(int)-rgb.min(2).astype(int);mask=(chroma>30)&(rgb.max(2)<254)
    best=(0,0,0)
    for x in range(min(im.width//4,500)):
        run=np.diff(np.r_[False,mask[:,x],False].astype(int));starts=np.where(run==1)[0];ends=np.where(run==-1)[0]
        if len(starts):
            i=np.argmax(ends-starts);length=ends[i]-starts[i]
            if length>best[0]:best=(int(length),x,int(starts[i]))
    length,x,y=best
    if length<im.height*.25:raise ValueError('Cannot uniquely locate native scalar bar')
    # Take a narrow central native strip. The scalar coordinate remains linear;
    # its separate display aspect is not a physical-domain geometry transform.
    x0=max(0,x);x1=min(im.width,x+3);crop=im.crop((x0,y,x1,y+length))
    if horizontal:crop=crop.transpose(Image.Transpose.ROTATE_270)
    target=OUT/(name+'_native_colour_strip.png');crop.save(target)
    return target,{'native_donor':str(p),'native_donor_sha256':sha(p),'crop_box_pixels':[x0,y,x1,y+length],'rotation':'90 degrees clockwise' if horizontal else 'none',
                   'output':str(target),'sha256':sha(target),'RGB_policy':'Only exact native pixel crop/transpose. No palette generation or recolouring; bar aspect reflow is independent of physical field geometry.'}

def bar(c,donor,name,rectangle,evidence,horizontal=False):
    image,record=native_colour_strip(donor,name,horizontal);x,y,w,h=rectangle;c.drawImage(str(image),x,y,width=w,height=h);record['pdf_box_pt']=rectangle;evidence.append(record)

def svg_annotations(c,source,number,physical_width_pt=468):
    original=ET.parse(ROOT/source).getroot();root=ET.Element('svg',original.attrib);group=ET.SubElement(root,'g',{'font-family':'Arial,sans-serif','font-size':'28','fill':'#222'})
    label_backgrounds={}
    if number==2:
        for parent in original.iter():
            children=list(parent)
            for index,node in enumerate(children):
                if node.tag.endswith('text') and node.text in ['aerofoil_suction','aerofoil_pressure'] and index and children[index-1].tag.endswith('rect'):
                    label_backgrounds[id(node)]=children[index-1]
    for node in original.iter():
        if node.tag.endswith('text'):
            if number==5 and float(node.attrib.get('x','nan'))==118 and (node.text or '') in ['-20','-10','0','10']:
                continue
            if id(node) in label_backgrounds:group.append(copy.deepcopy(label_backgrounds[id(node)]))
            node=copy.deepcopy(node)
            if number==5 and node.text=='Red cell outlines: y+ < 30':node.text='Five red-outlined cells: y+ < 30'
            if number==2:
                native_colours={'inlet':'#00a600','outlet':'#ff5985','aerofoil_suction':'#0000a6','aerofoil_pressure':'#ff6600'}
                if node.text in native_colours:node.attrib['fill']=native_colours[node.text]
            group.append(node)
    if number==5:
        change=json.loads((OUT/'centering_layout_audit.json').read_text(encoding='utf-8'));ymax=change['figure5']['new_world_bounds_m'][3]
        for tick in [-10,0,10,20]:
            label=ET.SubElement(group,'text',{'x':'118','y':str(95+(ymax-tick/1000)*10500+9),'font-size':'28','text-anchor':'end','fill':'#222'});label.text=str(tick)
    w=float(root.attrib['width']);h=float(root.attrib['height']);s=physical_width_pt/w;c.saveState();c.translate(0,h*s);c.scale(s,-s);SVGVector(root,c).draw(root,STYLE);c.restoreState()

def figure2(layout):
    item=next(f for f in layout['figures'] if f['figure']==2);w,h=item['target_size_pt'];s=w/1600;target=OUT/'fig02_mesh_bc.pdf';c=canvas.Canvas(str(target),pagesize=(w,h),invariant=True);e=[]
    native_layer(c,'solver/native_figures_2026-11-10/taskA/mesh_full_native_interioronly.png','taskA_full_camera_calibration.json',item['panels'][0],e)
    native_layer(c,'solver/native_figures_2026-11-10/taskA/mesh_local_native_interioronly.png','taskA_local_camera_calibration.json',item['panels'][1],e)
    xy=lambda x,y:(x*s,h-y*s)
    def ln(a,b,colour=(.2,.2,.2),width=1.5,dash=None):stroke(c,*xy(*a),*xy(*b),width*s,colour,[v*s for v in dash] if dash else None)
    def dimension(a,b):
        import math
        ln(a,b);dx=b[0]-a[0];dy=b[1]-a[1];length=math.hypot(dx,dy);ux,uy=dx/length,dy/length
        for tip,sign in [(a,-1),(b,1)]:
            p=(tip[0]-sign*9*ux+4.5*uy,tip[1]-sign*9*uy-4.5*ux);q=(tip[0]-sign*9*ux-4.5*uy,tip[1]-sign*9*uy+4.5*ux);ln(p,tip);ln(tip,q)
    dimension((120,38),(1420,38));dimension((1540,80),(1540,275));ln((1425,80),(1550,80),(.467,.467,.467));ln((1425,275),(1550,275),(.467,.467,.467))
    bounds=item['panels'][1]['world_bounds_m'];full=item['panels'][0];fx,fy,fw,fh=full['form_box_bottom_left_pt'];x0,y0=fx+(bounds[0]+.5)*fw,fy+(bounds[2]+.075)/.15*fh
    c.saveState();c.setLineWidth(2*s);c.setDash([7*s,4*s]);c.rect(x0,y0,(bounds[1]-bounds[0])*fw,(bounds[3]-bounds[2])/.15*fh,stroke=1,fill=0);c.restoreState()
    p=item['panels'][1];px,py,pw,ph=p['form_box_bottom_left_pt'];c.saveState();c.setLineWidth(1.4*s);c.setStrokeColorRGB(.2,.2,.2);c.rect(px,py,pw,ph,stroke=1,fill=0);c.restoreState()
    for tick in [0,50,100]:
        xx=px+(tick/1000-bounds[0])*pw/(bounds[1]-bounds[0]);stroke(c,xx,py,xx,py-7*s,1.5*s)
    for tick in [20,10,0,-10,-20,-30]:
        if bounds[2]<=tick/1000<=bounds[3]:yy=py+(tick/1000-bounds[2])*ph/(bounds[3]-bounds[2]);stroke(c,px-7*s,yy,px,yy,1.5*s)
    sys.path.insert(0,str(ROOT/'data'));from plot_taskA_mesh import parse_mesh
    nodes,faces,zones,counts=parse_mesh(ROOT/'solver/aligned_taskA/taskA_baseline.msh')
    for name,start,colour in [('aerofoil_suction',(850,390),(0,0,166/255)),('aerofoil_pressure',(820,620),(1,102/255,0)),('aerofoil_te',(1400,610),(.133,.133,.133))]:
        face=faces[zones[name]['faces'][len(zones[name]['faces'])//2]];world=[(nodes[face[0]][j]+nodes[face[1]][j])/2 for j in [0,1]];end=(px+(world[0]-bounds[0])*pw/(bounds[1]-bounds[0]),py+(world[1]-bounds[2])*ph/(bounds[3]-bounds[2]));stroke(c,*xy(*start),*end,1.5*s,colour)
    svg_annotations(c,'data/taskA/figure2_mesh_compact.svg',2,w);c.showPage();c.save();e.append({'role':'Annotation disclosure','all_scientific_mesh_paths':'Fluent-native PNGs only; no external mesh re-rendering','seven_boundary_labels':'Original labels retained; four label colours match the actual native RGB','dimensions_mm':[1000,150],'axis_label_baseline_svg':730});return target,e

def axes(c,panel,xticks,yticks,ytitle=True):
    x,y,w,h=panel['form_box_bottom_left_pt'];lo,hi,bottom,top=panel['world_bounds_m'];sx=w/(hi-lo);sy=h/(top-bottom);s=.2925
    c.saveState();c.setStrokeColorRGB(.15,.15,.15);c.setLineWidth(.2925);c.rect(x,y,w,h,stroke=1,fill=0);c.restoreState()
    for tick in xticks:
        px=x+(tick/1000-lo)*sx;stroke(c,px,y,px,y-6*s)
    for tick in yticks:
        py=y+(tick/1000-bottom)*sy;stroke(c,x-6*s,py,x,py)

def figure4(layout):
    item=next(f for f in layout['figures'] if f['figure']==4);w,h=item['target_size_pt'];target=OUT/'fig04_rsm_vectors.pdf';c=canvas.Canvas(str(target),pagesize=(w,h),invariant=True);e=[]
    native_layer(c,'solver/native_figures_2026-11-10/case03/velocity_native_75us_outline5.png','case03_velocity_outline5_calibration.json',item['panels'][0],e)
    native_layer(c,'solver/native_figures_2026-11-10/case03/velocity_native_normalised_te_outline9.png','case03_te_outline9_calibration.json',item['panels'][1],e)
    axes(c,item['panels'][0],[0,50,100,150,200],[-40,-20,0,20]);axes(c,item['panels'][1],[90,100,110,120],[-20,-10,0],False)
    c.saveState();c.setLineWidth(.2925);c.setDash([1.755,1.17]);c.rect(155.025,91.26,46.8,28.08,stroke=1,fill=0);c.restoreState()
    bar(c,'solver/native_figures_2026-11-10/case03/velocity_native_legend_valid.png','fig04_speed',item['colour_bars'][0]['form_box_bottom_left_pt'],e,True)
    svg_annotations(c,'data/case03_aligned/figures/figure4_velocity_vectors.svg',4);c.showPage();c.save();return target,e

def figure5(layout):
    item=next(f for f in layout['figures'] if f['figure']==5);w,h=item['target_size_pt'];target=OUT/'fig05_rsm_yplus.pdf';c=canvas.Canvas(str(target),pagesize=(w,h),invariant=True);e=[]
    native_layer(c,'solver/native_figures_2026-11-10-centered/case03/yplus_native_context_centered.png','case03_yplus_centered_calibration.json',item['panels'][0],e)
    axes(c,item['panels'][0],[0,20,40,60,80,100],[-10,0,10,20]);bar(c,'solver/native_figures_2026-11-10/case03/yplus_native_legend_valid.png','fig05_yplus',item['colour_bars'][0]['form_box_bottom_left_pt'],e)
    # Quantity leaders refer to native cell centres already independently audited.
    field=json.loads((ROOT/'data/case03_aligned/cell_field_plot_audit.json').read_text());raw=ROOT/'data/case03_aligned/native/raw/domain_cell_fields.csv'
    import csv
    with raw.open() as f:rows={int(float(r['cell-id'])):r for r in ({k.strip():v for k,v in row.items()} for row in csv.DictReader(f))}
    for key,tx,ty in [('max_cell_id',280,83),('min_cell_id',870,570),('TE_cell_id',1195,570)]:
        r=rows[field['wall_yplus_display'][key]];x,y,pw,ph=item['panels'][0]['form_box_bottom_left_pt'];xmin,xmax,ymin,ymax=item['panels'][0]['world_bounds_m'];px=x+(float(r['x-coordinate'])-xmin)*pw/(xmax-xmin);py=y+(float(r['y-coordinate'])-ymin)*ph/(ymax-ymin)
        stroke(c,tx*.2925,h-ty*.2925,px,py,width=1.3*.2925,colour=(.2,.2,.2))
    # Exactly five post-processing outlines, never a range bracket. Native image
    # pixels are not modified; these are explicitly separate annotation paths.
    sys.path.insert(0,str(ROOT/'data'));from plot_taskA_mesh import parse_mesh
    nodes,faces,zones,counts=parse_mesh(ROOT/'solver/aligned_taskA/taskA_baseline.msh');low=set(field['wall_yplus_display']['below30_cell_ids'])
    wall_ids=set()
    for side in ['suction','pressure','trailing']:
        with (ROOT/f'data/case03_aligned/native/raw/{side}_p_yplus.csv').open() as stream:
            for raw_wall in csv.DictReader(stream):
                wall={k.strip():v for k,v in raw_wall.items()};wall_ids.add(int(float(wall['cell-id'])))
    actual_low={ci for ci in wall_ids if float(rows[ci]['y-plus'])<30}
    if actual_low!={7588,7316,69,7251,2573}:raise ValueError('Native low-y+ five-cell identities differ')
    px=lambda v:x+(v-item['panels'][0]['world_bounds_m'][0])*pw/(item['panels'][0]['world_bounds_m'][1]-item['panels'][0]['world_bounds_m'][0])
    py=lambda v:y+(v-item['panels'][0]['world_bounds_m'][2])*ph/(item['panels'][0]['world_bounds_m'][3]-item['panels'][0]['world_bounds_m'][2])
    red=(.69,0,0);outlines=[]
    for ci in [7588,7316,69,7251,2573]:
        nodeids=set()
        for face in faces.values():
            if ci in face[2:]:nodeids.update(face[:2])
        if len(nodeids)!=3:raise ValueError('Selected cell is not an original triangle')
        import math
        centre=[sum(nodes[i][j] for i in nodeids)/3 for j in [0,1]];ordered=sorted(nodeids,key=lambda i:math.atan2(nodes[i][1]-centre[1],nodes[i][0]-centre[0]))
        world=[nodes[i] for i in ordered];pdf=[(px(v[0]),py(v[1])) for v in world]
        c.saveState();c.setStrokeColorRGB(*red);c.setLineWidth(.35);c.setLineJoin(0);path=c.beginPath();path.moveTo(*pdf[0])
        for v in pdf[1:]:path.lineTo(*v)
        path.close();c.drawPath(path,stroke=1,fill=0);c.restoreState()
        outlines.append({'cell_id':ci,'yplus':float(rows[ci]['y-plus']),'actual_node_ids':ordered,'world_vertices_m':world,'pdf_vertices_pt':pdf})
    e.append({'role':'Non-native annotation only','type':'Exactly five thin red empty triangle outlines on their real native mesh edges','stroke_width_pt':.35,'fill':False,'cell_ids':[7588,7316,69,7251,2573],'excluded_not_below30':[6134,7578],'polygons':outlines,'native_colour_fill_unchanged':True,'previous_wide_bracket_removed':True})
    svg_annotations(c,'data/case03_aligned/figures/figure5_wall_cell_yplus.svg',5);c.showPage();c.save();return target,e

def reference_text_only_pdf(target):
    """Retain authority typography only. No original scientific drawing operators survive."""
    from extract_attachment_layout import SOURCE,concat
    source=PdfReader(SOURCE);form=source.pages[3]['/Resources']['/XObject']['/Im6'].get_object();matrix=(1,0,0,1,0,0);stack=[];block=None;captured=[];title=[];omitted=[]
    def strings(operations):
        out=[]
        for a,op in operations:
            if op not in [b'Tj',b'TJ']:continue
            for v in (a[0] if op==b'TJ' else a):
                if isinstance(v,ByteStringObject):out.append(bytes(v).decode('latin1'))
                elif isinstance(v,TextStringObject):out.append(str(v))
        return ''.join(out)
    for args,op in ContentStream(form,source).operations:
        if block is not None:
            block.append((args,op))
            if op==b'ET':
                if 'Cell-centred' in strings(block):title.append({'original_text':strings(block),'matrix':list(entry),'replacement':'(a) Fluent-native rake-sampled velocity vectors and wake'})
                elif strings(block)=='Zoom in (b)':omitted.append({'original_text':strings(block),'replacement':'Foil enlargement: panel (b)','reason':'Moved to external inter-panel whitespace to avoid crossing native arrows.'})
                elif strings(block) in ['0','50','100','150','200'] and 270<entry[5]<285 and entry[4]<405:
                    omitted.append({'original_text':strings(block),'original_matrix':list(entry),'replacement':'Replaced by correct centred-window tick labels -50,0,50,100,150'})
                else:
                    captured.extend([([],b'q'),([FloatObject(x) for x in entry],b'cm'),([NumberObject(0)],b'g')]+block+[([],b'Q')])
                block=None
            continue
        if op==b'q':stack.append(matrix)
        elif op==b'Q':matrix=stack.pop()
        elif op==b'cm':matrix=concat(matrix,tuple(map(float,args)))
        elif op==b'BT':block=[(args,op)];entry=matrix
    if len(title)!=1 or sum('original_matrix' in x for x in omitted)!=5:raise ValueError('Could not isolate authority title and all five obsolete A-axis tick labels')
    writer=PdfWriter();writer.clone_document_from_reader(PdfReader(target));textform=DecodedStreamObject();stream=ContentStream(None,source);stream.operations=captured;textform.set_data(stream.get_data())
    textform[NameObject('/Type')]=NameObject('/XObject');textform[NameObject('/Subtype')]=NameObject('/Form');textform[NameObject('/FormType')]=NumberObject(1);textform[NameObject('/BBox')]=form['/BBox'].clone(writer);textform[NameObject('/Resources')]=form['/Resources'].clone(writer)
    ref=writer._add_object(textform);page=writer.pages[0];page['/Resources']['/XObject'][NameObject('/AuthorityAnnotationText')]=ref
    content=DecodedStreamObject();content.set_data(page.get_contents().get_data()+b'\nq /AuthorityAnnotationText Do Q\n');page[NameObject('/Contents')]=writer._add_object(content);out=BytesIO();writer.write(out);target.write_bytes(out.getvalue())
    return {'role':'Authority typography preserved as text-only Form','source_pdf':str(SOURCE),'original_scientific_paths_retained':False,'text_operators_only':True,'title_change':title[0],'external_annotation_replacements':omitted}

def figure6(layout):
    item=next(f for f in layout['figures'] if f['figure']==6);w,h=item['target_size_pt'];target=OUT/'fig06_enhanced_combined.pdf';c=canvas.Canvas(str(target),pagesize=(w,h),invariant=True);e=[]
    native_layer(c,'solver/native_figures_2026-11-10-centered/case05/velocity_native_rakes_75us_centered.png','case05_velocity_centered_calibration.json',item['panels'][0],e)
    native_layer(c,'solver/native_figures_2026-11-10/case05/yplus_native_full_outline8.png','case05_yplus_outline8_calibration.json',item['panels'][1],e)
    native_layer(c,'solver/native_figures_2026-11-10/case05/yplus_native_inset_thin_final.png','case05_yplus_inset_calibration.json',item['panels'][2],e)
    # Axis rules/ticks only, no scientific polygons or arrows are generated.
    ticks=[([-50,0,50,100,150],[-20,0,20]),([0,20,40,60,80,100],[-10,0,10]),([0,.5,1,1.5],[7,7.5])]
    for p,(xt,yt) in zip(item['panels'],ticks):
        x,y,pw,ph=p['form_box_bottom_left_pt'];xmin,xmax,ymin,ymax=p['world_bounds_m'];stroke(c,x,y,x+pw,y,.55);stroke(c,x,y,x,y+ph,.55)
        for tick in xt:xx=x+(tick/1000-xmin)*pw/(xmax-xmin);stroke(c,xx,y,xx,y-3.5,.55)
        for tick in yt:yy=y+(tick/1000-ymin)*ph/(ymax-ymin);stroke(c,x-3.5,yy,x,yy,.55)
    p=item['panels'][0];x,y,pw,ph=p['form_box_bottom_left_pt'];xmin,xmax,ymin,ymax=p['world_bounds_m']
    for tick in [-50,0,50,100,150]:text(c,x+(tick/1000-xmin)*pw/(xmax-xmin),275.2396788878,str(tick).replace('-', '\u2212'),8,'middle',(0,0,0))
    bar(c,'solver/native_figures_2026-11-10/case05/velocity_native_legend_valid.png','fig06_speed',item['colour_bars'][0]['form_box_bottom_left_pt'],e)
    bar(c,'solver/native_figures_2026-11-10/case05/yplus_native_legend_valid.png','fig06_yplus',item['colour_bars'][1]['form_box_bottom_left_pt'],e)
    text(c,49.14,376.573898,'(a) Fluent-native rake-sampled velocity vectors and wake',9)
    text(c,49.14,249.5,'Foil enlargement: panel (b)',8)
    # These three authority leaders are annotations. Their cubic control points are collinear.
    leaders=[[(149.157856,153.89979),(125.190624,169.759793),(101.223391,185.619797),(77.256159,201.4798)],[(280.564949,58.039188),(257.908046,55.767322),(235.251143,53.495456),(212.59424,51.22359)]]
    for points in leaders:
        c.saveState();c.setLineWidth(.6);path=c.beginPath();path.moveTo(*points[0]);path.curveTo(*points[1],*points[2],*points[3]);c.drawPath(path,stroke=1,fill=0);c.restoreState()
    p=item['panels'][1];x,y,pw,ph=p['form_box_bottom_left_pt'];xmin,xmax,ymin,ymax=p['world_bounds_m'];ib=item['panels'][2]['world_bounds_m'];c.saveState();c.setLineWidth(.55);c.rect(x+(ib[0]-xmin)*pw/(xmax-xmin),y+(ib[2]-ymin)*ph/(ymax-ymin),(ib[1]-ib[0])*pw/(xmax-xmin),(ib[3]-ib[2])*ph/(ymax-ymin),stroke=1,fill=0);c.restoreState()
    import csv
    evidence_source=ROOT/'solver/native_figures_2026-11-10-centered/case05/native_rake_centered_velocity_evidence.csv'
    with evidence_source.open() as stream:fluid_count=len(list(csv.DictReader(stream)))
    c.showPage();c.save();e.append(reference_text_only_pdf(target));e.append({'role':'Native sampling disclosure','rakes':12,'points_per_rake':45,'requested_points':540,'rendered_fluid_points':fluid_count,'solid_points_excluded_by_native_Fluent':540-fluid_count,'source':str(evidence_source),'source_sha256':sha(evidence_source),'colour_field':'Fluent-native velocity-magnitude as rendered; no external recomputation from signedU/V','scientific_arrows':'Unchanged native raster, no external redistribution or arrow drawing'});return target,e

def main():
    p=argparse.ArgumentParser();p.add_argument('--figures',nargs='+',type=int,choices=[5],default=[5]);args=p.parse_args();layout=json.loads((OUT/'reference_layout_audit.json').read_text(encoding='utf-8'));records=[]
    changes=json.loads((OUT/'centering_layout_audit.json').read_text(encoding='utf-8'))
    next(f for f in layout['figures'] if f['figure']==5)['panels'][0]['world_bounds_m']=changes['figure5']['new_world_bounds_m']
    next(f for f in layout['figures'] if f['figure']==6)['panels'][0]['world_bounds_m']=changes['figure6A']['new_world_bounds_m']
    for n in args.figures:
        if n in [2,4]:
            import shutil
            name={2:'fig02_mesh_bc',4:'fig04_rsm_vectors'}[n]
            for suffix in ['.pdf','.png','_print300.png']:shutil.copyfile(PREVIOUS/(name+suffix),OUT/(name+suffix))
            record=json.loads((PREVIOUS/f'fig{n:02d}_native_composition_audit.json').read_text(encoding='utf-8'));record.update(path=str(OUT/(name+'.pdf')),unchanged_byte_copy_from=str(PREVIOUS/(name+'.pdf')))
            (OUT/f'fig{n:02d}_native_composition_audit.json').write_text(json.dumps(record,indent=2),encoding='utf-8');records.append(record);continue
        target,layers={2:figure2,4:figure4,5:figure5,6:figure6}[n](layout)
        expected=next(f['target_size_pt'] for f in layout['figures'] if f['figure']==n);reader=PdfReader(target)
        if [float(reader.pages[0].mediabox.width),float(reader.pages[0].mediabox.height)]!=expected:
            writer=PdfWriter();writer.clone_document_from_reader(reader);writer.pages[0].mediabox=RectangleObject([0,0,*expected]);writer.pages[0].cropbox=RectangleObject([0,0,*expected]);buffer=BytesIO();writer.write(buffer);target.write_bytes(buffer.getvalue())
        page=PdfReader(target).pages[0];images=list(page.images)
        record={'figure':n,'path':str(target),'sha256':sha(target),'page_size_pt':[float(page.mediabox.width),float(page.mediabox.height)],'native_layers':layers,'scientific_content':'Native Fluent PNGs only; vector content is annotation/axes/text only.','pdf_image_count':len(images)}
        (OUT/f'fig{n:02d}_native_composition_audit.json').write_text(json.dumps(record,indent=2),encoding='utf-8');records.append(record)
    print(json.dumps([{'figure':r['figure'],'pdf':r['path'],'native_image_count':r['pdf_image_count']} for r in records]))

if __name__=='__main__':main()
