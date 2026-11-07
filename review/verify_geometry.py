"""Read-only audit of actual saved Task A coordinates and named selections."""
import csv
import hashlib
import json
import math
from pathlib import Path
import zipfile
from xml.etree import ElementTree as ET

root = Path(__file__).resolve().parent.parent
base = root / 'solver' / 'taskA'
sources = ['create_geometry.py', 'geometry_properties.txt', 'boundary_edges.csv',
           'foil_coordinates_m.csv', 'geometry_creation.txt', 'taskA_geometry.scdoc']
rows = list(csv.DictReader((base / 'foil_coordinates_m.csv').open()))
sides = {s: [] for s in ['suction', 'pressure']}
angle = math.radians(-8)
error = 0
for row in rows:
    x, y, z = (float(row[k]) for k in ['x_m', 'y_m', 'z_m'])
    xb = x * math.cos(angle) + y * math.sin(angle)
    yb = -x * math.sin(angle) + y * math.cos(angle)
    t = max(0, xb / .1)
    sign = 1 if row['side'] == 'suction' else -1
    expected = sign * .06 * (.2969 * math.sqrt(t) - .126 * t - .3516 * t**2
                             + .2843 * t**3 - .1015 * t**4)
    error = max(error, abs(yb - expected), abs(z))
    sides[row['side']].append((x, y, xb, yb))
upper, lower = sides['suction'], sides['pressure']
te = tuple((upper[-1][i] + lower[-1][i]) / 2 for i in [0, 1])
polygon = upper + list(reversed(lower))
area = abs(sum(p[0] * q[1] - q[0] * p[1]
               for p, q in zip(polygon, polygon[1:] + polygon[:1]))) / 2
edges = list(csv.DictReader((base / 'boundary_edges.csv').open()))
outer = [e for e in edges if not e['name'].startswith('aerofoil')]
outer_points = [(float(e[k + '_x_m']), float(e[k + '_y_m']))
                for e in outer for k in ['start', 'end']]
with zipfile.ZipFile(base / 'taskA_geometry.scdoc') as archive:
    document = ET.fromstring(archive.read('SpaceClaim/document.xml'))
    groups = []
    for element in document.iter():
        if element.tag.split('}')[-1] == 'NamedSelectionDef':
            names = [n.text for n in element if n.tag.split('}')[-1] == 'name']
            refs = [n.attrib['refId'] for n in element.iter() if 'refId' in n.attrib]
            groups.append({'name': names, 'object_refs': refs})
result = {
    'source_files': [{'path': str(base / p), 'sha256': hashlib.sha256((base / p).read_bytes()).hexdigest()}
                     for p in sources],
    'coordinate_count': len(rows), 'side_counts': {k: len(v) for k, v in sides.items()},
    'max_formula_or_planarity_error_m': error,
    'chord_m': math.hypot(*te), 'chord_angle_degrees': math.degrees(math.atan2(te[1], te[0])),
    'positive_aerodynamic_AoA_degrees_if_inlet_is_plus_x': -math.degrees(math.atan2(te[1], te[0])),
    'trailing_edge_centre_m': te, 'trailing_edge_gap_m': math.dist(upper[-1][:2], lower[-1][:2]),
    'maximum_sampled_thickness_m': max(p[3] - q[3] for p, q in zip(upper, lower)),
    'foil_sample_polygon_area_m2': area,
    'expected_fluid_surface_area_from_polygon_m2': .15 - area,
    'duct_x_bounds_m': [min(p[0] for p in outer_points), max(p[0] for p in outer_points)],
    'duct_y_bounds_m': [min(p[1] for p in outer_points), max(p[1] for p in outer_points)],
    'saved_named_selections': groups,
    'cross_duct_sampling_x_m_if_using_chord_midpoint_and_TE_centre': [te[0] / 2, te[0], te[0] + .1],
    'limitation': 'Coordinate formula and named-selection persistence verified. Kernel face hole, surface area and mesher/Fluent boundary transfer need direct downstream evidence.'
}
target = Path(__file__).parent / 'taskA_geometry_audit.json'
target.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(target)
