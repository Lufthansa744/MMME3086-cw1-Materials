"""Compact submission figures: native CAD image panels and exact mesh segments."""
import base64
import argparse
import csv
import hashlib
import html
import json
import math
from pathlib import Path
from xml.etree import ElementTree
from PIL import Image
import numpy as np
from plot_taskA_mesh import parse_mesh

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/taskA'
SRC=ROOT/'solver/taskA'
DETAIL_CENTRE_Y=-.007


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def base(width,height):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
            '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto-start-reverse"><path d="M0,0L6,3L0,6" fill="none" stroke="#222"/></marker></defs>',
            '<rect width="100%" height="100%" fill="white"/>','<g font-family="Arial,sans-serif" font-size="30" fill="#222">']


def text(svg,x,y,label,size=30,anchor='start',color='#222',back=False):
    if back: svg.append(f'<rect x="{x-5}" y="{y-size}" width="{len(label)*size*.57+10}" height="{size+8}" fill="white" fill-opacity="0.96"/>')
    svg.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{color}">{html.escape(label)}</text>')


def line(svg,a,b,color='#333',dash='',arrows=False):
    attrs=f' stroke-dasharray="{dash}"' if dash else ''
    if arrows: attrs+=' marker-start="url(#arr)" marker-end="url(#arr)"'
    svg.append(f'<path d="M{a[0]:.3f},{a[1]:.3f}L{b[0]:.3f},{b[1]:.3f}" fill="none" stroke="{color}" stroke-width="1.5"{attrs}/>')


def figure1():
    sources=[SRC/'taskA_geometry_native.png',SRC/'taskA_geometry_native_local.png']
    crops=[]
    for i,p in enumerate(sources):
        im=Image.open(p).convert('RGB'); a=np.asarray(im)
        mask=a.min(axis=2)<245 if i==0 else a.min(axis=2)>245
        ys,xs=np.where(mask)
        bbox=(int(xs.min()),int(ys.min()),int(xs.max()+1),int(ys.max()+1))
        pad=5 if i==0 else 40
        box=(max(0,bbox[0]-pad),max(0,bbox[1]-pad),min(im.width,bbox[2]+pad),min(im.height,bbox[3]+pad))
        target=OUT/('figure1_native_full_crop.png' if i==0 else 'figure1_native_detail_crop.png')
        im.crop(box).save(target)
        crops.append({'source':str(p),'sha256':sha(p),'source_size':im.size,'detected_bbox_px':bbox,'crop_box_px':box,'crop':str(target),'crop_sha256':sha(target)})
    svg=base(1600,530)
    placements=[(100,65,1350),(340,285,920)]
    for item,(x,y,w) in zip(crops,placements):
        crop=Path(item['crop']); im=Image.open(crop)
        h=w*im.height/im.width
        encoded=base64.b64encode(crop.read_bytes()).decode()
        svg.append(f'<image x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{encoded}"/>')
        item['placement_svg_px']={'x':x,'y':y,'width':w,'height':h,'uniform_scale':w/im.width}
    text(svg,25,105,'(a)',36);text(svg,25,332,'(b)',36)
    c=crops[0]; scale=c['placement_svg_px']['uniform_scale']; box=c['crop_box_px']; b=c['detected_bbox_px']
    xleft=100+(b[0]-box[0])*scale; xright=100+(b[2]-box[0])*scale
    ytop=65+(b[1]-box[1])*scale; ybottom=65+(b[3]-box[1])*scale
    line(svg,(xleft,44),(xright,44),arrows=True);text(svg,(xleft+xright)/2,34,'1000 mm',36,'middle')
    line(svg,(1480,ytop),(1480,ybottom),arrows=True);text(svg,1510,(ytop+ybottom)/2+12,'150',36);text(svg,1510,(ytop+ybottom)/2+48,'mm',36)
    line(svg,(200,175),(400,175));svg.append('<path d="M385,167L400,175L385,183" fill="none" stroke="#222" stroke-width="2"/>');text(svg,200,151,'Inlet flow',32)
    # Pixel/world transform from the actual native export's Frame and projection size.
    dense=list(csv.DictReader((SRC/'cad_edge_dense_coordinates_m.csv').open()))
    edges=list(csv.DictReader((SRC/'boundary_edges.csv').open()))
    pressure=next(r for r in edges if r['name']=='aerofoil_pressure');suction=next(r for r in edges if r['name']=='aerofoil_suction')
    le_world=(float(pressure['start_x_m']),float(pressure['start_y_m']))
    if math.dist(le_world,(float(suction['start_x_m']),float(suction['start_y_m'])))>1e-12:raise ValueError('Actual LE endpoints do not match')
    tepoints=[r for r in dense if r['edge']=='0']
    te=(sum(float(r['x_m']) for r in [tepoints[0],tepoints[-1]])/2,sum(float(r['y_m']) for r in [tepoints[0],tepoints[-1]])/2)
    c=crops[1]; cropbox=c['crop_box_px']; pl=c['placement_svg_px']; sw,sh=c['source_size']; native_scale=sh/.09
    def point(x,y):
        px=sw/2+(x-.05)*native_scale; py=sh/2-(y-DETAIL_CENTRE_Y)*native_scale
        return pl['x']+(px-cropbox[0])*pl['uniform_scale'],pl['y']+(py-cropbox[1])*pl['uniform_scale']
    le=point(*le_world); te_img=point(*te)
    line(svg,le,te_img,'#555','8 5');line(svg,le,(le[0]+235,le[1]),'#555','5 5')
    angle=math.atan2(te_img[1]-le[1],te_img[0]-le[0]);r=165
    svg.append(f'<path d="M{le[0]+r},{le[1]}A{r},{r} 0 0 1 {le[0]+r*math.cos(angle)},{le[1]+r*math.sin(angle)}" fill="none" stroke="#222" stroke-width="2"/>')
    text(svg,le[0]+r+16,le[1]+30,'8°',36)
    text(svg,800,516,'100 mm chord',36,'middle')
    text(svg,1295,395,'NACA0012',36)
    svg.append('</g></svg>'); out=OUT/'figure1_native_compact.svg';out.write_text('\n'.join(svg),encoding='utf-8');ElementTree.parse(out)
    return {'sources_and_crops':crops,'geometry_evidence':[{'path':str(p),'sha256':sha(p)} for p in [SRC/'export_geometry_native.py',SRC/'cad_edge_dense_coordinates_m.csv',SRC/'boundary_edges.csv',SRC/'taskA_geometry.scdoc']],
            'annotation_method':'Native PNG pixel content preserved through lossless crop; SVG placement uniformly scales each panel. Only dimension/flow/chord/angle annotations added. No geometry re-rendering, recolouring, stretching, replacement or redrawing.',
            'actual_LE_m':le_world,'actual_TE_centre_m':te,'actual_chord_m':math.dist(le_world,te),
            'local_projection':{'frame_centre_m':[.05,DETAIL_CENTRE_Y,0],'vertical_extent_m':.09,'derived_native_pixels_per_m':native_scale},'output':str(out),'sha256':sha(out),'size_svg_px':[1600,530],'minimum_annotation_font_px':32}


