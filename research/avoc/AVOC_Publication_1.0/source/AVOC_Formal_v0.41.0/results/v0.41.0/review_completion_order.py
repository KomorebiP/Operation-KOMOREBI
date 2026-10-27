#!/usr/bin/env python3
"""Exact completion-order obstruction for real-process applicability, not the formal theorem."""
from fractions import Fraction
from itertools import product
from math import comb
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tools'))
import observation_recorder
from calibrate_quote import interval


def fraction(value):
    return f'{value.numerator}/{value.denominator}'


def completed_snapshot(bits):
    # All operations begin together. Success duration=1, rejection duration=2.
    # ID is only a deterministic tie breaker within equal completion times.
    order=sorted(range(len(bits)),key=lambda operation:(1 if bits[operation] else 2,operation))
    commands=[['begin',operation,0] for operation in range(len(bits))]
    commands += [['finish',operation,0,'success' if bits[operation] else 'rejection'] for operation in order]
    result=observation_recorder.evaluate(['observation-recorder-v1',commands])
    assert result['status']=='recorded' and result['ready'] and result['pending']==[]
    reported=[event[2]=='success' for event in result['log']]
    assert len(reported)==len(bits) and sum(reported)==sum(bits)
    return order,reported,commands


def main():
    four=[]
    mass=Fraction(1,4)
    for pair in product([False,True],repeat=2):
        order,reported,commands=completed_snapshot(pair)
        four.append({'initiation_bits':list(pair),'mass':fraction(mass),'completion_order':order,
          'stored_bits':reported,'first_stored_success':reported[0],
          'ready_after_both_complete':True,'commands':commands})
    first_mass=sum((mass for row in four if row['first_stored_success']),Fraction())
    assert first_mass==Fraction(3,4)
    initiation_marginals=[sum((mass for row in four if row['initiation_bits'][i]),Fraction()) for i in range(2)]
    assert initiation_marginals==[Fraction(1,2)]*2
    cells=10;n=10;alpha=Fraction(1,10);p=Fraction(1,2)
    grid=[Fraction(i,cells) for i in range(cells+1)]
    lower,upper,_=interval(n,10,alpha,grid)
    assert (lower,upper)==(Fraction(3,5),Fraction(1)) and not lower<=p<=upper
    rows=[]
    for total in range(21):
        # Representative of its binomial count class. Completion ordering makes
        # first-n success count min(total,n), independently of initiation order.
        bits=[True]*total+[False]*(20-total)
        order,reported,commands=completed_snapshot(bits)
        observed=sum(reported[:n]);assert observed==min(total,n)
        cell_lower,cell_upper,_=interval(n,observed,alpha,grid)
        weight=Fraction(comb(20,total),2**20)
        rows.append({'initiation_successes':total,'multiplicity':comb(20,total),
          'mass':fraction(weight),'first_ten_successes':observed,
          'interval':[fraction(cell_lower),fraction(cell_upper)],
          'misses_initiation_parameter':not cell_lower<=p<=cell_upper,
          'lower_bound_event':total>=10,'all_twenty_terminal':True,
          'pending_count':0,'fault_count':0,'dropped_outcomes':0})
    assert sum(comb(20,k) for k in range(21))==2**20
    lower_bound=sum((Fraction(comb(20,k),2**20) for k in range(10,21)),Fraction())
    assert lower_bound==Fraction(308333,524288) and lower_bound>alpha
    assert all(row['misses_initiation_parameter'] for row in rows if row['lower_bound_event'])
    # Complete exact count-class enumeration additionally records actual miss
    # mass, while the requested conclusion needs only the displayed lower bound.
    exact_miss=sum((Fraction(row['mass']) for row in rows if row['misses_initiation_parameter']),Fraction())
    assert exact_miss>=lower_bound
    source_paths=['results/v0.41.0/review_completion_order.py','tools/observation_recorder.py','tools/calibrate_quote.py']
    report={
      'status':'passed','evidence_kind':'Exact finite rational computation; not a new Lean theorem',
      'claim_refuted':'IID outcomes in initiation order plus valid complete lifecycle records imply IID prefixes in outcome-dependent completion order.',
      'four_case_example':{'initiation_model':'Two independent fair Booleans','cases':four,
        'initiation_success_marginals':list(map(fraction,initiation_marginals)),
        'first_stored_success_mass':fraction(first_mass),'target_initiation_parameter':'1/2',
        'all_runs_accepted_and_ready':True},
      'interval_counterexample':{'initiation_model':'Twenty independent fair Booleans',
        'completion_rule':'Success duration 1, rejection duration 2; all attempts start together; ID breaks ties.',
        'collection_rule':'Wait until all twenty operations finish, then read first ten stored terminal reports.',
        'n':n,'grid_cells':cells,'alpha':fraction(alpha),'target_initiation_parameter':fraction(p),
        'all_success_interval':[fraction(lower),fraction(upper)],
        'lower_bound_event':'At least ten successes among twenty initiation outcomes',
        'lower_bound_event_mass':fraction(lower_bound),'lower_bound_exceeds_alpha':True,
        'lower_bound_decimal':float(lower_bound),
        'count_classes':rows,'represented_outcome_vectors':2**20,
        'multiplicity_sum_verified':True,'count_classes_evaluated':21,
        'exact_total_miss_mass':fraction(exact_miss),
        'exact_total_miss_mass_scope':'Exhaustive 21 binomial count classes; each has choose(20,k) equally likely vectors. No simulation and no 2^20-vector loop.',
        'all_reports_recorded':True,'no_pending_operations':True,'no_faults':True},
      'interpretation':'The lifecycle recorder is correct in each example. Outcome-dependent completion order violates the required stationary accepted-source prefix law at p=1/2. It does not refute the formal source-generative theorem, which assigns bits in report order and explicitly assumes that source law.',
      'source_sha256':{path:hashlib.sha256((ROOT/path).read_bytes()).hexdigest() for path in source_paths}}
    path=ROOT/'results/v0.41.0/review_completion_order.json'
    path.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':'passed','first_report_mass':fraction(first_mass),
      'all_success_interval':report['interval_counterexample']['all_success_interval'],
      'interval_miss_lower_bound':fraction(lower_bound),'alpha':fraction(alpha),
      'exact_total_miss_mass':fraction(exact_miss),'classes':21},indent=2))
if __name__=='__main__':main()
