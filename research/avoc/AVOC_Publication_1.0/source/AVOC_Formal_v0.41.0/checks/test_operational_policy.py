#!/usr/bin/env python3
from __future__ import annotations
import json
from fractions import Fraction
from functools import lru_cache
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def Q(x):
    if x is None:return None
    if isinstance(x,str):return Fraction(x)
    if type(x) is int:return Fraction(x)
    if isinstance(x,list):return Fraction(x[0],x[1])
    raise TypeError(x)

def detects(A,p):
    if p[0]=='entry':return A[p[1]][p[2]]%5!=0
    _,r1,r2,c1,c2=p
    return (A[r1][c1]*A[r2][c2]-A[r1][c2]*A[r2][c1])%5!=0

def audit(config_path,result_path):
    cfg=json.load(open(config_path));out=json.load(open(result_path))
    assert out['status']=='executed_checked_multi_level_policy'
    As=[w['normal']['matrix'] for w in out['catalogue']]
    cold=[Q(w['cold']['payoff']) for w in out['catalogue']]
    warm=[Q(w['warm']['payoff']) if w['warm'] else None for w in out['catalogue']]
    fees=[Q(x) for x in cfg['fees']];probes=cfg['probes'];reuse=out['reuse_available']
    @lru_cache(None)
    def V(worlds,rem,h):
        worlds=tuple(worlds);rem=tuple(rem)
        if h==0:return Fraction(),('stop',None)
        vals=[(Fraction(),('stop',None))]
        if reuse:vals.append((sum(warm[i] for i in worlds)/len(worlds),('reuse',None)))
        vals.append((sum(cold[i] for i in worlds)/len(worlds),('cold',None)))
        for p in rem:
            yes=tuple(i for i in worlds if detects(As[i],probes[p]));no=tuple(i for i in worlds if not detects(As[i],probes[p]))
            if not yes:yes=worlds
            if not no:no=worlds
            nr=tuple(x for x in rem if x!=p)
            ps=Fraction(sum(detects(As[i],probes[p]) for i in worlds),len(worlds))
            val=-fees[p]+ps*V(yes,nr,h-1)[0]+(1-ps)*V(no,nr,h-1)[0]
            vals.append((val,('probe',p)))
        # Stable first maximum, matching stop/reuse/cold/probe ordering.
        best=vals[0]
        for z in vals[1:]:
            if z[0]>best[0]:best=z
        return best
    worlds=tuple(range(len(As)));rem=tuple(range(len(probes)))
    for p,o in cfg.get('history',[]):
        sub=tuple(i for i in worlds if detects(As[i],probes[p])==bool(o))
        if sub:worlds=sub
        rem=tuple(x for x in rem if x!=p)
    root=V(worlds,rem,cfg['horizon'])
    assert root[0]==Q(out['planner_expected_net']),(root,out['planner_expected_net'])
    first=out['trace'][0]['choice'];firstw=(first['kind'],first.get('index'))
    assert firstw==root[1],(firstw,root[1])
    fees_paid=Fraction();h=cfg['horizon'];actual=cfg['actual_world']
    for step in out['trace']:
        val,choice=V(worlds,rem,h)
        cw=(step['choice']['kind'],step['choice'].get('index'))
        assert cw==choice and val==Q(step['expected_net_value'])
        if choice[0]=='probe':
            p=choice[1];o=detects(As[actual],probes[p]);assert step['actual_report'] is o
            sub=tuple(i for i in worlds if detects(As[i],probes[p])==o)
            if sub:worlds=sub
            rem=tuple(x for x in rem if x!=p);fees_paid+=fees[p];h-=1
        else:break
    terminal=out['terminal_action']
    actual_payoff=Fraction()
    if terminal=='reuse':actual_payoff=warm[actual]
    elif terminal=='cold':actual_payoff=cold[actual]
    assert actual_payoff-fees_paid==Q(out['actual_decision_net'])
    assert sum(cold)/len(cold)==Q(out['fixed_cold_expected'])
    if reuse:assert sum(warm)/len(warm)==Q(out['fixed_warm_expected'])
    return {'case':Path(config_path).stem,'root_value':str(root[0]),'first_choice':root[1],
            'actual_net':str(actual_payoff-fees_paid),'trace_steps':len(out['trace'])}

def main():
    cases=[]
    for name in ('cold_catalogue','warm_catalogue'):
        cases.append(audit(ROOT/f'examples/operational/{name}.json',ROOT/f'results/v0.34.0/operational/{name}.json'))
    summary={'status':'pass','cases':cases}
    (ROOT/'results/v0.34.0/operational/policy_oracle.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
