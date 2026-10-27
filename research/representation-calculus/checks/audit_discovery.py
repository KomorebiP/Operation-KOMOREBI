"""Deterministic, scope-declared tests. Synthetic examples are not new theorems."""
from __future__ import annotations
from collections import Counter
from copy import deepcopy
from itertools import product
from pathlib import Path
import importlib.util
import json
import random
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from discover import discover,encode,compressed_output,matvec,rowmul,canonical
from checks.check_certificate import check,InvalidCertificate

COUNTS=Counter()
def require(ok,label):
    COUNTS[label]+=1
    if not ok:raise AssertionError(label)

def identity(d):return [[int(i==j) for j in range(d)] for i in range(d)]
def mm(a,b,m):return [[sum(x*y for x,y in zip(row,col))%m for col in zip(*b)] for row in a]
def spec(p,r,d,acts,obs):
    return {'schema':'finite-linear-profile-v1','p':p,'r':r,'dimension':d,
      'actions':acts,'observations':obs,'initial_interface':'all_states','word_order':'left_to_right'}
def scramble(s,rng):
    d=s['dimension'];m=s['p']**s['r'];U=identity(d);V=identity(d)
    if d>1:
        for _ in range(8*d):
            i,j=rng.sample(range(d),2);c=rng.randrange(m)
            E=identity(d);E[i][j]=c
            F=identity(d);F[i][j]=(-c)%m
            U=mm(E,U,m);V=mm(V,F,m)
    require(mm(U,V,m)==identity(d),'fixture_invertible_scramble')
    out=deepcopy(s)
    out['actions']=[mm(mm(U,a,m),V,m) for a in s['actions']]
    out['observations']=[rowmul(o,V,m) for o in s['observations']]
    return out

def finite_quotient(s):
    """Independent exhaustive table algorithm, only for <=256 source states."""
    d=s['dimension'];m=s['p']**s['r']
    states=list(product(range(m),repeat=d));index={x:i for i,x in enumerate(states)}
    tables=[[index[tuple(matvec(a,x,m))] for x in states] for a in s['actions']]
    outputs=[tuple(sum(a*b for a,b in zip(o,x))%m for o in s['observations']) for x in states]
    def labels(signatures):
        dic={};return [dic.setdefault(v,len(dic)) for v in signatures]
    part=labels(outputs);history=[len(set(part))]
    for _ in range(len(states)):
        new=labels([(part[i],tuple(part[a[i]] for a in tables)) for i in range(len(states))])
        if len(set(new))==len(set(part)):part=new;break
        part=new;history.append(len(set(part)))
    else:raise AssertionError('finite reference failed to stabilize')
    return states,part,history

def run_case(name,s,rng,do_exhaustive=False):
    got=discover(s);cert=got['certificate'];m=s['p']**s['r'];d=s['dimension']
    verdict=check(s,cert);require(verdict['status']=='PASS','independent_symbolic_certificate')
    (ROOT/'certificates'/f'{name}.source.json').write_text(json.dumps(s,indent=2)+'\n')
    (ROOT/'certificates'/f'{name}.certificate.json').write_text(json.dumps(cert,indent=2)+'\n')
    for _ in range(12):
        x=[rng.randrange(m) for _ in range(d)];w=[rng.randrange(len(s['actions'])) for _ in range(rng.randrange(13))]
        z=list(x)
        for a in w:z=matvec(s['actions'][a],z,m)
        for j,o in enumerate(s['observations']):
            expected=sum(a*b for a,b in zip(o,z))%m
            actual=compressed_output(cert,encode(cert,x,m),w,j,m)
            require(actual==expected,'sample_state_word_observation')
    for event in cert['strict_growth_witnesses']:
        j,w=event['test']['observation'],event['test']['word'];x=event['delta']
        z=list(x)
        for a in w:z=matvec(s['actions'][a],z,m)
        require(sum(a*b for a,b in zip(s['observations'][j],z))%m!=0,'witness_actual_word_distinguishes')
    if do_exhaustive:
        states,part,hist=finite_quotient(s)
        mapping={};reverse={}
        for x,label in zip(states,part):
            y=tuple(encode(cert,x,m))
            require(mapping.setdefault(label,y)==y and reverse.setdefault(y,label)==label,'exhaustive_same_partition')
        require(len(mapping)==s['p']**verdict['quotient_p_digits'],'exhaustive_quotient_cardinality')
        got['summary']['exhaustive_reference_classes']=len(mapping)
        got['summary']['exhaustive_source_states']=len(states)
        got['summary']['reference_history']=hist
    return got['summary']

