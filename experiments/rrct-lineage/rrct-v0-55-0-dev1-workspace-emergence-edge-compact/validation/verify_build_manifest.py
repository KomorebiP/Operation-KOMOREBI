#!/usr/bin/env python3
from __future__ import annotations
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
MANIFEST=ROOT/'V0_55_BUILD_SHA256SUMS.txt'
COMPANION=MANIFEST.with_suffix(MANIFEST.suffix+'.sha256')
EXCLUDED={MANIFEST.relative_to(ROOT).as_posix(),COMPANION.relative_to(ROOT).as_posix()}

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()

def actual_files():
 out=set()
 for p in ROOT.rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(ROOT).as_posix()
  if rel in EXCLUDED:continue
  if '__pycache__' in p.parts or '.pytest_cache' in p.parts or p.suffix in {'.pyc','.pyo'}:continue
  out.add(rel)
 return out

def main():
 if not MANIFEST.is_file() or not COMPANION.is_file():raise RuntimeError('build manifest missing')
 lines=[x for x in MANIFEST.read_text().splitlines() if x.strip()];entries={};duplicate=False
 for line in lines:
  digest,rel=line.split('  ',1);duplicate=duplicate or rel in entries;entries[rel]=digest
 failed=[]
 if duplicate:failed.append('duplicate_entries')
 if set(entries)!=actual_files():failed.append('file_set_exact')
 for rel,digest in entries.items():
  p=ROOT/rel
  if not p.is_file() or sha(p)!=digest:failed.append(rel)
 companion=COMPANION.read_text().split()[0] if COMPANION.read_text().split() else ''
 if companion!=sha(MANIFEST):failed.append('manifest_companion')
 out={'schema':'rrct.v055.build_manifest_verification.v1','all_checks_pass':not failed,'entry_count':len(entries),'manifest_sha256':sha(MANIFEST),'failed':failed}
 print(json.dumps(out,indent=2,sort_keys=True));return 0 if not failed else 1
if __name__=='__main__':raise SystemExit(main())
