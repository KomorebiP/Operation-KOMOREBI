from dataclasses import replace
from itertools import product

import pytest

from proof_path_theory import (
    ClaimNode, Justification, NodeKind, ProofField, ProofFieldViews,
    DecoderCertificate, CollisionWitness, FactorizationResult, factor_task,
    verify_factorization, compose_decoders, joint_task_scheme,
    DerivationWitness, solve_extension, extend_partial, verify_extension_result,
    verify_extension_obstruction,
)


def views(rules=((('a', 'b'), 'c', True),), leaves=()):
    return ProofFieldViews(ProofField(
        [ClaimNode(v, v, NodeKind.PREMISE if v in leaves else NodeKind.CLAIM) for v in ('a','b','c')],
        [Justification(f'r{i}', pre, con, 'declared', certified=cert) for i,(pre,con,cert) in enumerate(rules)],
        premises=leaves, targets=('c',)))


def test_uniform_decoder_and_exact_domain():
    enc={'p0':'x','p1':'x','p2':'y'};task={'p0':'a','p1':'a','p2':'b'}
    result=factor_task(enc,task)
    assert result.sufficient and verify_factorization(enc,task,result)
    assert result.decoder.decode('x')=='a'
    with pytest.raises(KeyError): result.decoder.decode('unattained')
    with pytest.raises(ValueError): factor_task(enc,{'p0':'a'})


def test_collision_is_explicit_and_validated():
    enc={'p0':'same','p1':'same'};task={'p0':'0','p1':'1'}
    result=factor_task(enc,task)
    assert result.collision==CollisionWitness('p0','p1')
    assert not result.sufficient and verify_factorization(enc,task,result)
    assert not verify_factorization(enc,task,FactorizationResult(collision=CollisionWitness('p0','p0')))


def test_empty_domain_has_a_unique_empty_decoder():
    result=factor_task({}, {})
    assert result.decoder==DecoderCertificate(())
    assert verify_factorization({}, {}, result)
    assert not verify_factorization({}, {}, FactorizationResult(decoder=DecoderCertificate((('unused','answer'),))))


@pytest.mark.parametrize('bad',[
    FactorizationResult(),
    FactorizationResult(DecoderCertificate(()),CollisionWitness('p','q')),
    FactorizationResult(decoder=DecoderCertificate((('x','a'),('x','a')))),
    FactorizationResult(decoder=DecoderCertificate((('x','wrong'),))),
    FactorizationResult(decoder=DecoderCertificate((('x','a'),('extra','a')))),
    FactorizationResult(collision=CollisionWitness('p','missing')),
])
def test_bad_factorization_records_are_rejected(bad):
    assert not verify_factorization({'p':'x'},{'p':'a'},bad)


@pytest.mark.parametrize('value',[1,True,None,(),float('nan')])
def test_factorization_does_not_coerce_values(value):
    with pytest.raises(ValueError): factor_task({'p':value},{'p':'a'})


def test_decoder_composition_and_missing_intermediate():
    inner=DecoderCertificate((('i','a'),('j','b')))
    outer=DecoderCertificate((('a','yes'),('b','no')))
    composite=compose_decoders(outer,inner)
    assert composite.decode('i')=='yes' and composite.decode('j')=='no'
    with pytest.raises(ValueError): compose_decoders(DecoderCertificate((('a','yes'),)),inner)


def test_joint_tasks_are_least_sufficient():
    domain=('00','01','10','11')
    qx={p:p[0] for p in domain};qy={p:p[1] for p in domain}
    joint=joint_task_scheme(domain,(qx,qy))
    assert len(set(joint.values()))==4
    assert factor_task(joint,qx).sufficient and factor_task(joint,qy).sufficient
    assert not factor_task(qx,joint).sufficient
    assert not factor_task(qx,qy).sufficient
    assert len(set(joint_task_scheme(domain,()).values()))==1
    assert joint_task_scheme((),())=={}


def test_joint_scheme_rejects_bad_domain_and_task_tables():
    with pytest.raises(ValueError): joint_task_scheme(('a','a'),())
    with pytest.raises(ValueError): joint_task_scheme(('a',),({'other':'0'},))
    with pytest.raises(ValueError): joint_task_scheme((1,),())


def test_obstruction_derives_forbidden_node():
    v=views();r=solve_extension(v,positive={'a','b'},negative={'c'})
    assert not r.feasible and r.closure==frozenset({'a','b','c'})
    assert r.obstruction==DerivationWitness('c',('r0',))
    assert verify_extension_result(v,positive={'a','b'},negative={'c'},result=r)


