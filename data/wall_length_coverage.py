"""Length-weighted y+ coverage on actual 2D mesh wall faces, without interpolation."""
import argparse
import json
import math
from pathlib import Path
from plot_taskA_mesh import parse_mesh, sha
from process_case import scalar_csv

ROOT=Path(__file__).resolve().parents[1]

def main():
    p=argparse.ArgumentParser();p.add_argument('--case',required=True);p.add_argument('--mesh',required=True);a=p.parse_args()
    mesh=ROOT/a.mesh;nodes,faces,zones,counts=parse_mesh(mesh)
    records={};sources=[]
    for side,aliases in [('suction',['aerofoil_suction','aerofoil-suction']),('pressure',['aerofoil_pressure','aerofoil-pressure']),('trailing',['aerofoil_te','aerofoil-trail'])]:
        zone=next(n for n in aliases if n in zones)
        source=ROOT/'data'/a.case/'native/raw'/f'{side}_p_yplus.csv'
        if not source.exists():source=ROOT/'solver'/a.case/'raw'/f'{side}_p_yplus.csv'
        rows=scalar_csv(source);sources.append({'path':str(source),'sha256':sha(source)})
        if len(rows)!=len(zones[zone]['faces']):raise ValueError('Wall face count differs from native scalar rows')
        unused=set(zones[zone]['faces']);mapped=[]
        for r in rows:
            point=(r['x-coordinate'],r['y-coordinate'])
            candidates=[]
            for fi in unused:
                n0,n1,c0,c1=faces[fi];mid=tuple((nodes[n0][j]+nodes[n1][j])/2 for j in [0,1])
                if math.dist(point,mid)<=1e-7 and int(r['cell-id']) in [c0,c1]:candidates.append(fi)
            if len(candidates)!=1:raise ValueError('Face midpoint/adjacent cell ID is not unique')
            fi=candidates[0];unused.remove(fi);n0,n1,_,_=faces[fi]
            mapped.append({'face_id':fi,'adjacent_cell_id':int(r['cell-id']),'length_m':math.dist(nodes[n0],nodes[n1]),'yplus':r['y-plus']})
        length=sum(r['length_m'] for r in mapped)
        filters={'at_most_1':lambda y:y<=1,'above_1_to_5':lambda y:1<y<=5,'above_5':lambda y:y>5,'below_30':lambda y:y<30,'from_30_to_300':lambda y:30<=y<=300,'above_300':lambda y:y>300}
        records[side]={'zone':zone,'face_count':len(mapped),'length_m':length,'yplus_range':[min(r['yplus'] for r in mapped),max(r['yplus'] for r in mapped)],
                       'length_fractions':{name:sum(r['length_m'] for r in mapped if f(r['yplus']))/length for name,f in filters.items()},'native_faces':mapped}
    result={'case':a.case,'mesh':{'path':str(mesh),'sha256':sha(mesh)},'sources':sources,'sides':records,
            'definition':'Sum actual wall-face lengths meeting each y+ indicator, divided by total side length. The face scalar is its native adjacent-cell y+; no interpolation. Thresholds are descriptive wall-treatment diagnostics, not proof of mesh accuracy.',
            'mapping':'Each exported face midpoint matched uniquely within 1e-7 m with identical adjacent cell ID; every actual side face used once.',
            'script_sha256':sha(Path(__file__))}
    out=ROOT/'data'/a.case/'wall_length_coverage.json';out.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps({side:{k:v for k,v in rec.items() if k!='native_faces'} for side,rec in records.items()},indent=2))

if __name__=='__main__':main()
