"""Read the user's authoritative report PDF; audit figure placement without redrawing fields."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import math
import csv
import xml.etree.ElementTree as ET

import numpy as np
import pdfplumber
from pypdf import PdfReader
from pypdf.generic import ContentStream
from PIL import Image

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
SOURCE=Path(r'C:/Users/A320N/.codex/attachments/fc6dc3e5-27d8-430a-8e56-dc5017c294c6/MMME3086_CFD_Coursework_2026___Yang_LIU_20617209-4.pdf')
sys.path.insert(0,str(ROOT/'data'))
from plot_taskA_mesh import parse_mesh

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mm(pt):return pt*25.4/72
def concat(p,n):
    a,b,c,d,e,f=p;g,h,i,j,k,l=n
    return (a*g+c*h,b*g+d*h,a*i+c*j,b*i+d*j,a*k+c*l+e,b*k+d*l+f)
def actual_font_runs(form,reader):
    matrix=(1,0,0,1,0,0);font=None;size=0;stack=[];runs=[]
    for args,op in ContentStream(form,reader).operations:
        if op==b'q':stack.append((matrix,font,size))
        elif op==b'Q':matrix,font,size=stack.pop()
        elif op==b'cm':matrix=concat(matrix,tuple(map(float,args)))
        elif op==b'Tf':font=str(args[0]);size=float(args[1])
        elif op in [b'Tj',b'TJ']:
            scale=math.sqrt(abs(matrix[0]*matrix[3]-matrix[1]*matrix[2]));runs.append({'font_resource':font,'effective_em_pt':round(size*scale,9)})
    return {'used_em_sizes_pt':sorted(set(r['effective_em_pt'] for r in runs)),'runs':runs,'method':'Tf font size multiplied by square root of the graphics CTM determinant; unaffected by vertical text rotation. Superscripts are intentionally smaller.'}
def panel(name,box,bounds,field=None,color_range=None,role='scientific native layer'):
    x,y,w,h=box
    result={'name':name,'form_box_bottom_left_pt':[x,y,w,h],'physical_size_mm':[mm(w),mm(h)],'world_bounds_m':bounds,'field':field,'colour_range':color_range,'role':role}
    if bounds:
        sx=w/(bounds[1]-bounds[0]);sy=h/(bounds[3]-bounds[2]);result.update(scale_pt_per_m=[sx,sy],equal_axis_relative_error=abs(sx-sy)/max(sx,sy))
    return result

def main():
    reader=PdfReader(SOURCE);records=[]
    figures=[(4,2,'/Im4',[72.001,515.616]),(5,2,'/Im5',[72.001,256.685]),(6,3,'/Im6',[72.001,208.878])]
    with pdfplumber.open(SOURCE) as pdf:
        image_evidence=[]
        for index,source_png in [(0,ROOT/'data/taskA/figure1_native_compact.png'),(1,ROOT/'data/taskA/figure2_mesh_compact.png')]:
            image=reader.pages[0].images[index].image.convert('RGB');current=Image.open(source_png).convert('RGB');info=pdf.pages[0].images[index]
            match=np.array_equal(np.asarray(image),np.asarray(current))
            evidence={'figure':index+1,'source_object_type':'Image XObject','resource':info['name'],'pixels':list(image.size),'page_origin_bottom_left_pt':[info['x0'],info['y0']],
                      'target_size_pt':[info['width'],info['height']],'target_size_mm':[mm(info['width']),mm(info['height'])],
                      'decoded_RGB_equals_current_source_png':match,'current_source_png':str(source_png),'current_source_png_sha256':sha(source_png)}
            if not match:raise ValueError('Attachment raster differs from local Figure1/2 source')
            image_evidence.append(evidence)
            if index==1:
                sx=info['width']/1600;sy=info['height']/740
                if abs(sx-sy)>1e-9:raise ValueError('Figure2 attachment has unexpected anisotropic placement')
                target_h=info['height'];from_top=lambda x,y,w,h:[x*sx,target_h-(y+h)*sy,w*sx,h*sy]
                local_bounds=json.loads((ROOT/'data/taskA/compact_figures_manifest.json').read_text())['figure2']['local_bounds_m']
                labels=[]
                for element in ET.parse(ROOT/'data/taskA/figure2_mesh_compact.svg').getroot().iter():
                    if element.tag.endswith('text'):labels.append({'text':''.join(element.itertext()),'source_svg_attributes':element.attrib,'effective_font_size_pt':float(element.attrib.get('font-size',30))*sx})
                record={**evidence,'page_1based':1,'source_viewbox_svg_px':[1600,740],'aspect_ratio_width_over_height':1600/740,
                        'panels':[panel('full aligned native baseline mesh',from_top(120,80,1300,195),[-.5,.5,-.075,.075],'native mesh'),
                                  panel('local foil native mesh',from_top(300,350,1035,324),local_bounds,'native mesh')],
                        'required_boundary_labels':['inlet','outlet','wall_top','wall_bottom','aerofoil_suction','aerofoil_pressure','aerofoil_te'],
                        'reference_labels':labels,'reference_dimensions_mm':{'duct_length':1000,'duct_height':150},
                        'annotation_constraints':['Keep outlet separate from height arrow at source SVG x1540','Height text at x1585,y177.5 rotated -90 at 28px','Bottom x(mm) baseline730; keep full parenthesis and separation from50 tick'],
                        'source_layout_lineage':{'source_svg':str(ROOT/'data/taskA/figure2_mesh_compact.svg'),'sha256':sha(ROOT/'data/taskA/figure2_mesh_compact.svg'),'annotation_audit':str(ROOT/'data/taskA/figure2_annotation_change_audit.json')}}
                page_image=OUT/'attachment_page-1.png'
                if page_image.exists():
                    im=Image.open(page_image);s=im.width/612;top=792-info['y1'];im.crop((round(info['x0']*s),round(top*s),round(info['x1']*s),round((top+info['height'])*s))).save(OUT/'reference_fig02_crop.png')
                records.append(record)
        for n,page_index,key,origin in figures:
            form=reader.pages[page_index]['/Resources']['/XObject'][key].get_object();bbox=list(map(float,form['/BBox']));w,h=bbox[2]-bbox[0],bbox[3]-bbox[1]
            top=792-origin[1]-h;words=pdf.pages[page_index].crop((origin[0],top,origin[0]+w,top+h)).extract_words(extra_attrs=['fontname','size'])
            texts=[]
            for word in words:
                texts.append({'text':word['text'],'local_top_left_box_pt':[word['x0']-origin[0],word['top']-top,word['x1']-origin[0],word['bottom']-top],'font':word['fontname'],'pdfplumber_size':word['size'],
                              'note':'For rotated text pdfplumber size is the vertical advance, not an unrotated em height.' if not word.get('upright',True) else ''})
            image_objects=[]
            for name,obj in form.get('/Resources',{}).get('/XObject',{}).items():
                if obj.get_object().get('/Subtype')=='/Image':image_objects.append(str(name))
            record={'figure':n,'page_1based':page_index+1,'form_resource':key,'page_origin_bottom_left_pt':origin,'page_box_top_left_pt':[origin[0],top,origin[0]+w,top+h],
                    'form_bbox_pt':bbox,'target_size_pt':[w,h],'target_size_mm':[mm(w),mm(h)],'aspect_ratio_width_over_height':w/h,
                    'source_form_decoded_stream_sha256':hashlib.sha256(form.get_data()).hexdigest(),'form_matrix':form.get('/Matrix',[1,0,0,1,0,0]),
                    'source_object_type':'Form XObject, not Image XObject','source_raster_image_objects':image_objects,'reference_text_items':texts}
            record['effective_font_sizes']=actual_font_runs(form,reader)
            if n==4:
                record['panels']=[panel('main velocity/foil/wake',[38.025,58.5,280.8,99.45],[-.015,.225,-.05,.035],'speed',[0,120]),
                                  panel('trailing-edge direction inset',[348.075,82.1925,99.45,59.67],[.085,.125,-.022,.002],'speed',[0,120])]
                record['colour_bars']=[panel('horizontal speed strip',[46.8,18.135,117,5.265],None,'speed',[0,120],'native colour-strip layer with separate original-size labels')]
                record['native_arrow_policy']={'main':'Arrow length proportional to speed','inset':'Equal-length normalised direction arrows; colour represents speed','reference_description':'Inset: normalised direction arrows; No cells with uₓ < 0'}
                record['inset_bounds_box_on_main_world_m']=[.085,.125,-.022,.002]
                record['reference_source_verification']={'local_original_pdf':'data/print_assets/fig04_rsm_vectors.pdf','decoded_stream_equals_local_original':form.get_data()==PdfReader(ROOT/'data/print_assets/fig04_rsm_vectors.pdf').pages[0].get_contents().get_data()}
            elif n==5:
                record['panels']=[panel('full baseline foil and actual adjacent triangles',[38.025,42.705,356.265,116.7075],[-.008,.108,-.024,.014],'adjacent-cell y+',[0,180])]
                record['colour_bars']=[panel('vertical y+ strip',[415.35,42.705,9.36,116.7075],None,'adjacent-cell y+',[0,180],'native colour-strip layer with separate original-size labels')]
                record['required_callouts']={'max_yplus':170.94,'min_yplus':19.57,'trailing_yplus':40.29,'red_cell_outlines':'y+ < 30; native cell/mesh highlighting only'}
                record['authority_annotation_difference']='The attachment starts the min/TE leader lines at original SVG y=570; the older local Windows PDF used y=598. Retain the attachment layout.'
            else:
                record['panels']=[panel('(a) enhanced velocity/foil/wake',[49.14,288.0638976378,355.68,81.51],[-.01,.23,-.03,.025],'speed',[0,120]),
                                  panel('(b) all enhanced foil-adjacent cells',[49.14,131.172251,355.68,91.986207],[-.008,.108,-.016,.014],'adjacent-cell y+',[0,8]),
                                  panel('equal-scale max-y+ cell inset',[152.2872890889,28.3464566929,116.6254218222,45.3543307087],[-.000274360798096,.001525639201923,.006939829262451,.007639829262523],'adjacent-cell y+',[0,8])]
                record['colour_bars']=[panel('vertical speed bar',[421.2,289.133858,8.424,79.370079],None,'speed',[0,120],'native colour-strip layer'),
                                       panel('vertical y+ bar',[421.2,136.062992,8.424,79.370079],None,'adjacent-cell y+',[0,8],'native colour-strip layer')]
                record['required_callouts']={'main':'Zoom in (b)','fullfoil':'Inset below','inset':'6.586 at maximum y+ cell','inset_title':'Inset: equal-scale native cells at maximum y+'}
                record['layout_warning']='Authoritative 143 mm tall stacked layout. Do not use the historical 71.199 mm side-by-side Figure6.'
                # Independently infer all three camera transforms from the actual 413 foil vertices.
                mesh=ROOT/'inputs/Aerofoil8-degAoA-enhancedBL.msh';nodes,faces,zones,counts=parse_mesh(mesh);ids=set()
                for name in ['aerofoil-suction','aerofoil-pressure','aerofoil-trail']:
                    for fi in zones[name]['faces']:ids.update(faces[fi][:2])
                world=np.array([nodes[n] for n in ids]);paths=[];points=[]
                for operands,op in ContentStream(form,reader).operations:
                    if op in [b'm',b'l']:points.append(tuple(map(float,operands)))
                    elif op in [b'f',b'f*',b'B',b'S',b'n']:
                        if len(points)>300:paths.append(np.array(points))
                        points=[]
                if len(paths)!=3 or any(len(p)!=413 for p in paths):raise ValueError('Unexpected authority foil path structure')
                fits=[]
                for pdf_points,p in zip(paths,record['panels']):
                    scale=(pdf_points.max(0)-pdf_points.min(0))/(world.max(0)-world.min(0));offset=pdf_points.min(0)-scale*world.min(0)
                    mapped=world*scale+offset;dist=np.linalg.norm(mapped[:,None,:]-pdf_points[None,:,:],axis=2);error=float(dist.min(axis=1).max())
                    if error>2e-6:raise ValueError('Reference foil does not fit native source mesh')
                    fits.append({'panel':p['name'],'scale_pt_per_m':scale.tolist(),'offset_pt':offset.tolist(),'maximum_native_node_to_reference_vertex_error_pt':error})
                record['world_limit_evidence']={'method':'Match the three 413-vertex reference foil paths to all 413 actual enhanced-mesh boundary nodes; derive limits from the PDF clipping rectangles. No data rendering is performed.','mesh':str(mesh),'mesh_sha256':sha(mesh),'fits':fits}
            # Rendered crop is reference QA only, never a scientific layer of the replacement.
            page_image=OUT/f'attachment_page-{page_index+1}.png'
            if page_image.exists():
                im=Image.open(page_image);sx=im.width/612;sy=im.height/792;crop=im.crop((round(origin[0]*sx),round(top*sy),round((origin[0]+w)*sx),round((top+h)*sy)))
                target=OUT/f'reference_fig{n:02d}_crop.png';crop.save(target);record['reference_qa_crop']={'path':str(target),'sha256':sha(target),'pixels':list(crop.size)}
            records.append(record)
    result={'source_pdf':{'path':str(SOURCE),'sha256':sha(SOURCE),'bytes':SOURCE.stat().st_size,'pages':len(reader.pages),'page_size_pt':[612,792]},
            'coordinate_convention':'All panel rectangles are [left,bottom,width,height] in original figure Form points (1 point=1/72 inch). World coordinates are metres. Text boxes are local top-left PDF points.',
            'retained_figure1':image_evidence[0],'figures':records,'composition_rules':['Use only solver-native raster/EPS science layers; the reference crops are QA only.','No external redrawing of vectors, cell polygons, contours or data colours.','Uniform scale of native scientific viewports only; match world bounds and equal x/y physical scale before placement.','Native colour strips retain original RGB values and scalar range; labels may be re-typeset outside the native data area.','Keep every overall target box exactly, including the 143 mm Figure6 stack and 160x74 mm Figure2.'],
            'export_target':'data/native_figures_2026-11-10/fig04_rsm_vectors.pdf/png; fig05_rsm_yplus.pdf/png; fig06_enhanced_combined.pdf/png',
            'script':{'path':str(Path(__file__)),'sha256':sha(Path(__file__))}}
    (OUT/'reference_layout_audit.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
    with (OUT/'reference_panel_sizes.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f);w.writerow(['figure','panel','left_pt','bottom_pt','width_pt','height_pt','width_mm','height_mm','xmin_m','xmax_m','ymin_m','ymax_m'])
        for r in records:
            for p in r['panels']:w.writerow([r['figure'],p['name'],*p['form_box_bottom_left_pt'],*p['physical_size_mm'],*p['world_bounds_m']])
    print('Extracted exact Figures2/4/5/6 boxes, 8 scientific panels, 4 native colour-strip boxes; Figure1 raster identity verified.')

if __name__=='__main__':main()
