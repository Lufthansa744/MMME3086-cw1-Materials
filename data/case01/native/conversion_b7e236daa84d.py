"""Preserve and process actual Fluent coursework exports into an auditable dataset."""
import argparse
import csv
import hashlib
import html
import json
import math
from pathlib import Path
import re
import statistics
import subprocess
import sys

ROOT=Path(__file__).resolve().parents[1]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def snapshot(source,target):
    data=source.read_bytes();target.parent.mkdir(parents=True,exist_ok=True)
    if target.exists() and target.read_bytes()!=data:
        previous=target.read_bytes()
        if source.suffix=='.transcript' and data.startswith(previous):
            return {'original':str(source),'preserved':str(target),'sha256':sha(target),'bytes':len(previous),'scope':'Preserved complete earlier prefix of append-only transcript; includes all solution iterations','original_current_sha256':sha(source)}
        raise ValueError(f'Native source changed; choose a new data version: {source}')
    if not target.exists():target.write_bytes(data)
    return {'original':str(source),'preserved':str(target),'sha256':sha(target),'bytes':len(data)}


def monitor(path,n):
    values=[]
    for lineno,line in enumerate(path.read_text().splitlines(),1):
        tokens=line.split()
        if tokens and tokens[0].isdigit():
            if len(tokens)!=n:raise ValueError(f'Wrong native column count at {path}:{lineno}')
            row=[float(x) for x in tokens]
            if not all(math.isfinite(x) for x in row):raise ValueError('Nonfinite native monitor')
            values.append([lineno]+row)
    if not values:raise ValueError('Empty monitor')
    if any(a[1]>=b[1] for a,b in zip(values,values[1:])):raise ValueError('Monitor restarted or iteration order invalid')
    return values


def scalar_csv(path):
    with path.open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f);reader.fieldnames=[x.strip() for x in reader.fieldnames]
        rows=[{k:float(v) for k,v in r.items()} for r in reader]
    if not rows or not all(math.isfinite(v) for r in rows for v in r.values()):raise ValueError('Empty or invalid export')
    return rows


def write_csv(path,headers,rows):
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.writer(f);w.writerow(headers);w.writerows(rows)


