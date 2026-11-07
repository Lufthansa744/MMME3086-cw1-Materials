"""Draw an independently checked geometry diagram from actual exported coordinates."""
import csv
import hashlib
import html
import json
import math
from pathlib import Path
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "solver" / "taskA"
OUT = ROOT / "data" / "taskA"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    files = [SOURCE / name for name in ["foil_coordinates_m.csv", "boundary_edges.csv", "geometry_properties.txt", "create_geometry.py", "taskA_geometry.scdoc"]]
    with files[0].open(newline="", encoding="utf-8-sig") as f:
        raw = list(csv.DictReader(f))
    foil = {}
    for side in ["suction", "pressure"]:
        records = sorted([r for r in raw if r["side"] == side], key=lambda r: int(r["index"]))
        foil[side] = [(float(r["x_m"]), float(r["y_m"])) for r in records]
        assert len(records) == 401 and all(float(r["z_m"]) == 0 for r in records)
    with files[1].open(newline="", encoding="utf-8-sig") as f:
        edges = {r["name"]: {k: float(v) if k not in ["name"] else v for k, v in r.items()} for r in csv.DictReader(f)}
    assert len(edges) == 7
    le = foil["suction"][0]
    assert math.dist(le, foil["pressure"][0]) < 1e-12
    te = tuple((foil["suction"][-1][i] + foil["pressure"][-1][i]) / 2 for i in [0, 1])
    chord = math.dist(le, te)
    chord_angle = math.degrees(math.atan2(te[1] - le[1], te[0] - le[0]))
    assert abs(chord - .1) < 1e-12 and abs(chord_angle + 8) < 1e-10
    xmin, xmax = edges["inlet"]["mid_x_m"], edges["outlet"]["mid_x_m"]
    ymin, ymax = edges["wall_bottom"]["mid_y_m"], edges["wall_top"]["mid_y_m"]
    assert abs(xmax - xmin - 1) < 1e-12 and abs(ymax - ymin - .15) < 1e-12
    for side in ["suction", "pressure"]:
        edge = edges["aerofoil_" + side]
        assert math.dist(foil[side][0], (edge["start_x_m"], edge["start_y_m"])) < 1e-12
        assert math.dist(foil[side][-1], (edge["end_x_m"], edge["end_y_m"])) < 1e-12
    te_edge = edges["aerofoil_te"]
    assert math.dist(te, (te_edge["mid_x_m"], te_edge["mid_y_m"])) < 1e-12
    cos_a, sin_a = math.cos(math.radians(chord_angle)), math.sin(math.radians(chord_angle))
    unrotated = {side: [(cos_a*(x-le[0])+sin_a*(y-le[1]), -sin_a*(x-le[0])+cos_a*(y-le[1])) for x,y in points] for side,points in foil.items()}
    symmetry_error = max(abs(a[0]-b[0]) + abs(a[1]+b[1]) for a,b in zip(unrotated["suction"], unrotated["pressure"]))
    assert symmetry_error < 1e-12
    max_thickness = max(a[1]-b[1] for a,b in zip(unrotated["suction"],unrotated["pressure"]))
    te_gap = math.dist(foil["suction"][-1], foil["pressure"][-1])
    svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1300" height="980" viewBox="0 0 1300 980">',
           '<defs><marker id="arr" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto-start-reverse"><path d="M0,0 L6,3 L0,6" fill="none" stroke="#333"/></marker></defs>',
           '<rect width="1300" height="980" fill="white"/>',
           '<g font-family="Arial,sans-serif" font-size="18" fill="#202020">']
    def text(x,y,s,size=18,anchor="start",color="#202020"):
        svg.append(f'<text x="{x:.3f}" y="{y:.3f}" font-size="{size}" text-anchor="{anchor}" fill="{color}">{html.escape(s)}</text>')
    def line(x1,y1,x2,y2,color="#333",dash="",arrow=False):
        extra = f' stroke-dasharray="{dash}"' if dash else ""
        if arrow: extra += ' marker-start="url(#arr)" marker-end="url(#arr)"'
        svg.append(f'<line x1="{x1:.3f}" y1="{y1:.3f}" x2="{x2:.3f}" y2="{y2:.3f}" stroke="{color}" stroke-width="1.5"{extra}/>')
    def poly(points,transform,color,width=2,fill="none"):
        pts=" ".join(f"{transform(x,y)[0]:.3f},{transform(x,y)[1]:.3f}" for x,y in points)
        svg.append(f'<polyline points="{pts}" stroke="{color}" stroke-width="{width}" fill="{fill}"/>')
    text(60,40,"Task A — independent diagram of the actual exported geometry",25)
    text(60,72,"Coordinate reconstruction from solver/taskA; this is not a Discovery screenshot",17)
    text(60,112,"(a) Full duct, equal scales on x and y",20)
    def full(x,y): return 110+(x-xmin)*1050, 205+(ymax-y)*1050
    x1,y1=full(xmin,ymax); x2,y2=full(xmax,ymin)
    svg.append(f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" fill="#f0f6f9" stroke="#333" stroke-width="2"/>')
    outline=foil["suction"]+list(reversed(foil["pressure"]))
    poly(outline+[outline[0]],full,"#333",1.5,"#cccccc")
    line(x1,165,x2,165,arrow=True); text((x1+x2)/2,155,f"{(xmax-xmin)*1000:.0f} mm",18,"middle")
    line(1220,y1,1220,y2,arrow=True); text(1254,(y1+y2)/2,f"{(ymax-ymin)*1000:.0f} mm",14,"middle")
    text(x1-10,(y1+y2)/2,"inlet",18,"end")
    text(x2+10,(y1+y2)/2,"outlet",18)
    text((x1+x2)/2,y1-10,"wall_top",18,"middle")
    text((x1+x2)/2,y2+25,"wall_bottom",18,"middle")
    ax,ay=full(-.35,0); bx,by=full(-.22,0)
    line(ax,ay,bx,by); svg.append(f'<path d="M{bx-8},{by-4} L{bx},{by} L{bx-8},{by+4}" fill="none" stroke="#333" stroke-width="2"/>')
    text(ax,ay-15,"Inlet flow: +x",17)
    for name,p in [("LE",le),("TE",te)]:
        x,y=full(*p); text(x,y+32,name,16,"middle")
    text(60,440,"(b) Aerofoil detail, equal scales on x and y",20)
    def local(x,y): return 180+(x+.01)*8000, 515+(.012-y)*8000
    poly(outline+[outline[0]],local,"#777",1,"#e7e7e7")
    poly(foil["suction"],local,"#0072b2",3)
    poly(foil["pressure"],local,"#d55e00",3)
    poly([foil["suction"][-1],foil["pressure"][-1]],local,"#202020",3)
    lx,ly=local(*le); tx,ty=local(*te)
    line(lx,ly,tx,ty,"#009e73","8 5")
    hx,hy=local(le[0]+.04,le[1]); line(lx,ly,hx,hy,"#777","4 4")
    r=210; end=(lx+r*cos_a,ly-r*sin_a)
    svg.append(f'<path d="M{lx+r},{ly} A{r},{r} 0 0 1 {end[0]},{end[1]}" fill="none" stroke="#333"/>')
    text(lx+r+15,ly+22,f"{abs(chord_angle):.0f}°",20)
    text(lx-10,ly-14,"LE (0, 0) mm",17,"end")
    text(780,835,f"TE centre ({te[0]*1000:.3f}, {te[1]*1000:.3f}) mm",17)
    text(710,550,"aerofoil_suction",18,color="#0072b2")
    sx,sy=local(*foil["suction"][230]); line(800,557,sx,sy,"#0072b2")
    text(620,800,"aerofoil_pressure",18,color="#d55e00")
    px,py=local(*foil["pressure"][230]); line(700,780,px,py,"#d55e00")
    text(1100,770,"aerofoil_te",17)
    line(1100,750,tx,ty)
    text(90,855,f"Chord = {chord*1000:.3f} mm; chord direction = {chord_angle:.3f}° from +x; inlet direction = 0°",18)
    text(90,887,"Physical angle of attack = inlet direction − chord direction = +8°",18)
    text(90,919,f"Finite trailing edge is closed by aerofoil_te: gap = {te_gap*1000:.3f} mm",18)
    text(90,951,"Coordinates in metres in source CSV files; dimensions shown here in millimetres",16)
    svg.append('</g></svg>')
    OUT.mkdir(parents=True, exist_ok=True)
    figure=OUT/"geometry_coordinate_check.svg"
    figure.write_text("\n".join(svg),encoding="utf-8")
    ElementTree.parse(figure)
    audit={"artifact_type":"coordinate-derived geometry inspection; not a software screenshot", "sources":[{"path":str(p),"sha256":digest(p)} for p in files],
           "script":{"path":str(Path(__file__).resolve()),"sha256":digest(Path(__file__))},
           "coordinate_units":"m", "LE_m":le,"TE_centre_m":te,"chord_m":chord,"chord_angle_deg":chord_angle,
           "physical_AoA_deg_for_positive_x_inlet":-chord_angle,"duct_length_m":xmax-xmin,"duct_height_m":ymax-ymin,
           "max_sampled_thickness_m":max_thickness,"trailing_edge_gap_m":te_gap,"unrotated_symmetry_error_m":symmetry_error,
           "boundary_names":list(edges),"geometry_checks":"pass: exported endpoints, planarity, dimensions, angle and symmetry",
           "figure":{"path":str(figure),"sha256":digest(figure)}}
    (OUT/"geometry_check_audit.json").write_text(json.dumps(audit,indent=2),encoding="utf-8")
    print(json.dumps({k:audit[k] for k in ["LE_m","TE_centre_m","chord_m","chord_angle_deg","max_sampled_thickness_m","trailing_edge_gap_m","unrotated_symmetry_error_m"]},indent=2))


if __name__=="__main__":
    main()
