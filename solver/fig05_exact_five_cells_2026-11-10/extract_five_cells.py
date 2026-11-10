"""Read-only extraction of the five actual Case3 wall-adjacent cells below y+=30."""
import csv, hashlib, json, math, re, struct
from collections import defaultdict
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
mesh_path=ROOT/'solver/aligned_taskA/taskA_baseline.msh'
blob=mesh_path.read_bytes()
def payload(m):
    i=m.end()
    while blob[i] in (9,10,13,32): i+=1
    assert blob[i]==40
    return i+1
nodes={}
for m in re.finditer(rb'[(]3010 [(]([0-9a-fA-F ]+)[)]',blob):
    zone,first,last,kind,dim=[int(t,16) for t in m.group(1).split()]
    values=struct.unpack_from('<'+'d'*((last-first+1)*dim),blob,payload(m))
    for i in range(last-first+1):nodes[first+i]=list(values[i*dim:i*dim+2])
faces={};cell_faces=defaultdict(list);zones={}
for m in re.finditer(rb'[(]2013 [(]([0-9a-fA-F ]+)[)]',blob):
    zone,first,last,kind,etype=[int(t,16) for t in m.group(1).split()]
    values=struct.unpack_from('<'+'i'*((last-first+1)*4),blob,payload(m))
    for i in range(last-first+1):
        fi=first+i;ns=values[4*i:4*i+4];faces[fi]=ns;zones[fi]=zone
        for ci in ns[2:]:
            if ci:cell_faces[ci].append(fi)
