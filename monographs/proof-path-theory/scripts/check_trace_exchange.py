"""Generate exact finite conformance cases for Python and the Lean JSON consumer.

Declared domains: all 3-node forward DAG rule fields exported by the named
package, all 2-node rule subsets including cycles, selected corruptions, and
malformed wire syntax. Comparison uses independently enumerated finite models.
No empirical learning or unbounded implementation proof is claimed.
"""
from __future__ import annotations
from dataclasses import replace
from itertools import product
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from proof_path_theory import (ClaimNode, Justification, NodeKind, ProofField,
    ProofFieldViews, solve_extension, verify_extension_result, load_proof_field)
from proof_path_theory.trace_codec import (
    IndexedProblem, IndexedRule, IndexedWitness, IndexedCertificate,
    PROBLEM_TAG, CERTIFICATE_TAG, canonical_bytes, problem_to_value,
    certificate_to_value, check_indexed_certificate, index_problem, index_certificate,
    export_trace_exchange, loads_problem, loads_trace_certificate,
)


def powerset(n):
    return [frozenset(i for i in range(n) if bits>>i&1) for bits in range(1<<n)]


def models(p, *, observations=False):
    return [s for s in powerset(p.node_count)
        if set(p.leaves)<=s and (not observations or set(p.positive)<=s)
        and all(not set(r.premises)<=s or r.conclusion in s for r in p.rules)]


def reference_accept(p,c):
    # This oracle uses set execution and independent model intersection, rather
    # than the list evaluator or checkClosure from either production checker.
    def trace(ids):
        s=set(p.leaves)|set(p.positive)
        for i in ids:
            if type(i) is not int or not 0<=i<len(p.rules):return None
            r=p.rules[i]
            if not set(r.premises)<=s:return None
            s.add(r.conclusion)
        return s
    state=set(p.leaves)|set(p.positive)
    for i in c.trace:
        if type(i) is not int or not 0<=i<len(p.rules):return False
        r=p.rules[i]
        if not set(r.premises)<=state or r.conclusion in state:return False
        state.add(r.conclusion)
    least=frozenset.intersection(*models(p,observations=True))
    if set(c.closure)!=least or state!=least or len(set(c.closure))!=len(c.closure):return False
    if c.feasible:return c.obstruction is None and not least.intersection(p.negative)
    w=c.obstruction
    if w is None or w.target not in p.negative:return False
    end=trace(w.trace)
    return end is not None and w.target in end


def simple_certificate(p):
    state=set(p.leaves)|set(p.positive); tr=[]
    while True:
        before=len(state)
        for i,r in enumerate(p.rules):
            if set(r.premises)<=state and r.conclusion not in state:
                state.add(r.conclusion); tr.append(i)
        if len(state)==before:break
    bad=sorted(state.intersection(p.negative))
    return IndexedCertificate(not bad,tuple(sorted(state)),tuple(tr),
        None if not bad else IndexedWitness(bad[0],tuple(tr)))


def lean_list(xs):return '['+', '.join(map(str,xs))+']'
def lean_problem(p):
    rs='['+', '.join('⟨'+lean_list(r.premises)+', '+str(r.conclusion)+'⟩' for r in p.rules)+']'
    return '⟨'+', '.join([str(p.node_count),lean_list(p.leaves),rs,lean_list(p.positive),lean_list(p.negative)])+'⟩'
def lean_certificate(c):
    w='none' if c.obstruction is None else 'some ⟨'+str(c.obstruction.target)+', '+lean_list(c.obstruction.trace)+'⟩'
    return '⟨'+', '.join(['true' if c.feasible else 'false',lean_list(c.closure),lean_list(c.trace),w])+'⟩'


