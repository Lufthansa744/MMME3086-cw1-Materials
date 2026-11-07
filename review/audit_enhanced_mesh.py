"""Read-only binary 2D enhanced-mesh topology and actual geometry audit."""
from collections import Counter, defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import struct

root=Path(__file__).resolve().parent.parent
path=root/'inputs/Aerofoil8-degAoA-enhancedBL.msh'
blob=path.read_bytes()
def hx(v): return int(v,16)
def start(m):
    i=m.end()
    while blob[i:i+1] in [b' ',b'\n',b'\r',b'\t']:i+=1
    assert blob[i:i+1]==b'('
    return i+1
nodes={};faces={};zone_faces=defaultdict(list);cell_faces=defaultdict(list)
for m in re.finditer(rb'\(3010 \(([0-9a-fA-F ]+)\)',blob):
    zone,first,last,kind,dim=map(hx,m.group(1).split());assert dim==2
    a=struct.unpack_from('<'+'d'*((last-first+1)*2),blob,start(m))
    for i in range(last-first+1):nodes[first+i]=a[i*2:i*2+2]
for m in re.finditer(rb'\(2013 \(([0-9a-fA-F ]+)\)',blob):
    zone,first,last,kind,elem=map(hx,m.group(1).split());assert elem==2
    a=struct.unpack_from('<'+'i'*((last-first+1)*4),blob,start(m))
    for i in range(last-first+1):
        f=first+i;faces[f]=a[i*4:i*4+4];zone_faces[zone].append(f)
        for cell in faces[f][2:]:
            if cell:cell_faces[cell].append(f)
cell_types=[]
for m in re.finditer(rb'\(2012 \(([0-9a-fA-F ]+)\)',blob):
    zone,first,last,kind,elem=map(hx,m.group(1).split())
    if elem==0:cell_types.extend(struct.unpack_from('<'+'i'*(last-first+1),blob,start(m)))
    else:cell_types.extend([elem]*(last-first+1))
zones={}
for m in re.finditer(rb'\(45 \((\d+) ([a-z-]+) ([a-zA-Z0-9_-]+)\)\(\)\)',blob):
    zone,kind,name=m.groups();zones[name.decode()]={'id':int(zone),'type':kind.decode()}
def ends(name):
    degree=Counter(n for f in zone_faces[zones[name]['id']] for n in faces[f][:2])
    return {n for n,d in degree.items() if d==1}
pe,se=ends('aerofoil-pressure'),ends('aerofoil-suction')
le_ids=pe&se;assert len(le_ids)==1
le=nodes[next(iter(le_ids))]
te_ids=(pe|se)-le_ids;assert len(te_ids)==2
te=tuple(sum(nodes[n][i] for n in te_ids)/2 for i in [0,1])
delta=tuple(te[i]-le[i] for i in [0,1])
cell_vertex_counts=Counter()
for c,fs in cell_faces.items():
    ns={n for f in fs for n in faces[f][:2]}
    cell_vertex_counts[len(ns)]+=1
boundary_graph=defaultdict(set)
for a,b,c,d in faces.values():
    if not(c and d):boundary_graph[a].add(b);boundary_graph[b].add(a)
assert all(len(v)==2 for v in boundary_graph.values())
unseen=set(boundary_graph);loops=[]
while unseen:
    first=next(iter(unseen));unseen.remove(first);component={first};todo=[first]
    while todo:
        for n in boundary_graph[todo.pop()]:
            if n in unseen:unseen.remove(n);component.add(n);todo.append(n)
    loops.append(len(component))
result={'source':str(path),'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),
        'nodes':len(nodes),'faces':len(faces),'cells':len(cell_faces),
        'cell_type_codes':dict(Counter(cell_types)),'actual_cell_vertex_counts':dict(cell_vertex_counts),
        'x_bounds_m':[min(x for x,y in nodes.values()),max(x for x,y in nodes.values())],
        'y_bounds_m':[min(y for x,y in nodes.values()),max(y for x,y in nodes.values())],
        'boundary_loop_vertex_counts':sorted(loops),'euler':len(nodes)-len(faces)+len(cell_faces),
        'leading_edge_m':le,'trailing_edge_centre_m':te,'chord_m':math.hypot(*delta),
        'chord_angle_deg':math.degrees(math.atan2(delta[1],delta[0])),
        'trailing_edge_gap_m':math.dist(*(nodes[n] for n in te_ids)),
        'zones':{name:{**v,'face_count':len(zone_faces[v['id']])} for name,v in zones.items()}}
target=Path(__file__).parent/'enhanced_mesh_geometry_audit.json'
target.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