paths=['suction_p_yplus.csv','pressure_p_yplus.csv','trailing_p_yplus.csv']
by_cell={};input_provenance=[]
for name in paths:
    p=ROOT/'solver/case03_aligned/raw'/name
    input_provenance.append({'path':str(p),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    with p.open() as f:
        for row in csv.DictReader(f):
            a={k.strip():float(v) for k,v in row.items()}
            ci=int(a['cell-id'])
            assert ci not in by_cell
            by_cell[ci]={'raw':a,'source_csv':name}
assert len(by_cell)==103
low=sorted(ci for ci,v in by_cell.items() if v['raw']['y-plus']<30)
assert low==[69,2573,7251,7316,7588]
names={5:'aerofoil_te',6:'aerofoil_pressure',7:'aerofoil_suction'}
def point_mean(ps):return [sum(p[i] for p in ps)/len(ps) for i in (0,1)]
def describe(ci):
    nodeids=sorted({n for fi in cell_faces[ci] for n in faces[fi][:2]})
    wall=[fi for fi in cell_faces[ci] if zones[fi] in names and 0 in faces[fi][2:]]
    assert len(nodeids)==3 and len(wall)==1
    fi=wall[0];ns=list(faces[fi][:2]);edge=[nodes[n] for n in ns]
    third=next(n for n in nodeids if n not in ns)
    return {'cell_id':ci,'yplus':by_cell[ci]['raw']['y-plus'],'pressure_Pa':by_cell[ci]['raw']['pressure'],
    'source_csv':by_cell[ci]['source_csv'],'raw_csv_coordinate_m':[by_cell[ci]['raw']['x-coordinate'],by_cell[ci]['raw']['y-coordinate']],
    'cell_node_ids':nodeids,'cell_vertices_m':[nodes[n] for n in nodeids],'cell_geometric_centroid_m':point_mean([nodes[n] for n in nodeids]),
    'wall_face_id':fi,'wall_zone_id':zones[fi],'wall_zone_name':names[zones[fi]],'wall_node_ids':ns,'wall_edge_vertices_m':edge,
    'wall_edge_midpoint_m':point_mean(edge),'nonwall_apex_node_id':third,'nonwall_apex_m':nodes[third],'wall_edge_length_m':math.dist(*edge),
    'wall_face_connections':{'cell_0':faces[fi][2],'cell_1':faces[fi][3]}}
all_cells={ci:describe(ci) for ci in by_cell}
selected=[all_cells[ci] for ci in low]
wallnodes=defaultdict(list)
for c in selected:
    for n in c['wall_node_ids']:wallnodes[n].append(c['cell_id'])
endnodes=[n for n,cs in wallnodes.items() if len(cs)==1]
assert all(len(v)<=2 for v in wallnodes.values())
ordered=sorted(selected,key=lambda c:c['wall_edge_midpoint_m'][0])
remaining=set(low);components=[]
while remaining:
    seed=min(remaining,key=lambda ci:all_cells[ci]['wall_edge_midpoint_m'][0])
    component=set();pending=[seed]
    while pending:
        ci=pending.pop()
        if ci in component:continue
        component.add(ci)
        for n in all_cells[ci]['wall_node_ids']:
            pending.extend(cj for cj in wallnodes[n] if cj not in component)
    remaining-=component
    cnodes={n for ci in component for n in all_cells[ci]['wall_node_ids']}
    endpoints=[n for n in cnodes if len([ci for ci in wallnodes[n] if ci in component])==1]
    assert len(endpoints)==2
    current=min(endpoints,key=lambda n:nodes[n][0]);path=[current];seen=set();chain=[]
    while True:
        candidates=[ci for ci in wallnodes[current] if ci in component and ci not in seen]
        if not candidates:break
        assert len(candidates)==1
        ci=candidates[0];seen.add(ci);chain.append(ci);n1,n2=all_cells[ci]['wall_node_ids'];current=n2 if n1==current else n1;path.append(current)
    components.append({'cell_ids_wall_order':chain,'wall_face_ids':[all_cells[ci]['wall_face_id'] for ci in chain],'node_ids':path,'coordinates_m':[nodes[n] for n in path]})
assert [len(c['cell_ids_wall_order']) for c in components]==[1,4]
verts=[p for c in selected for p in c['cell_vertices_m']]
x0=min(p[0] for p in verts);x1=max(p[0] for p in verts);yb=max(p[1] for p in verts)+.0012
wallverts=[p for c in components for p in c['coordinates_m']]
wx0=min(p[0] for p in wallverts);wx1=max(p[0] for p in wallverts)
def overlap(a,b):return max(0,min(max(a),max(b))-max(min(a),min(b)))
wall_projection=[c for c in all_cells.values() if overlap([p[0] for p in c['wall_edge_vertices_m']],[x0,x1])>1e-12]
suction_projection=[c for c in wall_projection if c['wall_zone_name']=='aerofoil_suction']
triangle_projection=[c for c in all_cells.values() if c['wall_zone_name']=='aerofoil_suction' and overlap([p[0] for p in c['cell_vertices_m']],[x0,x1])>1e-12]
def compact(c):return {k:c[k] for k in ['cell_id','yplus','wall_zone_name','wall_face_id','wall_edge_midpoint_m']}
audit={
 'method':'Read actual native binary mesh plus original three wall CSV files. No Fluent session, CFD update, or modification of native PNG/CASE/DATA.',
 'mesh_source':{'path':str(mesh_path),'bytes':len(blob),'sha256':hashlib.sha256(blob).hexdigest()},
 'CSV_sources':input_provenance,
 'reused_CaseData_hash_evidence':{'path':'solver/native_figures_2026-11-10-centered/logs/source_hashes_verified.json','note':'Existing native postprocessing before/after hash record is referenced; no new Fluent session and no new H5 hash pass was needed.'},
 'threshold':{'operator':'<','yplus':30,'total_foil_wall_adjacent_cells':103,'selected_unique_cells':len(selected),'selected_ids_sorted':low},
 'selected_cells_in_upstream_to_TE_wall_order':ordered,
 'selected_wall_edge_topology':{'connected_component_count':2,'component_cell_counts':[1,4],'components':components,'selected_wall_edges_are_NOT_one_continuous_five_cell_interval':True,'intervening_unselected_cell':all_cells[6134]},
 'old_annotation':{'rule':'xmin/xmax of ALL vertices of the five selected triangles; y=maximum vertex y+0.0012m','world_bracket_m':[x0,x1,yb],
 'suction_wall_faces_whose_x_projection_overlaps_bracket':sorted([compact(c) for c in suction_projection],key=lambda c:c['wall_edge_midpoint_m'][0]),
 'suction_triangles_whose_full_x_projection_overlaps_bracket':sorted([compact(c) for c in triangle_projection],key=lambda c:c['wall_edge_midpoint_m'][0]),
 'extra_suction_triangle_ids_in_projection':[c['cell_id'] for c in triangle_projection if c['cell_id'] not in low],
 'comparison_scope':'The seven visible-projection candidates here are suction-side wall-adjacent triangles only. TE cell7516 is not included in this seven-cell explanation.',
 'left_apex_neighbour':all_cells[7578],
 'why_seven':'Cell7578 has a nonwall apex entering the bracket x-projection from the left although its wall edge ends at the bracket xmin. Cell6134 is an actual intervening suction wall cell above30 between the isolated first low cell and the remaining four. A global projection bracket therefore does not identify precisely five cells.'},
 'exact_wall_edge_annotation_data':{'selected_wall_edges_global_x_extent_m':[wx0,wx1],'same_as_old_projection_span':abs(wx0-x0)<1e-15 and abs(wx1-x1)<1e-15,'single_wall_extent_bracket_does_not_remove_the_gap':True,
 'five_short_leader_targets_m':[c['wall_edge_midpoint_m'] for c in ordered],
 'five_label_records':[{'label':str(i+1),'cell_id':c['cell_id'],'wall_face_id':c['wall_face_id'],'yplus':c['yplus'],'wall_midpoint_m':c['wall_edge_midpoint_m'],'cell_centroid_m':c['cell_geometric_centroid_m']} for i,c in enumerate(ordered)],
 'suggestion':'Use five separate short callouts to these exact wall-face midpoints (or five cell centroids if the intended target is filled cells). The selected wall edges form one isolated edge plus four consecutive edges, separated by cell6134. A single narrower horizontal bracket cannot express that gap. Preserve native field fill; annotations must not imitate externally reconstructed scientific cells.'}
}
reused_hash_path=ROOT/'solver/native_figures_2026-11-10-centered/logs/source_hashes_verified.json'
audit['reused_CaseData_hash_evidence']['Case3_records']=[r for r in json.loads(reused_hash_path.read_text(encoding='utf-8-sig')) if 'case03_aligned' in r['Path']]
audit['coordinate_interpretation']={'wall_CSV_coordinates_are_near_wall_face_midpoints_not_cell_centroids':True,'max_wall_CSV_to_exact_wall_midpoint_distance_m':max(math.dist(c['raw_csv_coordinate_m'],c['wall_edge_midpoint_m']) for c in ordered),'leader_target_options':'Choose exact wall-edge midpoint for wall-edge identification, or actual triangle centroid for an interior cell marker; these are different physical coordinates.'}
assert audit['coordinate_interpretation']['max_wall_CSV_to_exact_wall_midpoint_distance_m']<1e-7
reference_path=ROOT/'review/fig05_exact_five_cells_2026-11-10/exact_five_cells.json'
reference=json.loads(reference_path.read_text())
assert [c['cell_id'] for c in ordered]==[c['cell_id'] for c in reference['ordered_exact_cells']]
assert {c['cell_id'] for c in triangle_projection}=={c['cell_id'] for c in reference['all_suction_triangles_overlapping_old_projection']}
assert set(audit['old_annotation']['extra_suction_triangle_ids_in_projection'])=={6134,7578}
audit['independent_review_crosscheck']={'reference':str(reference_path),'ordered_five_IDs_match':True,'seven_suction_triangle_projection_IDs_match':True,'extra_IDs':[7578,6134]}
(OUT/'exact_five_cell_geometry.json').write_text(json.dumps(audit,indent=2))
print(json.dumps({'low_ids_wall_order':[c['cell_id'] for c in ordered],'low_yplus_wall_order':[c['yplus'] for c in ordered],'wall_component_sizes':[1,4],'full_vertex_bracket':[x0,x1,yb],'global_wall_edge_x_extent':[wx0,wx1],'projected_suction_wall_face_count':len(suction_projection),'projected_suction_triangle_count':len(triangle_projection),'extra_suction_triangles':audit['old_annotation']['extra_suction_triangle_ids_in_projection']},indent=2))

