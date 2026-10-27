#!/usr/bin/env python3
"""Check source integrity and evidence bookkeeping, not theorem truth."""
from pathlib import Path
import collections, hashlib, json, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'previous/Komorebi_Seeded_Two_Axis_Calculus_v0.9.0.tex'
TEX=ROOT/'Komorebi_Seeded_Two_Axis_Calculus_v0.10.0.tex'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def blocks(s):
    return [m.group(0) for m in re.finditer(r'\\begin\{(theorem|lemma|proposition|corollary|proof)\}.*?\\end\{\1\}',s,re.S)]

def main():
    source=TEX.read_text(); base=BASE.read_text(); before=sha(TEX)
    inherited=blocks(base); current=blocks(source); j=0
    for b in current:
        if j<len(inherited) and b==inherited[j]:j+=1
    assert j==len(inherited),'An inherited theorem/proof block was changed or removed.'
    labels=re.findall(r'\\label\{([^}]+)\}',source)
    duplicate=[k for k,v in collections.Counter(labels).items() if v>1]
    assert not duplicate,duplicate
    used=[]
    for match in re.finditer(r'\\(?:c|C|eq|page)?ref\{([^}]+)\}',source): used.extend(match.group(1).split(','))
    missing=sorted(set(used)-set(labels)); assert not missing,missing
    cites=[]
    for m in re.finditer(r'\\cite(?:\[[^\]]*\])*\{([^}]+)\}',source):cites.extend(m.group(1).split(','))
    keys=re.findall(r'\\bibitem\{([^}]+)\}',source)
    assert not(set(cites)-set(keys)),set(cites)-set(keys)
    assert len(keys)==len(set(keys))
    ledger=[int(x) for x in re.findall(r'^K(\d+) &',source,re.M)]
    assert ledger==list(range(1,72)),ledger
    hashes=json.loads((ROOT/'audit/base_sha256.json').read_text())
    for name,digest in hashes.items():assert sha(ROOT/'previous'/name)==digest,name
    log=(ROOT/'audit/latex_final.log').read_text()
    warnings=[x for x in log.splitlines() if re.search(r'Warning|Overfull|Underfull|undefined|multiply defined|^!',x)]
    assert not warnings,warnings
    manifest=json.loads((ROOT/'checks/all_runs.json').read_text());assert manifest['status']=='PASS'
    assert len(manifest['runs'])==5
    for run in manifest['runs']:
        script=ROOT/'checks'/Path(run['argv'][1]).name
        assert sha(script)==run['script_sha256_after']==run['script_sha256_before']
        assert sha(ROOT/run['output'])==run['output_sha256']
    process=subprocess.run([sys.executable,str(ROOT/'audit/integrate_v0100.py')],cwd=ROOT,capture_output=True,text=True,check=True)
    assert before==sha(TEX),'The integration script did not regenerate the exact current source.'
    result={'status':'PASS','inherited_theorem_and_proof_blocks':len(inherited),'current_theorem_and_proof_blocks':len(current),
            'inherited_blocks_preserved_verbatim':True,'ledger_entries':len(ledger),'labels':len(labels),
            'duplicate_labels':duplicate,'missing_references':missing,'latex_warnings':warnings,
            'all_five_suites_passed_with_matching_hashes':True,'source_reconstruction_identical':True,
            'base_files_match_hashes':True,'source_sha256':sha(TEX),
            'evidence_boundary':'Static structure/provenance checks only. Written proofs are self-reviewed, not kernel-checked.'}
    (ROOT/'audit/static_source_checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
