"""Read-only source geometry, native sampling, and centered artifact audit."""
import csv, hashlib, json, re, struct
from pathlib import Path
root=Path(__file__).resolve().parents[1]
workspace=root.parents[1]
mesh_path=workspace/'solver/aligned_taskA/taskA_baseline.msh'
blob=mesh_path.read_bytes()
def start(m):
    i=m.end()
    while blob[i:i+1] in (bytes([32]),bytes([13]),bytes([10]),bytes([9])): i+=1
    assert blob[i:i+1]==b'('
    return i+1
nodes={}
for m in re.finditer(rb'[(]3010 [(]([0-9a-fA-F ]+)[)]',blob):
    zone,first,last,kind,dim=map(lambda x:int(x,16),m.group(1).split())
    values=struct.unpack_from('<'+'d'*((last-first+1)*dim),blob,start(m))
    for i in range(last-first+1): nodes[first+i]=(values[i*dim],values[i*dim+1])
foil=set()
for m in re.finditer(rb'[(]2013 [(]([0-9a-fA-F ]+)[)]',blob):
    zone,first,last,kind,elem=map(lambda x:int(x,16),m.group(1).split())
    if zone not in (5,6,7): continue
    values=struct.unpack_from('<'+'i'*((last-first+1)*4),blob,start(m))
    for i in range(last-first+1): foil.update(values[i*4:i*4+2])
