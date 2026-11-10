from pathlib import Path
import importlib.util,contextlib,io,json,csv,hashlib
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent
spec=importlib.util.spec_from_file_location('mesh',root/'review/verify_aligned_mesh.py');m=importlib.util.module_from_spec(spec);m.mesh_audit_target_override=out/'mesh_audit.json'
with contextlib.redirect_stdout(io.StringIO()):spec.loader.exec_module(m)
raw=root/'solver/case03_aligned/raw';rows=list(csv.DictReader((raw/'suction_p_yplus.csv').open()));rows=[{k.strip():float(v) for k,v in r.items()} for r in rows]
low=[r for r in rows if r['y-plus']<30];assert len(low)==5
result=[]
for r in low:
 cid=int(r['cell-id']);fis=m.cell_faces[cid];ns=sorted({n for fi in fis for n in m.faces[fi][:2]});assert len(ns)==3
 wall=[fi for fi in fis if fi in m.zone_faces[5]]
 # Resolve side by actual node connectivity, regardless of raw row order.
 allwall=[{'zone':z,'face_id':fi,'node_ids':list(m.faces[fi][:2]),'vertices_m':[m.nodes[n] for n in m.faces[fi][:2]]} for z in [5,6,7] for fi in fis if fi in m.zone_faces[z]]
 result.append({'cell_id':cid,'yplus':r['y-plus'],'raw_face_midpoint_m':[r['x-coordinate'],r['y-coordinate']],'node_ids':ns,'vertices_m':[m.nodes[n] for n in ns],'face_ids':list(fis),'foil_wall_edges':allwall,'neighbour_cells':sorted({c for fi in fis for c in m.faces[fi][2:] if c not in [0,cid]})})
result.sort(key=lambda r:r['raw_face_midpoint_m'][0]);lowids={r['cell_id'] for r in result}
xmin=min(p[0] for r in result for p in r['vertices_m']);xmax=max(p[0] for r in result for p in r['vertices_m'])
projected=[]
for r in rows:
 cid=int(r['cell-id']);ns={n for fi in m.cell_faces[cid] for n in m.faces[fi][:2]};xs=[m.nodes[n][0] for n in ns]
 if max(xs)>xmin+1e-12 and min(xs)<xmax-1e-12:projected.append({'cell_id':cid,'yplus':r['y-plus'],'wall_x_m':r['x-coordinate'],'x_projection_m':[min(xs),max(xs)],'is_below30':cid in lowids})
projected.sort(key=lambda r:r['wall_x_m'])
domainrows=[{k.strip():float(v) for k,v in r.items()} for r in csv.DictReader((raw/'domain_cell_fields.csv').open())];domain={int(r['cell-id']):r for r in domainrows}
for r in result:r['actual_cell_centroid_m']=[domain[r['cell_id']]['x-coordinate'],domain[r['cell_id']]['y-coordinate']]
summary={'actual_suction_below30_count':5,'ordered_exact_cells':result,'old_global_projection_m':[xmin,xmax],'all_suction_triangles_overlapping_old_projection':projected,'correction':'The original count5 is correct. A single global x-projection bracket is ambiguous: it covers triangles beyond or between the selected set. Replace it with five individually identified centroid markers/leaders or true triangle-outline annotations. Do not narrow a single bracket or change the count to7.','native_scientific_layer_policy':'Keep original native RGB unchanged. New red marks are post-export identity annotations, not native colour fill.'}
summary['source_hashes']=[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [root/'solver/aligned_taskA/taskA_baseline.msh',raw/'suction_p_yplus.csv',raw/'domain_cell_fields.csv']]
assert 6134 in m.faces[11445][2:]
summary['intervening_wall_face_11445']={'cell_id':6134,'yplus':next(r['y-plus'] for r in rows if int(r['cell-id'])==6134),'node_ids':list(m.faces[11445][:2])}
(out/'exact_five_cells.json').write_text(json.dumps(summary,indent=2));print(json.dumps(summary,indent=2))

