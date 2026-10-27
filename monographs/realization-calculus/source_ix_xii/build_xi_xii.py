from pathlib import Path
import subprocess,os,shutil,json,re,concurrent.futures,fitz
R=Path(__file__).resolve().parent
E=dict(os.environ,TMPDIR=str(R),SOURCE_DATE_EPOCH='1792540800',FORCE_SOURCE_DATE='1',TZ='UTC',PYTHONDONTWRITEBYTECODE='1')
def one(k,role):
 out=R/(k+'_build');out.mkdir(exist_ok=True)
 if k=='XI':
  cmd=['python3','-B',str(R/k/'tools/build_readers.py'),'--output',str(out),'--stage',role]
  q=subprocess.run(cmd,env=E,capture_output=True,text=True,timeout=600)
  (out/(role+'.build_driver.log')).write_text(q.stdout+q.stderr)
  return {'paper':k,'role':role,'status':'passed' if q.returncode==0 else 'failed','returncode':q.returncode,'tail':q.stdout[-1200:]+q.stderr[-1200:] if q.returncode else ''}
 work=out/role;shutil.copytree(R/k/'publication/source'/role,work,dirs_exist_ok=True)
 stem=f'Paper_{k}_{"Traditional" if role=="traditional" else "Visual_Guide" if role=="visual_guide" else "Lean_Guide"}_Final'
 for s in ['.aux','.out','.toc','.log','.blg']:(work/(stem+s)).unlink(missing_ok=True)
 eng='xelatex' if role=='lean_guide' else 'pdflatex'
 cmd=[eng,'-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder',stem+'.tex']
 runs=[]
 for i in range(3):
  q=subprocess.run(cmd,cwd=work,env=E,capture_output=True,text=True,timeout=200);(work/f'pass{i+1}.stdout.log').write_text(q.stdout+q.stderr);runs.append(q.returncode)
  if q.returncode:return {'paper':k,'role':role,'status':'failed','runs':runs,'tail':q.stdout[-2000:]}
  if i==0 and role=='traditional':
   bib=next(c for c in ['bibtex','bibtex.original','bibtex8'] if shutil.which(c) and subprocess.run([c,'--version'],capture_output=True).returncode==0)
   q=subprocess.run([bib,stem],cwd=work,env=E,capture_output=True,text=True,timeout=60);(work/'bibliography.stdout.log').write_text(q.stdout+q.stderr)
   if q.returncode:return {'paper':k,'role':role,'status':'failed','runs':runs,'tail':q.stdout[-2000:]}
 log=(work/(stem+'.log')).read_text(errors='replace');warnings=[s for s in log.splitlines() if any(t in s for t in ['Warning:','Overfull','Missing character','Underfull'])]
 return {'paper':k,'role':role,'status':'passed','runs':runs,'pages':len(fitz.open(work/(stem+'.pdf'))),'warnings':warnings}
rows=[]
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 fs=[ex.submit(one,k,r) for k in ['XI','XII'] for r in ['traditional','visual_guide','lean_guide']]
 for f in concurrent.futures.as_completed(fs):
  x=f.result();rows.append(x);print(json.dumps(x),flush=True);(R/'BUILD_XI_XII.json').write_text(json.dumps(rows,indent=2))
