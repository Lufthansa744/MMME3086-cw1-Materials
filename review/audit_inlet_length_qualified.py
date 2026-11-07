"""Independent read-only acceptance gate bound to native terminal sources."""
from pathlib import Path
import hashlib,json,re,statistics
root=Path(__file__).resolve().parents[1]
base=root/'solver/sensitivity_ke_length_001'
text=(base/'logs/setup.transcript').read_text()
rows={};duplicates=[]
for line in text.splitlines():
    parts=line.split()
    if len(parts)>=10 and parts[0].isdigit() and all(re.fullmatch(r'[-+\d.]+e[-+]\d+',v) for v in parts[1:6]):
        n=int(parts[0]); vals=list(map(float,parts[1:6]))
        if n in rows:
            assert rows[n]==vals
            duplicates.append(n)
        rows[n]=vals
assert list(rows)==list(range(1,2501))
assert next(n for n,v in rows.items() if max(v)<=1e-3)==332
assert all(max(v)>1e-5 for v in rows.values())
raw=json.loads((root/'review/sensitivity_ke_length_001_raw_audit.json').read_text())
assert all(v['range_percent_mean']<.1 for v in raw['force_window_stats']['100'].values())
mass=[[float(v) for v in line.split()] for line in (base/'monitors/mass_balance.out').read_text().splitlines() if re.match(r'^\d+ ',line)]
assert len(mass)==2500
last=mass[-100:]
assert all(a[1]*b[1]<0 for a,b in zip(last,last[1:]))
audit={
 'case_id':'sensitivity_ke_length_001','first_default_threshold_iteration':332,'final_iteration':2500,
 'unique_residual_rows':len(rows),'identical_reprinted_iterations':duplicates,
 'residual_column_order':['continuity','x-velocity','y-velocity','k','epsilon'],
 'final_residuals':rows[2500],
 'last100_continuity_range':[min(v[0] for n,v in rows.items() if n>2400),max(v[0] for n,v in rows.items() if n>2400)],
 'last100_force_stats':raw['force_window_stats']['100'],
 'last100_mass_net_range_kg_s':[min(v[1] for v in last),max(v[1] for v in last)],
 'last100_mass_sign_alternates':True,
 'strict_residual_target_met':False,'force_stability_target_met':True,
 'native_flux_imbalance_percent':raw['mass_imbalance_percent'],
 'interpretation':'Qualified acceptance for the separate analyst-selected inlet-length sensitivity comparison. Native default 1e-3 was met at 332. The predeclared continuation cap of 2500 was reached with scaled continuity at 7.635e-5, above the analyst 1e-5 target. Stable integral forces and small global net mass flux do not establish local continuity satisfaction, spatial accuracy, physical unsteadiness, or a floating-point floor mechanism.'
}
auditpath=root/'review/sensitivity_ke_length_001_qualified_audit.json'
auditpath.write_text(json.dumps(audit,indent=2))
hashfile=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
gate={
 'case_id':'sensitivity_ke_length_001','accepted_with_limitation':True,
 'numeric_final_gate':False,'numeric_strict_gate':False,
 'reason':audit['interpretation'],
 'first_default_threshold_iteration':332,'final_iteration':2500,
 'stop_reason':'predeclared continuation cap; scaled continuity plateau above analyst strict target',
 'native_forces_sha256':hashfile(base/'monitors/forces.out'),
 'native_final_settings_sha256':hashfile(base/'settings/sensitivity_ke_length_001_final.set'),
 'review_source':str(auditpath),
 'review_source_sha256':hashfile(auditpath),
 'raw_audit_source':str(root/'review/sensitivity_ke_length_001_raw_audit.json'),
 'field_mapping_source':str(root/'review/sensitivity_ke_length_001_field_mapping_audit.json'),
 'report_requirements':['Retain first 1e-3 iteration 332 separately from final 2500*','Flag strict 1e-5 continuity target as unmet','This auxiliary run is excluded from the prescribed five-case model table']
}
(root/'review/sensitivity_ke_length_001_qualified_acceptance.json').write_text(json.dumps(gate,indent=2))
print(json.dumps(audit,indent=2))
