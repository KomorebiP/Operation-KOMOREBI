"""Regression examples for issues identified during the monograph review."""
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path

import pytest
from proof_path_theory import (
    Certificate, ClaimNode, Justification, NodeKind, ProofField,
    load_proof_field, minimum_certificate, unique_and_dag_certificate,
    validate_certificate,
)
from proof_path_theory.certificate import is_and_dag

ROOT = Path(__file__).resolve().parents[1]


def leaf_boundary_field():
    return ProofField(
        [ClaimNode('X','unused claim',NodeKind.CLAIM),
         ClaimNode('A','admitted premise',NodeKind.PREMISE),
         ClaimNode('B','target',NodeKind.CLAIM)],
        [Justification('optional-proof-A',('X',),'A','optional derivation'),
         Justification('j-B',('A',),'B','deduction')],
        premises=('A',),targets=('B',),
    )


def test_admitted_leaf_stops_backward_expansion():
    f=leaf_boundary_field()
    assert is_and_dag(f)
    c=unique_and_dag_certificate(f)
    assert c.node_ids == frozenset({'A','B'})
    assert c.justification_ids == frozenset({'j-B'})
    assert validate_certificate(f,c).valid


def test_least_justification_set_does_not_make_pair_unique():
    f=leaf_boundary_field(); c=unique_and_dag_certificate(f)
    larger=Certificate(c.node_ids|{'X'},c.justification_ids,c.targets)
    assert validate_certificate(f,larger).valid
    assert larger != c and larger.justification_ids == c.justification_ids


def test_least_node_set_does_not_make_pair_unique():
    f=leaf_boundary_field(); c=unique_and_dag_certificate(f)
    other=Certificate(c.node_ids,c.justification_ids|{'optional-proof-A'},c.targets)
    assert validate_certificate(f,other).valid
    assert other != c and other.node_ids == c.node_ids


def test_core_pair_is_contained_in_every_certificate_on_example():
    f=leaf_boundary_field(); core=unique_and_dag_certificate(f)
    ns=tuple(f.nodes); js=tuple(f.justifications)
    checked=0
    for nb in product((0,1),repeat=len(ns)):
        K=frozenset(x for x,b in zip(ns,nb) if b)
        for jb in product((0,1),repeat=len(js)):
            H=frozenset(x for x,b in zip(js,jb) if b)
            c=Certificate(K,H,f.targets)
            if validate_certificate(f,c).valid:
                checked+=1
                assert core.node_ids<=K and core.justification_ids<=H
    assert checked>1


def test_zero_premise_certified_rule_is_retained():
    f=ProofField([ClaimNode('B','target',NodeKind.CLAIM)],
                 [Justification('j-B',(),'B','zero-premise rule')],
                 premises=(),targets=('B',))
    c=unique_and_dag_certificate(f)
    assert c.justification_ids==frozenset({'j-B'})
    assert validate_certificate(f,c).valid


@pytest.mark.parametrize('large_base,rich_cost,short_cost',[
    (0.0,1.5e-12,1.0e-12),
    (0.0,1.5e-100,1.0e-100),
    (float(2**54),2.0,1.0),
    (float(2**100),3.0,2.0),
])
def test_exact_cost_ordering_no_tolerance_or_rounding_loss(large_base,rich_cost,short_cost):
    f=load_proof_field(ROOT/'examples/alternative_proofs.json')
    nodes={key:0.0 for key in f.nodes}; nodes['A']=large_base
    costs={key:0.0 for key in f.justifications}
    costs['j-rich']=rich_cost; costs['j-short']=short_cost
    c=minimum_certificate(f,node_cost=nodes,justification_cost=costs)
    assert 'j-short' in c.justification_ids
    assert 'j-rich' not in c.justification_ids


def test_single_archive_decoders_do_not_supply_uniform_sufficiency():
    archives=(0,1); encode=lambda _: 0
    individual=[lambda _,a=a:a for a in archives]
    assert all(d(encode(a))==a for a,d in zip(archives,individual))
    assert not any(all(answer==a for a in archives) for answer in (0,1))


def test_tagged_portfolio_avoids_untagged_collision():
    a=(0,1); b=(1,0)
    assert set(a)==set(b) and a!=b
    assert a[0]!=b[0]


def test_all_predicate_sufficiency_is_injectivity_on_finite_examples():
    domain=range(3)
    for encoding in product(range(3),repeat=3):
        factors_all=True
        for predicate in product((0,1),repeat=3):
            factors=all(encoding[i]!=encoding[j] or predicate[i]==predicate[j]
                        for i in domain for j in domain)
            factors_all &= factors
        assert factors_all==(len(set(encoding))==3)


def test_randomized_difference_is_sample_average_effect():
    y1=(1,0,3,2); y0=(0,1,2,0); N=4; n1=2
    effects=[]
    for treatment in combinations(range(N),n1):
        treated=set(treatment)
        estimate=sum(Fraction(y1[i],n1) for i in treated)
        estimate-=sum(Fraction(y0[i],N-n1) for i in range(N) if i not in treated)
        effects.append(estimate)
    mean=sum(effects,Fraction(0))/len(effects)
    expected=sum((Fraction(a-b,N) for a,b in zip(y1,y0)),Fraction(0))
    assert mean==expected


def test_complete_monograph_example_imports():
    f=load_proof_field(ROOT/'examples/minimal_monograph.json')
    assert f.targets<=f.derive()
    assert validate_certificate(f,unique_and_dag_certificate(f)).valid


def test_zero_goal_weights_do_not_select_unique_refinement():
    residual=(3,1); cost=(1,4)
    for alpha,beta,expected in ((1,0,1),(0,1,0)):
        values=[alpha*r+beta*c for r,c in zip(residual,cost)]
        assert min(range(2),key=values.__getitem__)==expected
    assert [0*r+0*c for r,c in zip(residual,cost)]==[0,0]
