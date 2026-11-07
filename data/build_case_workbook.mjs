import fs from 'node:fs/promises';
import path from 'node:path';
import {Workbook, SpreadsheetFile} from '@oai/artifact-tool';

const caseId=process.argv[2]??'case01';
const root=process.cwd();
const folder=path.join(root,'data',caseId);
const data=JSON.parse(await fs.readFile(path.join(folder,'workbook_input.json'),'utf8'));
const s=data.summary,p=s.parameters;
const wb=Workbook.create();
const sheets={};
for(const name of ['Summary','Monitors','Surfaces','Profiles','Residuals','Acceptance']){
  const sheet=wb.worksheets.add(name);sheet.showGridLines=false;sheets[name]=sheet;
}
function style(sheet,address){
  const r=sheet.getRange(address);r.format.font={name:'Arial',size:10,color:'#222222'};
  r.format.rowHeight=20;r.format.verticalAlignment='center';
}
function header(sheet,address){sheet.getRange(address).format={fill:'#263746',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},rowHeight:25,horizontalAlignment:'center',verticalAlignment:'center'};}
function title(sheet,title){sheet.getRange('A2').values=[[sheet.name==='Summary'?title:s.label]];sheet.getRange('A2').format.font={name:'Arial',size:14,bold:true,color:'#222222'};sheet.getRange('A2:G2').format.rowHeight=28;}
function inputSource(sheet,sourceNames){
  const selected=s.sources.filter(x=>sourceNames.some(n=>x.original.endsWith(n)));
  sheet.getRange('I2:K2').values=[['Native source','SHA256','Scope']];header(sheet,'I2:K2');
  selected.forEach((v,i)=>{sheet.getRange(`I${i+3}:K${i+3}`).values=[[path.relative(root,v.preserved),v.sha256,v.scope??'Complete native file']];});
  style(sheet,`I3:K${Math.max(3,selected.length+2)}`);sheet.getRange('I:I').format.columnWidth=62;sheet.getRange('J:J').format.columnWidth=70;sheet.getRange('K:K').format.columnWidth=70;
}
const sum=sheets.Summary;
sum.tabColor='#263746';style(sum,'A1:D37');sum.getRange('A:A').format.columnWidth=48;sum.getRange('B:B').format.columnWidth=20;sum.getRange('C:C').format.columnWidth=21;sum.getRange('D:D').format.columnWidth=3;
title(sum,`${s.label} results and normalisation`);
sum.getRange('A4:C14').values=[['Parameter','Value','Unit'],['Air density',p.rho_kg_m3,'kg/m³'],['Dynamic viscosity',p.mu_Pa_s,'Pa s'],['Inlet speed',p.U_m_s,'m/s'],['Inlet turbulence intensity',p.TI_fraction,'fraction'],['Chord',p.chord_m,'m'],['Reference planform area',p.area_m2,'m²'],['Chord Reynolds number',null,'dimensionless'],['Isotropic component RMS fluctuation',null,'m/s'],['Dynamic pressure',null,'Pa'],['Force normalisation qS',null,'N']];
header(sum,'A4:C4');sum.getRange('B11:B14').formulas=[['=B5*B7*B9/B6'],['=B7*B8'],['=0.5*B5*B7^2'],['=B13*B10']];
sum.getRange('B5:B14').setNumberFormat('0.000000');sum.getRange('B6').setNumberFormat('0.0000E+00');sum.getRange('B8').setNumberFormat('0.0%');sum.getRange('B11').setNumberFormat('0.000E+00');
sum.getRange('C8').values=[['dimensionless']];
const n=data.forces.length,last=n+5,lastRes=data.residuals.length+5;
sum.getRange('A17:C26').values=[['Result','Value','Unit'],['Iterations',null,'iterations'],['Total drag',null,'N'],['Total lift',null,'N'],['Drag coefficient CD',null,'dimensionless'],['Lift coefficient CL',null,'dimensionless'],['Net inlet/outlet mass imbalance',null,'kg/s'],['Fluent convergence flag',s.solver_converged_flag?'Converged':'Not converged','actual saved setting'],['Scaled residual criterion',s.residual_threshold,'all solved equations'],['Final continuity residual',null,'scaled']];header(sum,'A17:C17');
sum.getRange('B18:B23').formulas=[[`='Monitors'!A${last}`],[`='Monitors'!B${last}`],[`='Monitors'!C${last}`],['=B19/B14'],['=B20/B14'],[`='Monitors'!D${last}`]];
sum.getRange('B26').formulas=[[`='Residuals'!B${lastRes}`]];sum.getRange('B18:B23').setNumberFormat('0.000000');sum.getRange('B18').setNumberFormat('0');sum.getRange('B23').setNumberFormat('0.000000E+00');sum.getRange('B26').setNumberFormat('0.0000E+00');
sum.getRange('A18').values=[['Terminal solver iteration']];sum.getRange('A27:C27').values=[['Updates recorded in this run',s.iterations_recorded_in_this_run??n,'iterations']];
sum.getRange('A28:C33').values=[['First 1e-3 crossing (global)',s.first_default_criterion_iteration??null,'solver iteration'],['First 1e-3 crossing (model count)',s.first_default_criterion_model_iteration_count??null,'model iterations'],['Final model iteration count',s.model_iteration_count??s.iteration,'model iterations'],['Last 100 drag range / |mean|',null,'dimensionless'],['Last 100 lift range / |mean|',null,'dimensionless'],['Recorded numerical acceptance gate',s.numeric_final_acceptance_gate_passed?'Met':'Not met','strict residual + force gates']];
sum.getRange('B31:B32').formulas=[[`=(MAX('Monitors'!B${Math.max(6,last-99)}:B${last})-MIN('Monitors'!B${Math.max(6,last-99)}:B${last}))/ABS(AVERAGE('Monitors'!B${Math.max(6,last-99)}:B${last}))`],[`=(MAX('Monitors'!C${Math.max(6,last-99)}:C${last})-MIN('Monitors'!C${Math.max(6,last-99)}:C${last}))/ABS(AVERAGE('Monitors'!C${Math.max(6,last-99)}:C${last}))`]];sum.getRange('B31:B32').setNumberFormat('0.0000%');
sum.getRange('A35').values=[['Terminal force values at the recorded final stopping point.']];sum.getRange('A36').values=[['Full residual/force stability and source evidence in case audit.']];sum.getRange('A35:C36').format.font={name:'Arial',size:10,italic:true,color:'#555555'};
const acceptance=sheets.Acceptance;title(acceptance,`${s.label} numerical acceptance and limitations`);style(acceptance,'A4:B12');acceptance.getRange('A:A').format.columnWidth=45;acceptance.getRange('B:B').format.columnWidth=100;
acceptance.getRange('A4:B12').values=[['Check','Recorded result'],['Strict numerical acceptance gate',s.numeric_final_acceptance_gate_passed?'Met':'Not met'],['Accepted with independent limitation',s.reviewed_with_limitation?'Yes':'No'],['Acceptance category',s.acceptance_category??'Recorded separately'],['Reason',s.final_acceptance_reason],['Independent review status',s.independent_review_status],['Review record',s.qualified_acceptance_evidence?.path??'See independent review audit'],['Review record SHA256',s.qualified_acceptance_evidence?.sha256??'Not a qualified-acceptance record'],['Actual terminal residuals',JSON.stringify(s.last_scaled_residuals)]];header(acceptance,'A4:B4');acceptance.getRange('B5:B12').format.wrapText=true;acceptance.getRange('A8:B9').format.rowHeight=60;acceptance.getRange('A10:B12').format.rowHeight=42;
const mon=sheets.Monitors;title(mon,`${s.label} native force and mass monitors`);style(mon,`A5:G${last}`);mon.getRange('A5:G5').values=[['Iteration','Drag (N)','Lift (N)','Net mass (kg/s)','CD','CL','Native force line']];header(mon,'A5:G5');
mon.getRange(`A6:G${last}`).values=data.forces.map(r=>[r.iteration,r.drag_N,r.lift_N,r.mass_net_kg_s,null,null,r.source_line]);
mon.getRange(`E6:F${last}`).formulas=data.forces.map((r,i)=>[`=B${i+6}/'Summary'!$B$14`,`=C${i+6}/'Summary'!$B$14`]);
mon.getRange(`B6:F${last}`).setNumberFormat('0.000000');mon.getRange(`D6:D${last}`).setNumberFormat('0.000000E+00');mon.getRange('A:G').format.columnWidth=19;mon.freezePanes.freezeRows(5);inputSource(mon,['forces.out','mass_balance.out',`${caseId}_final.set`]);
const surf=sheets.Surfaces;title(surf,`${s.label} native cell-centred aerofoil data`);const surfaceRows=Object.entries(data.surfaces).flatMap(([side,rows])=>rows.map(r=>[side,r.cellnumber,r['cell-id']??null,r['x-coordinate'],r['y-coordinate'],r['pressure'],r['y-plus']]));
style(surf,`A5:G${surfaceRows.length+5}`);surf.getRange('A5:G5').values=[['Side','Native cell number','Fluent cell ID','x (m)','y (m)','Static pressure (Pa)','Wall y+']];header(surf,'A5:G5');surf.getRange(`A6:G${surfaceRows.length+5}`).values=surfaceRows;surf.getRange('A:G').format.columnWidth=22;surf.getRange(`D6:G${surfaceRows.length+5}`).setNumberFormat('0.000000');surf.freezePanes.freezeRows(5);inputSource(surf,['suction_p_yplus.csv','pressure_p_yplus.csv']);
const pro=sheets.Profiles;title(pro,`${s.label} native nodal line velocity data`);const [lower,upper]=s.midline_solid_interval_m;
const profileRows=Object.entries(data.profiles).flatMap(([station,rows])=>rows.map(r=>[station,r.nodenumber,r['x-coordinate'],r['y-coordinate'],r['velocity-magnitude'],station==='mid'?(r['y-coordinate']<(lower+upper)/2?'lower fluid':'upper fluid'):'continuous fluid']));
style(pro,`A5:F${profileRows.length+5}`);pro.getRange('A5:F5').values=[['Fixed x station','Native node number','x (m)','y (m)','Velocity (m/s)','Fluid segment']];header(pro,'A5:F5');pro.getRange(`A6:F${profileRows.length+5}`).values=profileRows;pro.getRange('A:F').format.columnWidth=22;pro.getRange(`C6:E${profileRows.length+5}`).setNumberFormat('0.000000');pro.freezePanes.freezeRows(5);inputSource(pro,['velocity_mid.csv','velocity_te.csv','velocity_wake.csv']);
const colLabel=n=>{let v='';for(let x=n;x>0;x=Math.floor((x-1)/26))v=String.fromCharCode(65+(x-1)%26)+v;return v;};
const res=sheets.Residuals;const residualHeaders=s.residual_headers??['iteration','continuity','x_velocity','y_velocity','nut','mass_net_kg_s','lift_N','drag_N','source_transcript_line'];const resLastCol=colLabel(residualHeaders.length);
title(res,`${s.label} residual records from native transcript`);style(res,`A5:${resLastCol}${lastRes}`);res.getRange(`A5:${resLastCol}5`).values=[residualHeaders.map(v=>v.replaceAll('_',' ').replace('nut','S-A variable'))];header(res,`A5:${resLastCol}5`);res.getRange(`A6:${resLastCol}${lastRes}`).values=data.residuals;res.getRange(`A:${resLastCol}`).format.columnWidth=20;res.getRange(`B6:${colLabel(residualHeaders.length-1)}${lastRes}`).setNumberFormat('0.0000E+00');res.freezePanes.freezeRows(5);
const sourceCol=colLabel(residualHeaders.length+2),hashCol=colLabel(residualHeaders.length+3);res.getRange(`${sourceCol}2:${hashCol}3`).values=[['Source','SHA256'],[path.relative(root,s.sources.find(x=>x.original.endsWith('setup.transcript')).preserved),s.sources.find(x=>x.original.endsWith('setup.transcript')).sha256]];header(res,`${sourceCol}2:${hashCol}2`);res.getRange(`${sourceCol}:${sourceCol}`).format.columnWidth=65;res.getRange(`${hashCol}:${hashCol}`).format.columnWidth=70;

