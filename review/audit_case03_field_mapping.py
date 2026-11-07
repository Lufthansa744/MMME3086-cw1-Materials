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

root=Path(__file__).resolve().parent.parent
spec=importlib.util.spec_from_file_location('baseline_audit',Path(__file__).parent/'verify_baseline_mesh.py')
mesh=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()): spec.loader.exec_module(mesh)
raw=root/'solver/case03/raw'
def read(name):
    return [{k.strip():float(v) for k,v in row.items()} for row in csv.DictReader((raw/name).open())]
domain=read('domain_cell_fields.csv')
by_id={int(row['cell-id']):row for row in domain}
centers={}
for cell,fs in mesh.cell_faces.items():
    ns={node for f in fs for node in mesh.faces[f][:2]}
    centers[cell]=tuple(sum(mesh.nodes[n][i] for n in ns)/3 for i in [0,1])
offsets={}
for offset in [-1,0,1]:
    errors=[];missing=0
    for idx,row in by_id.items():
        if idx+offset not in centers: missing+=1;continue
        errors.append(math.dist((row['x-coordinate'],row['y-coordinate']),centers[idx+offset]))
    offsets[str(offset)]={'missing':missing,'max_center_error_m':max(errors),'median_center_error_m':statistics.median(errors)}
best=min(offsets,key=lambda x:(offsets[x]['missing'],offsets[x]['max_center_error_m']))
offset=int(best)
assert len(by_id)==len(domain)==mesh.counts['cells']
assert offsets[best]['missing']==0 and offsets[best]['max_center_error_m']<1e-7
wall_results=[];cell_values=defaultdict(list)
for name,zone in [('suction_p_yplus.csv',7),('pressure_p_yplus.csv',6),('trailing_p_yplus.csv',5)]:
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
        'wall_mapping':wall_results,'foil_face_count':sum(len(v['records']) for v in wall_results),
        'unique_foil_adjacent_cells':len(cell_values),'multi_foil_face_cells':duplicates,
        'signed_velocity_ranges':{k:[min(r[k] for r in domain),max(r[k] for r in domain)]
                                  for k in ['x-velocity','y-velocity']},
        'interpretation':'Render vector origins using matched real cell centers and signed u/v. For cell y-plus use the actual domain-cell value after matching IDs; multi-face cells must not be blindly averaged or counted twice.'}
target=Path(__file__).parent/'case03_field_mapping_audit.json'
target.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='wall_mapping'},indent=2))
for wall in wall_results:
    print(json.dumps({k:v for k,v in wall.items() if k!='records'},indent=2))
