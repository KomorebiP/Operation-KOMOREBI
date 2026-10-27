#!/usr/bin/env python3
"""Fail-closed source, exact-model, and optional Lean verification for Paper V.

Static checks and independent exact tests NEVER imply Lean compilation.
A Lean run checks the declared scope contract; PDF correspondence is a manual review.
No validation gate uses Python assert, so optimization cannot remove the gates.
Author: Komorebi P.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import time

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


def source_inventory(root: Path) -> list[dict[str, object]]:
    """Recognize the simple namespace/declaration format used in this package."""
    lean = root/'formalization/lean'
    targets: list[dict[str, object]] = []
    for path in sorted((lean/'KomorebiPaperV').glob('*.lean')):
        code = lean_code_only(path.read_text(encoding='utf-8'))
        namespaces = re.findall(r'(?m)^namespace\s+([\w.]+)\s*$', code)
        require(len(namespaces) == 1, f'Expected one explicit namespace in {path.name}.')
        namespace = namespaces[0]
        require(namespace == 'KomorebiPaperV' or namespace.startswith('KomorebiPaperV.'),
                f'Unexpected namespace in {path.name}.')
        for match in re.finditer(r'(?m)^theorem\s+(\w+)\b', code):
            targets.append({'declaration':namespace+'.'+match.group(1),'kind':'theorem',
                'file':path.relative_to(lean).as_posix(),'line':code[:match.start()].count('\n')+1})
    return targets


def static_checks(root: Path) -> dict[str, object]:
    lean = root/'formalization/lean'
    contract = read_json(root/'verification/candidate_contract.json')
    baseline = read_json(root/'provenance/BASELINE.json')
    require(sha256(root/'manuscript'/baseline['baseline_file']) == baseline['baseline_sha256'],
            'Baseline PDF hash mismatch.')
    require((lean/'lean-toolchain').read_text().strip() == TOOLCHAIN, 'Unexpected Lean toolchain pin.')
    manifest = read_json(lean/'lake-manifest.json')
    mathlib = [p for p in manifest['packages'] if p['name']=='mathlib']
    require(len(mathlib)==1 and mathlib[0]['rev']==MATHLIB_REV, 'Unexpected mathlib pin.')
    config = (lean/'lakefile.toml').read_text(encoding='utf-8')
    require(f'rev = "{MATHLIB_REV}"' in config, 'Lake configuration/mathlib pin mismatch.')
    require('"-DwarningAsError=true"' in config, 'Warnings-as-errors configuration missing.')
    require('autoImplicit = false' in config and 'relaxedAutoImplicit = false' in config,
            'Implicit-variable guard configuration missing.')
    actual_lean = sorted(list(lean.glob('*.lean'))+list((lean/'KomorebiPaperV').glob('*.lean')))
    # Reject unexpected Lean files outside the registered source modules/audit/root.
    unexpected = [p for p in lean.rglob('*.lean') if '.lake' not in p.relative_to(lean).parts
                  and p not in actual_lean]
    require(not unexpected, f'Unexpected Lean source locations: {unexpected}.')
    frozen = contract['source_sha256']
    expected_paths = set(frozen)
    actual_paths = {p.relative_to(root).as_posix() for p in actual_lean}
    actual_paths.update('formalization/lean/'+name for name in
                        ('lean-toolchain','lakefile.toml','lake-manifest.json'))
    require(actual_paths == expected_paths, 'Source file-set mismatch.')
    for rel, expected_hash in frozen.items():
        path = root/rel
        require(path.is_file() and sha256(path)==expected_hash, f'Source integrity mismatch: {rel}.')
    for path in actual_lean:
        code=lean_code_only(path.read_text(encoding='utf-8'))
        bad=re.findall(FORBIDDEN,code)
        require(not bad, f'Forbidden active Lean tokens in {path.name}: {bad}.')
        if path.name != 'KernelAudit.lean':
            require(not re.search(r'\b(?:run_cmd|initialize|opaque)\b',code),
                    f'Unexpected metaprogram/opaque command in {path.name}.')
    actual=source_inventory(root)
    found={row['declaration'] for row in actual}
    expected={row['declaration'] for row in contract['theorem_targets']}
    require(len(actual)==len(found), 'Duplicate theorem names.')
    require(len(contract['theorem_targets'])==len(expected), 'Duplicate contract target.')
    require(found==expected, f'Theorem target mismatch: {sorted(found ^ expected)}.')
    require(actual==contract['theorem_targets'], 'Source-location/theorem contract mismatch.')
    imports=set(re.findall(r'(?m)^import\s+(KomorebiPaperV\.\w+)\s*$',
                           (lean/'KomorebiPaperV.lean').read_text(encoding='utf-8')))
    modules={'KomorebiPaperV.'+p.stem for p in (lean/'KomorebiPaperV').glob('*.lean')}
    require(imports==modules, 'Top-level library import coverage mismatch.')
    audit=(lean/'KernelAudit.lean').read_text(encoding='utf-8')
    printed=re.findall(r'(?m)^#print axioms\s+([\w.]+)\s*$',audit)
    named=re.findall(r'(?m)^\s+`(KomorebiPaperV\.[\w.]+),?\s*$',audit)
    require(set(printed)==expected and len(printed)==len(expected), 'Axiom-print target coverage mismatch.')
    require(set(named)==expected and len(named)==len(expected), 'Audit target-array coverage mismatch.')
    require('PAPER_V_CANDIDATE_TARGET_AUDIT_PASS:' in audit, 'Audit sentinel definition missing.')
    scope = read_json(root/'verification/scope_contract.json')
    require(scope['manuscript_result_count'] == 20 and len(scope['results']) == 20,
            'Manuscript scope contract must contain exactly 20 results.')
    require(len({r['number'] for r in scope['results']}) == 20, 'Duplicate manuscript result.')
    for row in scope['results']:
        require(row['status'] == 'complete_scoped_statement', 'Incomplete manuscript scope row.')
        require(row['targets'] and set(row['targets']) <= expected, 'Unregistered scope target.')
    require(scope['correspondence_review'] == 'manual', 'PDF correspondence is not mechanized.')
    return {'baseline_hash':'PASS','source_integrity':'PASS','pinned_configuration':'PASS',
            'lexical_scan':'PASS','target_contract':'PASS','import_and_audit_coverage':'PASS',
            'scope_contract_results':20,'lean_files':len(actual_lean),'proof_modules':len(modules),
            'explicit_theorem_targets':len(expected),
            'meaning':'Static source checks only. No parsing, elaboration, or kernel acceptance inferred.'}


def _run_ready(command: list[str], cwd: Path, log_path: Path, timeout: float,
               ready_token: str, startup_timeout: float) -> subprocess.CompletedProcess[str]:
    """Wait for an exact stdout/stderr line before starting the execution timer.

    Output goes to a file, so a full pipe cannot deadlock readiness or cleanup.
    Startup and post-readiness execution have separate, finite deadlines. This
    opt-in protocol is for cooperative local test children, not arbitrary jobs.
    The direct child is killed and reaped on each failure path.
    """
    require(bool(ready_token) and "\n" not in ready_token and "\r" not in ready_token,
            "Readiness token must be one nonempty line.")
    require(math.isfinite(startup_timeout) and startup_timeout > 0,
            "Startup timeout must be finite and positive.")
    token = ready_token.encode("utf-8")
    with tempfile.TemporaryDirectory(prefix="paper_v_child_") as td:
        capture = Path(td)/"capture.log"
        process = None
        def content() -> str:
            return capture.read_text(encoding="utf-8", errors="replace")
        def stop() -> None:
            if process is not None and process.poll() is None:
                process.kill()
            if process is not None:
                process.wait(timeout=10)
        try:
            with capture.open("wb") as stream:
                try:
                    process = subprocess.Popen(command, cwd=cwd, stdin=subprocess.DEVNULL,
                                               stdout=stream, stderr=subprocess.STDOUT)
                except OSError as exc:
                    log_path.write_text(f"PROCESS NOT STARTED: {exc}\n", encoding="utf-8")
                    raise VerificationError(f"Command could not start; see {log_path.name}.") from exc
                deadline = time.monotonic() + startup_timeout
                ready, pending = False, b""
                # A separate descriptor is essential: reads must not move the child's write offset.
                with capture.open("rb") as reader:
                    while not ready:
                        pending += reader.read(65536)
                        while b"\n" in pending:
                            line, pending = pending.split(b"\n", 1)
                            if line.rstrip(b"\r") == token:
                                ready = True
                        if ready:
                            break
                        if process.poll() is not None:
                            # The child may have exited between the previous read and poll.
                            pending += reader.read()
                            ready = token in [line.rstrip(b"\r") for line in pending.split(b"\n")[:-1]]
                            if ready:
                                break
                            stop()
                            log_path.write_text(content()+"\nREADINESS FAILURE: child exited before ready.\n", encoding="utf-8")
                            raise VerificationError(f"Command exited before readiness; see {log_path.name}.")
                        if time.monotonic() >= deadline:
                            stop()
                            log_path.write_text(content()+f"\nSTARTUP TIMEOUT after {startup_timeout} seconds.\n", encoding="utf-8")
                            raise VerificationError(f"Command readiness timed out; see {log_path.name}.")
                        time.sleep(0.01)
                try:
                    process.wait(timeout=timeout)
                except subprocess.TimeoutExpired as exc:
                    stop()
                    log_path.write_text(content()+f"\nTIMEOUT after {timeout} seconds following readiness.\n", encoding="utf-8")
                    raise VerificationError(f"Command timed out after readiness; see {log_path.name}.") from exc
            text = content()
            log_path.write_text(text, encoding="utf-8")
            require(process.returncode == 0,
                    f"{command[0]} exited {process.returncode}; see {log_path.name}.")
            return subprocess.CompletedProcess(command, process.returncode, text)
        finally:
            stop()


def run(command: list[str], cwd: Path, log_path: Path,
        timeout: float = 900, *, ready_token: str | None = None,
        startup_timeout: float = 30) -> subprocess.CompletedProcess[str]:
    require(math.isfinite(timeout) and timeout > 0, "Timeout must be finite and positive.")
    if ready_token is not None:
        return _run_ready(command, cwd, log_path, timeout, ready_token, startup_timeout)
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


def main() -> int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--static-only',action='store_true',help='Run source and exact Python checks, not Lean.')
    args=parser.parse_args()
    V=ROOT/'verification'; V.mkdir(exist_ok=True)
    lean=ROOT/'formalization/lean'
    report={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'release':'1.1.0-expanded-lean-checked',
        'package_classification':'CHECKS_PENDING',
        'pdf_correspondence_mechanically_checked':False,'lean_kernel_checked':False,
        'python_optimization_level':sys.flags.optimize,'gates':{},'status':'STARTED'}
    status_path=V/('static_status.json' if args.static_only else 'verification_status.json')
    code=1
    try:
        report['gates']['source']=static_checks(ROOT)
        for script,stem in [('test_exact_models.py','exact_model'),
                            ('test_second_block.py','second_block'),
                            ('test_verifier.py','verifier_controls')]:
            output=V/(stem+'_results.json')
            run([sys.executable,str(ROOT/'tests'/script),'--report',str(output)],
                ROOT,V/(stem+'_tests.log'),timeout=180)
            results=read_json(output)
            require(results['status']=='PASS' and results['tests_run']>0,
                    f'No passing tests reported by {script}.')
            report['gates'][stem]=results
        if args.static_only:
            report['gates']['lean']='NOT_REQUESTED'
            report['status']='STATIC_AND_EXACT_ONLY'
            code=0
        elif shutil.which('lake') is None:
            report['gates']['lean']='BLOCKED_NO_LAKE'
            report['status']='BLOCKED_NO_LAKE'
            report['limitation']='No Lean process ran. Exact Python tests do not execute or certify the Lean candidates.'
            code=2
        else:
            # This branch must run with the pinned compiler/dependencies before any kernel claim.
            version=run(['lake','env','lean','--version'],lean,V/'lean_version.log',120)
            require(re.search(r'\b4\.34\.0-rc2\b',version.stdout) is not None, 'Unexpected Lean version.')
            run(['lake','build','KomorebiPaperV'],lean,V/'lean_build.log')
            # Reject any lock/config/source change performed while fetching/building.
            static_checks(ROOT)
            manifest=read_json(lean/'lake-manifest.json')
            for package in manifest['packages']:
                dep=lean/'.lake/packages'/package['name']
                rev=run(['git','rev-parse','HEAD'],dep,V/('pin_'+package['name']+'.log'),30).stdout.strip()
                require(rev==package['rev'],f'Dependency revision mismatch: {package["name"]}.')
                dirty=run(['git','status','--porcelain','--untracked-files=no'],dep,
                          V/('dirty_'+package['name']+'.log'),30).stdout.strip()
                require(not dirty,f'Modified tracked dependency sources: {package["name"]}.')
            audited=run(['lake','env','lean','-DwarningAsError=true','KernelAudit.lean'],
                        lean,V/'lean_axiom_audit.log')
            count=report['gates']['source']['explicit_theorem_targets']
            require(f'PAPER_V_CANDIDATE_TARGET_AUDIT_PASS: {count} theorem targets;' in audited.stdout,
                    'Missing audit success sentinel.')
            require('sorryAx' not in audited.stdout,'Unexpected proof placeholder in audit output.')
            report['lean_kernel_checked']=True
            report['gates']['lean']='TARGETS_BUILD_AND_AUDIT_PASS'
            report['package_classification']='CHECKED_SCOPED_MANUSCRIPT_CONTRACT'
            report['status']='LEAN_CHECKS_PASS'
            code=0
    except Exception as exc:
        report['status']='FAIL'; report['error']=str(exc); code=1
    finally:
        report['exit_code']=code
        status_path.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
        print(json.dumps(report,indent=2))
    return code


if __name__=='__main__':
    raise SystemExit(main())
