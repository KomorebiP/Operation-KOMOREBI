from dataclasses import replace
import pytest
from proof_path_theory import (ClaimNode, NodeKind, Justification, ProofField, ProofFieldViews,
    analyze_semantic_cover, verify_semantic_cover, glue_semantic, SemanticCoverResult,
    RuleEntailment, DerivationWitness)


def field(rules,leaves=()):
    return ProofFieldViews(ProofField(
        [ClaimNode(v,v,NodeKind.PREMISE if v in leaves else NodeKind.CLAIM) for v in 'abc'],
        [Justification(f'r{i}',p,c,'declared') for i,(p,c) in enumerate(rules)],
        premises=leaves, targets=('c',)))


def test_missing_redundant_support_is_semantically_covered():
    v=field([(('a',),'b'),(('b',),'c'),(('a',),'c')])
    ps=[{'a','b'},{'b','c'}]
    assert not v.covers_supports(ps)
    r=analyze_semantic_cover(v,ps)
    assert r.sufficient and verify_semantic_cover(v,ps,r)
    assert r.entailments[-1].witness.rule_ids==('r0','r1')
    assert glue_semantic(v,ps,[{'a','b'},{'b','c'}],r)==frozenset('abc')
    assert len(v.rules)==3  # Filtering did not mutate the original field.


def test_nonredundant_support_supplies_countermodel():
    v=field([(('a','b'),'c')]); ps=[{'a','c'},{'b','c'}]
    r=analyze_semantic_cover(v,ps)
    assert not r.sufficient and r.countermodel==frozenset('ab')
    assert verify_semantic_cover(v,ps,r)
    with pytest.raises(ValueError):glue_semantic(v,ps,[{'a'},{'b'}],r)


def test_leaves_can_make_a_missing_rule_redundant():
    v=field([(('a','b'),'c')],leaves=('c',));ps=[{'a','c'},{'b','c'}]
    r=analyze_semantic_cover(v,ps)
    assert r.sufficient and verify_semantic_cover(v,ps,r)
    assert r.entailments[0].witness.rule_ids==()


def test_support_cover_is_sufficient():
    v=field([(('a','b'),'c')]); ps=[set('abc')]
    assert v.covers_supports(ps)
    r=analyze_semantic_cover(v,ps)
    assert verify_semantic_cover(v,ps,r) and r.sufficient


def test_node_coverage_remains_required():
    v=field([])
    with pytest.raises(ValueError,match='node coverage'):analyze_semantic_cover(v,[{'a'}])


def test_ruleless_field_has_positive_empty_certificate():
    v=field([]);ps=[{'a'},{'b'},{'c'}];r=analyze_semantic_cover(v,ps)
    assert r.entailments==() and verify_semantic_cover(v,ps,r)


def test_positive_certificate_rejects_missing_duplicated_and_invalid_derivations():
    v=field([(('a',),'b'),(('b',),'c'),(('a',),'c')]);ps=[{'a','b'},{'b','c'}]
    r=analyze_semantic_cover(v,ps)
    assert not verify_semantic_cover(v,ps,replace(r,entailments=r.entailments[:-1]))
    assert not verify_semantic_cover(v,ps,replace(r,entailments=r.entailments+r.entailments[:1]))
    assert not verify_semantic_cover(v,ps,replace(r,entailments=(RuleEntailment('r2',DerivationWitness('c',('r2',))),)+r.entailments[:2]))
    assert not verify_semantic_cover(v,ps,replace(r,countermodel=frozenset()))


def test_negative_certificate_rejects_fake_models():
    v=field([(('a','b'),'c')]);ps=[{'a','c'},{'b','c'}];r=analyze_semantic_cover(v,ps)
    assert not verify_semantic_cover(v,ps,replace(r,countermodel=frozenset('abc')))
    assert not verify_semantic_cover(v,ps,replace(r,countermodel=frozenset('a')))
    assert not verify_semantic_cover(v,ps,replace(r,failed_rule='unknown'))
    assert not verify_semantic_cover(v,ps,replace(r,sufficient='false'))


def test_gluing_rejects_mismatch():
    v=field([(('a',),'b'),(('b',),'c'),(('a',),'c')]);ps=[{'a','b'},{'b','c'}];r=analyze_semantic_cover(v,ps)
    with pytest.raises(ValueError,match='overlap'):glue_semantic(v,ps,[{'b'},set()],r)
