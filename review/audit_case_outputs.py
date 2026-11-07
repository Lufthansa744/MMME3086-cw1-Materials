"""Independent, read-only audit of actual per-case native surface/line/force exports."""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import re
import statistics

parser=argparse.ArgumentParser()
parser.add_argument('case_id')
parser.add_argument('--foil-origin',nargs=2,type=float,default=[0.,0.])
parser.add_argument('--iteration-origin',type=int,default=0)
args=parser.parse_args()
root=Path(__file__).resolve().parent.parent
base=root/'solver'/args.case_id
manifest=json.loads((base/'manifest.json').read_text(encoding='utf-8-sig'))
rho=manifest['air']['density_kg_m3']
velocity=manifest['inlet']['speed_m_s']
area=manifest['reference']['area_m2']
normalizer=.5*rho*velocity**2*area
out={'case_id':args.case_id,'normalizing_force_N':normalizer,'foil_frame_origin_m':args.foil_origin,'sources':[]}
for path in sorted(base.rglob('*')):
    if path.is_file() and path.suffix in ['.csv','.out','.set','.transcript','.json','.jou','.txt']:
        out['sources'].append({'path':str(path),'bytes':path.stat().st_size,
                               'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
for name in ['suction_p_yplus.csv','pressure_p_yplus.csv','velocity_mid.csv','velocity_te.csv','velocity_wake.csv']:
    path=base/'raw'/name
    rows=[{k.strip():float(v) for k,v in row.items()} for row in csv.DictReader(path.open())]
    assert all(math.isfinite(v) for row in rows for v in row.values())
    result={'rows':len(rows),'x_range':[min(r['x-coordinate'] for r in rows),max(r['x-coordinate'] for r in rows)],
            'y_range':[min(r['y-coordinate'] for r in rows),max(r['y-coordinate'] for r in rows)]}
    if 'y-plus' in rows[0]:
        normal=[(r['x-coordinate']-args.foil_origin[0])*math.sin(math.radians(8))+(r['y-coordinate']-args.foil_origin[1])*math.cos(math.radians(8)) for r in rows]
        result.update(foil_frame_y_range=[min(normal),max(normal)],
                      yplus_range=[min(r['y-plus'] for r in rows),max(r['y-plus'] for r in rows)],
                      pressure_range=[min(r['pressure'] for r in rows),max(r['pressure'] for r in rows)])
    else:
        ys=sorted(r['y-coordinate'] for r in rows)
        result.update(velocity_range=[min(r['velocity-magnitude'] for r in rows),max(r['velocity-magnitude'] for r in rows)],
                      largest_y_gaps=sorted([(b-a,a,b) for a,b in zip(ys,ys[1:])],reverse=True)[:3])
    out[name]=result
force_text=(base/'monitors/forces.out').read_text()
force_headers=[re.findall(r'"([^"]+)"',line) for line in force_text.splitlines() if line.startswith('(')]
assert force_headers and force_headers[0][:3]==['Iteration','drag-force','lift-force'], 'Verify native force-column identities before using fixed positions'
native_forces=[[float(t) for t in line.split()] for line in force_text.splitlines()
        if re.match(r'^\d+ ',line)]
forces=[r for r in native_forces if r[0]>args.iteration_origin]
assert forces and all(row[0]==forces[0][0]+i for i,row in enumerate(forces)), 'Split restarted/noncontiguous histories explicitly'
out['iteration_origin']=args.iteration_origin
out['native_force_rows_at_or_before_origin']=len(native_forces)-len(forces)
out['first_force_iteration']=forces[0][0]
out['new_model_force_sample_count']=len(forces)
out['force_window_stats']={}
for size in [25,50,100]:
    selected=forces[-size:];stats={}
    for index,key in [(1,'drag_N'),(2,'lift_N')]:
        values=[r[index] for r in selected];mean=statistics.mean(values)
        stats[key]={'samples':len(values),'final':values[-1],'mean':mean,'range':max(values)-min(values),
                    'range_percent_mean':100*(max(values)-min(values))/abs(mean),
                    'endpoint_drift_percent_mean':100*(values[-1]-values[0])/abs(mean)}
    out['force_window_stats'][str(size)]=stats
out['last_force_iteration']=forces[-1][0]
out['CD_final']=forces[-1][1]/normalizer
out['CL_final']=forces[-1][2]/normalizer
mass=manifest.get('mass_report',{})
if not mass and 'mass_balance' in manifest:
    actual=manifest['mass_balance']
    mass={'net_kg_s':actual['final_net_kg_s'],'inlet_kg_s':actual['prescribed_inlet_kg_s']}
    out['mass_denominator_definition']='uniform prescribed inlet rho*U*height*depth from the manifest; check against native flux report separately'
if 'net_kg_s' in mass and 'inlet_kg_s' in mass:
    out['mass_imbalance_fraction']=abs(mass['net_kg_s'])/abs(mass['inlet_kg_s'])
    out['mass_imbalance_percent']=100*out['mass_imbalance_fraction']
out['limitation']='Native values and finite-window diagnostics, not independent acceptance of convergence or experimental accuracy. Foil-frame side check uses the explicitly recorded LE origin and verified clockwise eight-degree chord orientation.'
target=Path(__file__).parent/(args.case_id+'_raw_audit.json')
target.write_text(json.dumps(out,indent=2),encoding='utf-8')
print(target)
