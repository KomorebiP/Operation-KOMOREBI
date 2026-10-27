#!/usr/bin/env python3
"""Fail-closed checks for Paper VI's fourth Lean block, not whole-paper certification.
Author: Komorebi P. No mandatory gate relies on Python assert.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
TOOLCHAIN = 'leanprover/lean4:v4.34.0-rc2'
MATHLIB_REV = 'aeb72f1e9981b6d35b426b16dca7759be3e7ba06'
FORBIDDEN = r'\b(?:sorry|admit|sorryAx|axiom|unsafe|native_decide|ofReduceBool|implemented_by|extern|partial)\b'


class VerificationError(RuntimeError):
    """A mandatory verification gate did not pass."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_json(path: Path):
    return json.loads(path.read_text(encoding='utf-8'))


def lean_code_only(text: str) -> str:
    """Lexically strip nested comments/strings, preserving line positions.

    This is a token scanner, NOT a Lean parser or an elaborator. Integrity hashes
    and the actual compiler/audit are separate gates.
    """
    out: list[str] = []
    i, depth = 0, 0
    quoted = False
    while i < len(text):
        if depth:
            if text.startswith('/-', i): depth += 1; i += 2
            elif text.startswith('-/', i): depth -= 1; i += 2
            else:
                if text[i] == '\n': out.append('\n')
                i += 1
        elif quoted:
            if text[i] == '\\': i += 2
            elif text[i] == '"': quoted = False; i += 1
            else:
                if text[i] == '\n': out.append('\n')
                i += 1
        elif text.startswith('/-', i): depth = 1; out.append(' '); i += 2
        elif text.startswith('--', i):
            end = text.find('\n', i)
            i = len(text) if end < 0 else end
        elif text[i] == '"': quoted = True; out.append(' '); i += 1
        else: out.append(text[i]); i += 1
    require(not depth and not quoted, 'Unterminated Lean comment or string.')
    return ''.join(out)


def run(command: list[str], cwd: Path, log_path: Path,
        timeout: int = 900) -> subprocess.CompletedProcess[str]:
    try:
        result=subprocess.run(command,cwd=cwd,text=True,stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,timeout=timeout,encoding='utf-8',errors='replace')
    except subprocess.TimeoutExpired as exc:
        partial=exc.stdout or ''
        if isinstance(partial,bytes): partial=partial.decode('utf-8',errors='replace')
        log_path.write_text(partial+f'\nTIMEOUT after {timeout} seconds.\n',encoding='utf-8')
        raise VerificationError(f'Command timed out; see {log_path.name}.') from exc
    except OSError as exc:
        log_path.write_text(f'PROCESS NOT STARTED: {exc}\n',encoding='utf-8')
        raise VerificationError(f'Command could not start; see {log_path.name}.') from exc
    log_path.write_text(result.stdout,encoding='utf-8')
    require(result.returncode==0, f'{command[0]} exited {result.returncode}; see {log_path.name}.')
    return result


def source_inventory(root: Path) -> list[dict]:
    lean=root/'formalization/lean'
    items=[]
    for path in sorted((lean/'KomorebiPaperVI').glob('*.lean')):
        code=lean_code_only(path.read_text())
        namespace=None
        for line_no,line in enumerate(code.splitlines(),1):
            match=re.fullmatch(r'namespace (KomorebiPaperVI[\w.]*)',line)
            if match: namespace=match[1]
            match=re.match(r'theorem (\w+)\b',line)
            if match:
                require(namespace is not None,'Theorem outside registered namespace')
                items.append(dict(declaration=namespace+'.'+match[1],kind='theorem',
                    file=path.relative_to(lean).as_posix(),line=line_no))
    return items


