"""Check all recovered Catalan audit bytes against the recovery record."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parent
rows = json.loads((ROOT / "evidence/historical_inputs.json").read_text())
records = []
for row in rows:
    path = ROOT / "historical" / row["name"]
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    assert actual == row["sha256"], path
    assert path.stat().st_size == row["bytes"], path
    records.append(dict(row, preserved=True))
assert len(records) == 3
out = {"status": "passed", "files": records,
       "scope": "The three recovered original audit files are byte identical. New exposition and computations are separate."}
(ROOT / "evidence/HISTORICAL_INTEGRITY.json").write_text(json.dumps(out, indent=2)+"\n")
print(json.dumps(out, indent=2))

