#!/usr/bin/env python3
"""Replay the stored-runtime checks and the recovered finite core offline."""
from __future__ import annotations
import argparse, json, os, re, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='Write outside the pristine release folder.')
    args = parser.parse_args()
    kit = args.kit.resolve()
    env = dict(os.environ)
    for key in ('LEAN_PATH', 'LEAN_SRC_PATH', 'LEAN_SYSROOT', 'LAKE_HOME'):
        env.pop(key, None)
    env['PATH'] = str(kit / 'toolchain/bin') + os.pathsep + env.get('PATH', '')
    records = []
    report = {'scope': 'Runtime validation plus 39 finite-core declarations; not the analytic monograph.', 'checks': records, 'passed': False}
    def run(name, cmd, expected=0, needle=None, cwd=None, seconds=40):
        t = time.monotonic()
        p = subprocess.run(list(map(str, cmd)), env=env, cwd=cwd or kit / 'workspace',
                           text=True, capture_output=True, timeout=seconds)
        output = p.stdout + p.stderr
        ok = p.returncode == expected and (needle is None or needle in output)
        row = {'name': name, 'argv': list(map(str, cmd)), 'returncode': p.returncode,
               'seconds': time.monotonic()-t, 'passed': ok, 'output': output}
        records.append(row)
        print(('PASS ' if ok else 'FAIL ') + name, flush=True)
        if not ok:
            raise RuntimeError(name + ': ' + output)
        return output
    try:
        lean = kit / 'toolchain/bin/lean'
        lake = kit / 'toolchain/bin/lake'
        run('Lean version', [lean, '--version'], needle='4.34.0-rc2')
        run('Lake version', [lake, '--version'])
        for pkg in json.loads((ROOT/'lean/dependency_pins.json').read_text())['packages']:
            run('Pinned ' + pkg['name'], ['git', 'rev-parse', 'HEAD'], needle=pkg['rev'],
                cwd=kit/'workspace/.lake/packages'/pkg['name'])
        p = subprocess.run([str(lake), 'env', 'printenv', 'LEAN_PATH'], cwd=kit/'workspace',
                           env=env, text=True, capture_output=True, timeout=20, check=True)
        env['LEAN_PATH'] = p.stdout.strip()
        base = [lean, '-j1', '-DwarningAsError=true']
        evidence = ROOT / 'verification/local_lean'
        run('Kernel arithmetic', base + [evidence/'Hello.lean'])
        run('Cached Mathlib ring proof', base + [evidence/'MathlibSmoke.lean'])
        run('Bundled core-series Paper VI algebra', base + [evidence/'PRSC_VI_Algebra.lean'])
        run('Reject false statement', base + [evidence/'FalseStatement.lean'], expected=1, needle='error:')
        run('Reject sorry placeholder', base + [evidence/'Placeholder.lean'], expected=1, needle='sorry')
        output = run('Recovered finite core and all 39 axiom reports', base + [ROOT/'lean/BrowserCoreAxiomAudit.lean'])
        axioms = {x.strip() for group in re.findall(r'depends on axioms:\s*\[([^]]*)\]', output) for x in group.split(',')}
        if 'sorryAx' in output or axioms - {'propext', 'Classical.choice', 'Quot.sound'}:
            raise RuntimeError('Unexpected axiom dependency: ' + repr(axioms))
        checked = re.findall(r"'([^']+)' (?:depends on axioms|does not depend on any axioms)", output)
        if len(checked) != 39:
            raise RuntimeError(f'Expected 39 axiom reports, got {len(checked)}')
        report.update({'passed': True, 'finite_core_theorem_count': 39, 'axioms': sorted(axioms)})
    except (OSError, ValueError, KeyError, subprocess.SubprocessError, RuntimeError) as exc:
        report['error'] = str(exc)
        print('FAILED: ' + str(exc), file=sys.stderr)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2) + '\n')
    return 0 if report['passed'] else 1

if __name__ == '__main__':
    raise SystemExit(main())
