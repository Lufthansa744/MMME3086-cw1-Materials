"""Audit actual enhanced native cells, inset thickness and native rake samples."""
from pathlib import Path
import json,csv,math,contextlib,io,hashlib
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[2];out=root/'review/native_figures_2026-11-10'
code=(root/'review/audit_enhanced_mesh.py').read_text(encoding='utf-8').replace("'enhanced_mesh_geometry_audit.json'","'native_figures_2026-11-10/case05_native_mesh_topology.json'")
mesh={'__file__':str(root/'review/audit_enhanced_mesh.py')}
with contextlib.redirect_stdout(io.StringIO()):exec(compile(code,'independent_native_enhanced_mesh','exec'),mesh)
def read(p):return [{k.strip():float(v) for k,v in r.items()} for r in csv.DictReader(p.open())]
base=root/'solver/case05_verified/raw';domain=read(base/'domain_cell_fields.csv');walls=sum([read(base/f) for f in ['suction_p_yplus.csv','pressure_p_yplus.csv','trailing_p_yplus.csv']],[]);ids={int(r['cell-id']) for r in walls};assert len(ids)==413
visible=set()
for r in domain:
    if r['y-plus']<=0:continue
    cid=int(r['cell-id']);ns={n for f in mesh['cell_faces'][cid] for n in mesh['faces'][f][:2]};p=np.array([mesh['nodes'][n] for n in ns])
    if p[:,0].max()>=-.008 and p[:,0].min()<=.108 and p[:,1].max()>=-.016 and p[:,1].min()<=.014:visible.add(cid)
assert visible==ids
def ordered_polygon(edgeids):
    adj={}
    for fi in edgeids:
        a,b=mesh['faces'][fi][:2];adj.setdefault(a,[]).append(b);adj.setdefault(b,[]).append(a)
    start=min(adj);order=[start];previous=None;current=start
    while True:
        nxt=next(n for n in adj[current] if n!=previous)
        if nxt==start:break
        order.append(nxt);previous,current=current,nxt
    return [mesh['nodes'][n] for n in order]
zoneids=[mesh['zones'][n]['id'] for n in ['aerofoil-pressure','aerofoil-suction','aerofoil-trail']];foil=ordered_polygon([f for z in zoneids for f in mesh['zone_faces'][z]])
def inside(x,y):
    state=False
    for (a,b),(c,d) in zip(foil,foil[1:]+foil[:1]):
        if (b>y)!=(d>y) and x<(c-a)*(y-b)/(d-b)+a:state=not state
    return state
grid={(i,j):(-.0075+(.235/44)*i,-.0275+(.05/11)*j) for j in range(12) for i in range(45)}
expected_fluid={ij for ij,p in grid.items() if not inside(*p)}
rakepath=root/'solver/native_figures_2026-11-10/case05/native_rake_dense_velocity_evidence.csv';rows=read(rakepath)
actual={};errors=[]
for r in rows:
    x,y=r['x-coordinate'],r['y-coordinate'];ij=(round((x+.0075)/(.235/44)),round((y+.0275)/(.05/11)));assert ij not in actual
    assert ij in grid and not inside(x,y);errors.append(math.dist((x,y),grid[ij]));actual[ij]=r
assert set(actual)==expected_fluid and len(rows)==len(expected_fluid)
deltas=[r['velocity-magnitude']-math.hypot(r['x-velocity'],r['y-velocity']) for r in rows]
assert min(deltas)>-1e-6
# Independent horizontal sections through the actual maximum-yplus quad and native inset pixels.
maxid=max(walls,key=lambda r:r['y-plus'])['cell-id'];maxid=int(maxid);quad=ordered_polygon(mesh['cell_faces'][maxid]);centre=np.array(quad).mean(0)
native=root/'solver/native_figures_2026-11-10/case05/yplus_native_inset_thin_final.png';im=np.asarray(Image.open(native).convert('RGB')).astype(int);h,w=im.shape[:2];scale=min(w/.0018,h/.0007);sections=[]
for y in [50,200,466,700,850]:
    worldy=centre[1]+(h/2-y-.5)/scale;cuts=[]
    for (x0,y0),(x1,y1) in zip(quad,quad[1:]+quad[:1]):
        if min(y0,y1)<=worldy<=max(y0,y1) and y0!=y1:cuts.append(x0+(x1-x0)*(worldy-y0)/(y1-y0))
    assert len(cuts)==2;expectedx=sorted([(x-centre[0])*scale+w/2 for x in cuts]);row=im[y];xx=np.flatnonzero(row.max(1)-row.min(1)>20)
    observed=[int(xx.min()),int(xx.max())];endpoint_error=max(abs(observed[i]-expectedx[i]) for i in [0,1]);assert endpoint_error<2.1
    sections.append({'native_row':y,'world_y_m':worldy,'actual_quad_expected_x_pixels':expectedx,'native_colour_run_x_pixels':observed,'max_endpoint_error_px':endpoint_error,'native_RGB_inside_cell':list(map(int,row[int(xx.mean())]))})
result={'actual_visible_positive_yplus_cell_ids_match_exact_foil413':True,'maximum_yplus_cell_id':maxid,'maximum_yplus_quad_world_vertices_m':quad,'inset':{'source':str(native),'sha256':hashlib.sha256(native.read_bytes()).hexdigest(),'pixel_size':[w,h],'orthographic_scale_px_per_m':scale,'sections':sections,'geometry_not_exaggerated':True},'rakes':{'source':str(rakepath),'sha256':hashlib.sha256(rakepath.read_bytes()).hexdigest(),'theoretical_grid_points':540,'theoretical_points_inside_actual_foil_excluded':540-len(expected_fluid),'actual_native_fluid_points':len(rows),'actual_points_exactly_match_all_theoretical_fluid_points':True,'largest_actual_coordinate_deviation_from_requested_rake_grid_m':max(errors),'all_field_values_finite':all(math.isfinite(v) for r in rows for v in r.values()),'max_interpolated_magnitude_minus_norm_of_interpolated_uv_m_s':max(deltas),'min_same_delta_m_s':min(deltas),'note':'Velocity magnitude and signed components are separately native-exported point fields. Their small positive norm discrepancy is consistent with noncommutativity of interpolation and taking a norm; preserve native fields. This is an inference, not a claim to have inspected Fluent interpolation source code.'},'status':'PASS actual visible cell scope, real max-cell inset thickness and native rake fluid/solid sampling; final composed layout and vector-image fidelity still need inspection.'}
(out/'case05_native_dense_inset_rake_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8');print(json.dumps(result,indent=2))
