from pathlib import Path
import json,hashlib,shutil,subprocess,os,difflib,concurrent.futures,time
ROOT=Path(__file__).resolve().parent
WORK=ROOT.parent
STYLE=(WORK/'publisher-layout.tex').read_text()
ADAPT=r'''% Collected core edition: typography only. Original scientific body is unchanged.
\input{publisher-layout.tex}
\CoreLayout
\colorlet{accent}{pubTeal}\colorlet{teal}{pubTeal}\colorlet{ink}{pubInk}\colorlet{muted}{pubMuted}\colorlet{light}{pubWash}\colorlet{pale}{pubWash}
\renewcommand{\KomorebiCover}{%
 \clearpage\hypersetup{pageanchor=false}\thispagestyle{empty}\begingroup\setlength{\parindent}{0pt}
 {\sffamily\fontsize{8.5}{11}\selectfont\color{pubTeal}\MakeUppercase{\KomorebiSeries}\par}
 \vspace{35pt}
 {\fontsize{28}{34}\selectfont\color{pubNavy}\raggedright\KomorebiCoverTitle\par}
 \vspace{16pt}
 {\sffamily\fontsize{11}{15.5}\selectfont\color{pubMuted}\raggedright\KomorebiSubtitle\par}
 \vspace{20pt}\noindent\textcolor{pubCopper}{\rule{42pt}{.8pt}}\par
 \vspace{20pt}
 {\fontsize{11.4}{16.2}\selectfont\raggedright\KomorebiCoverBlurb\par}
 \vfill
 {\fontsize{14}{18}\selectfont Komorebi P.\par}
 \vspace{7pt}{\sffamily\fontsize{9}{12}\selectfont\color{pubMuted}\KomorebiKind\quad\textbullet\quad\KomorebiEdition\par}
 \endgroup\clearpage\pagenumbering{roman}\hypersetup{pageanchor=true}\color{pubInk}\normalfont
}
'''
records=[]
for number in ['V','VI','VII','VIII']:
 for role,kind in [('traditional','Traditional'),('visual_guide','Visual_Guide'),('lean_guide','Lean_Guide')]:
  cwd=ROOT/number/'editable'/role; stem=f'Paper_{number}_{kind}_Final';src=cwd/(stem+'.tex')
  before=ROOT/'before'/number/role/(stem+'.tex');before.parent.mkdir(parents=True,exist_ok=True)
  if not before.exists():shutil.copyfile(src,before)
  original=before.read_text();assert original.count(r'\begin{document}')==1
  updated=original.replace(r'\begin{document}',r'\input{component-layout.tex}'+'\n'+r'\begin{document}',1)
  src.write_text(updated);(cwd/'publisher-layout.tex').write_text(STYLE);(cwd/'component-layout.tex').write_text(ADAPT)
  assert original.split(r'\begin{document}',1)[1]==updated.split(r'\begin{document}',1)[1]
  fontdir=cwd/'fonts';fontdir.mkdir(exist_ok=True)
  fonts=['P052-Roman.otf','P052-Bold.otf','P052-Italic.otf','P052-BoldItalic.otf','NimbusSans-Regular.otf','NimbusSans-Bold.otf','NimbusSans-Italic.otf','NimbusSans-BoldItalic.otf','lmmono10-regular.otf','lmmono10-italic.otf','latinmodern-math.otf']
  if role=='lean_guide':fonts+=['DejaVuSansMono.ttf','DejaVuSansMono-Bold.ttf','DejaVuSansMono-Oblique.ttf','DejaVuSansMono-BoldOblique.ttf']
  deps=[]
  for n in fonts:
   p=Path(subprocess.check_output(['kpsewhich',n],text=True).strip());assert p.is_file(),n
   dst=fontdir/n
   if dst.exists():dst.unlink()
   dst.symlink_to(p)
   deps.append({'name':n,'path':str(p),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
  (cwd/'MONOGRAPH_FONT_DEPENDENCIES.json').write_text(json.dumps(deps,indent=2))
  rec={'paper':number,'role':role,'stem':stem,'source':str(src),'before':str(before),'body_after_begin_document_byte_equal':True,'source_original_sha256':hashlib.sha256(before.read_bytes()).hexdigest(),'source_edited_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'font_dependencies':deps}
  records.append(rec)
(ROOT/'SOURCE_EDITS.json').write_text(json.dumps(records,indent=2))

def build(rec):
 cwd=Path(rec['source']).parent;stem=rec['stem'];out=ROOT/'compiled'/rec['paper']/rec['role'];out.mkdir(parents=True,exist_ok=True)
 env=dict(os.environ,TMPDIR=str(WORK),SOURCE_DATE_EPOCH='1792540800',FORCE_SOURCE_DATE='1',TEXINPUTS=str(cwd)+os.pathsep)
 command=['xelatex','-no-shell-escape','-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder','-output-directory='+str(out),stem+'.tex']
 runs=[]
 for i in range(1,5):
  run=subprocess.run(command,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
  (out/f'pass_{i}.txt').write_text(run.stdout);runs.append({'pass':i,'returncode':run.returncode})
  if run.returncode:break
  if i==1 and r'\bibdata' in (out/(stem+'.aux')).read_text():
   bibenv=dict(env,BIBINPUTS=str(cwd)+os.pathsep,BSTINPUTS=str(cwd)+os.pathsep)
   b=subprocess.run(['bibtex',stem],cwd=out,env=bibenv,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT);(out/'bibtex.txt').write_text(b.stdout);runs.append({'bibtex':b.returncode})
   if b.returncode:break
 rec.update(runs=runs,pdf=str(out/(stem+'.pdf')),compiled_directory=str(out),success=not any(x.get('returncode',x.get('bibtex',0)) for x in runs));print(rec['paper'],rec['role'],rec['success'],flush=True)
 return rec
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
 results=list(ex.map(build,records))
(ROOT/'BUILD_RESULTS.json').write_text(json.dumps(results,indent=2))
