#!/usr/bin/env python3
"""Budgeted exact minor probes before affine factor generation over GF(5).

The actual Lean scanner supplies rank LOWER bounds and stopping decisions. A
failed or truncated probe search does not claim a rank upper bound. This driver
is read-only: it does not modify certificate, upgrade, or research stores.
"""
from __future__ import annotations
import argparse
import hashlib
import itertools
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
from typing import Any, Callable

import factor_affine as proposer

ROOT = Path(__file__).resolve().parents[1]
VERSION = 'v0.31.0'
ENTRY = 'tools/AffineProbeMain.lean'
REUSE_ENTRY = 'tools/AffineReuseMain.lean'
LIMIT = 4 * 1024 * 1024


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def decode(text: str) -> Any:
    return json.loads(text, parse_float=proposer.reject_float,
                      parse_constant=proposer.reject_float,
                      object_pairs_hook=proposer.unique_object)


def read_config(path: Path) -> Any:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > LIMIT:
        raise ValueError('expected regular nonsymlink input within byte cap')
    return decode(path.read_text(encoding='utf-8'))


def runtime(entry: str) -> tuple[Path, dict[str, str]]:
    lean, env = proposer.environment(check_records=False)
    output = ROOT / '.lake/build/lib/lean'
    visited: set[str] = set()

    def validate(rel: str) -> None:
        if rel in visited:
            return
        visited.add(rel)
        source = ROOT / rel
        obj = output / Path(rel).with_suffix('.olean')
        record = ROOT / f'results/{VERSION}/clean_{source.stem}.json'
        if not obj.is_file() or not record.is_file():
            raise ValueError('build current source first: ' + rel)
        r = json.loads(record.read_text())
        imports = re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$', source.read_text(), re.M)
        hashes = {}
        for module in imports:
            dependency = module.replace('.', '/') + '.lean'
            validate(dependency)
            hashes[module] = digest(output / Path(dependency).with_suffix('.olean'))
        if (r.get('returncode') != 0 or r.get('timed_out') or not r.get('source_unchanged')
            or not r.get('imports_unchanged') or r.get('source_sha256') != digest(source)
            or r.get('output_sha256') != digest(obj) or r.get('import_outputs') != hashes):
            raise ValueError('stale source/import/output record: ' + rel)
    validate(entry)
    return lean, env


def invoke(request: Any, *, entry: str = ENTRY, batch: bool = False,
           records: list[dict] | None = None, timeout: float = 45) -> Any:
    if not 0 < timeout <= 120:
        raise ValueError('timeout must be in (0,120]')
    lean, env = runtime(entry)
    payload = (json.dumps(request, separators=(',', ':')) + '\n').encode()
    if len(payload) > LIMIT:
        raise ValueError('request size cap')
    with tempfile.TemporaryDirectory(prefix='avoc_rank_probe_') as td:
        path = Path(td) / 'request.json'
        path.write_bytes(payload)
        cmd = [str(lean), '-j1', '--run', str(ROOT / entry)]
        if batch:
            cmd.append('--batch')
        cmd.append(str(path))
        start = time.monotonic()
        cp = subprocess.run(cmd, cwd=ROOT, env=env, text=True, capture_output=True, timeout=timeout)
    if records is not None:
        records.append({'argv': cmd, 'returncode': cp.returncode,
                        'seconds': round(time.monotonic()-start, 6),
                        'request_sha256': hashlib.sha256(payload).hexdigest(),
                        'stdout_sha256': hashlib.sha256(cp.stdout.encode()).hexdigest(),
                        'stderr': cp.stderr})
    if cp.returncode not in (0, 2):
        raise RuntimeError('Lean execution failure: ' + cp.stderr[-3000:])
    if batch:
        values = [decode(line) for line in cp.stdout.splitlines() if line.strip()]
        if len(values) != len(request):
            raise RuntimeError('wrong response count')
        return values
    result = decode(cp.stdout)
    if cp.returncode and result.get('status') != 'error':
        raise RuntimeError('unexpected Lean return status')
    return result


