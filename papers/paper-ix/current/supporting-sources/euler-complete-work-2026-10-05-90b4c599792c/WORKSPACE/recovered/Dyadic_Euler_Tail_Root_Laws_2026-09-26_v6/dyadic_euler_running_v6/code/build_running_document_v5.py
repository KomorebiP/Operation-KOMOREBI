#!/usr/bin/env python3
"""Build the append-only mathematical record and a separate current appendix.

Requires Pandoc and XeLaTeX. Does not modify recovered historical source files.
"""
from __future__ import annotations
import re,subprocess,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DOC=ROOT/'manuscript';HIST=ROOT/'history'/'v4'

PREAMBLE=r'''\documentclass[11pt,letterpaper]{article}
\usepackage[margin=0.88in,headheight=15pt,headsep=18pt,footskip=27pt]{geometry}
\usepackage{fontspec}
\setmainfont{lmroman10-regular.otf}[BoldFont=lmroman10-bold.otf,ItalicFont=lmroman10-italic.otf,BoldItalicFont=lmroman10-bolditalic.otf]
\setsansfont{lmsans10-regular.otf}[BoldFont=lmsans10-bold.otf,ItalicFont=lmsans10-oblique.otf]
\setmonofont{DejaVu Sans Mono}[Scale=0.79]
\usepackage{amsmath,amssymb,mathtools}
\usepackage{unicode-math}
\setmathfont{latinmodern-math.otf}
\usepackage{microtype}
\usepackage{booktabs,longtable,array,calc,multirow}
\usepackage{graphicx,float,caption}
\usepackage{fvextra}
\DefineVerbatimEnvironment{verbatim}{Verbatim}{breaklines=true,breakanywhere=true,fontsize=\footnotesize}
\usepackage{xurl,seqsplit}
\usepackage{fancyhdr,titlesec,etoolbox}
\usepackage{hyperref,bookmark}
\hypersetup{hidelinks,bookmarksdepth=2,pdftitle={Dyadic Euler Tails: A Running Research Record},pdfauthor={Komorebi P.}}
\pagestyle{fancy}
\fancyhf{}
\fancyhead[L]{\small\sffamily Dyadic Euler Tails}
\fancyhead[R]{\small\sffamily Research record \textbar\ v5}
\fancyfoot[L]{\small\sffamily Komorebi P.}
\fancyfoot[R]{\small\thepage}
\renewcommand{\headrulewidth}{0.3pt}
\renewcommand{\footrulewidth}{0pt}
\titleformat{\section}{\Large\sffamily\bfseries}{}{0pt}{}
\titleformat{\subsection}{\large\sffamily\bfseries}{}{0pt}{}
\titleformat{\subsubsection}{\normalsize\sffamily\bfseries}{}{0pt}{}
\titlespacing*{\section}{0pt}{22pt}{12pt}
\titlespacing*{\subsection}{0pt}{16pt}{7pt}
\titlespacing*{\subsubsection}{0pt}{12pt}{5pt}
\setcounter{secnumdepth}{-1}
\setcounter{tocdepth}{1}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5.5pt plus 1pt}
\setlength{\emergencystretch}{3em}
\setlength{\tabcolsep}{5pt}
\renewcommand{\arraystretch}{1.13}
\AtBeginEnvironment{longtable}{\small}
\captionsetup{font=small,labelfont=bf}
\linespread{1.04}
\allowdisplaybreaks[2]
\clubpenalty=10000
\widowpenalty=10000
\providecommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\providecommand{\passthrough}[1]{#1}
\providecommand{\pandocbounded}[1]{#1}
\DeclareMathOperator{\sech}{sech}
\DeclareMathOperator{\Res}{Res}
\begin{document}
'''


def cover(appendix:bool)->str:
    title='New Results and Audit Appendix' if appendix else 'A Running Research Record'
    desc=('Version-5 continuation. Exact stopping certificates, cancellation distributions, and the next irregular walls.'
          if appendix else 'Triangular inversion, carry walls, root resolution, and exact precision distributions. Full recovered proof notes from versions 1 through 4, with version 5 appended.')
    return r'''\hypersetup{pageanchor=false}
\begin{titlepage}
\thispagestyle{empty}
\vspace*{0.65in}
{\sffamily\large OPERATION KOMOREBI\par}
\vspace{0.55in}
{\sffamily\fontsize{31}{36}\selectfont\bfseries Dyadic Euler Tails\par}
\vspace{0.20in}
{\sffamily\fontsize{20}{25}\selectfont '''+title+r'''\par}
\vspace{0.38in}
{\large '''+desc+r'''\par}
\vspace{0.45in}
\[
\mathcal T_{r-1}(N)
=\kappa_r\binom{2N}{2r}\,2^{\mu_r}G_r(N-r)
\]
\vfill
{\large Komorebi P.\par}
\vspace{0.14in}
{\sffamily Version 5 \textbar\ 26 September 2026\par}
\vspace{0.35in}
\begin{minipage}{0.94\textwidth}
\small
Working research manuscript. Mathematical proofs, finite coefficient certificates and unresolved claims are distinguished in the text. No Lean verification or historical-priority assessment is claimed for these continuations.
\end{minipage}
\end{titlepage}
\pagenumbering{roman}
\hypersetup{pageanchor=true}
\tableofcontents
\clearpage
\pagenumbering{arabic}
'''


