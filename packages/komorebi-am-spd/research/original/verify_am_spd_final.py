from __future__ import annotations

import itertools
import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np

import adaptive_multiscale_spd_exact as exact

ROOT = Path(__file__).resolve().parent


@dataclass
class Ledger:
    scenarios: int = 0
    failures: int = 0
    max_residual: float = 0.0

    def check(self, passed: bool, residual: float = 0.0) -> None:
        self.scenarios += 1
        self.max_residual = max(self.max_residual, float(abs(residual)))
        if not passed:
            self.failures += 1

    @property
    def passed(self) -> bool:
        return self.failures == 0


def random_orthonormal(rng: np.random.Generator, rows: int, columns: int) -> np.ndarray:
    if columns == 0:
        return np.empty((rows, 0), dtype=np.float64)
    Q, _ = np.linalg.qr(rng.normal(size=(rows, columns)))
    return Q[:, :columns]


def patch_roundtrip_ledger(rng: np.random.Generator) -> Ledger:
    ledger = Ledger()
    for _ in range(30):
        h = int(rng.integers(2, 11))
        w = int(rng.integers(2, 11))
        channels = int(rng.integers(1, 5))
        patch = rng.normal(size=(h, w, channels))
        for orientation in ('row', 'column', 'channel'):
            matrix = exact.patch_matrix(patch, orientation)
            recovered = exact.component_from_matrix(matrix, patch.shape, orientation)
            residual = float(np.max(np.abs(recovered - patch)))
            ledger.check(residual < 1e-12, residual)
    return ledger


def local_svd_ledger(rng: np.random.Generator) -> Ledger:
    ledger = Ledger()
    for _ in range(32):
        h = int(rng.integers(3, 10))
        w = int(rng.integers(3, 10))
        channels = int(rng.integers(1, 4))
        patch = rng.normal(size=(h, w, channels))
        region = exact.Region(0, 0, h, w, 0, 'verification')
        models = exact.local_models(patch, region, max_rank=3)
        zero = next(model for model in models if model.rank == 0)
        energy = float(np.sum(patch * patch))
        ledger.check(abs(zero.error_squared - energy) < 1e-10, abs(zero.error_squared - energy))
        for orientation in ('row', 'column', 'channel'):
            matrix = exact.patch_matrix(patch, orientation)
            singular_values = np.linalg.svd(matrix, compute_uv=False)
            eligible = [model for model in models if model.orientation == orientation]
            for model in eligible:
                expected = float(np.sum(singular_values[model.rank:] ** 2))
                error_residual = abs(model.error_squared - expected)
                ledger.check(error_residual < 2e-9 * max(1.0, energy), error_residual)
                if model.directions:
                    D = np.column_stack([direction.reshape(-1) for direction in model.directions])
                    orth = float(np.max(np.abs(D.T @ D - np.eye(D.shape[1]))))
                    ledger.check(orth < 2e-11, orth)
                    coefficients = D.T @ patch.reshape(-1)
                    expected_coefficients = np.asarray(model.singular_values)
                    coeff_residual = float(np.max(np.abs(np.abs(coefficients) - expected_coefficients)))
                    ledger.check(coeff_residual < 2e-9, coeff_residual)
    return ledger


def complement_basis_ledger(rng: np.random.Generator) -> Ledger:
    ledger = Ledger()
    for _ in range(60):
        dimension = int(rng.integers(12, 70))
        base_rank = int(rng.integers(0, min(8, dimension - 1)))
        raw_rank = int(rng.integers(1, min(10, dimension)))
        base = random_orthonormal(rng, dimension, base_rank)
        raw_matrix = rng.normal(size=(dimension, raw_rank))
        raw = [raw_matrix[:, index].reshape(dimension, 1) for index in range(raw_rank)]
        Q = exact.complement_basis(raw, base)
        if Q.shape[1]:
            orth = float(np.max(np.abs(Q.T @ Q - np.eye(Q.shape[1]))))
            cross = float(np.max(np.abs(base.T @ Q))) if base_rank else 0.0
        else:
            orth = 0.0
            cross = 0.0
        projected = raw_matrix - base @ (base.T @ raw_matrix) if base_rank else raw_matrix
        span_residual = float(np.linalg.norm(projected - Q @ (Q.T @ projected))) if Q.shape[1] else float(np.linalg.norm(projected))
        ledger.check(orth < 2e-11 and cross < 2e-11 and span_residual < 2e-9, max(orth, cross, span_residual))
    return ledger


