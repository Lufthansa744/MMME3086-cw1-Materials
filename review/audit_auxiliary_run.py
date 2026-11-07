"""Review native iterative criteria and model controls for an auxiliary run."""
from pathlib import Path
import json,re,sys,hashlib
root=Path(__file__).resolve().parents[1];run=sys.argv[1];base=root/'solver'/run
m=json.loads((base/'manifest.json').read_text(encoding='utf-8-sig'))
native=(base/'logs/setup.transcript').read_text()
active=list(m['residual_criteria']);nres=len(active);rows={};duplicates=[]
for line in native.splitlines():
    parts=line.split()
    if len(parts)>nres+2 and parts[0].isdigit() and all(re.fullmatch(r'[-+\d.]+e[-+]\d+',v) for v in parts[1:nres+1]):
        n=int(parts[0]);v=list(map(float,parts[1:nres+1]))
        if n in rows:assert rows[n]==v;duplicates.append(n)
        rows[n]=v
terminal=max(rows);assert list(rows)==list(range(1,terminal+1))
last=rows[terminal];thresholds=list(m['residual_criteria'].values())
strict=all(v<=thresholds[j] for j,v in enumerate(last))
raw=json.loads((root/'review'/f'{run}_raw_audit.json').read_text(encoding='utf-8'))
forcegate=all(v['range_percent_mean']<=.1 for v in raw['force_window_stats']['100'].values())
settings=Path(m['actual_settings_source']).read_text()
actualcontrols={}
for key,value in m['actual_rp_readbacks'].items():
    found=re.search(r'^\('+re.escape(key)+r' \. ([^()]+)\)',settings,re.M)
    if found:
        actual=float(found.group(1));source='explicit final set'
    else:
        found=re.search(r'ACTUAL_RP '+re.escape(key)+r' = ([-+\d.eE]+)',native)
        assert found,key
        actual=float(found.group(1));source='actual native rpgetvar readback; default omitted from set'
    assert actual==float(value),(key,actual,value)
    actualcontrols[key]={'value':actual,'source':source}
assert m['air']=={'density_kg_m3':1.225,'dynamic_viscosity_Pa_s':1.7894e-5}
assert m['inlet']['speed_m_s']==50.9 and m['inlet']['intensity_fraction']==.05
result={'run':run,'final_iteration':terminal,'native_rows':len(rows),'duplicate_reprints':duplicates,
 'native_first_default_1e3':next((n for n,v in rows.items() if max(v)<=1e-3),None),
 'active_equations':active,'final_residuals':last,'strict_residual_gate':strict,'force_gate':forcegate,
 'combined_gate':strict and forcegate,'controls_verified_against_native_evidence':actualcontrols,
 'inlet_manifest':m['inlet'],'CL':raw['CL_final'],'CD':raw['CD_final'],
 'force_window_100':raw['force_window_stats']['100'],'mass_imbalance_percent':raw['mass_imbalance_percent'],
 'native_transcript_sha256':hashlib.sha256((base/'logs/setup.transcript').read_bytes()).hexdigest(),
 'final_settings_sha256':hashlib.sha256(Path(m['actual_settings_source']).read_bytes()).hexdigest()}
(root/'review'/f'{run}_numerical_audit.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
