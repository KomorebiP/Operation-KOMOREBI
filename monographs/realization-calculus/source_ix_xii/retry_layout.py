from pathlib import Path
import concurrent.futures,subprocess,json,os,re,fitz
r=Path(__file__).resolve().parent
def run(k,role):
 w=r/(k+'_build')/('build' if k=='XI' else '')/role
 stem=f'Paper_{k}_{"Visual_Guide" if role=="visual_guide" else "Lean_Guide"}_Final'
 eng='pdflatex' if role=='visual_guide' else 'xelatex';runs=[]
 for i in range(3):
  q=subprocess.run([eng,'-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder',stem+'.tex'],cwd=w,env=dict(os.environ,TMPDIR=str(r),SOURCE_DATE_EPOCH='1792540800',FORCE_SOURCE_DATE='1',TZ='UTC'),capture_output=True,text=True,timeout=200)
  (w/f'layout_retry_pass{i+1}.log').write_text(q.stdout+q.stderr);runs.append(q.returncode)
  if q.returncode:return {'paper':k,'role':role,'passed':False,'tail':q.stdout[-1500:]}
 log=(w/(stem+'.log')).read_text(errors='replace');diags=[s for s in log.splitlines() if any(t in s for t in ['Warning:','Overfull','Underfull','Missing character'])]
 return {'paper':k,'role':role,'passed':True,'pages':len(fitz.open(w/(stem+'.pdf'))),'diagnostics':diags}
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 rows=list(ex.map(lambda x:run(*x),[('XI','visual_guide'),('XII','visual_guide'),('XII','lean_guide')]))
(r/'LAYOUT_RETRIES.json').write_text(json.dumps(rows,indent=2));print(json.dumps(rows,indent=2))
