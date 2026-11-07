"""Inspect saved XLSX formula caches against independent native-data summaries."""
import argparse
import hashlib
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]
NS={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
ERRORS={'#REF!','#DIV/0!','#VALUE!','#NAME?','#N/A','#NUM!','#NULL!','#SPILL!','#CALC!'}

def verify(case):
    summary=ROOT/'data'/case/'case_summary.json';s=json.loads(summary.read_text())
    file=ROOT/'outputs/01a1b755-05b7-7841-9420-c1bed337cfa6'/f'{case}_data.xlsx'
    with zipfile.ZipFile(file) as z:
        strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            strings=[''.join(el.itertext()) for el in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('x:si',NS)]
        names=[e.attrib['name'] for e in ET.fromstring(z.read('xl/workbook.xml')).findall('x:sheets/x:sheet',NS)]
        if names!=['Summary','Monitors','Surfaces','Profiles','Residuals','Acceptance']:raise ValueError(f'{case}: missing expected sheet')
        allcells=[];sheets=[]
        for i in range(1,len(names)+1):
            cells={}
            for el in ET.fromstring(z.read(f'xl/worksheets/sheet{i}.xml')).findall('.//x:c',NS):
                value=el.find('x:v',NS);val=None if value is None else value.text
                if el.attrib.get('t')=='s':val=strings[int(val)]
                elif el.attrib.get('t')=='inlineStr':val=''.join(el.find('x:is',NS).itertext())
                if el.attrib.get('t')=='e' or val in ERRORS:raise ValueError(f'{case}: saved cell error {el.attrib["r"]}: {val}')
                cells[el.attrib['r']]={'value':val,'formula':el.find('x:f',NS) is not None}
            sheets.append(cells);allcells.extend(cells.values())
        checks={'B11':s['parameters']['Re'],'B12':s['parameters']['RMS_fluctuation_m_s'],'B14':s['parameters']['qS_N'],
                'B18':s['iteration'],'B19':s['drag_N'],'B20':s['lift_N'],'B21':s['CD'],'B22':s['CL'],
                'B28':s['first_default_criterion_iteration'],'B29':s['first_default_criterion_model_iteration_count'],'B30':s['model_iteration_count'],
                'B31':s['stability_windows']['100']['forces']['drag']['range_over_mean_fraction'],
                'B32':s['stability_windows']['100']['forces']['lift']['range_over_mean_fraction']}
        for cell,expected in checks.items():
            if expected is None:continue
            if not math.isclose(float(sheets[0][cell]['value']),expected,rel_tol=1e-11,abs_tol=1e-12):raise ValueError(f'{case}: cached {cell} mismatch')
        if sheets[5]['B5']['value']!=('Met' if s['numeric_final_acceptance_gate_passed'] else 'Not met'):raise ValueError('Acceptance gate cache mismatch')
        if sheets[5]['B6']['value']!=('Yes' if s.get('reviewed_with_limitation') else 'No'):raise ValueError('Qualified acceptance cache mismatch')
        monitor_rows=sum(1 for k in sheets[1] if k.startswith('A') and k[1:].isdigit() and int(k[1:])>=6)
        if monitor_rows!=s['iterations_recorded_in_this_run']:raise ValueError('Saved monitor count mismatch')
    result={'case':case,'xlsx':str(file),'sha256':hashlib.sha256(file.read_bytes()).hexdigest(),'summary_sha256':hashlib.sha256(summary.read_bytes()).hexdigest(),
            'sheet_names':names,'formula_count':sum(c['formula'] for c in allcells),'monitor_rows':monitor_rows,'verified_summary_cells':checks,
            'formula_error_count':0,'acceptance_and_qualified_flags_match':True,'scope':'Saved XLSX ZIP/XML and formula caches checked independently against source-derived summary; no claim of testing in a native Excel UI.'}
    (ROOT/'data'/case/'workbook_saved_file_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(f'{case}: saved XLSX passed, {monitor_rows} monitor rows, {result["formula_count"]} formulas')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('cases',nargs='+');a=p.parse_args()
    for c in a.cases:verify(c)
