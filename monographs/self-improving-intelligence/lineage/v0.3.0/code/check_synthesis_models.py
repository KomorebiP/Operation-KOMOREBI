#!/usr/bin/env python3
"""Exact bounded cross-checks for synthesized prefix pruning and its scope.

The universal statements are proved in the manuscript. These tests check their
finite surrogates and deliberately reject unsupported formulas or certificates.
"""
from pathlib import Path
from fractions import Fraction as Q
from itertools import product, combinations
from collections import Counter
import json, time
from synthesized_pruning import (grammar, expr_size, parse_expr, evaluate,
    prefix_contexts, impossible_by_completions, feature_conflict, synthesize,
    certify_rule, compile_streaming, cover_number)
from repair_calculus import (Problem, Experiment, Repair, Tree, cell_problem,
    compile_frontier, check_tree, tree_to_dict, tree_from_dict, relabel_problem)

ROOT=Path(__file__).resolve().parents[1]
GROUPS=[];COUNT=0

def check(condition,message='finite assertion failed'):
    global COUNT
    COUNT+=1
    if not condition:raise AssertionError(message)

def rejected(f):
    try:f()
    except (ValueError,TypeError,KeyError):return True
    return False

def group(name,domain):
    def decorate(f):
        start=COUNT;t=time.perf_counter();f()
        GROUPS.append({'name':name,'domain':domain,'assertions':COUNT-start,
                       'seconds':time.perf_counter()-t,'status':'PASS'})
        return f
    return decorate

def points(front):return {(w.work,w.storage) for w in front}

RULE,LEARNING=synthesize()

@group('typed syntax and exhaustive bounded grammar',
       'All 3960 generated ASTs with 3 or 5 nodes, six integer atoms, +/min/max and five comparisons.')
def syntax():
    gs=grammar();check(len(gs)==3960);check(len(set(gs))==3960)
    for e in gs:
        check(expr_size(e) in (3,5))
        check(parse_expr(json.loads(json.dumps(e)))==e)
        check(type(evaluate(e,{'a':1,'b':2,'m':4,'c':2})) is bool)

@group('feature obstruction and finite synthesis receipt',
       'All 198 prefixes with capacity 1,2,4 and total size 2..2c; all programs preceding the first passing AST.')
def learning():
    contexts=prefix_contexts();labels=[impossible_by_completions(c) for c in contexts]
    conflict=feature_conflict(contexts,labels,('a','b','m'))
    check(conflict is not None);check(conflict['left_label']!=conflict['right_label'])
    check(all(conflict['left'][f]==conflict['right'][f] for f in ('a','b','m')))
    check(feature_conflict(contexts,labels,('a','b','m','c')) is None)
    check(LEARNING['counterexamples']==3)
    check(LEARNING['expression_text']=='(max(a,b) > c)')
    for context,label in zip(contexts,labels):check(evaluate(RULE,context)==label)
    index=grammar().index(RULE);check(index==189)
    for expression in grammar()[:index]:
        check(any(evaluate(expression,c)!=y for c,y in zip(contexts,labels)))
    for row in LEARNING['trace'][:-1]:
        e=grammar()[row['candidate_index']]
        check(evaluate(e,row['context'])!=row['label'])
    again,record=synthesize();check(again==RULE);check(record==LEARNING)

@group('prefix capacity against literal binary completions',
       'Every binary prefix and all remaining suffixes for total sizes 2..8, all integer capacities ceil(m/2)..8.')
