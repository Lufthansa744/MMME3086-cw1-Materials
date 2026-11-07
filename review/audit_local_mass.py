"""Audit actual native per-cell mass-imbalance values without a residual-floor inference."""
from pathlib import Path
import contextlib,io,csv,math,json,hashlib,re
with contextlib.redirect_stdout(io.StringIO()):import verify_aligned_mesh as mesh
root=Path(__file__).resolve().parents[1]
evidence=root/'solver/case02_mass_diagnostic/logs/native.transcript'
text=evidence.read_text();assert re.search(r'Mass Imbalance\s+\[kg/s\]',text)
out={'units':'kg/s','unit_evidence':str(evidence),'unit_evidence_sha256':hashlib.sha256(evidence.read_bytes()).hexdigest(),'cases':{}}
for run,folder in [('case02_aligned','case02_mass_diagnostic'),('case03_aligned','case03_aligned')]:
    path=root/'solver'/folder/'raw/cell_mass_imbalance.csv'
    rows=[{k.strip():float(v) for k,v in r.items()} for r in csv.DictReader(path.open())]
    assert len(rows)==7687 and {int(r['cell-id']) for r in rows}==set(range(1,7688))
    errors=[];volerrors=[]
    for r in rows:
        cid=int(r['cell-id']);verts={n for f in mesh.cell_faces[cid] for n in mesh.faces[f][:2]}
        ps=[mesh.nodes[n] for n in verts];mid=[sum(p[j] for p in ps)/3 for j in [0,1]]
        errors.append(math.dist(mid,[r['x-coordinate'],r['y-coordinate']]))
        if 'cell-volume' in r:
            a,b,c=ps;area=abs((b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]))/2
            volerrors.append(abs(area-r['cell-volume'])/area)
    assert max(errors)<1e-7
    vals=[r['mass-imbalance'] for r in rows];inlet=1.225*50.9*.15
    extreme=max(rows,key=lambda r:abs(r['mass-imbalance']))
    out['cases'][run]={'source':str(path),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
      'unique_cell_ids':7687,'max_center_mapping_error_m':max(errors),
      'cell_volume_vs_native_2D_area_max_relative_error':max(volerrors) if volerrors else None,
      'min_kg_s':min(vals),'max_kg_s':max(vals),'max_abs_kg_s':max(map(abs,vals)),
      'signed_sum_kg_s':math.fsum(vals),'sum_abs_kg_s':math.fsum(map(abs,vals)),
      'max_abs_over_inlet_percent':max(map(abs,vals))/inlet*100,
      'sum_abs_over_inlet_percent':math.fsum(map(abs,vals))/inlet*100,
      'max_abs_cell':extreme}
out['interpretation']='The exported local finite-volume mass imbalance is small relative to total inlet mass flow in these saved states. Signed summation checks cancellation against global net flux; sum of magnitudes reports local cancellation separately. These dimensional diagnostics neither prove the scaled residual target was achieved nor identify the mechanism of its plateau. Case 3 uses the same native field confirmed in the Case 2 native report; units are not inferred from the CSV header alone.'
target=root/'review/local_mass_imbalance_audit.json';target.write_text(json.dumps(out,indent=2),encoding='utf-8');print(json.dumps(out,indent=2))
