"""Plot actual native Fluent mesh faces; no retriangulation or smoothing."""
from collections import defaultdict
import hashlib
import html
import json
import math
from pathlib import Path
import re
import struct
from xml.etree import ElementTree

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'solver/taskA/taskA_baseline.msh'
OUT=ROOT/'data/taskA'


def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_mesh(path):
    # Binary section interpretation independently checked in review/verify_baseline_mesh.py.
    blob=path.read_bytes()
    def integer(token): return int(token,16)
    def start(match):
        offset=match.end()
        while blob[offset:offset+1] in [b' ',b'\r',b'\n',b'\t']: offset+=1
        if blob[offset:offset+1]!=b'(': raise ValueError('Binary payload opener absent')
        return offset+1
    counts={}
    for typ,name in [(10,'nodes'),(12,'cells'),(13,'faces')]:
        match=re.search(rb'\('+str(typ).encode()+rb' \(0 1 ([0-9a-fA-F]+) 0\)\)',blob[:600])
        if not match: raise ValueError('Missing mesh count')
        counts[name]=integer(match.group(1))
    if not re.search(rb'\(2 2\)',blob[:600]): raise ValueError('Expected 2D mesh')
    nodes={}
    for m in re.finditer(rb'\(3010 \(([0-9a-fA-F ]+)\)',blob):
        zone,first,last,kind,dim=map(integer,m.group(1).split())
        if dim!=2: raise ValueError('Only two-coordinate nodes supported')
        n=last-first+1
        values=struct.unpack_from('<'+'d'*(n*2),blob,start(m))
        for i in range(n): nodes[first+i]=(values[2*i],values[2*i+1])
    faces={}; zone_faces=defaultdict(list)
    for m in re.finditer(rb'\(2013 \(([0-9a-fA-F ]+)\)',blob):
        zone,first,last,kind,element=map(integer,m.group(1).split())
        if element!=2: raise ValueError('Expected line-segment 2D faces')
        n=last-first+1
        values=struct.unpack_from('<'+'i'*(n*4),blob,start(m))
        for i in range(n):
            face=tuple(values[4*i:4*i+4])
            if face[0] not in nodes or face[1] not in nodes: raise ValueError('Invalid node reference')
            faces[first+i]=face; zone_faces[zone].append(first+i)
    zones={}
    for m in re.finditer(rb'\(45 \((\d+) ([a-z-]+) ([a-zA-Z0-9_-]+)\)\(\)\)',blob):
        raw,kind,name=[x.decode() for x in m.groups()]
        zones[name]={'id':int(raw),'type':kind,'faces':zone_faces[int(raw)]}
    if len(nodes)!=counts['nodes'] or len(faces)!=counts['faces']: raise ValueError('Incomplete node/face coverage')
    if not all(math.isfinite(q) for p in nodes.values() for q in p): raise ValueError('Nonfinite coordinate')
    return nodes,faces,zones,counts


