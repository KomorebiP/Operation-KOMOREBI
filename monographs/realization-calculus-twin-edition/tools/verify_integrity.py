#!/usr/bin/env python3
"""Check every delivered file against the twin edition SHA-256 manifest."""
from hashlib import sha256
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
failures=[];checked=0
for line in (ROOT/'SHA256SUMS').read_text().splitlines():
 expected,name=line.split('  ',1);relative=Path(name)
 if relative.is_absolute() or '..' in relative.parts:failures.append(name+': invalid path');continue
 path=ROOT/relative
 if not path.is_file():failures.append(name+': missing');continue
 if sha256(path.read_bytes()).hexdigest()!=expected:failures.append(name+': digest mismatch')
 checked+=1
if failures:print('\n'.join(failures),file=sys.stderr);raise SystemExit(1)
print(f'PASS: {checked} manifest entries match.')