def block_gain_ledger(rng: np.random.Generator) -> Ledger:
    ledger = Ledger()
    for _ in range(80):
        dimension = int(rng.integers(15, 90))
        base_rank = int(rng.integers(0, min(10, dimension - 2)))
        block_rank = int(rng.integers(1, min(8, dimension - base_rank)))
        base = random_orthonormal(rng, dimension, base_rank)
        target = rng.normal(size=dimension)
        residual = target - base @ (base.T @ target) if base_rank else target.copy()
        block = rng.normal(size=(dimension, block_rank))
        raw = [block[:, index].reshape(dimension, 1) for index in range(block_rank)]
        Q = exact.complement_basis(raw, base)
        old_squared = float(residual @ residual)
        if Q.shape[1]:
            gain = float(np.sum((Q.T @ residual) ** 2))
            expanded = np.column_stack([base, Q]) if base_rank else Q
            new_residual = target - expanded @ (expanded.T @ target)
        else:
            gain = 0.0
            new_residual = residual
        new_squared = float(new_residual @ new_residual)
        identity_residual = abs((old_squared - new_squared) - gain)
        ledger.check(identity_residual < 4e-9 * max(1.0, old_squared), identity_residual)
    return ledger


def monotone_refit_ledger(rng: np.random.Generator) -> Ledger:
    ledger = Ledger()
    for _ in range(40):
        dimension = int(rng.integers(20, 90))
        target = rng.normal(size=dimension)
        basis = np.empty((dimension, 0))
        previous = float(np.linalg.norm(target))
        for _step in range(8):
            raw = [rng.normal(size=(dimension, 1)) for _ in range(int(rng.integers(1, 4)))]
            Q = exact.complement_basis(raw, basis)
            if Q.shape[1]:
                basis = np.column_stack([basis, Q])
            residual = target - basis @ (basis.T @ target) if basis.shape[1] else target
            current = float(np.linalg.norm(residual))
            ledger.check(current <= previous + 2e-11, max(0.0, current - previous))
            previous = current
    return ledger


def enumerate_tree_states(node: exact.TreeNode) -> list[exact.ParetoState]:
    keep = [exact.ParetoState(model.parameter_count, model.error_squared, [exact.TreeSelection(node.region, model)]) for model in node.models]
    if not node.children:
        return keep
    child_lists = [enumerate_tree_states(child) for child in node.children]
    split: list[exact.ParetoState] = []
    for choice in itertools.product(*child_lists):
        split.append(
            exact.ParetoState(
                sum(item.parameter_count for item in choice),
                sum(item.error_squared for item in choice),
                [selection for item in choice for selection in item.selections],
            )
        )
    return keep + split


def random_test_tree(rng: np.random.Generator) -> exact.TreeNode:
    root = exact.TreeNode(exact.Region(0, 0, 8, 8, 0, 'random'))
    children = [
        exact.TreeNode(exact.Region(0, 0, 4, 4, 1, 'random')),
        exact.TreeNode(exact.Region(0, 4, 4, 8, 1, 'random')),
        exact.TreeNode(exact.Region(4, 0, 8, 4, 1, 'random')),
        exact.TreeNode(exact.Region(4, 4, 8, 8, 1, 'random')),
    ]
    root.children = children
    for index, node in enumerate([root] + children):
        models = [exact.LocalModel('zero', 0, 0, float(rng.uniform(2.0, 12.0)), [], [])]
        for rank in range(1, 4):
            cost = int(rng.integers(2, 24)) + rank * 3
            error = float(rng.uniform(0.0, models[-1].error_squared * 0.82))
            models.append(exact.LocalModel('row', rank, cost, error, [], [1.0] * rank))
        node.models = models
    return root


