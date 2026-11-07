"""Accumulate genuine completed cases without cross-mesh sample pairing."""
import csv
import hashlib
import json
from pathlib import Path
from process_case import graph

ROOT=Path(__file__).resolve().parents[1]
STYLES=[('case01','S-A','#0072b2',''),('case02','k-e','#d55e00','10 5'),('case03','RSM','#009e73','3 5'),('case04','k-e EWT','#cc79a7','12 4 3 4'),('case05','RSM EWT','#222222','18 5')]


def main():
    out=ROOT/'data/comparison';fig=out/'figures';fig.mkdir(parents=True,exist_ok=True)
    available=[];missing=[];unaccepted=[]
    registry_path=ROOT/'data/dataset_registry.json'
    registry=json.loads(registry_path.read_text()) if registry_path.exists() else {}
    for case,name,color,dash in STYLES:
        source_case=registry.get('final_logical_cases',{}).get(case,{}).get('dataset_folder',case)
        file=ROOT/'data'/source_case/'workbook_input.json'
        if not file.exists():missing.append(case);continue
        d=json.loads(file.read_text())
        if registry and not (d['summary'].get('numeric_final_acceptance_gate_passed',False) or d['summary'].get('reviewed_with_limitation',False)):
            missing.append(case);unaccepted.append({'case':case,'dataset':str(file),'reason':d['summary'].get('final_acceptance_reason','Numerical final-acceptance gates not recorded')});continue
        available.append((case,name,color,dash,d,file))
    if not available:
        status={'available_cases':[],'missing_cases':missing,'unaccepted_datasets':unaccepted,'five_case_comparison_complete':False,'dataset_registry':registry,'status':'Awaiting numerically accepted final aligned/verified datasets; no archive fallback','figures_status':'Existing earlier images are not final; no new comparison figures generated'}
        (out/'comparison_audit.json').write_text(json.dumps(status,indent=2),encoding='utf-8')
        print('Final comparison pending: no accepted active datasets yet');return
    def series(name,color,dash,chunks):return {'name':name,'color':color,'dash':dash,'chunks':chunks}
    for station,number in [('mid',7),('te',8),('wake',9)]:
        traces=[]
        for case,name,color,dash,d,file in available:
            lo,hi=d['summary']['midline_solid_interval_m'];chunks=[[]]
            for row in d['profiles'][station]:
                y=row['y-coordinate']
                if station=='mid' and chunks[-1] and chunks[-1][-1][0]/1000<(lo+hi)/2<y:chunks.append([])
                chunks[-1].append((y*1000,row['velocity-magnitude']))
            traces.append(series(name,color,dash,chunks))
        graph(fig/f'figure{number}_velocity_{station}.svg',traces,'y (mm)','Velocity (m/s)',xrange=(-75,75),layout='profile_print')
    for kind,field,ylabel,side,number in [('pressure','pressure','Static pressure (Pa)','pressure',10),('pressure','pressure','Static pressure (Pa)','suction',11),('yplus','y-plus','Wall y+','suction',12),('yplus','y-plus','Wall y+','pressure',13)]:
        traces=[series(name,color,dash,[[(r['x-coordinate']*1000,r[field]) for r in d['surfaces'][side]]]) for case,name,color,dash,d,file in available]
        graph(fig/f'figure{number}_{kind}_{side}.svg',traces,'x (mm)',ylabel,xrange=(0,100),layout='half_print')
    rows=[];details=[]
    for case,name,color,dash,d,file in available:
        s=d['summary'];profile=s['profile_summary'];surfaces=s['surface_summary']
        row={'case':case,'dataset_folder':file.parent.name,'model':name,'terminal_solver_iteration':s['iteration'],'iterations_recorded_in_this_run':s.get('iterations_recorded_in_this_run',len(d['forces'])),'stop_status':s.get('stop_status'),'drag_N':s['drag_N'],'lift_N':s['lift_N'],'CD':s['CD'],'CL':s['CL'],
             'first_default_criterion_iteration':s.get('first_default_criterion_iteration'),'first_default_criterion_model_iteration_count':s.get('first_default_criterion_model_iteration_count'),'model_iteration_count':s.get('model_iteration_count'),'inherited_iteration':s.get('inherited_iteration'),
             'drag_last100_range_over_mean_fraction':s['stability_windows']['100']['forces']['drag']['range_over_mean_fraction'],'lift_last100_range_over_mean_fraction':s['stability_windows']['100']['forces']['lift']['range_over_mean_fraction'],
             'numeric_final_acceptance_gate_passed':s.get('numeric_final_acceptance_gate_passed',False),'reviewed_with_limitation':s.get('reviewed_with_limitation',False),'acceptance_category':s.get('acceptance_category'),
             'mass_net_kg_s':s['mass_net_kg_s'],'mass_imbalance_fraction':s['mass_imbalance_fraction_of_uniform_inlet'],
             'drag_last50_range_fraction':s['last50']['drag']['range_over_final_fraction'],'lift_last50_range_fraction':s['last50']['lift']['range_over_final_fraction'],
             'midline_peak_speed_m_s':profile['mid']['maximum_velocity_m_s'],'TE_core_min_speed_m_s':profile['te'].get('wake_core_minimum_m_s'),'wake_core_min_speed_m_s':profile['wake'].get('wake_core_minimum_m_s'),
             'wake_deficit_from_inlet_m_s':profile['wake'].get('deficit_relative_to_inlet_m_s'),
             'suction_yplus_min':surfaces['suction']['yplus_min'],'suction_yplus_max':surfaces['suction']['yplus_max'],'pressure_yplus_min':surfaces['pressure']['yplus_min'],'pressure_yplus_max':surfaces['pressure']['yplus_max']}
        coverage_path=file.parent/'wall_length_coverage.json';coverage=json.loads(coverage_path.read_text()) if coverage_path.exists() else None
        for side in ['suction','pressure']:
            minimum=min(d['surfaces'][side],key=lambda r:r['pressure']);maximum=max(d['surfaces'][side],key=lambda r:r['pressure'])
            row[f'{side}_min_pressure_Pa']=minimum['pressure'];row[f'{side}_min_pressure_x_mm']=minimum['x-coordinate']*1000
            row[f'{side}_max_pressure_Pa']=maximum['pressure'];row[f'{side}_max_pressure_x_mm']=maximum['x-coordinate']*1000
            for group in ['at_most_1','above_1_to_5','above_5','below_30','from_30_to_300','above_300']:
                row[f'{side}_length_fraction_yplus_{group}']=coverage['sides'][side]['length_fractions'][group] if coverage else None
        if 'brief_reference_comparison' in s:
            for coeff in ['CL','CD']:row[f'{coeff}_relative_difference_from_brief']=s['brief_reference_comparison'][coeff]['signed_relative_difference_fraction']
        rows.append(row);details.append({'case':case,'dataset':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'summary':s,
                                        'wall_length_coverage_evidence':{'path':str(coverage_path),'sha256':hashlib.sha256(coverage_path.read_bytes()).hexdigest()} if coverage else None})
    with (out/'case_comparison.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    manifest={'available_cases':[r[0] for r in available],'missing_cases':missing,'unaccepted_datasets':unaccepted,'five_case_comparison_complete':not missing,'dataset_registry':registry,
              'generator_sources':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in [Path(__file__),ROOT/'data/process_case.py']],
              'all_strict_numerical_gates_passed':all(d['summary'].get('numeric_final_acceptance_gate_passed',False) for case,name,color,dash,d,file in available),
              'qualified_cases':[case for case,name,color,dash,d,file in available if d['summary'].get('reviewed_with_limitation',False)],
              'case_order':[x[0] for x in STYLES],'plot_styles':[{'case':case,'label':name,'color':color,'dash':dash} for case,name,color,dash in STYLES],
              'coordinate_policy':'Plot each native sample at its own exported coordinate. No direct sample-index pairing across meshes and no cross-case interpolation. Two midline fluid intervals kept separate for each case.',
              'wake_metric_definition':'Minimum exported velocity within analyst-defined y=[-40,+20] mm at x=0.10/0.20 m, excluding duct walls. Deficits use actual inlet U and separately the nearest native samples to each window boundary; no interpolation. Core-adjacent native y spacing and global peak locations retained per case. This is a sampled core metric, not a resolved exact minimum.',
              'wall_metric_policy':'y+ counts/ranges are evidence for the actual wall treatment; model complexity and small residuals do not establish experimental accuracy.',
              'datasets':details,'figures':[{'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in sorted(fig.glob('*.svg'))]}
    (out/'comparison_audit.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('Comparison updated from actual datasets: '+', '.join(manifest['available_cases']))


if __name__=='__main__':main()
