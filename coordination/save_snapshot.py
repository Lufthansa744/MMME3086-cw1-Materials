"""Copy coursework evidence without following runtime junctions or modifying sources."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import shutil

ROOT = Path(__file__).resolve().parent.parent
CLOUD = Path(r'D:\iCloud\iCloudDrive\iCloudDrive\Documents\Codex\MMME3086 cw1 (Windows)')
EXCLUDED = {'node_modules', '__pycache__', '.git', '.venv'}

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('name')
    args = parser.parse_args()
    if Path(args.name).name != args.name or args.name in {'.', '..'}:
        raise ValueError('Snapshot name must be a single directory name')
    destination = CLOUD / args.name
    if destination.exists():
        raise ValueError('Preserve existing snapshots; choose a new name')
    destination.mkdir()
    records = []
    for folder in ('coordination', 'inputs', 'solver', 'data', 'review', 'report', 'outputs'):
        base = ROOT / folder
        if not base.is_dir():
            continue
        for parent, directories, files in os.walk(base, followlinks=False):
            directories[:] = [name for name in directories if name not in EXCLUDED
                              and not (Path(parent)/name).is_junction()
                              and not (Path(parent)/name).is_symlink()]
            for name in files:
                source = Path(parent)/name
                if source.is_symlink():
                    continue
                relative = source.relative_to(ROOT)
                target = destination/relative
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, target)
                records.append({'path':relative.as_posix(), 'bytes':target.stat().st_size,
                                'snapshot_sha256':digest(target)})
    (destination/'snapshot-manifest.json').write_text(json.dumps({
        'source_workspace':str(ROOT), 'excluded_directories':sorted(EXCLUDED),
        'policy':'Files copied without following symlinks/junctions. Live logs may be earlier prefixes; source files remain authoritative.',
        'files':records}, indent=2), encoding='utf-8')
    print(f'{len(records)} files copied to {destination}')

if __name__ == '__main__':
    main()
