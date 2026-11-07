"""Prepare a checked source ZIP for Overleaf, without compiling LaTeX locally."""
from pathlib import Path
import hashlib
import json
import re
import shutil
import zipfile

ROOT=Path(__file__).resolve().parent.parent
PREPARED=ROOT/'report/prepared'
EXPECTED_SECTIONS=['Task A Geometry [16]','Task B Solution and data extraction [34]',
                   'Task C Analysis [50]','Task C Boundary Conditions and Results']
ASSETS={
 'fig01_geometry.png':'data/taskA/figure1_native_compact.png',
 'fig02_mesh_bc.png':'data/taskA/figure2_mesh_compact.png',
 'fig03_sa_convergence.pdf':'data/print_assets/fig03_sa_convergence.pdf',
 'fig04_rsm_vectors.pdf':'data/print_assets/fig04_rsm_vectors.pdf',
 'fig05_rsm_yplus.pdf':'data/print_assets/fig05_rsm_yplus.pdf',
 'fig06_enhanced_combined.pdf':'data/print_assets/fig06_enhanced_combined.pdf',
 'fig07_velocity_midchord.pdf':'data/print_assets/fig07_velocity_midchord.pdf',
 'fig08_velocity_trailingedge.pdf':'data/print_assets/fig08_velocity_trailingedge.pdf',
 'fig09_velocity_downstream.pdf':'data/print_assets/fig09_velocity_downstream.pdf',
 'fig10_pressure_pressure.pdf':'data/print_assets/fig10_pressure_pressure.pdf',
 'fig11_pressure_suction.pdf':'data/print_assets/fig11_pressure_suction.pdf',
 'fig12_yplus_suction.pdf':'data/print_assets/fig12_yplus_suction.pdf',
 'fig13_yplus_pressure.pdf':'data/print_assets/fig13_yplus_pressure.pdf'}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    source=(PREPARED/'main.tex').read_text(encoding='utf-8')
    content=re.sub(r'(?<!\\)%[^\n]*','',source)
    if re.findall(r'\\section\{([^}]+)\}',content)!=EXPECTED_SECTIONS:
        raise ValueError('Required section headings changed')
    if re.search(r'\\(?:Fill|NA)\b',content):
        raise ValueError('Unresolved evidence macros remain; finish integration first')
    if re.search(r'working\s+draft|\bTODO\b',content,re.I):
        raise ValueError('Non-submission language remains')
    if len(re.findall(r'\\begin\{figure\}',content))+len(re.findall(r'\\captionof\{figure\}',content))!=13:
        raise ValueError('Figure numbering must cover Figures 1 to 13')
    references=re.findall(r'\\evidence\{[^}]+\}\{([^}]+)\}',content)
    if len(references)!=13 or set(references)!=set(ASSETS):
        raise ValueError('Report image references do not match the final thirteen assets')
    for body in re.findall(r'\\begin\{equation\}(.*?)\\end\{equation\}',content,re.S):
        body=re.sub(r'\\label\{[^}]*\}|\\end\{(?:aligned|gathered)\}','',body).rstrip()
        if body.endswith(tuple(',.;:')):
            raise ValueError('Displayed equation has terminal punctuation')
    results=json.loads((PREPARED/'verified_results.json').read_text(encoding='utf-8'))
    if len(results['cases'])!=5:
        raise ValueError('Five registered result summaries are required')
    registry=json.loads((ROOT/'data/dataset_registry.json').read_text(encoding='utf-8'))
    for case in results['cases']:
        if case['dataset']!=registry['final_logical_cases'][case['logical_case']]['dataset_folder']:
            raise ValueError('Results do not match current registered final datasets')
        if sha(ROOT/case['summary_path'])!=case['summary_sha256']:
            raise ValueError('Result summary changed after integration')
    comparison=json.loads((ROOT/'data/comparison/comparison_audit.json').read_text(encoding='utf-8'))
    if not comparison['five_case_comparison_complete'] or comparison['missing_cases']:
        raise ValueError('The comparison figures do not yet contain five accepted formal datasets')
    if comparison['dataset_registry']['final_logical_cases']!=registry['final_logical_cases']:
        raise ValueError('Comparison figures use a different dataset registry')
    missing=[name for name,path in ASSETS.items() if not (ROOT/path).is_file()]
    if missing:
        raise ValueError(f'Missing final source graphics: {missing}')
    manifest=[]
    for name,path in ASSETS.items():
        original=ROOT/path
        shutil.copy2(original,PREPARED/name)
        manifest.append({'report_asset':name,'original':path,'sha256':sha(original)})
    for name in ('new-aiaa.cls','new-aiaa.bst'):
        shutil.copy2(ROOT/'report/overleaf_original/source'/name,PREPARED/name)
    (PREPARED/'asset_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    required={'main.tex','verified_table.tex','AI_prompt_record.txt','new-aiaa.cls','new-aiaa.bst',
              'verified_results.json','asset_manifest.json',*ASSETS.keys()}
    for name in required:
        if not (PREPARED/name).is_file():
            raise ValueError(f'Missing source package file: {name}')
    archive=ROOT/'report/LIU_Yang_20617209_CFD_Overleaf_Source.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as out:
        for name in sorted(required):
            out.write(PREPARED/name,name)
    (ROOT/'report/source_package_status.json').write_text(json.dumps({
        'archive':archive.name,'sha256':sha(archive),'source_preflight_passed':True,
        'latex_compiled':False,'final_page_layout_verified':False,
        'remaining_action':'Upload and compile only in the approved Overleaf project; visually verify every final page.'},indent=2),encoding='utf-8')
    print(f'Checked source package prepared: {archive}; not compiled')

if __name__=='__main__':
    main()
