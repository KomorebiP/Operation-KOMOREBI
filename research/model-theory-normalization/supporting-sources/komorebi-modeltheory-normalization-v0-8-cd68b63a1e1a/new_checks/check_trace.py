"""Independent exact checker: no discover.py, chainring.py or Smith imports.
Checks supplied source metadata, FIFO evolution, every branch witness, and final
queue exhaustion. The caller supplies the intended source separately.
"""
from __future__ import annotations
from collections import deque
from hashlib import sha256
import json
from math import isqrt
from typing import Any


def canonical(x: Any) -> bytes:
    return json.dumps(x,sort_keys=True,separators=(',', ':'),ensure_ascii=True).encode()


def validate(source: dict) -> tuple[int,int,int,int]:
    if set(source) != {'schema','p','r','dimension','actions','observations','initial_interface','word_order'}:
        raise ValueError('source fields')
    p,r,d=source['p'],source['r'],source['dimension']
    if type(p) is not int or p<2 or any(p%i==0 for i in range(2,isqrt(p)+1)):
        raise ValueError('prime required')
    if type(r) is not int or not 1<=r<=256 or type(d) is not int or not 1<=d<=32:
        raise ValueError('finite implementation bounds')
    if source['schema']!='finite-linear-profile-v1' or source['initial_interface']!='all_states' or source['word_order']!='left_to_right':
        raise ValueError('profile semantics')
    if not 1<=len(source['actions'])<=16 or not 1<=len(source['observations'])<=32:
        raise ValueError('signature bounds')
    m=p**r
    for A in source['actions']:
        if len(A)!=d or any(len(row)!=d for row in A):raise ValueError('action shape')
    if any(len(v)!=d for v in source['observations']):raise ValueError('observation shape')
    values=[v for A in source['actions'] for row in A for v in row]+[v for row in source['observations'] for v in row]
    if any(type(v) is not int or not 0<=v<m for v in values):raise ValueError('coefficient outside ring')
    return p,r,d,m


def test_row(source:dict,test:dict) -> list[int]:
    m=source['p']**source['r'];d=source['dimension'];v=source['observations'][test['observation']][:]
    for a in reversed(test['word']):
        A=source['actions'][a]
        v=[sum(v[h]*A[h][j] for h in range(d))%m for j in range(d)]
    return v


def check_trace(source:dict,trace:dict) -> dict:
    p,r,d,m=validate(source)
    if set(trace)!={'schema','source_sha256','events','result','status'} or trace['schema']!='complete-observation-queue-trace-v1' or trace['status']!='complete':
        raise ValueError('trace schema/status')
    if trace['source_sha256']!=sha256(canonical(source)).hexdigest():raise ValueError('unexpected source')
    events=trace['events'];k=len(source['actions']);o=len(source['observations'])
    if len(events)>o+k*r*d:raise ValueError('too many candidates')
    pending=deque({'word':[],'observation':j} for j in range(o))
    tests=[];rows=[];accepts=0;skips=0
    for ev in events:
        if not pending:raise ValueError('trailing event after queue exhaustion')
        t=pending.popleft()
        if ev.get('test')!=t:raise ValueError('wrong FIFO test or word order')
        v=test_row(source,t)
        if ev.get('decision')=='skip':
            if set(ev)!={'test','decision','coefficients'}:raise ValueError('skip fields')
            c=ev['coefficients']
            if len(c)!=len(rows) or any(type(a)is not int or not 0<=a<m for a in c):raise ValueError('skip witness shape')
            reconstructed=[sum(a*b[j] for a,b in zip(c,rows))%m for j in range(d)]
            if reconstructed!=v:raise ValueError('invalid span coefficients')
            skips+=1
        elif ev.get('decision')=='accept':
            if set(ev)!={'test','decision','delta'}:raise ValueError('accept fields')
            delta=ev['delta']
            if len(delta)!=d or any(type(a)is not int or not 0<=a<m for a in delta):raise ValueError('delta shape')
            dot=lambda row:sum(a*b for a,b in zip(row,delta))%m
            if any(dot(row) for row in rows) or dot(v)==0:raise ValueError('invalid separating witness')
            rows.append(v);tests.append(t);accepts+=1
            if accepts>r*d or len(t['word'])>=accepts:raise ValueError('rank/horizon bound')
            for a in range(k):pending.append({'word':[a]+t['word'],'observation':t['observation']})
        else:raise ValueError('unknown decision')
    if pending:raise ValueError('trace stopped before queue exhaustion')
    if trace['result']!=tests:raise ValueError('incorrect returned tests')
    if len(events)!=o+k*accepts:raise ValueError('queue accounting')
    return {'accepted':accepts,'skipped':skips,'candidates':len(events),
            'bound_accepted':r*d,'bound_candidates':o+k*r*d,
            'horizon':max((len(t['word']) for t in tests),default=0)}
