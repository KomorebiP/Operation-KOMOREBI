"""Verify the final finite-scope freeze against the immediate 0.9.0 source.

Hashes and source spans establish identity, not mathematical truth. No network.
"""
from pathlib import Path
import hashlib, importlib.util, json, re
ROOT=Path(__file__).resolve().parents[1]
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def spans(text):
    matches=list(re.finditer(r'\*\*Proposition (\d+)\..*?\\square\$',text,re.S))
    values={int(m.group(1)):m.group(0) for m in matches}
    if len(values)!=len(matches):raise ValueError('Duplicate proposition number')
    return values

def main():
    contract=json.loads((ROOT/'RELEASE_CONTRACT.json').read_text())
    if contract['version']!='1.0.0' or contract['propositions']!=87 or contract['new_propositions']!=0:
        raise ValueError('Frozen release identity changed')
    for flag in ['proof_kernel_verified','independent_external_review','production_runtime_modified','published','license_changed']:
        if contract[flag] is not False:raise ValueError('Unsupported claim: '+flag)
    old=ROOT/contract['preserved_prose']
    if digest(old)!=contract['preserved_prose_sha256']:raise ValueError('Preserved predecessor changed')
    before=spans(old.read_text());after=spans((ROOT/'theory/FOUNDATIONS.md').read_text())
    if set(before)!=set(range(1,88)) or before!=after:
        raise ValueError('A frozen proposition/proof passage changed')
    # Definitions and assumptions after Section 1 are also frozen, not only bold statements.
    marker='# 1. Three objects that must remain distinct'
    old_body=old.read_text().split(marker,1)[1]
    new_body=(ROOT/'theory/FOUNDATIONS.md').read_text().split(marker,1)[1]
    if old_body!=new_body:raise ValueError('Mathematical body or reference lineage changed')
    groups={}
    for field in ['unchanged_math_modules','unchanged_certificates','unchanged_fixed_inputs']:
        for name,expected in contract[field].items():
            p=ROOT/name
            if not p.resolve().is_relative_to(ROOT) or digest(p)!=expected:
                raise ValueError('Frozen artifact mismatch: '+name)
        groups[field]=len(contract[field])
    spec=importlib.util.spec_from_file_location('release_runner', ROOT/'run_reference_checks.py')
    runner=importlib.util.module_from_spec(spec);spec.loader.exec_module(runner)
    if runner.VERSION!='1.0.0' or len(runner.SCRIPTS)!=contract['expected_reference_programs']:
        raise ValueError('Replay script inventory changed')
    reg=json.loads((ROOT/'PROOF_REGISTER.json').read_text())
    if reg['version']!='1.0.0' or reg['proposition_count']!=87:raise ValueError('Register mismatch')
    report={'version':'1.0.0','passed':True,'unchanged_proposition_proof_spans':87,
            'entire_mathematical_body_and_references_unchanged':True,
            **groups,'reference_programs':len(runner.SCRIPTS),
            'proof_kernel_verified':False,'production_runtime_modified':False}
    (ROOT/'verification/release_freeze.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
