#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys, tempfile, zipfile
from pathlib import Path

ROOT=Path(__file__).resolve().parent

def sha(path: Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for ch in iter(lambda:f.read(1<<20),b''):
            h.update(ch)
    return h.hexdigest()

def run_json(script: Path):
    cp=subprocess.run([sys.executable,'-B',str(script)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=180)
    if cp.returncode!=0:
        raise RuntimeError(f'{script} failed: {cp.stderr}')
    return json.loads(cp.stdout), cp.stderr

def check_manifest():
    mp=ROOT/'MANIFEST.json'
    obj=json.loads(mp.read_text())
    for rel, expected in obj['sha256'].items():
        p=ROOT/rel
        if not p.is_file(): raise AssertionError(f'missing payload {rel}')
        got=sha(p)
        if got!=expected: raise AssertionError(f'hash mismatch {rel}')
    actual=set()
    for p in ROOT.rglob('*'):
        if p.is_file() and p.name!='MANIFEST.json' and '__pycache__' not in p.parts:
            actual.add(p.relative_to(ROOT).as_posix())
    declared=set(obj['sha256'])
    if actual!=declared:
        raise AssertionError(f'member set mismatch extra={sorted(actual-declared)} missing={sorted(declared-actual)}')
    return len(declared)

def replay_predecessor():
    z=ROOT/'predecessor/Komorebi_Beal_Block76_Exact_Cyclotomic_Image_v7.6.0.zip'
    with tempfile.TemporaryDirectory(prefix='b76_replay_') as td:
        td=Path(td)
        with zipfile.ZipFile(z) as zz: zz.extractall(td)
        candidates=list(td.rglob('verify.py'))
        if not candidates: raise RuntimeError('predecessor verify.py not found')
        # choose shallowest root verifier
        vp=min(candidates,key=lambda p:len(p.parts))
        cp=subprocess.run([sys.executable,'-B',vp.name,'--report',str(td/'Block76_Replay.json')],cwd=vp.parent,
                          stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=300)
        if cp.returncode!=0:
            raise RuntimeError('predecessor replay failed\n'+cp.stdout+'\n'+cp.stderr)
        return cp.stdout.strip()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--report',type=Path)
    ap.add_argument('--replay-predecessor',action='store_true')
    args=ap.parse_args()
    primary,_=run_json(ROOT/'work77/computations/cochain77.py')
    independent,_=run_json(ROOT/'work77/computations/independent77.py')
    frozen1=json.loads((ROOT/'work77/verification/cochain77.json').read_text())
    frozen2=json.loads((ROOT/'work77/verification/independent77.json').read_text())
    if primary!=frozen1: raise AssertionError('primary output does not match frozen JSON')
    if independent!=frozen2: raise AssertionError('independent output does not match frozen JSON')
    if primary['status']!='PASS' or independent['status']!='PASS': raise AssertionError('scientific status not PASS')
    if primary['heisenberg_commuting_control']['R_xz']!=2 or primary['heisenberg_commuting_control']['R_zx']!=0:
        raise AssertionError('Heisenberg negative control changed')
    if independent['heisenberg_R_pair']!=[2,0]: raise AssertionError('independent negative control changed')
    # Deliberate corruption rejection: an altered scientific result must disagree.
    corrupted=dict(primary); corrupted['scalar_exhaustive_cases']+=1
    if corrupted==frozen1: raise AssertionError('corruption test failed')
    payload_count=check_manifest()
    pred=ROOT/'predecessor/Komorebi_Beal_Block76_Exact_Cyclotomic_Image_v7.6.0.zip'
    pred_hash=sha(pred)
    predecessor_stdout=None
    if args.replay_predecessor:
        predecessor_stdout=replay_predecessor()
    out={
      'status':'PASS_DECLARED_CHECKS',
      'version':'7.7.0',
      'primary_status':primary['status'],
      'independent_status':independent['status'],
      'primary_scalar_cases':primary['scalar_exhaustive_cases'],
      'primary_field_cases':primary['field_slice_cases'],
      'heisenberg_pair_checks':primary['heisenberg_pair_checks'],
      'payload_files_checked':payload_count,
      'predecessor_sha256':pred_hash,
      'replayed_immediate_predecessor':bool(args.replay_predecessor),
      'predecessor_stdout_tail': predecessor_stdout[-500:] if predecessor_stdout else None,
      'nonclaims':[
        'finite checks do not prove the universal cochain identities',
        'no Block70/76 arithmetic pattern is eliminated',
        'default replay is not a full historical-chain replay',
        'no Lean compilation or independent mathematical review is claimed'
      ]
    }
    if args.report:
        args.report.parent.mkdir(parents=True,exist_ok=True)
        args.report.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS_DECLARED_CHECKS')
    print(json.dumps(out,indent=2,sort_keys=True))
    return 0
if __name__=='__main__': raise SystemExit(main())
