from pathlib import Path
import hashlib,json,difflib,shutil
R=Path(__file__).resolve().parent; W=R.parent
common=(W/'publisher-layout.tex').read_text()
append=r'''
% Core-series presentation additions, applied after the inherited setup.
\CoreLayout
\renewcommand{\familydefault}{\rmdefault}
\definecolor{KomorebiInk}{HTML}{3C263F}
\definecolor{KomorebiPine}{HTML}{7B4165}
\definecolor{KomorebiOchre}{HTML}{A68A56}
\definecolor{KomorebiWarm}{HTML}{FFFFFF}
\definecolor{KomorebiMuted}{HTML}{655D68}
\colorlet{ink}{KomorebiInk}\colorlet{accent}{KomorebiPine}
\colorlet{teal}{KomorebiPine}\colorlet{Teal}{KomorebiPine}
\colorlet{Navy}{KomorebiInk}\colorlet{navy}{KomorebiInk}
\fancypagestyle{fancy}{\fancyhf{}\renewcommand{\headrulewidth}{0pt}\renewcommand{\footrulewidth}{0pt}}
\renewcommand{\KomorebiCover}{%
 \clearpage\hypersetup{pageanchor=false}\thispagestyle{empty}\begingroup
 \setlength{\parindent}{0pt}\setlength{\parskip}{0pt}
 \vspace*{22pt}
 {\sffamily\fontsize{8.5}{11}\selectfont\color{pubTeal}\MakeUppercase{\KomorebiSeries}\par}
 \vspace{30pt}
 {\rmfamily\fontsize{30}{36}\selectfont\color{pubNavy}\raggedright\KomorebiTitle\par}
 \vspace{18pt}
 {\rmfamily\fontsize{19}{25}\selectfont\color{pubNavy}\raggedright\KomorebiSubtitle\par}
 \vspace{24pt}\textcolor{pubCopper}{\rule{42pt}{.8pt}}\par\vspace{18pt}
 {\sffamily\fontsize{10}{14}\selectfont\color{pubMuted}\KomorebiKind\par}
 \vfill
 {\rmfamily\fontsize{13}{17}\selectfont Komorebi P.\par}\vspace{9pt}
 {\sffamily\fontsize{8.5}{12}\selectfont\color{pubMuted}\KomorebiEdition\par}
 \vspace{20pt}\endgroup\clearpage\setcounter{page}{1}\hypersetup{pageanchor=true}\color{pubInk}\normalfont
}
'''
records=[]
for k in ['XI','XII']:
 root=R/k
 for role in ['traditional','visual_guide','lean_guide']:
  p=root/'publication/source'/role/f'Paper_{k}_{"Traditional" if role=="traditional" else "Visual_Guide" if role=="visual_guide" else "Lean_Guide"}_Final.tex'
  original=p.read_bytes(); before=root/'before'/p.relative_to(root);before.parent.mkdir(parents=True,exist_ok=True);before.write_bytes(original)
  src=original.decode();src=src.replace('\\begin{document}','\\input{core-monograph-layout.tex}\n\\begin{document}',1)
  p.write_text(src)
  layout=p.parent/'core-monograph-layout.tex';layout.write_text(common+append)
  # Pinned local installed OTF paths avoid fontconfig choosing unrequested variants.
  f=p.parent/'komorebi-font-paths.tex'
  if not f.exists():f.write_text('\\providecommand{\\KomorebiFontDirectory}{/usr/share/fonts/opentype/urw-base35/}\n')
  records.append({'file':str(p),'before_sha256':hashlib.sha256(original).hexdigest(),'after_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'document_body_identical':original.decode().split('\\begin{document}',1)[1]==src.split('\\begin{document}',1)[1],'change':'Inject publication-only layout immediately before document body.'})
  (before.parent/(before.name+'.diff')).write_text(''.join(difflib.unified_diff(original.decode().splitlines(True),src.splitlines(True),fromfile='before/'+p.name,tofile=p.name)))
 (root/'SOURCE_PRESERVATION.json').write_text(json.dumps([x for x in records if f'/{k}/' in x['file']],indent=2))
print(json.dumps(records,indent=2))
