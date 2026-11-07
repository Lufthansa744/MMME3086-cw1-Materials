"""Recompute data coverage with independent review native mesh readers."""
import contextlib,io,json,math,csv,hashlib
from pathlib import Path
with contextlib.redirect_stdout(io.StringIO()):
    import audit_enhanced_mesh as enhanced
    import verify_aligned_mesh as aligned
root=Path(__file__).resolve().parents[1]
checks={}
for case in ['case01_aligned','case02_aligned','case03_aligned','case04_verified','case05_verified']:
    m=aligned if 'aligned' in case else enhanced
    path=root/'data'/case/'wall_length_coverage.json'
    data=json.loads(path.read_text(encoding='utf-8'));result={}
    for source in data['sources']:
        assert hashlib.sha256(Path(source['path']).read_bytes()).hexdigest()==source['sha256']
    for side,rec in data['sides'].items():
        native=root/'solver'/case/'raw'/f'{side}_p_yplus.csv'
        rows=[{k.strip():float(v) for k,v in r.items()} for r in csv.DictReader(native.open())]
        expected={};lengths=[]
        for item in rec['native_faces']:
            fi=item['face_id'];face=m.faces[fi]
            a,b=m.nodes[face[0]],m.nodes[face[1]]
            length=math.dist(a,b)
            assert abs(length-item['length_m'])<1e-14
            mid=[(a[j]+b[j])/2 for j in range(2)]
            matching=[r for r in rows if int(r['cell-id'])==item['adjacent_cell_id'] and math.dist(mid,[r['x-coordinate'],r['y-coordinate']])<1e-7]
            assert len(matching)==1 and matching[0]['y-plus']==item['yplus']
            expected[fi]=length;lengths.append((length,item['yplus']))
        assert len(expected)==len(rows)==rec['face_count']
        total=math.fsum(expected.values())
        assert abs(total-rec['length_m'])<1e-13
        f={
          'at_most_1':math.fsum(l for l,y in lengths if y<=1)/total,
          'above_1_to_5':math.fsum(l for l,y in lengths if 1<y<=5)/total,
          'above_5':math.fsum(l for l,y in lengths if y>5)/total,
          'below_30':math.fsum(l for l,y in lengths if y<30)/total,
          'from_30_to_300':math.fsum(l for l,y in lengths if 30<=y<=300)/total,
          'above_300':math.fsum(l for l,y in lengths if y>300)/total}
        assert max(abs(f[k]-rec['length_fractions'][k]) for k in f)<1e-13
        result[side]={'faces':len(rows),'length_m':total,'independent_length_fractions':f}
    checks[case]={'coverage_source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'sides':result}
target=root/'review/wall_length_coverage_audit.json'
target.write_text(json.dumps(checks,indent=2),encoding='utf-8')
print('PASS independent mesh lengths, native face scalars and all six coverage fractions for five final runs')
