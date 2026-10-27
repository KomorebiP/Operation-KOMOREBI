#!/usr/bin/env python3
"""Compose the visual guide from its reviewed scene records."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'source'

FRONT=r'''\documentclass[11pt]{article}
\input{preamble}
\renewcommand{\KomorebiKind}{Visual guide}
\renewcommand{\KomorebiSubtitle}{Sixteen visual investigations in coherent realization}
\renewcommand{\KomorebiEdition}{Publication edition / October 2026}
\hypersetup{pdftitle={Komorebi Space: Sixteen Visual Investigations},pdfsubject={Worked visual experiments in realization, correction, and limits}}
\setcounter{tocdepth}{1}
\newcommand{\scene}[4]{%
  \clearpage\phantomsection\addcontentsline{toc}{section}{#1\quad #2}%
  {\sffamily\small\bfseries\color{KomorebiMuted}VISUAL INVESTIGATION #1\par}%
  \vspace{4pt}{\sffamily\Large\bfseries\color{KomorebiPine}#2\par}%
  \vspace{8pt}#3\par\vspace{4pt}%
  \begin{center}\includegraphics[width=\linewidth,height=5.05in,keepaspectratio]{#4}\end{center}\vspace{2pt}}
\newcommand{\scenenotes}[3]{%
  \noindent\textbf{Read the picture.} #1\par\medskip
  \noindent\textbf{Change one thing.} #2\par
  \vfill{\small\color{KomorebiMuted}Definitions, proofs, and general hypotheses: #3.\par}}
\begin{document}
\KomorebiCover
\pdfbookmark[0]{Contents}{visual-contents}
\begingroup
\makeatletter
\renewcommand{\@pnumwidth}{3em}
\renewcommand{\@tocrmarg}{4em}
\makeatother
\tableofcontents
\endgroup
\clearpage\phantomsection\addcontentsline{toc}{section}{How to use this guide}
\section*{How to use this guide}
Start with a picture and change one ingredient. Keep a boundary value fixed. Remove an observation. Rotate a correction direction. Tighten a solver tolerance. The following investigations show what moves, what survives, and what can fail.

Each page supplies a small declared model, a figure to inspect, and a worked change to that model. The monograph references lead to the definitions and proofs. You can follow the pictures in sequence or choose a question from the contents.

\subsection*{Three things to identify}
\begin{enumerate}
\item \textbf{The allowed objects.} Integer points, real vectors, matrices, and infinite sequences have different completion rules. A line drawn through integer markers does not create new integer solutions.
\item \textbf{The information held fixed.} An exact answer may exist but fail to preserve the prescribed data. Two pictures of exactness can describe different correction problems.
\item \textbf{The measured quantity.} A residual, a correction norm, a movement budget, and a coordinate norm are different numbers. Axis labels and metrics are part of the example.
\end{enumerate}

\subsection*{Reading the graphics}
Green marks the principal admissible object or successful route. Ochre and red distinguish comparisons, discrepancies, or excluded cases. Labels and legends identify what each color and line pattern measures. The spatial figures use genuine three-dimensional coordinates. Curves are evaluated from the formulas stated in the examples; they are not fitted to observations.

Finite windows of infinite sequences illustrate explicit formulas. An exact tail norm or a convergence condition comes from the accompanying mathematical argument, not from the end of a plotted line. Numerical drawing coordinates are rounded for display.

\subsection*{The companions}
The monograph develops the general results and their hypotheses. The Lean guide identifies exact formal declarations and their scope. These visual investigations include concrete instances and illustrative variations; they are not individually asserted to be Lean formalizations. The source package contains the plotting scripts and the recorded checks for the worked values.
'''

def main():
    data=json.loads((SOURCE/'visual_companion/scenes.json').read_text())
    refs=json.loads((SOURCE/'visual_companion/monograph_references.json').read_text())
    lines=[FRONT]
    for i,s in enumerate(data,1):
        figure='figures/visual_companion/'+s['figure']
        assert (SOURCE/figure).is_file(),figure
        numbers=[refs[k]['section'] for k in s['monograph_labels']]
        reference='Monograph '+('Section~' if len(numbers)==1 else 'Sections~')+', '.join(numbers)
        lines.append('\\scene{'+f'{i:02}'+'}{'+s['title']+'}{'+s['setup_tex']+'}{'+figure+'}\n')
        lines.append('\\scenenotes{'+s['reading_tex']+'}{'+s['experiment_tex']+'}{'+reference+'}\n')
    lines.append('\\end{document}\n')
    target=SOURCE/'Komorebi_Space_Visual_Guide.tex'
    target.write_text('\n'.join(lines))
    print(target)

if __name__=='__main__':main()
