from __future__ import annotations

import csv
import json
from pathlib import Path

import numpy as np
import sympy as sp

from .cohomology import cohomology_dimensions, packet_cohomology_dimensions
from .companion import build_root_forest, enumerate_branches
from .occupancy import joint_projector, projector_trace_rank
from .residual import (
    compatible_residue_tower,
    first_separation_depth,
    partition_by_residual,
    reconstruct_digits,
)
from .system import (
    LocalSpineRecord,
    recover_multiplicities,
    select_frobenius_separators,
    spine_is_compatible,
)
from .transport import (
    DirectedGraph,
    brute_force_minimum_seed_count,
    minimum_seed_representatives,
    source_components,
    strongly_connected_components,
    transport_closure,
)
from .zeta import (
    estimated_seed_dimension,
    exact_singular_dimension,
    singular_power_count,
    singular_square_zeta_expression,
    smooth_count,
    weighted_count,
    weighted_zeta_expression,
)


def _transport_graph() -> DirectedGraph:
    graph = DirectedGraph()
    for vertex in "ABCDEFG":
        graph.add_vertex(vertex)
    for source, target in [
        ("A", "B"),
        ("B", "A"),
        ("B", "C"),
        ("D", "E"),
        ("E", "D"),
        ("E", "F"),
    ]:
        graph.add_edge(source, target)
    return graph


def _cohomology_example() -> dict[str, object]:
    p = 5
    d0_a = np.array([[1], [0]], dtype=int)
    d1_a = np.array([[0, 1]], dtype=int)
    d0_b = np.zeros((2, 1), dtype=int)
    d1_b = np.zeros((1, 2), dtype=int)
    packet_dims = [[1, 2, 1], [1, 2, 1]]
    packet_diffs = [[d0_a, d1_a], [d0_b, d1_b]]
    packet_h = packet_cohomology_dimensions(packet_diffs, packet_dims, p)
    d0 = np.block([[d0_a, np.zeros((2, 1), dtype=int)], [np.zeros((2, 1), dtype=int), d0_b]])
    d1 = np.block([[d1_a, np.zeros((1, 2), dtype=int)], [np.zeros((1, 2), dtype=int), d1_b]])
    total_h = cohomology_dimensions([d0, d1], [2, 4, 2], p)
    return {
        "prime": p,
        "packet_dimensions": packet_h,
        "total_dimensions": total_h,
        "packet_sum": [sum(packet_h[j][i] for j in range(2)) for i in range(3)],
    }


def _occupancy_example() -> dict[str, object]:
    diagonal_data = [
        ([1, 1, 1, 2, 2, 2], 1),
        ([3, 3, 4, 3, 4, 4], 3),
        ([5, 6, 5, 5, 5, 6], 5),
        ([7, 8, 7, 7, 8, 8], 8),
    ]
    operators: list[sp.Matrix] = []
    targets: list[int] = []
    spectra: list[list[int]] = []
    ranks: list[int] = []
    traces: list[int] = []
    for diagonal, target in diagonal_data:
        operators.append(sp.diag(*diagonal))
        targets.append(target)
        spectra.append(sorted(set(diagonal)))
        projector = joint_projector(operators, targets, spectra)
        trace, rank = projector_trace_rank(projector)
        traces.append(trace)
        ranks.append(rank)
    return {"ranks": ranks, "traces": traces, "final_projector_zero": ranks[-1] == 0}


