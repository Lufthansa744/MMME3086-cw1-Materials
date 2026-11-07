"""Build the formal five-case table exclusively from registered final datasets."""
from pathlib import Path
import hashlib
import json
import math

ROOT = Path(__file__).resolve().parent.parent

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    registry_path = ROOT/'data/dataset_registry.json'
    registry = json.loads(registry_path.read_text(encoding='utf-8-sig'))
    cases = []
    for logical, spec in registry['final_logical_cases'].items():
        folder = spec['dataset_folder']
        if logical in ('case01','case02','case03') and not folder.endswith('_aligned'):
            raise ValueError('Final baseline must use geometry-registered datasets')
        path = ROOT/'data'/folder/'case_summary.json'
        summary = json.loads(path.read_text(encoding='utf-8-sig'))
        if summary['case'] != folder or summary['logical_case_id'] != logical:
            raise ValueError(f'Logical/source dataset mismatch: {path}')
        if Path(summary['source_folder']).name != folder:
            raise ValueError(f'Solver source mismatch: {path}')
        for key in ('lift_N','drag_N','CL','CD'):
            if not math.isfinite(summary[key]):
                raise ValueError(f'Nonfinite result: {logical}/{key}')
        qS = summary['parameters']['qS_N']
        for force, coefficient in (('drag_N','CD'),('lift_N','CL')):
            if not math.isclose(summary[force]/qS,summary[coefficient],rel_tol=1e-11):
                raise ValueError(f'Coefficient normalisation mismatch: {logical}')
        if logical=='case05':
            if summary['model_iteration_count'] != summary['iteration']-summary['inherited_iteration']:
                raise ValueError('Case5 incremental/global iteration mismatch')
        solver_folder=Path(summary['source_folder'])
        evidence_files=[]
        for pattern in ('*final.cas.h5','*final.dat.h5'):
            matches=list(solver_folder.glob(pattern))
            if len(matches)!=1:
                raise ValueError(f'Expected one final restorable file: {solver_folder}/{pattern}')
            evidence_files.extend(matches)
        settings=list((solver_folder/'settings').glob('*final.set'))
        if len(settings)!=1:
            raise ValueError(f'Expected one final settings snapshot: {solver_folder}')
        evidence_files.extend(settings)
        mesh=ROOT/('solver/aligned_taskA/taskA_baseline.msh' if logical in ('case01','case02','case03') else 'inputs/Aerofoil8-degAoA-enhancedBL.msh')
        evidence_files.append(mesh)
        cases.append({'logical_case':logical,'dataset':folder,'summary':summary,
                      'summary_path':str(path.relative_to(ROOT)),'summary_sha256':sha(path),
                      'restorable_evidence':[{'path':f.relative_to(ROOT).as_posix(),'sha256':sha(f),'bytes':f.stat().st_size} for f in evidence_files]})
    if len(cases) != 5:
        raise ValueError('Exactly five formal cases are required')
    result = {'registry_sha256':sha(registry_path),'cases':cases,
              'reference':{'CL':0.81,'CD':0.017,'Re':360000,
                           'CL_graph_reading_allowance':0.02,'CD_graph_reading_allowance':0.003,
                           'source':'data/literature/brief_reference_reading.json',
                           'note':'Approximate brief-curve readings; allowances are not statistical confidence intervals'}}
    for case in cases:
        s=case['summary']
        case['approximate_reference_difference_percent']={key:100*(s[key]-result['reference'][key])/result['reference'][key] for key in ('CL','CD')}
    target=ROOT/'report/prepared'
    (target/'verified_results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    (ROOT/'coordination/final_case_index.json').write_text(json.dumps({
        'policy':'Only registered aligned/verified datasets are formal final cases; early stopping and prealignment datasets are retained separately.',
        'cases':[{k:case[k] for k in ('logical_case','dataset','summary_path','summary_sha256','restorable_evidence')} for case in cases]
    },indent=2),encoding='utf-8')
    lines=[r'\begin{tabular*}{0.88\linewidth}{@{\extracolsep{\fill}}lccccc@{}}',
           r'\toprule',r' & S--A & \caseKE & RSM & \caseKEE & \caseRSME\\\midrule']
    for label,key in [(r'Lift, \si{\newton}','lift_N'),(r'Drag, \si{\newton}','drag_N'),
                      (r'First $10^{-3}$ crossing','first_default_criterion_iteration'),
                      (r'Final stopping iteration','iteration'),('$C_D$','CD'),('$C_L$','CL')]:
        values=[]
        for case in cases:
            s=case['summary']
            if key=='first_default_criterion_iteration':
                count=s['first_default_criterion_model_iteration_count'] if case['logical_case']=='case05' else s[key]
                value='---' if count is None else str(count)
            elif key=='iteration':
                count=s['model_iteration_count'] if case['logical_case']=='case05' else s[key]
                accepted=s.get('numeric_final_acceptance_gate_passed',False)
                value=str(count) if accepted else '$'+str(count)+r'^{*}$'
            else:
                value=format(s[key],'.4g')
            values.append(value)
        lines.append(label+' & '+' & '.join(values)+r'\\')
    lines.extend([r'\bottomrule',r'\end{tabular*}'])
    (target/'verified_table.tex').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print('Integrated five registered final datasets; no LaTeX compilation performed')

if __name__=='__main__':
    main()
