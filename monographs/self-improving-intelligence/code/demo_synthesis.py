#!/usr/bin/env python3
"""Freeze the generated compiler rule before evaluating larger finite families."""
from pathlib import Path
from fractions import Fraction as Q
from dataclasses import replace
import hashlib, json
from synthesized_pruning import synthesize, compile_streaming, certify_rule
from repair_calculus import (Problem, Experiment, Repair, cell_problem, check_tree,
                             tree_to_dict, relabel_problem)
from compiler_improvement import compile_measured

ROOT=Path(__file__).resolve().parents[1]

def dump(name,obj):
    p=ROOT/'validation'/name;p.parent.mkdir(exist_ok=True,parents=True)
    p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n');return p

def main():
    rule,learning=synthesize()
    frozen=dump('synthesized_rule.json',learning)
    initial_hash=hashlib.sha256(frozen.read_bytes()).hexdigest()
    # No result from these evaluations is fed to synthesize or rule certification.
    rows=[]
    for n in (2,4,8,16,32,64):
        p=cell_problem(n);h=n.bit_length()-1
        base,rb=compile_streaming(p,h)
        interpreted,ri=compile_streaming(p,h,rule)
        lowered,rl=compile_streaming(p,h,rule,engine='lowered')
        previous,rp=compile_measured(p,h,'balanced')
        assert [(w.work,w.storage,w.tree) for w in base]==[(w.work,w.storage,w.tree) for w in lowered]
        assert [w.tree for w in interpreted]==[w.tree for w in lowered]
        assert [(w.work,w.storage) for w in previous]==[(w.work,w.storage) for w in base]
        saved=rb['table_reads']-rl['table_reads']
        rows.append({'cases':n,'full_scan':rb,'interpreted':ri,'lowered':rl,
                     'previous_balanced_wrapper':rp,'saved_model_reads':saved,
                     'read_price_threshold_interpreted':None if not saved else str(Q(ri['counters']['expression_node_visits'],saved)),
                     'read_price_threshold_lowered':None if not saved else str(Q(rl['counters']['lowered_comparisons'],saved))})
        if n==16:
            dump('synthesized_controller_16.json',tree_to_dict(lowered[0].tree))
    # Negative control: saving reads does not mean saving every resource.
    p=cell_problem(2)
    tiny={'full_scan':compile_streaming(p,1)[1],
          'learned':compile_streaming(p,1,rule,engine='lowered')[1]}
    # Outside singleton scope, the generic parent computes a zero-query repair.
    p0=cell_problem(4); broad=Problem(4,p0.experiments,(Repair('repair_all',Q(1),frozenset(range(4))),))
    bf,br=compile_streaming(broad,2,rule,engine='lowered')
    assert br['mode']=='fallback' and [(w.work,w.storage) for w in bf]==[(Q(1),1)]
    # Capacity is not sufficient for actual downstream separation.
    trap=Problem(4,(Experiment('only_split',Q(1),tuple((x,x//2) for x in range(4))),),p0.repairs)
    tf,tr=compile_streaming(trap,2,rule)
    assert not tf and tr['status']=='complete'
    equality=cell_problem(4,bits=False)
    ef,er=compile_streaming(equality,3,rule,engine='lowered')
    assert er['mode']=='fallback'
    # Fresh query/report/state orders: task is new, formula does not change.
    relabels=[]
    for multiplier,shift in ((1,1),(3,2),(5,3),(7,4)):
        n=8;sigma=tuple((multiplier*x+shift)%n for x in range(n))
        pp=relabel_problem(cell_problem(n),sigma,tuple(i%2 for i in range(n+3)))
        pp=Problem(n,tuple(reversed(pp.experiments)),pp.repairs)
        f,r=compile_streaming(pp,3,rule,engine='lowered')
        assert [(w.work,w.storage) for w in f]==[(Q(4),15)]
        relabels.append({'affine_state_map':[multiplier,shift],'report':r})
    # Capacity-only sample agreement is not the certificate theorem.
    alias={'a':0,'b':5,'m':16,'c':8}
    evidence={'context':alias,'good_rule_rejects':False,'capped_rule_rejects':True,
              'safe_completion_final_counts':[8,8],
              'capped_rule':'max(a,b) > min(c,4)',
              'note':'Agrees with the learned rule for every training context c<=4, but the structural certificate rejects it.'}
    assert hashlib.sha256(frozen.read_bytes()).hexdigest()==initial_hash
    out={'status':'PASS','frozen_rule_sha256':initial_hash,'learning':learning,
         'evaluations':rows,'two_case_resource_tradeoff':tiny,
         'changed_repair_language':br,'local_capacity_not_sufficient':tr,
         'equality_only_fallback':er,'fresh_relabelings':relabels,
         'finite_agreement_without_general_scope':evidence,
         'comparison':'Primary effect isolates prefix pruning in the same ordered compiler. The prior balanced wrapper is a separate comparator.',
         'limitations':['Exact finite analytical models, not statistical holdout evidence or neural-agent trials.',
                        'The compiler sketch, primitive grammar, feature registry, teacher, and universal proof remain supplied.',
                        'Model tables are supplied; input validation, scope guard, and witness checking are included or separately charged.',
                        'Lowered predicate work counts comparisons; not a processor-time model.']}
    dump('synthesis_demonstration.json',out)
    print('Learned',learning['expression_text'],'after',learning['counterexamples'],'counterexamples')
    print('cases full-scan streaming savings lowered comparisons')
    for row in rows:
        print(row['cases'],row['full_scan']['table_reads'],row['lowered']['table_reads'],
              row['saved_model_reads'],row['lowered']['counters'].get('lowered_comparisons',0))
    print('Frozen rule',initial_hash)

if __name__=='__main__':main()
