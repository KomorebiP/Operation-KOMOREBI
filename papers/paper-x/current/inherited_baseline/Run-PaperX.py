#!/usr/bin/env python3
"""Inspect and rebuild Paper X's source-and-evidence edition. No automatic installation.

verify uses only the standard library. Other commands need the dependencies listed
in requirements.txt. No command here invokes Lean or downloads a runtime.
"""
from __future__ import annotations
import argparse,hashlib,json,os,shutil,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
PROTECTED=('original_companion','original_releases','current_continuation','manuscript','visual_appendix','reading_editions','editorial_evidence','tools')
def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  while block:=f.read(1024*1024):h.update(block)
 return h.hexdigest()
def output_path(p):
 out=p.resolve()
 if out==ROOT or any(out==ROOT/t or ROOT/t in out.parents for t in PROTECTED):raise ValueError('Choose an output outside the preserved trees.')
 if out.exists() and any(out.iterdir()):raise ValueError('Output directory must be new or empty.')
 return out
def verify():
 manifest=json.loads((ROOT/'MANIFEST.json').read_text());bad=[]
 for name,record in manifest['files'].items():
  p=ROOT/name
  if not p.is_file() or p.stat().st_size!=record['bytes'] or sha(p)!=record['sha256']:bad.append(name)
 if bad:raise RuntimeError('Integrity failed for '+repr(bad[:12]))
 upstream=json.loads((ROOT/'editorial_evidence/UPSTREAM_HASHES.json').read_text())
 if any(sha(ROOT/k)!=v for k,v in upstream.items()):raise RuntimeError('An upstream file changed.')
 print(f"PASS: {len(manifest['files'])} manifest files; {len(upstream)} preserved upstream files. No compiler invoked.")
def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('command',choices=['verify','examples','appendix','original','manuscript','saved-evidence']);ap.add_argument('--output-dir',type=Path);a=ap.parse_args()
 env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
 if a.command=='verify':verify();return
 if a.command=='saved-evidence':subprocess.run([sys.executable,str(ROOT/'tools/verify_saved_evidence.py')],check=True,env=env);return
 out=output_path(a.output_dir or ROOT/('rebuild_'+a.command))
 if a.command=='examples':
  out.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(prefix='paper_x_checks_') as td:
   w=Path(td);shutil.copytree(ROOT/'visual_appendix/source',w/'source',ignore=shutil.ignore_patterns('__pycache__'));shutil.copytree(ROOT/'visual_appendix/checks',w/'checks')
   with (out/'examples.log').open('w') as f:r=subprocess.run([sys.executable,'-W','error',str(w/'checks/verify_examples.py')],cwd=w,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   if r.returncode:raise RuntimeError('Exact checks failed; see '+str(out/'examples.log'))
   shutil.copy2(w/'checks/EXACT_CHECKS.json',out/'EXACT_CHECKS.json')
   print((out/'examples.log').read_text(),end='')
  return
 script={'appendix':'visual_appendix/build.py','original':'tools/replay_original.py','manuscript':'tools/rebuild_manuscript.py'}[a.command]
 subprocess.run([sys.executable,str(ROOT/script),'--output-dir',str(out)],check=True,env=env)
if __name__=='__main__':
 try:main()
 except (OSError,ValueError,RuntimeError,subprocess.SubprocessError) as e:raise SystemExit(str(e)) from e
