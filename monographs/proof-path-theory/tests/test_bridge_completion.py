from __future__ import annotations

from itertools import combinations, product
import random

import pytest

from proof_path_theory import (
    ClaimNode, Justification, NodeKind, ProofField, ProofFieldViews,
    FiniteViewSystem, Restriction, analyze_affine_realizations,
    check_obstruction_witness, proof_field_from_dict, proof_field_to_dict,
)


def make_field(premises=(), rules=((('a', 'b'), 'c', True),)):
    return ProofField(
        [ClaimNode(v, v, NodeKind.PREMISE if v in premises else NodeKind.CLAIM)
         for v in ('a', 'b', 'c')],
        [Justification(str(i), tuple(pre), con, 'declared rule', certified=cert)
         for i, (pre, con, cert) in enumerate(rules)],
        premises=premises, targets=('c',),
    )


def test_pairwise_cover_is_not_hyperedge_support_cover():
    v = ProofFieldViews(make_field())
    patches = ({'a', 'c'}, {'b', 'c'})
    truths = ({'a'}, {'b'})
    assert all(v.is_local_model(p, t) for p, t in zip(patches, truths))
    assert not v.covers_supports(patches)
    with pytest.raises(ValueError, match='whole'):
        v.glue(patches, truths)
    assert not v.is_local_model(v.nodes, {'a', 'b'})
    diagram, mapping = v.to_view_system(patches)
    # This diagram has coherent families that omit the full conjunction constraint.
    assert len(diagram.sections()) == 8
    assert len(v.local_models(v.nodes)) == 7


def test_support_cover_glues_and_restrictions_compose():
    v = ProofFieldViews(make_field(premises=('a',)))
    u, w, full = frozenset({'a'}), frozenset({'a', 'c'}), v.nodes
    for t in v.local_models(full):
        assert v.restrict(w, u, v.restrict(full, w, t)) == v.restrict(full, u, t)
        assert v.restrict(full, full, t) == t
        assert v.glue((full, w, u), (t, t & w, t & u)) == t


def test_support_cover_without_global_patch():
    field = ProofField(
        [ClaimNode(v, v, NodeKind.PREMISE if v == 'a' else NodeKind.CLAIM)
         for v in ('a', 'b', 'c', 'd')],
        [Justification('ab', ('a',), 'b', 'rule'),
         Justification('bcd', ('b', 'c'), 'd', 'rule')], premises=('a',), targets=('d',))
    v = ProofFieldViews(field)
    ps = ({'a', 'b'}, {'b', 'c', 'd'})
    assert v.covers_supports(ps)
    system, mapping = v.to_view_system(ps)
    global_models = v.local_models(v.nodes)
    assert len(system.sections()) == len(global_models)
    for t in global_models:
        assert v.glue(ps, tuple(t & frozenset(p) for p in ps)) == t
    # A native restriction assignment verifies the actual edge equations.
    for t in global_models:
        assignment = {k: ''.join('1' if x in t else '0' for x in p) for k, p in mapping.items()}
        assert system.is_coherent(assignment)


def test_declared_rule_countermodel_is_not_semantic_refutation():
    v = ProofFieldViews(make_field(premises=('a',)))
    cm = v.countermodel('c')
    assert cm == frozenset({'a'}) and v.is_local_model(v.nodes, cm)
    alternative = ProofFieldViews(make_field(premises=('a',), rules=(
        (('a', 'b'), 'c', False), (('a',), 'c', True))))
    assert alternative.countermodel('c') is None


def test_exhaustive_three_node_model_completeness():
    rules = [((), 'b', True), (('a',), 'b', True), (('b',), 'c', True),
             (('a',), 'c', True), (('a', 'b'), 'c', True)]
    for mask in range(1 << len(rules)):
        selected = tuple(r for i, r in enumerate(rules) if (mask >> i) & 1)
        for leaves in ((), ('a',), ('a', 'b')):
            f = make_field(premises=leaves, rules=selected)
            v = ProofFieldViews(f)
            models = v.local_models(v.nodes)
            assert v.least_model() == f.derive()
            for target in v.nodes:
                assert (target in f.derive()) == all(target in model for model in models)
                cm = v.countermodel(target)
                if cm is not None:
                    assert v.is_local_model(v.nodes, cm) and target not in cm


