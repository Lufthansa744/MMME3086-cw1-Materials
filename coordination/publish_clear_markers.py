"""Publish the accepted prominent-marker revision with native RGB preserved."""
from pathlib import Path
import json
import os

from PIL import Image
from pypdf import PdfReader

from prepare_centered_native_graphics_delivery import (
    ROOT, TARGET, EXPECTED_MM, EXCLUDE, digest, record, copy_checked,
)

DELIVERY = ROOT / 'report/native_fluent_2026-11-10-clear-markers'
PREVIOUS = ROOT / 'report/native_fluent_2026-11-10-exact-cells'
AUDIT = ROOT / 'review/fig05_clear_markers_2026-11-10'
EXPECTED_CELLS = {7588, 7316, 69, 7251, 2573}


def main():
    if not (TARGET / '.git').is_dir():
        raise RuntimeError('Verified Git checkout missing')
    acceptance_path = AUDIT / 'final_acceptance.json'
    acceptance = json.loads(acceptance_path.read_text(encoding='utf-8-sig'))
    checked = acceptance['fig5']
    if (acceptance['overall'] != 'ACCEPT' or not checked['accepted']
            or set(checked['actual_selected_cell_ids']) != EXPECTED_CELLS
            or checked['false_positive_cells'] or checked['false_negative_cells']
            or not checked['native_scientific_RGB_unchanged']
            or not checked['five_non_crossing_leaders']
            or checked['marker_diameter_mm'] < 2.8 or checked['number_font_pt'] < 7.5):
        raise RuntimeError('Native source, identity or prominent-marker acceptance incomplete')

    artwork = []
    for name, expected in EXPECTED_MM.items():
        path = DELIVERY / name
        reader = PdfReader(path)
        if len(reader.pages) != 1:
            raise RuntimeError(f'Expected one artwork page: {name}')
        box = reader.pages[0].mediabox
        actual = [float(box.width) * 25.4 / 72, float(box.height) * 25.4 / 72]
        if any(abs(a-b) > .01 for a, b in zip(actual, expected)):
            raise RuntimeError(f'Wrong artwork size: {name}')
        item = record(path)
        if item['sha256'] != acceptance[f'fig{int(name[3:5])}']['sha256']:
            raise RuntimeError(f'Acceptance does not bind current PDF: {name}')
        item['physical_size_mm'] = actual
        artwork.append(item)
    for stem in ('fig02_mesh_bc', 'fig04_rsm_vectors', 'fig06_enhanced_combined'):
        for suffix in ('.pdf', '.png', '_print300.png'):
            if digest(DELIVERY/(stem+suffix)) != digest(PREVIOUS/(stem+suffix)):
                raise RuntimeError(f'Unrelated accepted asset changed: {stem+suffix}')

    native_path = ROOT / 'solver/native_figures_2026-11-10-centered/case03/yplus_native_context_centered.png'
    native = Image.open(native_path).convert('RGB')
    embedded = [item.image.convert('RGB') for item in PdfReader(DELIVERY/'fig05_rsm_yplus.pdf').pages[0].images]
    matches = [im for im in embedded if im.size == native.size and im.tobytes() == native.tobytes()]
    if len(matches) != 1:
        raise RuntimeError('Fluent-native RGB source not embedded unchanged exactly once')
    for item in acceptance['handoff_documents']:
        if not item['accepted'] or digest(Path(item['path'])) != item['sha256']:
            raise RuntimeError('Reviewed Mac instruction changed')

    manifest_path = DELIVERY / 'delivery_manifest.json'
    manifest = {
        'date': '2026-11-10',
        'scope': 'Increase Figure 5 identification visibility; retain original five cells and other figures',
        'repository': 'https://github.com/Lufthansa744/MMME3086-cw1-Materials',
        'marker_to_actual_cell_ID': checked['marker_to_cell_IDs'],
        'false_positive_cells': 0, 'false_negative_cells': 0,
        'native_scientific_source': record(native_path),
        'native_source_RGB_embedded_exactly_unchanged': True,
        'post_export_marks': 'Five filled red numbered circles with white digits and separate small-arrowhead leaders',
        'marker_diameter_mm': checked['marker_diameter_mm'],
        'number_font_pt': checked['number_font_pt'],
        'leader_width_pt': checked['leader_width_pt'],
        'actual_print_width_visibility_accepted': True,
        'previous_exact_cell_identity_retained': True,
        'thin_outline_presentation_superseded': True,
        'Fluent_started_for_this_update': False,
        'solution_or_physical_settings_changed': False,
        'latex_compiled': False, 'integrated_report_layout_checked': False,
        'independent_acceptance': record(acceptance_path),
        'artwork': artwork,
        'delivery_files': [record(p) for p in sorted(DELIVERY.iterdir())
                           if p.is_file() and p != manifest_path],
    }
    manifest_path.write_text(json.dumps(manifest, indent=2)+'\n', encoding='utf-8')
    for relative in ('data/fig05_clear_markers_2026-11-10',
                     'review/fig05_clear_markers_2026-11-10',
                     'report/native_fluent_2026-11-10-clear-markers'):
        for parent, directories, files in os.walk(ROOT/relative, followlinks=False):
            directories[:] = [d for d in directories if d not in EXCLUDE
                              and not (Path(parent)/d).is_symlink()
                              and not (Path(parent)/d).is_junction()]
            for name in files:
                path = Path(parent)/name
                if path.suffix != '.pyc' and not path.is_symlink():
                    copy_checked(path)
    for relative in ('README.md', 'MAC_HANDOFF.md', 'coordination/publish_clear_markers.py'):
        copy_checked(ROOT/relative)
    inventory_path = TARGET/'repository_file_manifest.json'
    inventory = json.loads(inventory_path.read_text(encoding='utf-8-sig'))
    files = []
    for parent, directories, names in os.walk(TARGET, followlinks=False):
        directories[:] = [d for d in directories if d not in EXCLUDE]
        for name in names:
            path = Path(parent)/name
            if path != inventory_path:
                files.append(record(path, TARGET))
    inventory['files'] = sorted(files, key=lambda item:item['path'])
    inventory['latest_native_artwork_addendum'] = manifest_path.relative_to(ROOT).as_posix()
    inventory_path.write_text(json.dumps(inventory, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'figure_5': artwork[2], 'native_RGB_exact': True,
                      'marker_diameter_mm': checked['marker_diameter_mm'],
                      'repository_payload_files': len(files)}, indent=2))


if __name__ == '__main__':
    main()
