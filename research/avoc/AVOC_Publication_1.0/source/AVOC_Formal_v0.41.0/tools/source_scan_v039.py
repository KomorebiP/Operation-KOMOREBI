#!/usr/bin/env python3
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
files=sorted([p for p in (ROOT/'AVOC').glob('*.lean') if p.name not in {'Audit.lean','FullAudit.lean'}] + list((ROOT/'tools').glob('*.lean')))
patterns={
 'sorry':re.compile(r'\bsorry\b'),
 'native_decide':re.compile(r'\bnative_decide\b'),
 'axiom':re.compile(r'^\s*axiom\s+',re.M),
 'unsafe_decl':re.compile(r'^\s*unsafe\s+(?:theorem|lemma|def)\b',re.M),
 'proof_admit':re.compile(r'\bby\s+admit\b|\bexact\s+admit\b|^\s*admit\s*$',re.M),
}
def strip_comments(s):
    s=re.sub(r'/\*.*?\*/','',s,flags=re.S)
    s=re.sub(r'--.*','',s)
    return s
hits=[]
for p in files:
    text=strip_comments(p.read_text())
    for kind,rx in patterns.items():
        for m in rx.finditer(text):
            hits.append({'source':str(p.relative_to(ROOT)),'kind':kind,'line':text[:m.start()].count('\n')+1,'text':m.group(0)})
result={'files':len(files),'hits':hits}
(ROOT/'results/v0.39.0/source_scan.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
raise SystemExit(1 if hits else 0)