def generate_kernel_fixtures():
    out=ROOT/'examples/trace_exchange';out.mkdir(parents=True,exist_ok=True)
    cases=[]
    for name,field_file,negative in [
        ('andPositive','and_dag.json',()),('andNegative','and_dag.json',('B',)),
        ('alternativePositive','alternative_proofs.json',()),
        ('alternativeNegative','alternative_proofs.json',('B',)),
    ]:
        views=ProofFieldViews(load_proof_field(ROOT/'examples'/field_file))
        result=solve_extension(views,negative=negative)
        binding,pj,cj=export_trace_exchange(views,result,negative=negative)
        p,c=loads_problem(pj),loads_trace_certificate(cj)
        (out/(name+'.problem.json')).write_bytes(pj+b'\n')
        (out/(name+'.certificate.json')).write_bytes(cj+b'\n')
        (out/(name+'.binding.json')).write_text(json.dumps({'source':field_file,
            'node_names':binding.node_names,'rule_names':binding.rule_names,
            'scope':'Executed address translation, not a universally verified source adapter.'},indent=2)+'\n')
        cases.append((name,p,c))
    p=IndexedProblem(2,(),(IndexedRule((0,),1),IndexedRule((1,),0)),(0,),(1,))
    cases.append(('seededCycle',p,simple_certificate(p)))
    p=IndexedProblem(0,(),(),(),())
    cases.append(('emptyProblem',p,simple_certificate(p)))
    text='''import ProofPath.TraceWire

/-! Generated concrete records. Acceptance is kernel-normalized with decide;
not inferred from Python's PASS flag. JSON text and address books remain in
examples/trace_exchange for independent input correspondence checks. -/
namespace ProofPath.Trace.Fixtures
open Wire

'''
    for name,p,c in cases:
        text+=f'def {name}Problem : Problem := {lean_problem(p)}\n'
        text+=f'def {name}Certificate : Certificate := {lean_certificate(c)}\n'
        text+=f'theorem {name}_accepted : accept {name}Problem {name}Certificate = true := by decide\n'
        text+=f'theorem {name}_checked : CertifiedAnswer {name}Problem {name}Certificate :=\n'
        text+=f'  acceptance_sound _ _ {name}_accepted\n\n'
    text+='end ProofPath.Trace.Fixtures\n'
    (ROOT/'formal/ProofPath/TraceFixtures.lean').write_text(text)
    return len(cases)


