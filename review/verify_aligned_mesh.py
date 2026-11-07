"""Independent read-only parser for this native 2D binary Fluent triangle mesh."""
from collections import Counter, defaultdict, deque
import hashlib
import json
import math
from pathlib import Path
import re
import struct

root = Path(__file__).resolve().parent.parent
path = globals().get('mesh_source_override', root / 'solver/aligned_taskA/taskA_baseline.msh')
blob = path.read_bytes()
def integer(token): return int(token, 16)
def payload_start(match):
    offset = match.end()
    while blob[offset:offset+1] in [b' ', b'\r', b'\n', b'\t']:
        offset += 1
    if blob[offset:offset+1] != b'(':
        raise ValueError('Expected binary payload opener')
    return offset + 1

counts = {}
for typ, name in [(10, 'nodes'), (12, 'cells'), (13, 'faces')]:
    match = re.search(rb'\(' + str(typ).encode() + rb' \(0 1 ([0-9a-fA-F]+) 0\)\)', blob[:600])
    counts[name] = integer(match.group(1))
assert re.search(rb'\(2 2\)', blob[:600]), 'Mesh must be 2D'
nodes = {}
for match in re.finditer(rb'\(3010 \(([0-9a-fA-F ]+)\)', blob):
    zone, first, last, kind, dim = map(integer, match.group(1).split())
    assert dim == 2
    count = last - first + 1
    data = struct.unpack_from('<' + 'd' * (count * dim), blob, payload_start(match))
    for i in range(count): nodes[first+i] = (data[i*2], data[i*2+1])
faces = {}
zone_faces = defaultdict(list)
cell_faces = defaultdict(list)
neighbors = defaultdict(set)
for match in re.finditer(rb'\(2013 \(([0-9a-fA-F ]+)\)', blob):
    zone, first, last, kind, element = map(integer, match.group(1).split())
    assert element == 2, '2D faces must be line segments'
    count = last - first + 1
    data = struct.unpack_from('<' + 'i' * (count * 4), blob, payload_start(match))
    for i in range(count):
        a, b, c, d = data[i*4:i*4+4]
        assert a in nodes and b in nodes and a != b
        assert 0 <= c <= counts['cells'] and 0 <= d <= counts['cells'] and (c or d)
        idx = first+i
        faces[idx] = (a, b, c, d)
        zone_faces[zone].append(idx)
        for cell in [c, d]:
            if cell: cell_faces[cell].append(idx)
        if c and d:
            neighbors[c].add(d); neighbors[d].add(c)
cell_headers = []
for match in re.finditer(rb'\(2012 \(([0-9a-fA-F ]+)\)', blob):
    values = list(map(integer, match.group(1).split()))
    cell_headers.append(values)
    assert values[-1] == 1, 'Only triangle cell type accepted by this audit'
assert len(nodes) == counts['nodes'] and len(faces) == counts['faces']
assert len(cell_faces) == counts['cells']
assert set(cell_faces) == set(range(1, counts['cells']+1))
cell_stats = []
test_point = (.00048367698354395+.05*math.cos(math.radians(-8)), .00691690311771526+.05*math.sin(math.radians(-8)))
foil_point_in_cells = []
def cross(a,b,c): return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
for cell, incident in cell_faces.items():
    assert len(incident) == 3
    vertices = sorted({node for f in incident for node in faces[f][:2]})
    assert len(vertices) == 3
    p = [nodes[node] for node in vertices]
    area = abs(cross(*p))/2
    assert area > 0
    lengths = [math.dist(p[i],p[(i+1)%3]) for i in range(3)]
    angles = []
    for i in range(3):
        a,b,c = lengths[i],lengths[(i+1)%3],lengths[(i+2)%3]
        angles.append(math.degrees(math.acos(max(-1,min(1,(a*a+b*b-c*c)/(2*a*b))))))
    skew = max((max(angles)-60)/120,(60-min(angles))/60)
    quality = 4*math.sqrt(3)*area/sum(x*x for x in lengths)
    signs = [cross(p[i],p[(i+1)%3],test_point) for i in range(3)]
    if min(signs) >= 0 or max(signs) <= 0: foil_point_in_cells.append(cell)
    cell_stats.append((area,quality,skew,min(angles)))
seen = {1}; queue=deque([1])
while queue:
    for cell in neighbors[queue.popleft()]:
        if cell not in seen: seen.add(cell);queue.append(cell)
boundary = [f for f,v in faces.items() if not(v[2] and v[3])]
boundary_graph = defaultdict(set)
for f in boundary:
    a,b = faces[f][:2]
    boundary_graph[a].add(b);boundary_graph[b].add(a)
assert all(len(v)==2 for v in boundary_graph.values())
unseen=set(boundary_graph);loops=[]
while unseen:
    start=next(iter(unseen));group={start};todo=[start];unseen.remove(start)
    while todo:
        for node in boundary_graph[todo.pop()]:
            if node in unseen: unseen.remove(node);group.add(node);todo.append(node)
    loops.append(len(group))
zones=[]
for match in re.finditer(rb'\(45 \((\d+) ([a-z-]+) ([a-zA-Z0-9_-]+)\)\(\)\)',blob):
    raw,kind,name = [x.decode() for x in match.groups()]
    zone=int(raw)
    ids=zone_faces.get(zone,[])
    lengths=[math.dist(nodes[faces[i][0]],nodes[faces[i][1]]) for i in ids]
    zones.append({'id_as_written':raw,'type':kind,'name':name,'face_count':len(ids),
                  'min_edge_length_m':min(lengths) if lengths else None,
                  'max_edge_length_m':max(lengths) if lengths else None})
result={'source':str(path),'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest(),
        'counts':counts,'dimension':2,'cell_headers_hex_decoded':cell_headers,'all_cells_triangles':True,
        'x_bounds_m':[min(x for x,y in nodes.values()),max(x for x,y in nodes.values())],
        'y_bounds_m':[min(y for x,y in nodes.values()),max(y for x,y in nodes.values())],
        'connected_fluid_cells':len(seen),'all_cells_one_component':len(seen)==counts['cells'],
        'boundary_face_count':len(boundary),'boundary_loop_vertex_counts':sorted(loops),
        'euler_V_minus_E_plus_C':len(nodes)-len(faces)+len(cell_faces),
        'cell_area_min_m2':min(v[0] for v in cell_stats),'cell_area_max_m2':max(v[0] for v in cell_stats),
        'total_cell_area_m2':sum(v[0] for v in cell_stats),
        'minimum_triangle_mean_ratio':min(v[1] for v in cell_stats),
        'maximum_triangle_equiangle_skew':max(v[2] for v in cell_stats),
        'minimum_triangle_angle_degrees':min(v[3] for v in cell_stats),
        'cells_containing_foil_interior_test_point':foil_point_in_cells,'zones':zones,
        'limitation':'Independent topology and triangle-geometry checks; computed mean-ratio/equiangle-skew are explicitly defined here and are not claimed to be Fluent orthogonal-quality metrics. Actual Fluent mesh check/quality and rendered mesh still required.'}
target=globals().get('mesh_audit_target_override', Path(__file__).parent/'aligned_mesh_audit.json')
target.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
