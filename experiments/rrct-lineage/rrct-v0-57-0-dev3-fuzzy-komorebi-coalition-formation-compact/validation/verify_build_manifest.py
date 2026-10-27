from __future__ import annotations
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
EXCLUDED={'V0_57_BUILD_SHA256SUMS.txt','V0_57_BUILD_SHA256SUMS.txt.sha256'}

def sha(path:pathlib.Path)->str:
 h=hashlib.sha256()
 with path.open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()

def current_files()->set[str]:
 output=set()
 for p in ROOT.rglob('*'):
  if not p.is_file():continue
  rel=p.relative_to(ROOT).as_posix()
  if rel in EXCLUDED:continue
  if any(part in {'__pycache__','.pytest_cache','build'} or part.endswith('.egg-info') for part in p.relative_to(ROOT).parts):continue
  if p.suffix in {'.pyc','.pyo'}:continue
  output.add(rel)
 return output
manifest=ROOT/'V0_57_BUILD_SHA256SUMS.txt'
entries={}
duplicates=False
for line in manifest.read_text().splitlines():
 if not line.strip():continue
 digest,rel=line.split('  ',1)
 duplicates=duplicates or rel in entries
 entries[rel]=digest
checks={
 'companion':(manifest.with_suffix(manifest.suffix+'.sha256').read_text().split()[0]==sha(manifest)),
 'no_duplicates':not duplicates,
 'exact_file_set':set(entries)==current_files(),
 'all_digests':all((ROOT/rel).is_file() and sha(ROOT/rel)==digest for rel,digest in entries.items()),
}
failed=sorted(k for k,v in checks.items() if not v)
print(json.dumps({'schema':'rrct.v057.build_manifest_audit.v1','entry_count':len(entries),'failed_checks':failed,'all_checks_pass':not failed,'manifest_sha256':sha(manifest)},indent=2,sort_keys=True))
raise SystemExit(0 if not failed else 1)
