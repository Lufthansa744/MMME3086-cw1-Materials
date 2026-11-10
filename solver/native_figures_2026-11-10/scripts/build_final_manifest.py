"""Inventory native hardcopies and their actual display settings; no solver calls."""
import csv, hashlib, json, struct
from pathlib import Path
root=Path(__file__).resolve().parents[1]
def item(name):
    p=root/name
    o={"path":name,"bytes":p.stat().st_size,"sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
    if p.suffix==".png":
        with p.open("rb") as f: header=f.read(24)
        assert header[:8].hex()=="89504e470d0a1a0a"
        o["pixels"]=list(struct.unpack(">II",header[16:24]))
    return o
groups={
 "Figure2_native_mesh":["taskA/mesh_full_native_interioronly","taskA/mesh_local_native_interioronly"],
 "Figure4_native_velocity":["case03/velocity_native_75us_outline5","case03/velocity_native_normalised_te_outline9"],
 "Figure5_native_wall_adjacent_yplus":["case03/yplus_native_context_final"],
 "Figure6_native_velocity_and_yplus":["case05/velocity_native_rakes_dense_75us_outline4","case05/yplus_native_full_outline8","case05/yplus_native_inset_thin_final"],
 "Figure6_uncovered_cell_fill_alternative":["case05/yplus_native_pure_full"],
}
artifacts={k:[item(stem+ext) for stem in stems for ext in [".png",".eps"]] for k,stems in groups.items()}
legends=[item(n) for n in ["case03/velocity_native_legend_valid.png","case03/yplus_native_legend_valid.png","case05/velocity_native_legend_valid.png","case05/yplus_native_legend_valid.png"]]
def rake_rows(name):
    with (root/"case05"/name).open() as f:
        return [{k.strip():float(v) for k,v in row.items()} for row in csv.DictReader(f)]
earlier=rake_rows("native_rake_dense_velocity_evidence.csv")
final=rake_rows("native_rake_dense_outline4_evidence.csv")
assert len(earlier)==len(final)==504
delta={k:max(abs(a[k]-b[k]) for a,b in zip(earlier,final)) for k in earlier[0]}
m={
 "date":"2026-11-10",
 "purpose":"Native postprocessing of saved final results only; no solution initialization, iteration, physical setting edits, mesh edits, or writes to source CASE/DATA.",
 "fluent":{"version":"2022 R2","build":10212,"executable":str(Path("D:/ANSYS Inc/v222/fluent/ntbin/win64/fluent.exe")),
 "actual_OS_arguments":["2ddp","-t1","-gu","-wait"],"graphics_mode":"Graphics-enabled TUI. -gu omits the full control-panel GUI but retains native graphics. No -g used in this postprocessing session.",
 "actual_launch_script":"scripts/launch_graphics_verified.ps1","unified_exec_session_id":9323,
 "wrapper_PID":316,"cortex_PID":21288,"initial_host_PID":16924,"later_host_PID":10488,"compute_PID":23772,
 "MPI_ranks":1,"source_partition_count":4,"source_read_note":"Native log records merging the saved four partitions onto one postprocessing rank.",
 "temporary_directory":str(Path("D:/CFD_WorkScratch/native_figures_2026-11-10/temp")),
 "native_complete_log":"fluent-20261110-005235-21288.trn",
 "process_command_evidence":"logs/active_graphics_processes.json","normal_exit_code":0,"active_numerical_processes_after_exit":0},
 "startup_attempt_notes":[
 "Initial full-GUI wrapper processes returned exit0 asynchronously and subsequently produced two GUI sessions. They loaded no source case and were closed before the successful single graphics-enabled TUI session.",
 "The initial report of missing AWP_ROOT222/ANSYSLMD_LICENSE_FILE was corrected after full environment enumeration confirmed both existed. No global environment setting was changed.",
 "Computer-use graphics window capture timed out; no claim is made of a successful full-GUI screenshot. All selected images are direct native Save Picture hardcopies.",
 "The 00:52:29 abnormal-exit diagnostic belongs to stopping the unused initial GUI attempt; the successful graphics-enabled session began00:52:35 and exited normally01:27:19."
 ],
 "source_hash_verification":json.loads((root/"logs/source_hashes_verified.json").read_text(encoding="utf-8-sig")),
 "sources_unchanged":True,
 "selected_artifacts":artifacts,
 "native_legend_donors":legends,
 "graphics_common":{"background":"White using native invert-background=yes","color_map":"Fluent built-in sequential-viridis","color_count":100,"legend_on_field_layer":False,
 "EPS_status":"Native HOOPS EPS hardcopies; EPS may embed raster image sections. These are not represented as guaranteed pure-vector files.",
 "projection":"Orthographic; camera position z=1m,target z=0m; up-vector explicitly set0,1,0. Saved native view files retain actual float values.",
 "source_geometry_outline":"Actual native mesh boundary surfaces; no external CAD outline or painted scalar cells."},
 "display_settings":{
 "case03_main":{"vector_field":"velocity","color_field":"velocity-magnitude","native_surfaces":["full-domain"],"scale_factor":0.000075,"auto_scale":False,"skip":3,"fixed_length":False,"style":"3d arrow","head_scale":0.4,"color_limits_m_s":[0,120],"target_m":[0.105,-0.0075,0],"field_extent_m":[0.24,0.085],"hardcopy_line_width_px":5,"estimated_foil_line_pt_at_99_06mm":5*99.06/3600*72/25.4},
 "case03_TE":{"scale_factor":0.0015,"auto_scale":False,"skip":1,"fixed_length":True,"style":"3d arrow","head_scale":0.4,"color_limits_m_s":[0,120],"target_m":[0.105,-0.01,0],"field_extent_m":[0.04,0.024],"hardcopy_line_width_px":9,"estimated_foil_line_pt_at_35_0833mm":9*35.0833/2400*72/25.4,"interpretation":"Direction-normalised vectors; color continues to encode native velocity magnitude."},
 "case03_yplus":{"field":"y-plus","node_values":False,"boundary_values":False,"filled":True,"coloring":"Banded as required by native cell-value rendering","native_range":[1e-10,180],"clip_to_range":True,"target_m":[0.05,-0.005,0],"field_extent_m":[0.116,0.038],"foil_adjacent_cells":103,"native_context":"Full-domain light-gray mesh before cell fill; actual black foil outline last.","hardcopy_line_width_px":1},
 "case05_main":{"vector_field":"velocity","color_field":"velocity-magnitude","native_surfaces":"Twelve native rake surfaces,45 requested points each","scale_factor":0.000075,"auto_scale":False,"skip":0,"fixed_length":False,"style":"3d arrow","head_scale":0.4,"color_limits_m_s":[0,120],"target_m":[0.11,-0.0025,0],"field_extent_m":[0.24,0.055],"hardcopy_line_width_px":4,"estimated_foil_line_pt_at_125_476mm":4*125.476/3600*72/25.4,"sampling":"Fluent-native evaluation and drawing on regular rake surfaces; not described as cell-centred vectors.","nominal_sampling_points":540,"valid_exported_points":504,"x_limits_m":[-0.0075,0.2275],"rake_y_limits_m":[-0.0275,0.0225],"dx_m":0.235/44,"dy_m":0.05/11,"rake_export_note":"CSV was exported with cell-centered=no (native node-interpolated output). It is independent native sampling evidence, not asserted numerically identical to every rendered arrow value.","line_width_change_native_export_max_abs_differences":delta},
 "case05_yplus_full":{"field":"y-plus","node_values":False,"boundary_values":False,"filled":True,"native_range":[1e-10,8],"clip_to_range":True,"target_m":[0.05,-0.001,0],"field_extent_m":[0.116,0.03],"foil_adjacent_cells":413,"hardcopy_line_width_px":8,"estimated_foil_line_pt_at_125_476mm":8*125.476/9000*72/25.4,"scope":"The requested native black foil outline locates the body but can cover the very thin real cell-color strip. The uncovered9000px pure-fill alternative is retained, and the equal-scale inset displays actual uninflated cells."},
 "case05_yplus_inset":{"field":"y-plus","node_values":False,"filled":True,"native_range":[1e-10,8],"clip_to_range":True,"target_m":[0.000625639202,0.0072898292625,0],"field_extent_m":[0.0018,0.0007],"hardcopy_line_width_px":1,"native_context":"Full-domain light-gray native mesh plus flat cell fill; no added thick black foil outline.","note":"Requested0.5line weight was rejected by native TUI;1was used."},
 "taskA":{"mesh_cells":7687,"nodes":4029,"interior_faces":11345,"boundary_faces":371,"all_faces":11716,"interior_surface":"native-interior-edges created from actual interior-sys_fluid face zone","strategy":"Render interior1Dfacets separately from the seven true boundary surfaces; no duplicate full-domain boundary wire and no display-Z offset or mesh mutation.","hardcopy_line_width_px":3,"full_target_m":[0,0,0],"full_field_extent_m":[1,0.15],"local_target_m":[0.05198367698354394,0.00091690311771526,0],"local_field_extent_m":[0.115,0.036],"native_boundary_colors":{"inlet":"dark green","outlet":"pink","wall_top":"black","wall_bottom":"black","aerofoil_suction":"dark blue","aerofoil_pressure":"orange","aerofoil_te":"black"},"color_note":"The native face-color menu rejects arbitrary hexadecimal colors. Fixed supported native colors were used; the scientific boundary strokes were not recolored externally."}
 },
 "yplus_mask_logic":"Cell-value positive-range clipping removes exact-zero interior cells. The requested foil viewport excludes duct walls. No iso-clip fragments, node averaging, external cell painting, or artificial cell inflation. Tiny1e-10range floor is a display mask; native legend formatting rounds it to0.",
 "replay":{"journal":"scripts/complete_native_replay.jou","launcher":"scripts/replay_all_native.ps1","status":"Compiled from actually successful observed TUI command sequences; NOT separately replay-executed end-to-end after assembly. No restart was made solely to test this consolidated journal.","output_policy":"Replays target the separate replay/ directory and leave these original native raw files unchanged."},
 "excluded_diagnostics":"Earlier scale tests, nearly invisible first normalised-TE test, yplus_200/yplus_256 failed-colormap files, gray-only TaskA trials and color/depth debug images are retained for audit but are not selected publication layers.",
 "render_interpolation_validation_boundary":"Native renderer identity, source hashes and geometry/sign checks are supported independently. The native rake ASCII node-interpolated values are not asserted exactly equal to every vector-on-rake renderer sample."
}
assert all(x["Unchanged"] for x in m["source_hash_verification"])
(root/"FINAL_NATIVE_MANIFEST.json").write_text(json.dumps(m,indent=2),encoding="utf-8")
print(json.dumps({"source_pairs_unchanged":m["sources_unchanged"],"publication_files":sum(map(len,artifacts.values())),"legends":len(legends),"rake_points":len(final),"native_value_difference_after_outline_change":delta},indent=2))

