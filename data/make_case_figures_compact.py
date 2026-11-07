"""Print-sized raw-data plots, preserving the existing audit figures."""
import argparse
import hashlib
import json
from pathlib import Path
from process_case import graph

ROOT=Path(__file__).resolve().parents[1]


def main():
    p=argparse.ArgumentParser();p.add_argument('--case',default='case01');a=p.parse_args()
    folder=ROOT/'data'/a.case;d=json.loads((folder/'workbook_input.json').read_text());s=d['summary'];out=folder/'figures';res=d['residuals']
    names=s.get('equation_names',['continuity','x-velocity','y-velocity','nut']);headers=s.get('residual_native_headers',['continuity','x-velocity','y-velocity','nut','mass-net','lift-force','drag-force'])
    palette=['#0072b2','#d55e00','#009e73','#cc79a7','#e69f00','#56b4e9','#222','#882255','#44aa99']
    series=[{'name':n.replace('nut','S-A').replace('-velocity',' vel'),'color':palette[i%len(palette)],'chunks':[[(r[0],r[headers.index(n)+1]) for r in res]]} for i,n in enumerate(names)]
    graph(out/'figure3_residuals_compact.svg',series,'Iteration','Scaled residual',True,s['residual_threshold'],layout='residual_print')
    lower,upper=s['midline_solid_interval_m']
    short_label={'case01':'S-A','case02':'k-e','case03':'RSM','case04':'k-e EWT','case05':'RSM EWT'}.get(s.get('logical_case_id',a.case),s['label'])
    for station,number in [('mid',7),('te',8),('wake',9)]:
        chunks=[[]]
        for r in d['profiles'][station]:
            y=r['y-coordinate'];u=r['velocity-magnitude']
            if station=='mid' and chunks[-1] and chunks[-1][-1][0]/1000<(lower+upper)/2<y:chunks.append([])
            chunks[-1].append((y*1000,u))
        graph(out/f'figure{number}_velocity_{station}_compact.svg',[{'name':short_label,'color':'#0072b2','chunks':chunks}], 'y (mm)','Velocity (m/s)',xrange=(-75,75),layout='profile_print')
    for side,number in [('pressure',10),('suction',11)]:
        graph(out/f'figure{number}_pressure_{side}_compact.svg',[{'name':short_label,'color':'#0072b2','chunks':[[(r['x-coordinate']*1000,r['pressure']) for r in d['surfaces'][side]]]}], 'x (mm)','Static pressure (Pa)',xrange=(0,100),layout='half_print')
    for side,number in [('suction',12),('pressure',13)]:
        graph(out/f'figure{number}_yplus_{side}_compact.svg',[{'name':short_label,'color':'#0072b2','chunks':[[(r['x-coordinate']*1000,r['y-plus']) for r in d['surfaces'][side]]]}], 'x (mm)','Wall y+',xrange=(0,100),layout='half_print')
    files=sorted(out.glob('*compact.svg'))
    manifest={'dataset':str(folder/'workbook_input.json'),'dataset_sha256':hashlib.sha256((folder/'workbook_input.json').read_bytes()).hexdigest(),
              'plotter_source_sha256':hashlib.sha256((ROOT/'data/process_case.py').read_bytes()).hexdigest(),
              'compact_script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'method':'Exact native samples, joined only within continuous fluid segments; no smoothing or cross-case interpolation',
              'print_layouts':{'residual':[1600,440],'profiles':[1600,355],'half_width_surfaces':[820,430]},
              'outputs':[{'path':str(q),'sha256':hashlib.sha256(q.read_bytes()).hexdigest()} for q in files]}
    (folder/'compact_plot_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(f'Saved eight compact print plots for {s["label"]}')


if __name__=='__main__':main()
