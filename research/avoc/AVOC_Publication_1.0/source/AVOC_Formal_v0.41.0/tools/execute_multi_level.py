#!/usr/bin/env python3
"""Build a checked terminal-payoff catalogue, plan adaptively, and execute one hidden world.

The planner sees only the finite catalogue.  Python prepares proof-carrying warm/cold
plans for every catalogue world by invoking the Lean checker.  This exact model
construction is charged and reported separately from the controller objective.
Operational failures are errors, never negative algebraic reports.
"""
from __future__ import annotations
import argparse, hashlib, json, os, re, subprocess, sys, tempfile, time
from fractions import Fraction
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
VERSION='v0.34.0'
LIMIT=4*1024*1024
TERMINAL='tools/AffineTerminalMain.lean'
PLANNER='tools/MultiLevelMain.lean'
sys.path.insert(0,str(ROOT/'tools'))
import factor_affine as proposer


def reject_float(x:str):raise ValueError('floating point is not accepted')
def unique_object(pairs):
    d={}
    for k,v in pairs:
        if k in d:raise ValueError('duplicate JSON field: '+k)
        d[k]=v
    return d

def decode(text:str)->Any:
    return json.loads(text,parse_float=reject_float,parse_constant=reject_float,
                      object_pairs_hook=unique_object)

def canonical(x:Any)->bytes:
    return (json.dumps(x,separators=(',',':'),sort_keys=True)+'\n').encode()

def sha(p:Path)->str:return hashlib.sha256(p.read_bytes()).hexdigest()

def runtime(entry:str)->tuple[Path,dict[str,str]]:
    kit=Path(os.environ.get('AVOC_LEAN_KIT','/mnt/data/voc_lean/Komorebi_Portable_Lean_4.34.0-rc2')).resolve()
    lean=kit/'toolchain/bin/lean';build=ROOT/'.lake/build/lib/lean'
    if not lean.is_file():raise ValueError('set AVOC_LEAN_KIT to the pinned portable Lean kit')
    seen=set()
    def validate(rel:str):
        if rel in seen:return
        seen.add(rel);src=ROOT/rel;obj=build/Path(rel).with_suffix('.olean')
        rec=ROOT/f'results/{VERSION}/clean_{src.stem}.json'
        if not src.is_file() or not obj.is_file() or not rec.is_file():
            raise ValueError('build current source first: '+rel)
        imports=re.findall(r'^import\s+(AVOC(?:\.\w+)*)\s*$',src.read_text(),re.M)
        ih={}
        for mod in imports:
            dep=mod.replace('.','/')+'.lean';validate(dep)
            ih[mod]=sha(build/Path(dep).with_suffix('.olean'))
        r=json.loads(rec.read_text())
        if (r.get('returncode')!=0 or r.get('timed_out') or not r.get('source_unchanged')
            or not r.get('imports_unchanged') or r.get('source_sha256')!=sha(src)
            or r.get('output_sha256')!=sha(obj) or r.get('import_outputs')!=ih):
            raise ValueError('stale compilation record: '+rel)
    validate(entry)
    paths=[build]+[d/'.lake/build/lib/lean' for d in (kit/'workspace/.lake/packages').iterdir() if d.is_dir()]
    env=os.environ.copy();env['LEAN_PATH']=':'.join(map(str,paths));env['PATH']=str(lean.parent)+':'+env.get('PATH','')
    return lean,env

def invoke(entry:str,request:Any,timeout:float,records:list[dict])->dict:
    if not 0<timeout<=120:raise ValueError('timeout must be in (0,120]')
    payload=canonical(request)
    if len(payload)>LIMIT:raise ValueError('request byte cap')
    lean,env=runtime(entry)
    with tempfile.TemporaryDirectory(prefix='avoc_operational_') as td:
        path=Path(td)/'request.json';path.write_bytes(payload)
        cmd=[str(lean),'-j1','--run',str(ROOT/entry),str(path)];t=time.monotonic()
        cp=subprocess.run(cmd,cwd=ROOT,env=env,text=True,capture_output=True,timeout=timeout)
    records.append(dict(entry=entry,argv=cmd,seconds=round(time.monotonic()-t,6),
        returncode=cp.returncode,request_sha256=hashlib.sha256(payload).hexdigest(),
        stdout_sha256=hashlib.sha256(cp.stdout.encode()).hexdigest(),stderr=cp.stderr[-2000:]))
    if cp.returncode not in (0,2):raise RuntimeError('Lean execution failure: '+cp.stderr[-3000:])
    out=decode(cp.stdout)
    if cp.returncode or out.get('status')=='error':raise RuntimeError(out.get('error','Lean request rejected'))
    return out

