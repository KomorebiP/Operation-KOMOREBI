#!/usr/bin/env python3
"""Offline, source-bound Lean verification of the coupled-functions block.

Example (Linux or WSL):
  python tools/verify_coupled_block.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --work /tmp/sf-block01
Use --stage to execute one stage at a time. Every stage saves a receipt immediately.
No compiler installation, dependency download, or source change is performed.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = {'propext', 'Classical.choice', 'Quot.sound'}
STAGES = ('runtime', 'baseline', 'compile', 'kernel', 'controls')

def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit', type=Path, required=True)
    parser.add_argument('--work', type=Path, required=True, help='An output directory outside this release.')
    parser.add_argument('--stage', choices=('all',) + STAGES, default='all')
    parser.add_argument('--timeout', type=int, default=90, help='Seconds per compiler/replay command.')
    args = parser.parse_args()
    kit, work = args.kit.resolve(), args.work.resolve()
    if work == ROOT or ROOT in work.parents:
        parser.error('--work must be outside the release directory')
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    work.mkdir(parents=True, exist_ok=True)
    build = work/'build'
    build.mkdir(exist_ok=True)
    env = dict(os.environ)
    for key in ('LEAN_PATH', 'LEAN_SRC_PATH', 'LEAN_SYSROOT', 'LAKE_HOME'):
        env.pop(key, None)
    env['PATH'] = str(kit/'toolchain/bin') + os.pathsep + env.get('PATH', '')
    env['LEAN_PATH'] = os.pathsep.join([str(build)] +
        [str(p/'.lake/build/lib/lean') for p in sorted((kit/'workspace/.lake/packages').iterdir()) if p.is_dir()] +
        [str(kit/'workspace/.lake/build/lib/lean'), str(kit/'toolchain/lib/lean')])
    lean = kit/'toolchain/bin/lean'
    base = [str(lean), '-j1', '-DwarningAsError=true']
    declaration_map = json.loads((ROOT/'formalization/Block01/declarations.json').read_text())
    expected = [row['name'] for row in declaration_map['declarations']]
    if sha(ROOT/'lean/CoupledFormal.lean') != declaration_map['sha256']:
        raise RuntimeError('Production source does not match its declaration map')
    if len(expected) != len(set(expected)) or len(expected) != declaration_map['count']:
        raise RuntimeError('Declaration map has duplicate names or a wrong count')
    src = (ROOT/'lean/CoupledFormal.lean').read_text()
    # This is a supplementary source guard. Kernel compilation and axiom checks are the proof evidence.
    scrub = re.sub(r'/\-.*?\-/', '', src, flags=re.S)
    scrub = re.sub(r'--[^\n]*', '', scrub)
    for pattern in (r'\bsorry\b', r'\badmit\b', r'\baxiom\b', r'\bnative_decide\b', r'\bunsafe\b'):
        if re.search(pattern, scrub):
            raise RuntimeError('Forbidden production construct: ' + pattern)
    selected = STAGES if args.stage == 'all' else (args.stage,)
    all_ok = True
    for stage in selected:
        rows: list[dict] = []
        report = {'stage': stage, 'passed': False, 'source_sha256': sha(ROOT/'lean/CoupledFormal.lean'),
                  'baseline_source_sha256': sha(ROOT/'lean/BrowserCoreLocal.lean'),
                  'proof_scope': '29 new named declarations, plus 39 baseline declarations; not full analytic formalization.',
                  'checks': rows}
        receipt = work/(stage + '.json')
        def save() -> None:
            receipt.write_text(json.dumps(report, indent=2) + '\n')
        def run(name: str, cmd: list[str], expected_rc: int=0, needle: str | None=None, cwd: Path | None=None) -> str:
            start = time.monotonic()
            proc = subprocess.Popen(cmd, env=env, cwd=cwd or build, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True, start_new_session=True)
            timed_out = False
            try:
                output, _ = proc.communicate(timeout=args.timeout)
            except subprocess.TimeoutExpired:
                timed_out = True
                os.killpg(proc.pid, signal.SIGKILL)
                output, _ = proc.communicate()
            ok = not timed_out and proc.returncode == expected_rc and (needle is None or needle in output)
            row = {'name': name, 'argv': cmd, 'cwd': str(cwd or build), 'returncode': proc.returncode,
                   'expected_returncode': expected_rc, 'timed_out': timed_out,
                   'seconds': round(time.monotonic()-start, 6), 'passed': ok, 'output': output}
            rows.append(row)
            save()
            print(('PASS ' if ok else 'FAIL ') + stage + ': ' + name, flush=True)
            if not ok:
                raise RuntimeError(name + ': ' + output[-4000:])
            return output
        def audit(output: str, wanted: list[str] | None=None, count: int | None=None) -> None:
            groups = re.findall(r'depends on axioms:\s*\[([^]]*)\]', output, flags=re.S)
            axioms = {x.strip() for g in groups for x in g.split(',') if x.strip()}
            names = re.findall(r"'([^']+)' (?:depends on axioms|does not depend on any axioms)", output)
            if 'sorryAx' in output or axioms - ALLOWED:
                raise RuntimeError('Unexpected axiom dependencies: ' + repr(axioms))
            if len(names) != len(set(names)) or (count is not None and len(names) != count):
                raise RuntimeError('Wrong or duplicate axiom report count')
            if wanted is not None and set(names) != set(wanted):
                raise RuntimeError('Axiom reports do not exactly match the declaration map')
            report['axioms'] = sorted(axioms)
            report['audited_theorems'] = names
            report['audited_count'] = len(names)
        try:
            if stage == 'runtime':
                run('Lean version', [str(lean), '--version'], needle='4.34.0-rc2')
                run('Lake startup', [str(kit/'toolchain/bin/lake'), '--version'])
                pins = json.loads((ROOT/'lean/dependency_pins.json').read_text())['packages']
                for pin in pins:
                    out = run('pin ' + pin['name'], ['git', 'rev-parse', 'HEAD'],
                              cwd=kit/'workspace/.lake/packages'/pin['name'])
                    if out.strip() != pin['rev']:
                        raise RuntimeError('Wrong dependency pin: ' + pin['name'])
                run('Kernel arithmetic smoke', base + [str(ROOT/'verification/local_lean/Hello.lean')])
                run('Cached Mathlib smoke', base + [str(ROOT/'verification/local_lean/MathlibSmoke.lean')])
            elif stage == 'baseline':
                out = run('Baseline source and axiom reports', base + [str(ROOT/'lean/BrowserCoreAxiomAudit.lean')])
                audit(out, count=39)
            elif stage == 'compile':
                for name in ('CoupledFormal.lean', 'CoupledFormalAudit.lean'):
                    shutil.copyfile(ROOT/'lean'/name, build/name)
                run('Compile production source', base + ['-o', str(build/'CoupledFormal.olean'), str(build/'CoupledFormal.lean')])
                out = run('All new theorem axiom reports', base + [str(build/'CoupledFormalAudit.lean')])
                audit(out, wanted=expected, count=len(expected))
                report['object_sha256'] = sha(build/'CoupledFormal.olean')
                (build/'SOURCE_SHA256.txt').write_text(sha(build/'CoupledFormal.lean')+'\n')
            elif stage in ('kernel', 'controls'):
                if not (build/'SOURCE_SHA256.txt').is_file() or (build/'SOURCE_SHA256.txt').read_text().strip() != sha(ROOT/'lean/CoupledFormal.lean'):
                    raise RuntimeError('Run compile on this exact source before ' + stage)
                if sha(build/'CoupledFormal.lean') != sha(ROOT/'lean/CoupledFormal.lean'):
                    raise RuntimeError('Compiled source snapshot changed')
                if stage == 'kernel':
                    run('Kernel replay from imported environment',
                        [str(kit/'toolchain/bin/leanchecker'), '--verbose', 'CoupledFormal'], needle='replaying CoupledFormal')
                    report['kernel_scope'] = 'All declarations of CoupledFormal are replayed. Imported dependencies are not freshly replayed. This uses the same Lean kernel, not an external verifier.'
                else:
                    controls = json.loads((ROOT/'lean/controls/manifest.json').read_text())
                    for row in controls:
                        run(row['name'], base + [str(ROOT/'lean/controls'/row['file'])], expected_rc=1, needle=row['needle'])
                    report['negative_controls'] = len(controls)
            report['passed'] = True
        except (OSError, ValueError, KeyError, RuntimeError, subprocess.SubprocessError) as exc:
            report['error'] = str(exc)
            all_ok = False
        finally:
            save()
        if not report['passed']:
            print('FAILED: ' + report.get('error', 'unknown error'), file=sys.stderr)
            break
    return 0 if all_ok else 1

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, RuntimeError) as exc:
        print('FAILED: ' + str(exc), file=sys.stderr)
        raise SystemExit(1)