def graph(path,series,xlabel,ylabel,logy=False,threshold=None,xrange=None):
    width,height=1200,760;l,r,t,b=150,45,95,120
    points=[p for s in series for chunk in s['chunks'] for p in chunk]
    if not points:raise ValueError('No plot points')
    def nice_axis(low,high,positive=False):
        span=high-low or max(abs(high),1)
        rough=span/5; power=10**math.floor(math.log10(rough))
        step=min([1,2,2.5,5,10],key=lambda x:abs(math.log((rough/power)/x)))*power
        low=math.floor(low/step)*step;high=math.ceil(high/step)*step
        if positive:low=0
        return low,high,[low+step*i for i in range(int(round((high-low)/step))+1)]
    xmin,xmax,xticks=nice_axis(*(xrange or (min(p[0] for p in points),max(p[0] for p in points))))
    yvalues=[p[1] for p in points]
    if logy:
        if min(yvalues)<=0:raise ValueError('Cannot silently log nonpositive data')
        ymin=math.floor(math.log10(min(yvalues)));ymax=math.ceil(math.log10(max(yvalues)))
        if threshold:ymin=min(ymin,math.log10(threshold));ymax=max(ymax,math.log10(threshold))
        yticks=list(range(int(ymin),int(ymax)+1));convert=math.log10
    else:
        ymin,ymax=min(yvalues),max(yvalues);pad=(ymax-ymin)*.04 or max(abs(ymax)*.1,.1)
        ymin,ymax,yticks=nice_axis(ymin-pad,ymax+pad,min(yvalues)>=0);convert=lambda y:y
    def px(x):return l+(x-xmin)/(xmax-xmin or 1)*(width-l-r)
    def py(y):return height-b-(y-ymin)/(ymax-ymin or 1)*(height-t-b)
    svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">','<rect width="100%" height="100%" fill="white"/>','<g font-family="Arial,sans-serif" font-size="29" fill="#222">']
    for y in yticks:
        yy=py(y);svg.append(f'<path d="M{l},{yy}H{width-r}" stroke="#ddd" fill="none"/>')
        label=f'10<tspan baseline-shift="super" font-size="21">{int(y)}</tspan>' if logy else f'{y:.4g}'
        svg.append(f'<text x="{l-15}" y="{yy+9}" text-anchor="end">{label}</text>')
    for x in xticks:
        svg.append(f'<text x="{px(x)}" y="{height-b+43}" text-anchor="middle">{x:.5g}</text>')
    svg.append(f'<path d="M{l},{t}V{height-b}H{width-r}" fill="none" stroke="#222" stroke-width="2"/>')
    svg.append(f'<text x="{(l+width-r)/2}" y="{height-28}" text-anchor="middle" font-size="32">{html.escape(xlabel)}</text>')
    svg.append(f'<text x="35" y="{(t+height-b)/2}" text-anchor="middle" transform="rotate(-90,35,{(t+height-b)/2})" font-size="32">{html.escape(ylabel)}</text>')
    if threshold:
        yy=py(convert(threshold));svg.append(f'<path d="M{l},{yy}H{width-r}" stroke="#222" stroke-width="1.6" stroke-dasharray="10 7"/>')
    legend_x=l
    for s in series:
        for chunk in s['chunks']:
            pts=' '.join(f'{px(x):.4f},{py(convert(y)):.4f}' for x,y in chunk)
            svg.append(f'<polyline points="{pts}" fill="none" stroke="{s["color"]}" stroke-width="2.7"/>')
            if s.get('markers'):
                for x,y in chunk:svg.append(f'<circle cx="{px(x):.4f}" cy="{py(convert(y)):.4f}" r="3.5" fill="white" stroke="{s["color"]}" stroke-width="1.5"/>')
        svg.append(f'<path d="M{legend_x},40h38" stroke="{s["color"]}" stroke-width="3"/>')
        svg.append(f'<text x="{legend_x+48}" y="49" font-size="27">{html.escape(s["name"])}</text>')
        legend_x+=len(s['name'])*16+100
    svg.append('</g></svg>');path.write_text('\n'.join(svg),encoding='utf-8')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--case',default='case01');parser.add_argument('--label',default='Case 1 S-A')
    args=parser.parse_args();src=ROOT/'solver'/args.case;out=ROOT/'data'/args.case;prov=out/'native';plots=out/'figures';plots.mkdir(parents=True,exist_ok=True)
    files=['monitors/forces.out','monitors/mass_balance.out','settings/'+args.case+'_final.set','logs/setup.transcript']
    files+=['raw/'+n+'.csv' for n in ['suction_p_yplus','pressure_p_yplus','velocity_mid','velocity_te','velocity_wake']]
    sources=[snapshot(src/n,prov/n) for n in files]
    settings=prov/'settings'/f'{args.case}_final.set';text=settings.read_text()
    if '(solution/converged? #t)' not in text:raise ValueError('Saved actual settings do not declare convergence; process separately as nonconverged')
    material=next(l for l in text.splitlines() if l.startswith('(materials ((air fluid '))
    def num(pattern,content=text):
        m=re.search(pattern,content)
        if not m:raise ValueError('Missing actual setting '+pattern)
        return float(m.group(1))
    rho=num(r'\(density \(constant \. ([\d.eE+-]+)\)',material);mu=num(r'\(viscosity \(constant \. ([\d.eE+-]+)\)',material)
    inlet=re.search(r'\(bc \(inlet velocity-inlet mixture\) \(\n(.*?)\n\)\)',text,re.S).group(0)
    speed=num(r'\(vmag \(constant \. ([\d.eE+-]+)\)',inlet);ti=num(r'\(turb-intensity \. ([\d.eE+-]+)\)',inlet)
    chord=num(r'\(reference-length ([\d.eE+-]+)\)');area=num(r'\(reference-area ([\d.eE+-]+)\)')
    if speed!=50.9 or '(rp-3d? . #f)' not in text:raise ValueError('Input velocity or 2D convention differs')
    if not all(name in text for name in ['aerofoil_te','aerofoil_pressure','aerofoil_suction']):raise ValueError('Body zones absent')
    forces=monitor(prov/'monitors/forces.out',3);mass=monitor(prov/'monitors/mass_balance.out',2)
    if [r[1] for r in forces]!=[r[1] for r in mass]:raise ValueError('Force and mass monitor iteration mismatch')
    normal=out/'forces_normalized.csv';write_csv(normal,['iteration','Fx_N','Fy_N','Fz_N'],[[r[1],r[2],r[3],0] for r in forces])
    evidence={k:{'path':str(settings),'locator':loc} for k,loc in {
        'density_kg_m3':'materials/air/density/constant','reference_speed_m_s':'bc/inlet/vmag constant and reference-velocity',
        'reference_area_m2':'reference-area','drag_direction':'monitor/report-definitions drag-force force-vector (1 0), global, scaled? #f',
        'lift_direction':'monitor/report-definitions lift-force force-vector (0 1), global, scaled? #f',
        'force_definition':'drag/lift report definitions: total force on aerofoil_te + aerofoil_pressure + aerofoil_suction; 2D rp-3d? #f; actual depth 1 m recorded in setup transcript'}.items()}
    evidence['native_force_source']={'path':str(prov/'monitors/forces.out'),'locator':'header (Iteration drag-force lift-force); all numeric records'}
    script_path=Path(__file__).resolve();script_digest=sha(script_path)
    script_copy=prov/f'conversion_{script_digest[:12]}.py';snapshot(script_path,script_copy)
    evidence['conversion_script']={'path':str(script_copy),'locator':'monitor() and main() mapping native drag/lift to Fx/Fy; Fz=0 from actual 2D setup'}
    mapping={k:{'source':source,'expression':expr,'source_units':unit,'target_units':target} for k,source,expr,unit,target in [
        ('iteration','Iteration','Iteration','iteration','iteration'),('Fx_N','drag-force','+drag-force','N','N'),('Fy_N','lift-force','+lift-force','N','N'),('Fz_N','2D case model','0, because rp-3d? is #f','N','N')]}
    meta={'case_id':args.label,'density_kg_m3':rho,'reference_speed_m_s':speed,'reference_area_m2':area,'drag_direction':[1,0,0],'lift_direction':[0,1,0],
          'force_definition':'Total pressure plus viscous fluid force on all three aerofoil zones; global +x drag/+y lift; 2D depth 1 m',
          'evidence':evidence,'conversion':{'mode':'script','column_mapping':mapping}}
    metapath=out/f'force_metadata_{script_digest[:12]}.json';metapath.write_text(json.dumps(meta,indent=2),encoding='utf-8')
    coefficients=out/f'force_coefficients_{script_digest[:12]}'
    if not coefficients.exists():subprocess.run([sys.executable,str(ROOT/'data/process_forces.py'),'--forces',str(normal),'--metadata',str(metapath),'--output',str(coefficients),'--window','50'],check=True)
    residuals=[];transcript=(prov/'logs/setup.transcript').read_text(errors='replace')
    for lineno,l in enumerate(transcript.splitlines(),1):
        tok=l.split()
        if len(tok)>=10 and tok[0].isdigit() and all(re.fullmatch(r'[+-]?[\d.]+e[+-]\d+',v,re.I) for v in tok[1:8]):
            residuals.append([int(tok[0])]+[float(v) for v in tok[1:8]]+[lineno])
    if not residuals or residuals[-1][0]!=int(forces[-1][1]):raise ValueError('Residual and force iteration coverage differs')
    write_csv(out/'residuals.csv',['iteration','continuity','x_velocity','y_velocity','nut','mass_net_kg_s','lift_N','drag_N','source_transcript_line'],residuals)
    resseries=[{'name':n,'color':c,'chunks':[[(r[0],r[i]) for r in residuals]]} for i,n,c in [(1,'Continuity','#0072b2'),(2,'x velocity','#d55e00'),(3,'y velocity','#009e73'),(4,'S-A variable','#cc79a7')]]
    graph(plots/'figure3_residuals.svg',resseries,'Iteration','Scaled residual',True,1e-3)
    graph(plots/'force_history.svg',[{'name':n,'color':c,'chunks':[[(r[1],r[j]) for r in forces]]} for j,n,c in [(2,'Drag (N)','#d55e00'),(3,'Lift (N)','#0072b2')]],'Iteration','Force (N)')
    surfaces={};surface_summary={}
    for side in ['suction','pressure']:
        rows=scalar_csv(prov/'raw'/f'{side}_p_yplus.csv');rows=sorted(rows,key=lambda r:r['x-coordinate'])
        if len(rows)!=51:raise ValueError('Expected all 51 surface faces on the baseline mesh')
        surfaces[side]=rows
        surface_summary[side]={'samples':len(rows),'yplus_min':min(r['y-plus'] for r in rows),'yplus_max':max(r['y-plus'] for r in rows),'pressure_min_Pa':min(r['pressure'] for r in rows),'pressure_max_Pa':max(r['pressure'] for r in rows)}
    for value,label,name in [('pressure','Static pressure (Pa)','static_pressure'),('y-plus','Wall y+','wall_yplus')]:
        graph(plots/f'{name}.svg',[{'name':side.capitalize(),'color':c,'chunks':[[(r['x-coordinate']*1000,r[value]) for r in surfaces[side]]],'markers':True} for side,c in [('suction','#0072b2'),('pressure','#d55e00')]],'x (mm)',label)
    # Determine the actual solid interval for x=0.05 from the native baseline mesh boundary segments.
    from plot_taskA_mesh import parse_mesh
    nodes,faces,zones,counts=parse_mesh(ROOT/'solver/taskA/taskA_baseline.msh');intersections=[]
    for side in ['aerofoil_suction','aerofoil_pressure','aerofoil_te']:
        for fid in zones[side]['faces']:
            a,b=[nodes[n] for n in faces[fid][:2]]
            if min(a[0],b[0])<=.05<=max(a[0],b[0]) and a[0]!=b[0]:
                intersections.append(a[1]+(.05-a[0])/(b[0]-a[0])*(b[1]-a[1]))
    if len(intersections)!=2:raise ValueError('Cannot determine two solid intersections at mid-chord line')
    lower,upper=sorted(intersections);profiles={};profile_summary={}
    for station,x,number in [('mid',.05,7),('te',.1,8),('wake',.2,9)]:
        rows=sorted(scalar_csv(prov/'raw'/f'velocity_{station}.csv'),key=lambda r:r['y-coordinate']);profiles[station]=rows
        if max(abs(r['x-coordinate']-x) for r in rows)>1e-7:raise ValueError('Profile differs from FAQ fixed absolute x station')
        chunks=[[]]
        for r in rows:
            y=r['y-coordinate'];u=r['velocity-magnitude']
            if station=='mid' and chunks[-1] and chunks[-1][-1][0]/1000<(lower+upper)/2 and y>(lower+upper)/2:chunks.append([])
            if station=='mid' and lower+1e-7<y<upper-1e-7:raise ValueError('A plotted velocity sample falls inside actual solid mesh boundary')
            chunks[-1].append((y*1000,u))
        graph(plots/f'figure{number}_velocity_{station}.svg',[{'name':args.label,'color':'#0072b2','chunks':chunks,'markers':True}],'y (mm)','Velocity magnitude (m/s)')
        profile_summary[station]={'x_m':x,'samples':len(rows),'minimum_velocity_m_s':min(r['velocity-magnitude'] for r in rows),'maximum_velocity_m_s':max(r['velocity-magnitude'] for r in rows),'number_of_fluid_segments':len(chunks)}
    denominator=.5*rho*speed**2*area;last=forces[-1];last50=forces[-50:];inflow=rho*speed*.15*1
    summary={'case':args.case,'label':args.label,'iteration':int(last[1]),'solver_converged_flag':True,'residual_threshold':.001,
             'last_scaled_residuals':dict(zip(['continuity','x_velocity','y_velocity','nut'],residuals[-1][1:5])),
             'drag_N':last[2],'lift_N':last[3],'CD':last[2]/denominator,'CL':last[3]/denominator,
             'mass_net_kg_s':mass[-1][2],'nominal_inlet_mass_flow_kg_s':inflow,'mass_imbalance_fraction_of_uniform_inlet':abs(mass[-1][2])/inflow,
             'last50':{n:{'mean_N':statistics.mean(r[j] for r in last50),'range_N':max(r[j] for r in last50)-min(r[j] for r in last50),'range_over_final_fraction':(max(r[j] for r in last50)-min(r[j] for r in last50))/abs(last[j])} for j,n in [(2,'drag'),(3,'lift')]},
             'parameters':{'rho_kg_m3':rho,'mu_Pa_s':mu,'U_m_s':speed,'TI_fraction':ti,'chord_m':chord,'area_m2':area,'Re':rho*speed*chord/mu,'RMS_fluctuation_m_s':speed*ti,'q_Pa':denominator/area,'qS_N':denominator},
             'surface_summary':surface_summary,'profile_summary':profile_summary,'midline_solid_interval_m':[lower,upper],
             'report_value_policy':'Terminal values at actual solver auto-convergence. Last50 ranges retained to show remaining force drift. No claim of grid independence or physical validation.',
             'sources':sources,'script':{'path':str(Path(__file__).resolve()),'sha256':sha(Path(__file__))}}
    (out/'case_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
    data={'summary':summary,'forces':[{'source_line':r[0],'iteration':r[1],'drag_N':r[2],'lift_N':r[3],'mass_net_kg_s':m[2]} for r,m in zip(forces,mass)],
          'residuals':residuals,'surfaces':surfaces,'profiles':profiles}
    (out/'workbook_input.json').write_text(json.dumps(data),encoding='utf-8')
    print(json.dumps({k:summary[k] for k in ['iteration','drag_N','lift_N','CD','CL','last50','surface_summary','profile_summary','midline_solid_interval_m']},indent=2))


if __name__=='__main__':main()
