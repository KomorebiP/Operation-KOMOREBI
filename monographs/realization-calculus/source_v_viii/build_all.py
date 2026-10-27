#!/usr/bin/env python3
"""Rebuild the twelve V-VIII typography components. No scientific generators run.

Requires XeLaTeX/BibTeX, installed URW Base35, Latin Modern, and DejaVu fonts.
The font payloads are external dependencies and are not distributed here.
"""
from pathlib import Path
import argparse,concurrent.futures,hashlib,json,os,shutil,subprocess
ROOT=Path(__file__).resolve().parent
P=argparse.ArgumentParser(description=__doc__)
P.add_argument('--jobs',type=int,default=2)
ARGS=P.parse_args()
TASKS=[(number,role,'Paper_'+number+'_'+name+'_Final') for number in ['V','VI','VII','VIII'] for role,name in [('traditional','Traditional'),('visual_guide','Visual_Guide'),('lean_guide','Lean_Guide')]]
def build(task):
 number,role,stem=task;cwd=ROOT/number/'editable'/role;out=ROOT/'compiled'/number/role;out.mkdir(parents=True,exist_ok=True)
 fonts=json.loads((cwd/'MONOGRAPH_FONT_DEPENDENCIES.json').read_text());target=cwd/'fonts';target.mkdir(exist_ok=True);resolved=[]
 for item in fonts:
  name=item['name'];found=subprocess.check_output(['kpsewhich',name],text=True).strip();p=Path(found)
  if not found or not p.is_file():raise RuntimeError('Install external font: '+name)
  digest=hashlib.sha256(p.read_bytes()).hexdigest()
  if digest!=item['sha256']:raise RuntimeError('External font version differs: '+name)
  dst=target/name
  if dst.is_symlink():dst.unlink()
  shutil.copyfile(p,dst);resolved.append({'name':name,'sha256':digest})
 env=dict(os.environ,SOURCE_DATE_EPOCH='1792540800',FORCE_SOURCE_DATE='1',TEXINPUTS=str(cwd)+os.pathsep)
 command=['xelatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder','-output-directory='+str(out),stem+'.tex']
 runs=[]
 for i in range(1,5):
  run=subprocess.run(command,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/f'pass_{i}.txt').write_text(run.stdout);runs.append(run.returncode)
  if run.returncode:break
  if i==1 and r'\bibdata' in (out/(stem+'.aux')).read_text():
   b=subprocess.run(['bibtex',stem],cwd=out,env=dict(env,BIBINPUTS=str(cwd)+os.pathsep,BSTINPUTS=str(cwd)+os.pathsep),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/'bibtex.txt').write_text(b.stdout);runs.append(b.returncode)
   if b.returncode:break
 log=(out/(stem+'.log')).read_text(errors='replace') if (out/(stem+'.log')).exists() else ''
 hard=[x for x in log.splitlines() if any(s in x for s in ['Missing character:', 'undefined references','undefined citations','undefined on input','Overfull'])]
 result={'paper':number,'role':role,'commands_returncodes':runs,'success':not any(runs) and not hard,'hard_diagnostics':hard,'fonts':resolved,'output_pdf':str((out/(stem+'.pdf')).relative_to(ROOT))}
 print(number,role,'PASS' if result['success'] else 'FAIL',flush=True);return result
with concurrent.futures.ThreadPoolExecutor(max_workers=max(1,ARGS.jobs)) as ex:results=list(ex.map(build,TASKS))
(ROOT/'REBUILD_RESULT.json').write_text(json.dumps(results,indent=2))
raise SystemExit(0 if all(x['success'] for x in results) else 1)
