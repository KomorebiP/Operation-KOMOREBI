from pathlib import Path
import json,hashlib,shutil,subprocess,os,re,time,concurrent.futures
R=Path(__file__).resolve().parents[1];ROOT=R/'source_i_iv';BEFORE=ROOT/'before';BEFORE.mkdir(exist_ok=True)
shared=(R/'publisher-layout.tex').read_text()
extra=r'''
% Publication-design overrides. Mathematical bodies retain their source text.
\CoreLayout
\colorlet{accent}{pubTeal}\colorlet{teal}{pubTeal}\colorlet{ink}{pubInk}\colorlet{muted}{pubMuted}\colorlet{pale}{pubWash}\colorlet{light}{pubWash}
\makeatletter
\@ifundefined{KomorebiCover}{}{\renewcommand{\KomorebiCover}{%
\clearpage\hypersetup{pageanchor=false}\thispagestyle{empty}\begingroup\setlength{\parindent}{0pt}%
{\sffamily\fontsize{8.5}{11}\selectfont\color{pubTeal}REALIZATION CALCULUS\par}%
\vspace{27pt}%
{\sffamily\fontsize{9}{12}\selectfont\color{pubTeal}\MakeUppercase{\KomorebiSeries}\par}%
\vspace{22pt}%
{\normalfont\fontsize{29}{35}\selectfont\color{pubNavy}\raggedright\KomorebiTitle\par}%
\vspace{17pt}%
{\normalfont\fontsize{17}{23}\selectfont\color{pubMuted}\raggedright\KomorebiSubtitle\par}%
\vspace{22pt}\noindent\textcolor{pubCopper}{\rule{42pt}{.8pt}}\par%
\vspace{20pt}%
\@ifundefined{KomorebiCoverBlurb}{}{\normalfont\fontsize{11.4}{16.2}\selectfont\color{pubMuted}\raggedright\KomorebiCoverBlurb\par}%
\vfill%
{\normalfont\fontsize{14}{18}\selectfont\color{pubInk}Komorebi P.\par}%
\vspace{9pt}{\sffamily\fontsize{9}{13}\selectfont\color{pubMuted}\KomorebiKind\par\KomorebiEdition\par}%
\endgroup\clearpage\pagenumbering{roman}\hypersetup{pageanchor=true}\color{pubInk}\normalfont\pagestyle{empty}}}
\makeatother
'''
entries=[('I','editable/traditional/Paper_I_Traditional_Final.tex','traditional','xelatex','Paper_I_Traditional_Final.pdf'),('I','editable/lean_guide/Paper_I_Lean_Guide_Final.tex','lean','xelatex','Paper_I_Lean_Guide_Final.pdf'),('I','editable/machine/Paper_I_Machine_Native_Final.tex','machine','pdflatex','Paper_I_Machine_Native_Final.pdf'),('II','editable/traditional/Paper_II_Traditional_Final.tex','traditional','xelatex','Paper_II_Traditional_Final.pdf'),('II','editable/visual_guide/Paper_II_Visual_Guide_Final.tex','visual','xelatex','Paper_II_Visual_Guide_Final.pdf'),('II','editable/lean_guide/Paper_II_Lean_Guide_Final.tex','lean','xelatex','Paper_II_Lean_Guide_Final.pdf'),('III','manuscript/Paper_III_Traditional_Final.tex','traditional','xelatex','Paper_III_Final_v1.0.0.pdf'),('III','guides/visual/Paper_III_Visual_Guide_Final.tex','visual','xelatex','Paper_III_Visual_Guide_v1.0.0.pdf'),('III','guides/lean/Paper_III_Lean_Guide_Final.tex','lean','xelatex','Paper_III_Lean_Guide_v1.0.0.pdf'),('III','docs/Paper_III_Section17_Analytic_Closeout.tex','analytic','pdflatex','Paper_III_Analytic_Supplement_v1.0.0.pdf'),('IV','Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/traditional/Paper_IV_Traditional_Final.tex','traditional','xelatex','Paper_IV_Traditional_Final.pdf'),('IV','Paper_IV_Verification_Closeout_v1.1.0/publication_baseline/editable/lean_guide/Paper_IV_Lean_Guide_Final.tex','lean','xelatex','Paper_IV_Lean_Guide_Final.pdf')]
inputlist=[]
for roman,rel,role,engine,baseline in entries:
 p=ROOT/roman/rel;s=p.read_text();bp=BEFORE/roman/rel;bp.parent.mkdir(parents=True,exist_ok=True)
 if not bp.exists():bp.write_bytes(p.read_bytes())
 else:s=bp.read_text()
 (p.parent/'core-layout.tex').write_text(shared)
 injected='\\usepackage{titlesec}\n\\input{core-layout.tex}\n'+extra+'\n'
 assert s.count('\\begin{document}')==1
 p.write_text(s.replace('\\begin{document}',injected+'\\begin{document}'))
 inputlist.append({'paper':roman,'source':str(p),'role':role,'engine':engine,'baseline_name':baseline,'before_sha256':hashlib.sha256(bp.read_bytes()).hexdigest(),'styled_sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(ROOT/'selected_sources.json').write_text(json.dumps(inputlist,indent=2))

def build(e):
 p=Path(e['source']);d=ROOT/'compiled'/e['paper']/e['role'];d.mkdir(parents=True,exist_ok=True)
 env=dict(os.environ,TMPDIR=str(ROOT),SOURCE_DATE_EPOCH='1792540800',FORCE_SOURCE_DATE='1');env['TEXINPUTS']=str(p.parent)+':';env['BIBINPUTS']=str(p.parent)+':';env['BSTINPUTS']=str(p.parent)+':'
 cmd=[e['engine'],'-interaction=nonstopmode','-halt-on-error','-file-line-error','-recorder','-output-directory='+str(d),p.name]
 runs=[]
 for i in range(4):
  proc=subprocess.run(cmd,cwd=p.parent,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
  (d/f'pass_{i+1}.txt').write_text(proc.stdout);runs.append(proc.returncode)
  if proc.returncode:break
  aux=d/(p.stem+'.aux')
  if i==0 and '\\bibdata' in aux.read_text(errors='replace'):
   b=subprocess.run(['bibtex',p.stem],cwd=d,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True);(d/'bibtex.txt').write_text(b.stdout);runs.append(b.returncode)
   if b.returncode:break
 pdf=d/(p.stem+'.pdf');log=d/(p.stem+'.log');txt=log.read_text(errors='replace') if log.exists() else ''
 warnings=[ln for ln in txt.splitlines() if re.search('Overfull|Missing character|undefined references|undefined citations|undefined on input|LaTeX Error|^!',ln)]
 result={**e,'runs':runs,'status':'passed' if all(x==0 for x in runs) else 'failed','pdf':str(pdf),'warnings':warnings}
 if result['status']=='passed':
  import fitz
  doc=fitz.open(pdf);result['pages']=len(doc);result['sha256']=hashlib.sha256(pdf.read_bytes()).hexdigest()
 print(json.dumps({k:result[k] for k in ['paper','role','status','runs','warnings']},ensure_ascii=False),flush=True)
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
 results=list(pool.map(build,inputlist))
(ROOT/'build_results.json').write_text(json.dumps(results,indent=2))
