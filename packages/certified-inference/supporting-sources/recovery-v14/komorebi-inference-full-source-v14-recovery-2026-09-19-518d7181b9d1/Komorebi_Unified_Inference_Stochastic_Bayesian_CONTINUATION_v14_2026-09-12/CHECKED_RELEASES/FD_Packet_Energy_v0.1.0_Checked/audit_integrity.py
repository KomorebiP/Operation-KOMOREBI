#!/usr/bin/env python3
"""Audit archived final-source Lean receipts, all declarations, and live compiled hashes.

This does not rerun Lean. Rebuild with verify_blocks.py first when reproduction is
required. A log without a successful matching receipt never establishes a pass.
"""
from __future__ import annotations
import argparse
import datetime as dt
import hashlib
import json
import platform
import re
import subprocess
from pathlib import Path

ALLOWED={'propext','Classical.choice','Quot.sound'}

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def declarations(root: Path, modules: list[str]) -> list[dict]:
    result=[]
    for module in modules:
        stack=[]
        for line_no,line in enumerate((root/'Komorebi'/f'{module}.lean').read_text().splitlines(),1):
            n=re.match(r'namespace\s+(\S+)',line)
            if n:
                stack.append(('namespace',n.group(1)));continue
            sec=re.match(r'(?:noncomputable\s+)?section(?:\s+(\S+))?$',line)
            if sec:
                stack.append(('section',sec.group(1) or ''));continue
            if re.match(r'end(?:\s|$)',line) and stack:
                stack.pop()
            t=re.match(r'(?:@\[[^\n]*?\]\s*)?(theorem|lemma)\s+(\w+)',line)
            if t:
                result.append({'name':'.'.join([name for kind,name in stack if kind=='namespace']+[t.group(2)]),'module':module,
                               'kind':t.group(1),'line':line_no})
    return result

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--runtime',required=True,type=Path)
    ap.add_argument('--seal',action='store_true',help='Write a new receipt and axiom report; default is read-only verification.')
    args=ap.parse_args()
    root=Path(__file__).resolve().parent; rt=args.runtime.resolve()
    cache=rt/'workspace/.lake/build/lib/lean/Komorebi'
    modules=json.loads((root/'MODULE_ORDER.json').read_text())
    assert len(modules)==len(set(modules))
    assert {p.stem for p in (root/'Komorebi').glob('*.lean')}==set(modules)
    decl=json.loads((root/'DECLARATIONS.json').read_text())
    discovered=declarations(root,modules)
    assert {v['name'] for v in decl}=={v['name'] for v in discovered}
    assert len(decl)==len(discovered)==len({v['name'] for v in decl})
    receipts=[]; final=[]; failed=[]; incomplete=[]
    for p in sorted((root/'audit').glob('*/*.json')):
        d=json.loads(p.read_text())
        if 'module' not in d:continue
        d['receipt_path']=str(p.relative_to(root));receipts.append(d)
        if d.get('exit_status')!=0: failed.append(d)
    for module in modules:
        src=root/'Komorebi'/f'{module}.lean'; h=sha(src)
        assert not re.search(r'\b(?:sorry|admit|axiom|unsafe|native_decide)\b',src.read_text())
        candidates=[r for r in receipts if r['module']==module and r['exit_status']==0
                    and r['source_sha256_before']==h and r['source_sha256_after']==h]
        assert candidates,('No successful final-source receipt',module)
        record=candidates[-1]
        assert record['staged_source_sha256']==h
        assert record['output_sha256']==sha(cache/f'{module}.olean'),module
        log=(root/record['receipt_path']).with_suffix('.log')
        assert record['log_sha256']==sha(log)
        assert '-DwarningAsError=true' in record['argv'] and '-j1' in record['argv']
        imports=re.findall(r'^(?:public )?import (Komorebi\.\w+)',src.read_text(),re.M)
        assert set(imports)==set(record['dependencies']),module
        for dep,dh in record['dependencies'].items():
            name=dep.rsplit('.',1)[1]
            assert dh['source_sha256']==sha(root/'Komorebi'/f'{name}.lean'),dep
            assert dh['olean_sha256']==sha(cache/f'{name}.olean'),dep
        final.append(record)
    for p in (root/'audit').glob('*/*.lean'):
        if not p.with_suffix('.json').exists():incomplete.append(str(p.relative_to(root)))
    ar=[r for r in final if r['module']=='FDPacketEnergyAxiomAudit'][0]
    log=(root/ar['receipt_path']).with_suffix('.log')
    matches=re.findall(r"'([^']+)' depends on axioms:\s*\[(.*?)\]",log.read_text(),re.S)
    assert len(matches)==len(decl),(len(matches),len(decl))
    ax={name:[x.strip() for x in text.split(',') if x.strip()] for name,text in matches}
    assert set(ax)=={x['name'] for x in decl}
    assert all(set(xs)<=ALLOWED for xs in ax.values()),ax
    axiom_report={'status':'PASS','declarations_audited':len(ax),
       'allowed_axioms':sorted(ALLOWED),'actual_union':sorted(set().union(*(set(x) for x in ax.values()))),
       'log':str(log.relative_to(root)),'log_sha256':sha(log),'declarations':ax}
    neg=json.loads((root/'checks/NEGATIVE_CONTROLS.json').read_text())
    assert len(neg)==2 and all(x['exit_status']!=0 and x['expected_rejection'] for x in neg)
    for item in neg:
        p=root/'checks'/('Negative'+item['name']+'.log')
        assert sha(p)==item['log_sha256']
        assert 'error:' in p.read_text() or 'error(' in p.read_text()
    ex=json.loads((root/'checks/EXACT_PACKET_CHECKS.json').read_text())
    assert ex['status']=='PASS' and ex['script_sha256']==sha(root/'checks/exact_packet_checks.py')
    inherited=json.loads((root/'INHERITED_SOURCES.json').read_text())
    assert all(sha(root/x['path'])==x['sha256'] for x in inherited)
    version=subprocess.check_output(['bash',str(rt/'run.sh'),'lean','--version'],text=True).strip()
    ml=rt/'workspace/.lake/packages/mathlib'
    mc=subprocess.check_output(['git','-c',f'safe.directory={ml}','-C',str(ml),'rev-parse','HEAD'],text=True).strip()
    commit=(subprocess.check_output(['git','-C',str(root),'rev-parse','HEAD'],text=True).strip()
            if (root/'.git').is_dir() else (root/'SOURCE_COMMIT').read_text().strip())
    assert '6a10ac8c22beadecabdbb0919c2b50214762f91d' in version
    assert mc=='aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
    result={'status':'PASS','sealed_at_utc':dt.datetime.now(dt.timezone.utc).isoformat(),
       'source_commit':commit,'scope':'Self-adjoint rectangular packet energy and actual posterior-distribution certificates',
       'environment':{'lean_version':version,'mathlib_commit':mc,'platform':platform.platform(),
          'warning_as_error':True,'threads_per_lean_process':1},
       'active_modules_passed':len(final),'retained_modules':len(inherited),
       'new_proof_modules':10,'new_audit_modules':1,'theorem_lemma_declarations':len(decl),
       'new_declarations':sum(x['group']=='new' for x in decl),
       'retained_declarations':sum(x['group']=='retained' for x in decl),
       'all_axiom_audits_passed':True,'successful_final_modules':final,
       'failed_completed_checks':[{'module':x['module'],'exit_status':x['exit_status'],
           'receipt_path':x['receipt_path'],'elapsed_seconds':x['elapsed_seconds']} for x in failed],
       'incomplete_attempt_source_snapshots':incomplete,
       'negative_controls':neg,'exact_diagnostic_summary':{k:v for k,v in ex.items() if k!='cases'},
       'accumulated_final_compile_process_seconds':round(sum(x['elapsed_seconds'] for x in final),3),
       'verification_boundary':'Final-source and direct-dependency hashes checked against successful pinned-runtime receipts; seal does not itself rerun Lean.',
       'non_claims':['No operator-norm square-sum theorem.',
          'No inference of self-adjointness from pairwise-annihilating idempotents.',
          'No decomposition of the optimal transport distance into independent packet distances.',
          'No automatic improvement from re-accounting for a fixed residual.',
          'No floating-point certification, solver termination, admissible pruning, or optimal refinement.',
          'No new Gaussian semantics outside the retained positive-noise finite-dimensional domain.',
          'No full historical or continuous-time-chain rebuild; all thirty active retained modules were rebuilt.',
          'No literature-priority claim. The separate official Mathbox manifest validator was not available.']}
    if args.seal:
        (root/'AXIOM_AUDIT.json').write_text(json.dumps(axiom_report,indent=2)+'\n')
        (root/'FINAL_VERIFICATION_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k in ['status','active_modules_passed',
        'new_declarations','retained_declarations','theorem_lemma_declarations','all_axiom_audits_passed',
        'incomplete_attempt_source_snapshots','accumulated_final_compile_process_seconds']},indent=2))
if __name__=='__main__':main()
