"""Copy the complete coursework tree into its empty Git checkout, preserving bytes."""
from pathlib import Path
import hashlib
import json
import os
import shutil

ROOT = Path(__file__).resolve().parent.parent
TARGET = Path(r'D:\CFD_WorkScratch\MMME3086-cw1-Materials')
FOLDERS = ('coordination', 'inputs', 'solver', 'data', 'review', 'report', 'outputs')
EXCLUDED = {'node_modules', '__pycache__', '.git', '.venv', '.pytest_cache'}


def digest(path):
    hasher = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


def main():
    if not (TARGET / '.git').is_dir():
        raise RuntimeError('The verified repository checkout is missing')
    if any(path.name != '.git' for path in TARGET.iterdir()):
        raise RuntimeError('Refuse to overwrite a populated checkout')
    records = []

    def copy(source):
        relative = source.relative_to(ROOT)
        destination = TARGET / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        original_hash = digest(source)
        if digest(destination) != original_hash:
            raise RuntimeError(f'Copy mismatch: {relative}')
        records.append({'path': relative.as_posix(), 'bytes': source.stat().st_size,
                        'sha256': original_hash})

    for folder in FOLDERS:
        for parent, directories, files in os.walk(ROOT / folder, followlinks=False):
            directories[:] = [name for name in directories if name not in EXCLUDED
                              and not (Path(parent) / name).is_symlink()
                              and not (Path(parent) / name).is_junction()]
            for name in files:
                source = Path(parent) / name
                if not source.is_symlink():
                    copy(source)
    for name in ('README.md', 'MAC_HANDOFF.md', '.gitignore', '.gitattributes'):
        copy(ROOT / name)
    for source in sorted(ROOT.glob('*.trn')):
        copy(source)
    manifest = {'scope': 'Complete coursework directories, native root transcripts and handoff documents',
                'byte_preservation': 'Every copied file SHA256 matched its source; Git text conversion disabled',
                'excluded_directories': sorted(EXCLUDED),
                'symlinks_and_junctions_followed': False,
                'repository': 'https://github.com/Lufthansa744/MMME3086-cw1-Materials',
                'latex_compiled': False, 'final_report_rendered_layout_verified': False,
                'files': sorted(records, key=lambda record: record['path'])}
    (TARGET / 'repository_file_manifest.json').write_text(
        json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(f'Copied and hash-verified {len(records)} files; '
          f'{sum(record["bytes"] for record in records) / 1024**2:.1f} MiB')


if __name__ == '__main__':
    main()
