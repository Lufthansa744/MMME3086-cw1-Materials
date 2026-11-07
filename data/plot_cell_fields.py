"""Render actual cell-centred velocities and adjacent-cell y+ on native mesh geometry."""
from collections import defaultdict
import argparse
import csv
import hashlib
import html
import json
import math
from pathlib import Path
from plot_taskA_mesh import parse_mesh
from process_case import scalar_csv, snapshot

ROOT=Path(__file__).resolve().parents[1]


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def color(value,maximum):
    # Fixed perceptually ordered purple/green/yellow scale; the legend uses this same mapping.
    palette=[(68,1,84),(72,40,120),(62,73,137),(49,104,142),(38,130,142),(31,158,137),(53,183,121),(110,206,88),(181,222,43),(253,231,37)]
    t=max(0,min(1,value/maximum))*(len(palette)-1);i=min(int(t),len(palette)-2);u=t-i
    return '#'+''.join(f'{round(a*(1-u)+b*u):02x}' for a,b in zip(palette[i],palette[i+1]))


def start(w,h):return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">','<rect width="100%" height="100%" fill="white"/>','<g font-family="Arial,sans-serif" font-size="28" fill="#222">']
def label(svg,x,y,text,size=28,anchor='start',fill='#222'):
    svg.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" fill="{fill}">{html.escape(text)}</text>')
