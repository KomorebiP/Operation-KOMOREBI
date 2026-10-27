#!/usr/bin/env python3
"""Fresh-source Lean proof build, axiom audit, kernel replay, and negative controls.

This verifies C01, F3, and the lower-bound component of C02. The evaluation-span dual and C03-C08 are not formalized here.
The pinned Lean/Lake toolchain must already be installed. No package downloads
are requested; only the toolchain's bundled standard library is imported.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'formalization/lean'
PIN = '4.34.0-rc2'
ALLOWED_AXIOMS = {'propext', 'Classical.choice', 'Quot.sound'}
MODULES = ['CircuitObstructions.Gates', 'CircuitObstructions.CutComparison',
           'CircuitObstructions.Degree', 'CircuitObstructions.MultiplicativeDegree',
           'CircuitObstructions.SafeDegree', 'CircuitObstructions.AffineOutput',
           'CircuitObstructions.DegreeChecks', 'CircuitObstructions.Examples']


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def without_comments(text: str) -> str:
    """Remove Lean's nested block and line comments while retaining line numbers."""
    out, i, depth = [], 0, 0
    while i < len(text):
        if text.startswith('/-', i):
            depth += 1; out.extend('  '); i += 2
        elif depth and text.startswith('-/', i):
            depth -= 1; out.extend('  '); i += 2
        elif not depth and text.startswith('--', i):
            end = text.find('\n', i)
            if end < 0: end = len(text)
            out.extend(' ' * (end - i)); i = end
        else:
            out.append(text[i] if not depth or text[i] == '\n' else ' '); i += 1
    if depth: raise ValueError('Unclosed Lean comment')
    return ''.join(out)


def inventory() -> list[dict]:
    entries = []
    for path in sorted((SOURCE / 'CircuitObstructions').glob('*.lean')):
        text = without_comments(path.read_text(encoding='utf-8'))
        if re.search(r'\b(sorry|admit|axiom|native_decide|unsafe|implemented_by|extern)\b', text):
            raise ValueError(f'Forbidden active proof construct in {path.name}')
        if 'skipKernelTC' in text:
            raise ValueError('Kernel-check bypass is forbidden')
        namespace = 'CircuitObstructions.Examples' if path.stem == 'Examples' else 'CircuitObstructions'
        for match in re.finditer(r'(?m)^\s*(?:@\[[^\]]+\]\s*)?theorem\s+([\w.]+)', text):
            # The anchor consumes blank lines. Locate the theorem token itself.
            token = text.find('theorem', match.start(), match.end())
            entries.append({'name': namespace + '.' + match.group(1),
                            'module': 'CircuitObstructions.' + path.stem,
                            'file': path.relative_to(SOURCE).as_posix(),
                            'line': text.count('\n', 0, token) + 1})
    return entries


