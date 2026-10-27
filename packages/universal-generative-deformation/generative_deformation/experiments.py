from __future__ import annotations

import csv
import json
import math
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp

from .branches import follow_branch
from .examples import (
    AnalyticExpressionSystem,
    DyadicLimitSystem,
    IntegerWalkSystem,
    PolynomialDeformationSystem,
    catalan_numbers,
    fibonacci_numbers,
)
from .extended_examples import (
    AffineShapeSystem,
    CongruenceLiftSystem,
    GaussianFamilySystem,
    GraphDeformationSystem,
    MatrixDeformationSystem,
    QubitGateSystem,
    SequenceTransformSystem,
    path_graph,
    triangle_seed,
)
from .families import infer_constant_coefficient_recurrence
from .forest import PerturbationForest
from .metrics import propagated_cover_error
from .model import Direction, ExplorationConfig
from .visual_atlas import (
    plot_adic_lift_forest,
    plot_affine_shape_atlas,
    plot_analytic_atlas,
    plot_branch_completion,
    plot_continuous_direction_covers,
    plot_cross_domain_counts,
    plot_direction_fiber_gallery,
    plot_exploration_frontier,
    plot_family_certificate_pipeline,
    plot_gaussian_atlas,
    plot_graph_atlas,
    plot_growth_phase_diagram,
    plot_matrix_atlas,
    plot_operadic_hyperforest,
    plot_polynomial_atlas,
    plot_qubit_atlas,
    plot_raw_tree_to_quotient,
    plot_sequence_atlas,
    plot_stability_regimes,
    plot_universal_overview,
)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows[0]) if rows else []
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _direction(system: Any, state: Any, name: str) -> Direction:
    for direction in system.directions(state, 0):
        if direction.name == name:
            return direction
    raise KeyError(name)


def _apply(system: Any, state: Any, *names: str) -> Any:
    value = state
    for name in names:
        value = system.apply(value, _direction(system, value, name))
    return value


