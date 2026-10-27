#!/usr/bin/env python3
"""Export the actual traditional manuscript with all claims, math and sources."""
from pathlib import Path
import json, re, subprocess

HERE=Path(__file__).resolve().parent
BT=chr(96)
tex=HERE/'Sufficient_Resolution_Traditional.tex'
data=json.loads((HERE/'Claim_Lean_Concordance.json').read_text())
result=subprocess.run(['pandoc','-f','latex','-t','markdown','--wrap=none',str(tex)],
                      check=True,capture_output=True,text=True)
s=result.stdout
title_end=s.index('# The problem and its mathematical contracts')
s=s[title_end:]
for c in data['claims']:
    needle='*Formal source:* .'
    if needle not in s: raise ValueError('Missing formal-source insertion point')
    source='**Formal source:** '+ '; '.join(BT+a['name']+BT for a in c['anchors'])+'.'
    s=s.replace(needle,source,1)
if '*Formal source:* .' in s: raise ValueError('Unfilled formal-source point')
s=re.sub(r'\(SR-(\d{2})([^ )])',r'(SR-\1: \2',s)
s='\n'.join(line for line in s.splitlines() if not line.startswith(':::'))+'\n'
abstract=re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}',tex.read_text(),re.S).group(1)
abstract=' '.join(abstract.split())
front=('# Sufficient Resolution\n\n'
       '## Exact Reduction, Hidden Memory, and Certified Reconstruction\n\n'
       '**Komorebi P. — Final edition, October 6, 2026**\n\n'
       'The complete source ZIP includes the .md files, editable manuscript sources, '
       'Lean sources, exact Python companions, example data, and verification records.\n\n'
       '### Abstract\n\n'+abstract+'\n\n')
s=front+s
ids=re.findall(r'\*\*Theorem \d+\*\* \(SR-(\d{2}):',s)
if ids!=[f'{i:02d}' for i in range(1,65)]: raise ValueError(f'Claim headings lost: {ids}')
anchors=re.findall(BT+r'(Komorebi\.SufficientResolution\.[^'+BT+']+)'+BT,s)
expected=[a['name'] for c in data['claims'] for a in c['anchors']]
if anchors!=expected: raise ValueError('Formal-source anchors changed in Markdown export')
if len(re.findall(r'\*Proof\.\*',s))!=64: raise ValueError('A prose proof was lost')
out=HERE/'Sufficient_Resolution_Traditional.md'
out.write_text(s)
print(json.dumps({'markdown':str(out),'claims':len(ids),'proofs':64,
                  'source_anchors':len(anchors),'display_math_delimiters':s.count('$$')}))
