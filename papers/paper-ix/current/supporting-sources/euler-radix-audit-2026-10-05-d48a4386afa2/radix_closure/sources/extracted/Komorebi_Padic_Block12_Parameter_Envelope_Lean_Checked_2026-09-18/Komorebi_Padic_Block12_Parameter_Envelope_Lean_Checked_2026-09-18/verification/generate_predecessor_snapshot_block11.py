#!/usr/bin/env python3
from __future__ import annotations
import hashlib, json, re
from pathlib import Path

THEOREM_START = re.compile(r"^\s*(?:@\[[^\]]+\]\s*)*(?:protected\s+)?(?:theorem|lemma)\s+([A-Za-z0-9_'.]+)\b")

def sha256(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1<<20), b''):
            h.update(b)
    return h.hexdigest()

def theorem_headers(lean_root: Path) -> dict[str,dict[str,str]]:
    out={}
    for path in sorted((lean_root/'KomorebiPadic').glob('*.lean')):
        lines=path.read_text(encoding='utf-8').splitlines()
        i=0
        while i < len(lines):
            m=THEOREM_START.match(lines[i])
            if not m:
                i+=1; continue
            name=m.group(1); acc=[lines[i]]
            while ':=' not in acc[-1]:
                i+=1
                if i>=len(lines): raise RuntimeError(f'unterminated theorem header {name} in {path}')
                acc.append(lines[i])
            out[name]={
                'header':' '.join('\n'.join(acc).split(':=',1)[0].split()),
                'file':str(path.relative_to(lean_root.parent)),
            }
            i+=1
    return out

def main():
    project=Path(__file__).resolve().parents[1]
    predecessor=Path('/mnt/data/padic_block11_work/Komorebi_Padic_COMPLETE_2026-09-18_Block10_Closed_Budget_Lean_Checked/blocks/Block10')
    headers=theorem_headers(predecessor/'lean')
    report={
      'schema':'komorebi-padic-block10-theorem-snapshot-v1',
      'authoritative_predecessor':str(predecessor),
      'theorem_count':len(headers),
      'headers':headers,
      'source_files':{
        str(p.relative_to(predecessor)):sha256(p)
        for p in sorted((predecessor/'lean').rglob('*.lean'))
      },
    }
    out=project/'predecessor'/'BLOCK10_THEOREM_HEADERS.json'
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({'theorem_count':len(headers),'output':str(out)},indent=2))
    if len(headers)!=152: raise SystemExit(f'expected 152 predecessor theorems, got {len(headers)}')
if __name__=='__main__': main()
