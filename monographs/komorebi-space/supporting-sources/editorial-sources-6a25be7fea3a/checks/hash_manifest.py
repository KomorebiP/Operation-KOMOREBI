#!/usr/bin/env python3
"""Hash the publication payload, excluding self-reference and disposable caches."""
from pathlib import Path
import hashlib
ROOT=Path(__file__).resolve().parents[1]
rows=[]
for p in sorted(ROOT.rglob('*')):
    if not p.is_file() or '__pycache__' in p.parts or p.name=='SHA256SUMS.txt':continue
    if p.suffix in {'.aux','.out','.toc','.fls','.fdb_latexmk'}:continue
    rows.append(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p.relative_to(ROOT)))
(ROOT/'SHA256SUMS.txt').write_text('\n'.join(rows)+'\n')
print(f'Hashed {len(rows)} payload files.')
