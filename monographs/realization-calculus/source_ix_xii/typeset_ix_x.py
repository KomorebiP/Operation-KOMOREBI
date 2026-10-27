from pathlib import Path
import os,json,subprocess,hashlib,difflib,re,concurrent.futures,shutil,time
import fitz
ROOT=Path(__file__).resolve().parents[1]
GROUP=ROOT/'source_ix_xii'
layout=(ROOT/'publisher-layout.tex').read_bytes()
addition=r'''
% Collected core monograph: Physics-derived typography, no mathematical edits.
\ifcsname captiontext\endcsname
 \let\CoreSavedCaptionText\captiontext\let\captiontext\relax
\fi
\input{publisher-layout.tex}
\ifcsname CoreSavedCaptionText\endcsname\let\captiontext\CoreSavedCaptionText\fi
\apptocmd{\KomorebiSetup}{%
  \renewcommand{\familydefault}{\rmdefault}%
  \CoreLayout
  \colorlet{KomorebiInk}{pubNavy}\colorlet{KomorebiPine}{pubTeal}%
  \colorlet{KomorebiMuted}{pubMuted}\colorlet{KomorebiOchre}{pubCopper}%
  \colorlet{KomorebiWarm}{white}\colorlet{KomorebiSoft}{pubWash}%
  \colorlet{accent}{pubTeal}\colorlet{teal}{pubTeal}\colorlet{Teal}{pubTeal}%
  \colorlet{navy}{pubNavy}\colorlet{Navy}{pubNavy}\colorlet{ink}{pubInk}%
  \colorlet{muted}{pubMuted}\colorlet{Muted}{pubMuted}\colorlet{Accent}{pubTeal}%
  \colorlet{KomorebiBlue}{pubTeal}\colorlet{KomorebiNavy}{pubNavy}%
}{}{}
\BeforeBeginEnvironment{tabularx}{\noindent}
\renewcommand{\KomorebiCover}{%
 \clearpage\hypersetup{pageanchor=false}\thispagestyle{empty}\begingroup\setlength{\parindent}{0pt}%
 {\sffamily\fontsize{8.5}{11}\selectfont\color{pubTeal}REALIZATION CALCULUS\par}%
 \vspace*{42pt}%
 \CoreOpening{\KomorebiSeries}{\KomorebiTitle}{\KomorebiSubtitle}%
 \vspace{9pt}{\sffamily\fontsize{11}{15}\selectfont\color{pubMuted}\KomorebiKind\par}%
 \vfill
 {\normalfont\fontsize{14}{19}\selectfont Komorebi P.\par}%
 \vspace{8pt}{\sffamily\fontsize{8.5}{12}\selectfont\color{pubMuted}\KomorebiEdition\par}%
 \endgroup\clearpage\setcounter{page}{1}\hypersetup{pageanchor=true}\normalfont\color{pubInk}%
}
'''
for k in ['IX','X']:
 root=GROUP/k;sty=root/'publication/house_style/komorebi-publication.sty';before=root/'before/publication/house_style';before.mkdir(parents=True,exist_ok=True)
 if not (before/sty.name).exists():shutil.copy2(sty,before/sty.name)
 original=(before/sty.name).read_text();new=original.replace('\\endinput',addition+'\n\\endinput')
 sty.write_text(new);(sty.parent/'publisher-layout.tex').write_bytes(layout)
 (root/'STYLE_DIFF.patch').write_text(''.join(difflib.unified_diff(original.splitlines(True),new.splitlines(True),fromfile='before/komorebi-publication.sty',tofile='publication/house_style/komorebi-publication.sty')))

def build(k,d):
 root=GROUP/k;source=root/d['main'];out=root/'compiled'/Path(d['file_name']).stem;out.mkdir(parents=True,exist_ok=True)
 env=dict(os.environ,TMPDIR=str(ROOT),SOURCE_DATE_EPOCH='1792540800',FORCE_SOURCE_DATE='1',TZ='UTC')
 env['TEXINPUTS']=str(out)+':'+str(root/'publication/house_style')+':'
 env['BIBINPUTS']=str(source.parent)+':';env['BSTINPUTS']=str(source.parent)+':'
 cmd=[d['engine'],'-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder','-output-directory='+str(out),'-jobname='+Path(d['file_name']).stem,source.name]
 runs=[];t=time.time();rc=0
 for n in range(3):
  q=subprocess.run(cmd,cwd=source.parent,env=env,capture_output=True,timeout=240);(out/f'pass{n+1}.txt').write_bytes(q.stdout+q.stderr);runs.append({'command':cmd,'returncode':q.returncode});rc=q.returncode
  if rc:break
  aux=out/(Path(d['file_name']).stem+'.aux')
  if n==0 and r'\bibdata' in aux.read_text(errors='replace'):
   bib=shutil.which('bibtex.original') or shutil.which('bibtex');q=subprocess.run([bib,Path(d['file_name']).stem],cwd=out,env=env,capture_output=True,timeout=120);(out/'bibtex.txt').write_bytes(q.stdout+q.stderr);runs.append({'command':[bib,Path(d['file_name']).stem],'returncode':q.returncode});rc=q.returncode
   if rc:break
 pdf=out/d['file_name'];log=(out/(Path(d['file_name']).stem+'.log')).read_text(errors='replace')
 row={'paper':k,'kind':d['kind'],'file_name':d['file_name'],'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'output_pdf':str(pdf),'returncode':rc,'runs':runs,'seconds':round(time.time()-t,2),'warnings':[s for s in log.splitlines() if re.search(r'Warning:|Overfull|Missing character',s)],'tail':log.splitlines()[-20:] if rc else []}
 if not rc:
  row.update(pages=len(fitz.open(pdf)),sha256=hashlib.sha256(pdf.read_bytes()).hexdigest())
 (out/'BUILD.json').write_text(json.dumps(row,indent=2));print(json.dumps({a:row[a] for a in ['paper','kind','returncode','seconds','tail']}),flush=True);return row
if __name__=='__main__':
 jobs=[(k,d) for k in ['IX','X'] for d in json.loads((GROUP/k/'publication/documents.json').read_text())]
 rows=[]
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
  for f in concurrent.futures.as_completed([pool.submit(build,k,d) for k,d in jobs]):
   rows.append(f.result());(GROUP/'IX_X_BUILD_RESULTS.json').write_text(json.dumps(rows,indent=2))

 # Produce the six assembled component PDFs without invoking evidence or experiments.
 if all(row['returncode']==0 for row in rows):
  import importlib.util
  bykey={(row['paper'],row['kind']):row for row in rows}
  for row in rows:
   if row['paper']=='X' and row['kind']=='traditional':continue
   target=GROUP/row['paper']/'publication/pdfs'/row['file_name'];target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(row['output_pdf'],target)
  spec=importlib.util.spec_from_file_location('paper_x_publication',GROUP/'X/publication/build_publication.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  m=bykey['X','traditional'];v=bykey['X','visual'];target=GROUP/'X/publication/pdfs'/m['file_name'];target.unlink(missing_ok=True)
  module.append_atlas(Path(m['output_pdf']),GROUP/'X/publication/pdfs'/v['file_name'],target)
 else:
  raise SystemExit('One or more TeX builds failed; inspect IX_X_BUILD_RESULTS.json')
