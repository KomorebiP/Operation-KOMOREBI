#!/usr/bin/env python3
"""Export a reading Markdown with the canonical PDF's labels and citations.
Requires an existing LaTeX .aux file and Pandoc. The LaTeX source remains canonical.
"""
from pathlib import Path
import re
import subprocess
import tempfile

ROOT=Path(__file__).resolve().parents[1]
BASE='Machine_Understanding_v1.0.0'
source=(ROOT/(BASE+'.tex')).read_text()
aux=(ROOT/'build'/(BASE+'.aux')).read_text()
labels={key:(num,page) for key,num,page in re.findall(r'\\newlabel\{([^}]+)\}\{\{([^}]*)\}\{([^}]*)\}',aux)}
keys=re.findall(r'\\bibitem\{([^}]+)\}',source)
cites={k:str(i+1) for i,k in enumerate(keys)}
# Replace references before Pandoc can renumber custom theorem environments.
source=re.sub(r'\\cite\{([^}]+)\}',lambda m:'['+', '.join(cites[k.strip()] for k in m[1].split(','))+']',source)
source=re.sub(r'\\eqref\{([^}]+)\}',lambda m:'('+labels[m[1]][0]+')',source)
source=re.sub(r'\\ref\{([^}]+)\}',lambda m:labels[m[1]][0],source)
# Preserve theorem headings with their actual LaTeX numbers.
pat=r'\\begin\{(theorem|proposition|definition|counterexample)\}\[([^\]]+)\]\\label\{([^}]+)\}'
source=re.sub(pat,lambda m:r'\paragraph{'+m[1].capitalize()+' '+labels[m[3]][0]+' ('+m[2]+').}',source)
source=re.sub(r'\\end\{(?:theorem|proposition|definition|counterexample)\}','',source)
source=source.replace(r'\begin{proof}',r'\paragraph{Proof.}').replace(r'\end{proof}','')
source=re.sub(r'\\section\{([^}]+)\}\\label\{([^}]+)\}',lambda m:r'\section*{'+labels[m[2]][0]+' '+m[1]+'}',source)
abstract=source.split(r'\large\bfseries Abstract}\par\smallskip')[1].split(r'\vfill')[0].strip()
abstract=abstract.removeprefix(r'\noindent ')
front=r'''\section*{Machine Understanding}
\subsection*{Representation, Explanation, and Transfer}
Komorebi P.\par
8 October 2026. Version 1.0.0. First consolidated edition.\par
Reading edition. The LaTeX source and PDF are canonical for layout and numbering.\par
\subsection*{Abstract}
'''+abstract
source=re.sub(r'\\begin\{titlepage\}.*?\\end\{titlepage\}',lambda m:front,source,flags=re.S)
source=re.sub(r'\\label\{[^}]+\}','',source)
source=re.sub(r'\\addcontentsline\{[^}]+\}\{[^}]+\}\{[^}]+\}','',source)
source=source.replace(r'\tableofcontents','')
source=re.sub(r'\\begin\{thebibliography\}\{99\}.*?\n(?=\\bibitem)',lambda m:r'\section*{References}\n',source,flags=re.S)
source=source.replace(r'\end{thebibliography}','')
source=re.sub(r'\\bibitem\{([^}]+)\}',lambda m:r'\paragraph{['+cites[m[1]]+']}',source)
source=re.sub(r'(figures/[^}]+)\.pdf}',r'\1.png}',source)
# Pandoc does not infer custom P-column widths in tabularx. These are layout
# choices, so replace them by ordinary alignment columns for the reading edition.
for spec, columns in [(r'@{}lX@{}','ll'),
                      (r'@{}P{1.35in}XX@{}','lll'),
                      (r'@{}P{1.1in}P{1.55in}X@{}','lll'),
                      (r'@{}P{1.7in}P{.7in}X@{}','lll')]:
    source=source.replace(r'\begin{tabularx}{\textwidth}{'+spec+'}',
                          r'\begin{tabular}{'+columns+'}')
source=source.replace(r'\end{tabularx}',r'\end{tabular}')
with tempfile.TemporaryDirectory() as td:
    temp=Path(td)/'reading.tex';temp.write_text(source)
    result=subprocess.run(['pandoc','-f','latex','-t','gfm','--wrap=none',str(temp)],text=True,capture_output=True,check=True)
    text=result.stdout
    text=text.replace('<div class="center">\n','').replace('</div>\n','')
    (ROOT/(BASE+'.md')).write_text(text)
    (ROOT/'validation'/'markdown_export.json').write_text(__import__('json').dumps({
        'status':'completed','canonical_source':BASE+'.tex',
        'label_count':len(labels),'bibliographic_entries':len(cites),
        'proof_headings':text.count('#### Proof.'),
        'pandoc_stderr':result.stderr,
        'scope':'Readable mathematical text; PDF controls pagination and exact layout.'},indent=2)+'\n')
print(f'Wrote reading Markdown with canonical labels and {len(cites)} numbered references.')
