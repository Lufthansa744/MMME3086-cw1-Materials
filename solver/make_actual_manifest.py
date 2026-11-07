"""Build a per-run manifest from actual saved Fluent settings and native history."""
import argparse, csv, hashlib, json, re, statistics
from pathlib import Path

p=argparse.ArgumentParser()
p.add_argument('run'); p.add_argument('--model',required=True)
p.add_argument('--mesh',required=True); p.add_argument('--source',required=True)
p.add_argument('--initialization',required=True); p.add_argument('--wall',required=True)
p.add_argument('--start-iteration',type=int,default=0)
p.add_argument('--criterion',type=float,default=.001)
a=p.parse_args(); root=Path(__file__).resolve().parent; run=root/a.run
settings=run/'settings'/f'{a.run}_final.set'
t=settings.read_text(encoding='utf-8',errors='replace')
logpath=run/'logs/setup.transcript'; log=logpath.read_text(encoding='utf-8',errors='replace')
air=next(x for x in t.splitlines() if x.startswith('(materials ((air fluid '))
bc=re.search(r'\(bc \(inlet velocity-inlet mixture\) \(\n(.*?)\n\)\)',t,re.S).group(0)
def num(pattern,source):
    m=re.search(pattern,source)
    if not m: raise ValueError('Actual setting missing: '+pattern)
    return float(m.group(1))
rho=num(r'\(density \(constant \. ([\d.eE+-]+)\)',air)
mu=num(r'\(viscosity \(constant \. ([\d.eE+-]+)\)',air)
u=num(r'\(vmag \(constant \. ([\d.eE+-]+)\)',bc)
intensity=num(r'\(turb-intensity \. ([\d.eE+-]+)\)',bc)
length=num(r'\(turb-length-scale \. ([\d.eE+-]+)\)',bc)
if '(ke-spec . 1)' not in bc: raise ValueError('Expected actual intensity/length inlet method')
if abs(u-50.9)>1e-9: raise ValueError('Inlet speed differs from authorised value')
cols=None; rows=[]
for line in log.splitlines():
    s=line.split()
    if len(s)>3 and s[0]=='iter' and s[1]=='continuity':
        cols=s[:s.index('time/iter')]
    elif cols and len(s)>len(cols) and re.fullmatch(r'\d+',s[0]):
        try: row=dict(zip(cols,[float(x) for x in s[:len(cols)]]))
        except ValueError: continue
        rows.append(row)
rows=[r for r in rows if r['iter']>a.start_iteration]
reprinted_rows=len(rows)-len({r['iter'] for r in rows})
rows=list({r['iter']:r for r in rows}.values())
last=rows[-1]
force=[]
for line in (run/'monitors/forces.out').read_text().splitlines():
    z=line.split()
    if len(z)==3 and z[0].isdigit(): force.append([float(v) for v in z])
mass=[]
for line in (run/'monitors/mass_balance.out').read_text().splitlines():
    z=line.split()
    if len(z)==2 and z[0].isdigit(): mass.append([float(v) for v in z])
rp={k:v.strip() for k,v in re.findall(r'ACTUAL_RP\s+([A-Za-z0-9_/?-]+)\s*=\s*([^\n]+)',log)}
all_converged=[int(x) for x in re.findall(r'!\s*(\d+)\s+solution is converged',log)]
converged=list(dict.fromkeys(i for i in all_converged if i>a.start_iteration))
res={k:v for k,v in last.items() if k not in ['iter','mass-net','lift-force','drag-force']}
first_printed_1e3=next((int(r['iter']) for r in rows if all(abs(r[k])<=.001 for k in res)),None)
fw=[r for r in force if r[0]>a.start_iteration][-100:]
force_ranges={name:(max(r[col] for r in fw)-min(r[col] for r in fw))/abs(statistics.mean(r[col] for r in fw)) for name,col in [('drag',1),('lift',2)]}
wallzones=re.findall(r'\(bc \((aerofoil[^ ]+) wall mixture\)',t)
manifest={
 'run_id':a.run,'model':a.model,'wall_treatment':a.wall,'mesh':a.mesh,
 'source_state':a.source,'initialization':a.initialization,
 'actual_settings_source':str(settings),'native_log_source':str(logpath),
 'air':{'density_kg_m3':rho,'dynamic_viscosity_Pa_s':mu},
 'inlet':{'speed_m_s':u,'intensity_fraction':intensity,'length_scale_m':length,'selected_method':'Intensity and Length Scale'},
 'reference':{'area_m2':num(r'\(reference-area ([\d.eE+-]+)\)',t),'length_m':num(r'\(reference-length ([\d.eE+-]+)\)',t)},
 'actual_rp_readbacks':rp,'native_auto_convergence_iterations':converged,
 'inherited_start_iteration':a.start_iteration,'inherited_state_convergence_markers':[i for i in all_converged if i<=a.start_iteration],
 'terminal_iteration':int(last['iter']),'new_model_monitored_iterations':len(rows),
 'reprinted_native_iteration_rows_excluded_from_update_count':reprinted_rows,
 'first_iteration_all_printed_active_residuals_le_1e3_after_seed':first_printed_1e3,
 'force_window':{'new_iterations':len(fw),'range_over_absolute_mean':force_ranges,'analyst_target_for_strict_runs':.001,'strict_force_target_met':len(fw)==100 and all(v<=.001 for v in force_ranges.values())},
 'final_residuals':res,'residual_criteria':{k:a.criterion for k in res},
 'final_residual_target_met':all(abs(v)<=a.criterion for v in res.values()),
 'combined_strict_target_met':all(abs(v)<=a.criterion for v in res.values()) and len(fw)==100 and all(v<=.001 for v in force_ranges.values()),
 'force_report':{'zones':wallzones,'drag_vector':[1,0],'lift_vector':[0,1],'scaled':False,'depth_m':1,'units':'N','final_drag_N':force[-1][1],'final_lift_N':force[-1][2]},
 'mass_balance':{'final_net_kg_s':mass[-1][1],'prescribed_inlet_kg_s':rho*u*.15,'absolute_relative_net':abs(mass[-1][1])/(rho*u*.15)},
 'sampling':{'line_x_m':[.05,.1,.2],'y_limits_m':[-.075,.075],'surface_values':'native cell-centered p/y-plus; cell-id when included','velocity_lines':'native node-interpolated magnitude; retain any actual fluid gap'},
 'evidence':[]}
for f in sorted(run.rglob('*')):
    if not f.is_file() or f.name=='manifest.json': continue
    if f.suffix in ['.csv','.set','.jou','.h5','.out']:
        try: digest=hashlib.sha256(f.read_bytes()).hexdigest()
        except PermissionError: continue
        manifest['evidence'].append({'path':str(f.relative_to(run)),'bytes':f.stat().st_size,'sha256':digest})
(run/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(json.dumps({k:manifest[k] for k in ['run_id','terminal_iteration','native_auto_convergence_iterations','force_report','mass_balance']},indent=2))

