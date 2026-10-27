#!/usr/bin/env python3
"""Generate the source-facing companion from the resolved claim ledger."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]

def escape(s):
    return s.replace('&',r'\&').replace('%',r'\%').replace('_',r'\_').replace('#',r'\#')

def main():
    rows=json.loads((ROOT/'data/claim_ledger.json').read_text())
    lines=[]
    for r in rows:
        lines.append(r'\par\noindent\begin{minipage}{\linewidth}\subsection*{'+r['id']+' / '+escape(r['title'])+'}')
        lines.append(escape(r['correspondence_note']))
        for ref in r['source_refs']:
            lines.append(r'\par\smallskip\noindent{\small\textbf{'+ref['tree']+'} '+r'\path{'+ref['module']+'.lean}'+', line '+str(ref['line_start'])+r'.\par\noindent\path{'+ref['declaration']+r'}\par{\sffamily\footnotesize Source SHA-256 prefix: '+ref['sha256'][:16]+r'.}}\par')
        if not r['source_refs']:
            lines.append(r'\par\smallskip\noindent\textbf{W.} The proof is written in the monograph. No new Lean declaration or compiler verification is claimed.')
        lines.append(r'\smallskip\noindent{\color{KomorebiMuted}\rule{\linewidth}{.3pt}}\par\end{minipage}\par\medskip')
    (ROOT/'source/guide_entries.tex').write_text('\n'.join(lines)+'\n')
    print(f'Generated {len(rows)} source-concordance entries.')

if __name__=='__main__':main()
