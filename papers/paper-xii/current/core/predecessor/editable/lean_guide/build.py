#!/usr/bin/env python3
"""Portable deterministic guide build; builds in a fresh output directory."""
from pathlib import Path
import argparse,datetime,hashlib,json,os,re,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parent
STEM='Paper_XII_Lean_Guide_Final'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output-dir',required=True,type=Path);a=p.parse_args()
 out=a.output_dir.resolve()
 if out==ROOT:raise SystemExit('Use a separate fresh output directory')
 if out.exists() and any(out.iterdir()):raise SystemExit('Output directory must be empty')
 out.mkdir(parents=True,exist_ok=True)
 for tool in ['xelatex','pdftotext','pdfinfo','pdffonts']:
  if not shutil.which(tool):raise SystemExit('Required executable absent: '+tool)
 shutil.copy2(ROOT/(STEM+'.tex'),out/(STEM+'.tex'))
 for d in ['fonts','data','excerpts']:
  shutil.copytree(ROOT/d,out/d,dirs_exist_ok=True)
 env=os.environ.copy();env['SOURCE_DATE_EPOCH']='1791244800';env['FORCE_SOURCE_DATE']='1';env['TZ']='UTC'
 logs=[]
 for i in range(3):
  proc=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error',STEM+'.tex'],cwd=out,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  (out/f'build_pass_{i+1}.txt').write_text(proc.stdout);logs.append(proc.returncode)
  if proc.returncode:raise SystemExit('TeX failed; inspect '+str(out/f'build_pass_{i+1}.txt'))
 log=(out/(STEM+'.log')).read_text(errors='replace')
 bad=[line for line in log.splitlines() if re.search(r'(Missing character:|LaTeX Warning:.*undefined|LaTeX Font Warning:.*undefined|Overfull \\hbox)',line)]
 if bad:raise SystemExit('Preflight failure: '+'\n'.join(bad))
 pdf=out/(STEM+'.pdf')
 subprocess.run(['pdftotext','-layout',str(pdf),str(out/(STEM+'.txt'))],check=True)
 info=subprocess.check_output(['pdfinfo',str(pdf)],text=True);fonts=subprocess.check_output(['pdffonts',str(pdf)],text=True)
 (out/'PDF_INFO.txt').write_text(info);(out/'PDF_FONTS.txt').write_text(fonts)
 pages=int(re.search(r'^Pages:\s+(\d+)',info,re.M)[1])
 text=(out/(STEM+'.txt')).read_text()
 required=['Komorebi P.','2026','748','1,229','291','49','Original wording','Complete production source','Markdown','No fresh Lean']
 assert all(t.lower() in text.lower() for t in required),[t for t in required if t.lower() not in text.lower()]
 font_rows=fonts.splitlines()[2:];assert all(re.search(r'\s+yes\s+yes\s+',r) for r in font_rows),fonts
 report={'status':'PASS','date':'2026-10-06','scope':'guide PDF build and document/source preflight; no Lean compilation','engine':subprocess.check_output(['xelatex','--version'],text=True).splitlines()[0],'pages':pages,'pdf_sha256':sha(pdf),'text_sha256':sha(out/(STEM+'.txt')),'tex_sha256':sha(out/(STEM+'.tex')),'three_passes':logs,'missing_glyphs':0,'overfull_hboxes':0,'undefined_references':0,'all_pdf_fonts_embedded':True,'source_date_epoch':1791244800,'build_prerequisites':['Python 3.10+','TeX Live with XeLaTeX, fontspec, unicode-math, fvextra, booktabs, longtable, microtype, fancyhdr, hyperref','Poppler pdfinfo, pdftotext, pdffonts'],'trailer_policy':'Fixed XeTeX/dvipdfmx trailer ID and CreationDate/ModDate; SOURCE_DATE_EPOCH; no wall-clock date in document'}
 (out/'BUILD_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
 print(json.dumps(report,indent=2))
if __name__=='__main__':main()