// Check live formula sensitivity, then restore the real input before export.
wb.recalculate();const baselineCD=sum.getRange('B21').values[0][0];
if(Math.abs(baselineCD-s.CD)>1e-12)throw new Error('CD formula does not reconcile with independent calculation');
sum.getRange('B5').values=[[p.rho_kg_m3*2]];wb.recalculate();const changedCD=sum.getRange('B21').values[0][0];
if(Math.abs(changedCD-s.CD/2)>1e-12)throw new Error('Density sensitivity failed');
sum.getRange('B5').values=[[p.rho_kg_m3]];wb.recalculate();
for(const [cell,value] of [['B11',p.Re],['B12',p.RMS_fluctuation_m_s],['B14',p.qS_N],['B21',s.CD],['B22',s.CL]]){
  const actual=sum.getRange(cell).values[0][0];if(typeof actual!=='number'||Math.abs(actual-value)>Math.max(1e-12,Math.abs(value)*1e-12))throw new Error(`Formula check failed: ${cell}`);
}
if(s.stability_windows?.['100']){
  for(const [cell,name] of [['B31','drag'],['B32','lift']]){
    const actual=sum.getRange(cell).values[0][0],expected=s.stability_windows['100'].forces[name].range_over_mean_fraction;
    if(Math.abs(actual-expected)>1e-12)throw new Error('Last100 stability formula does not reconcile: '+name);
  }
}
const err=await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!|#SPILL!|#CALC!',options:{useRegex:true,maxResults:30},summary:'formula error scan'});
await fs.writeFile(path.join(folder,'workbook_verification.txt'),err.ndjson+'\nIndependent Re/RMS/qS/CD/CL reconciliations passed. Density doubled and restored: CD halved and restored.\n');
const previewDir=path.join(folder,'workbook_previews');await fs.mkdir(previewDir,{recursive:true});
for(const name of Object.keys(sheets)){
  const blob=await wb.render({sheetName:name,range:name==='Summary'?'A1:C36':name==='Acceptance'?'A1:B12':name==='Residuals'?`A1:${resLastCol}15`:'A1:G15',scale:1.5,format:'png'});
  await fs.writeFile(path.join(previewDir,name+'.png'),new Uint8Array(await blob.arrayBuffer()));
}
const outdir=path.join(root,'outputs','01a1b755-05b7-7841-9420-c1bed337cfa6');await fs.mkdir(outdir,{recursive:true});
const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(path.join(outdir,`${caseId}_data.xlsx`));
console.log(`Exported ${caseId}: ${data.forces.length} monitor rows, ${surfaceRows.length} surface rows, ${profileRows.length} profile rows`);
