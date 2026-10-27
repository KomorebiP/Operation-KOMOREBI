#!/usr/bin/env python3
"""Read-only AVOC retry advice from declared exact-rational operational models.

Does not inspect or change a live store, infer a fault, or mint a retry key.
Use the existing v0.21 workflow for explicit authorization and atomic fencing.
"""
from __future__ import annotations
import argparse, hashlib, json, os, signal, subprocess, sys, tempfile, time
from fractions import Fraction
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[1]

def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for k, v in pairs:
        if k in out: raise ValueError(f'duplicate field: {k}')
        out[k] = v
    return out

def frac(x: Any) -> list[int]:
    if type(x) is not int and type(x) is not str:
        raise ValueError('rational parameters must be integers or strings, not floats/bools')
    q = Fraction(x)
    if max(abs(q.numerator).bit_length(), q.denominator.bit_length()) > 256:
        raise ValueError('rational component exceeds 256 bits')
    return [q.numerator, q.denominator]

def natural(x: Any) -> int:
    if type(x) is not int or not 0 <= x <= 1_000_000:
        raise ValueError('natural field must lie in [0, 1000000]')
    return x

def wire_request(c: dict[str, Any]) -> list[Any]:
    required = {'prior_fast', 'resolve_if_slow', 'resolve_if_fast', 'completion_benefit',
                'attempt_budget', 'max_attempts', 'ledger', 'horizon'}
    if set(c) - (required | {'observe_operational_fault'}) or not required <= set(c):
        raise ValueError('missing or unknown configuration fields')
    l = c['ledger']
    if not isinstance(l, list) or len(l) != 6 or type(l[4]) is not bool or type(l[5]) is not bool:
        raise ValueError('ledger must be [charged, confirmed, reserved, ticket|null, published, terminal]')
    ticket = l[3]
    if ticket is not None:
        if not isinstance(ticket, list) or len(ticket) != 3: raise ValueError('ticket shape')
        ticket = [natural(x) for x in ticket]
    book = [natural(l[0]), natural(l[1]), natural(l[2]), ticket, l[4], l[5]]
    h = natural(c['horizon'])
    if h > 32: raise ValueError('horizon exceeds 32')
    w = ['avoc-retry-decision-v1', frac(c['prior_fast']), frac(c['resolve_if_slow']),
         frac(c['resolve_if_fast']), frac(c['completion_benefit']),
         [natural(c['attempt_budget']), natural(c['max_attempts'])], book, h]
    fault = c.get('observe_operational_fault', False)
    if type(fault) is not bool: raise ValueError('fault flag must be Boolean')
    return ['observe-operational-fault', w] if fault else w

def run_wire(w: Any, *, batch: bool = False, timeout: float = 60) -> tuple[Any, dict[str, Any]]:
    kit = Path(os.environ.get('AVOC_LEAN_KIT', '/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2'))
    lean = kit / 'toolchain/bin/lean'
    packages = kit / 'workspace/.lake/packages'
    build = ROOT / '.lake/build/lib/lean'
    if not lean.is_file() or not (build / 'AVOC/RetryDecisionCodec.olean').is_file():
        raise RuntimeError('Build the pinned project first; see REPRODUCE.md')
    env = dict(os.environ)
    env['LEAN_PATH'] = os.pathsep.join(map(str, [build] + [p/'.lake/build/lib/lean' for p in sorted(packages.iterdir()) if p.is_dir()]))
    env['PATH'] = str(lean.parent) + os.pathsep + env.get('PATH', '')
    raw = json.dumps(w, separators=(',', ':'), ensure_ascii=False).encode('utf-8')
    if len(raw) > (8388608 if batch else 65536): raise ValueError('wire size limit')
    with tempfile.TemporaryDirectory(prefix='avoc-retry-advice-') as d:
        request = Path(d) / 'input.json'; request.write_bytes(raw)
        cmd = [str(lean), '-j1', '--run', str(ROOT/'tools/RetryDecisionMain.lean')]
        if batch: cmd.append('--batch')
        cmd.append(str(request)); start = time.monotonic()
        p = subprocess.Popen(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                             text=True, start_new_session=True)
        try: out, err = p.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid, signal.SIGKILL); p.communicate(); raise TimeoutError('Lean advisor timed out; no advice confirmed')
        meta = {'argv': cmd, 'returncode': p.returncode, 'seconds': time.monotonic()-start,
                'request_sha256': hashlib.sha256(raw).hexdigest(),
                'stdout_sha256': hashlib.sha256(out.encode()).hexdigest(), 'stderr': err,
                'main_sha256': hashlib.sha256((ROOT/'tools/RetryDecisionMain.lean').read_bytes()).hexdigest(),
                'codec_sha256': hashlib.sha256((ROOT/'AVOC/RetryDecisionCodec.lean').read_bytes()).hexdigest()}
        if p.returncode: raise RuntimeError(f'Lean advisor rejected the request: {err.strip()}')
        result = [json.loads(line) for line in out.splitlines()] if batch else json.loads(out)
        return result, meta

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('config', type=Path); ap.add_argument('--output', type=Path)
    ap.add_argument('--timeout', type=float, default=60)
    a = ap.parse_args()
    if a.timeout <= 0: raise ValueError('timeout must be positive')
    if a.config.stat().st_size > 65536: raise ValueError('configuration size limit')
    c = json.loads(a.config.read_text(), object_pairs_hook=unique)
    r, m = run_wire(wire_request(c), timeout=a.timeout)
    result = {'advice': r, 'execution': m, 'effects': 'read-only; no database, receipt, or scientific-state changes'}
    raw = json.dumps(result, indent=2) + '\n'
    if a.output:
        a.output.parent.mkdir(parents=True, exist_ok=True)
        with a.output.open('x') as f: f.write(raw)
    print(raw, end=''); return 0
if __name__ == '__main__':
    try: raise SystemExit(main())
    except (ValueError, RuntimeError, TimeoutError, OSError) as e:
        print(f'FAILED: {e}', file=sys.stderr); raise SystemExit(2)
