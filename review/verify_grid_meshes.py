"""Reuse the independent binary topology audit on two native aligned refinements."""
from pathlib import Path
import contextlib,io,math,json
base=Path(__file__).resolve().parent
source=(base/'verify_aligned_mesh.py').read_text(encoding='utf-8')
checks={}
for level in ['medium','fine']:
    code=source.replace("solver/aligned_taskA/taskA_baseline.msh",f"solver/grid_{level}_mesh/mesh.msh").replace("'aligned_mesh_audit.json'",f"'grid_{level}_mesh_audit.json'")
    scope={'__file__':str(base/'verify_aligned_mesh.py'),'__name__':'independent_grid_review'}
    with contextlib.redirect_stdout(io.StringIO()):exec(compile(code,str(base/'verify_aligned_mesh.py'),'exec'),scope)
    r=scope['result'];assert r['all_cells_one_component'] and len(r['boundary_loop_vertex_counts'])==2 and not r['cells_containing_foil_interior_test_point']
    assert r['euler_V_minus_E_plus_C']==0
    assert r['x_bounds_m']==[-.5,.5] and r['y_bounds_m']==[-.075,.075]
    names={z['name']:int(z['id_as_written']) for z in r['zones']}
    zone_nodes=lambda key:{n for f in scope['zone_faces'][names[key]] for n in scope['faces'][f][:2]}
    shared=zone_nodes('aerofoil_suction')&zone_nodes('aerofoil_pressure')
    assert len(shared)==1
    le=scope['nodes'][shared.pop()]
    te=[scope['nodes'][n] for n in zone_nodes('aerofoil_te')]
    tecentre=[sum(p[j] for p in te)/len(te) for j in [0,1]]
    assert math.dist(le,[.00048367698354395,.00691690311771526])<1e-12
    assert math.dist(tecentre,[.099510483857701,-.00700040697829128])<1e-12
    checks[level]={'mesh_sha256':r['sha256'],'counts':r['counts'],'LE_m':le,'TEcentre_m':tecentre,'effective_h_m':math.sqrt(r['total_cell_area_m2']/r['counts']['cells']),
        'topology_gate':True,'domain_hole_alignment_gate':True}
(base/'grid_mesh_alignment_audit.json').write_text(json.dumps(checks,indent=2),encoding='utf-8')
print(json.dumps(checks,indent=2))