def main():
    data=ROOT/'data';data.mkdir(exist_ok=True)
    cases_path=data/'trace_exchange_cases.ndjson'; expected_path=data/'trace_exchange_expected.txt'
    counts={k:0 for k in ['named_rule_fields','named_protected_problems','cyclic_capable_fields',
        'cyclic_capable_problems','mutated_certificates','malformed_inputs','accepted_positive','accepted_negative','rejected']}
    def add(p,c,fh,eh):
        actual=check_indexed_certificate(p,c); expected=reference_accept(p,c)
        if actual!=expected:raise AssertionError((p,c,actual,expected))
        status=('ACCEPT_POSITIVE' if c.feasible else 'ACCEPT_NEGATIVE') if expected else 'REJECT'
        counts[{'ACCEPT_POSITIVE':'accepted_positive','ACCEPT_NEGATIVE':'accepted_negative','REJECT':'rejected'}[status]]+=1
        raw=canonical_bytes([problem_to_value(p),certificate_to_value(c)])
        fh.write(raw+b'\n');eh.write(status+'\n')
    with cases_path.open('wb') as fh, expected_path.open('w') as eh:
        names=('a','b','c')
        rule_spec=[(tuple(names[i] for i in range(j) if bits[i]),names[j])
                    for j in range(3) for bits in product((0,1),repeat=j)]
        subsets=[frozenset(names[i] for i in range(3) if mask>>i&1) for mask in range(8)]
        for rule_mask in range(1<<len(rule_spec)):
            chosen=[r for i,r in enumerate(rule_spec) if rule_mask>>i&1]
            rules=[Justification(f'r{i}',ps,co,'declared') for i,(ps,co) in enumerate(chosen)]
            for leaf in subsets:
                f=ProofField([ClaimNode(v,v,NodeKind.PREMISE if v in leaf else NodeKind.CLAIM) for v in names],rules,premises=leaf,targets=('c',))
                view=ProofFieldViews(f);counts['named_rule_fields']+=1
                for s in subsets:
                    for n in subsets:
                        result=solve_extension(view,positive=s,negative=n)
                        binding=index_problem(view,positive=s,negative=n)
                        cert=index_certificate(binding,result)
                        assert verify_extension_result(view,positive=s,negative=n,result=result)
                        p=binding.problem
                        add(p,cert,fh,eh);counts['named_protected_problems']+=1
                        if counts['named_protected_problems']%256==0:
                            variants=[replace(cert,trace=cert.trace+(len(p.rules),)),
                                replace(cert,trace=tuple(reversed(cert.trace))),
                                replace(cert,trace=cert.trace[:-1]),replace(cert,feasible=not cert.feasible),
                                replace(cert,closure=tuple(range(p.node_count))),
                                replace(cert,closure=()),replace(cert,obstruction=None),
                                replace(cert,obstruction=IndexedWitness(0,()))]
                            for bad in variants:
                                add(p,bad,fh,eh);counts['mutated_certificates']+=1
        # Here self-dependencies and cycles are included explicitly. This is the
        # indexed checker domain, not a change to the named DAG constructor.
        sets=powerset(2)
        all_rules=[IndexedRule(tuple(sorted(ps)),c) for ps in sets for c in range(2)]
        for mask in range(256):
            rules=tuple(r for i,r in enumerate(all_rules) if mask>>i&1)
            for leaves in sets:
                counts['cyclic_capable_fields']+=1
                for s in sets:
                    for n in sets:
                        p=IndexedProblem(2,tuple(sorted(leaves)),rules,tuple(sorted(s)),tuple(sorted(n)))
                        c=simple_certificate(p);add(p,c,fh,eh);counts['cyclic_capable_problems']+=1
        basep=[PROBLEM_TAG,1,[],[],[],[]]
        basec=[CERTIFICATE_TAG,True,[],[],None]
        malformed=[None,{},True,[],[basep], [basep,basec,None],
            [[PROBLEM_TAG,True,[],[],[],[]],basec],
            [[PROBLEM_TAG,-1,[],[],[],[]],basec],
            [[PROBLEM_TAG,1.0,[],[],[],[]],basec],
            [basep,[CERTIFICATE_TAG,'false',[],[],None]],
            [basep,[CERTIFICATE_TAG,True,[True],[],None]],
            [basep,[CERTIFICATE_TAG,True,[],[False],None]],
            [basep,[CERTIFICATE_TAG,True,[],[],False]],
            [basep,[CERTIFICATE_TAG,True,[],[],[True,[]]]],
            [basep,[CERTIFICATE_TAG,True,[],[],None,0]],
            [[PROBLEM_TAG,0,[0],[],[],[]],basec],
            [[PROBLEM_TAG,1,[0,0],[],[],[]],basec],
            [[PROBLEM_TAG,1,[],[[[0,0],0]],[],[]],basec],
            [[PROBLEM_TAG,0,[],[[[],0]],[],[]],basec],
            [basep,['wrong-version',True,[],[],None]],
        ]
        for value in malformed:
            fh.write(canonical_bytes(value)+b'\n');eh.write('REJECT\n')
            counts['malformed_inputs']+=1;counts['rejected']+=1
        good=canonical_bytes([basep,basec])
        for raw in [b' '+good,good.replace(b',1,',b',1e0,',1),good.replace(b',1,',b',1.0,',1),
                    good.replace(b',1,',b',-0,',1),b'{"a":1,"a":2}',b'not json']:
            fh.write(raw+b'\n');eh.write('REJECT\n')
            counts['malformed_inputs']+=1;counts['rejected']+=1
    fixture_count=generate_kernel_fixtures()
    report={'publication':'1.8.0','status':'PASS','counts':counts,
        'kernel_fixture_records':fixture_count,
        'case_file':str(cases_path.relative_to(ROOT)),
        'case_sha256':hashlib.sha256(cases_path.read_bytes()).hexdigest(),
        'expected_sha256':hashlib.sha256(expected_path.read_bytes()).hexdigest(),
        'scope':'Complete declared small domains, model enumeration, selected tampering and malformed inputs. No general Python or byte-parser proof.'}
    (data/'trace_exchange_1.8.0.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))

if __name__=='__main__':main()
