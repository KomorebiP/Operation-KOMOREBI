#!/usr/bin/env python3
"""Regenerate the fixed-family compiler revision and its cold-start comparisons."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib,json,time
from compiler_improvement import compile_measured, tagged_problem, orientation_family, evidence_step
from repair_calculus import cell_problem, relabel_problem, Problem, tree_to_dict, check_tree
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'validation'
OUT.mkdir(exist_ok=True)

def evaluate(n,rule,**kwargs):
    start=time.perf_counter()
    f,r=compile_measured(cell_problem(n),n.bit_length()-1,rule,**kwargs)
    r['wall_seconds']=time.perf_counter()-start
    return f,r

rules=(None,'first','balanced')
# Only these fixed development tasks can affect the selected policy record.
development=[]
for rule in rules:
    cases=[{'n':n,**evaluate(n,rule)[1]} for n in (4,8)]
    development.append({'proposal_rule':rule,'cases':cases,'total_reads':sum(x['table_reads'] for x in cases)})
chosen=min(development,key=lambda r:r['total_reads'])['proposal_rule']
policy={'schema':'komorebi-discovery-policy-1','proposal_rule':chosen,
        'preconditions':'Checked immutable binary unit-cost experiments and singleton successful repairs.',
        'early_return':'Independent valid tree meets both proved global lower bounds.',
        'fallback':'Unchanged exact predecessor compile_frontier.',
        'development_sizes':[4,8],'candidate_rules':[None,'first','balanced'],
        'selection_unit':'Sum of transition/report record reads, including guard and verification.',
        'learned_component':'Selection among two supplied proposal rules plus the unchanged baseline.',
        'not_learned':['The program templates','The lower-bound proof','The checker','The experiment table','The selector itself']}
serialized=json.dumps(policy,indent=2,sort_keys=True)+'\n'
(OUT/'discovery_policy.json').write_text(serialized)
frozen_hash=hashlib.sha256(serialized.encode()).hexdigest()

# Evaluation starts only after the policy bytes above are fixed.
heldout=[]
for name,p,support in [('larger_cube_16',cell_problem(16),None),
                       ('six_case_support',cell_problem(8),range(6)),
                       ('no_singleton_queries',Problem(16,cell_problem(16).experiments[16:],cell_problem(16).repairs),None),
                       ('equality_only_control',cell_problem(4,bits=False),None)]:
    h=3 if name=='equality_only_control' else ((len(tuple(support)) if support is not None else p.n)-1).bit_length()
    comparison={}
    for rule,label in ((None,'parent'),(chosen,'descendant')):
        t=time.perf_counter();f,r=compile_measured(p,h,rule,support=support)
        r['wall_seconds']=time.perf_counter()-t
        comparison[label]=r
    assert comparison['parent']['frontier']==comparison['descendant']['frontier']
    heldout.append({'case':name,'n':p.n,'horizon':h,**comparison})

rows=[]
for n in (2,4,8,16):
    _,a=evaluate(n,None);f,b=evaluate(n,chosen)
    rows.append({'n':n,'parent':a,'descendant':b})
    if n==16:
        (OUT/'descendant_tree_16.json').write_text(json.dumps(tree_to_dict(f[0].tree),indent=2)+'\n')

budgets={label:compile_measured(cell_problem(16),4,rule,read_limit=2000)[1]
         for rule,label in ((None,'parent'),(chosen,'descendant'))}
uncertainty=[]
for cal in (False,True):
    p=tagged_problem(orientation_family(cal));f,r=compile_measured(p,2,'balanced')
    uncertainty.append({'reference_available':cal,**r})
    if f:(OUT/'calibration_tree.json').write_text(json.dumps(tree_to_dict(f[0].tree),indent=2)+'\n')

# A fixed illustrative score sequence, not sampled performance data.
yseq=(1,1,-1,1,1,1,-1,1,1,1)
capital=Q(1);trajectory=[]
for y in yseq:
    capital=evidence_step(capital,Q(y),Q(1,2))
    trajectory.append(str(capital))

report={'policy_sha256':frozen_hash,'policy':policy,'development':development,
        'heldout_structural_cases':heldout,'comparison_rows':rows,
        'common_read_allowance_2000':budgets,'uncertain_sensor_model':uncertainty,
        'illustrative_evidence':{'scores':yseq,'predictable_bet':'1/2','gamma':'0','capital':trajectory},
        'source_bytes':{str(p.relative_to(ROOT)):p.stat().st_size for p in [ROOT/'code'/'compiler_improvement.py',ROOT/'code'/'repair_calculus.py']},
        'limitations':['A finite selection of supplied compiler templates, not invention of the templates.',
          'A faster compiler on a family, not improved selection of compiler templates on a second recursive generation.',
          'The same table is supplied to both methods. Cold caches and complete witness checking are used.',
          'The lookup budget does not charge all Python operations, source storage, or model acquisition.',
          'No statistical generalization claim is inferred from deterministic named cases.',
          'The equality-only control shows positive fallback overhead.']}
assert hashlib.sha256((OUT/'discovery_policy.json').read_bytes()).hexdigest()==frozen_hash
(OUT/'discovery_demonstration.json').write_text(json.dumps(report,indent=2)+'\n')
print('Selected rule:',chosen)
for row in rows:print(row['n'],row['parent']['table_reads'],row['descendant']['table_reads'],row['descendant']['frontier'])
print('Unknown orientation:',[x['frontier'] for x in uncertainty])
print('Frozen policy SHA256:',frozen_hash)
