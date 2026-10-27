from pathlib import Path
import json,subprocess,os,shutil,concurrent.futures
ROOT=Path(__file__).resolve().parent;WORK=ROOT.parent
records=json.loads((ROOT/'BUILD_RESULTS_FINAL.json').read_text());todo=[r for r in records if r['role']!='lean_guide']
def build(rec):
 cwd=Path(rec['source']).parent;stem=rec['stem'];out=Path(rec['compiled_directory']);env=dict(os.environ,TMPDIR=str(WORK),SOURCE_DATE_EPOCH='1792540800',FORCE_SOURCE_DATE='1',TEXINPUTS=str(cwd)+os.pathsep)
 command=['xelatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder','-output-directory='+str(out),stem+'.tex'];runs=[]
 for i in range(1,5):
  run=subprocess.run(command,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/f'pass_{i}.txt').write_text(run.stdout);runs.append({'pass':i,'returncode':run.returncode})
  if run.returncode:break
  if i==1 and r'\bibdata' in (out/(stem+'.aux')).read_text():
   b=subprocess.run(['bibtex',stem],cwd=out,env=dict(env,BIBINPUTS=str(cwd)+os.pathsep,BSTINPUTS=str(cwd)+os.pathsep),text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/'bibtex.txt').write_text(b.stdout);runs.append({'bibtex':b.returncode})
   if b.returncode:break
 rec.update(runs=runs,success=not any(x.get('returncode',x.get('bibtex',0)) for x in runs));print(rec['paper'],rec['role'],rec['success'],flush=True);return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:revised=list(ex.map(build,todo))
new={(r['paper'],r['role']):r for r in revised};records=[new.get((r['paper'],r['role']),r) for r in records];(ROOT/'BUILD_RESULTS_FINAL.json').write_text(json.dumps(records,indent=2))
