#!/usr/bin/env python3
"""Exact finite checks for acquisition quotienting and repair-relative pruning.

Assertions concern the recorded finite domains. Universal soundness depends on
stated arithmetic axioms and prose proofs, not on the size of these enumerations.
"""
from __future__ import annotations
from collections import Counter
from fractions import Fraction as Q
from itertools import product,combinations
from pathlib import Path
import copy,json,time
from meta_synthesis import *
from weighted_repair_pruning import *
from repair_calculus import compile_frontier,check_tree,tree_depth,tree_records,cell_problem
from synthesized_pruning import prefix_contexts,impossible_by_completions,synthesize
from demo_meta import tasks

ROOT=Path(__file__).resolve().parents[1]
GROUPS=[];TOTAL=0

def check(claim):
    global TOTAL
    TOTAL+=1
    if not claim:raise AssertionError('Exact check failed.')

def rejected(fn):
    try:fn()
    except (ValueError,TypeError,KeyError,IndexError):check(True);return
    check(False)

def group(name,domain):
    def deco(fn):GROUPS.append((name,domain,fn));return fn
    return deco

LIB,LEARN=discover_library();PS=grammar();IND,QR=ordered_quotient(PS,LIB)

@group('every admitted schema has a replayable proof and signed-value cross-check',
       '336 admitted equations, all integer substitutions x,y in -2..3; independent direct evaluations')
def schemas():
    check(len(LIB['equations'])==336);check(LEARN['unproved_proposals']==732)
    for cert in LIB['equations']:
        validate_equation(cert)
        for x,y in product(range(-2,4),repeat=2):
            check(value(cert['left'],{'x':x,'y':y})==value(cert['right'],{'x':x,'y':y}))
    check(discover_library()[0]==LIB)

@group('ordered program quotient preserves semantics on all declared signed corners',
       '3960 grammar programs, 16 feature contexts over {-2,3}; earliest representative and 1362 retained entries')
def quotient():
    check(len(IND)==1362);check(len(QR['representative_indices'])==3960)
    for i,e in enumerate(PS):
        j=QR['representative_indices'][i]
        check(j<=i and j in IND)
        check(QR['normal_forms'][i]==QR['normal_forms'][j])
        for vals in product((-2,3),repeat=4):
            ctx=dict(zip(('a','b','m','c'),vals))
            check(value(e,ctx)==value(PS[j],ctx))
    check(verify_quotient(PS,LIB,QR)==IND)

@group('malformed and unsupported equational certificates are rejected',
       'Every admitted schema with an unsupported axiom or wrong endpoint; mismatched semantics and wrong sorts')
def bad_certificates():
    for cert in LIB['equations']:
        changed=copy.deepcopy(cert)
        changed['left_steps']=[{'path':[],'law':'invented_equality'}]
        rejected(lambda:validate_equation(changed))
        changed=copy.deepcopy(cert);changed['common']=('999',)
        rejected(lambda:validate_equation(changed))
    bad=copy.deepcopy(LIB['equations'][0]);bad['semantics']='addition-with-hidden-state'
    rejected(lambda:validate_equation(bad))
    rejected(lambda:equation_certificate(('true',),('x',)))
    rejected(lambda:sort_of(('+',('true',),('1',))))

@group('finite agreement is not global equivalence, and failure to prove is not falsity',
       'max(x,1)=x on x=1,2,3 versus x=0; max(x,0)=x on naturals versus negative integers')
def finite_equivalence():
    a=('max',('x',),('1',));b=('x',)
    for x in (1,2,3):check(value(a,{'x':x})==value(b,{'x':x}))
    check(value(a,{'x':0})!=value(b,{'x':0}))
    rejected(lambda:equation_certificate(a,b))
    a=('max',('x',),('0',))
    for x in range(8):check(value(a,{'x':x})==x)
    check(value(a,{'x':-1})!=-1)
    rejected(lambda:equation_certificate(a,b))

@group('CEGIS task proposals and first counterexamples are preserved',
       'Nine distinct target ASTs; 256 contexts in {0,1,3,5}^4; exact original AST and teacher trace, not only final values')
def target_tasks():
    contexts=tuple(dict(zip(('a','b','m','c'),x)) for x in product((0,1,3,5),repeat=4))
    eager,_=eager_quotient(PS)
    for name,target in tasks():
        labels=tuple(value(target,c) for c in contexts)
        a=cegis(PS,contexts,labels);b=cegis(PS,contexts,labels,IND);c=cegis(PS,contexts,labels,eager)
        check(a['trace']==b['trace']==c['trace'])
        check(a['winner']==b['winner']==c['winner'])
        check(b['counters']['example_evaluations']<=a['counters']['example_evaluations'])
        check(b['counters']['teacher_evaluations']==a['counters']['teacher_evaluations'])
        check(b['counters']['semantic_node_visits']<=a['counters']['semantic_node_visits'])
    check(len(eager)==1352)  # The stronger supplied normalizer is retained as a control.

