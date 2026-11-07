"""Verify actual new CAD inputs/endpoints against the provided mesh's rigid placement."""
import csv
import hashlib
import json
import math
from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET

root=Path(__file__).resolve().parent.parent
base=root/'solver/aligned_taskA'
reference=json.loads((Path(__file__).parent/'enhanced_mesh_geometry_audit.json').read_text())
translation=reference['leading_edge_m']
def rows(p): return list(csv.DictReader(p.open()))
old={(r['side'],r['index']):r for r in rows(root/'solver/taskA/foil_coordinates_m.csv')}
new=rows(base/'foil_coordinates_m.csv')
assert len(new)==len(old)==802
translation_error=0;formula_error=0
angle=math.radians(-8)
for row in new:
    source=old[row['side'],row['index']]
    x,y,z=[float(row[k]) for k in ['x_m','y_m','z_m']]
    translation_error=max(translation_error,abs(x-float(source['x_m'])-translation[0]),
                          abs(y-float(source['y_m'])-translation[1]),abs(z))
    dx,dy=x-translation[0],y-translation[1]
    xb=dx*math.cos(angle)+dy*math.sin(angle)
    yb=-dx*math.sin(angle)+dy*math.cos(angle)
    t=max(0,min(1,xb/.1));sign=1 if row['side']=='suction' else -1
    expected=sign*.06*(.2969*math.sqrt(t)-.126*t-.3516*t*t+.2843*t**3-.1015*t**4)
    formula_error=max(formula_error,abs(yb-expected))
edges=rows(base/'boundary_edges.csv')
byname={r['name']:r for r in edges}
def endpoints(name):
    r=byname[name]
    return {(float(r[k+'_x_m']),float(r[k+'_y_m'])) for k in ['start','end']}
pressure,suction=endpoints('aerofoil_pressure'),endpoints('aerofoil_suction')
common=pressure&suction;assert len(common)==1
leading=next(iter(common));trailing=(pressure|suction)-common
te=tuple(sum(p[i] for p in trailing)/2 for i in [0,1])
outer=rows(root/'solver/taskA/boundary_edges.csv')
oldouter={r['name']:r for r in outer if not r['name'].startswith('aerofoil')}
assert all(byname[name]==row for name,row in oldouter.items())
with zipfile.ZipFile(base/'taskA_geometry.scdoc') as archive:
    document=ET.fromstring(archive.read('SpaceClaim/document.xml'))
    groups=[]
    for e in document.iter():
        if e.tag.split('}')[-1]=='NamedSelectionDef':
            names=[n.text for n in e if n.tag.split('}')[-1]=='name']
            refs=[n.attrib['refId'] for n in e.iter() if 'refId' in n.attrib]
            groups.append({'name':names,'objects':refs})
result={'sources':[{'path':str(base/name),'sha256':hashlib.sha256((base/name).read_bytes()).hexdigest()}
                   for name in ['create_geometry.py','foil_coordinates_m.csv','boundary_edges.csv','taskA_geometry.scdoc','geometry_properties.txt']],
        'translation_target_m':translation,'coordinate_count':len(new),
        'maximum_actual_translation_error_m':translation_error,'maximum_NACA_formula_vertical_residual_m':formula_error,
        'shared_LE_from_actual_curve_endpoints_m':leading,'trailing_edge_center_m':te,
        'LE_match_provided_m':math.dist(leading,reference['leading_edge_m']),
        'TE_match_provided_m':math.dist(te,reference['trailing_edge_centre_m']),
        'chord_m':math.dist(leading,te),'chord_angle_deg':math.degrees(math.atan2(te[1]-leading[1],te[0]-leading[0])),
        'outer_duct_edges_unchanged':True,'named_selections':groups,
        'limitation':'Actual CAD endpoint/coordinate inputs and saved names verified. New kernel hole check and exported mesh topology/quality remain separate gates.'}
target=Path(__file__).parent/'aligned_geometry_audit.json'
target.write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