def figure2():
    source=SRC/'taskA_baseline.msh';nodes,faces,zones,counts=parse_mesh(source)
    svg=base(1600,740)
    edges=list(csv.DictReader((SRC/'boundary_edges.csv').open()));edge=next(r for r in edges if r['name']=='aerofoil_pressure');dx,dy=float(edge['start_x_m']),float(edge['start_y_m'])
    bounds=(-.006+dx,.109+dx,-.024+dy,.012+dy); lx,ly,s=300,350,9000;lw=(bounds[1]-bounds[0])*s;lh=(bounds[3]-bounds[2])*s
    svg.insert(1,f'<defs><clipPath id="lc"><rect x="{lx}" y="{ly}" width="{lw}" height="{lh}"/></clipPath></defs>')
    def full(p):return 120+(p[0]+.5)*1300,80+(.075-p[1])*1300
    def local(p):return lx+(p[0]-bounds[0])*s,ly+(bounds[3]-p[1])*s
    def draw(ids,trans,color,stroke,clip=False):
        segments=[];n=0
        for fid in ids:
            a,b=[nodes[q] for q in faces[fid][:2]]
            if clip and (max(a[0],b[0])<bounds[0] or min(a[0],b[0])>bounds[1] or max(a[1],b[1])<bounds[2] or min(a[1],b[1])>bounds[3]):continue
            p,q=trans(a),trans(b);segments.append(f'M{p[0]:.4f},{p[1]:.4f}L{q[0]:.4f},{q[1]:.4f}');n+=1
        clip_attr=' clip-path="url(#lc)"' if clip else ''
        svg.append(f'<path d="{" ".join(segments)}" fill="none" stroke="{color}" stroke-width="{stroke}"{clip_attr}/>');return n
    names=['inlet','outlet','wall_top','wall_bottom','aerofoil_suction','aerofoil_pressure','aerofoil_te']
    colors=dict(zip(names,['#009e73','#cc79a7','#222','#222','#0072b2','#d55e00','#222']))
    total=draw(sorted(faces),full,'#777',.55)
    for n in names:draw(zones[n]['faces'],full,colors[n],1.8)
    text(svg,25,112,'(a)',32);text(svg,25,390,'(b)',32)
    line(svg,(120,38),(1420,38),arrows=True);text(svg,770,29,'1000 mm',30,'middle')
    text(svg,770,72,'wall_top',30,'middle');text(svg,770,312,'wall_bottom',30,'middle')
    text(svg,110,190,'inlet',30,'end',colors['inlet']);text(svg,1434,190,'outlet',30,color=colors['outlet'])
    line(svg,(1490,80),(1490,275),arrows=True);text(svg,1510,236,'150',28);text(svg,1510,267,'mm',28)
    a,b=full((bounds[0],bounds[3])),full((bounds[1],bounds[2]))
    svg.append(f'<rect x="{a[0]}" y="{a[1]}" width="{b[0]-a[0]}" height="{b[1]-a[1]}" fill="none" stroke="#111" stroke-width="2" stroke-dasharray="7 4"/>')
    local_count=draw(sorted(faces),local,'#777',.65,True)
    for n in names[-3:]:draw(zones[n]['faces'],local,colors[n],2.7,True)
    svg.append(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="none" stroke="#333" stroke-width="1.4"/>')
    for xmm in [0,50,100]:
        x,y=local((xmm/1000,bounds[2]));line(svg,(x,y),(x,y+7));text(svg,x,y+34,str(xmm),28,'middle')
    for ymm in [20,10,0,-10,-20,-30]:
        if not bounds[2]<=ymm/1000<=bounds[3]:continue
        x,y=local((bounds[0],ymm/1000));line(svg,(x-7,y),(x,y));text(svg,x-15,y+10,str(ymm),28,'end')
    text(svg,lx+lw/2,736,'x (mm)',28,'middle')
    svg.append('<text x="190" y="515" font-size="28" text-anchor="middle" transform="rotate(-90,190,515)">y (mm)</text>')
    def mid(n):
        f=faces[zones[n]['faces'][len(zones[n]['faces'])//2]]
        return local(tuple((nodes[f[0]][i]+nodes[f[1]][i])/2 for i in [0,1]))
    line(svg,(850,390),mid('aerofoil_suction'),colors['aerofoil_suction']);text(svg,705,387,'aerofoil_suction',30,color=colors['aerofoil_suction'],back=True)
    line(svg,(820,620),mid('aerofoil_pressure'),colors['aerofoil_pressure']);text(svg,670,650,'aerofoil_pressure',30,color=colors['aerofoil_pressure'],back=True)
    line(svg,(1400,610),mid('aerofoil_te'));text(svg,1362,642,'aerofoil_te',28,back=True)
    svg.append('</g></svg>');out=OUT/'figure2_mesh_compact.svg';out.write_text('\n'.join(svg),encoding='utf-8');ElementTree.parse(out)
    return {'source':str(source),'source_sha256':sha(source),'counts':counts,'method':'Exact original face segments; no smoothing or retriangulation. Equal coordinate scale on both axes in each panel.',
            'full_faces_drawn':total,'local_intersecting_face_selection':local_count,'local_bounds_m':bounds,'full_scale_px_per_m':1300,'local_scale_px_per_m':s,
            'source_coordinate_units':'m','labels_units':'mm','minimum_font_px':28,'font_at_170mm_width_pt':28/1600*170*72/25.4,
            'figure':str(out),'figure_sha256':sha(out),'size_svg_px':[1600,740]}


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--source',default='solver/taskA');parser.add_argument('--detail-centre-y',type=float,default=-.007);args=parser.parse_args()
    SRC=ROOT/args.source;DETAIL_CENTRE_Y=args.detail_centre_y
    OUT.mkdir(parents=True,exist_ok=True)
    result={'figure1':figure1(),'figure2':figure2(),'script':{'path':str(Path(__file__).resolve()),'sha256':sha(Path(__file__))}}
    (OUT/'compact_figures_manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print('Compact native geometry and exact mesh SVGs saved')
