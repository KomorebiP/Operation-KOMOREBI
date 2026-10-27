#!/usr/bin/env python3
"""Run the theorem-backed Lean planner on bounded, exact-rational JSON data.

No candidate is executed as Lean code. The wrapper is a tested I/O adapter, not
part of the formal extraction theorem. Fractions must be integers or strings.
"""
from __future__ import annotations
import argparse, hashlib, json, os, signal, subprocess, sys, tempfile, time
from fractions import Fraction
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[1]

def unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result: raise ValueError(f'duplicate JSON field: {key}')
        result[key] = value
    return result

def fraction(value: Any) -> list[int]:
    if type(value) is not int and not isinstance(value, str):
        raise ValueError('fractions must be integers or strings, never floats or booleans')
    q = Fraction(value)
    if max(abs(q.numerator).bit_length(), q.denominator.bit_length()) > 256:
        raise ValueError('rational component exceeds 256 bits')
    return [q.numerator, q.denominator]

def natural(value: Any, name: str) -> int:
    if type(value) is not int or value < 0: raise ValueError(f'{name} must be a nonnegative integer')
    return value

def wire_request(c: dict[str, Any], base: Path) -> list[Any]:
    allowed = {'prior_true','success_if_false','success_if_true','register_fee','verify_fee',
      'admit_fee','admission_value','research_budget','horizon','planning_work_per_decision',
      'planning_price_per_unit','target_file','target_text','candidate_files','candidate_texts',
      'public_reports','run_trace'}
    if set(c)-allowed: raise ValueError(f'unknown fields: {sorted(set(c)-allowed)}')
    if ('target_file' in c) == ('target_text' in c): raise ValueError('provide exactly one target source')
    if ('candidate_files' in c) == ('candidate_texts' in c): raise ValueError('provide exactly one candidate source list')
    def read_text(name: str) -> str:
        p = (base / name).resolve()
        b = p.read_bytes()
        if len(b)>8192: raise ValueError(f'file too large: {p.name}')
        return b.decode('utf-8', errors='strict')
    target = read_text(c['target_file']) if 'target_file' in c else c['target_text']
    candidates = [read_text(p) for p in c['candidate_files']] if 'candidate_files' in c else c['candidate_texts']
    if not isinstance(target,str) or not isinstance(candidates,list) or not all(isinstance(s,str) for s in candidates):
        raise ValueError('target/candidates must be strings')
    reports = c.get('public_reports', [])
    if not isinstance(reports,list) or any(type(d) is not bool for d in reports): raise ValueError('reports must be booleans')
    trace = c.get('run_trace',False)
    if type(trace) is not bool: raise ValueError('run_trace must be a boolean')
    return ['avoc-planner-v1', fraction(c['prior_true']),fraction(c['success_if_false']),
      fraction(c['success_if_true']), natural(c['register_fee'],'register_fee'),
      natural(c['verify_fee'],'verify_fee'),natural(c['admit_fee'],'admit_fee'),
      fraction(c['admission_value']),natural(c['research_budget'],'research_budget'),
      natural(c['horizon'],'horizon'),natural(c['planning_work_per_decision'],'planning_work_per_decision'),
      fraction(c.get('planning_price_per_unit','0')), target, candidates,reports,trace]

def runtime() -> tuple[Path, dict[str,str]]:
    default='/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2'
    kit=Path(os.environ.get('AVOC_LEAN_KIT',default)).resolve()
    lean=kit/'toolchain/bin/lean'; packages=kit/'workspace/.lake/packages'
    if not lean.is_file() or not packages.is_dir():
        raise RuntimeError('Set AVOC_LEAN_KIT to the pinned portable runtime; see REPRODUCE.md')
    build=ROOT/'.lake/build/lib/lean'
    if not (build/'AVOC/PlannerRuntime.olean').is_file(): raise RuntimeError('Build the release before running; see REPRODUCE.md')
    paths=[build]+[d/'.lake/build/lib/lean' for d in sorted(packages.iterdir()) if d.is_dir()]
    env=os.environ.copy();env['LEAN_PATH']=os.pathsep.join(map(str,paths))
    env['PATH']=str(kit/'toolchain/bin')+os.pathsep+env.get('PATH','')
    return lean,env

def run_wire(wire: Any, *, batch: bool=False, timeout: int=60) -> tuple[subprocess.CompletedProcess[str], dict[str, Any]]:
    lean,env=runtime()
    encoded=json.dumps(wire,ensure_ascii=False,separators=(',',':')).encode('utf-8')
    if len(encoded) > (8388608 if batch else 65536): raise ValueError('request byte limit')
    with tempfile.TemporaryDirectory(prefix='avoc-planner-') as tmp:
        request=Path(tmp)/'request.json';request.write_bytes(encoded)
        cmd=[str(lean),'-j1','--run',str(ROOT/'tools/PlannerMain.lean')]
        if batch: cmd.append('--batch')
        cmd.append(str(request))
        start=time.monotonic()
        proc=subprocess.Popen(cmd,cwd=ROOT,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
        timed_out=False
        try: out,err=proc.communicate(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out=True;os.killpg(proc.pid,signal.SIGKILL);out,err=proc.communicate()
        record={'command':cmd,'seconds':round(time.monotonic()-start,6),'returncode':proc.returncode,
          'timed_out':timed_out,'request_sha256':hashlib.sha256(encoded).hexdigest(),
          'entrypoint_sha256':hashlib.sha256((ROOT/'tools/PlannerMain.lean').read_bytes()).hexdigest(),
          'stdout_sha256':hashlib.sha256(out.encode()).hexdigest(),
          'stderr_sha256':hashlib.sha256(err.encode()).hexdigest()}
        if timed_out: raise TimeoutError(f'Planner run hit its execution cap; no decision certificate issued. {record}')
        return subprocess.CompletedProcess(cmd,proc.returncode,out,err),record

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('config',type=Path);ap.add_argument('--output',type=Path);ap.add_argument('--record',type=Path)
    ap.add_argument('--timeout',type=int,default=60)
    args=ap.parse_args()
    try:
        if not 1<=args.timeout<=300: raise ValueError('timeout must be 1..300 seconds')
        config=json.loads(args.config.read_text(),object_pairs_hook=unique_object)
        wire=wire_request(config,args.config.resolve().parent)
        result,record=run_wire(wire,timeout=args.timeout)
        if args.record:
            args.record.parent.mkdir(parents=True,exist_ok=True);args.record.write_text(json.dumps(record,indent=2)+'\n')
        if result.returncode:
            print(result.stderr,file=sys.stderr);return result.returncode
        output=json.dumps(json.loads(result.stdout),indent=2)+'\n'
        if args.output:
            args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(output)
        print(output,end='');return 0
    except (ValueError, OSError, RuntimeError,TimeoutError,KeyError,TypeError) as error:
        print(f'ERROR: {error}',file=sys.stderr);return 2
if __name__=='__main__': raise SystemExit(main())
