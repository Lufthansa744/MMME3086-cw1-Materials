"""Calculate B0 from preserved actual Fluent settings, without default properties."""
import hashlib
import json
from pathlib import Path
import re

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/case01'
SOURCE=ROOT/'solver/case01/settings/case01_setup.set'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    provenance=OUT/'provenance';provenance.mkdir(exist_ok=True)
    snapshot=provenance/'case01_setup_source.set'
    content=SOURCE.read_bytes()
    if snapshot.exists() and snapshot.read_bytes()!=content:
        raise ValueError('Saved setup changed; use a new evidence version instead of overwriting the snapshot')
    if not snapshot.exists():snapshot.write_bytes(content)
    text=snapshot.read_text(encoding='utf-8')
    lines=text.splitlines()
    material=[(i+1,l) for i,l in enumerate(lines) if l.startswith('(materials ((air fluid ')]
    if len(material)!=1:raise ValueError('Expected one actual air material definition')
    air=material[0][1]
    inlet=re.search(r'\(bc \(inlet velocity-inlet mixture\) \(\n(.*?)\n\)\)',text,re.S)
    if not inlet:raise ValueError('Actual inlet block missing')
    inlet_text=inlet.group(0)
    def number(pattern,source):
        match=re.search(pattern,source)
        if not match:raise ValueError('Required setting is missing: '+pattern)
        return float(match.group(1))
    rho=number(r'\(density \(constant \. ([\d.eE+-]+)\)',air)
    mu=number(r'\(viscosity \(constant \. ([\d.eE+-]+)\)',air)
    velocity=number(r'\(vmag \(constant \. ([\d.eE+-]+)\)',inlet_text)
    intensity=number(r'\(turb-intensity \. ([\d.eE+-]+)\)',inlet_text)
    lengthscale=number(r'\(turb-length-scale \. ([\d.eE+-]+)\)',inlet_text)
    if '(ke-spec . 1)' not in inlet_text:raise ValueError('Intensity/length-scale inlet choice not found')
    chord=number(r'\(reference-length ([\d.eE+-]+)\)',text)
    area=number(r'\(reference-area ([\d.eE+-]+)\)',text)
    if min(rho,mu,velocity,chord,area)<=0:raise ValueError('Invalid positive input')
    if abs(velocity-50.9)>1e-9:raise ValueError('Actual inlet differs from authorised velocity')
    geometry=json.loads((ROOT/'data/taskA/geometry_check_audit.json').read_text())
    if abs(chord-geometry['chord_m'])>1e-10:raise ValueError('Fluent reference chord differs from actual CAD chord')
    def locator(pattern):return [{'line_one_based':i+1,'exact_line':l} for i,l in enumerate(lines) if pattern(l)]
    evidence={'material_definition':{'line_one_based':material[0][0],'exact_line':air},
              'inlet_block':{'line_one_based':text[:inlet.start()].count('\n')+1,'exact_text':inlet_text},
              'reference_length_and_area':locator(lambda l:l.startswith('(reference-length ') or l.startswith('(reference-area '))}
    values={'density_kg_m3':rho,'dynamic_viscosity_Pa_s':mu,'inlet_speed_m_s':velocity,'inlet_turbulence_intensity_fraction':intensity,
            'inlet_turbulence_intensity_percent':intensity*100,'inlet_turbulent_length_scale_m':lengthscale,'chord_m':chord,'reference_area_m2':area,
            'Reynolds_number':rho*velocity*chord/mu,'isotropic_component_RMS_fluctuation_m_s':velocity*intensity,
            'dynamic_pressure_Pa':.5*rho*velocity**2,'force_normalisation_N':.5*rho*velocity**2*area}
    report={'case':'Case1 setup; no solution values used','settings_source':{'path':str(SOURCE),'sha256':sha(SOURCE)},
            'preserved_snapshot':{'path':str(snapshot),'sha256':sha(snapshot)},'script':{'path':str(Path(__file__).resolve()),'sha256':sha(Path(__file__))},
            'geometry_check':{'path':str(ROOT/'data/taskA/geometry_check_audit.json'),'sha256':sha(ROOT/'data/taskA/geometry_check_audit.json')},
            'actual_values_and_calculations':values,'evidence':evidence,
            'equations':{'Re':'rho*U*c/mu','isotropic_component_RMS':'U*(TI_percent/100)','dynamic_pressure':'0.5*rho*U**2','force_normalisation':'dynamic_pressure*reference_area'},
            'interpretation':'Intensity+length scale is actually selected in saved inlet ke-spec=1 and independently visible in setup transcript. Fluctuation is isotropic per-component RMS, not magnitude RMS. Values are read from actual saved setup; no TI is inferred from viscosity ratio.'}
    (OUT/'b0_actual_settings_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    p=OUT/'b0_values.csv'
    p.write_text('quantity,value\n'+'\n'.join(f'{k},{v:.15g}' for k,v in values.items())+'\n',encoding='utf-8')
    print(json.dumps(values,indent=2))


if __name__=='__main__':main()
