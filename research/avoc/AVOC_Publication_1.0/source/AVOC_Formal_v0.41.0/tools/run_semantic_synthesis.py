#!/usr/bin/env python3
"""Read-only executed Lean semantic-library synthesis (v0.26).
No generated source execution, store mutation, or automatic promotion authorization.
"""
from __future__ import annotations
import argparse, hashlib, json, os, subprocess, sys
from pathlib import Path
from typing import Any
ROOT = Path(__file__).resolve().parents[1]

def unique_object(items: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in items:
        if key in out: raise ValueError(f'duplicate field: {key}')
        out[key] = value
    return out

def nat(value: Any, label: str, upper: int) -> int:
    if type(value) is not int or not 0 <= value <= upper:
        raise ValueError(f'{label} must be an integer in [0,{upper}]')
    return value

def program(value: Any, fuel: int = 16) -> Any:
    if fuel <= 0 or not isinstance(value, list) or not value:
        raise ValueError('malformed or over-nested pure program')
    op = value[0]
    if op == 'literal' and len(value)==2 and type(value[1]) is bool: return value
    if op == 'variable' and len(value)==2:
        nat(value[1], 'variable', 2); return value
    arity = {'not': 1, 'and': 2, 'or': 2, 'xor': 2}.get(op) if isinstance(op,str) else None
    if arity is None or len(value)!=arity+1: raise ValueError('unsupported program constructor')
    for x in value[1:]: program(x, fuel-1)
    return value

def request(config: Any) -> list[Any]:
    if not isinstance(config,dict): raise ValueError('configuration must be an object')
    mode = config.get('mode')
    allowed = {
        'feedback': {'mode','depth','references'},
        'frozen': {'mode','depth','references'},
        'budget': {'mode','depth','credit','references'},
        'campaign': {'mode','depth','credit','reference','calls'},
    }.get(mode)
    if allowed is None or not set(config)<=allowed: raise ValueError('unknown mode or configuration field')
    depth = nat(config.get('depth'), 'depth', 2 if mode=='frozen' else 3)
    if mode=='campaign':
        return ['campaign',program(config.get('reference')),depth,
                nat(config.get('credit'),'credit',10**9),nat(config.get('calls'),'calls',10**6)]
    refs=config.get('references',[])
    if not isinstance(refs,list) or len(refs)>256: raise ValueError('at most 256 references')
    for ref in refs: program(ref)
    if mode=='budget': return ['budget',depth,nat(config.get('credit'),'credit',10**9),refs]
    return ['build',mode,depth,refs]

def env_and_lean() -> tuple[dict[str,str],Path]:
    kit=Path(os.environ.get('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2')).resolve()
    lean=kit/'toolchain/bin/lean'
    if not lean.is_file(): raise ValueError('Set AVOC_LEAN_KIT to the pinned portable runtime')
    build=ROOT/'.lake/build/lib/lean'
    packages=kit/'workspace/.lake/packages'
    env=os.environ.copy()
    env['LEAN_PATH']=':'.join(map(str,[build]+[p/'.lake/build/lib/lean' for p in packages.iterdir() if p.is_dir()]))
    return env,lean

def check_pins() -> None:
    pinfile=ROOT/'semantic_source_pins.json'
    if not pinfile.is_file(): raise ValueError('Missing reviewed source pins')
    pins=json.loads(pinfile.read_text())
    for name,wanted in pins.items():
        path=ROOT/name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=wanted:
            raise ValueError('Source drift: '+name)
    # Check the actual compiled import closure, not merely entrypoint existence.
    seen=set()
    def check_module(name: str) -> None:
        if name in seen:return
        seen.add(name)
        source=ROOT/(name.replace('.','/')+'.lean')
        artifact=ROOT/'.lake/build/lib/lean'/(name.replace('.','/')+'.olean')
        record=ROOT/'results/v0.26.0'/('clean_'+source.stem+'.json')
        if not source.is_file() or not artifact.is_file() or not record.is_file():
            raise ValueError('Current compiled source missing: '+name)
        r=json.loads(record.read_text())
        if r.get('returncode')!=0 or r.get('timed_out') or not r.get('source_unchanged') or not r.get('imports_unchanged'):
            raise ValueError('Invalid compilation record: '+name)
        if r['source_sha256']!=hashlib.sha256(source.read_bytes()).hexdigest() or r['output_sha256']!=hashlib.sha256(artifact.read_bytes()).hexdigest():
            raise ValueError('Stale compiled module: '+name)
        for dep,digest in r.get('import_outputs',{}).items():
            check_module(dep)
            p=ROOT/'.lake/build/lib/lean'/(dep.replace('.','/')+'.olean')
            if hashlib.sha256(p.read_bytes()).hexdigest()!=digest: raise ValueError('Stale compiled import: '+dep)
    check_module('AVOC.SemanticSynthesisRuntime')

def main() -> int:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('config',type=Path)
    ap.add_argument('--timeout',type=int,default=90)
    args=ap.parse_args()
    if not 1<=args.timeout<=600: raise ValueError('timeout outside [1,600] seconds')
    if args.config.stat().st_size>2**20:raise ValueError('configuration byte limit')
    config=json.loads(args.config.read_text(encoding='utf-8'),object_pairs_hook=unique_object)
    wire=request(config)
    check_pins();env,lean=env_and_lean()
    import tempfile
    with tempfile.TemporaryDirectory(prefix='avoc-semantic-') as tmp:
        p=Path(tmp)/'request.json';p.write_text(json.dumps(wire),encoding='utf-8')
        proc=subprocess.run([str(lean),'--run',str(ROOT/'tools/SemanticSynthesisMain.lean'),str(p)],
            cwd=ROOT,env=env,text=True,capture_output=True,timeout=args.timeout)
        if proc.returncode!=0:
            raise ValueError('Lean execution failed: '+(proc.stderr+proc.stdout)[-4000:])
        out=json.loads(proc.stdout)
        print(json.dumps(out,indent=2))
    return 0
if __name__=='__main__':
    try: sys.exit(main())
    except (ValueError,OSError,subprocess.TimeoutExpired,json.JSONDecodeError) as error:
        print('FAILED: '+str(error),file=sys.stderr);sys.exit(2)