@group('cold reacquisition and genuine finite grammar exhaustion',
       '198 capacity prefixes matching v0.3; parity on every four-feature context in {0,1,2,3}^4')
def reacquisition():
    contexts=prefix_contexts();labels=tuple(impossible_by_completions(c) for c in contexts)
    a=cegis(PS,contexts,labels);b=cegis(PS,contexts,labels,IND);old,record=synthesize()
    check(a['winner']==b['winner']==old);check(a['trace']==b['trace'])
    check(a['counters']['semantic_node_visits']==1898);check(b['counters']['semantic_node_visits']==1376)
    cs=tuple(dict(zip(('a','b','m','c'),x)) for x in product(range(4),repeat=4))
    ys=tuple(c['a']%2==0 for c in cs)
    a=cegis(PS,cs,ys);b=cegis(PS,cs,ys,IND)
    check(a['status']==b['status']=='grammar_exhausted');check(a['trace']==b['trace'])

@group('cached quotient is invalidated by a changed grammar or semantics',
       'Altered semantic name, grammar order, quotient representative and library proof')
def binding():
    bad=copy.deepcopy(QR);bad['semantics']='different'
    rejected(lambda:verify_quotient(PS,LIB,bad))
    rejected(lambda:verify_quotient(tuple(reversed(PS)),LIB,QR))
    bad=copy.deepcopy(QR);bad['representative_indices'][0]=1
    rejected(lambda:verify_quotient(PS,LIB,bad))
    badlib=copy.deepcopy(LIB);badlib['equations'][0]['common']=('999',)
    rejected(lambda:ordered_quotient(PS,badlib))
    # If '+' silently changes to x+y+1, the former identity x+0=x is false.
    for x in range(4):check(x+0+1!=x)

@group('repair-weight feasibility and greedy construction on every small repair family',
       'n=1..3; every family of one or two nonempty success sets; rational exact loads')
def weights():
    for n in range(1,4):
        subsets=[frozenset(x for x in range(n) if mask>>x&1) for mask in range(1,1<<n)]
        for k in (1,2):
            for family in combinations(subsets,k):
                p=Problem(n,(),tuple(Repair(f'r{i}',Q(1),s) for i,s in enumerate(family)))
                w,r=checked_greedy_weights(p)
                check(all(v>=0 for v in w))
                for rep in p.repairs:check(sum(w[x] for x in rep.good)<=1)
                uniform=tuple(Q(1,max(map(len,family))) for _ in range(n))
                check(verify_weights(p,uniform)[0]==uniform)

@group('weighted depth-first search matches unpruned exact synthesis on small models',
       'n=1..3; all one/two nonempty repair sets; every ordered pair of total binary tables; horizons 0..2; greedy exact weights')
def weighted_search():
    for n in range(1,4):
        subsets=[frozenset(x for x in range(n) if mask>>x&1) for mask in range(1,1<<n)]
        families=[family for k in (1,2) for family in combinations(subsets,k)]
        for family in families:
            reps=tuple(Repair(f'r{i}',Q(1),s) for i,s in enumerate(family))
            for bits in product((0,1),repeat=2*n):
                es=tuple(Experiment(f'e{i}',Q(1),tuple((x,bits[i*n+x]) for x in range(n))) for i in (0,1))
                p=Problem(n,es,reps);w,_=checked_greedy_weights(p)
                for h in (0,1,2):
                    front=compile_frontier(p,range(n),h)
                    a,ar=ordered_weighted_search(p,h,w,False);b,br=ordered_weighted_search(p,h,w,True)
                    check(a==b);check(bool(front)==(a is not None))
                    check(br['counters'].get('search_model_reads',0)<=ar['counters'].get('search_model_reads',0))
                    check(ar['counters'].get('search_model_reads',0)-br['counters'].get('search_model_reads',0)==br['counters'].get('rows_skipped',0))
                    if a is not None:
                        check(sum(w)<=2**h)
                        check(check_tree(p,range(n),a,h)==(Q(ar['witness']['work']),ar['witness']['storage']))

@group('fractional cover witnesses can be stronger than the supplied greedy construction',
       'Three states, three two-state repairs, weights (1/2,1/2,1/2), one informative query; exact costs and bounds')