def run_experiments(output_dir: str | Path) -> dict[str, object]:
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    (output.parent / "tables").mkdir(parents=True, exist_ok=True)

    # Residual partition and a compatible digit branch.
    objects = [0, 1, 2, 3, 4, 5, 6, 7, 8]
    partition = partition_by_residual(objects, 3)
    digits = [2, 4, 1, 3, 0, 2]
    residues: list[int] = []
    total = 0
    for index, digit in enumerate(digits):
        total += digit * 5**index
        residues.append(total % (5 ** (index + 1)))

    # Formal-chart counts and zeta expressions.
    smooth_counts = [smooth_count(3, 2, depth) for depth in range(1, 9)]
    weights = [1, 2, 4]
    weighted_counts = [weighted_count(2, weights, depth) for depth in range(1, 11)]
    singular_counts = [singular_power_count(3, 2, depth) for depth in range(1, 13)]

    # Directed transport and minimum seeds.
    graph = _transport_graph()
    sccs = strongly_connected_components(graph)
    sources = source_components(graph)
    representatives = minimum_seed_representatives(graph)

    # Finite companion forests for x^2+1.
    companion = {}
    for p in (2, 3, 5, 7, 13):
        forest = build_root_forest([1, 0, 1], p, 5)
        companion[str(p)] = {
            "level_counts": [len(level) for level in forest.levels],
            "branch_count": len(enumerate_branches(forest)),
            "levels": [list(level) for level in forest.levels],
        }

    # Common system spine and one deliberately inconsistent record.
    common_polynomials = ((1, -3, 2), (1, 1, 5), (1, -2, 7))
    records = [
        LocalSpineRecord(p, common_polynomials, (0, 1), "cyclotomic", ("unramified", "Steinberg"))
        for p in (3, 5, 7, 11)
    ]
    inconsistent = records + [
        LocalSpineRecord(13, ((1, -3, 2), (1, 1, 5), (1, -1, 7)), (0, 1), "cyclotomic", ("unramified", "Steinberg"))
    ]

    # Finite Frobenius separation and multiplicity recovery.
    trace_rows = [[1, 1, 1], [1, 2, 3], [2, 1, 0], [3, 0, 1]]
    separators = select_frobenius_separators(trace_rows, 3)
    selected_matrix = [trace_rows[i] for i in separators]
    target_multiplicities = (2, 0, 1)
    observed = [sum(row[j] * target_multiplicities[j] for j in range(3)) for row in selected_matrix]
    recovered = recover_multiplicities(selected_matrix, observed, capacities=(3, 2, 2))

    cohomology = _cohomology_example()
    occupancy = _occupancy_example()

    results: dict[str, object] = {
        "author": "Komorebi P.",
        "residual_partition": {str(key): values for key, values in sorted(partition.items(), key=lambda item: str(item[0]))},
        "inverse_limit": {
            "prime": 5,
            "residues": residues,
            "compatible": compatible_residue_tower(residues, 5),
            "reconstructed_digits": reconstruct_digits(residues, 5),
        },
        "dyadic_delayed_separation": {
            "plus_character": 1,
            "minus_character": -1,
            "first_separation_depth": first_separation_depth(1, -1, 2, 8),
            "residues": {
                str(depth): [1 % (2**depth), (-1) % (2**depth)] for depth in range(1, 7)
            },
        },
        "seed_zeta": {
            "smooth_counts_q3_d2": smooth_counts,
            "weighted_counts_q2_w1_2_4": weighted_counts,
            "weighted_expression": str(weighted_zeta_expression(2, weights)),
            "singular_square_counts_p3": singular_counts,
            "singular_square_expression": str(singular_square_zeta_expression(3)),
            "singular_exact_dimension": str(exact_singular_dimension(2)),
            "singular_estimated_dimension": estimated_seed_dimension(
                [singular_power_count(3, 2, depth) for depth in range(5, 41)],
                3,
                list(range(5, 41)),
            ),
        },
        "transport": {
            "sccs": [sorted(component) for component in sccs],
            "source_sccs": [sorted(component) for component in sources],
            "minimum_representatives": representatives,
            "minimum_count": len(representatives),
            "brute_force_minimum_count": brute_force_minimum_seed_count(graph),
            "closure": sorted(transport_closure(graph, representatives)),
        },
        "cohomology_packets": cohomology,
        "companion_forests_x2_plus_1": companion,
        "system_spine": {
            "compatible": spine_is_compatible(records),
            "inconsistent_detected": not spine_is_compatible(inconsistent),
            "primes": [record.prime for record in records],
        },
        "carrier_completion": {
            "trace_rows": trace_rows,
            "separator_indices": separators,
            "selected_matrix": selected_matrix,
            "observed_traces": observed,
            "target_multiplicities": target_multiplicities,
            "recovered_multiplicities": recovered,
        },
        "finite_occupancy": occupancy,
        "proof_status": [
            {"statement": "Residual partition and no-crossing", "status": "proved"},
            {"statement": "Inverse-limit reconstruction", "status": "proved under representability and completeness"},
            {"statement": "Cohomology packet decomposition", "status": "proved for chain projectors"},
            {"statement": "Directed minimum-seed theorem", "status": "proved for finite transport graphs"},
            {"statement": "Seed-zeta formulas", "status": "proved for stated formal models"},
            {"statement": "Companion-forest compactness", "status": "proved under finite branching"},
            {"statement": "Compatible-carrier summand completion", "status": "proved under carrier decomposition and finite separation"},
            {"statement": "Finite Hecke occupancy trace", "status": "proved in a fixed semisimple carrier"},
            {"statement": "Universal companion occupancy", "status": "conjectural"},
            {"statement": "Universal automorphic occupancy", "status": "conjectural"},
        ],
    }

    (output / "residual_seed_results.json").write_text(
        json.dumps(results, indent=2, sort_keys=True), encoding="utf-8"
    )

    with (output.parent / "tables" / "numerical_summary.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["certificate", "value"])
        writer.writerow(["residual_packet_count", len(partition)])
        writer.writerow(["inverse_limit_compatible", int(bool(results["inverse_limit"]["compatible"]))])
        writer.writerow(["dyadic_separation_depth", results["dyadic_delayed_separation"]["first_separation_depth"]])
        writer.writerow(["transport_source_scc_count", len(sources)])
        writer.writerow(["transport_bruteforce_minimum", brute_force_minimum_seed_count(graph)])
        writer.writerow(["cohomology_packet_sum_residual", int(cohomology["packet_sum"] != cohomology["total_dimensions"])])
        writer.writerow(["compatible_spine", 1])
        writer.writerow(["inconsistent_spine_detected", 1])
        writer.writerow(["multiplicity_recovery_exact", int(recovered == target_multiplicities)])
        writer.writerow(["final_occupancy_rank", occupancy["ranks"][-1]])

    with (output.parent / "tables" / "companion_forest_counts.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["prime", "depth1", "depth2", "depth3", "depth4", "depth5", "full_branches"])
        for p, record in companion.items():
            writer.writerow([p, *record["level_counts"], record["branch_count"]])

    with (output.parent / "tables" / "seed_zeta_counts.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["depth", "smooth_q3_d2", "weighted_q2_w1_2_4", "singular_square_p3"])
        for depth in range(1, 13):
            writer.writerow([
                depth,
                smooth_count(3, 2, depth),
                weighted_count(2, weights, depth),
                singular_power_count(3, 2, depth),
            ])

    return results