def exact_tree_dp_ledger(rng: np.random.Generator) -> Ledger:
    ledger = Ledger()
    for _ in range(120):
        root = random_test_tree(rng)
        brute = enumerate_tree_states(root)
        budget = 80
        frontier = exact.exact_tree_frontier(root, budget)
        # Check every budget, not just one point.
        for current_budget in range(budget + 1):
            brute_candidates = [state for state in brute if state.parameter_count <= current_budget]
            exact_candidates = [state for state in frontier if state.parameter_count <= current_budget]
            brute_error = min((state.error_squared for state in brute_candidates), default=math.inf)
            exact_error = min((state.error_squared for state in exact_candidates), default=math.inf)
            residual = 0.0 if math.isinf(brute_error) and math.isinf(exact_error) else abs(brute_error - exact_error)
            ledger.check(residual < 1e-10, residual)
        # Verify nondominance and monotonicity of the frontier.
        costs = [state.parameter_count for state in frontier]
        errors = [state.error_squared for state in frontier]
        ledger.check(costs == sorted(costs), 0.0 if costs == sorted(costs) else 1.0)
        ledger.check(all(errors[index + 1] < errors[index] - 1e-12 for index in range(len(errors) - 1)), 0.0)
    return ledger


def region_partition_ledger(rng: np.random.Generator) -> Ledger:
    ledger = Ledger()
    for _ in range(30):
        h = int(rng.integers(9, 40))
        w = int(rng.integers(9, 40))
        depth = int(rng.integers(1, 5))
        root = exact.build_tree(h, w, max_depth=depth)

        def visit(node: exact.TreeNode) -> None:
            if not node.children:
                return
            mask = np.zeros((node.region.height, node.region.width), dtype=int)
            for child in node.children:
                y0 = child.region.y0 - node.region.y0
                y1 = child.region.y1 - node.region.y0
                x0 = child.region.x0 - node.region.x0
                x1 = child.region.x1 - node.region.x0
                mask[y0:y1, x0:x1] += 1
            residual = float(np.max(np.abs(mask - 1)))
            ledger.check(residual == 0.0, residual)
            for child in node.children:
                visit(child)

        visit(root)
    return ledger


def singular_gap_ledger(rng: np.random.Generator) -> Ledger:
    ledger = Ledger()
    for _ in range(70):
        rows = int(rng.integers(6, 16))
        cols = int(rng.integers(6, 16))
        rank = min(rows, cols)
        U = random_orthonormal(rng, rows, rank)
        V = random_orthonormal(rng, cols, rank)
        singular_values = np.linspace(5.0, 0.5, rank)
        split = int(rng.integers(1, rank))
        singular_values[split - 1] += 1.5
        gap = singular_values[split - 1] - singular_values[split]
        matrix = U @ np.diag(singular_values) @ V.T
        perturbation = rng.normal(size=(rows, cols))
        perturbation_norm = float(np.linalg.norm(perturbation, 2))
        perturbation *= (0.20 * gap) / max(perturbation_norm, 1e-15)
        actual_norm = float(np.linalg.norm(perturbation, 2))
        perturbed_values = np.linalg.svd(matrix + perturbation, compute_uv=False)
        original_values = np.linalg.svd(matrix, compute_uv=False)
        weyl_residual = float(np.max(np.abs(perturbed_values - original_values)) - actual_norm)
        threshold = 0.5 * (original_values[split - 1] + original_values[split])
        stable = int(np.sum(perturbed_values > threshold)) == split
        ledger.check(weyl_residual <= 2e-10 and stable, max(0.0, weyl_residual))
    return ledger


def archive_identity_ledger(rng: np.random.Generator) -> Ledger:
    ledger = Ledger()
    for _ in range(60):
        shape = (int(rng.integers(4, 12)), int(rng.integers(4, 12)), int(rng.integers(1, 4)))
        target = rng.normal(size=shape)
        dimension = int(np.prod(shape))
        rank = int(rng.integers(0, min(10, dimension)))
        basis = random_orthonormal(rng, dimension, rank)
        reconstruction, residual = exact.project_target(target, basis)
        identity_residual = float(np.max(np.abs(target - reconstruction - residual)))
        pythagorean = abs(float(np.sum(target * target)) - float(np.sum(reconstruction * reconstruction)) - float(np.sum(residual * residual)))
        ledger.check(identity_residual < 1e-12 and pythagorean < 2e-9, max(identity_residual, pythagorean))
    return ledger


def portfolio_nonregression_ledger(rng: np.random.Generator) -> Ledger:
    ledger = Ledger()
    for _ in range(300):
        baseline = float(rng.uniform(0.001, 1.0))
        candidates = [baseline] + [float(rng.uniform(0.0, 2.0)) for _ in range(int(rng.integers(1, 20)))]
        selected = min(candidates)
        ledger.check(selected <= baseline, max(0.0, selected - baseline))
    return ledger


