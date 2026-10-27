from fractions import Fraction

import sympy as sp

from generative_deformation import (
    AnalyticExpressionSystem,
    DyadicLimitSystem,
    ExplorationConfig,
    IntegerWalkSystem,
    PerturbationForest,
    PolynomialDeformationSystem,
)


def test_integer_walk_raw_counts() -> None:
    forest = PerturbationForest(IntegerWalkSystem(), [0]).explore(
        ExplorationConfig(max_depth=8, max_paths=1000, max_nodes=100, max_edges=500)
    )
    for depth in range(9):
        assert forest.raw_counts()[depth] == 2**depth


def test_integer_walk_quotient_counts() -> None:
    forest = PerturbationForest(IntegerWalkSystem(), [0]).explore(
        ExplorationConfig(max_depth=8, max_paths=1000, max_nodes=100, max_edges=500)
    )
    for depth in range(9):
        assert forest.quotient_counts()[depth] == depth + 1


def test_integer_walk_quotient_total() -> None:
    depth = 8
    forest = PerturbationForest(IntegerWalkSystem(), [0]).explore(
        ExplorationConfig(max_depth=depth, max_paths=1000, max_nodes=100, max_edges=500)
    )
    assert len(forest.nodes) == 2 * depth + 1


def test_edge_multiplicity_records_duplicate_routes() -> None:
    forest = PerturbationForest(IntegerWalkSystem(), [0]).explore(
        ExplorationConfig(max_depth=4, max_paths=100, max_nodes=100, max_edges=500)
    )
    assert any(edge.multiplicity > 1 for edge in forest.edges.values())


def test_shortest_path_reaches_endpoint() -> None:
    system = IntegerWalkSystem()
    forest = PerturbationForest(system, [0]).explore(
        ExplorationConfig(max_depth=5, max_paths=1000, max_nodes=100, max_edges=500)
    )
    target_id = forest.node_by_key[5]
    state = 0
    for label in forest.shortest_path_labels(target_id):
        if label == "plus_one":
            state += 1
        elif label == "minus_one":
            state -= 1
    assert state == 5


def test_dyadic_depth_counts() -> None:
    forest = PerturbationForest(DyadicLimitSystem(), [Fraction(0)]).explore(
        ExplorationConfig(max_depth=6, max_paths=200, max_nodes=200, max_edges=1000)
    )
    assert forest.raw_counts()[6] == 64


def test_polynomial_relations_collapse_paths() -> None:
    x = sp.Symbol("x")
    forest = PerturbationForest(PolynomialDeformationSystem(x, max_degree=5), [x]).explore(
        ExplorationConfig(max_depth=3, max_paths=500, max_nodes=500, max_edges=2000)
    )
    assert len(forest.nodes) < len(forest.paths)


def test_analytic_generates_tanh_and_sech() -> None:
    x = sp.Symbol("x")
    system = AnalyticExpressionSystem(x)
    forest = PerturbationForest(system, [sp.cosh(x)]).explore(
        ExplorationConfig(max_depth=2, max_paths=300, max_nodes=300, max_edges=1000)
    )
    assert any(sp.simplify(node.state - sp.tanh(x)) == 0 for node in forest.nodes.values())
    assert any(sp.simplify(node.state - 1 / sp.cosh(x)) == 0 for node in forest.nodes.values())


def test_invalid_analytic_reciprocal_is_audited() -> None:
    x = sp.Symbol("x")
    system = AnalyticExpressionSystem(x)
    forest = PerturbationForest(system, [sp.Integer(0)]).explore(
        ExplorationConfig(max_depth=1, max_paths=50, max_nodes=50, max_edges=100)
    )
    assert forest.invalid_attempts
    assert any("reciprocal" in item["direction"] for item in forest.invalid_attempts)


def test_export_roundtrip_files(tmp_path) -> None:
    forest = PerturbationForest(IntegerWalkSystem(), [0]).explore(
        ExplorationConfig(max_depth=3, max_paths=100, max_nodes=100, max_edges=500)
    )
    forest.export(tmp_path)
    assert (tmp_path / "forest.json").is_file()
    assert (tmp_path / "nodes.csv").is_file()
    assert (tmp_path / "edges.csv").is_file()