def line(svg,a,b,color='#333',width=1.4,dash=''):
    extra=f' stroke-dasharray="{dash}"' if dash else ''
    svg.append(f'<path d="M{a[0]:.3f},{a[1]:.3f}L{b[0]:.3f},{b[1]:.3f}" fill="none" stroke="{color}" stroke-width="{width}"{extra}/>')


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',default='case03');ap.add_argument('--mesh',default='solver/taskA/taskA_baseline.msh');ap.add_argument('--speed-max',type=float,default=120);ap.add_argument('--enhanced',action='store_true');a=ap.parse_args()
    src=ROOT/'solver'/a.case;out=ROOT/'data'/a.case;fig=out/'figures';native=out/'native/raw';fig.mkdir(parents=True,exist_ok=True)
    evidence=[snapshot(src/f'raw/{name}.csv',native/f'{name}.csv') for name in ['domain_cell_fields','suction_p_yplus','pressure_p_yplus','trailing_p_yplus']]
    mesh=ROOT/a.mesh;nodes,faces,zones,counts=parse_mesh(mesh)
    cellnodes=defaultdict(set)
    for n0,n1,c0,c1 in faces.values():
        for ci in [c0,c1]:
            if ci:cellnodes[ci].update([n0,n1])
    centres={ci:tuple(sum(nodes[n][j] for n in ns)/len(ns) for j in [0,1]) for ci,ns in cellnodes.items()}
    polygons={ci:sorted(ns,key=lambda n:math.atan2(nodes[n][1]-centres[ci][1],nodes[n][0]-centres[ci][0])) for ci,ns in cellnodes.items()}
    field_rows=scalar_csv(native/'domain_cell_fields.csv');fields={int(r['cell-id']):r for r in field_rows}
    velocity_legend_max=a.speed_max
    if max(math.hypot(r['x-velocity'],r['y-velocity']) for r in field_rows)>velocity_legend_max:raise ValueError('Actual speed exceeds shared legend; increase speed-max for both compared cases')
    if len(fields)!=len(field_rows) or set(fields)!=set(cellnodes):raise ValueError('Cell-id set does not match native mesh')
    errors={ci:math.dist(centres[ci],(r['x-coordinate'],r['y-coordinate'])) for ci,r in fields.items()}
    if max(errors.values())>1e-7:raise ValueError('Exported centroid does not match original native cell-id geometry')
    # Require a unique native centroid match within 1 micrometre, not merely a near-looking picture.
    bins=defaultdict(list);tol=1e-6
    for ci,p in centres.items():bins[(math.floor(p[0]/tol),math.floor(p[1]/tol))].append(ci)
    for ci,r in fields.items():
        p=(r['x-coordinate'],r['y-coordinate']);key=(math.floor(p[0]/tol),math.floor(p[1]/tol))
        candidates=[cj for di in [-1,0,1] for dj in [-1,0,1] for cj in bins.get((key[0]+di,key[1]+dj),[]) if math.dist(p,centres[cj])<tol]
        if candidates!=[ci]:raise ValueError('Ambiguous cell-to-coordinate mapping')
    foil_names=['aerofoil_suction','aerofoil_pressure','aerofoil_te']
    if not all(name in zones for name in foil_names):foil_names=['aerofoil-suction','aerofoil-pressure','aerofoil-trail']
    if not all(name in zones for name in foil_names):raise ValueError('Native mesh aerofoil boundary zones are missing')
    expected={next(c for c in faces[fi][2:] if c) for name in foil_names for fi in zones[name]['faces']}
    wallrows=sum([scalar_csv(native/f'{side}_p_yplus.csv') for side in ['suction','pressure','trailing']],[])
    wall={int(r['cell-id']):r for r in wallrows}
    maximum_yplus=max(r['y-plus'] for r in wallrows)
    yplus_legend_max=math.ceil(maximum_yplus/2)*2 if maximum_yplus<=20 else math.ceil(maximum_yplus/20)*20
    yplus_legend_ticks=[v for v in range(0,int(yplus_legend_max)+1,2 if yplus_legend_max<=20 else 50)]+([] if yplus_legend_max%50==0 or yplus_legend_max<=20 else [yplus_legend_max])
    highlight=lambda value:value>5 if a.enhanced else value<30
    if set(wall)!=expected:raise ValueError('Exported wall-adjacent cells do not match actual foil zone adjacency')
    for r in wallrows:
        ci=int(r['cell-id'])
        if not math.isclose(r['y-plus'],fields[ci]['y-plus'],rel_tol=1e-9,abs_tol=1e-8):raise ValueError('Wall and domain y+ disagree at the same cell-id')
    boundary_graph=defaultdict(list)
    for name in foil_names:
        for fi in zones[name]['faces']:
            n0,n1=faces[fi][:2];boundary_graph[n0].append(n1);boundary_graph[n1].append(n0)
    if any(len(v)!=2 for v in boundary_graph.values()):raise ValueError('Foil boundary is not one simple loop')
    first=min(boundary_graph,key=lambda n:nodes[n][0]);foil=[first];previous=None;current=first
    while True:
        nxt=next(n for n in boundary_graph[current] if n!=previous)
        if nxt==first:break
        foil.append(nxt);previous,current=current,nxt
        if len(foil)>len(boundary_graph):raise ValueError('Foil loop did not close')
    if len(foil)!=len(boundary_graph):raise ValueError('Incomplete foil loop')
    def transform(bounds,origin,scale,p):return origin[0]+(p[0]-bounds[0])*scale,origin[1]+(bounds[3]-p[1])*scale
    def poly(svg,ids,fn,fill,stroke='#555',stroke_width=.7):
        points=' '.join(f'{fn(nodes[n])[0]:.4f},{fn(nodes[n])[1]:.4f}' for n in ids)
        svg.append(f'<polygon points="{points}" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}"/>')
    def axes(svg,bounds,origin,scale,xticks,yticks,ytitle=True):
        fn=lambda p:transform(bounds,origin,scale,p);x0,y0=fn((bounds[0],bounds[3]));x1,y1=fn((bounds[1],bounds[2]))
        svg.append(f'<rect x="{x0}" y="{y0}" width="{x1-x0}" height="{y1-y0}" fill="none" stroke="#333" stroke-width="1.5"/>')
        for x in xticks:
            px,py=fn((x/1000,bounds[2]));line(svg,(px,py),(px,py+6));label(svg,px,py+35,str(x),28,'middle')
        for y in yticks:
            px,py=fn((bounds[0],y/1000));line(svg,(px-6,py),(px,py));label(svg,px-12,py+9,str(y),28,'end')
        label(svg,(x0+x1)/2,y1+76,'x (mm)',30,'middle')
        if ytitle:
            title_x=max(35,x0-100)
            svg.append(f'<text x="{title_x}" y="{(y0+y1)/2}" font-size="30" text-anchor="middle" transform="rotate(-90,{title_x},{(y0+y1)/2})">y (mm)</text>')
    def select(bounds,spacing):
        chosen={}
        for ci,r in fields.items():
            x,y=r['x-coordinate'],r['y-coordinate']
            if not(bounds[0]<=x<=bounds[1] and bounds[2]<=y<=bounds[3]):continue
            key=(math.floor(x/spacing),math.floor(y/spacing));distance=(x-(key[0]+.5)*spacing)**2+(y-(key[1]+.5)*spacing)**2
            if key not in chosen or distance<chosen[key][0]:chosen[key]=(distance,ci)
        ids={v[1] for v in chosen.values()}
        ids.update(ci for ci,r in fields.items() if r['x-velocity']<0 and bounds[0]<=r['x-coordinate']<=bounds[1] and bounds[2]<=r['y-coordinate']<=bounds[3])
        return sorted(ids)
    def arrows(svg,ids,fn,pixels_per_speed=None,fixed_length=None):
        for ci in ids:
            r=fields[ci];u,v=r['x-velocity'],r['y-velocity'];speed=math.hypot(u,v)
            if speed<1e-12:continue
            x,y=fn((r['x-coordinate'],r['y-coordinate']));length=fixed_length if fixed_length is not None else pixels_per_speed*speed
            dx,dy=u/speed*length,-v/speed*length;end=(x+dx/2,y+dy/2);begin=(x-dx/2,y-dy/2);c=color(speed,velocity_legend_max)
            line(svg,begin,end,c,1.25)
            head=min(4,max(2,length*.28));ux,uy=dx/length,dy/length
            line(svg,end,(end[0]-head*ux+head*.45*uy,end[1]-head*uy-head*.45*ux),c,1.25)
            line(svg,end,(end[0]-head*ux-head*.45*uy,end[1]-head*uy+head*.45*ux),c,1.25)
    # Figure 4: sampled actual vectors in the foil/wake region and a direction-only trailing-edge inset.
    svg=start(1600,630);full=(-.015,.225,-.05,.035);origin=(130,90);scale=4000;local=(.085,.125,-.022,.002);local_origin=(1190,145);local_scale=8500
    fn=lambda p:transform(full,origin,scale,p);fl=lambda p:transform(local,local_origin,local_scale,p)
    svg.insert(1,'<defs><clipPath id="vf"><rect x="130" y="90" width="960" height="340"/></clipPath><clipPath id="vi"><rect x="1190" y="145" width="340" height="204"/></clipPath></defs>')
    full_ids=select(full,.0055);local_ids=select(local,.0014)
    label(svg,130,45,'Cell-centred velocity vectors',30);label(svg,1190,105,'Trailing edge',28)
    svg.append('<g clip-path="url(#vf)">');arrows(svg,full_ids,fn,pixels_per_speed=.3);poly(svg,foil,fn,'white','#222',1.6);svg.append('</g>')
    svg.append('<g clip-path="url(#vi)">');arrows(svg,local_ids,fl,fixed_length=12);poly(svg,foil,fl,'white','#222',1.5);svg.append('</g>')
    axes(svg,full,origin,scale,[0,50,100,150,200],[-40,-20,0,20]);axes(svg,local,local_origin,local_scale,[90,100,110,120],[-20,-10,0],False)
    for ci in local_ids:
        r=fields[ci]
        if r['x-velocity']<0:
            x,y=fl((r['x-coordinate'],r['y-coordinate']));svg.append(f'<circle cx="{x}" cy="{y}" r="5" fill="none" stroke="#d40000" stroke-width="1.5"/>')
    # Outline the actual inset limits on the main view.
    p0,p1=fn((local[0],local[3])),fn((local[1],local[2]));svg.append(f'<rect x="{p0[0]}" y="{p0[1]}" width="{p1[0]-p0[0]}" height="{p1[1]-p0[1]}" fill="none" stroke="#222" stroke-dasharray="6 4"/>')
    label(svg,1185,475,'Inset: normalised',27);label(svg,1185,508,'direction arrows',27)
    label(svg,1185,550,'Red rings: uₓ < 0' if any(r['x-velocity']<0 for r in field_rows) else 'No cells with uₓ < 0',27,fill='#b00000' if any(r['x-velocity']<0 for r in field_rows) else '#222')
    for i in range(200):svg.append(f'<rect x="{160+i*2}" y="550" width="2.1" height="18" fill="{color(i/199*velocity_legend_max,velocity_legend_max)}"/>')
    for value in range(0,int(velocity_legend_max)+1,20):label(svg,160+value/velocity_legend_max*400,605,str(value),28,'middle')
    label(svg,600,568,'Speed (m/s)',28);svg.append('</g></svg>');vf=fig/('figure6_velocity_vectors.svg' if a.enhanced else 'figure4_velocity_vectors.svg');vf.write_text('\n'.join(svg),encoding='utf-8')
    # Figure 5: exact polygons of all foil-adjacent cells, filled by their own exported y+.
    svg=start(1600,640);bounds=(-.008,.108,-.024,.014);origin=(130,95);scale=10500;fn=lambda p:transform(bounds,origin,scale,p)
    svg.insert(1,'<defs><clipPath id="yf"><rect x="130" y="95" width="1218" height="399"/></clipPath></defs>')
    label(svg,130,43,'Foil-adjacent cell y+',30)
    svg.append('<g clip-path="url(#yf)">')
    for ci,ids in polygons.items():
        p=centres[ci]
        if bounds[0]-.01<=p[0]<=bounds[1]+.01 and bounds[2]-.01<=p[1]<=bounds[3]+.01:poly(svg,ids,fn,'white','#dddddd',.6)
    for ci in sorted(wall):poly(svg,polygons[ci],fn,color(wall[ci]['y-plus'],yplus_legend_max),'#b00000' if highlight(wall[ci]['y-plus']) else '#444',1.2 if highlight(wall[ci]['y-plus']) else .6)
    poly(svg,foil,fn,'white','#222',1.6);svg.append('</g>')
    axes(svg,bounds,origin,scale,[0,20,40,60,80,100],[-20,-10,0,10])
    for i in range(200):svg.append(f'<rect x="1420" y="{95+i*399/200}" width="32" height="{399/200+.2}" fill="{color(yplus_legend_max*(1-i/199),yplus_legend_max)}"/>')
    for value in yplus_legend_ticks:label(svg,1470,95+(yplus_legend_max-value)/yplus_legend_max*399+9,str(value),28)
    label(svg,1435,70,'y+',30,'middle')
    maximum=max(wall,key=lambda ci:wall[ci]['y-plus']);minimum=min(wall,key=lambda ci:wall[ci]['y-plus']);teid=int(scalar_csv(native/'trailing_p_yplus.csv')[0]['cell-id'])
    for ci,tx,ty in [(maximum,280,78),(minimum,870,610),(teid,1195,610)]:
        point=fn(centres[ci]);line(svg,(tx,ty-12 if ty>500 else ty+5),point,'#333',1.3)
        label(svg,tx,ty,f'{wall[ci]["y-plus"]:.2f}',30,'middle')
    label(svg,130,625,'Red cell outlines: y+ > 5' if a.enhanced else 'Red cell outlines: y+ < 30',28,fill='#b00000');svg.append('</g></svg>');yf=fig/('figure6_wall_cell_yplus.svg' if a.enhanced else 'figure5_wall_cell_yplus.svg');yf.write_text('\n'.join(svg),encoding='utf-8')
    combined=None;combined_info=None
    if a.enhanced:
        # A full-width two-panel Figure 6. The actual thin cells are enlarged equally in x and y.
        svg=start(1600,690);vb=(-.01,.23,-.045,.035);vo=(110,120);vs=2700
        peak_point=centres[maximum];yb=(peak_point[0]-.0009,peak_point[0]+.0009,peak_point[1]-.00035,peak_point[1]+.00035);yo=(920,120);ys=320000
        fv=lambda p:transform(vb,vo,vs,p);fy=lambda p:transform(yb,yo,ys,p)
        svg.insert(1,'<defs><clipPath id="cv"><rect x="110" y="120" width="648" height="216"/></clipPath><clipPath id="cy"><rect x="920" y="120" width="576" height="224"/></clipPath></defs>')
        label(svg,110,45,'(a) Velocity vectors and wake',30);label(svg,920,45,'(b) Actual near-wall cell y+',30)
        cvids=select(vb,.0065)
        svg.append('<g clip-path="url(#cv)">');arrows(svg,cvids,fv,pixels_per_speed=.000075*vs);poly(svg,foil,fv,'white','#222',1.5);svg.append('</g>')
        axes(svg,vb,vo,vs,[0,100,200],[-40,-20,0,20])
        corner0,corner1=fv((yb[0],yb[3])),fv((yb[1],yb[2]));zoom_marker=fv(peak_point)
        svg.append(f'<rect x="{corner0[0]}" y="{corner0[1]}" width="{corner1[0]-corner0[0]}" height="{corner1[1]-corner0[1]}" fill="none" stroke="#222" stroke-width="1.2"/>')
        line(svg,(270,102),zoom_marker,'#222',1.2);label(svg,270,97,'Zoom (b)',28,'middle')
        svg.append('<g clip-path="url(#cy)">')
        visible_cells=[]
        for ci,ids in polygons.items():
            pts=[nodes[n] for n in ids]
            if max(p[0] for p in pts)<yb[0] or min(p[0] for p in pts)>yb[1] or max(p[1] for p in pts)<yb[2] or min(p[1] for p in pts)>yb[3]:continue
            visible_cells.append(ci)
            poly(svg,ids,fy,color(wall[ci]['y-plus'],yplus_legend_max) if ci in wall else 'white','#777',.25)
        poly(svg,foil,fy,'white','#222',1);svg.append('</g>')
        xt=[round((yb[0]*1000)+(.0018*1000)*i/4,2) for i in range(5)]
        yt=[round((yb[2]*1000)+(.0007*1000)*i/2,2) for i in range(3)]
        axes(svg,yb,yo,ys,xt,yt)
        point=fy(peak_point);line(svg,(1190,98),point,'#222',1.2);label(svg,1190,90,f'Cell value: {wall[maximum]["y-plus"]:.2f}',30,'middle')
        for i in range(200):
            svg.append(f'<rect x="{130+i*2}" y="515" width="2.1" height="18" fill="{color(i/199*velocity_legend_max,velocity_legend_max)}"/>')
            svg.append(f'<rect x="{950+i*2}" y="515" width="2.1" height="18" fill="{color(i/199*yplus_legend_max,yplus_legend_max)}"/>')
        for value in [0,40,80,120]:label(svg,130+value/velocity_legend_max*400,575,str(value),28,'middle')
        for i in range(5):label(svg,950+i*100,575,f'{yplus_legend_max*i/4:g}',28,'middle')
        label(svg,570,534,'m/s',28);label(svg,1390,534,'y+',28)
        label(svg,110,625,'Arrow length ∝ speed',28);label(svg,110,663,'Shared physical scale with Figure 4',27)
        label(svg,920,625,f'All {len(wall)} foil-adjacent cells:',28);label(svg,920,663,f'y+ = {wall[minimum]["y-plus"]:.2f}–{wall[maximum]["y-plus"]:.2f}',28)
        svg.append('</g></svg>');combined=fig/'figure6_combined_compact.svg';combined.write_text('\n'.join(svg),encoding='utf-8')
        combined_info={'vector_bounds_m':vb,'vector_selected_native_cell_ids':cvids,'vector_arrow_physical_displacement_factor_s':.000075,
                       'near_wall_zoom_bounds_m':yb,'near_wall_zoom_equal_axis_scale_px_per_m':ys,'visible_native_cell_ids':visible_cells,
                       'zoom_location_actual_bbox_marked_in_vector_panel':True,
                       'cell_label_id':maximum,'cell_label_value':wall[maximum]['y-plus'],'zoom_policy':'Equal x/y enlargement of exact native polygons; wall-layer thickness is not exaggerated or rescaled independently.'}
    negatives=[{'cell_id':ci,'x_m':r['x-coordinate'],'y_m':r['y-coordinate'],'u_m_s':r['x-velocity'],'v_m_s':r['y-velocity']} for ci,r in fields.items() if r['x-velocity']<0]
    manifest={'case':a.case,'mesh':{'path':str(mesh),'sha256':sha(mesh),'counts':counts},'native_sources':evidence,'combined_figure6':combined_info,
              'cell_mapping':{'domain_count':len(fields),'max_centroid_error_m':max(errors.values()),'unique_centroid_match_tolerance_m':tol,'all_unique_matches_pass':True,
                              'foil_adjacent_cell_count':len(expected),'exported_wall_id_set_equals_mesh_adjacency':True,'wall_domain_yplus_match_all':True},
              'velocity_display':{'full_bounds_m':full,'full_spatial_bins_m':.0055,'full_selected_native_cell_ids':full_ids,'full_arrow_pixels_per_m_s':.3,'physical_arrow_displacement_factor_s':.3/4000,'speed_legend_max_m_s':velocity_legend_max,
                                  'inset_bounds_m':local,'inset_spatial_bins_m':.0014,'inset_selected_native_cell_ids':local_ids,'inset_arrows_normalised_pixels':12,
                                  'selection':'One actual cell nearest each spatial-bin centre; native position and values unchanged. Every negative-u cell in the view also included. No velocity interpolation.',
                                  'negative_u_cells':negatives,'interpretation_limit':'Negative global u alone does not establish wall separation or a closed recirculation region; leading-edge curved flow must be distinguished from local trailing-edge reverse flow.'},
              'wall_yplus_display':{'filled_cells':len(wall),'legend_range':[0,yplus_legend_max],'actual_min':wall[minimum]['y-plus'],'actual_max':wall[maximum]['y-plus'],'min_cell_id':minimum,'max_cell_id':maximum,'TE_cell_id':teid,'TE_yplus':wall[teid]['y-plus'],'below30_cell_ids':[ci for ci,r in wall.items() if r['y-plus']<30],
                                    'value_policy':'Each exact native cell polygon uses its own exported cell value; min/max/TE values labelled; colour legend is fixed and includes actual range. No smoothing.'},
              'script':{'path':str(Path(__file__).resolve()),'sha256':sha(Path(__file__))},'figures':[{'path':str(p),'sha256':sha(p)} for p in [vf,yf]+([combined] if combined else [])]}
    (out/'cell_field_plot_audit.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print(json.dumps({'mapping':manifest['cell_mapping'],'selected_vectors':[len(full_ids),len(local_ids)],'negative_u_cells':negatives,'wall_yplus':manifest['wall_yplus_display']},indent=2))


if __name__=='__main__':main()
