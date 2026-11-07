"""Cross-check actual Fluent cell IDs/centres and foil wall faces against native mesh."""
import contextlib
from collections import defaultdict
import csv
import hashlib
import importlib.util
import io
import json
import math
from pathlib import Path
import statistics
import argparse

root=Path(__file__).resolve().parent.parent
parser=argparse.ArgumentParser()
parser.add_argument('case_id')
parser.add_argument('--enhanced',action='store_true')
parser.add_argument('--aligned',action='store_true')
parser.add_argument('--grid',choices=['medium','fine'])
args=parser.parse_args()
assert sum([bool(args.enhanced),bool(args.aligned),bool(args.grid)])<=1,'Select exactly one mesh family'
reader='audit_enhanced_mesh.py' if args.enhanced else ('verify_aligned_mesh.py' if args.aligned or args.grid else 'verify_baseline_mesh.py')
spec=importlib.util.spec_from_file_location('mesh_audit',Path(__file__).parent/reader)
mesh=importlib.util.module_from_spec(spec)
if args.grid:
    mesh.mesh_source_override=root/f'solver/grid_{args.grid}_mesh/mesh.msh'
    mesh.mesh_audit_target_override=Path(__file__).parent/f'grid_{args.grid}_mesh_audit.json'
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(mesh)
raw=root/'solver'/args.case_id/'raw'
def read(name):
    return [{k.strip():float(v) for k,v in row.items()} for row in csv.DictReader((raw/name).open())]
domain=read('domain_cell_fields.csv')
by_id={int(row['cell-id']):row for row in domain}
center_options={'vertex_mean':{},'polygon_area_centroid':{}}
for cell,fs in mesh.cell_faces.items():
    ns={node for f in fs for node in mesh.faces[f][:2]}
    center_options['vertex_mean'][cell]=tuple(sum(mesh.nodes[n][i] for n in ns)/len(ns) for i in [0,1])
    adj=defaultdict(set)
    for f in fs:
        a,b=mesh.faces[f][:2];adj[a].add(b);adj[b].add(a)
    assert all(len(v)==2 for v in adj.values())
    ordered=[next(iter(ns))];previous=None
    while True:
        choices=adj[ordered[-1]]-({previous} if previous is not None else set())
        nxt=min(choices)
        if nxt==ordered[0]:break
        previous=ordered[-1];ordered.append(nxt)
    assert len(ordered)==len(ns)
    points=[mesh.nodes[n] for n in ordered]
    pairs=list(zip(points,points[1:]+points[:1]))
    crosses=[a[0]*b[1]-b[0]*a[1] for a,b in pairs]
    denominator=3*sum(crosses)
    center_options['polygon_area_centroid'][cell]=tuple(sum((a[i]+b[i])*c for (a,b),c in zip(pairs,crosses))/denominator for i in [0,1])
offsets={}
for definition,centers in center_options.items():
    for offset in [-1,0,1]:
        errors=[];missing=0
        for idx,row in by_id.items():
            if idx+offset not in centers: missing+=1;continue
            errors.append(math.dist((row['x-coordinate'],row['y-coordinate']),centers[idx+offset]))
        offsets[definition+':'+str(offset)]={'missing':missing,'max_center_error_m':max(errors),'median_center_error_m':statistics.median(errors)}
best=min(offsets,key=lambda x:(offsets[x]['missing'],offsets[x]['max_center_error_m']))
definition,offset_text=best.split(':');offset=int(offset_text)
assert len(by_id)==len(domain)==len(mesh.cell_faces)
assert offsets[best]['missing']==0 and offsets[best]['max_center_error_m']<1e-7
wall_results=[];cell_values=defaultdict(list)
zone_ids=[('suction_p_yplus.csv',10),('pressure_p_yplus.csv',9),('trailing_p_yplus.csv',11)] if args.enhanced else [('suction_p_yplus.csv',7),('pressure_p_yplus.csv',6),('trailing_p_yplus.csv',5)]
for name,zone in zone_ids:
    rows=read(name);face_ids=mesh.zone_faces[zone]
    used=set();records=[]
    for row in rows:
        point=(row['x-coordinate'],row['y-coordinate'])
        distances=[]
        for face in face_ids:
            a,b=mesh.faces[face][:2]
            center=tuple((mesh.nodes[a][i]+mesh.nodes[b][i])/2 for i in [0,1])
            distances.append((math.dist(point,center),face))
        error,face=min(distances)
        assert error<1e-7 and face not in used
        used.add(face)
        adjacent=next(c for c in mesh.faces[face][2:] if c)
        raw_id=int(row['cell-id'])
        assert raw_id+offset==adjacent
        domain_row=by_id[raw_id]
        value={'mesh_face':face,'raw_cell_id':raw_id,'mesh_cell_id':adjacent,
               'face_center_match_error_m':error,'wall_yplus':row['y-plus'],
               'domain_cell_yplus':domain_row['y-plus'],
               'yplus_difference':row['y-plus']-domain_row['y-plus'],
               'wall_pressure':row['pressure'],'domain_cell_pressure':domain_row['pressure']}
        records.append(value);cell_values[adjacent].append(value)
    wall_results.append({'file':name,'zone':zone,'rows':len(rows),'mesh_faces':len(face_ids),
                         'all_faces_mapped_once':len(used)==len(face_ids),
                         'max_face_center_error_m':max(v['face_center_match_error_m'] for v in records),
                         'max_yplus_difference_domain_vs_wall':max(abs(v['yplus_difference']) for v in records),
                         'records':records})
duplicates={str(c):values for c,values in cell_values.items() if len(values)>1}
result={'source_mesh_sha256':hashlib.sha256(mesh.blob).hexdigest(),
        'raw_hashes':{name:hashlib.sha256((raw/name).read_bytes()).hexdigest() for name in
                      ['domain_cell_fields.csv','suction_p_yplus.csv','pressure_p_yplus.csv','trailing_p_yplus.csv']},
        'domain_rows':len(domain),'unique_cell_ids':len(by_id),'raw_cell_id_range':[min(by_id),max(by_id)],
        'tested_raw_to_mesh_id_offsets':offsets,'accepted_raw_to_mesh_id_offset':offset,
        'accepted_centroid_definition':definition,
        'wall_mapping':wall_results,'foil_face_count':sum(len(v['records']) for v in wall_results),
        'unique_foil_adjacent_cells':len(cell_values),'multi_foil_face_cells':duplicates,
        'signed_velocity_ranges':{k:[min(r[k] for r in domain),max(r[k] for r in domain)]
                                  for k in ['x-velocity','y-velocity']},
        'interpretation':'Render vector origins using matched real cell centers and signed u/v. For cell y-plus use the actual domain-cell value after matching IDs; multi-face cells must not be blindly averaged or counted twice.'}
target=Path(__file__).parent/(args.case_id+'_field_mapping_audit.json')
target.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='wall_mapping'},indent=2))
for wall in wall_results:
    print(json.dumps({k:v for k,v in wall.items() if k!='records'},indent=2))