def invoke_batch(entry:str,requests:list[Any],timeout:float,records:list[dict])->list[dict]:
    if not 0<timeout<=120:raise ValueError('timeout must be in (0,120]')
    if len(requests)>256:raise ValueError('batch size cap')
    payload=canonical(requests)
    if len(payload)>LIMIT:raise ValueError('request byte cap')
    lean,env=runtime(entry)
    with tempfile.TemporaryDirectory(prefix='avoc_operational_batch_') as td:
        path=Path(td)/'request.json';path.write_bytes(payload)
        cmd=[str(lean),'-j1','--run',str(ROOT/entry),'--batch',str(path)];t=time.monotonic()
        cp=subprocess.run(cmd,cwd=ROOT,env=env,text=True,capture_output=True,timeout=timeout)
    lines=[decode(x) for x in cp.stdout.splitlines() if x.strip()]
    records.append(dict(entry=entry,batch=len(requests),argv=cmd,seconds=round(time.monotonic()-t,6),
        returncode=cp.returncode,request_sha256=hashlib.sha256(payload).hexdigest(),
        stdout_sha256=hashlib.sha256(cp.stdout.encode()).hexdigest(),stderr=cp.stderr[-2000:]))
    if cp.returncode or len(lines)!=len(requests):
        raise RuntimeError('Lean batch execution failure: '+cp.stderr[-3000:]+f' outputs={len(lines)}')
    for out in lines:
        if out.get('status')=='error':raise RuntimeError(out.get('error','Lean request rejected'))
    return lines

def as_fraction(x:Any)->Fraction:
    if isinstance(x,str):return Fraction(x)
    if type(x) is int:return Fraction(x)
    if isinstance(x,list) and len(x)==2 and all(type(z) is int for z in x):return Fraction(x[0],x[1])
    raise ValueError('expected exact rational')

def rat_wire(q:Fraction)->list[int]:return [q.numerator,q.denominator]

def read_config(path:Path)->dict:
    if path.is_symlink() or not path.is_file() or path.stat().st_size>LIMIT:raise ValueError('invalid config file')
    x=decode(path.read_text())
    allowed={'worlds','calls','credit_per_world','probes','fees','horizon','actual_world','history','inputs','cache_record'}
    if not isinstance(x,dict) or set(x)-allowed:raise ValueError('unknown configuration fields')
    if not isinstance(x.get('worlds'),list) or not x['worlds'] or len(x['worlds'])>32:raise ValueError('world catalogue size')
    for w in x['worlds']:
        if not isinstance(w,dict) or set(w)!={'program'}:raise ValueError('world is {program}')
    for k,cap in [('calls',1000000),('credit_per_world',100000000),('horizon',8),('actual_world',len(x['worlds'])-1)]:
        if type(x.get(k)) is not int or not 0<=x[k]<=cap:raise ValueError(k+' out of range')
    if x['actual_world']>=len(x['worlds']):raise ValueError('actual_world out of range')
    if not isinstance(x.get('probes',[]),list) or len(x['probes'])>16:raise ValueError('probe catalogue cap')
    if not isinstance(x.get('fees',[]),list) or len(x['fees'])!=len(x['probes']):raise ValueError('fee/probe mismatch')
    if not isinstance(x.get('history',[]),list) or len(x['history'])>32:raise ValueError('history cap')
    if not isinstance(x.get('inputs',[]),list) or len(x['inputs'])>128:raise ValueError('input cap')
    return x

def get_deployment(out:dict)->dict:
    d=out.get('deployment')
    if not isinstance(d,dict):raise RuntimeError('missing checked deployment')
    return d

