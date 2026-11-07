"""Read only the native mesh ASCII header and zone records, preserving binary data."""
from pathlib import Path
import hashlib
import json
import re

root = Path(__file__).resolve().parent.parent
path = root / 'inputs' / 'Aerofoil8-degAoA-enhancedBL.msh'
blob = path.read_bytes()
result = {'path': str(path), 'bytes': len(blob), 'sha256': hashlib.sha256(blob).hexdigest(),
          'counts': {}, 'zones': [],
          'limitation': 'Header counts and zone declarations only; not a solver import, quality check, boundary-value read or solved result.'}
for typ, name in [(10, 'nodes'), (12, 'cells'), (13, 'faces')]:
    match = re.search(rb'\(' + str(typ).encode() + rb' \(0 1 ([0-9a-fA-F]+) 0\)\)', blob[:600])
    if not match:
        raise ValueError('Missing global header for ' + name)
    result['counts'][name] = int(match.group(1), 16)
for match in re.finditer(rb'\(45 \((\d+) ([a-z-]+) ([a-zA-Z0-9_-]+)\)\(\)\)', blob):
    result['zones'].append({'zone_id_as_written': match.group(1).decode(),
                            'type': match.group(2).decode(), 'name': match.group(3).decode(),
                            'byte_offset': match.start()})
target = Path(__file__).parent / 'enhanced_header_audit.json'
target.write_text(json.dumps(result, indent=2), encoding='utf-8')
print(target)
