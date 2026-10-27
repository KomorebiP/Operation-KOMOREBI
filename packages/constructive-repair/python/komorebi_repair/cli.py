"""Installed CLI for untrusted production and exact Python certificate checks.

Lean certification is run from scripts/certify_{one,menu,branch}.py in the source
archive. This CLI never promotes Python checking into a kernel-checked result.
"""
from __future__ import annotations
import argparse
import json
import platform
import sys
from pathlib import Path
from . import __version__
from .api import Outcome, load, solve, verify
from repair_certificates import canonical, read_json, MAX_BYTES, InvalidData

def _write(path: Path, data: bytes) -> None:
    if len(data) > MAX_BYTES:
        raise InvalidData('Serialized artifact exceeds resource limit')
    with path.open('xb') as stream:
        stream.write(data)

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--version', action='version', version=__version__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('doctor', help='Show local Python capability; no network access')
    for name in ('solve', 'check'):
        p = sub.add_parser(name)
        p.add_argument('input', type=Path)
        if name == 'check':
            p.add_argument('certificate', type=Path)
        else:
            p.add_argument('--max-nodes', type=int, default=8191)
            p.add_argument('--max-linear-trials', type=int, default=8191)
            p.add_argument('--max-menu-trials', type=int, default=256)
        p.add_argument('--output', type=Path, required=True,
                       help='New evidence directory. Existing paths are not overwritten.')
    args = parser.parse_args(argv)
    if args.command == 'doctor':
        print(json.dumps({'version': __version__, 'python': platform.python_version(),
              'python_certificate_checking': True, 'kernel_checked': False,
              'lean_workflow': 'Use the source archive and pinned offline Lean kit',
              'network_required': False}, sort_keys=True))
        return 0
    # Exclusive creation prevents accidental replacement of previous evidence.
    try:
        args.output.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
        print(json.dumps({'status': 'UNRESOLVED', 'kernel_checked': False,
                          'error_code': 'OUTPUT_UNAVAILABLE', 'error': str(exc)}))
        return 2
    try:
        p = load(args.input)
        _write(args.output/'input.json', canonical(p))
        if args.command == 'check':
            c = read_json(args.certificate)
            _write(args.output/'submitted_certificate.json', canonical(c))
            result = verify(p, c)
        else:
            result = solve(p, max_nodes=args.max_nodes,
                           max_linear_trials=args.max_linear_trials,
                           max_menu_trials=args.max_menu_trials)
        if result.certificate is not None:
            _write(args.output/'certificate.json', canonical(result.certificate))
        _write(args.output/'trace.txt', ('\n'.join(result.trace)+'\n').encode())
        record = result.to_dict(include_certificate=False)
    except (OSError, ValueError, RecursionError, ArithmeticError) as exc:
        record = {'status': 'UNRESOLVED', 'kernel_checked': False,
                  'error_code': 'INPUT_OR_OUTPUT_FAILURE', 'error': str(exc)}
    # Result is written last. No success receipt precedes the witness files.
    try:
        _write(args.output/'result.json', canonical(record))
    except (OSError, ValueError) as exc:
        record = {'status': 'UNRESOLVED', 'kernel_checked': False,
                  'error_code': 'RESULT_WRITE_FAILURE', 'error': str(exc)}
    print(json.dumps(record, sort_keys=True))
    return 0 if record['status'] == 'PYTHON_CERTIFICATE_VALID' else 2