def prepare_world(program:Any,cfg:dict,cache_record:Any,timeout:float,records:list[dict])->dict:
    norm=invoke(TERMINAL,['affine-terminal-normalize-f5-v1',program],timeout,records)
    n=norm['input_dim'];m=norm['output_dim']
    # Generate a cold candidate from the Lean-certified normal coefficients.
    meter=proposer.Meter(cfg['credit_per_world'])
    candidate=proposer.certificate(n,m,norm['normal']['matrix'],norm['normal']['offset'],meter)
    cold=invoke(TERMINAL,['affine-terminal-cold-f5-v1',program,candidate,cfg['calls'],meter.spent,
                          cfg['credit_per_world'],cfg.get('inputs',[])],timeout,records)
    if cold.get('status')!='certified_cold_deployment':raise RuntimeError('cold candidate not certified: '+str(cold))
    warm=None
    if cache_record is not None:
        warm=invoke(TERMINAL,['affine-terminal-warm-f5-v1',program,cache_record,cfg['calls'],0,
                              cfg['credit_per_world'],cfg.get('inputs',[])],timeout,records)
        if warm.get('status')!='certified_warm_deployment':warm=None
    return dict(program=program,normal=norm['normal'],cold=cold,warm=warm,
                cold_generation_charge=meter.spent)

def prepare_worlds(programs:list[Any],cfg:dict,cache_record:Any,timeout:float,records:list[dict])->list[dict]:
    norms=invoke_batch(TERMINAL,[['affine-terminal-normalize-f5-v1',p] for p in programs],timeout,records)
    candidates=[];meters=[]
    for norm in norms:
        n=norm['input_dim'];m=norm['output_dim'];meter=proposer.Meter(cfg['credit_per_world'])
        candidates.append(proposer.certificate(n,m,norm['normal']['matrix'],norm['normal']['offset'],meter))
        meters.append(meter)
    colds=invoke_batch(TERMINAL,[['affine-terminal-cold-f5-v1',p,c,cfg['calls'],meter.spent,
        cfg['credit_per_world'],cfg.get('inputs',[])] for p,c,meter in zip(programs,candidates,meters)],timeout,records)
    for out in colds:
        if out.get('status')!='certified_cold_deployment':raise RuntimeError('cold candidate not certified: '+str(out))
    warms=[None]*len(programs)
    if cache_record is not None:
        raw=invoke_batch(TERMINAL,[['affine-terminal-warm-f5-v1',p,cache_record,cfg['calls'],0,
            cfg['credit_per_world'],cfg.get('inputs',[])] for p in programs],timeout,records)
        warms=[out if out.get('status')=='certified_warm_deployment' else None for out in raw]
    return [dict(program=p,normal=norm['normal'],cold=cold,warm=warm,cold_generation_charge=meter.spent)
        for p,norm,cold,warm,meter in zip(programs,norms,colds,warms,meters)]

def fee_fraction(x:Any)->Fraction:
    q=as_fraction(x)
    if q<0:raise ValueError('negative probe fee')
    return q

def average(xs:list[Fraction])->Fraction:return sum(xs,Fraction())/len(xs)

