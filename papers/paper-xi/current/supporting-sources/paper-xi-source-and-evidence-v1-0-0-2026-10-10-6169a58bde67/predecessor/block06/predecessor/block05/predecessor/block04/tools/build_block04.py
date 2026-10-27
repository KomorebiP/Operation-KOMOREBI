#!/usr/bin/env python3
"""Build the independently editable Part III. Requires XeLaTeX and installed fonts."""
from __future__ import annotations
import argparse,json,os,shutil,subprocess,time
from pathlib import Path

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
 root=Path(__file__).resolve().parents[1];src=root/'publication/source/Paper_XI_Conjecture66_Block04.tex'
 out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
 engine=shutil.which('xelatex')
 if not engine:raise SystemExit('XeLaTeX was not found. The supplied PDFs do not require rebuilding.')
 env=dict(os.environ,TEXINPUTS=str(src.parent)+os.pathsep,SOURCE_DATE_EPOCH='1791648000',FORCE_SOURCE_DATE='1')
 # Remove only auxiliary files for this target, never source or preserved evidence.
 for ext in ['aux','toc','out','log']:
  (out/(src.stem+'.'+ext)).unlink(missing_ok=True)
 records=[]
 for i in range(3):
  start=time.monotonic();cmd=[engine,'-interaction=nonstopmode','-halt-on-error','-output-directory='+str(out),str(src)]
  r=subprocess.run(cmd,cwd=src.parent,env=env,capture_output=True,text=True,timeout=120)
  (out/f'build_{i+1}.txt').write_text(r.stdout+r.stderr)
  records.append({'pass':i+1,'exit_code':r.returncode,'seconds':round(time.monotonic()-start,3)})
  if r.returncode:raise SystemExit(f'Build pass {i+1} failed; see {out}/build_{i+1}.txt')
 log=(out/(src.stem+'.log')).read_text(errors='replace')
 diagnostics=[x for x in log.splitlines() if any(k in x for k in ['Warning:','Overfull','Underfull','Missing character'])]
 rec={'status':'passed','passes':records,'final_diagnostics':diagnostics,'output_pdf':str(out/(src.stem+'.pdf'))}
 (out/'BUILD_RECORD.json').write_text(json.dumps(rec,indent=2)+'\n');print(json.dumps(rec,indent=2))
if __name__=='__main__':main()
