#!/usr/bin/env python3
"""Freeze the active polynomial parameter chart source inventory in dependency order.

This is a release-maintenance operation, not a verification step. The verifier
consumes the frozen inventory and rejects source mutations or extra modules.
"""
from __future__ import annotations
import json
from pathlib import Path
from source_audit import inspect_source, sha

ROOT = Path(__file__).resolve().parents[1]


def order(entries: list[dict], already: set[str] | None = None) -> list[dict]:
    known = {e['module'] for e in entries}
    seen = set() if already is None else set(already)
    pending = {e['module']: e for e in entries}
    result = []
    while pending:
        ready = sorted(name for name, e in pending.items()
                       if all(i not in known or i in seen for i in e['imports']))
        if not ready:
            raise ValueError('Cyclic project import dependencies')
        for name in ready:
            result.append(pending.pop(name))
            seen.add(name)
    return result


def main() -> None:
    modules = order([inspect_source(p) for p in sorted((ROOT/'formalization').glob('*.lean'))])
    support = order([inspect_source(p) for p in sorted((ROOT/'controls').glob('Polynomial*.lean'))],
                    {e['module'] for e in modules})
    contracts = order([inspect_source(p) for p in sorted((ROOT/'contracts').glob('*.lean'))],
                      {e['module'] for e in modules + support})
    if not modules or not contracts:
        raise ValueError('Both active modules and statement contracts are required')
    controls = []
    for path in sorted((ROOT/'controls').glob('Invalid*.lean')):
        inspect_source(path)
        controls.append({'source': str(path.relative_to(ROOT)), 'sha256': sha(path),
                         'expected_error': 'type mismatch|application type mismatch'})
    if len(controls) < 3:
        raise ValueError('Expected the three mathematical negative controls')
    result = {'schema_version': 1, 'claim_id': 'PaperIX.fixed_polynomial.continuous_parameter_charts',
              'modules': modules, 'control_support': support, 'contracts': contracts, 'negative_controls': controls}
    dest = ROOT/'inventory.json'
    dest.write_text(json.dumps(result, indent=2)+'\n')
    print(f'Wrote {dest}: {len(modules)} modules, {len(support)} control supports, {len(contracts)} contracts, '
          f'{len(controls)} negative controls')


if __name__ == '__main__':
    main()