def prefix_theorem():
    for m in range(2,9):
        for cap in range((m+1)//2,9):
            for t in range(m+1):
                for ones in range(t+1):
                    ctx={'a':t-ones,'b':ones,'m':m,'c':cap}
                    possible=any(ctx['a']+tail.count(0)<=cap and ctx['b']+tail.count(1)<=cap
                                 for tail in product((0,1),repeat=m-t))
                    check(evaluate(RULE,ctx)==(not possible))
                    check(impossible_by_completions(ctx)==(not possible))

@group('streaming search matches exact compiler on every small binary table pair',
       'n=1..4, every ordered pair of total immutable binary tables, horizon ceil(log2 n); independent parent frontier.')
def all_tables():
    for n in range(1,5):
        reps=tuple(Repair(f'r{x}',Q(1),frozenset((x,))) for x in range(n))
        for bits in product((0,1),repeat=2*n):
            es=tuple(Experiment(f'e{i}',Q(1),tuple((x,bits[i*n+x]) for x in range(n))) for i in (0,1))
            p=Problem(n,es,reps);h=(n-1).bit_length()
            expected=compile_frontier(p,range(n),h)
            a,ar=compile_streaming(p,h)
            b,br=compile_streaming(p,h,RULE)
            c,cr=compile_streaming(p,h,RULE,engine='lowered')
            check(points(a)==points(expected));check(points(b)==points(expected));check(points(c)==points(expected))
            check([w.tree for w in a]==[w.tree for w in b]==[w.tree for w in c])
            check(br['table_reads']==cr['table_reads']<=ar['table_reads'])
            check(ar['table_reads']-br['table_reads']==br['counters'].get('model_rows_skipped',0))
            for w in c:check(check_tree(p,range(n),w.tree,h)==(w.work,w.storage))

@group('lowering preserves the pure formula under its loop invariant',
       'Every prior prefix with counts 0..c at capacities 1..32, each possible next binary report.')
def lowering():
    for cap in range(1,33):
        for a in range(cap+1):
            for b in range(cap+1):
                if a+b>=2*cap:continue
                for report in (0,1):
                    sides=[a,b];sides[report]+=1
                    context={'a':sides[0],'b':sides[1],'m':2*cap,'c':cap}
                    check(evaluate(RULE,context)==(sides[report]>cap))
    # Without the prior-prefix invariant, the one-counter lowering can be wrong.
    context={'a':3,'b':1,'m':4,'c':2}
    check(evaluate(RULE,context) and not (context['b']>context['c']))

@group('literal repair-cover obstruction under immutable experiments',
       'n=1..3, every nonempty family of one or two nonempty repair-success sets; every binary query; horizons 0,1,2.')
def covers():
    for n in range(1,4):
        subsets=[frozenset(i for i in range(n) if mask&(1<<i)) for mask in range(1,1<<n)]
        families=[x for k in (1,2) for x in combinations(subsets,k)]
        for family in families:
            reps=tuple(Repair(f'r{i}',Q(1),x) for i,x in enumerate(family))
            for bits in product((0,1),repeat=n):
                p=Problem(n,(Experiment('e',Q(1),tuple((x,bits[x]) for x in range(n))),),reps)
                cover=cover_number(p,range(n))
                for h in (0,1,2):
                    front=compile_frontier(p,range(n),h)
                    if cover is None or cover>2**h:check(not front)
                    for w in front:
                        check(cover is not None and cover<=2**h)
                        check(w.storage>=2*cover-1)
    # Four cases, a universal repair: cardinality is not the right leaf demand.
    base=cell_problem(4)
    broad=Problem(4,base.experiments,(Repair('all',Q(1),frozenset(range(4))),))
    check(cover_number(broad,range(4))==1)
    front,r=compile_streaming(broad,0,RULE)
    check(points(front)=={(Q(1),1)} and r['mode']=='fallback')

@group('reject unsupported scope and preserve general fallback',
       'Every entry of n=4,q=6 changed separately to partial, destructive, or nonbinary; bad costs and nonsingleton repairs.')
def scope():
    p0=cell_problem(4)
    for ei,e in enumerate(p0.experiments):
        for x in range(4):
            for item in (None,((x+1)%4,0),(x,2)):
                es=list(p0.experiments);rows=list(e.transitions);rows[x]=item
                es[ei]=Experiment(e.name,e.cost,tuple(rows));p=Problem(4,tuple(es),p0.repairs)
                fs,r=compile_streaming(p,2,RULE,engine='lowered')
                check(r['mode']=='fallback');check(points(fs)==points(compile_frontier(p,range(4),2)))
    for cost in (Q(0),Q(2)):
        es=list(p0.experiments);e=es[0];es[0]=Experiment(e.name,cost,e.transitions)
        p=Problem(4,tuple(es),p0.repairs)
        fs,r=compile_streaming(p,2,RULE);check(r['mode']=='fallback')
        check(points(fs)==points(compile_frontier(p,range(4),2)))

@group('capacity feasibility is not actual query-library solvability',
       'Four cases with one 2/2 split and singleton repairs; two- and three-step horizons; equality-only fallback.')
def capacity_not_sufficient():
    reps=cell_problem(4).repairs
    p=Problem(4,(Experiment('e',Q(1),tuple((x,x//2) for x in range(4))),),reps)
    for h in (2,3):
        front,r=compile_streaming(p,h,RULE)
        check(not front and r['status']=='complete')
        check(r['counters'].get('failed_feasible_roots',0)>0)
    eq=cell_problem(4,bits=False)
    front,r=compile_streaming(eq,3,RULE)
    check(r['mode']=='fallback');check(points(front)=={(Q(4),7)})

@group('finite agreement does not license an unbounded pruning formula',
       'Capped predicate on all 198 training contexts, then explicit c=8 counterexample; structural certificate gate.')
def extrapolation():
    for c in prefix_contexts():
        capped=max(c['a'],c['b'])>min(c['c'],4)
        check(capped==evaluate(RULE,c))
    c={'a':0,'b':5,'m':16,'c':8}
    check(max(c['a'],c['b'])>min(c['c'],4))
    check(not impossible_by_completions(c))
    unsupported=('>',('max',('a',),('b',)),('min',('c',),('1',)))
    check(rejected(lambda:certify_rule(unsupported)))
    check(rejected(lambda:certify_rule(('>=',('max',('a',),('b',)),('c',)))))
    check(certify_rule(('<',('c',),('max',('b',),('a',))))['theorem']=='prefix_capacity_v1')

@group('pure-data parser and untrusted-certificate negative controls',
       'Wrong types, executable names, duplicate operands, nested comparisons, invalid engine, empty/out-of-range supports.')
def parser_controls():
    for bad in (None,[],['exec','x'],['a'],['>', ['max',['a'],['a']],['c']],
                ['>', ['>', ['a'],['b']],['c']], ['>', ['a'],['unknown']]):
        check(rejected(lambda b=bad:certify_rule(b)))
    check(rejected(lambda:compile_streaming(cell_problem(4),2,RULE,engine='jit')))
    check(rejected(lambda:compile_streaming(cell_problem(4),2,RULE,support=[])))
    check(rejected(lambda:compile_streaming(cell_problem(4),-1,RULE)))
    front,r=compile_streaming(cell_problem(4),1,RULE)
    check(not front and r['mode']=='certified_horizon_obstruction')

@group('input-read caps do not become false infeasibility certificates',
       'Every cap 0..66 for the four-case model; compare exact same methods without caps.')
def budgets():
    p=cell_problem(4)
    for rule in (None,RULE):
        expected,report=compile_streaming(p,2,rule)
        for cap in range(67):
            front,r=compile_streaming(p,2,rule,read_limit=cap)
            check(r['table_reads']<=cap)
            if cap<report['table_reads']:
                check(r['status']=='incomplete' and r['mode']=='read_budget_exhausted')
            else:
                check(r['status']=='complete');check(points(front)==points(expected))

@group('fresh finite families, supplementary work, and saved-row identity',
       'Powers of two 2..64; both expression engines; read savings versus the same full-scan search, not processor speed.')
def costs():
    for k in range(1,7):
        p=cell_problem(2**k)
        a,ar=compile_streaming(p,k)
        b,br=compile_streaming(p,k,RULE)
        c,cr=compile_streaming(p,k,RULE,engine='lowered')
        saved=ar['table_reads']-br['table_reads']
        check(saved==br['counters'].get('model_rows_skipped',0))
        check(br['table_reads']==cr['table_reads'])
        check(br['counters']['expression_node_visits']==5*cr['counters']['lowered_comparisons'])
        check(br['shared_input_validation_reads']==ar['shared_input_validation_reads']==(2**k)*(2**k+k))
        check(points(a)==points(b)==points(c)=={(Q(k+1),2*(2**k)-1)})
        if k==1:check(saved==0 and cr['counters']['lowered_comparisons']>0)

@group('state-label and report-label transport with altered input order',
       '32 affine permutations on eight states, eight report-flip patterns, reversed query order; 256 cold compilations.')
def transports():
    base=cell_problem(8)
    for a in (1,3,5,7):
        for b in range(8):
            sigma=tuple((a*x+b)%8 for x in range(8))
            for mask in range(8):
                pp=relabel_problem(base,sigma,tuple((mask>>(i%3))&1 for i in range(11)))
                pp=Problem(8,tuple(reversed(pp.experiments)),pp.repairs)
                fs,r=compile_streaming(pp,3,RULE,engine='lowered')
                old,orr=compile_streaming(pp,3)
                check(points(fs)=={(Q(4),15)})
                check([w.tree for w in fs]==[w.tree for w in old])
                check(r['table_reads']<=orr['table_reads'])

@group('nonpower supports, downstream failures, and witness integrity',
       'Every nonempty subset of the eight-case model, h=ceil(log2 support); corrupt each field in a returned four-case witness.')
def subsets_and_witnesses():
    p=cell_problem(8)
    for mask in range(1,256):
        states=tuple(x for x in range(8) if mask&(1<<x));h=(len(states)-1).bit_length()
        a,ar=compile_streaming(p,h,support=states)
        b,br=compile_streaming(p,h,RULE,support=states,engine='lowered')
        check([w.tree for w in a]==[w.tree for w in b])
        check(ar['table_reads']>=br['table_reads'])
        for w in b:check(check_tree(p,states,w.tree,h)==(w.work,w.storage))
    p=cell_problem(4);fs,r=compile_streaming(p,2,RULE)
    obj=tree_to_dict(fs[0].tree)
    bad=dict(obj);bad['index']=100
    check(rejected(lambda:check_tree(p,range(4),tree_from_dict(bad),2)))
    bad=dict(obj);bad['children']=bad['children'][:1]
    check(rejected(lambda:check_tree(p,range(4),tree_from_dict(bad),2)))
    check(rejected(lambda:check_tree(p,range(4),fs[0].tree,1)))
    check(rejected(lambda:check_tree(p,range(4),fs[0].tree,2,allowance=(Q(2),7))))

if __name__=='__main__':
    result={'status':'PASS','group_count':len(GROUPS),'assertions':COUNT,
            'arithmetic':'exact integers, finite sets, and fractions.Fraction',
            'groups':GROUPS,
            'non_claim':'Bounded project-authored implementation cross-checks, not a universal proof or independent neural experiment.'}
    out=ROOT/'validation/synthesis_checks.json';out.parent.mkdir(exist_ok=True,parents=True)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(f'PASS: {len(GROUPS)} groups and {COUNT:,} exact assertions.')