def main()->int:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('config',type=Path)
    ap.add_argument('--timeout',type=float,default=60);args=ap.parse_args()
    records=[]
    try:
        cfg=read_config(args.config);cache=cfg.get('cache_record')
        worlds=prepare_worlds([w['program'] for w in cfg['worlds']],cfg,cache,args.timeout,records)
        dims={(w['normal']['input_dim'],w['normal']['output_dim']) for w in worlds}
        if len(dims)!=1:raise ValueError('all worlds must have the same dimensions')
        n,m=next(iter(dims))
        reuse_enabled=all(w['warm'] is not None for w in worlds)
        warm_values=[as_fraction(get_deployment(w['warm'])['modeled_net_payoff']) if reuse_enabled else Fraction(0) for w in worlds]
        cold_values=[as_fraction(get_deployment(w['cold'])['modeled_net_payoff']) for w in worlds]
        fees=[fee_fraction(x) for x in cfg['fees']]
        history=[list(x) for x in cfg.get('history',[])]
        trace=[];horizon=cfg['horizon'];root_expected=None;probe_spent=Fraction(0)
        terminal=None
        while True:
            req=['multi-level-affine-f5-v1',m,n,[w['normal']['matrix'] for w in worlds],
                 cfg['probes'],[rat_wire(q) for q in fees],reuse_enabled,
                 [rat_wire(q) for q in warm_values],[rat_wire(q) for q in cold_values],horizon,history]
            plan=invoke(PLANNER,req,args.timeout,records)
            if root_expected is None:root_expected=as_fraction(plan['expected_net_value'])
            choice=plan['choice'];kind=choice['kind']
            step=dict(horizon=horizon,state=plan['state'],choice=choice,
                      expected_net_value=plan['expected_net_value'],planning_work=plan['planning_work'])
            if kind=='probe':
                if horizon==0:raise RuntimeError('probe selected at zero horizon')
                idx=choice['index']
                report=invoke(TERMINAL,['affine-terminal-probe-f5-v1',
                    worlds[cfg['actual_world']]['program'],cfg['probes'][idx]],args.timeout,records)
                outcome=bool(report['report']);history.append([idx,outcome]);probe_spent+=fees[idx]
                step['actual_report']=outcome;step['probe_fee']=str(fees[idx]);trace.append(step)
                horizon-=1
                continue
            if kind=='reuse':
                if not reuse_enabled:raise RuntimeError('planner selected unavailable reuse')
                terminal=get_deployment(worlds[cfg['actual_world']]['warm'])
            elif kind=='cold':terminal=get_deployment(worlds[cfg['actual_world']]['cold'])
            elif kind=='stop':terminal=None
            else:raise RuntimeError('unknown action kind')
            trace.append(step);break
        terminal_payoff=Fraction(0) if terminal is None else as_fraction(terminal['modeled_net_payoff'])
        realized=terminal_payoff-probe_spent
        # Exact catalogue construction is metareasoning outside the Bellman objective.
        prep=sum((get_deployment(w['cold'])['setup_charge'] for w in worlds),0)
        if reuse_enabled:prep+=sum((get_deployment(w['warm'])['setup_charge'] for w in worlds),0)
        world_summary=[]
        for i,w in enumerate(worlds):
            cd=get_deployment(w['cold']); wd=get_deployment(w['warm']) if reuse_enabled else None
            world_summary.append(dict(index=i,normal=w['normal'],
                cold=dict(payoff=cd['modeled_net_payoff'],setup=cd['setup_charge'],
                    per_call_original=cd['per_call_original'],per_call_selected=cd['per_call_selected'],
                    selected=cd['selected']),
                warm=(None if wd is None else dict(payoff=wd['modeled_net_payoff'],setup=wd['setup_charge'],
                    per_call_original=wd['per_call_original'],per_call_selected=wd['per_call_selected'],
                    selected=wd['selected']))))
        out=dict(status='executed_checked_multi_level_policy',field='ZMod(5)',world_count=len(worlds),
            actual_world=cfg['actual_world'],reuse_available=reuse_enabled,
            planner_expected_net=str(root_expected),actual_decision_net=str(realized),
            catalogue_preparation_charge=prep,
            end_to_end_net_after_catalogue_preparation=str(realized-Fraction(prep)),
            fixed_stop_expected='0',fixed_warm_expected=str(average(warm_values)) if reuse_enabled else None,
            fixed_cold_expected=str(average(cold_values)),probe_fees_actual=str(probe_spent),
            terminal_action=trace[-1]['choice']['kind'],terminal_deployment=terminal,
            catalogue=world_summary,history=history,trace=trace,invocations=records,
            boundary='terminal payoffs are derived from checked plans; exact model construction is charged separately and performed before planning')
        print(json.dumps(out,indent=2));return 0
    except (ValueError,OSError,RuntimeError,subprocess.SubprocessError,proposer.CreditExhausted) as e:
        print(json.dumps({'status':'error','error':str(e),'invocations':records},indent=2));return 2

if __name__=='__main__':raise SystemExit(main())