def fractional_weights():
    p=Problem(3,(Experiment('split',Q(1),((0,0),(1,1),(2,1))),),
       tuple(Repair(f'r{i}',Q(1),s) for i,s in enumerate((frozenset((0,1)),frozenset((1,2)),frozenset((0,2))))))
    greedy,_=checked_greedy_weights(p);w=(Q(1,2),)*3
    check(sum(greedy)==1);check(sum(w)==Q(3,2))
    check(verify_weights(p,w)[0]==w)
    t,r=ordered_weighted_search(p,0,w);check(t is None)
    a,x=ordered_weighted_search(p,1,w,False);b,y=ordered_weighted_search(p,1,w,True)
    check(a==b);check(x['witness']=={'work':'2','storage':3})
    for rep in p.repairs:check(sum(w[j] for j in rep.good)==1)

@group('stale weight scopes, negative weights and mutable operations are rejected',
       'Paired repair case with universal repair added; malformed weights and each mutable/partial/nonbinary transition')
def stale_weights():
    p=paired_repair_problem(4);w,_=checked_greedy_weights(p)
    broad=Problem(p.n,p.experiments,p.repairs+(Repair('all',Q(1),frozenset(range(p.n))),))
    rejected(lambda:verify_weights(broad,w))
    fresh,_=checked_greedy_weights(broad);tree,r=ordered_weighted_search(broad,0,fresh)
    check(r['witness']=={'work':'1','storage':1})
    rejected(lambda:verify_weights(p,[-1]*p.n));rejected(lambda:verify_weights(p,[Q(0)]*(p.n-1)))
    rejected(lambda:verify_weights(p,[0.0]*p.n))
    e=p.experiments[0]
    for entry in (None,(1,0),(0,2)):
        rows=list(e.transitions);rows[0]=entry
        bad=Problem(p.n,(Experiment('bad',Q(1),tuple(rows)),),p.repairs)
        rejected(lambda:verify_weights(bad,w))

@group('cover bounds do not invent experiments and need not be tight',
       'Four states, one constant report query, two disjoint repairs; zero weights on singleton repair model')
def weak_certificates():
    p=Problem(4,(Experiment('constant',Q(1),tuple((x,0) for x in range(4))),),
       (Repair('left',Q(1),frozenset((0,1))),Repair('right',Q(1),frozenset((2,3)))))
    w,_=checked_greedy_weights(p)
    check(sum(w)==2)
    t,r=ordered_weighted_search(p,3,w);check(t is None)
    q=cell_problem(4);t,r=ordered_weighted_search(q,2,[Q(0)]*4)
    check(t is not None)  # a useless bound remains safe, but saves no reads

@group('multi-case repair demonstration and complete read accounting',
       '2,4,8,16 repair groups with two cases each; every case replayed; same full-scan and streaming tree')
def large_repairs():
    expected={2:(20,18,2,3),4:(152,120,3,7),8:(864,608,4,15),16:(4416,2864,5,31)}
    for g,(full,stream,work,storage) in expected.items():
        p=paired_repair_problem(g);w,_=checked_greedy_weights(p);h=(g-1).bit_length()
        a,x=ordered_weighted_search(p,h,w,False);b,y=ordered_weighted_search(p,h,w,True)
        check(a==b);check(x['counters']['search_model_reads']==full);check(y['counters']['search_model_reads']==stream)
        check(x['witness']==y['witness']=={'work':str(work),'storage':storage})
        check(sum(w)==g);check(tree_records(a)==storage)
        check(y['counters']['capacity_comparisons']>x['counters']['capacity_comparisons'])

@group('extra construction work is not erased by smaller per-task counters',
       'Cold capacity target and frozen quotient, separately measured setup events')
def costs():
    ctx=prefix_contexts();ys=tuple(impossible_by_completions(x) for x in ctx)
    a=cegis(PS,ctx,ys);b=cegis(PS,ctx,ys,IND)
    savings=a['counters']['semantic_node_visits']-b['counters']['semantic_node_visits']
    check(savings==522)
    setup=QR['counters']['schema_match_attempts']
    check(setup>savings)  # even this single setup coordinate exceeds this per-use gain
    check(LEARN['library_bytes']>0)


def main():
    started=time.perf_counter();rows=[]
    for name,domain,fn in GROUPS:
        before=TOTAL;t=time.perf_counter();fn()
        rows.append({'name':name,'domain':domain,'assertions':TOTAL-before,'status':'PASS','runtime_seconds':time.perf_counter()-t})
        print(name,'PASS',TOTAL-before,flush=True)
    report={'status':'PASS','groups':rows,'group_count':len(rows),'assertions':TOTAL,
            'arithmetic':'Exact Python integers, finite sets, fractions.Fraction',
            'runtime_seconds':time.perf_counter()-started,
            'non_claim':'Finite implementation checks, not universal proof, independent review or empirical general intelligence.'}
    (ROOT/'validation/meta_checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f'PASS: {len(rows)} groups, {TOTAL} assertions.')
if __name__=='__main__':main()
