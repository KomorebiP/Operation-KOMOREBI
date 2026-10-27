import sympy as sp

from generative_deformation import (
    ExplorationConfig,
    IntegerWalkSystem,
    PerturbationForest,
    certify_family,
    cluster_by_signature,
    fibonacci_numbers,
    infer_constant_coefficient_recurrence,
)
from generative_deformation.families import verify_recurrence


def test_fibonacci_recurrence_inference() -> None:
    coefficients = infer_constant_coefficient_recurrence(fibonacci_numbers(16), max_order=4)
    assert coefficients == [sp.Integer(1), sp.Integer(1)]


def test_recurrence_verification_rejects_wrong_rule() -> None:
    values = [sp.Rational(value) for value in fibonacci_numbers(12)]
    assert not verify_recurrence(values, [sp.Integer(2)])


def test_cluster_by_parity() -> None:
    forest = PerturbationForest(IntegerWalkSystem(), [0]).explore(
        ExplorationConfig(max_depth=5, max_paths=1000, max_nodes=100, max_edges=500)
    )
    groups = cluster_by_signature(forest, ["parity"])
    assert set(groups) == {(0,), (1,)}


def test_integer_family_closure_under_plus_and_minus() -> None:
    forest = PerturbationForest(IntegerWalkSystem(), [0]).explore(
        ExplorationConfig(max_depth=4, max_paths=100, max_nodes=100, max_edges=500)
    )
    certificate = certify_family(
        forest,
        name="integers",
        predicate=lambda state: isinstance(state, int),
        parameter_map=int,
        closure_directions=("plus_one", "minus_one"),
        invariant_fields=("parity",),
        relations=("plus_one followed by minus_one is identity",),
    )
    assert certificate.verified
    assert certificate.member_node_ids
