#!/usr/bin/env python3
"""Build the editable Paper XI Lean guide. No Lean compiler is invoked."""
import argparse,hashlib,json,os,shutil,subprocess,tempfile
from pathlib import Path
R=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--output-dir',type=Path,required=True);a=ap.parse_args();out=a.output_dir.resolve()
if out.exists() and any(out.iterdir()):raise SystemExit('Output directory must be new or empty.')
out.mkdir(parents=True,exist_ok=True)
with tempfile.TemporaryDirectory(prefix='paperxi-lean-guide-') as td:
 t=Path(td)
 for p in R.glob('*.tex'):shutil.copy2(p,t/p.name)
 shutil.copytree(R/'excerpts',t/'excerpts')
 env=os.environ.copy();env.update(SOURCE_DATE_EPOCH='1791244800',FORCE_SOURCE_DATE='1',TZ='UTC')
 logs=[];n='Paper_XI_Lean_Guide_Final'
 for i in range(3):
  q=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error',n+'.tex'],cwd=t,env=env,capture_output=True,text=True)
  logs.append(q.stdout+q.stderr)
  if q.returncode:(out/'BUILD_FAILED.log').write_text(logs[-1]);raise SystemExit('XeLaTeX failed; inspect BUILD_FAILED.log')
 for ext in ['pdf','aux','log','toc','out']:
  p=t/(n+'.'+ext)
  if p.exists():shutil.copy2(p,out/p.name)
 (out/'BUILD_STDOUT.log').write_text('\n'.join(logs))
 p=out/(n+'.pdf');(out/'BUILD.json').write_text(json.dumps({'status':'PASS','engine':'xelatex','passes':3,'source_date_epoch':1791244800,'pdf_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size,'lean_compilation_performed':False},indent=2)+'\n')
 print(p)
