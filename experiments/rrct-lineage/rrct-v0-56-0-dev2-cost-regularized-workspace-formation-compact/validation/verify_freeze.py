from __future__ import annotations
import hashlib,json,pathlib
ROOT=pathlib.Path(__file__).resolve().parents[1]
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 m=ROOT/'validation/PREOUTCOME_FREEZE.json'; x=json.loads(m.read_text()); bad=[]
 for r in x['files']:
  p=ROOT/r['relative_path']
  if not p.is_file() or p.stat().st_size!=r['size_bytes'] or sha(p)!=r['sha256']: bad.append(r['relative_path'])
 ok=not bad and m.with_suffix(m.suffix+'.sha256').read_text().split()[0]==sha(m); print(json.dumps({'all_checks_pass':ok,'file_count':len(x['files']),'failed':bad,'manifest_sha256':sha(m)},sort_keys=True)); return 0 if ok else 1
if __name__=='__main__': raise SystemExit(main())
