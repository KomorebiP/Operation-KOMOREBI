#!/usr/bin/env python3
"""Run exact-rational budget and discrete-precision regression cases in Lean. Author: Komorebi P.

This is an executable test suite, separate from kernel-checked theorem claims.
The independent enumerator does not call the dynamic-programming recurrence.
A previous successful `verify.py` run supplies compiled local modules.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import time


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--kit', type=Path, required=True)
    parser.add_argument('--build', type=Path)
    parser.add_argument('--out', type=Path)
    parser.add_argument('--timeout', type=int, default=240)
    args = parser.parse_args()
    base = Path(__file__).resolve().parents[1]
    build = (args.build or base/'verification/final/build').resolve()
    out = (args.out or base/'verification/budget_execution').resolve()
    out.mkdir(parents=True, exist_ok=True)
    source = base/'verification/test_sources/BudgetExecution.lean'
    command = [sys.executable, str(base/'scripts/check_low_memory.py'), '--kit', str(args.kit.resolve()),
               '--import-dir', str(build), '--timeout', str(args.timeout), str(source)]
    started = time.monotonic()
    try:
        proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                              text=True, timeout=args.timeout+100)
        code, log = proc.returncode, proc.stdout
    except subprocess.TimeoutExpired as exc:
        code = 124
        data = exc.stdout or ''
        log = data.decode(errors='replace') if isinstance(data, bytes) else data
        log += '\nEXECUTION TEST TIMEOUT\n'
    (out/'BudgetExecution.log').write_text(log)
    expected = {
        'tree_instances': (r'PASS tree instances: (\d+)', 384),
        'tree_exact_weight_comparisons': (r'PASS tree exact-weight comparisons: (\d+)', 4992),
        'tree_budget_comparisons': (r'PASS tree budget comparisons: (\d+)', 4992),
        'enumerated_tree_cuts': (r'PASS independently enumerated tree cuts: (\d+)', 19152),
        'tree_specification_comparisons': (r'PASS tree specification comparisons: (\d+)', 1440),
        'precision_instances': (r'PASS precision instances: (\d+)', 288),
        'precision_exact_weight_comparisons': (r'PASS precision exact-weight comparisons: (\d+)', 3744),
        'precision_budget_comparisons': (r'PASS precision budget comparisons: (\d+)', 3744),
        'enumerated_assignments': (r'PASS independently enumerated assignments: (\d+)', 1453),
        'boundary_regressions': (r'PASS boundary regressions: (\d+)', 5),
    }
    counts = {}
    for key, (pattern, target) in expected.items():
        match = re.search(pattern, log)
        counts[key] = int(match.group(1)) if match else None
    report = {
        'author': 'Komorebi P.', 'checked_utc': datetime.now(timezone.utc).isoformat(),
        'source': str(source.relative_to(base)),
        'source_sha256': hashlib.sha256(source.read_bytes()).hexdigest(),
        'command': command, 'exit_code': code,
        'log_sha256': hashlib.sha256(log.encode()).hexdigest(),
        'seconds': round(time.monotonic()-started, 3), 'counts': counts,
        'compiled_dependency_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
            for module in ['ExactTreeCompiler', 'BudgetConvolution', 'QuantizedTreeCompiler', 'DiscretePrecision', 'StoredBudgetCompiler']
            for p in sorted(build.glob(module+'.*')) if p.is_file()},
        'pass': code == 0 and all(counts[key] == spec[1] for key,spec in expected.items())
                and not re.search(r'\b(?:error|warning):', log, re.I),
        'scope': 'Executable exact-rational tests, not new manuscript theorems. No GPU or original numerical-suite rerun.',
    }
    (out/'SUMMARY.json').write_text(json.dumps(report, indent=2)+'\n')
    print(log, end='')
    print('OVERALL', 'PASS' if report['pass'] else 'FAIL')
    return 0 if report['pass'] else 1

if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except (OSError, ValueError) as exc:
        print(f'Execution checks failed: {exc}', file=sys.stderr)
        raise SystemExit(1)