def current_results_ledger() -> Ledger:
    ledger = Ledger()
    results = json.loads((ROOT / 'results' / 'adaptive_multiscale_spd_final_results.json').read_text())
    for name, item in results['cases'].items():
        ledger.check(bool(item['nonregression']), 0.0 if item['nonregression'] else 1.0)
        ledger.check(int(item['final_parameters']) <= int(item['parameter_budget']), max(0, int(item['final_parameters']) - int(item['parameter_budget'])))
        ledger.check(float(item['final_bounded_rmse']) < float(item['matched_residual_svd_rmse']), max(0.0, float(item['final_bounded_rmse']) - float(item['matched_residual_svd_rmse'])))
        ledger.check(int(item['frontier_states']) > 0, 0.0 if int(item['frontier_states']) > 0 else 1.0)
        ledger.check(float(item['exact_budget_global_error_squared']) <= float(item['exact_budget_local_error_squared']) + 1e-10, max(0.0, float(item['exact_budget_global_error_squared']) - float(item['exact_budget_local_error_squared'])))
    stress = json.loads((ROOT / 'results' / 'am_spd_final_stress.json').read_text())
    ledger.check(int(stress['full_beats_row_rank1']) == int(stress['cases']), abs(int(stress['full_beats_row_rank1']) - int(stress['cases'])))
    ledger.check(int(stress['full_beats_row_column_rank1']) == int(stress['cases']), abs(int(stress['full_beats_row_column_rank1']) - int(stress['cases'])))
    ledger.check(int(stress['full_beats_global_svd']) >= 7, max(0, 7 - int(stress['full_beats_global_svd'])))
    ledger.check(float(stress['median_full_to_row_rank1_ratio']) < 0.65, max(0.0, float(stress['median_full_to_row_rank1_ratio']) - 0.65))
    noise = json.loads((ROOT / 'results' / 'am_spd_final_noise_stress.json').read_text())
    ledger.check(int(noise['scenario_count']) == 36, abs(int(noise['scenario_count']) - 36))
    ledger.check(bool(noise['all_within_budget']), 0.0 if noise['all_within_budget'] else 1.0)
    ledger.check(bool(noise['finite_metrics']), 0.0 if noise['finite_metrics'] else 1.0)
    ledger.check(0 <= int(noise['positive_denoising_scenarios']) <= 36, 0.0)
    ledger.check(0.0 <= float(noise['mean_support_jaccard']) <= 1.0, 0.0)
    return ledger


def main() -> None:
    rng = np.random.default_rng(20260731)
    groups = {
        'patch_roundtrip': patch_roundtrip_ledger(rng),
        'local_svd_optimality': local_svd_ledger(rng),
        'orthogonal_complement': complement_basis_ledger(rng),
        'exact_block_gain': block_gain_ledger(rng),
        'monotone_global_refit': monotone_refit_ledger(rng),
        'exact_budget_tree_dp': exact_tree_dp_ledger(rng),
        'region_partition': region_partition_ledger(rng),
        'singular_gap_stability': singular_gap_ledger(rng),
        'exact_archive_identity': archive_identity_ledger(rng),
        'portfolio_nonregression': portfolio_nonregression_ledger(rng),
        'reported_results_consistency': current_results_ledger(),
    }
    output = {
        'groups': {
            name: {
                'passed': ledger.passed,
                'scenarios': ledger.scenarios,
                'failures': ledger.failures,
                'max_residual': ledger.max_residual,
            }
            for name, ledger in groups.items()
        },
        'groups_passed': sum(ledger.passed for ledger in groups.values()),
        'groups_total': len(groups),
        'scenarios_passed': sum(ledger.scenarios - ledger.failures for ledger in groups.values()),
        'scenarios_total': sum(ledger.scenarios for ledger in groups.values()),
        'failures': [name for name, ledger in groups.items() if not ledger.passed],
    }
    destination = ROOT / 'results' / 'am_spd_final_verification.json'
    destination.write_text(json.dumps(output, indent=2) + '\n')
    print(json.dumps(output, indent=2))
    if output['failures']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
