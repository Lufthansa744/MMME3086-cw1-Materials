"""Publish the accepted centred native artwork without replacing Mac report source."""
from pathlib import Path
import csv
import hashlib
import json
import os
import shutil

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
TARGET = Path(r'D:\CFD_WorkScratch\MMME3086-cw1-Materials')
REVISION = '2026-11-10-centered'
DELIVERY = ROOT / f'report/native_fluent_{REVISION}'
EXPECTED_MM = {
    'fig02_mesh_bc.pdf': (159.9974222222222, 73.9988077777778),
    'fig04_rsm_vectors.pdf': (165.1, 65.008125),
    'fig05_rsm_yplus.pdf': (165.1, 66.04),
    'fig06_enhanced_combined.pdf': (165.1, 143.0),
}
EXCLUDE = {'.git', 'node_modules', '__pycache__', '.venv', '.pytest_cache'}


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def record(path, base=ROOT):
    return {'path': path.relative_to(base).as_posix(), 'bytes': path.stat().st_size,
            'sha256': digest(path)}


def copy_checked(source):
    destination = TARGET / source.relative_to(ROOT)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if digest(destination) != digest(source):
        raise RuntimeError(f'Copy changed bytes: {source}')


def main():
    if not (TARGET / '.git').is_dir():
        raise RuntimeError('Verified Git checkout missing')
    acceptance_path = ROOT / f'review/native_figures_{REVISION}/final_acceptance.json'
    acceptance = json.loads(acceptance_path.read_text(encoding='utf-8-sig'))
    if acceptance.get('overall') != 'ACCEPT':
        raise RuntimeError('Independent review has not accepted the centred artwork')
    acceptance_text = json.dumps(acceptance)
    artwork = []
    for name, expected in EXPECTED_MM.items():
        path = DELIVERY / name
        reader = PdfReader(path)
        if len(reader.pages) != 1:
            raise RuntimeError(f'Expected one artwork page: {name}')
        box = reader.pages[0].mediabox
        actual = [float(box.width) * 25.4 / 72, float(box.height) * 25.4 / 72]
        if any(abs(a - b) > .01 for a, b in zip(actual, expected)):
            raise RuntimeError(f'Wrong physical box: {name}, {actual}')
        item = record(path)
        if item['sha256'] not in acceptance_text:
            raise RuntimeError(f'Acceptance does not identify final artwork: {name}')
        item['physical_size_mm'] = actual
        artwork.append(item)
    for name in ('fig02_mesh_bc.pdf', 'fig04_rsm_vectors.pdf'):
        if digest(DELIVERY / name) != digest(ROOT / 'report/native_fluent_2026-11-10' / name):
            raise RuntimeError(f'Unchanged figure source bytes differ: {name}')

    sample_path = ROOT / f'solver/native_figures_{REVISION}/case05/native_rake_centered_velocity_evidence.csv'
    with sample_path.open(newline='') as stream:
        fluid_samples = len(list(csv.DictReader(stream)))
    if fluid_samples <= 0 or fluid_samples > 540:
        raise RuntimeError('Unexpected native rake sample count')
    for name in ('fig02_mesh_bc.png', 'MAC_FINAL_PROMPT.txt', 'MAC_NATIVE_FIGURE_HANDOFF.md',
                 'figure6_caption.tex'):
        if not (DELIVERY / name).is_file():
            raise RuntimeError(f'Required handoff file missing: {name}')

    manifest_path = DELIVERY / 'native_artwork_delivery_manifest.json'
    manifest = {
        'date': '2026-11-10', 'revision': REVISION,
        'repository': 'https://github.com/Lufthansa744/MMME3086-cw1-Materials',
        'supersedes_artwork_set': 'report/native_fluent_2026-11-10',
        'scope': 'Centred artwork addendum; current Mac report source is preserved',
        'layout_authority': 'User-supplied Mac report PDF attachment -4; same artwork boxes',
        'figure_1': 'Retain verified native SpaceClaim picture pixels',
        'unchanged_figures_2_and_4_bytes_verified': True,
        'scientific_layers': 'Native Fluent Save Picture PNG embedded losslessly',
        'post_export_layers': 'Vector typography, axes, labels and factual annotations',
        'display_windows_mm': {
            'figure_5': {'x': [-8, 108], 'y': [-17.4705965338148, 20.5294034661852],
                         'foil_bbox_y_midpoint': 1.5294034661851664},
            'figure_6_a': {'x': [-70, 170], 'y': [-30, 25],
                           'nominal_chord_midpoint_x': 50,
                           'visible_extent_after_trailing_edge': 70.489516},
        },
        'case_5_vector_sampling': {'rakes': 12, 'requested': 540,
                                   'fluid_exported': fluid_samples,
                                   'solid_excluded': 540 - fluid_samples,
                                   'actual_native_csv': record(sample_path),
                                   'visible_clipped_glyph_count_asserted': False},
        'solution_iterations_performed': False, 'geometry_or_physics_changed': False,
        'latex_compiled': False, 'final_updated_Overleaf_report_layout_checked': False,
        'independent_acceptance': record(acceptance_path), 'artwork': artwork,
        'delivery_files': [record(path) for path in sorted(DELIVERY.iterdir())
                           if path.is_file() and path != manifest_path],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

    folders = (f'solver/native_figures_{REVISION}', f'data/native_figures_{REVISION}',
               f'review/native_figures_{REVISION}', f'report/native_fluent_{REVISION}')
    for relative in folders:
        for parent, directories, filenames in os.walk(ROOT / relative, followlinks=False):
            directories[:] = [name for name in directories if name not in EXCLUDE
                              and not (Path(parent) / name).is_symlink()
                              and not (Path(parent) / name).is_junction()]
            for name in filenames:
                source = Path(parent) / name
                if source.suffix != '.pyc' and not source.is_symlink():
                    copy_checked(source)
    for relative in ('README.md', 'MAC_HANDOFF.md',
                     'coordination/prepare_centered_native_graphics_delivery.py'):
        copy_checked(ROOT / relative)

    inventory_path = TARGET / 'repository_file_manifest.json'
    inventory = json.loads(inventory_path.read_text(encoding='utf-8-sig'))
    records = []
    for parent, directories, filenames in os.walk(TARGET, followlinks=False):
        directories[:] = [name for name in directories if name not in EXCLUDE]
        for name in filenames:
            path = Path(parent) / name
            if path != inventory_path:
                records.append(record(path, TARGET))
    inventory['files'] = sorted(records, key=lambda item: item['path'])
    inventory['latest_native_artwork_addendum'] = manifest_path.relative_to(ROOT).as_posix()
    inventory_path.write_text(json.dumps(inventory, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'artwork': artwork, 'native_rake_fluid_samples': fluid_samples,
                      'repository_payload_files': len(records)}, indent=2))


if __name__ == '__main__':
    main()
