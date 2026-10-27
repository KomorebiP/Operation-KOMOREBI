#!/usr/bin/env python3
"""Build the reader guide from its editable Markdown and verified inventories."""
from __future__ import annotations
import json,pathlib,re,subprocess,sys

HERE=pathlib.Path(__file__).resolve().parent
PREFIX='Komorebi.SufficientResolution.'
PREAMBLE=r'''\documentclass[11pt]{article}
\usepackage[letterpaper,margin=.85in,headheight=15pt]{geometry}
\usepackage[T1]{fontenc}
\usepackage{lmodern,microtype,amsmath,amssymb,amsthm}
\usepackage{booktabs,longtable,array,enumitem,xcolor,seqsplit,calc}
\usepackage{listings,tcolorbox,fancyhdr,titlesec,hyperref}
\definecolor{Navy}{HTML}{17324D}
\definecolor{Teal}{HTML}{2F7A78}
\definecolor{Pale}{HTML}{E7F0F6}
\hypersetup{colorlinks=true,linkcolor=Navy,urlcolor=Teal,pdfauthor={Komorebi P.},pdftitle={Sufficient Resolution: Lean Guide and Formalization Concordance}}
\pagestyle{fancy}\fancyhf{}\fancyhead[L]{\small Sufficient Resolution: Lean Guide}\fancyhead[R]{\small Komorebi P.}\fancyfoot[C]{\thepage}
\titleformat{\section}{\Large\bfseries\color{Navy}}{\thesection}{.7em}{}
\titleformat{\subsection}{\large\bfseries\color{Navy}}{\thesubsection}{.6em}{}
\setlength{\parindent}{0pt}\setlength{\parskip}{5pt}
\setlist{itemsep=3pt,topsep=4pt}
\lstset{basicstyle=\small\ttfamily,breaklines=true,columns=fullflexible,backgroundcolor=\color{Pale},frame=single,framerule=0pt,xleftmargin=6pt,xrightmargin=6pt}
\newtcolorbox{scopebox}{colback=Pale,colframe=Navy,boxrule=.5pt,arc=0pt}
\newcommand{\tightlist}{\setlength{\itemsep}{0pt}\setlength{\parskip}{0pt}}
\allowdisplaybreaks
\begin{document}
\hypersetup{pageanchor=false}
\begin{titlepage}
\vspace*{1.0in}
{\large\color{Teal}\textsc{Operation Komorebi}}\par\vspace{.35in}
{\Huge\bfseries\color{Navy}Sufficient Resolution}\par\vspace{.2in}
{\LARGE Lean Guide and\par Formalization Concordance}\par\vspace{.45in}
{\large Komorebi P.}\par\vspace{.18in}
{\large Final Edition\quad October 6, 2026}\par\vspace{.6in}
\begin{scopebox}
An exact source map for split representation, behavioral reduction,
hidden memory, and certified Hilbert-space reconstruction.
\end{scopebox}
\vfill
93 production modules. 998 theorem/lemma declarations.\par
Full Markdown, Lean sources, inventories, and verification records included.\par
Archived proof checks and fresh finite tests are explicitly distinguished.
\end{titlepage}
\hypersetup{pageanchor=true}
\setcounter{tocdepth}{1}
\begingroup\small\setlength{\parskip}{0pt}\tableofcontents\endgroup\clearpage
'''

def texcode(s):
    s=s.replace(r'\_', '_').replace(r'\#','#').replace(r'\&','&')
    escaped=s.replace('_',r'\_').replace('#',r'\#').replace('&',r'\&')
    if ' ' in s or (len(s)<24 and not any(c in s for c in './_')):
        return '\\texttt{'+escaped+'}'
    return '\\texttt{\\seqsplit{'+escaped+'}}'

