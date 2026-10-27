from pathlib import Path
import subprocess,concurrent.futures,json,time,sys
P=Path(__file__).resolve().parent;S=P/'source';B=P/'compiled';B.mkdir(exist_ok=True);(P/'audit').mkdir(exist_ok=True)
roots=[(f,'xelatex') for f in sorted((S/'monographs').glob('Physics_*.tex')) if 'Collection_Guide' not in f.name]
roots.extend([(S/'generator/Block50_Spectral_Generator_Bridge.tex','pdflatex'),(S/'backreaction/Projector_Refinement_Physics_Covariant_Backreaction_Bridge.tex','pdflatex'),(S/'cosmology/Projector_Refinement_Physics_Volume_II.tex','pdflatex')])
if len(sys.argv)>1:roots=[x for x in roots if any(k in x[0].name for k in sys.argv[1:])]
def build(item):
 f,engine=item;out=B/f.stem;out.mkdir(exist_ok=True);record={'source':str(f.relative_to(S)),'engine':engine,'passes':[]};start=time.time()
 for i in range(3):
  r=subprocess.run([engine,'-interaction=nonstopmode','-halt-on-error','-file-line-error',f'-output-directory={out}',f.name],cwd=f.parent,capture_output=True,text=True,timeout=120)
  (out/f'pass_{i+1}.txt').write_text(r.stdout+r.stderr);record['passes'].append({'returncode':r.returncode,'pass':i+1})
  if r.returncode:record['tail']=(r.stdout+r.stderr)[-2000:];break
 record['seconds']=round(time.time()-start,2);record['success']=len(record['passes'])==3 and all(x['returncode']==0 for x in record['passes']);return record
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 futures={ex.submit(build,item):item[0].name for item in roots};results=[]
 for f in concurrent.futures.as_completed(futures):
  try:r=f.result()
  except Exception as e:r={'source':futures[f],'error':str(e),'success':False}
  results.append(r);print(json.dumps(r),flush=True)
  (P/'audit/latex_build_results.json').write_text(json.dumps(results,indent=2))

if not all(r.get('success') for r in results):
 raise SystemExit(1)
