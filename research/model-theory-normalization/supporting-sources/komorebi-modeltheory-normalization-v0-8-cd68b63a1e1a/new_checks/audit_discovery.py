#!/usr/bin/env python3
"""Independent finite audits and trace/export regressions. Finite tests do not
establish the universal loop theorem: the Lean proof does that separately.
"""
from __future__ import annotations
from pathlib import Path
import sys,json,time,copy,itertools,re,ast
from collections import deque,Counter
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from discovery_trace import traced_discover
from new_checks.check_trace import check_trace,test_row,canonical
from new_checks.export_queue_lean import export
ROOT=Path(__file__).resolve().parents[1]


def brute(source, fuel=None):
    m=source['p']**source['r'];d=source['dimension'];k=len(source['actions']);o=len(source['observations'])
    if fuel is None:fuel=o+k*source['r']*d+1
    todo=deque({'word':[],'observation':j} for j in range(o));ts=[];rows=[];exams=0
    while fuel:
        fuel-=1
        if not todo:return ts,exams
        t=todo.popleft();v=test_row(source,t);exams+=1
        member=any([sum(c[i]*rows[i][j] for i in range(len(rows)))%m for j in range(d)]==v
                   for c in itertools.product(range(m),repeat=len(rows)))
        if not member:
            ts.append(t);rows.append(v)
            for a in range(k):todo.append({'word':[a]+t['word'],'observation':t['observation']})
    return None,exams


def fixture(p,r,d,A,O):
    return {'schema':'finite-linear-profile-v1','p':p,'r':r,'dimension':d,'actions':A,
            'observations':O,'initial_interface':'all_states','word_order':'left_to_right'}


def literal_vector(text,name):
    line=next(x for x in text.splitlines() if x.startswith('def '+name+' :'))
    return ast.literal_eval(line.split(':=',1)[1].strip().replace('![','['))