def audit_text(entries: list[dict]) -> str:
    parts = ['import CircuitObstructions', 'set_option pp.universes false',
             'set_option pp.proofs false']
    for e in entries:
        parts += ['#check ' + e['name'], '#print axioms ' + e['name']]
    for name in ('Restores', 'cut_transport_identity', 'complete_safe_cover',
                 'canonical_complete_safe_cover', 'every_index_cut', 'DegreeLE',
                 'WorkspaceDegree', 'workspaceDegree_run', 'canonical_cut_packet_degree',
                 'CompleteSafeDegreeLE', 'beta', 'betaStar', 'betaStar_restoration_bound',
                 'canonical_restored_output_degree', 'restored_degree_and_cover_bound'):
        parts.append('#print CircuitObstructions.' + name)
    return '\n'.join(parts) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--toolchain', type=Path, help='Directory containing bin/lean and bin/lake')
    parser.add_argument('--out', type=Path, help='New output directory; must not already exist')
    args = parser.parse_args()
    output = args.out or ROOT / 'build/lean' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    output = output.resolve(); output.mkdir(parents=True, exist_ok=False)
    (output / 'logs').mkdir()
    env = os.environ.copy(); env.pop('LEAN_PATH', None)
    if args.toolchain:
        env['PATH'] = str(args.toolchain.resolve() / 'bin') + os.pathsep + env.get('PATH', '')
    records, start = [], time.perf_counter()
    result = {'schema': 1, 'claim': 'C01, F3, C02 lower-bound component', 'started_at': now(), 'status': 'FAIL',
              'scope': 'C01, F3, complete-safe-degree beta and affine-optimized betaStar lower bounds; exact indexed statements only',
              'nonclaims': ['The C02 evaluation-span dual and C03-C08 are not formalized by this block',
                            'No P versus NP resolution', 'No independent human or external-kernel review'],
              'commands': records}

    def execute(label: str, argv: list[str], cwd: Path, *, rejects: bool = False) -> str:
        log = output / 'logs' / (label + '.log')
        then = time.perf_counter()
        try:
            p = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, text=True, timeout=90)
            text = p.stdout + p.stderr; code = p.returncode
        except subprocess.TimeoutExpired as exc:
            log.write_text(str(exc), encoding='utf-8')
            raise RuntimeError(f'{label}: timeout is inconclusive') from exc
        log.write_text(text, encoding='utf-8')
        ok = (code != 0 and 'error' in text.lower()) if rejects else code == 0
        records.append({'name': label, 'argv': argv, 'cwd': str(cwd), 'exit_status': code,
                        'expected_rejection': rejects, 'passed': ok,
                        'seconds': time.perf_counter() - then, 'wall_time_limit_seconds': 90,
                        'log': log.relative_to(output).as_posix(), 'sha256': sha(log)})
        if not ok: raise RuntimeError(f'{label}: unexpected exit status {code}; see {log}')
        print(label + ': PASS' + (' (expected rejection)' if rejects else ''), flush=True)
        return text

    try:
        entries = inventory()
        declared = json.loads((SOURCE / 'theorem_inventory.json').read_text())['theorems']
        if entries != declared: raise ValueError('Committed theorem inventory differs from source declarations')
        result['source_sha256'] = {p.relative_to(SOURCE).as_posix(): sha(p)
                                  for p in sorted(SOURCE.rglob('*'))
                                  if p.is_file() and '.lake' not in p.parts}
        try:
            result['base_git_commit'] = subprocess.check_output(
                ['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
            result['git_dirty'] = bool(subprocess.check_output(
                ['git', 'status', '--porcelain'], cwd=ROOT, text=True).strip())
        except (OSError, subprocess.CalledProcessError):
            result['base_git_commit'] = 'source archive; identified by recorded source hashes'
            result['git_dirty'] = None
        version = execute('lean_version', ['lean', '--version'], ROOT).strip()
        if not version.startswith('Lean (version ' + PIN + ','):
            raise ValueError(f'Toolchain mismatch: expected {PIN}, got {version}')
        result['toolchain'] = version
        result['environment'] = {'python': sys.version, 'platform': platform.platform()}
        for exe in ('lean', 'lake', 'leanchecker'):
            path = shutil.which(exe, path=env['PATH'])
            if path is None: raise RuntimeError(f'Missing required tool: {exe}')
            result.setdefault('tool_binaries', {})[exe] = {'path': path, 'sha256': sha(Path(path))}
        stage = output / 'fresh_source'
        shutil.copytree(SOURCE, stage, ignore=shutil.ignore_patterns('.lake'))
        (stage / 'Audit.lean').write_text(audit_text(entries), encoding='utf-8')
        execute('fresh_build', ['lake', '--wfail', 'build'], stage)
        for module in MODULES:
            execute('strict_' + module.rsplit('.', 1)[-1],
                    ['lake', 'env', 'lean', '-DwarningAsError=true', module.replace('.', '/') + '.lean'], stage)
        audit = execute('axioms_and_statements', ['lake', 'env', 'lean', '-DwarningAsError=true', 'Audit.lean'], stage)
        axioms = {}
        for name, body in re.findall(r"'([^']+)' depends on axioms: \[([^\]]*)\]", audit):
            axioms[name] = [x.strip() for x in body.split(',') if x.strip()]
        for name in re.findall(r"'([^']+)' does not depend on any axioms", audit): axioms[name] = []
        names = {e['name'] for e in entries}
        if set(axioms) != names: raise ValueError('Axiom audit does not cover every indexed theorem')
        used = set().union(*(set(a) for a in axioms.values()))
        if not used <= ALLOWED_AXIOMS: raise ValueError(f'Unexpected proof axioms: {used - ALLOWED_AXIOMS}')
        result['theorem_count'] = len(entries)
        result['axioms_used'] = sorted(used)
        result['axioms_by_theorem'] = axioms
        for module in MODULES:
            text = execute('kernel_replay_' + module.rsplit('.', 1)[-1],
                           ['lake', 'env', 'leanchecker', '--verbose', module], stage)
            if 'replaying ' + module not in text:
                raise ValueError('Kernel replay did not report the requested module')
        negative = {
            'false_statement': 'import CircuitObstructions\nexample : False := by decide\n',
            'illegal_repeated_wire': 'import CircuitObstructions\nopen CircuitObstructions\ndef bad : Gate Bool := .cnot false false (by decide)\n',
            'target_only_claim': 'import CircuitObstructions\nopen CircuitObstructions CircuitObstructions.Examples\nexample : packet swapBoundary swapCircuit swapSuffix false .target = true := by decide\n',
            'placeholder_guard': 'import CircuitObstructions\nexample : False := by sorry\n',
            'false_monomial_degree': 'import CircuitObstructions\nopen CircuitObstructions\nexample : DegreeLE (n := 2) 1 (fun x => bprod [0,1] x) := DegreeLE.monomial [0,1] (by decide)\n',
            'false_beta_bound': 'import CircuitObstructions\nopen CircuitObstructions\nexample : beta andTwo <= 1 := by rw [beta_andTwo]; decide\n',
            'false_affine_and': 'import CircuitObstructions\nopen CircuitObstructions\nexample : DegreeLE 1 andTwo := by exact andTwo_degree_two\n',
            'false_betaStar_bound': 'import CircuitObstructions\nopen CircuitObstructions\nexample : betaStar andTwo = 1 := by rw [betaStar_andTwo]; decide\n',

        }
        neg = stage / 'negative'; neg.mkdir()
        for label, text in negative.items():
            p = neg / (label + '.lean'); p.write_text(text, encoding='utf-8')
            execute('reject_' + label, ['lake', 'env', 'lean', '-DwarningAsError=true', str(p)], stage, rejects=True)
        result['negative_controls'] = len(negative)
        result['kernel_replayed_modules'] = MODULES
        for name, digest in result['source_sha256'].items():
            if sha(SOURCE / name) != digest: raise ValueError('Formal source changed during verification: ' + name)
        result['status'] = 'PASS'
    except Exception as exc:
        result['error'] = str(exc)
        print('FAIL:', exc, file=sys.stderr)
    result['seconds'] = time.perf_counter() - start
    result['completed_at'] = now()
    (output / 'verification.json').write_text(json.dumps(result, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: result.get(k) for k in ('status', 'theorem_count', 'axioms_used', 'seconds', 'error')}, indent=2))
    return 0 if result['status'] == 'PASS' else 1

if __name__ == '__main__':
    raise SystemExit(main())
