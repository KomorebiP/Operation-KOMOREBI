#!/usr/bin/env python3
"""Frozen proof-checked search compression and changed-repair demonstrations."""
from __future__ import annotations
from pathlib import Path
from collections import Counter
from itertools import product
from fractions import Fraction as Q
import hashlib,json
from meta_synthesis import *
from synthesized_pruning import prefix_contexts,impossible_by_completions,synthesize
from weighted_repair_pruning import *
from repair_calculus import tree_to_dict

ROOT=Path(__file__).resolve().parents[1]

def tasks():
    a,b,c,m=((v,) for v in ('a','b','c','m'))
    return (
        ('sum_budget',('>',('+',a,b),c)),
        ('minimum_trigger',('<',('min',a,b),c)),
        ('maximum_deadline',('>=',('max',a,b),m)),
        ('exact_sum',('==',('+',a,b),c)),
        ('exact_maximum',('==',('max',a,b),c)),
        ('cross_budget',('<=',('+',a,c),b)),
        ('minimum_quota',('>=',('min',a,c),b)),
        ('sum_capacity',('>',('+',a,b),m)),
        ('overlap_equality',('==',('min',a,b),c)),
    )

def main():
    out=ROOT/'validation';out.mkdir(exist_ok=True)
    ps=grammar()
    lib,learn=discover_library()
    (out/'learned_equations.json').write_text(json.dumps(lib,indent=2)+'\n')
    indices,quot=ordered_quotient(ps,lib)
    # Write the frozen candidate-space representation BEFORE any task target is used.
    frozen={k:v for k,v in quot.items() if k!='normal_forms'}
    (out/'synthesis_quotient.json').write_text(json.dumps(frozen,indent=2)+'\n')
    digest=hashlib.sha256((out/'synthesis_quotient.json').read_bytes()).hexdigest()
    eager,er=eager_quotient(ps)
    results=[]
    contexts=tuple(dict(zip(('a','b','m','c'),z)) for z in product((0,1,3,5),repeat=4))
    for name,target in tasks():
        labels_count=Counter();labels=tuple(value(target,c,labels_count) for c in contexts)
        parent=cegis(ps,contexts,labels);child=cegis(ps,contexts,labels,indices);strong=cegis(ps,contexts,labels,eager)
        if parent['winner']!=child['winner'] or parent['trace']!=child['trace']:
            raise AssertionError('Ordered quotient changed its CEGIS transcript.')
        results.append({'task':name,'target':target,'context_count':len(contexts),
                        'shared_target_label_nodes':dict(labels_count),'parent':parent,'child':child,'full_prover':strong})
    # A grammar-exhaustion case is also informative. Parity is not admitted syntax.
    paritycontexts=tuple(dict(zip(('a','b','m','c'),z)) for z in product(range(4),repeat=4))
    labels=tuple(c['a']%2==0 for c in paritycontexts)
    parent=cegis(ps,paritycontexts,labels);child=cegis(ps,paritycontexts,labels,indices)
    if parent['status']!='grammar_exhausted' or child['status']!='grammar_exhausted':raise AssertionError('Parity control became expressible.')
    if parent['winner']!=child['winner'] or parent['trace']!=child['trace']:raise AssertionError('Exhaustion changed.')
    results.append({'task':'parity_outside_grammar','context_count':len(contexts),'parent':parent,'child':child})
    # Cold re-acquisition of the original capacity rule, not insertion of its answer.
    oldcontexts=prefix_contexts();oldlabels=tuple(impossible_by_completions(c) for c in oldcontexts)
    oldparent=cegis(ps,oldcontexts,oldlabels);oldchild=cegis(ps,oldcontexts,oldlabels,indices)
    winner,prior=synthesize()
    if oldparent['winner']!=winner or oldchild['winner']!=winner:raise AssertionError('Original learned rule changed.')
    for f in ('trace','examples','winner_index'):assert oldparent[f]==oldchild[f]
    # Negative control: contexts with all positive inputs make a false equation look true.
    false_a=('max',('x',),('1',));false_b=('x',)
    false_proposed=all(value(false_a,{'x':x})==value(false_b,{'x':x}) for x in (1,2,3))
    try:equation_certificate(false_a,false_b);false_rejected=False
    except ValueError:false_rejected=True
    # Honest comparator: a fully supplied prover can directly normalize the grammar.
    totals={side:sum(row[side]['counters']['semantic_node_visits'] for row in results)
            for side in ('parent','child')}
    quotientnode=quot['counters']['normalizer_node_visits'];match=quot['counters']['schema_match_attempts']
    report={'status':'PASS','library_frozen_before_targets':True,'frozen_quotient_sha256':digest,
      'library_learning':learn,'quotient':frozen,'eager_full_prover_comparator':er,
      'capacity_rule_reacquisition':{'parent':oldparent,'child':oldchild,'same_as_v03_rule':True},
      'new_task_cases':results,'batch_semantic_node_visits':totals,
      'sample_only_equivalence_control':{'proposed':false_proposed,'rejected':false_rejected,
          'x0_values':[value(false_a,{'x':0}),value(false_b,{'x':0})]},
      'accounting':{'library_schema_count':learn['schema_terms'],'frozen_library_bytes':learn['library_bytes'],
          'new_target_labels_not_used_in_library_learning':True,
          'quotient_normalizer_visits':quotientnode,'quotient_match_attempts':match,
          'full_prover_constructor_is_supplied':True,
          'note':'All event types are separately reported. Program generation, proof search, hashing, matching, and target-label construction are not hidden inside per-task interpreter counts. No total CPU speedup is claimed.'},
      'boundary':'The learner learns a task-independent search representation with a fixed primitive language and proof procedure. It does not learn new arithmetic semantics or revise the library learner itself.'}
    (out/'meta_synthesis_demonstration.json').write_text(json.dumps(report,indent=2)+'\n')
    repairrows=[]
    for groups in (2,4,8,16):
        p=paired_repair_problem(groups);w,wr=checked_greedy_weights(p);h=(groups-1).bit_length()
        a,ar=ordered_weighted_search(p,h,w,False);b,br=ordered_weighted_search(p,h,w,True)
        if a!=b:raise AssertionError('Weighted streaming changed the controller.')
        repairrows.append({'hidden_states':p.n,'repair_groups':groups,'weight_construction':wr,
                          'full_scan':ar,'streaming':br,'same_literal_tree':True})
    # A stale certificate must be rejected after a universal repair is admitted.
    p=paired_repair_problem(4);w,_=checked_greedy_weights(p)
    broad=Problem(p.n,p.experiments,p.repairs+(Repair('universal',Q(1),frozenset(range(p.n))),))
    try:verify_weights(broad,w);stale=False
    except ValueError:stale=True
    fresh,fr=checked_greedy_weights(broad);tree,tr=ordered_weighted_search(broad,0,fresh)
    weighted={'status':'PASS','cases':repairrows,'stale_weight_certificate_rejected':stale,
              'new_weights':list(map(str,fresh)),'universal_repair':tr,'universal_tree':tree_to_dict(tree)}
    (out/'weighted_repair_demonstration.json').write_text(json.dumps(weighted,indent=2)+'\n')
    print('PASS: frozen search quotient, fresh target synthesis, and repair-relative certificate demonstrations.')
    print('grammar',len(ps),'->',len(indices),'eager',len(eager))
    print('batch evaluator node visits',totals)
    for row in results:
        print(row['task'],row['parent']['counters']['semantic_node_visits'],row['child']['counters']['semantic_node_visits'],row['parent']['status'])

if __name__=='__main__':main()
