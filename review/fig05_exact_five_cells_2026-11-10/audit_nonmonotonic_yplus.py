"""Geometric evidence only: no new CFD or assumed wall-shear export."""
from pathlib import Path
import importlib.util,contextlib,io,csv,json,math
root=Path(__file__).resolve().parents[2];out=Path(__file__).parent
spec=importlib.util.spec_from_file_location('mesh',root/'review/verify_aligned_mesh.py');m=importlib.util.module_from_spec(spec);m.mesh_audit_target_override=out/'mesh_audit.json'
with contextlib.redirect_stdout(io.StringIO()):spec.loader.exec_module(m)
raw=root/'solver/case03_aligned/raw'
read=lambda name:[{k.strip():float(v) for k,v in r.items()} for r in csv.DictReader((raw/name).open())]
domain={int(r['cell-id']):r for r in read('domain_cell_fields.csv')};records=[]
for r in read('suction_p_yplus.csv'):
 cid=int(r['cell-id'])
 if cid not in [7578,7588,6134,7316,69,7251,2573]:continue
 fi=next(fi for fi in m.cell_faces[cid] if fi in m.zone_faces[7]);a,b=[m.nodes[n] for n in m.faces[fi][:2]];d=domain[cid];c=(d['x-coordinate'],d['y-coordinate'])
 length=math.dist(a,b);delta=(b[0]-a[0],b[1]-a[1]);normal_distance=abs(delta[0]*(c[1]-a[1])-delta[1]*(c[0]-a[0]))/length
 foot_parameter=((c[0]-a[0])*delta[0]+(c[1]-a[1])*delta[1])/length**2
 assert 0<foot_parameter<1
 records.append({'cell_id':cid,'wall_x_mm':1000*r['x-coordinate'],'raw_yplus':r['y-plus'],'wall_face_id':fi,'wall_edge_length_mm':1000*length,'actual_centroid_to_own_wall_edge_normal_distance_mm':1000*normal_distance,'centroid_projection_parameter':foot_parameter,'yplus_divided_by_geometric_normal_distance_per_m':r['y-plus']/normal_distance})
records.sort(key=lambda r:r['wall_x_mm']);by={r['cell_id']:r for r in records};ratios=[]
for cid in [7588,7316]:
 gap=by[6134];ref=by[cid];ratios.append({'gap_cell':6134,'comparison_cell':cid,'yplus_ratio':gap['raw_yplus']/ref['raw_yplus'],'geometric_wall_distance_ratio':gap['actual_centroid_to_own_wall_edge_normal_distance_mm']/ref['actual_centroid_to_own_wall_edge_normal_distance_mm'],'ratio_of_yplus_over_geometric_distance':gap['yplus_divided_by_geometric_normal_distance_per_m']/ref['yplus_divided_by_geometric_normal_distance_per_m']})
result={'records':records,'gap_to_adjacent_selected_ratios':ratios,'interpretation':'Actual irregular first-cell normal distance changes appreciably and contributes substantially to the observed local threshold crossing; distance alone does not explain the full variation. yplus need not be monotonic; the raw count is not an error. yplus/distance is a diagnostic ratio only: actual Fluent wall distance and wall shear were not separately exported here, so do not claim direct shear measurement or exact solver wall-distance equivalence.','wall_function_scope':'The5 cells below30 remain a wall-treatment suitability concern; neither their count nor these geometric ratios establish convergence, mesh accuracy or grid independence.'}
(out/'nonmonotonic_yplus_geometry.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))

