"""Read actual mesh and existing CSV only; do not import/write the published audit."""
import csv, hashlib, json, math
from pathlib import Path
out=Path(__file__).resolve().parent
extractor=out.parent/'extract_five_cells.py'
ns={'__file__':str(extractor)}
# Execute only the existing parser/read portion; stop before any published output.
prefix=extractor.read_text().split('selected=[all_cells[ci] for ci in low]')[0]
exec(compile(prefix,str(extractor),'exec'),ns)
root=ns['ROOT'];cells=ns['all_cells'];faces=ns['faces'];nodes=ns['nodes']
domain_path=root/'solver/case03_aligned/raw/domain_cell_fields.csv'
with domain_path.open() as f:
    domain={int(r['cell-id']):r for row in csv.DictReader(f) for r in [{k.strip():float(v) for k,v in row.items()}]}
sequence=[(11444,7588),(11445,6134),(11446,7316),(11447,69),(11448,7251),(11414,2573)]
def distance(c,a,b):
    vx,vy=b[0]-a[0],b[1]-a[1];length=math.hypot(vx,vy)
    t=((c[0]-a[0])*vx+(c[1]-a[1])*vy)/(length*length)
    foot=[a[0]+t*vx,a[1]+t*vy]
    return abs(vx*(c[1]-a[1])-vy*(c[0]-a[0]))/length,t,foot
rows=[]
for fi,ci in sequence:
    record=cells[ci];assert record['wall_face_id']==fi
    a,b=record['wall_edge_vertices_m'];g=record['cell_geometric_centroid_m']
    native=[domain[ci]['x-coordinate'],domain[ci]['y-coordinate']]
    yp,t,foot=distance(native,a,b);yg,tg,fg=distance(g,a,b)
    assert 0<=t<=1
    rows.append({'cell_id':ci,'wall_face_id':fi,'wall_node_ids':record['wall_node_ids'],'wall_edge_vertices_m':[a,b],'yplus':record['yplus'],'below30':record['yplus']<30,'native_exported_cell_centroid_m':native,'exact_triangle_centroid_m':g,'yp_native_centroid_m':yp,'yp_native_centroid_mm':yp*1000,'yp_exact_mesh_centroid_m':yg,'yp_exact_mesh_centroid_mm':yg*1000,'normal_foot_on_actual_edge_m':foot,'normal_projection_parameter_t':t,'foot_lies_within_wall_edge':True})
by={r['cell_id']:r for r in rows};gap=by[6134]
comparisons=[]
for ci in [7588,7316,7251,2573]:
    other=by[ci];dr=gap['yp_native_centroid_m']/other['yp_native_centroid_m'];yr=gap['yplus']/other['yplus']
    comparisons.append({'gap_cell':6134,'comparison_cell':ci,'yp_ratio':dr,'yp_increase_percent':(dr-1)*100,'yplus_ratio':yr,'conditional_yplus_over_yp_ratio':yr/dr,'interpretation_of_last_ratio':'Only the ratio implied by y+=uTau*yp/nu if this geometric normal distance equals the solver wall-unit distance. Not a wall-shear or uTau measurement and not independent evidence.'})
headers={}
for path in sorted((root/'solver/case03_aligned/raw').glob('*.csv')):
    with path.open() as f:headers[path.name]=next(csv.reader(f))
shear_headers={n:cols for n,cols in headers.items() if any('shear' in k.lower() or 'friction' in k.lower() or 'u-tau' in k.lower() for k in cols)}
result={'method':'Read existing binary mesh, original wall CSV and original native domain-cell CSV. No Fluent startup, iterations, source changes or image modifications. Published figure audit outputs are not rewritten.','wall_order_upstream_to_TE':rows,'gap_vs_neighbors_and_similar_height_cells':comparisons,'native_wall_shear_or_uTau_CSV_found_in_case03_raw':bool(shear_headers),'matching_shear_headers':shear_headers,'conclusion':'The skipped cell6134 has a larger geometric wall-normal height than both adjacent selected cells: about27.0% above7588 and10.7% above7316. That contributes to its higher y+. However7251/2573 have almost the same height as6134 while substantially lower y+, so wall distance alone cannot explain all variation. An irregular triangular first layer and local friction-velocity variation are consistent with a noncontiguous below30set. This diagnostic does not independently measure wall shear or certify physical accuracy.','distance_formula':'yp=abs((B-A)x(C-A))/length(B-A), using actual mesh wall endpoints A,B and existing native exported cell centroid C. The perpendicular foot lies on each actual wall segment.','geometry_rounding_note':'Exact arithmetic triangle-centroid distances are also retained. Their tiny difference from native exported centroid distances reflects existing coordinate/serialization precision, not a new geometric modification.','source_hashes':[{'path':str(domain_path),'sha256':hashlib.sha256(domain_path.read_bytes()).hexdigest()},{'path':str(root/'solver/aligned_taskA/taskA_baseline.msh'),'sha256':hashlib.sha256(ns['blob']).hexdigest()}]+ns['input_provenance'],'prior_CASE_DATA_hash_record':'solver/native_figures_2026-11-10-centered/logs/source_hashes_verified.json'}
(out/'wall_normal_distances.json').write_text(json.dumps(result,indent=2))
print(json.dumps({'rows':[{'cell':r['cell_id'],'yp_mm':r['yp_native_centroid_mm'],'yplus':r['yplus']} for r in rows],'ratios':comparisons,'independent_wall_shear_CSV_found':bool(shear_headers)},indent=2))