def test_partial_extension_preserves_false_values():
    v=views()
    yes=extend_partial(v,{'a','c'},{'a'})
    assert yes.feasible and yes.closure==frozenset({'a'})
    no=extend_partial(v,{'a','b','c'},{'a','b'})
    assert not no.feasible


def test_seed_and_negative_overlap_has_empty_trace():
    v=views();r=solve_extension(v,positive={'a'},negative={'a'})
    assert not r.feasible and r.obstruction==DerivationWitness('a',())
    assert verify_extension_result(v,positive={'a'},negative={'a'},result=r)


def test_required_leaf_cannot_be_forbidden():
    v=views(leaves=('a',));r=solve_extension(v,negative={'a'})
    assert not r.feasible and r.obstruction.rule_ids==()


def test_unconditional_rule_is_not_an_assumed_leaf():
    v=views(rules=(((), 'a',True),(('a',),'b',True),(('b',),'c',True)))
    r=solve_extension(v,negative={'c'})
    assert not r.feasible and r.obstruction.rule_ids==('r0','r1','r2')
    assert verify_extension_result(v,positive=(),negative={'c'},result=r)


def test_uncertified_steps_cannot_support_an_obstruction():
    v=views(rules=((('a','b'),'c',False),))
    r=solve_extension(v,positive={'a','b'},negative={'c'})
    assert r.feasible
    assert not verify_extension_obstruction(v,{'a','b'},{'c'},DerivationWitness('c',('r0',)))


def test_witness_prunes_causal_trace_without_claiming_minimum_cost():
    v=views(rules=(((), 'a',True),((), 'b',True),(('a',),'c',True)))
    r=solve_extension(v,negative={'c'})
    assert r.rule_ids==('r0','r1','r2')
    assert r.obstruction.rule_ids==('r0','r2')
    assert verify_extension_obstruction(v,(),{'c'},r.obstruction)
    assert not verify_extension_obstruction(v,(),{'c'},DerivationWitness('c',('r2','r0')))


def test_obstruction_reuse_requires_scope():
    v=views();r=solve_extension(v,positive={'a','b'},negative={'c'})
    assert verify_extension_obstruction(v,{'a','b','c'},{'c'},r.obstruction)
    assert not verify_extension_obstruction(v,{'a'},{'c'},r.obstruction)
    assert not verify_extension_obstruction(v,{'a','b'},{'b'},r.obstruction)
    assert not verify_extension_obstruction(views(rules=()),{'a','b'},{'c'},r.obstruction)


def test_leastness_checker_rejects_arbitrary_larger_model():
    v=views();r=solve_extension(v)
    assert r.feasible and r.closure==frozenset()
    assert not verify_extension_result(v,positive=(),negative=(),result=replace(r,closure=v.nodes))
    assert not verify_extension_result(v,positive=(),negative=(),result=replace(r,feasible=False))
    assert not verify_extension_result(v,positive=(),negative=(),result=replace(r,feasible=1))


def test_infeasible_record_needs_a_valid_witness():
    v=views();r=solve_extension(v,positive={'a','b'},negative={'c'})
    assert not verify_extension_result(v,positive={'a','b'},negative={'c'},result=replace(r,obstruction=None))
    assert not verify_extension_result(v,positive={'a','b'},negative={'c'},result=replace(r,obstruction=DerivationWitness('a',())))


def test_unknown_observations_and_outside_true_nodes():
    v=views()
    with pytest.raises(ValueError): solve_extension(v,positive={'z'})
    with pytest.raises(ValueError): solve_extension(v,negative={'z'})
    with pytest.raises(ValueError): extend_partial(v,{'a'},{'b'})


def test_malformed_witness_is_rejected_not_used():
    v=views()
    assert not verify_extension_obstruction(v,(),{'c'},DerivationWitness(['c'],()))


def test_staged_closure_and_observation_antitonicity():
    v=views(rules=((('a',),'b',True),(('b',),'c',True)))
    first=solve_extension(v,positive={'a'})
    staged=solve_extension(v,positive=first.closure | {'b'})
    direct=solve_extension(v,positive={'a','b'})
    assert staged.closure==direct.closure
    assert not solve_extension(v,positive={'a'},negative={'c'}).feasible


def test_symbol_labels_not_semantic_truth():
    # Failure is relative to the declared rules, even if names look like truth values.
    v=views(rules=())
    assert solve_extension(v,positive={'a','b'},negative={'c'}).feasible


def test_seven_model_space_is_not_an_affine_binary_fiber():
    assert len(views().local_models({'a','b','c'}))==7
    assert 7 not in (1,2,4,8)