def _write_result_macros(path: Path, summaries: dict[str, dict[str, Any]], checks_total: int, test_count: int) -> None:
    macro_names = {
        "integer walk": "Walk",
        "analytic": "Analytic",
        "polynomial": "Polynomial",
        "sequence": "Sequence",
        "gaussian": "Gaussian",
        "qubit": "Qubit",
        "matrix": "Matrix",
        "shape": "Shape",
        "graph": "Graph",
        "adic simple": "AdicSimple",
        "adic singular": "AdicSingular",
    }
    lines = []
    for name, prefix in macro_names.items():
        summary = summaries[name]
        lines.append(f"\\newcommand{{\\{prefix}RawPaths}}{{{summary['raw_paths']}}}")
        lines.append(f"\\newcommand{{\\{prefix}QuotientNodes}}{{{summary['quotient_nodes']}}}")
        lines.append(f"\\newcommand{{\\{prefix}QuotientEdges}}{{{summary['quotient_edges']}}}")
    lines.extend(
        [
            f"\\newcommand{{\\BuiltInChecks}}{{{checks_total}}}",
            f"\\newcommand{{\\TestCount}}{{{test_count}}}",
            "\\newcommand{\\FigureCount}{20}",
            "\\newcommand{\\ExampleCount}{11}",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def run_all(base: str | Path) -> dict[str, Any]:
    root = Path(base)
    figures = root / "paper" / "figures"
    tables = root / "paper" / "tables"
    results_dir = root / "results"
    examples_dir = root / "examples" / "generated"
    for directory in (figures, tables, results_dir, examples_dir):
        directory.mkdir(parents=True, exist_ok=True)

    # Core architecture visuals.
    plot_universal_overview(figures / "00_universal_overview")
    plot_direction_fiber_gallery(figures / "01_direction_fiber_gallery")
    plot_raw_tree_to_quotient(figures / "02_raw_tree_to_quotient", depth=4)
    plot_continuous_direction_covers(figures / "03_continuous_direction_covers")
    plot_operadic_hyperforest(figures / "05_operadic_hyperforest")
    plot_growth_phase_diagram(figures / "06_growth_phase_diagram")
    plot_family_certificate_pipeline(figures / "07_family_certificate_pipeline")
    plot_exploration_frontier(figures / "08_exploration_frontier")
    plot_stability_regimes(figures / "18_stability_regimes")

    # Integer walk.
    walk = PerturbationForest(IntegerWalkSystem(), [0]).explore(
        ExplorationConfig(max_depth=12, max_paths=9000, max_nodes=100, max_edges=1000)
    )
    walk.export(examples_dir / "integer_walk")

    # Analytic grammar.
    x = sp.Symbol("x")
    analytic_system = AnalyticExpressionSystem(x, operation_cap=180)
    analytic = PerturbationForest(analytic_system, [sp.cosh(x)]).explore(
        ExplorationConfig(max_depth=3, max_paths=1800, max_nodes=500, max_edges=4000)
    )
    analytic.export(examples_dir / "analytic")
    analytic_expressions = [
        sp.cosh(x),
        sp.sinh(x),
        1 / sp.cosh(x),
        sp.tanh(x),
        sp.cosh(x) ** 2,
        sp.tanh(x) ** 2,
        1 / sp.sinh(x),
        1 / sp.tanh(x),
        sp.cosh(2 * x),
        sp.cosh(x) ** -2,
    ]
    analytic_labels = [
        "$\\cosh x$",
        "$\\sinh x$",
        "$\\operatorname{sech}x$",
        "$\\tanh x$",
        "$\\cosh^2x$",
        "$\\tanh^2x$",
        "$\\operatorname{csch}x$",
        "$\\coth x$",
        "$\\cosh(2x)$",
        "$\\operatorname{sech}^2x$",
    ]
    plot_analytic_atlas(analytic_expressions, analytic_labels, x, figures / "10_analytic_atlas")

    # Polynomial grammar.
    polynomial_system = PolynomialDeformationSystem(x, max_degree=6)
    polynomial_seed = x**2 + 1
    polynomial = PerturbationForest(polynomial_system, [polynomial_seed]).explore(
        ExplorationConfig(max_depth=4, max_paths=4000, max_nodes=1000, max_edges=6000)
    )
    polynomial.export(examples_dir / "polynomial")
    polynomial_expressions = [
        polynomial_seed,
        _apply(polynomial_system, polynomial_seed, "differentiate"),
        _apply(polynomial_system, polynomial_seed, "finite_difference"),
        _apply(polynomial_system, polynomial_seed, "shift_plus_one"),
        _apply(polynomial_system, polynomial_seed, "multiply_x"),
        _apply(polynomial_system, polynomial_seed, "multiply_x", "differentiate"),
        _apply(polynomial_system, polynomial_seed, "shift_plus_one", "finite_difference"),
        _apply(polynomial_system, polynomial_seed, "finite_difference", "finite_difference"),
    ]
    polynomial_labels = [
        "$x^2+1$",
        "$D p$",
        "$\\Delta p$",
        "$p(x+1)$",
        "$xp$",
        "$D(xp)$",
        "$\\Delta p(x+1)$",
        "$\\Delta^2p$",
    ]
    plot_polynomial_atlas(polynomial_expressions, polynomial_labels, x, figures / "09_polynomial_atlas")

    # Sequence transforms.
    sequence_system = SequenceTransformSystem(length=8)
    sequence_seed = tuple(fibonacci_numbers(8))
    sequence = PerturbationForest(sequence_system, [sequence_seed]).explore(
        ExplorationConfig(max_depth=3, max_paths=800, max_nodes=800, max_edges=3000)
    )
    sequence.export(examples_dir / "sequence")
    sequence_states = [
        sequence_seed,
        _apply(sequence_system, sequence_seed, "difference"),
        _apply(sequence_system, sequence_seed, "partial_sum"),
        _apply(sequence_system, sequence_seed, "binomial_transform"),
        _apply(sequence_system, sequence_seed, "alternating_sign"),
        _apply(sequence_system, sequence_seed, "reverse"),
        _apply(sequence_system, sequence_seed, "difference", "partial_sum"),
    ]
    sequence_labels = [
        "Fibonacci seed",
        "first difference",
        "partial sums",
        "binomial transform",
        "alternating signs",
        "reversal",
        "sum after difference",
    ]
    plot_sequence_atlas(sequence_states, sequence_labels, figures / "11_sequence_atlas")

    # Gaussian parameter family.
    gaussian_system = GaussianFamilySystem()
    gaussian_seed = (Fraction(0), Fraction(1))
    gaussian = PerturbationForest(gaussian_system, [gaussian_seed]).explore(
        ExplorationConfig(max_depth=4, max_paths=5000, max_nodes=1000, max_edges=8000)
    )
    gaussian.export(examples_dir / "gaussian")
    plot_gaussian_atlas(gaussian, figures / "12_gaussian_atlas", max_nodes=58)

    # Projective qubit orbit.
    qubit_system = QubitGateSystem()
    qubit_seed = (0, 0, 1)
    qubit = PerturbationForest(qubit_system, [qubit_seed]).explore(
        ExplorationConfig(max_depth=5, max_paths=1800, max_nodes=50, max_edges=500)
    )
    qubit.export(examples_dir / "qubit")
    plot_qubit_atlas(qubit, figures / "13_qubit_atlas")

    # Matrix orbit.
    matrix_system = MatrixDeformationSystem(entry_cap=512)
    matrix_seed = ((1, 1), (0, 1))
    matrix = PerturbationForest(matrix_system, [matrix_seed]).explore(
        ExplorationConfig(max_depth=3, max_paths=800, max_nodes=800, max_edges=4000)
    )
    matrix.export(examples_dir / "matrix")
    matrix_states = [
        matrix_seed,
        _apply(matrix_system, matrix_seed, "transpose"),
        _apply(matrix_system, matrix_seed, "square"),
        _apply(matrix_system, matrix_seed, "adjugate"),
        _apply(matrix_system, matrix_seed, "transpose", "symmetrize"),
        _apply(matrix_system, matrix_seed, "conjugate_swap"),
        _apply(matrix_system, matrix_seed, "commutator_J"),
    ]
    matrix_labels = ["seed", "transpose", "square", "adjugate", "symmetrize", "swap conjugate", "$[J,A]$"]
    plot_matrix_atlas(matrix_states, matrix_labels, figures / "15_matrix_atlas")

    # Affine geometry.
    shape_system = AffineShapeSystem(coordinate_cap=32)
    shape_seed = triangle_seed()
    shape = PerturbationForest(shape_system, [shape_seed]).explore(
        ExplorationConfig(max_depth=3, max_paths=600, max_nodes=600, max_edges=3000)
    )
    shape.export(examples_dir / "shape")
    shape_states = [
        shape_seed,
        _apply(shape_system, shape_seed, "rotate_90"),
        _apply(shape_system, shape_seed, "shear_x"),
        _apply(shape_system, shape_seed, "scale_two"),
        _apply(shape_system, shape_seed, "reflect_x"),
        _apply(shape_system, shape_seed, "translate_x", "rotate_90"),
    ]
    shape_labels = ["seed", "rotate", "shear", "scale", "reflect", "translate then rotate"]
    plot_affine_shape_atlas(shape_states, shape_labels, figures / "14_affine_shape_atlas")

    # Graph rewriting with isomorphism quotient.
    graph_system = GraphDeformationSystem(node_cap=6)
    graph_seed = path_graph(3)
    graph = PerturbationForest(graph_system, [graph_seed]).explore(
        ExplorationConfig(max_depth=3, max_paths=700, max_nodes=500, max_edges=3000)
    )
    graph.export(examples_dir / "graph")
    graph_states = [
        graph_seed,
        _apply(graph_system, graph_seed, "complement"),
        _apply(graph_system, graph_seed, "line_graph"),
        _apply(graph_system, graph_seed, "add_leaf"),
        _apply(graph_system, graph_seed, "subdivide_first_edge"),
        _apply(graph_system, graph_seed, "complement", "line_graph"),
        _apply(graph_system, graph_seed, "line_graph", "complement"),
        _apply(graph_system, graph_seed, "add_leaf", "relabel_reverse"),
    ]
    graph_labels = ["$P_3$", "complement", "line graph", "add leaf", "subdivide", "$L(\\bar P_3)$", "$\\overline{L(P_3)}$", "same unlabeled graph"]
    plot_graph_atlas(graph_states, graph_labels, figures / "16_graph_atlas")

    # Congruence lift forests.
    adic_simple_system = CongruenceLiftSystem(3, "square_one", depth_cap=5)
    adic_simple = PerturbationForest(adic_simple_system, adic_simple_system.residual_seeds()).explore(
        ExplorationConfig(max_depth=4, max_paths=100, max_nodes=100, max_edges=300)
    )
    adic_simple.export(examples_dir / "adic_simple")
    adic_singular_system = CongruenceLiftSystem(2, "square_zero", depth_cap=6)
    adic_singular = PerturbationForest(adic_singular_system, adic_singular_system.residual_seeds()).explore(
        ExplorationConfig(max_depth=5, max_paths=300, max_nodes=300, max_edges=1000)
    )
    adic_singular.export(examples_dir / "adic_singular")
    plot_adic_lift_forest(adic_simple, adic_singular, figures / "17_adic_lift_forest")

    # Branch completion and continuous covers.
    dyadic_system = DyadicLimitSystem()

    def alternating_selector(state: Fraction, depth: int, directions: list[Any]) -> Any:
        return directions[0] if depth % 3 != 2 else directions[1]

    branch_states, branch_directions = follow_branch(dyadic_system, Fraction(0), alternating_selector, depth=18)
    branch_values = [float(value) for value in branch_states]
    # The infinite continuation has a computable tail. Use a deeper numerical continuation as the plotted limit.
    deep_states, _ = follow_branch(dyadic_system, Fraction(0), alternating_selector, depth=80)
    completed_limit = float(deep_states[-1])
    plot_branch_completion(branch_values, figures / "04_branch_completion", limit=completed_limit)

    cover_levels = list(range(1, 11))
    cover_errors = []
    for level in cover_levels:
        depth = 8
        radii = [2.0 ** (-level - step - 1) for step in range(depth)]
        cover_errors.append(propagated_cover_error([1.0] * depth, [1.0] * depth, radii))

    catalans = catalan_numbers(13)
    fibonacci = fibonacci_numbers(16)
    recurrence = infer_constant_coefficient_recurrence(fibonacci, max_order=5)

    summaries = {
        "integer walk": walk.summary(),
        "analytic": analytic.summary(),
        "polynomial": polynomial.summary(),
        "sequence": sequence.summary(),
        "gaussian": gaussian.summary(),
        "qubit": qubit.summary(),
        "matrix": matrix.summary(),
        "shape": shape.summary(),
        "graph": graph.summary(),
        "adic simple": adic_simple.summary(),
        "adic singular": adic_singular.summary(),
    }
    plot_cross_domain_counts(summaries, figures / "19_cross_domain_counts")

    # Reproducible tables.
    example_rows = []
    for name, summary in summaries.items():
        example_rows.append(
            {
                "example": name,
                "raw_paths": summary["raw_paths"],
                "quotient_nodes": summary["quotient_nodes"],
                "quotient_edges": summary["quotient_edges"],
                "invalid_attempts": summary["invalid_attempts"],
                "compression_ratio": float(summary["quotient_nodes"]) / float(summary["raw_paths"]),
            }
        )
    _write_csv(tables / "example_summary.csv", example_rows)

    with (tables / "example_summary.tex").open("w", encoding="utf-8") as handle:
        handle.write("\\begin{longtable}{lrrrr}\n")
        handle.write("\\caption{Finite explored prefixes used in the visual atlas.}\\label{tab:example-summary}\\\\\n")
        handle.write("\\toprule\nExample & Raw paths & Quotient nodes & Edges & Invalid \\\\\n\\midrule\n\\endfirsthead\n")
        handle.write("\\toprule\nExample & Raw paths & Quotient nodes & Edges & Invalid \\\\\n\\midrule\n\\endhead\n")
        for row in example_rows:
            label = row["example"].replace("adic", "$p$-adic")
            handle.write(f"{label} & {row['raw_paths']} & {row['quotient_nodes']} & {row['quotient_edges']} & {row['invalid_attempts']} \\\\\n")
        handle.write("\\bottomrule\n\\end{longtable}\n")

    sequence_rows = []
    for label, state in zip(sequence_labels, sequence_states):
        sequence_rows.append({"transform": label, "values": " ".join(str(value) for value in state)})
    _write_csv(tables / "sequence_examples.csv", sequence_rows)

    theorem_checks = {
        "integer_walk_raw_depth_12": walk.raw_counts().get(12) == 2**12,
        "integer_walk_quotient_depth_12": walk.quotient_counts().get(12) == 13,
        "dyadic_branch_tail_bound": abs(branch_values[-1] - completed_limit) <= 2 ** -18,
        "cover_error_decreases": all(cover_errors[index + 1] < cover_errors[index] for index in range(len(cover_errors) - 1)),
        "catalan_prefix": catalans[:7] == [1, 1, 2, 5, 14, 42, 132],
        "fibonacci_recurrence": recurrence == [sp.Integer(1), sp.Integer(1)],
        "analytic_contains_tanh": any(sp.simplify(node.state - sp.tanh(x)) == 0 for node in analytic.nodes.values()),
        "analytic_contains_sech": any(sp.simplify(node.state - 1 / sp.cosh(x)) == 0 for node in analytic.nodes.values()),
        "sequence_difference_sum_inverse": _apply(sequence_system, sequence_seed, "difference", "partial_sum") == sequence_seed,
        "gaussian_standardization_returns_canonical_seed": _apply(gaussian_system, _apply(gaussian_system, gaussian_seed, "shift_plus_one", "convolve_unit"), "standardize") == gaussian_seed,
        "qubit_projective_orbit_size": len(qubit.nodes) == 6,
        "qubit_norms_preserved": all(abs(float(node.invariants["purity"]) - 1.0) < 1e-12 for node in qubit.nodes.values()),
        "matrix_transpose_involution": _apply(matrix_system, matrix_seed, "transpose", "transpose") == matrix_seed,
        "shape_rotation_order_four": shape_system.canonical_key(_apply(shape_system, shape_seed, "rotate_90", "rotate_90", "rotate_90", "rotate_90")) == shape_system.canonical_key(shape_seed),
        "graph_relabel_is_quotient_identity": graph_system.canonical_key(_apply(graph_system, graph_seed, "relabel_reverse")) == graph_system.canonical_key(graph_seed),
        "simple_adic_lifts_unique": all(len(list(adic_simple_system.directions(node.state, node.min_depth))) == 1 for node in adic_simple.nodes.values() if node.state[0] < adic_simple_system.depth_cap),
        "singular_adic_branching_occurs": any(len(list(adic_singular_system.directions(node.state, node.min_depth))) > 1 for node in adic_singular.nodes.values()),
        "all_extended_examples_reduce_routes": all(summary["quotient_nodes"] <= summary["raw_paths"] for summary in summaries.values()),
    }

    # test count is rewritten after the test suite runs by Run_All.ps1. The source macro uses the current suite size.
    test_count = 50
    _write_result_macros(tables / "result_macros.tex", summaries, len(theorem_checks), test_count)

    summary = {
        "title": "Universal Generative Deformation Calculus: Visual Atlas and Worked Examples Edition",
        "version": "1.1.0",
        "examples": summaries,
        "dyadic_branch": {
            "depth": len(branch_directions),
            "last_value": str(branch_states[-1]),
            "completed_limit_approximation": completed_limit,
        },
        "continuous_cover": {"levels": cover_levels, "errors": cover_errors},
        "catalan_numbers": catalans,
        "fibonacci_recurrence": [str(value) for value in recurrence] if recurrence else None,
        "checks": theorem_checks,
        "checks_passed": sum(bool(value) for value in theorem_checks.values()),
        "checks_total": len(theorem_checks),
        "figure_pairs": 20,
    }
    (results_dir / "results.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    _write_csv(results_dir / "checks.csv", [{"check": key, "passed": bool(value)} for key, value in theorem_checks.items()])
    return summary
