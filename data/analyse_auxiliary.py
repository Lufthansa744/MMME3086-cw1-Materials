"""Source-bound auxiliary grid and inlet-length diagnostics, separate from five cases."""
from collections import defaultdict
import csv
import json
import math
from pathlib import Path
import re
from plot_taskA_mesh import parse_mesh,sha
from process_case import graph

ROOT=Path(__file__).resolve().parents[1]

def load(case):
    p=ROOT/'data'/case/'case_summary.json'
    if not p.exists():return None
    s=json.loads(p.read_text());setting=ROOT/'data'/case/'native/settings'/f'{case}_final.set'
    text=setting.read_text();inlet=re.search(r'\(bc \(inlet velocity-inlet mixture\) \(\n(.*?)\n\)\)',text,re.S).group(0)
    s['actual_inlet_length_m']=float(re.search(r'\(turb-length-scale \. ([\d.eE+-]+)\)',inlet).group(1))
    return {'case':case,'summary':s,'source':{'path':str(p),'sha256':sha(p)},'actual_settings':{'path':str(setting),'sha256':sha(setting)}}

def grid(case,path):
    d=load(case)
    if not d:return None
    mesh=ROOT/path;nodes,faces,zones,counts=parse_mesh(mesh);cellnodes=defaultdict(set)
    for n0,n1,c0,c1 in faces.values():
        for ci in [c0,c1]:
            if ci:cellnodes[ci].update([n0,n1])
    area=0
    for ns in cellnodes.values():
        centre=tuple(sum(nodes[n][j] for n in ns)/len(ns) for j in [0,1]);ordered=sorted(ns,key=lambda n:math.atan2(nodes[n][1]-centre[1],nodes[n][0]-centre[0]))
        area+=abs(sum(nodes[a][0]*nodes[b][1]-nodes[b][0]*nodes[a][1] for a,b in zip(ordered,ordered[1:]+ordered[:1])))/2
    s=d['summary'];d.update(mesh={'path':str(mesh),'sha256':sha(mesh)},cells=counts['cells'],domain_area_m2=area,effective_h_m=math.sqrt(area/counts['cells']))
    d['metrics']={k:s[k] for k in ['CD','CL','iteration','numeric_final_acceptance_gate_passed']};return d

def main():
    out=ROOT/'data/auxiliary';out.mkdir(exist_ok=True)
    grids=[grid(c,p) for c,p in [('case01_aligned','solver/aligned_taskA/taskA_baseline.msh'),('sa_grid_medium','solver/grid_medium_mesh/mesh.msh'),('sa_grid_fine','solver/grid_fine_mesh/mesh.msh')]]
    ready=[d for d in grids if d];changes=[]
    for coarse,fine in zip(ready,ready[1:]):
        keys=['rho_kg_m3','mu_Pa_s','U_m_s','TI_fraction','chord_m','area_m2']
        if any(coarse['summary']['parameters'][k]!=fine['summary']['parameters'][k] for k in keys) or coarse['summary']['actual_inlet_length_m']!=fine['summary']['actual_inlet_length_m']:raise ValueError('Grid-study physical inputs differ')
        changes.append({'from':coarse['case'],'to':fine['case'],'actual_h_ratio':coarse['effective_h_m']/fine['effective_h_m'],
                        'relative_change_using_coarser_result':{k:(fine['metrics'][k]-coarse['metrics'][k])/coarse['metrics'][k] for k in ['CD','CL']}})
    result={'scope':'Auxiliary S-A refinement study; not a sixth coursework case','complete_three_grids':len(ready)==3,'datasets':ready,'successive_changes':changes,
            'effective_h_definition':'sqrt(sum actual native 2D cell polygon areas / actual cell count), not the nominal Mesher sizing ratio.',
            'limits':'Changes show sensitivity for these actual grids. No grid-independence claim, extrapolated continuum value, observed order or GCI is inferred automatically. Near-wall resolution, CAD boundary discretisation and unstructured refinement require independent interpretation.'}
    sensitivity=load('sensitivity_ke_length_001');baseline=load('case02_aligned')
    if sensitivity:
        for key in ['rho_kg_m3','mu_Pa_s','U_m_s','TI_fraction','chord_m','area_m2']:
            if sensitivity['summary']['parameters'][key]!=baseline['summary']['parameters'][key]:raise ValueError('Length sensitivity physical input also differs: '+key)
        result['inlet_length_sensitivity']={'baseline':baseline,'perturbed':sensitivity,'relative_change_using_baseline':{k:(sensitivity['summary'][k]-baseline['summary'][k])/baseline['summary'][k] for k in ['CD','CL']},
                                            'scope':'A declared inlet length perturbation, not an experimentally established input. Numerical limitations of both runs must remain explicit.'}
        figure_dir=out/'figures';figure_dir.mkdir(exist_ok=True);profile_traces=[];pressure_traces=[];plot_sources=[]
        for item,color,dash in [(baseline,'#0072b2',''),(sensitivity,'#d55e00','10 5')]:
            file=ROOT/'data'/item['case']/'workbook_input.json';native=json.loads(file.read_text());name=f'L = {item["summary"]["actual_inlet_length_m"]:g} m'
            plot_sources.append({'path':str(file),'sha256':sha(file)})
            profile_traces.append({'name':name,'color':color,'dash':dash,'chunks':[[(r['y-coordinate']*1000,r['velocity-magnitude']) for r in native['profiles']['wake']]]})
            pressure_traces.append({'name':name,'color':color,'dash':dash,'chunks':[[(r['x-coordinate']*1000,r['pressure']) for r in native['surfaces']['suction']]]})
        graph(figure_dir/'length_sensitivity_wake.svg',profile_traces,'y (mm)','Velocity (m/s)',xrange=(-75,75),layout='profile_print')
        graph(figure_dir/'length_sensitivity_suction.svg',pressure_traces,'x (mm)','Static pressure (Pa)',xrange=(0,100),layout='half_print')
        result['inlet_length_sensitivity']['plots']={'sources':plot_sources,'method':'Each actual native sample at its original coordinate, no interpolation or smoothing; wake station is fixed x=0.20 m.',
                                                    'outputs':[{'path':str(p),'sha256':sha(p)} for p in sorted(figure_dir.glob('length_sensitivity*.svg'))]}
    result['script']={'path':str(Path(__file__)),'sha256':sha(Path(__file__))}
    (out/'auxiliary_comparison.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    with (out/'grid_comparison.csv').open('w',newline='',encoding='utf-8') as f:
        fields=['dataset','cells','effective_h_m','domain_area_m2','CD','CL','iteration','numeric_strict_gate'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for d in ready:w.writerow(dict(zip(fields,[d['case'],d['cells'],d['effective_h_m'],d['domain_area_m2'],d['metrics']['CD'],d['metrics']['CL'],d['metrics']['iteration'],d['metrics']['numeric_final_acceptance_gate_passed']])))
    print(f'Auxiliary grid datasets available: {len(ready)}/3; length perturbation available: {bool(sensitivity)}')

if __name__=='__main__':main()