def static_checks(root: Path) -> dict:
    lean=root/'formalization/lean'; V=root/'verification'
    contract=read_json(V/'source_contract.json')
    require((lean/'lean-toolchain').read_text().strip()==TOOLCHAIN,'Unexpected toolchain')
    config=(lean/'lakefile.toml').read_text()
    require('"-DwarningAsError=true"' in config and 'autoImplicit = false' in config
        and 'relaxedAutoImplicit = false' in config,'Missing strict Lean options')
    require(f'rev = "{MATHLIB_REV}"' in config,'Unexpected mathlib configuration pin')
    manifest=read_json(lean/'lake-manifest.json')
    mathlib=[p for p in manifest['packages'] if p['name']=='mathlib']
    require(len(mathlib)==1 and mathlib[0]['rev']==MATHLIB_REV,'Unexpected mathlib lock pin')
    paths=[*lean.glob('*.lean'),*(lean/'KomorebiPaperVI').glob('*.lean')]
    unexpected=[p for p in lean.rglob('*.lean') if '.lake' not in p.relative_to(lean).parts and p not in paths]
    require(not unexpected,'Unexpected Lean source location')
    expected={p.relative_to(root).as_posix() for p in paths}
    expected.update('formalization/lean/'+name for name in ('lean-toolchain','lakefile.toml','lake-manifest.json'))
    expected.add('THEOREM_LEDGER.json')
    require(set(contract['source_sha256'])==expected,'Source file-set mismatch')
    for rel,digest in contract['source_sha256'].items():
        require((root/rel).is_file() and sha256(root/rel)==digest,'Source integrity mismatch: '+rel)
    for p in paths:
        code=lean_code_only(p.read_text())
        require(not re.search(FORBIDDEN,code),'Forbidden Lean token: '+p.name)
        if p.name!='KernelAudit.lean':
            require(not re.search(r'\b(?:run_cmd|initialize|opaque)\b',code),'Unregistered metaprogram: '+p.name)
    inventory=source_inventory(root)
    require(inventory==contract['theorem_targets'],'Theorem inventory mismatch')
    targets={i['declaration'] for i in inventory}
    require(len(targets)==len(inventory),'Duplicate theorem target')
    modules={'KomorebiPaperVI.'+p.stem for p in (lean/'KomorebiPaperVI').glob('*.lean')}
    imports=set(re.findall(r'(?m)^import (KomorebiPaperVI\.\w+)$',(lean/'KomorebiPaperVI.lean').read_text()))
    require(imports==modules,'Root import coverage mismatch')
    audit=(lean/'KernelAudit.lean').read_text()
    printed=re.findall(r'(?m)^#print axioms ([\w.]+)$',audit)
    named=re.findall(r'(?m)^\s+`(KomorebiPaperVI\.[\w.]+),?\s*$',audit)
    require(len(printed)==len(targets) and set(printed)==targets,'Audit print coverage mismatch')
    require(len(named)==len(targets) and set(named)==targets,'Audit target-array mismatch')
    require('PAPER_VI_TARGET_AUDIT_PASS:' in audit,'Missing audit sentinel definition')
    rows=read_json(root/'THEOREM_LEDGER.json')
    require(len(rows)==33 and len({r['number'] for r in rows})==33,'Manuscript ledger must contain 33 unique results')
    for row in rows:
        require(row['status'] in ('complete_scoped_statement','partial','not_formalized'),'Unknown scope status')
        require(set(row['targets'])<=targets,'Unknown ledger target')
        if row['status']!='not_formalized':require(bool(row['targets']),'Missing scope target')
        if row['status']!='complete_scoped_statement':require(bool(row['remaining']),'Missing remaining obligation')
    return dict(source_integrity='PASS',configuration='PASS',imports='PASS',target_inventory='PASS',
        audit_coverage='PASS',theorems=len(targets),proof_modules=len(modules),
        complete=sum(r['status']=='complete_scoped_statement' for r in rows),
        partial=sum(r['status']=='partial' for r in rows),
        pending=sum(r['status']=='not_formalized' for r in rows))


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-only',action='store_true')
    args=parser.parse_args(); V=ROOT/'verification'; L=ROOT/'formalization/lean'
    report=dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),release='0.5.0-checked-fifth-block',
        lean_kernel_checked=False,full_paper_formalized=False,all_scoped_results_complete=False,open_conjectures=3,manuscript_correspondence='manual',
        python_optimization_level=sys.flags.optimize,status='STARTED',gates={})
    code=1
    try:
        report['gates']['source']=static_checks(ROOT)
        tests=run([sys.executable,'-m','pytest','-q','tests'],ROOT/'companion',V/'companion_tests.log',180)
        match=re.search(r'(\d+) passed',tests.stdout)
        require(match is not None and int(match[1])>=54,'Companion tests missing')
        report['gates']['companion']={'passed':int(match[1]),'meaning':'Finite numerical regression tests; not Lean proofs.'}
        controls=run([sys.executable,str(V/'test_verifier.py')],ROOT,V/'verifier_controls.log',120)
        require('OK' in controls.stdout,'Verifier controls did not pass')
        if args.static_only:
            report['status']='STATIC_AND_COMPANION_ONLY';code=0
        elif shutil.which('lake') is None:
            report['status']='BLOCKED_NO_LAKE';code=2
        else:
            version=run(['lake','env','lean','--version'],L,V/'lean_version.log',120)
            require(re.search(r'\b4\.34\.0-rc2\b',version.stdout) is not None,'Unexpected compiler version')
            run(['lake','build','KomorebiPaperVI'],L,V/'lean_build.log')
            static_checks(ROOT)
            for package in read_json(L/'lake-manifest.json')['packages']:
                dep=L/'.lake/packages'/package['name']
                rev=run(['git','rev-parse','HEAD'],dep,V/('pin_'+package['name']+'.log'),30).stdout.strip()
                require(rev==package['rev'],'Dependency pin mismatch: '+package['name'])
                dirty=run(['git','status','--porcelain','--untracked-files=no'],dep,V/('dirty_'+package['name']+'.log'),30).stdout.strip()
                require(not dirty,'Dirty tracked dependency: '+package['name'])
            audit=run(['lake','env','lean','-DwarningAsError=true','KernelAudit.lean'],L,V/'lean_axiom_audit.log')
            count=report['gates']['source']['theorems']
            match=re.search(rf'PAPER_VI_TARGET_AUDIT_PASS: {count} theorem targets; (\d+) namespace declarations',audit.stdout)
            require(match is not None,'Missing real namespace-audit success marker')
            require('sorryAx' not in audit.stdout,'Placeholder axiom in audit')
            report['gates']['lean']=dict(status='BUILD_AND_AXIOM_AUDIT_PASS',theorems=count,namespace_declarations=int(match[1]),
                allowed_axioms=['propext','Classical.choice','Quot.sound'])
            report['all_scoped_results_complete']=(report['gates']['source']['complete']==33)
            report['lean_kernel_checked']=True;report['status']='LEAN_FIFTH_BLOCK_CHECKS_PASS';code=0
    except Exception as exc:
        report.update(status='FAIL',error=str(exc));code=1
    report['exit_code']=code
    (V/('static_status.json' if args.static_only else 'verification_status.json')).write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return code

if __name__=='__main__':
    raise SystemExit(main())
