#!/usr/bin/env python3
"""Build isolated output directories from source-faithful manuscript entry points."""
from pathlib import Path
import argparse,json,os,subprocess,shutil,sys,re,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from current_publication import configuration, source_epoch
ROOT=Path(__file__).resolve().parents[1]
DOCS=[d for d in json.loads((ROOT/'publication/documents.json').read_text()) if d['kind']!='essay']
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--edition-date',help='ISO edition date for the deterministic TeX timestamp')
parser.add_argument('documents',nargs='*',help='Reader filenames or a document family')
args=parser.parse_args();_,edition_day=configuration(edition_date=args.edition_date)
selected=set(args.documents);DOCS=[d for d in DOCS if not selected or d['file_name'] in selected or d['family'] in selected]
if not DOCS:raise SystemExit('No document matches the requested selection')
BUILD=ROOT/'publication/build';BUILD.mkdir(exist_ok=True)
def build(d):
 t0=time.time();directory=d['source_directory'] if 'source_directory' in d else str(Path(d['root']).relative_to(ROOT));main=ROOT/directory/d['main'];key=Path(d['file_name']).stem;out=BUILD/key;out.mkdir(exist_ok=True)
 env=dict(os.environ);env['SOURCE_DATE_EPOCH']=source_epoch(edition_day);env['FORCE_SOURCE_DATE']='1';env['TEXINPUTS']=str(out)+os.pathsep+str(ROOT/'publication/house_style')+os.pathsep+env.get('TEXINPUTS','')
 env['BIBINPUTS']=str(main.parent)+os.pathsep+env.get('BIBINPUTS','');env['BSTINPUTS']=str(main.parent)+os.pathsep+env.get('BSTINPUTS','')
 cmd=['xelatex','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder','-output-directory='+str(out),'-jobname='+key,main.name]
 logs=[];status='failed';errors=[]
 for n in range(6):
  run=subprocess.run(cmd,cwd=main.parent,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=600);txt=run.stdout.decode(errors='replace');logs.append(txt)
  if run.returncode:
   errors=txt.splitlines()[-22:];break
  if n==0:
   aux=out/(key+'.aux')
   if aux.exists() and r'\bibdata' in aux.read_text(errors='replace'):
    bib=subprocess.run(['bibtex',key],cwd=out,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
    logs.append(bib.stdout.decode(errors='replace'))
    if bib.returncode:errors=bib.stdout.decode(errors='replace').splitlines()[-15:];break
  if n>=3 and not re.search(r'(Rerun to get cross-references right|Label\(s\) may have changed|Rerun to get outlines right)',txt):
   status='passed';break
 (out/'build_transcript.txt').write_text('\n'.join(logs))
 pdf=out/(key+'.pdf');warnings=[]
 if status=='passed':
  (ROOT/'publication/pdfs').mkdir(exist_ok=True)
  shutil.copy2(pdf,ROOT/'publication/pdfs'/d['file_name'])
  import fitz
  with fitz.open(pdf) as f:pages=len(f)
  log=(out/(key+'.log')).read_text(errors='replace')
  warnings=[l for l in log.splitlines() if re.search('Warning:|Overfull|Missing character',l)]
 else:pages=None
 return {'file_name':d['file_name'],'status':status,'edition_date':edition_day.isoformat(),'source_date_epoch':source_epoch(edition_day),'pages':pages,'seconds':round(time.time()-t0,1),'errors':errors,'warnings':warnings,'build_directory':str(out)}
results=[]
priorfile=ROOT/'publication/build_results.json';prior=json.loads(priorfile.read_text()) if priorfile.exists() else []
with ThreadPoolExecutor(max_workers=4) as pool:
 futures={pool.submit(build,d):d for d in DOCS}
 for f in as_completed(futures):
  try:r=f.result()
  except Exception as e:r={'file_name':futures[f]['file_name'],'status':'failed','errors':[repr(e)]}
  results.append(r);print(json.dumps({k:r.get(k) for k in ['file_name','status','pages','seconds','errors'] if r.get(k)}),flush=True)
  merged=[x for x in prior if x['file_name'] not in {y['file_name'] for y in results}]+results
  priorfile.write_text(json.dumps(merged,indent=2))
print('completed',len(results),'passed',sum(r['status']=='passed' for r in results),flush=True)
if any(r['status']!='passed' for r in results):raise SystemExit(1)