def make_request(cfg: Any) -> list:
    fields = {'program', 'calls', 'credit', 'inputs', 'probe_credit', 'probe_limit', 'probe_plan'}
    if not isinstance(cfg, dict) or set(cfg)-fields:
        raise ValueError('unknown configuration field')
    n, m, _, _ = proposer.shape(cfg.get('program'))
    calls = proposer.integer(cfg.get('calls', 1000), 1000000, 'calls')
    credit = proposer.integer(cfg.get('credit', 100000), 100000000, 'credit')
    allowance = proposer.integer(cfg.get('probe_credit', 8), 100000000, 'probe_credit')
    limit = proposer.integer(cfg.get('probe_limit', 1), 784, 'probe_limit')
    vectors = cfg.get('inputs', [])
    if not isinstance(vectors, list) or len(vectors) > 128:
        raise ValueError('input batch cap')
    for x in vectors:
        proposer.vector_shape(x, n)
    if 'probe_plan' in cfg:
        if 'probe_limit' in cfg:
            raise ValueError('use probe_plan or probe_limit, not both')
        plan = cfg['probe_plan']
        if not isinstance(plan, list) or len(plan) > 784:
            raise ValueError('probe plan cap')
        for q in plan:
            if not isinstance(q, list) or len(q) != 4:
                raise ValueError('probe plan row requires four indices')
            for x, bound in zip(q, [m, m, n, n]):
                if type(x) is not int or not 0 <= x < bound:
                    raise ValueError('probe index out of range')
    else:
        plan = [[i, j, k, l] for i, j in itertools.combinations(range(m), 2)
                for k, l in itertools.combinations(range(n), 2)][:limit]
    return ['affine-rank-probe-f5-v1', cfg['program'], calls, credit, allowance, plan]


def add_totals(result: dict) -> dict:
    result['baseline_deployment'] = result['calls'] * result['per_call_original']
    result['campaign_total'] = result['spent'] + result['calls'] * result['per_call_selected']
    result['net_gain'] = result['baseline_deployment'] - result['campaign_total']
    result['breaks_even'] = result['net_gain'] >= 0
    return result


def run(cfg: dict, *, preflight_only: bool = False, timeout: float = 45,
        generator: Callable = proposer.certificate) -> dict:
    request = make_request(cfg)
    records: list[dict] = []
    pre = invoke(request, timeout=timeout, records=records)
    if pre.get('status') == 'error':
        raise ValueError(pre['error'])
    if preflight_only or pre['status'] != 'search_may_pay':
        result = dict(pre, invocations=records, generation_charge=0, certificate_executed=False)
        return add_totals(result)
    # Only now is the general factor proposer allowed to execute.
    paid, credit = pre['spent'], pre['credit']
    if pre['remaining_minimum'] > credit-paid:
        return add_totals(dict(pre, status='unfunded_generation_floor', invocations=records,
                               generation_charge=0, certificate_executed=False))
    reserve = pre['validation_reserve']
    meter = proposer.Meter(credit-paid-reserve)
    normal = pre['normal']
    try:
        candidate = generator(normal['input_dim'], normal['output_dim'],
                              normal['matrix'], normal['offset'], meter)
    except proposer.CreditExhausted:
        return add_totals(dict(pre, status='generation_budget_exhausted',
            spent=paid+meter.spent, remaining=credit-paid-meter.spent, generator_executed=True,
            generation_charge=meter.spent, generation_events=meter.events,
            certificate_executed=False, invocations=records))
    paid += meter.spent
    record = ['avoc-affine-cache-f5-dense-v1', normal['input_dim'], normal['output_dim'],
              normal['matrix'], normal['offset'], candidate]
    result = invoke(['affine-reuse-f5-v1', cfg['program'], record, pre['calls'], paid,
                     credit, cfg.get('inputs', [])], entry=REUSE_ENTRY, timeout=timeout, records=records)
    if result.get('status') == 'error':
        raise ValueError(result['error'])
    result.update(preflight=pre, generator_executed=True, generation_charge=meter.spent,
                  generation_events=meter.events, invocations=records,
                  probe_tests=pre['probe_tests'], probe_spent=pre['probe_spent'])
    # The old checker reports selected outputs only after certificate acceptance.
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('config', type=Path)
    parser.add_argument('--preflight-only', action='store_true')
    parser.add_argument('--timeout', type=float, default=45)
    args = parser.parse_args()
    try:
        result = run(read_config(args.config), preflight_only=args.preflight_only, timeout=args.timeout)
        print(json.dumps(result, indent=2))
        return 2 if result.get('status') in {'error', 'rejected_cache_certificate'} else 0
    except (ValueError, OSError, RuntimeError, subprocess.SubprocessError) as error:
        print(json.dumps({'status': 'error', 'error': str(error)}))
        return 2

if __name__ == '__main__':
    raise SystemExit(main())
