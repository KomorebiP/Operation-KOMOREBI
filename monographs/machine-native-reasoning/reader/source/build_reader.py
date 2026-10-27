#!/usr/bin/env python3
"""Build this reader and rerun its finite checks in a fresh temporary directory."""
from pathlib import Path
import argparse,hashlib,json,re,shutil,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parent

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def spans(text,pattern): return [m.group(0) for m in re.finditer(pattern,text,re.S)]

def preservation():
 original=(ROOT/'source_original/core_v0.2.tex').read_text();current=(ROOT/'book.tex').read_text()
 if hashlib.sha256(original.encode()).hexdigest()!='a15f192322357893c2bb9b2427aac2a02b0753e558b42c0460a6288006ddbe6b':
  raise RuntimeError('Original reviewed-core source identity mismatch')
 patterns={'inline_math':r'(?<!\\)\$(?!\$).*?(?<!\\)\$',
 'proofs':r'\\begin\{proof\}.*?\\end\{proof\}',
 'displays':r'(?<!\\)\\\[.*?\\\]|\\begin\{(?:equation\*?|align\*?|gather\*?)\}.*?\\end\{(?:equation\*?|align\*?|gather\*?)\}',
 'statements':r'\\begin\{(theorem|proposition|corollary|counterexample)\}.*?\\end\{\1\}'}
 result={}
 for name,pat in patterns.items():
  a=spans(original,pat);b=spans(current,pat)
  result[name]={'count_original':len(a),'count_reader':len(b),'identical':a==b,'original_sha256':hashlib.sha256('\n'.join(a).encode()).hexdigest(),'reader_sha256':hashlib.sha256('\n'.join(b).encode()).hexdigest()}
  if a!=b:raise RuntimeError(f'{name} changed')
 return result

def main():
 ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--out',type=Path,required=True);a=ap.parse_args();out=a.out.resolve()
 if out==ROOT or ROOT in out.parents:ap.error('Output must be outside this reader directory')
 if out.exists() and any(out.iterdir()):ap.error('Output directory must be new or empty')
 out.mkdir(parents=True,exist_ok=True)
 inputs={p.relative_to(ROOT).as_posix():sha(p) for p in [ROOT/'build_reader.py',ROOT/'book.tex',ROOT/'formal_correspondence.tex',ROOT/'source_original/core_v0.2.tex',*sorted((ROOT/'figures').glob('*.pdf')),*sorted((ROOT/'code').glob('*.py'))]}
 records=[];error=None
 def run(cmd,cwd,label):
  start=time.monotonic();r=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=120)
  (out/(label+'.log')).write_bytes(r.stdout)
  records.append({'label':label,'command':cmd,'exit_code':r.returncode,'elapsed_seconds':time.monotonic()-start,'log_sha256':sha(out/(label+'.log'))})
  if r.returncode:raise RuntimeError(label+' failed')
  return r.stdout.decode(errors='replace')
 try:
  (out/'editorial_preservation.json').write_text(json.dumps(preservation(),indent=2)+'\n')
  with tempfile.TemporaryDirectory(prefix='mnr-reviewed-reader-') as td:
   w=Path(td)
   for n in ['book.tex','formal_correspondence.tex']:shutil.copy2(ROOT/n,w/n)
   shutil.copytree(ROOT/'figures',w/'figures');shutil.copytree(ROOT/'code',w/'code');(w/'evidence').mkdir()
   run([sys.executable,'code/check_core.py'],w,'core_exact');run([sys.executable,'code/check_admissions.py'],w,'admission_exact')
   for p in (w/'evidence').glob('*.json'):shutil.copy2(p,out/p.name)
   for i in range(1,4):log=run(['pdflatex','-recorder','-interaction=nonstopmode','-halt-on-error','book.tex'],w,f'latex_pass{i}')
   defects=[s for s in log.splitlines() if any(t in s for t in ['Overfull','Missing character','undefined','multiply defined'])]
   if defects:raise RuntimeError('Unresolved document defects: '+repr(defects))
   fontlog=run(['pdffonts','book.pdf'],w,'pdf_fonts')
   font_rows=fontlog.splitlines()[2:]
   if any(not re.search(r'\s+yes\s+(?:yes|no)\s+(?:yes|no)\s+\d+\s+\d+\s*$',s) for s in font_rows if s.strip()):raise RuntimeError('An embedded font check failed')
   run(['pdfinfo','book.pdf'],w,'pdf_info')
   shutil.copy2(w/'book.pdf',out/'Machine_Native_Reasoning_Reviewed_Core.pdf')
   shutil.copy2(w/'book.log',out/'latex.log');shutil.copy2(w/'book.fls',out/'latex_inputs.fls')
 except Exception as e:error=f'{type(e).__name__}: {e}'
 unchanged=inputs=={n:sha(ROOT/n) for n in inputs}
 report={'status':'PASS' if error is None and unchanged else 'FAIL','error':error,'inputs_unchanged':unchanged,'source_sha256':inputs,'commands':records,'lean_executed':False,'limits':['This runner rebuilds the reviewed-core reader, not the wider 1,155-page monograph.','Finite checks supplement written and formal proofs; they are not universal proof certificates.','Formal acceptance is stated by the separate Lean release record, not by this PDF build.']}
 (out/'REPRODUCTION.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps({'status':report['status'],'error':error,'output':str(out)},indent=2))
 return 0 if report['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