def main():
    declarations=json.loads((HERE/'Declaration_Inventory.json').read_text())
    by_name={x['name']:x for x in declarations}
    md=(HERE/'Sufficient_Resolution_Lean_Guide.md').read_text().split('<!-- GENERATED APPENDICES -->',1)[0].rstrip()+'\n'
    shortnames=[]; missing=[]
    for value in re.findall(r'`([^`\n]+)`',md):
        if re.match(r'^[A-Z][A-Za-z]+\.[A-Za-z_][\w.]*$',value):
            if PREFIX+value in by_name: shortnames.append(value)
            elif value not in ['Classical.choice','Quot.sound','SufficientResolution.lean','Metric.infDist','Komorebi.SufficientResolution.','Komorebi.SufficientResolution']: missing.append(value)
    if missing:
        print(json.dumps({'unresolved_declaration_anchors':missing},indent=2));sys.exit(2)
    body=md.split('\\newpage',1)[1].strip()
    frag=subprocess.run(['pandoc','--from=markdown+tex_math_dollars','--to=latex','--listings'],
                        input=body,text=True,capture_output=True,check=True).stdout
    frag=re.sub(r'\\passthrough\{\\lstinline(.)((?:(?!\1).)*)\1\}',
                lambda m:texcode(m.group(2)),frag)
    frag=frag.replace('[language=Lean]','').replace('[language=bash]','')
    modules=json.loads((HERE/'Module_Inventory.json').read_text())
    audit=json.loads((HERE/'INVENTORY_AUDIT.json').read_text())
    appendix='\\clearpage\n\\section{Production module inventory}\n'
    appendix+='All counts below are textual source counts. The source hashes, imports, and declaration locations are supplied in the full CSV and JSON inventories.\n'
    appendix+=r'''\begingroup\small
\begin{longtable}{@{}p{.62in}p{3.50in}rr@{}}
\toprule Block & Module & Thm./lemma & Named\\\midrule\endfirsthead
\toprule Block & Module & Thm./lemma & Named\\\midrule\endhead
\midrule\multicolumn{4}{r}{Continued on next page}\\\endfoot
\bottomrule\endlastfoot
'''
    for m in sorted(modules,key=lambda x:(x['block'],x['module'])):
        appendix+=f"{m['block']:02d} & {texcode(m['module'])} & {m['theorem_lemma_count']} & {m['named_declaration_count']}\\\\\n"
    appendix+='\\midrule Total & 93 modules & 998 & 1,159\\\\\n\\end{longtable}\n\\endgroup\n'
    appendix+='\\clearpage\n\\section{Development block census}\n'
    appendix+='These are additions by historical development block, not counts of independent claims.\n'
    appendix+=r'''\begin{longtable}{@{}rrrr@{}}
\toprule Block & Modules added & Thm./lemma added & Named added\\\midrule\endfirsthead
\toprule Block & Modules added & Thm./lemma added & Named added\\\midrule\endhead
\bottomrule\endlastfoot
'''
    for row in audit['block_counts']:
        appendix+=f"{row['block']:02d} & {row['modules']} & {row['theorem_lemma']} & {row['named_declarations']}\\\\\n"
    appendix+='\\end{longtable}\n'
    map_path=HERE/'Claim_Lean_Concordance.json'
    if map_path.exists():
        maps=json.loads(map_path.read_text())
        appendix+='\\clearpage\n\\section{Traditional claim concordance}\n'
        appendix+='Each stable paper claim maps to the declarations named below. These are representative proof anchors; full signatures, dependencies, and hypotheses remain in the source. The formula and hypothesis synopsis is retained in the machine-readable concordance.\n'
        appendix+=r'''\begingroup\small
\begin{longtable}{@{}>{\raggedright\arraybackslash}p{.60in}>{\raggedright\arraybackslash}p{2.05in}>{\raggedright\arraybackslash}p{3.80in}@{}}
\toprule ID & Claim group & Representative declarations\\\midrule\endfirsthead
\toprule ID & Claim group & Representative declarations\\\midrule\endhead
\midrule\multicolumn{3}{r}{Continued on next page}\\\endfoot
\bottomrule\endlastfoot
'''
        for row in maps:
            anchors=[name[len(PREFIX):] if name.startswith(PREFIX) else name for name in row['declarations']]
            appendix+=texcode(row['claim_id'])+' & '+row['title'].replace('&',r'\&')+' & '+'\\par '.join(texcode(x) for x in anchors)+'\\\\[4pt]\n'
        appendix+='\\end{longtable}\n\\endgroup\n'
    md_appendix='\n<!-- GENERATED APPENDICES -->\n\n# Production module inventory\n\n'
    md_appendix+='All counts are textual source counts. Full hashes and imports are in the CSV and JSON inventories.\n\n'
    md_appendix+='| Block | Module | Theorem/lemma | Named |\n|---|---|---:|---:|\n'
    for m in sorted(modules,key=lambda x:(x['block'],x['module'])):
        md_appendix+=f"| {m['block']:02d} | `{m['module']}` | {m['theorem_lemma_count']} | {m['named_declaration_count']} |\n"
    md_appendix+='| Total | 93 modules | 998 | 1,159 |\n\n# Development block census\n\n'
    md_appendix+='| Block | Modules added | Theorem/lemma added | Named added |\n|---|---:|---:|---:|\n'
    for row in audit['block_counts']:
        md_appendix+=f"| {row['block']:02d} | {row['modules']} | {row['theorem_lemma']} | {row['named_declarations']} |\n"
    if map_path.exists():
        md_appendix+='\n# Traditional claim concordance\n\nRepresentative proof anchors. Full hypotheses and dependencies remain in the source.\n\n'
        md_appendix+='| ID | Claim group | Representative declarations |\n|---|---|---|\n'
        for row in maps:
            md_appendix+='| '+row['claim_id']+' | '+row['title']+' | '+'; '.join('`'+x+'`' for x in row['declarations'])+' |\n'
    (HERE/'Sufficient_Resolution_Lean_Guide.md').write_text(md+md_appendix)
    (HERE/'Sufficient_Resolution_Lean_Guide.tex').write_text(PREAMBLE+frag+appendix+'\\end{document}\n')
    inspection={'status':'PASS_SOURCE_ANCHOR_RESOLUTION','inline_source_anchor_occurrences':len(shortnames),
                'unique_inline_source_anchors':len(set(shortnames)),'full_inventory_rows':len(declarations),
                'unresolved_declaration_anchors':[],'fresh_lean_compilation':False}
    (HERE/'GUIDE_SOURCE_AUDIT.json').write_text(json.dumps(inspection,indent=2)+'\n')
    for _ in range(3):
        p=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error','Sufficient_Resolution_Lean_Guide.tex'],cwd=HERE,capture_output=True,text=True)
        if p.returncode:
            print(p.stdout[-6000:]);sys.exit(p.returncode)
    print(json.dumps(inspection))

if __name__=='__main__': main()
