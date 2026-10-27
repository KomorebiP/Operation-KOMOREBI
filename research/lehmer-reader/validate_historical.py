"""Check that every recovered original byte remains unchanged."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parent
rows = json.loads((ROOT / 'evidence/historical_inputs.json').read_text())
records = []
for row in rows:
    archive_path = ROOT / 'historical' / row['name']
    actual_hash = hashlib.sha256(archive_path.read_bytes()).hexdigest()
    assert actual_hash == row['sha256'], archive_path
    extracted = archive_path.with_suffix('')
    with zipfile.ZipFile(archive_path) as archive:
        checked = 0
        for info in archive.infolist():
            if info.is_dir():
                continue
            member = Path(info.filename)
            assert not member.is_absolute() and '..' not in member.parts
            payload = archive.read(info)
            local = extracted / member
            assert local.is_file(), local
            assert local.read_bytes() == payload, local
            checked += 1
    records.append({'archive': row['name'], 'sha256': actual_hash,
                    'original_file_members_unchanged': checked})
record = {'status': 'passed', 'archives': records,
          'scope': 'All original archive bytes and every original extracted file member. Interpreter caches are not original members.'}
(ROOT / 'evidence/HISTORICAL_INTEGRITY.json').write_text(json.dumps(record, indent=2) + '\n')
print(json.dumps(record, indent=2))
