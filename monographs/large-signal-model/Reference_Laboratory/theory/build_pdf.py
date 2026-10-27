"""Build the cumulative volume, reader's guide and proof register offline.

Requires installed Pandoc and pdfLaTeX. No network access or font redistribution.
"""
from __future__ import annotations
from pathlib import Path
import argparse,re,shutil,subprocess,hashlib,json
ROOT=Path(__file__).resolve().parents[1]
THEORY=ROOT/'theory'
CONFIG={
'FOUNDATIONS':(r'Foundations of realization,\\refinement and predictive closure',r'87 propositions. Frozen finite scope.\\Exact witnesses and conditional learning.\\Unchanged mathematics from the audited candidate.'),
'READING_GUIDE':(r'A unified reading guide',r'From signal archives to predictive states.\\From transfer defects to valid inference.\\A map of what is supplied, learned and certified.'),
'VISUAL_ATLAS':(r'A visual atlas of the finite foundations',r'Thirteen preserved mathematical illustrations.\\State, transfer, probability and evidence.\\No new empirical performance claims.'),
'PROOF_REGISTER':(r'Proof, assumptions\\and evidence register',r'87 statement records.\\Principal dependencies and scope boundaries.\\Restricted source-to-code correspondence.')}

def compile_volume(stem: str) -> None:
    subtitle,cover=CONFIG[stem]
    template=(THEORY/'template.tex').read_text()
    template=template.replace('@@TITLE@@','Large Signal Model').replace('@@SUBTITLE@@',subtitle).replace('@@COVER@@',cover)
    template=template.replace('@@PDFTITLE@@', 'Komorebi Large Signal Model: ' + stem.replace('_', ' ').title() + ' 1.0.0')
    (THEORY/f'{stem}_template.tex').write_text(template)
    markdown=(THEORY/f'{stem}.md').read_text()
    if stem=='FOUNDATIONS':
        # Cover already carries the document title and edition. Keep the actual preface.
        at=markdown.find('This volume freezes')
        if at>=0:markdown=markdown[at:]
        markdown=markdown.replace('# References and source lineage',r'\begingroup'+'\n'+r'\small\raggedright'+'\n\n# References and source lineage')+'\n'+r'\endgroup'+'\n'
    markdown=(r'\begingroup\footnotesize\setlength{\cftbeforesecskip}{0pt}\tableofcontents\endgroup\newpage'+'\n\n'+markdown)
    if stem=='VISUAL_ATLAS':
        markdown=markdown.replace(r'\tableofcontents\endgroup\newpage',r'\tableofcontents\endgroup\bigskip',1)
    (THEORY/f'{stem}_body.md').write_text(markdown)
    subprocess.run(['pandoc',f'{stem}_body.md','--from','markdown+tex_math_dollars+raw_tex','--to','latex',
                    '--standalone','--template',f'{stem}_template.tex','--output',f'{stem}.tex'],cwd=THEORY,check=True)
    source=(THEORY/f'{stem}.tex').read_text()
    source=re.sub(r'\\texttt\{([^{}]+)\}',lambda m:r'\path{'+m.group(1).replace(r'\_','_')+'}',source)
    source=source.replace(r'\textbf{Proposition',r'\Needspace{5\baselineskip}'+'\n'+r'\textbf{Proposition')
    if stem=='PROOF_REGISTER':
        # Keep each evidence record whole, avoiding a stranded final paragraph.
        pattern=r'\\Needspace\{9\\baselineskip\}\s*(.*?)(?=\\Needspace\{9\\baselineskip\}|\\newpage|\\end\{document\})'
        source=re.sub(pattern,lambda m:r'\par\noindent\begin{minipage}{\textwidth}'+'\n'+m.group(1).rstrip()+'\n'+r'\end{minipage}\par\medskip'+'\n\n',source,flags=re.S)
    (THEORY/f'{stem}.tex').write_text(source)
    def pagination_state():
        return {ext:hashlib.sha256((THEORY/f'{stem}.{ext}').read_bytes()).hexdigest()
                for ext in ('aux','toc','out') if (THEORY/f'{stem}.{ext}').exists()}
    previous=None
    records=[]
    converged=False
    for idx in range(1,7):
        proc=subprocess.run(['pdflatex','-interaction=nonstopmode','-halt-on-error',f'{stem}.tex'],cwd=THEORY,
                            text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        (ROOT/'verification'/f'{stem}_latex_pass{idx}.log').write_text(proc.stdout)
        if proc.returncode:raise RuntimeError(f'{stem} compilation failed; see preserved log.')
        current=pagination_state()
        records.append({'pass':idx,'returncode':proc.returncode,'pagination_state':current})
        needs_rerun=any(message in proc.stdout for message in
                       ('Rerun to get cross-references right','Label(s) may have changed','Rerun to get outlines right'))
        if idx>=2 and current==previous and not needs_rerun:
            converged=True
            break
        previous=current
    (ROOT/'verification'/f'{stem}_latex_final.log').write_text(proc.stdout)
    (ROOT/'verification'/f'{stem}_build.json').write_text(json.dumps(
        {'document':stem,'converged':converged,'passes':records},indent=2)+'\n')
    if not converged:raise RuntimeError(f'{stem} pagination did not stabilize in six passes.')
    log=(THEORY/f'{stem}.log').read_text()
    if 'Overfull' in log:raise RuntimeError(f'{stem} has overfull boxes; inspect the log.')
    print(THEORY/f'{stem}.pdf')

def main() -> None:
    p=argparse.ArgumentParser();p.add_argument('document',choices=list(CONFIG)+['all'],default='all',nargs='?');a=p.parse_args()
    for tool in ['pandoc','pdflatex']:
        if not shutil.which(tool):raise RuntimeError('Missing '+tool)
    (ROOT/'verification').mkdir(exist_ok=True)
    for name in CONFIG:
        if a.document in ('all',name):compile_volume(name)
if __name__=='__main__':main()
