"""Independent certificate checker. Imports NO discovery or Smith code.

The caller must supply its expected complete source specification. A source hash
inside an untrusted certificate alone never authenticates the intended problem.
Finite matrix equations imply all-state/all-word semantics by the separate
written proof and the generic Lean transport theorem. JSON parsing and these
Python arithmetic loops are not themselves formally verified.
"""
from __future__ import annotations
from hashlib import sha256
from math import isqrt
import json
from pathlib import Path
import sys

class InvalidCertificate(ValueError):pass

def require(ok, message):
    if not ok:raise InvalidCertificate(message)

def canonical(data):return json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode()

def scalar(v,m):return type(v) is int and 0<=v<m

def matrix(a,n,k,m):
    return isinstance(a,list) and len(a)==n and all(isinstance(row,list) and len(row)==k and all(scalar(v,m) for v in row) for row in a)

def mul(a,b,inner,out,m):
    return [[sum(a[i][k]*b[k][j] for k in range(inner))%m for j in range(out)] for i in range(len(a))]

def dot(a,b,m):return sum(x*y for x,y in zip(a,b))%m

def check(spec,cert):
    fields={'schema','p','r','dimension','actions','observations','initial_interface','word_order'}
    require(isinstance(spec,dict) and set(spec)==fields,'source fields')
    require(spec['schema']=='finite-linear-profile-v1','source schema')
    p,r,d=spec['p'],spec['r'],spec['dimension']
    require(type(p) is int and p>=2 and all(p%k for k in range(2,isqrt(p)+1)),'prime')
    require(type(r) is int and 1<=r<=256 and type(d) is int and 1<=d<=32,'dimensions')
    require(spec['initial_interface']=='all_states' and spec['word_order']=='left_to_right','profile contract')
    m=p**r;actions=spec['actions'];obs=spec['observations']
    require(isinstance(actions,list) and 1<=len(actions)<=16 and all(matrix(a,d,d,m) for a in actions),'source actions')
    require(isinstance(obs,list) and 1<=len(obs)<=32 and matrix(obs,len(obs),d,m),'source observations')
    cfields={'schema','source_sha256','dimension','basis','raw_tests','basis_combinations','transitions','observation_decoder','smith_valuations','V','V_inverse','strict_growth_witnesses'}
    require(isinstance(cert,dict) and set(cert)==cfields,'certificate fields')
    require(cert['schema']=='komorebi-observable-module-v0.2','certificate schema')
    require(cert['source_sha256']==sha256(canonical(spec)).hexdigest(),'source identity mismatch')
    t=cert['dimension'];P=cert['basis'];raw=[]
    require(type(t) is int and 0<=t<=d and matrix(P,t,d,m),'encoding shape')
    require(isinstance(cert['raw_tests'],list) and len(cert['raw_tests'])<=r*d,'witness limit')
    for test in cert['raw_tests']:
        require(isinstance(test,dict) and set(test)=={'observation','word'},'test schema')
        j,w=test['observation'],test['word']
        require(type(j) is int and 0<=j<len(obs) and isinstance(w,list) and len(w)<=r*d,'test index')
        require(all(type(a) is int and 0<=a<len(actions) for a in w),'digit outside operation signature')
        # Build A_last ... A_first on each input coordinate, independently.
        result=[]
        for k in range(d):
            v=[int(i==k) for i in range(d)]
            for a in w:v=[dot(row,v,m) for row in actions[a]]
            result.append(dot(obs[j],v,m))
        raw.append(result)
    n=len(raw);comb=cert['basis_combinations']
    require(matrix(comb,t,n,m),'combination shape')
    require(mul(comb,raw,n,d,m)==P,'encoding lacks observation provenance')
    C=cert['transitions'];D=cert['observation_decoder']
    require(isinstance(C,list) and len(C)==len(actions) and all(matrix(a,t,t,m) for a in C),'target actions')
    require(matrix(D,len(obs),t,m),'output decoder')
    for a,c in zip(actions,C):
        require(mul(P,a,d,d,m)==mul(c,P,t,d,m),'action intertwining failed')
    require(mul(D,P,t,d,m)==obs,'observation factorization failed')
    V,W,ss=cert['V'],cert['V_inverse'],cert['smith_valuations']
    require(matrix(V,d,d,m) and matrix(W,d,d,m),'Smith transformation shape')
    I=[[int(i==j) for j in range(d)] for i in range(d)]
    require(mul(V,W,d,d,m)==I and mul(W,V,d,d,m)==I,'noninvertible Smith frame')
    require(isinstance(ss,list) and len(ss)==t and all(type(s) is int and 0<=s<r for s in ss),'Smith valuations')
    require(ss==sorted(ss),'Smith order')
    expected=[[p**ss[i] if i==j else 0 for j in range(d)] for i in range(t)]
    require(mul(P,V,d,d,m)==expected,'claimed Smith form fails')
    events=cert['strict_growth_witnesses']
    require(isinstance(events,list) and len(events)==n,'growth witnesses')
    for i,(event,test,new) in enumerate(zip(events,cert['raw_tests'],raw)):
        require(set(event)=={'test','delta'},'growth event fields')
        delta=event['delta']
        require(event['test']==test and isinstance(delta,list) and len(delta)==d and all(scalar(v,m) for v in delta),'growth delta')
        require(all(dot(old,delta,m)==0 for old in raw[:i]),'delta visible to previous tests')
        require(dot(new,delta,m)!=0,'new test does not distinguish witness')
    return {'status':'PASS','coordinates':t,'quotient_p_digits':sum(r-s for s in ss),
            'all_initial_states':True,'all_finite_words':True,
            'linear_minimality':'written chain-ring generator proof; not new Lean minimum endpoint'}

if __name__=='__main__':
    if len(sys.argv)!=3:raise SystemExit('usage: check_certificate.py source.json certificate.json')
    print(json.dumps(check(json.loads(Path(sys.argv[1]).read_text()),json.loads(Path(sys.argv[2]).read_text())),indent=2))
