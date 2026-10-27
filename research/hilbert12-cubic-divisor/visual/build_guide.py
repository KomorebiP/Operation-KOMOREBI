#!/usr/bin/env python3
"""Render the authored guide_content.json to portable TeX and Markdown."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
PAGES=json.loads((ROOT/'guide_content.json').read_text())

def escape_text(s):
    return s.replace('·',r'\textperiodcentered{}')

def tex_document():
    head=r'''\documentclass[11pt]{article}
\usepackage[letterpaper,margin=.78in,headheight=15pt]{geometry}
\usepackage[T1]{fontenc}
\usepackage[utf8]{inputenc}
\usepackage{lmodern,microtype,amsmath,amssymb,graphicx,xcolor,fancyhdr,hyperref,booktabs,array}
\usepackage{tcolorbox}
\definecolor{navy}{HTML}{17334D}
\definecolor{teal}{HTML}{168B8D}
\definecolor{pale}{HTML}{F2F7F8}
\hypersetup{colorlinks=true,linkcolor=teal,urlcolor=teal,pdftitle={Hilbert 12: Cubic Divisor Transport and Reconstruction: Visual Guide},pdfauthor={Komorebi P.}}
\pagestyle{fancy}\fancyhf{}
\fancyhead[L]{\small\color{navy}Hilbert 12: Cubic Divisor}
\fancyhead[R]{\small\color{navy}Visual Guide}
\fancyfoot[L]{\small\color{navy}Komorebi P.\quad October 7, 2026}
\fancyfoot[R]{\small\color{navy}\thepage}
\renewcommand{\headrulewidth}{.4pt}
\setlength{\parindent}{0pt}\setlength{\parskip}{7pt}
\setlength{\emergencystretch}{2em}
\setlength{\abovedisplayskip}{7pt}\setlength{\belowdisplayskip}{7pt}
\begin{document}
'''
    parts=[head]
    for i,p in enumerate(PAGES):
        if i:parts.append(r'\clearpage'+'\n')
        parts.append(r'{\small\bfseries\color{teal}'+escape_text(p['deck'])+'}\n\n')
        parts.append(r'{\LARGE\bfseries\color{navy}'+p['title']+r'\par}'+'\n'+r'\vspace{3pt}'+'\n')
        if p['figure']:
            parts.append(r'\begin{center}\includegraphics[width=\linewidth,height='+p.get('figure_height','3.1in')+r',keepaspectratio]{figures/'+p['figure']+r'.pdf}\end{center}'+'\n')
            parts.append(r'{\small\color{navy}'+p['caption']+'}\n\n')
        if p.get('table'):
            parts.append(r'\vspace{5pt}\begin{center}\small\renewcommand{\arraystretch}{1.3}\begin{tabular}{@{}>{\raggedright\arraybackslash}p{.25\linewidth}>{\raggedright\arraybackslash}p{.33\linewidth}>{\raggedright\arraybackslash}p{.36\linewidth}@{}}\toprule'+'\n')
            for j,row in enumerate(p['table']):
                parts.append(' & '.join(row)+r'\\'+('\n'+r'\midrule'+'\n' if j==0 else '\n'))
            parts.append(r'\bottomrule\end{tabular}\end{center}'+'\n')
        for eq in p['equations']:
            parts.append(r'\['+eq+r'\]'+'\n')
        for para in p['paragraphs']:parts.append(para+'\n\n')
        parts.append(r'\begin{tcolorbox}[colback=pale,colframe=teal,boxrule=.4pt,arc=2pt,left=7pt,right=7pt,top=5pt,bottom=5pt]\small\bfseries '+p['takeaway']+r'\end{tcolorbox}'+'\n')
        parts.append(r'\vfill{\footnotesize\color{navy}\textbf{Source anchors.} '+p['anchor']+'}\n')
    parts.append(r'\end{document}'+'\n')
    return ''.join(parts)

def md_document():
    parts=['# Hilbert 12: Cubic Divisor Transport and Reconstruction: Visual Guide\n\nKomorebi P. · October 7, 2026\n\n']
    for i,p in enumerate(PAGES):
        parts.append('## '+p['title']+'\n\n'+p['deck']+'\n\n')
        if p['figure']:
            parts.append('!['+p['caption']+'](figures/'+p['figure']+'.png)\n\n')
        if p.get('table'):
            table=p['table']
            parts.append('| '+' | '.join(table[0])+' |\n| '+' | '.join(['---']*len(table[0]))+' |\n')
            parts.extend('| '+' | '.join(row)+' |\n' for row in table[1:])
            parts.append('\n')
        for eq in p['equations']:parts.append('$$\n'+eq+'\n$$\n\n')
        parts.extend(para.replace(r'\textquotesingle s',"'s")+'\n\n' for para in p['paragraphs'])
        parts.append('**Takeaway.** '+p['takeaway']+'\n\n**Source anchors.** '+p['anchor']+'\n\n')
    parts.append('## Rebuild and finite controls\n\nRun `python generate_figures.py`, then `python build_guide.py` and `pdflatex -halt-on-error H12_Cubic_Divisor_Visual_Guide.tex` twice. Figures require NumPy and Matplotlib. All other script dependencies are from the Python standard library. `finite_control.json` records declared inputs, finite checks, arithmetic scope, software versions, and the figure-generator checksum. It does not replace source proofs, an infinite-product evaluation, or the unresolved arithmetic comparison.\n')
    return ''.join(parts)

(ROOT/'H12_Cubic_Divisor_Visual_Guide.tex').write_text(tex_document())
(ROOT/'H12_Cubic_Divisor_Visual_Guide.md').write_text(md_document())
(ROOT/'guide_content.json').write_text(json.dumps(PAGES,indent=2)+'\n')
(ROOT/'validation'/'source_anchors.json').write_text(json.dumps([{'page':i+1,'title':p['title'],'anchor':p['anchor']} for i,p in enumerate(PAGES)],indent=2)+'\n')
print(json.dumps({'pages':len(PAGES),'figure_pages':sum(bool(p['figure']) for p in PAGES)}))