def test_matching_checks_false_as_well_as_true_values():
    v = ProofFieldViews(make_field())
    with pytest.raises(ValueError, match='overlap'):
        v.glue((v.nodes, {'a'}), ({'a'}, set()))


def test_bridge_rejects_unknown_nodes_and_excessive_enumeration():
    v = ProofFieldViews(make_field())
    with pytest.raises(ValueError): v.local_models({'unknown'})
    with pytest.raises(ValueError): v.local_models(v.nodes, max_assignments=1)
    with pytest.raises(ValueError): v.to_view_system(({'a'}, {'b'}), max_patches=1)
    with pytest.raises(ValueError): v.restrict({'a'}, {'b'}, set())
    with pytest.raises(ValueError): v.glue((v.nodes,), ())
    with pytest.raises(ValueError): v.countermodel('unknown')


def test_empty_and_obstructed_view_fibers_are_distinct():
    empty = FiniteViewSystem({}, ())
    assert empty.sections() == ({},) and empty.glue(()) == {}
    obstructed = FiniteViewSystem({'v': ()}, ())
    assert obstructed.sections() == ()
    with pytest.raises(ValueError): obstructed.glue(({'v': 'x'},))
    singleton = FiniteViewSystem({'empty_patch': ('',)}, ())
    assert singleton.sections() == ({'empty_patch': ''},)


def test_restriction_input_mutation_does_not_change_validated_system():
    data = {'0': '0', '1': '1'}
    system = FiniteViewSystem({'a': ('0','1'), 'b': ('0','1')}, (Restriction('a','b',data),))
    data['1'] = '0'
    assert system.is_coherent({'a':'1','b':'1'})
    with pytest.raises(TypeError): system.fibers['a'] = ()


@pytest.mark.parametrize('bad', ['false', 'true', 0, 1, [], {}, None])
def test_certification_is_not_coerced_from_truthiness(bad):
    payload = proof_field_to_dict(make_field())
    payload['justifications'][0]['certified'] = bad
    with pytest.raises(ValueError, match='boolean'):
        proof_field_from_dict(payload)
    with pytest.raises(ValueError, match='boolean'):
        Justification('bad', ('a',), 'b', 'rule', certified=bad)


@pytest.mark.parametrize('bad', [-1, 1.0, True, '3'])
def test_exact_dimension_contract(bad):
    with pytest.raises(ValueError):
        analyze_affine_realizations(dimension=bad, compatibility=[], protected=[], candidate=[])
    with pytest.raises(ValueError):
        check_obstruction_witness(dimension=bad, compatibility=[], protected=[], candidate=[], witness=[])


def test_binary_floats_rejected_before_arithmetic():
    with pytest.raises(ValueError, match='binary integer'):
        analyze_affine_realizations(dimension=1, compatibility=[[1.0]], protected=[], candidate=[0])
    with pytest.raises(ValueError, match='binary integer'):
        analyze_affine_realizations(dimension=1, compatibility=[], protected=[], candidate=[0.0])
    assert not check_obstruction_witness(dimension=1, compatibility=[[1]], protected=[[1]],
                                        candidate=[1], witness=[1.0, 1.0])


def test_zero_dimension_and_redundant_observations():
    z = analyze_affine_realizations(dimension=0, compatibility=[[]], protected=[[]], candidate=[], observation=[[]])
    assert z.feasible and z.realization_count == 1 and z.observation_gain_bits == 0
    r = analyze_affine_realizations(dimension=3, compatibility=[[1,1,0]], protected=[], candidate=[0,0,0],
                                    observation=[[0,0,1], [0,0,1]])
    assert r.ambiguity_dimension == 2 and r.observation_gain_bits == 1