def main():
    nodes,faces,zones,counts=parse_mesh(SOURCE)
    required=['inlet','outlet','wall_top','wall_bottom','aerofoil_suction','aerofoil_pressure','aerofoil_te']
    if any(n not in zones for n in required): raise ValueError('Missing boundary zone')
    full_bounds=(-.5,.5,-.075,.075)
    local_bounds=(-.012,.115,-.035,.020)
    width,height=1600,1160
    full=(160,190,1200)
    local=(250,540,9000)
    def transform(view,bounds,p):
        x0,y0,s=view; xmin,xmax,ymin,ymax=bounds
        return x0+(p[0]-xmin)*s,y0+(ymax-p[1])*s
    def dims(view,bounds):
        return view[0],view[1],(bounds[1]-bounds[0])*view[2],(bounds[3]-bounds[2])*view[2]
    lx,ly,lw,lh=dims(local,local_bounds)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto-start-reverse"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#333"/></marker>',
         f'<clipPath id="localclip"><rect x="{lx}" y="{ly}" width="{lw}" height="{lh}"/></clipPath></defs>',
         '<rect width="100%" height="100%" fill="white"/>','<g font-family="Arial,sans-serif" fill="#222" font-size="20">']
    def text(x,y,s,size=20,anchor='start',color='#222'):
        svg.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" text-anchor="{anchor}" fill="{color}">{html.escape(s)}</text>')
    def line(a,b,color='#444',dash='',arrows=False):
        attrs=f' stroke-dasharray="{dash}"' if dash else ''
        if arrows: attrs+=' marker-start="url(#arrow)" marker-end="url(#arrow)"'
        svg.append(f'<path d="M{a[0]:.3f},{a[1]:.3f} L{b[0]:.3f},{b[1]:.3f}" stroke="{color}" stroke-width="1.3" fill="none"{attrs}/>')
    def face_path(ids,view,bounds,color,stroke,clip=False):
        path=[]; selected=0
        for fid in ids:
            a,b=[nodes[n] for n in faces[fid][:2]]
            if clip and (max(a[0],b[0])<bounds[0] or min(a[0],b[0])>bounds[1] or max(a[1],b[1])<bounds[2] or min(a[1],b[1])>bounds[3]): continue
            pa,pb=transform(view,bounds,a),transform(view,bounds,b)
            path.append(f'M{pa[0]:.4f},{pa[1]:.4f}L{pb[0]:.4f},{pb[1]:.4f}')
            selected+=1
        attrs=' clip-path="url(#localclip)"' if clip else ''
        svg.append(f'<path d="{" ".join(path)}" stroke="{color}" stroke-width="{stroke}" fill="none"{attrs}/>')
        return selected
    text(70,45,'Task A baseline triangular mesh',29)
    text(70,80,f'{counts["nodes"]:,} nodes · {counts["cells"]:,} triangular cells · {counts["faces"]:,} native face segments',20)
    text(70,125,'(a) Complete computational domain',22)
    all_faces=sorted(faces)
    full_count=face_path(all_faces,full,full_bounds,'#777',.55)
    colors={'inlet':'#009e73','outlet':'#cc79a7','wall_top':'#333','wall_bottom':'#333','aerofoil_suction':'#0072b2','aerofoil_pressure':'#d55e00','aerofoil_te':'#222'}
    for name in required: face_path(zones[name]['faces'],full,full_bounds,colors[name],1.8)
    text(145,285,'inlet',20,'end',colors['inlet']); text(1378,285,'outlet',20,color=colors['outlet'])
    text(760,178,'wall_top',20,'middle'); text(760,403,'wall_bottom',20,'middle')
    line((160,151),(1360,151),arrows=True); text(760,142,'1000 mm',18,'middle')
    line((1470,190),(1470,370),arrows=True); text(1490,285,'150 mm',16)
    for x in [-.5,-.25,0,.25,.5]:
        px,py=transform(full,full_bounds,(x,-.075))
        text(px,434,f'{x*1000:.0f}',17,'middle')
    text(760,465,'x (mm)',19,'middle')
    # Mark the actual local region on the full mesh without modifying its cells.
    ra=transform(full,full_bounds,(local_bounds[0],local_bounds[3])); rb=transform(full,full_bounds,(local_bounds[1],local_bounds[2]))
    svg.append(f'<rect x="{ra[0]}" y="{ra[1]}" width="{rb[0]-ra[0]}" height="{rb[1]-ra[1]}" fill="none" stroke="#111" stroke-width="1.6" stroke-dasharray="7 4"/>')
    text(70,510,'(b) Enlarged region around the aerofoil; equal x and y scales',22)
    local_count=face_path(all_faces,local,local_bounds,'#777',.65,True)
    for name in ['aerofoil_suction','aerofoil_pressure','aerofoil_te']:
        face_path(zones[name]['faces'],local,local_bounds,colors[name],2.4,True)
    svg.append(f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" fill="none" stroke="#333" stroke-width="1.3"/>')
    for xmm in [0,20,40,60,80,100]:
        px,py=transform(local,local_bounds,(xmm/1000,local_bounds[2]))
        line((px,py),(px,py+7)); text(px,py+28,str(xmm),17,'middle')
    for ymm in [-30,-20,-10,0,10,20]:
        px,py=transform(local,local_bounds,(local_bounds[0],ymm/1000))
        line((px-7,py),(px,py));text(px-15,py+6,str(ymm),17,'end')
    text(lx+lw/2,lh+ly+62,'x (mm)',19,'middle')
    svg.append(f'<text x="{lx-80}" y="{ly+lh/2}" font-size="19" text-anchor="middle" transform="rotate(-90,{lx-80},{ly+lh/2})">y (mm)</text>')
    def boundary_mid(name):
        segs=[faces[i] for i in zones[name]['faces']]
        f=segs[len(segs)//2]
        return tuple((nodes[f[0]][i]+nodes[f[1]][i])/2 for i in [0,1])
    # Read actual boundary-face centroids for label leader endpoints.
    ps=transform(local,local_bounds,boundary_mid('aerofoil_suction'))
    pp=transform(local,local_bounds,boundary_mid('aerofoil_pressure'))
    pt=transform(local,local_bounds,boundary_mid('aerofoil_te'))
    # White text backgrounds preserve readable labels without changing the actual line geometry.
    def label(x,y,s,color):
        w=len(s)*11.8
        svg.append(f'<rect x="{x-5}" y="{y-21}" width="{w+10}" height="27" fill="white" fill-opacity="0.96"/>')
        text(x,y,s,20,color=color)
    line((680,610),ps,colors['aerofoil_suction']); label(620,599,'aerofoil_suction',colors['aerofoil_suction'])
    line((710,930),pp,colors['aerofoil_pressure']); label(620,958,'aerofoil_pressure',colors['aerofoil_pressure'])
    line((1310,895),pt); label(1265,924,'aerofoil_te','#222')
    text(70,1120,'Source: native taskA_baseline.msh; exact exported face connectivity, with no retriangulation or smoothing',17)
    svg.append('</g></svg>')
    OUT.mkdir(parents=True,exist_ok=True)
    target=OUT/'figure2_baseline_mesh.svg'
    target.write_text('\n'.join(svg),encoding='utf-8'); ElementTree.parse(target)
    audit={'source':str(SOURCE),'source_sha256':sha(SOURCE),'source_bytes':SOURCE.stat().st_size,'counts':counts,
           'parser_reference':{'path':str(ROOT/'review/verify_baseline_mesh.py'),'sha256':sha(ROOT/'review/verify_baseline_mesh.py')},
           'script':{'path':str(Path(__file__).resolve()),'sha256':sha(Path(__file__))},
           'method':'Read little-endian binary 3010 double node coordinates and 2013 integer face connectivity; draw exact face segments. No smoothing, reconstruction or point triangulation.',
           'coordinate_units':'m','display_axis_units':'mm','full_equal_scale_pixels_per_m':full[2],'local_equal_scale_pixels_per_m':local[2],
           'full_bounds_m':full_bounds,'local_bounds_m':local_bounds,'full_unique_faces_drawn':full_count,'local_faces_with_intersecting_bounding_box':local_count,
           'boundary_faces':{name:len(zones[name]['faces']) for name in required},'figure':{'path':str(target),'sha256':sha(target)}}
    (OUT/'figure2_mesh_manifest.json').write_text(json.dumps(audit,indent=2),encoding='utf-8')
    print(json.dumps({'source_sha256':audit['source_sha256'],'counts':counts,'full_faces_drawn':full_count,'local_faces':local_count},indent=2))


if __name__=='__main__': main()
