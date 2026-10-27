#!/usr/bin/env python3
"""Scan actual Lean tokens for forbidden proof shortcuts, including nested comments."""
import json,re
from release_common_v041 import ROOT,RD,source_files,masked_lean,sha,write_json
PATTERNS={
 'sorry':re.compile(r'\bsorry\b'), 'native_decide':re.compile(r'\bnative_decide\b'),
 'axiom':re.compile(r'\baxiom\s+'), 'unsafe_decl':re.compile(r'\bunsafe\s+(?:theorem|lemma|def)\b'),
 'proof_admit':re.compile(r'\bby\s+admit\b|\bexact\s+admit\b|^\s*admit\s*(?:$|;)|;\s*admit\b',re.M),
}
def collect():
    files=source_files();hits=[]
    for source in files:
        text=masked_lean((ROOT/source).read_text())
        for kind,pattern in PATTERNS.items():
            for match in pattern.finditer(text):
                hits.append(dict(source=source,kind=kind,line=text[:match.start()].count('\n')+1,text=match.group(0)))
    return dict(files=len(files),source_sha256={source:sha(ROOT/source) for source in files},hits=hits)
def main():
    result=collect();write_json(RD/'source_scan.json',result)
    print(json.dumps({'files':result['files'],'hits':result['hits']},indent=2))
    return 1 if result['hits'] else 0
if __name__=='__main__':raise SystemExit(main())