def include_note(name:str,title:str,notice:str)->str:
    text=(HIST/name).read_text()
    lines=text.splitlines()
    return '# '+title+'\n\n> **Historical record.** '+notice+'\n\n'+'\n'.join(lines[1:])+'\n'


def compose()->tuple[str,str]:
    front=(DOC/'FRONT_MATTER.md').read_text()
    parts=[front]
    specs=[
      ('PROOF.md','Continuation I. Binary-edge root laws',
       'Recovered v1 proof note. Its finite execution counts are historical unless explicitly covered by the fresh reruns. Later continuations generalize the root law.'),
      ('CONTINUATION_02.md','Continuation II. Carry-Newton reduction at arbitrary depth',
       'Recovered v2 note. Its taxonomy is a taxonomy of residual roots. Multiple residual roots require further analysis before a dyadic-root claim.'),
      ('CONTINUATION_03.md','Continuation III. Shifted-wall normal form and the first multiple branch',
       'Recovered v3 note. The condition delta > 2 d_i is sufficient, not an exact threshold. Continuation IV supplies the sharp regular-wall threshold. Continuation V disproves a general monotone-emergence interpretation.'),
      ('COMPLETION_04.md','Continuation IV. Exact wall resolution and finite polynomial reduction',
       'Recovered consolidated v4 proof note. Its main scientific checker has been rerun in this release. Continuation V appends new results without replacing this record.')]
    for spec in specs:parts.append('\\clearpage\n\n'+include_note(*spec))
    parts.append('\\clearpage\n\n'+(DOC/'CONTINUATION_05.md').read_text())
    # A current illustrative figure not already embedded in the original record.
    current_image='\n![The resolved five-root residual on offsets 0 through 63. Ordinary integer order is used for display; the exact root-distance law uses the dyadic metric.](../figures/06_residual_valuations.png)\n'
    parts.append(current_image)
    parts.append('\\clearpage\n\n'+(DOC/'SOURCES_AND_REPRODUCTION.md').read_text())
    running='\n\n'.join(parts)
    appendix=(DOC/'CONTINUATION_05.md').read_text()+current_image+'\n\\clearpage\n\n'+(DOC/'SOURCES_AND_REPRODUCTION.md').read_text()
    return running,appendix


def build(text:str,stem:str,appendix:bool=False):
    md=DOC/(stem+'.md');md.write_text(text)
    body_path=DOC/(stem+'_body.tex')
    subprocess.run(['pandoc',str(md),'-f','markdown+tex_math_single_backslash+tex_math_dollars+raw_tex',
                    '-t','latex','--wrap=none','--no-highlight','-o',str(body_path)],check=True,cwd=DOC)
    body=body_path.read_text()
    # Use vector copies of generated plots in the print document.
    body=body.replace('.png}', '.pdf}')
    # Every generated plot fits the content width regardless of natural size.
    body=re.sub(r'\\includegraphics(?:\[[^\]]*\])?\{(\.\./figures/[^}]+)\}',
                lambda m:r'\includegraphics[width=0.94\linewidth,keepaspectratio]{'+m.group(1)+'}',body)
    # Avoid floating-figure queues interacting with multipage tables.
    body=re.sub(r'\\begin\{figure\}(?:\[[^\]]*\])?',r'\\begin{figure}[H]',body)
    # Explicit section anchors make the PDF navigation independent of titlesec.
    body=re.sub(r'(\\(?:section|subsection|subsubsection)\{)',r'\\phantomsection\n\1',body)
    # Preserve historical prose but make its long bare references breakable.
    body=re.sub(r'(?<![\w{])https?://[^\s{}<>]+',
                lambda m:r'\url{'+m.group(0)+'}',body)
    body=body.replace('181803547360506310314536504063203550384',
                      r'\seqsplit{181803547360506310314536504063203550384}')
    body=body.replace('88c616ef1758fccb3a10571c7c3524b0',
                      r'\texttt{\seqsplit{88c616ef1758fccb3a10571c7c3524b0}}')
    # Source archive names and hashes can be long. xurl handles them in monospace.
    body=re.sub(r'\\texttt\{([A-Za-z0-9_\\.\-/]{45,})\}',
                lambda m:r'\path{'+m.group(1).replace('\\_','_')+'}',body)
    tex=DOC/(stem+'.tex');tex.write_text(PREAMBLE+cover(appendix)+body+'\n\\end{document}\n')
    for i in range(2):
        cp=subprocess.run(['xelatex','-interaction=nonstopmode','-halt-on-error',tex.name],
                          cwd=DOC,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        (DOC/(stem+f'_build_{i+1}.txt')).write_text(cp.stdout)
        if cp.returncode:
            print(cp.stdout[-9000:]);raise RuntimeError('XeLaTeX build failed')
    print(stem,'BUILT')

if __name__=='__main__':
    running,appendix=compose()
    build(running,'Dyadic_Euler_Tails_Running_v5')
    build(appendix,'Dyadic_Euler_Tails_Appendix_v5',True)