def audit():
    start=time.monotonic();rng=random.Random(2026092002);summaries={}
    for case in range(180):
        p=(2,3,5)[case%3];r=1+(case//3)%5;d=1+(case//15)%6;m=p**r
        acts=[[[rng.randrange(m) for _ in range(d)] for _ in range(d)] for _ in range(1+case%3)]
        obs=[[rng.randrange(m) for _ in range(d)] for _ in range(1+(case%2))]
        # Include identically zero and uniformly torsion observations.
        if case%13==0:obs=[[0]*d for _ in obs]
        elif case%7==0:obs=[[(p**(r-1)*v)%m for v in row] for row in obs]
        s=spec(p,r,d,acts,obs)
        name=f'random_{case:03d}';summaries[name]=run_case(name,s,rng,p**(r*d)<=256)
    # Completely specified mixed-precision hidden-coordinate family. The
    # conjugating matrices are NOT passed to discover(). These are synthetic
    # structural tests, not a held-out learned discovery experiment.
    for p in (2,3,5):
      for r in (2,3,5):
       for d in (4,6):
        m=p**r;A=identity(d);A[0][1]=p
        B=identity(d);B[0][0]=2%m
        for i in range(2,d):
            A[i]=[rng.randrange(m) for _ in range(d)]
            B[i]=[rng.randrange(m) for _ in range(d)]
        s=scramble(spec(p,r,d,[A,B],[[1]+[0]*(d-1)]),rng)
        name=f'hidden_p{p}_r{r}_d{d}';summaries[name]=run_case(name,s,rng)
        require(summaries[name]['coordinate_count']==2,'hidden_two_coordinates')
        require(summaries[name]['quotient_p_digits']==2*r-1,'hidden_torsion_length')
    # 2^128 source states, but this is verified through small matrix identities.
    d=8;r=16;m=2**r;A=identity(d);A[0][1]=4;B=identity(d);B[0][0]=3;B[1][1]=5
    for i in range(2,d):
        A[i]=[rng.randrange(m) for _ in range(d)];B[i]=[rng.randrange(m) for _ in range(d)]
    big=scramble(spec(2,r,d,[A,B],[[1]+[0]*(d-1)]),rng)
    summaries['scrambled_128bit']=run_case('scrambled_128bit',big,rng)
    require(summaries['scrambled_128bit']['coordinate_count']==2,'big_two_coordinates')
    require(summaries['scrambled_128bit']['quotient_p_digits']==30,'big_thirty_digits')
    # Long future dependence: observing x0 after j shifts reveals xj.
    A=[[int(j==i+1) for j in range(8)] for i in range(8)]
    s=spec(2,4,8,[A],[[1]+[0]*7])
    summaries['delay_chain']=run_case('delay_chain',s,rng)
    require(summaries['delay_chain']['max_test_word_length']==7,'delay_seven_steps')
    # Minimize at modulus four, then lower precision: a real noncommutation.
    lo=spec(2,1,1,[[[1]]],[[0]])
    hi=spec(2,2,1,[[[1]]],[[2]])
    summaries['precision_one']=run_case('precision_one',lo,rng,True)
    summaries['precision_two']=run_case('precision_two',hi,rng,True)
    require(summaries['precision_one']['coordinate_count']==0 and summaries['precision_two']['coordinate_count']==1,'precision_noncommutation')
    # These controls operate on a known nontrivial certificate, not random luck.
    base=spec(2,4,2,[[[1,4],[0,1]]],[[1,0]])
    cert=discover(base)['certificate'];mutations=[]
    c=deepcopy(cert);c['source_sha256']='0'*64;mutations.append(('source_hash',base,c))
    c=deepcopy(cert);c['basis'][0][0]=2;mutations.append(('encoding',base,c))
    c=deepcopy(cert);c['basis_combinations'][0][0]=0;mutations.append(('fake_provenance',base,c))
    c=deepcopy(cert);c['transitions'][0][0][1]=0;mutations.append(('transition',base,c))
    c=deepcopy(cert);c['observation_decoder'][0][0]=0;mutations.append(('observation',base,c))
    c=deepcopy(cert);c['V_inverse'][0][0]=0;mutations.append(('inverse',base,c))
    c=deepcopy(cert);c['smith_valuations'][1]=1;mutations.append(('lost_torsion',base,c))
    c=deepcopy(cert);c['raw_tests'][1]['word']=[];mutations.append(('false_word',base,c))
    c=deepcopy(cert);c['strict_growth_witnesses'][1]['delta']=[0,0];mutations.append(('false_counterexample',base,c))
    new=deepcopy(base);new['actions'][0][0][1]=0;mutations.append(('changed_operation_profile',new,deepcopy(cert)))
    c=deepcopy(cert);c['source_sha256']=__import__('hashlib').sha256(canonical(new)).hexdigest();mutations.append(('changed_profile_rebound_hash',new,c))
    for name,source,c in mutations:
        try:check(source,c)
        except (InvalidCertificate,TypeError,KeyError,IndexError):COUNTS['corrupt_certificates_rejected']+=1
        else:raise AssertionError('accepted mutation: '+name)
    for bad in (dict(base,p=4),dict(base,r=0),dict(base,initial_interface='single_seed'),dict(base,word_order='reversed')):
        try:discover(bad)
        except ValueError:COUNTS['invalid_inputs_rejected']+=1
        else:raise AssertionError('invalid input accepted')
    try:discover(base,max_accepts=1)
    except RuntimeError:COUNTS['resource_cap_unresolved']+=1
    else:raise AssertionError('cap incorrectly accepted')
    result={'status':'PASS','seed':2026092002,'case_count':len(summaries),'check_counts':dict(COUNTS),
      'runtime_seconds':time.monotonic()-start,'cases':summaries,
      'scope':'Known complete finite-dimensional linear models over residue rings, all initial states. Synthetic fixtures; no trained AI, no blind benchmark or superiority claim.',
      'finite_tests_do_not_replace':'Symbolic certs have written all-word proof reduction; generic finite transport soundness is formalized. Python checker/Smith implementation not Lean-verified.'}
    (ROOT/'results/DISCOVERY_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    print('BIG',summaries['scrambled_128bit'])

if __name__=='__main__':audit()
