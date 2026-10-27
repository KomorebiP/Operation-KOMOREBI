#!/usr/bin/env python3
"""Recheck inherited integrity and saved-record parity. Does NOT run Lean."""
from __future__ import annotations
import argparse, collections, hashlib, json, os, re, shutil, subprocess, sys, tempfile
from datetime import datetime, timezone
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ORIGINAL=ROOT/'original_snapshot'
FORMAL=ORIGINAL/'lean_release/PRSC_IV'
REVIEW=ORIGINAL/'proofread_review/PRSC_IV_Review'

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def verify_manifest(root:Path,name:str)->int:
    n=0
    for line in (root/name).read_text().splitlines():
        if not line.strip():continue
        expected,relative=line.split(maxsplit=1);relative=relative.lstrip('*')
        target=(root/relative).resolve()
        if root.resolve() not in target.parents:raise RuntimeError(f'Unsafe manifest entry: {relative}')
        if sha(target)!=expected:raise RuntimeError(f'Inherited checksum mismatch: {relative}')
        n+=1
    return n

def main()->None:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir',type=Path,default=ROOT/'rebuilt/original_static_audit')
    args=parser.parse_args();out=args.output_dir.resolve()
    if out==ORIGINAL or ORIGINAL in out.parents:raise RuntimeError('Output may not overwrite the original snapshot.')
    out.mkdir(parents=True,exist_ok=True)
    formal_hashes=verify_manifest(FORMAL,'SHA256SUMS.txt')
    review_hashes=verify_manifest(REVIEW,'REVIEW_SHA256SUMS.txt')
    contract=json.loads((FORMAL/'verification/lean_contract_v1.0.0.json').read_text())
    targets=contract['targets'];names={x['declaration'] for x in targets}
    transcript=(FORMAL/'formalization/lean/kernel_audit_output.txt').read_text()
    pattern=r"'([^']+)' (?:depends on axioms:\s*\[([^\]]*)\]|(does not depend on any axioms))"
    parsed={}
    for name,axioms,none in re.findall(pattern,transcript):
        if name in parsed:raise RuntimeError('Repeated inherited target report: '+name)
        parsed[name]=[] if none else [a.strip() for a in axioms.split(',') if a.strip()]
    if set(parsed)!=names:raise RuntimeError('Saved audit target set differs from contract.')
    allowed={'propext','Classical.choice','Quot.sound'}
    if any(set(v)-allowed for v in parsed.values()):raise RuntimeError('Saved report lists an unexpected axiom.')
    tex=(FORMAL/'paper/paper4.tex').read_text()
    counts=collections.Counter(re.findall(r'\\begin\{(theorem|proposition|corollary|lemma|standardfact)\}',tex))
    env=os.environ.copy();env['PYTHONDONTWRITEBYTECODE']='1'
    with tempfile.TemporaryDirectory(prefix='paper_iv_register_') as td:
        tmp=Path(td)/'PRSC_IV';shutil.copytree(FORMAL,tmp)
        before=(tmp/'provenance/THEOREM_REGISTER.md').read_bytes()
        proc=subprocess.run([sys.executable,'scripts/generate_register.py'],cwd=tmp,env=env,capture_output=True,text=True,timeout=60)
        (out/'register_replay.log').write_text(proc.stdout+proc.stderr)
        if proc.returncode:raise RuntimeError('Register generator failed; inspect register_replay.log')
        if (tmp/'provenance/THEOREM_REGISTER.md').read_bytes()!=before:raise RuntimeError('Regenerated register differs from original.')
        register=before.decode();record_count=len(re.findall(r'^\|\s*\d+\.\d+\s*\|',register,re.M))
    source_files=[p for p in ORIGINAL.rglob('*') if p.is_file()]
    lean_files=list(FORMAL.rglob('*.lean'))
    report={'status':'PASS','generated_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Inherited SHA manifests, source census, register replay, and SAVED audit/contract parity. Not proof checking.',
        'original_snapshot_files':len(source_files),'formal_manifest_entries_verified':formal_hashes,
        'review_manifest_entries_verified':review_hashes,'lean_source_files':len(lean_files),
        'register_reproduced_byte_for_byte':True,'manuscript_register_records':record_count,
        'manuscript_environment_counts':dict(counts),'scoped_theorem_like_records':sum(counts[k] for k in ('theorem','proposition','corollary','lemma')),
        'saved_contract_targets':len(names),'saved_target_kind_counts':dict(collections.Counter(x['kind'] for x in targets)),
        'saved_audit_exact_target_set':True,'saved_reports_allowed_axioms_only':True,
        'new_lean_invocation':False,'saved_namespace_counts_not_regenerated':True}
    (out/'ORIGINAL_STATIC_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {formal_hashes} formal and {review_hashes} review hashes, {len(lean_files)} Lean sources, {len(names)} saved-target records; no Lean invocation.')

if __name__=='__main__':
    try:main()
    except (OSError,RuntimeError,ValueError,subprocess.SubprocessError) as exc:raise SystemExit(f'Original static audit failed: {exc}')
