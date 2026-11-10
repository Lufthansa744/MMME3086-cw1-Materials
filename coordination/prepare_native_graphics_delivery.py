"""Publish the accepted native-artwork addendum without replacing Mac report source."""
from pathlib import Path
import hashlib
import json
import os
import shutil

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
TARGET = Path(r'D:\CFD_WorkScratch\MMME3086-cw1-Materials')
DELIVERY = ROOT / 'report/native_fluent_2026-11-10'
EXPECTED_MM = {
    'fig02_mesh_bc.pdf': (159.9974, 73.9988),
    'fig04_rsm_vectors.pdf': (165.1, 65.008125),
    'fig05_rsm_yplus.pdf': (165.1, 66.04),
    'fig06_enhanced_combined.pdf': (165.1, 143.0),
}
EXCLUDE = {'.git', 'node_modules', '__pycache__', '.venv', '.pytest_cache'}


def digest(path):
    result = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            result.update(block)
    return result.hexdigest()


def record(path, base=ROOT):
    return {'path': path.relative_to(base).as_posix(),
            'bytes': path.stat().st_size, 'sha256': digest(path)}


def copy_checked(source):
    relative = source.relative_to(ROOT)
    destination = TARGET / relative
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)
    if digest(destination) != digest(source):
        raise RuntimeError(f'Copy changed bytes: {relative}')


def main():
    if not (TARGET / '.git').is_dir():
        raise RuntimeError('Verified Git checkout missing')
    acceptance_path = ROOT / 'review/native_figures_2026-11-10/final_acceptance.json'
    if not acceptance_path.is_file():
        raise RuntimeError('Independent final acceptance record missing')
    acceptance = json.loads(acceptance_path.read_text(encoding='utf-8-sig'))
    if acceptance.get('overall') != 'ACCEPT':
        raise RuntimeError('Independent review has not accepted the final artwork')

    assets = []
    for name, expected in EXPECTED_MM.items():
        path = DELIVERY / name
        reader = PdfReader(path)
        if len(reader.pages) != 1:
            raise RuntimeError(f'Expected single artwork page: {name}')
        box = reader.pages[0].mediabox
        actual = [float(box.width) * 25.4 / 72, float(box.height) * 25.4 / 72]
        if any(abs(a - b) > 0.01 for a, b in zip(actual, expected)):
            raise RuntimeError(f'Wrong printed box: {name}: {actual}')
        item = record(path)
        item.update({'physical_size_mm': actual, 'pages': 1})
        assets.append(item)

    # Review must identify the exact files being delivered, rather than earlier candidates.
    acceptance_text = json.dumps(acceptance)
    for item in assets:
        if item['sha256'] not in acceptance_text:
            raise RuntimeError(f'Acceptance does not identify final artwork: {item["path"]}')
    if not (DELIVERY / 'fig02_mesh_bc.png').is_file():
        raise RuntimeError('Figure 2 PNG drop-in missing')

    manifest = {
        'date': '2026-11-10',
        'repository': 'https://github.com/Lufthansa744/MMME3086-cw1-Materials',
        'layout_authority': 'User-supplied Mac report PDF, nine pages, attachment -4',
        'scope': 'Artwork addendum only; current Mac report source is preserved',
        'figure_1': 'Retain verified native SpaceClaim picture pixels',
        'scientific_layers': 'Native Fluent Save Picture PNG; embedded losslessly',
        'post_export_layers': 'Vector typography, axes, numerical legend labels and factual annotations',
        'case_5_vector_sampling': {'requested': 540, 'solid_excluded': 36,
                                   'fluid_exported': 504, 'rakes': 12},
        'solution_iterations_performed': False,
        'latex_compiled': False,
        'final_overleaf_report_layout_checked': False,
        'independent_acceptance': record(acceptance_path),
        'artwork': assets,
        'additional_assets': [record(p) for p in sorted(DELIVERY.glob('*.png'))],
        'historical_diagnostics': 'Raw diagnostic variants remain preserved in the solver folder; only listed artwork is selected',
    }
    manifest_path = DELIVERY / 'native_artwork_delivery_manifest.json'
    manifest_path.write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')

    folders = ('solver/native_figures_2026-11-10', 'data/native_figures_2026-11-10',
               'review/native_figures_2026-11-10', 'report/native_fluent_2026-11-10')
    for relative in folders:
        for parent, directories, filenames in os.walk(ROOT / relative, followlinks=False):
            directories[:] = [d for d in directories if d not in EXCLUDE
                              and not (Path(parent) / d).is_symlink()
                              and not (Path(parent) / d).is_junction()]
            for name in filenames:
                source = Path(parent) / name
                if source.suffix != '.pyc' and not source.is_symlink():
                    copy_checked(source)
    for relative in ('README.md', 'MAC_HANDOFF.md',
                     'coordination/NATIVE_FIGURE_MAC_FINDINGS.md',
                     'coordination/prepare_native_graphics_delivery.py'):
        copy_checked(ROOT / relative)

    # Refresh the inventory for all bytes in the populated repository, including preserved history.
    old_inventory = json.loads((TARGET / 'repository_file_manifest.json').read_text(encoding='utf-8-sig'))
    inventory = []
    for parent, directories, filenames in os.walk(TARGET, followlinks=False):
        directories[:] = [d for d in directories if d not in EXCLUDE]
        for name in filenames:
            path = Path(parent) / name
            if path != TARGET / 'repository_file_manifest.json':
                inventory.append(record(path, TARGET))
    old_inventory['files'] = sorted(inventory, key=lambda item: item['path'])
    old_inventory['native_artwork_addendum'] = manifest_path.relative_to(ROOT).as_posix()
    (TARGET / 'repository_file_manifest.json').write_text(
        json.dumps(old_inventory, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'artwork': assets, 'repository_files': len(inventory),
                      'repository_MiB': sum(item['bytes'] for item in inventory) / 1024**2}, indent=2))


if __name__ == '__main__':
    main()