def run():
    counts=Counter();start=time.monotonic();summaries=[]
    def ck(name,ok):
        if not ok:raise AssertionError(name)
        counts[name]+=1
    for src in sorted((ROOT/'certificates').glob('*.source.json')):
        s=json.loads(src.read_text());tr=traced_discover(s);z=check_trace(s,tr)
        saved=json.loads((ROOT/'queue_traces'/src.name.replace('.source.json','.trace.json')).read_text())
        old=json.loads(src.with_name(src.name.replace('.source.json','.certificate.json')).read_text())
        ck('deterministic_trace_regeneration',tr==saved)
        ck('independent_complete_trace',True)
        ck('frozen_test_list_preserved',tr['result']==old['raw_tests'])
        ck('accepted_bound',z['accepted']<=s['r']*s['dimension'])
        ck('queue_accounting',z['candidates']==len(s['observations'])+len(s['actions'])*z['accepted'])
        counts['skip_witnesses']+=z['skipped'];counts['accept_witnesses']+=z['accepted']
        summaries.append({'source':src.name,**z})
    # Exhaustive 64 binary two-coordinate/one-action systems and all 29 scalar
    # one-action systems for moduli 2,3,4. No random sampling in this audit.
    small=[]
    for a in itertools.product(range(2),repeat=4):
        for o in itertools.product(range(2),repeat=2):
            small.append(fixture(2,1,2,[[list(a[:2]),list(a[2:])]], [list(o)]))
    for p,r in [(2,1),(3,1),(2,2)]:
        m=p**r
        for a,o in itertools.product(range(m),repeat=2):small.append(fixture(p,r,1,[[[a]]],[[o]]))
    for s in small:
        ts,exam=brute(s);tr=traced_discover(s)
        ck('exhaustive_coefficient_oracle_agreement',ts==tr['result'])
        ck('exhaustive_candidate_agreement',exam==len(tr['events']))
        rows=[test_row(s,t) for t in ts];m=s['p']**s['r'];d=s['dimension']
        span={tuple(sum(c[i]*rows[i][j] for i in range(len(rows)))%m for j in range(d))
              for c in itertools.product(range(m),repeat=len(rows))}
        ck('exhaustive_final_observations',all(tuple(o) in span for o in s['observations']))
        for v in span:
            for A in s['actions']:
                ck('exhaustive_final_span_invariant',tuple(sum(v[h]*A[h][j] for h in range(d))%m for j in range(d)) in span)
    boundaries=[fixture(2,2,0,[[ ]],[[]]),fixture(2,0,1,[[[0]]],[[0]]),
                fixture(2,2,2,[],[[2,0],[2,0],[0,2]]),fixture(2,2,2,[[[1,0],[0,1]]],[])]
    for s in boundaries:
        ts,_=brute(s)
        ck('reference_degenerate_boundary',ts==([{'word':[],'observation':0},{'word':[],'observation':2}] if not s['actions'] else []))
    sh=fixture(2,2,3,[[[1,1,0],[0,1,0],[0,0,1]]],[[1,0,0]])
    ck('insufficient_fuel_unresolved',brute(sh,1)[0] is None)
    # Typed, deterministic Lean exports and independent source literal checks.
    exports=[('scrambled_128bit','LargeQueue','DiscoveryLargeTrace'),('delay_chain','DelayQueue','DiscoveryDelayTrace'),
             ('hidden_p2_r2_d4','TorsionQueue','DiscoveryTorsionTrace'),('precision_one','ZeroQueue','DiscoveryZeroTrace')]
    for name,ns,mod in exports:
        s=json.loads((ROOT/'certificates'/(name+'.source.json')).read_text());t=json.loads((ROOT/'queue_traces'/(name+'.trace.json')).read_text())
        text=(ROOT/'formalization'/(mod+'.lean')).read_text()
        ck('lean_export_regeneration',text==export(s,t,ns))
        ck('lean_literal_source_actions',literal_vector(text,'A')==s['actions'])
        ck('lean_literal_source_observations',literal_vector(text,'O')==s['observations'])
        ck('lean_literal_modulus',f'abbrev R := ZMod {s["p"]**s["r"]}' in text)
        ck('lean_trace_branches',len(re.findall(r'^theorem branch',text,re.M))==len(t['events']))
    s=json.loads((ROOT/'certificates/scrambled_128bit.source.json').read_text())
    t=json.loads((ROOT/'queue_traces/scrambled_128bit.trace.json').read_text())
    mutations=[]
    def mut(f):
        x=copy.deepcopy(t);f(x);mutations.append((s,x))
    mut(lambda x:x['events'].pop())
    mut(lambda x:x['events'].pop(0))
    mut(lambda x:x['events'][0].update(delta=[0]*8))
    mut(lambda x:x['events'][2]['coefficients'].__setitem__(0,4))
    mut(lambda x:x['events'][-1]['test']['word'].reverse())
    mut(lambda x:x['result'].reverse())
    mut(lambda x:x['events'].append(copy.deepcopy(x['events'][-1])))
    mut(lambda x:x.update(status='unresolved'))
    mut(lambda x:x.update(source_sha256='0'*64))
    changed=copy.deepcopy(s);changed['observations'][0][0]=(changed['observations'][0][0]+1)%65536
    reb=copy.deepcopy(t);from hashlib import sha256
    reb['source_sha256']=sha256(canonical(changed)).hexdigest();mutations.append((changed,reb))
    for ss,tt in mutations:
        try:check_trace(ss,tt)
        except (ValueError,AssertionError):ck('corrupt_trace_rejected',True)
        else:raise AssertionError('bad trace accepted')
    try:traced_discover(s,candidate_cap=1)
    except RuntimeError:ck('resource_cap_unresolved',True)
    else:raise AssertionError('premature queue cap accepted')
    ck('checker_implementation_independence',not re.search(r'^(?:from|import) (?:discover|chainring|discovery_trace)',(ROOT/'new_checks/check_trace.py').read_text(),re.M))
    result={'status':'PASS','counts':dict(counts),'profiles':len(summaries),'finite_exhaustive_profiles':len(small),
      'large':next(z for z in summaries if z['source']=='scrambled_128bit.source.json'),
      'bounds':{'frozen_profiles':202,'finite_exhaustive_families':'all 64 binary dimension-two single-action/single-observation and all 29 scalar systems for moduli 2,3,4',
                'negative_traces':len(mutations),'literal_lean_exports':len(exports)},
      'seconds':time.monotonic()-start,'nonclaims':['Fast Python Smith implementation is not verified.','Not a fresh structural-holdout benchmark.','Reference oracle enumerates coefficient tuples, potentially exponentially expensive.']}
    (ROOT/'results/DISCOVERY_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2));return result
if __name__=='__main__':run()