assert len(foil)==103
xs=[nodes[i][0] for i in foil];ys=[nodes[i][1] for i in foil]
center=(min(ys)+max(ys))/2
assert abs(center-0.0015294034661851664)<1e-15
y_bounds=[center-.019,center+.019]
geometry={'mesh':str(mesh_path),'mesh_sha256':hashlib.sha256(blob).hexdigest(),'foil_nodes':len(foil),'foil_face_zones':[5,6,7],'foil_bbox_m':[min(xs),max(xs),min(ys),max(ys)],'actual_foil_vertical_bbox_center_m':center,'figure5_target_m':[.05,center,0],'figure5_field_extent_m':[.116,.038],'figure5_y_bounds_m':y_bounds,'equal_foil_bbox_margins_m':[min(ys)-y_bounds[0],y_bounds[1]-max(ys)]}
(root/'geometry_window_audit.json').write_text(json.dumps(geometry,indent=2))
csv_path=root/'case05/native_rake_centered_velocity_evidence.csv'
with csv_path.open() as f: rows=[{k.strip():float(v) for k,v in row.items()} for row in csv.DictReader(f)]
assert len(rows)==506
wake=[r for r in rows if .10<r['x-coordinate']<.17 and -.015<r['y-coordinate']<.005]
up=[r for r in rows if -.065<r['x-coordinate']<-.02 and -.015<r['y-coordinate']<.005]
sampling={'nominal_rakes':12,'points_per_rake':45,'nominal_points':540,'actual_valid_exported_points':len(rows),'rake_x_limits_m':[-.0675,.1675],'rake_y_limits_m':[-.0275,.0225],'dx_m':.235/44,'dy_m':.05/11,'figure6a_x_bounds_m':[-.07,.17],'figure6a_y_bounds_m':[-.03,.025],'TE_center_x_m':.099510483857701,'visible_wake_length_after_TE_m':.17-.099510483857701,'wake_length_in_chords':(.17-.099510483857701)/.1,'wake_sampling_window_m':[.10,.17,-.015,.005],'wake_native_csv_points':len(wake),'wake_sampled_speed_range_m_s':[min(r['velocity-magnitude'] for r in wake),max(r['velocity-magnitude'] for r in wake)],'upstream_reference_sampling_window_m':[-.065,-.02,-.015,.005],'upstream_sampled_speed_range_m_s':[min(r['velocity-magnitude'] for r in up),max(r['velocity-magnitude'] for r in up)],'interpretation':'These sampled ranges only support that a real local velocity deficit remains visible in the cropped near wake. They are not an exact wake minimum or a quantitative matched-streamline deficit.','CSV_renderer_boundary':'Native ASCII output uses cell-centered=no; it is native node-interpolated sampling evidence, not asserted identical to every renderer vector value.'}
(root/'native_sampling_audit.json').write_text(json.dumps(sampling,indent=2))
def item(name):
    p=root/name
    d={'path':name,'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
    if p.suffix=='.png':
        with p.open('rb') as f: h=f.read(24)
        assert h[:8].hex()=='89504e470d0a1a0a'
        d['pixels']=list(struct.unpack('>II',h[16:24]))
    return d
source=json.loads((root/'logs/source_hashes_verified.json').read_text(encoding='utf-8-sig'))
assert all(v['Unchanged'] for v in source)
files=[item(x) for x in ['case03/yplus_native_context_centered.png','case03/yplus_native_context_centered.eps','case03/camera_centered.vw','case05/velocity_native_rakes_75us_centered.png','case05/velocity_native_rakes_75us_centered.eps','case05/camera_centered.vw','case05/native_rake_centered_velocity_evidence.csv','scripts/centered_native_executed.jou','scripts/shutdown_executed.jou']]
manifest={'version':'centered native artwork','date':'2026-11-10','source_case_data_hashes':source,'original_source_files_unchanged':True,'old_native_raw_policy':'The earlier native_figures_2026-11-10 directory and all prior native raw files remain unchanged. Only Figure5 and Figure6(a) are newly exported here; Figures2/4 and Figure6B/C retain their earlier selected native layers.','launch':{'executable':str(Path('D:/ANSYS Inc/v222/fluent/ntbin/win64/fluent.exe')),'arguments':['2ddp','-t1','-gu','-wait','-i',str(root/'scripts/centered_native_executed.jou')],'script':'scripts/launch_centered_graphics.ps1','scratch':str(Path('D:/CFD_WorkScratch/native_figures_2026-11-10-centered/temp')),'process_evidence':'logs/graphics_processes.json','final_process_evidence':'logs/graphics_processes_final.json','MPI_ranks':1,'source_partitions_combined':4,'unified_exec_session_id':78785,'native_auto_transcript':'fluent-20261110-144359-28944.trn','execution_status':'The complete centered artwork journal was actually launched through-i in one fresh graphics-enabled Fluent process and executed to EOF without errors. The saved shutdown command sequence was subsequently executed through the same TUI and exited normally. This is more specific than the older consolidated journal, which was not separately replayed.','normal_exit_code':0,'initialization_or_iterations_performed':False,'physical_or_mesh_settings_changed':False,'source_CASE_DATA_writes':False},'artifacts':files,'figure5':{'native_field':'y-plus','node_values':False,'boundary_values':False,'filled':True,'coloring':'Native banded cell-value contours','palette':'sequential-viridis','palette_size':100,'native_range':[1e-10,180],'clip_to_range':True,'positive_threshold_note':'Tiny positive display floor removes exact-zero interior cells; color legends continue to display the lower end rounded to0.','native_context':'Unchanged light-gray full-domain wireframe and native black foil outline','hardcopy_line_width_px':1,'target_m':[.05,center,0],'field_extent_m':[.116,.038],'old_target_y_m':-.005,'only_intended_change':'Vertical camera target moved to the actual foil-boundary bounding-box midpoint. Native field values, scalar mapping, source, extent and rendering parameters stay the same.','geometry_audit':'geometry_window_audit.json'},'figure6a':{'native_field':'Velocity vectors colored by velocity-magnitude','native_sampling':'Twelve newly created native rake surfaces in the new world-coordinate view','scale_factor':.000075,'auto_scale':False,'style':'3d arrow','head_scale':.4,'fixed_length':False,'skip':0,'palette':'sequential-viridis','palette_size':100,'color_limits_m_s':[0,120],'hardcopy_line_width_px':4,'target_m':[.05,-.0025,0],'field_extent_m':[.24,.055],'old_target_x_m':.11,'nominal_points':540,'actual_valid_exported_points':len(rows),'rake_x_limits_m':[-.0675,.1675],'rake_y_limits_m':[-.0275,.0225],'view_x_limits_m':[-.07,.17],'view_y_limits_m':[-.03,.025],'sampling_audit':'native_sampling_audit.json','native_foil':'Actual saved Case5 three foil boundary surfaces, black','page_field_size_mm':[125.476,28.755],'coordinate_policy':'The native camera moved and the native rake surfaces were regenerated at the new world coordinates. No native pixels were shifted and no upstream vectors were fabricated.','downstream_scope':'Shows about0.705c after the trailing edge. The x=.2m reporting station is outside this view; no claim is made to display that station.'},'camera_note':'Requested orthographic positionz1/targetz0/up0,1,0 and extents are recorded by native view files. Native saved float camera values include tiny roundoff/roll, retained without external pixel relocation.','EPS_note':'Direct native HOOPS EPS output; may contain embedded raster sections and is not claimed pure-vector.','replay_scope':'The new main journal itself was executed end-to-end from a fresh process. No additional identical replay was performed after saving the artwork; shutdown was a separate saved and executed command block.','processes_released':True}
(root/'CENTERED_NATIVE_MANIFEST.json').write_text(json.dumps(manifest,indent=2))
print(json.dumps({'bbox_y_center_m':center,'valid_native_rake_points':len(rows),'source_files_unchanged':True,'artifacts':len(files),'wake_speed_range':sampling['wake_sampled_speed_range_m_s']},indent=2))

