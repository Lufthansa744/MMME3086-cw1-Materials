"""Inventory the final formal data artifacts without changing any solver file."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def evidence(path):
    p=ROOT/path
    if not p.is_file():raise FileNotFoundError(p)
    return {'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size}

def main():
    registry=json.loads((ROOT/'data/dataset_registry.json').read_text());cases=[]
    for logical,entry in registry['final_logical_cases'].items():
        folder=entry['dataset_folder'];base=Path('data')/folder
        s=json.loads((ROOT/base/'case_summary.json').read_text())
        if not (s['numeric_final_acceptance_gate_passed'] or s.get('reviewed_with_limitation')):raise ValueError(f'{logical}: not accepted')
        book=Path('outputs/01a1b755-05b7-7841-9420-c1bed337cfa6')/f'{folder}_data.xlsx'
        audit=json.loads((ROOT/base/'workbook_saved_file_audit.json').read_text())
        if evidence(book)['sha256']!=audit['sha256'] or evidence(base/'case_summary.json')['sha256']!=audit['summary_sha256']:raise ValueError('Workbook verification is stale')
        cases.append({'logical_case':logical,'physical_dataset':folder,'numeric_strict_gate':s['numeric_final_acceptance_gate_passed'],'reviewed_with_limitation':s.get('reviewed_with_limitation',False),
                      'global_final_iteration':s['iteration'],'model_iteration_count':s['model_iteration_count'],
                      'artifacts':[evidence(p) for p in [base/'case_summary.json',base/'workbook_input.json',base/'wall_length_coverage.json',base/'workbook_saved_file_audit.json',book]]})
    figures={1:'data/taskA/figure1_native_compact.png',2:'data/taskA/figure2_mesh_compact.png',3:'data/case01_aligned/figures/figure3_residuals_compact.png',
             4:'data/case03_aligned/figures/figure4_velocity_vectors.png',5:'data/case03_aligned/figures/figure5_wall_cell_yplus.png',6:'data/case05_verified/figures/figure6_combined_compact.png'}
    for number,name in [(7,'velocity_mid'),(8,'velocity_te'),(9,'velocity_wake'),(10,'pressure_pressure'),(11,'pressure_suction'),(12,'yplus_suction'),(13,'yplus_pressure')]:figures[number]=f'data/comparison/figures/figure{number}_{name}.png'
    auxiliary=[]
    for folder in ['sa_grid_medium','sa_grid_fine','sensitivity_ke_length_001']:
        base=Path('data')/folder;audit_path=ROOT/base/'workbook_saved_file_audit.json'
        if not audit_path.exists():continue
        book=Path('outputs/01a1b755-05b7-7841-9420-c1bed337cfa6')/f'{folder}_data.xlsx';audit=json.loads(audit_path.read_text())
        if evidence(book)['sha256']!=audit['sha256'] or evidence(base/'case_summary.json')['sha256']!=audit['summary_sha256']:raise ValueError('Auxiliary workbook verification is stale')
        auxiliary.append({'physical_dataset':folder,'excluded_from_formal_five_cases':True,'artifacts':[evidence(p) for p in [base/'case_summary.json',base/'workbook_saved_file_audit.json',book]]})
    result={'scope':'Formal five-case and separate auxiliary data delivery; report integration, Overleaf compilation and submission are owned by the main agent.',
            'registry':evidence('data/dataset_registry.json'),'cases':cases,'report_figure_candidates':{str(k):evidence(v) for k,v in figures.items()},
            'comparison':[evidence(p) for p in ['data/comparison/case_comparison.csv','data/comparison/comparison_audit.json']],
            'auxiliary_datasets':auxiliary,'auxiliary_analysis':[evidence(p) for p in ['data/auxiliary/grid_comparison.csv','data/auxiliary/auxiliary_comparison.json','data/comparison/enhanced_rsm_diagnostic_comparison.json'] if (ROOT/p).exists()],
            'limitations':['Cases 2 and 3 meet the original 1e-3 residual target and force-stability check but not the additional 1e-5 continuity target; both have independent qualified acceptance bound to native hashes.',
                           'Raw data and archived prealignment/early-stop datasets remain preserved. No archived fields enter the final five-case comparison.',
                           'Saved XLSX formulas/caches and rendered previews were checked with the bundled spreadsheet engine and ZIP/XML inspection; no native Excel UI test is claimed.',
                           'Graph reading allowances are manual resolution allowances, not statistical confidence intervals. Convergence and model complexity do not establish experimental accuracy.']}
    target=ROOT/'data/final_data_manifest.json';target.write_text(json.dumps(result,indent=2),encoding='utf-8');print(f'Inventoried 5 formal datasets, {5+len(auxiliary)} verified workbooks and {len(figures)} report figure candidates')

if __name__=='__main__':main()
