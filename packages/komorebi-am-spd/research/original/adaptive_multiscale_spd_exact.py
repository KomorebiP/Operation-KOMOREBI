from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Sequence

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import NDArray
from scipy import ndimage

import infinite_packet_gibbs_reconstruction as atlas
import singular_packet_decomposition_extension as spd

Array = NDArray[np.float64]


@dataclass(frozen=True)
class Region:
    y0: int
    x0: int
    y1: int
    x1: int
    depth: int = 0
    source: str = 'unknown'

    @property
    def height(self) -> int:
        return self.y1 - self.y0

    @property
    def width(self) -> int:
        return self.x1 - self.x0

    @property
    def key(self) -> tuple[int, int, int, int]:
        return self.y0, self.x0, self.y1, self.x1


@dataclass
class LocalModel:
    orientation: str
    rank: int
    parameter_count: int
    error_squared: float
    directions: list[Array]
    singular_values: list[float]


@dataclass
class TreeNode:
    region: Region
    children: list['TreeNode'] = field(default_factory=list)
    models: list[LocalModel] = field(default_factory=list)


@dataclass
class TreeSelection:
    region: Region
    model: LocalModel


@dataclass
class ParetoState:
    parameter_count: int
    error_squared: float
    selections: list[TreeSelection]


@dataclass
class BlockSelection:
    iteration: int
    region: Region
    orientation: str
    rank: int
    parameter_count: int
    gain: float
    score: float
    singular_values: list[float]


@dataclass
class AMResult:
    reconstruction: Array
    residual: Array
    directions: list[Array]
    parameter_count: int
    residual_norms: list[float]
    blocks: list[BlockSelection]
    tree_selections: list[TreeSelection] = field(default_factory=list)


def clamp_region(region: Region, height: int, width: int, source: str | None = None) -> Region | None:
    y0 = max(0, min(height, int(region.y0)))
    x0 = max(0, min(width, int(region.x0)))
    y1 = max(0, min(height, int(region.y1)))
    x1 = max(0, min(width, int(region.x1)))
    if y1 - y0 < 2 or x1 - x0 < 2:
        return None
    return Region(y0, x0, y1, x1, max(0, region.depth), source or region.source)


def unique_regions(regions: Iterable[Region], height: int, width: int) -> list[Region]:
    store: dict[tuple[int, int, int, int], Region] = {}
    for region in regions:
        value = clamp_region(region, height, width)
        if value is None:
            continue
        current = store.get(value.key)
        if current is None or value.depth < current.depth:
            store[value.key] = value
    return list(store.values())


def split_region(region: Region) -> list[Region]:
    y0, x0, y1, x1 = region.key
    ym = (y0 + y1) // 2
    xm = (x0 + x1) // 2
    return [
        Region(y0, x0, ym, xm, region.depth + 1, 'split'),
        Region(y0, xm, ym, x1, region.depth + 1, 'split'),
        Region(ym, x0, y1, xm, region.depth + 1, 'split'),
        Region(ym, xm, y1, x1, region.depth + 1, 'split'),
    ]


def perturb_regions(region: Region, height: int, width: int) -> list[Region]:
    dy = max(1, region.height // 6)
    dx = max(1, region.width // 6)
    y0, x0, y1, x1 = region.key
    out = [
        Region(y0 - dy, x0, y1 - dy, x1, region.depth + 1, 'move'),
        Region(y0 + dy, x0, y1 + dy, x1, region.depth + 1, 'move'),
        Region(y0, x0 - dx, y1, x1 - dx, region.depth + 1, 'move'),
        Region(y0, x0 + dx, y1, x1 + dx, region.depth + 1, 'move'),
        Region(y0 - dy, x0 - dx, y1 + dy, x1 + dx, region.depth + 1, 'expand'),
    ]
    if region.height > 8 and region.width > 8:
        out.append(Region(y0 + dy // 2, x0 + dx // 2, y1 - dy // 2, x1 - dx // 2, region.depth + 1, 'contract'))
    return unique_regions(out, height, width)


def dyadic_regions(height: int, width: int, max_depth: int = 4) -> list[Region]:
    root = Region(0, 0, height, width, 0, 'dyadic')
    frontier = [root]
    output = [root]
    for _ in range(max_depth):
        next_frontier: list[Region] = []
        for region in frontier:
            children = [child for child in split_region(region) if child.height >= 2 and child.width >= 2]
            output.extend(children)
            next_frontier.extend(children)
        frontier = next_frontier
    return unique_regions(output, height, width)


def packet_regions(result: atlas.ReconstructionResult, height: int, width: int) -> list[Region]:
    output: list[Region] = []
    for atom in result.active_atoms:
        threshold = max(float(np.max(np.abs(atom))) * 0.15, 1e-10)
        yy, xx = np.nonzero(np.abs(atom) >= threshold)
        if len(yy) == 0:
            continue
        output.append(Region(int(yy.min()), int(xx.min()), int(yy.max()) + 1, int(xx.max()) + 1, 0, 'packet'))
    return unique_regions(output, height, width)


def residual_regions(residual: Array, max_components: int = 18) -> list[Region]:
    value = np.sqrt(np.mean(np.asarray(residual) ** 2, axis=2))
    gradient = np.hypot(ndimage.sobel(value, axis=0), ndimage.sobel(value, axis=1))
    output: list[Region] = []
    for field, source in ((value, 'residual'), (gradient, 'gradient')):
        for quantile in (0.78, 0.88, 0.94):
            threshold = float(np.quantile(field, quantile))
            labels, count = ndimage.label(field >= threshold)
            slices = ndimage.find_objects(labels)
            candidates: list[tuple[float, Region]] = []
            for index, slc in enumerate(slices, start=1):
                if slc is None:
                    continue
                yslice, xslice = slc
                if (yslice.stop - yslice.start) * (xslice.stop - xslice.start) < 6:
                    continue
                mask = labels[slc] == index
                energy = float(np.sum(field[slc][mask] ** 2))
                pad_y = max(1, (yslice.stop - yslice.start) // 5)
                pad_x = max(1, (xslice.stop - xslice.start) // 5)
                region = Region(yslice.start - pad_y, xslice.start - pad_x, yslice.stop + pad_y, xslice.stop + pad_x, 0, source)
                candidates.append((energy, region))
            candidates.sort(reverse=True, key=lambda item: item[0])
            output.extend(region for _, region in candidates[:max_components])
    h, w = residual.shape[:2]
    return unique_regions(output, h, w)


def patch_matrix(patch: Array, orientation: str) -> Array:
    h, w, channels = patch.shape
    if orientation == 'row':
        return patch.reshape(h, w * channels)
    if orientation == 'column':
        return np.transpose(patch, (1, 0, 2)).reshape(w, h * channels)
    if orientation == 'channel':
        return np.transpose(patch, (2, 0, 1)).reshape(channels, h * w)
    raise ValueError(orientation)


def component_from_matrix(matrix_component: Array, shape: tuple[int, int, int], orientation: str) -> Array:
    h, w, channels = shape
    if orientation == 'row':
        return matrix_component.reshape(h, w, channels)
    if orientation == 'column':
        return matrix_component.reshape(w, h, channels).transpose(1, 0, 2)
    if orientation == 'channel':
        return matrix_component.reshape(channels, h, w).transpose(1, 2, 0)
    raise ValueError(orientation)


def model_parameter_count(region: Region, orientation: str, rank: int, channels: int) -> int:
    h, w = region.height, region.width
    if orientation == 'row':
        rows, cols = h, w * channels
    elif orientation == 'column':
        rows, cols = w, h * channels
    else:
        rows, cols = channels, h * w
    return int(6 + rank * (rows + cols + 1))


def local_models(residual: Array, region: Region, max_rank: int = 3) -> list[LocalModel]:
    patch = residual[region.y0:region.y1, region.x0:region.x1]
    h, w, channels = patch.shape
    patch_energy = float(np.sum(patch * patch))
    if patch_energy <= 1e-16:
        return [LocalModel('zero', 0, 0, 0.0, [], [])]
    output: list[LocalModel] = [
        LocalModel(
            orientation='zero',
            rank=0,
            parameter_count=0,
            error_squared=patch_energy,
            directions=[],
            singular_values=[],
        )
    ]
    orientations = ['row', 'column']
    if h * w <= 420:
        orientations.append('channel')
    for orientation in orientations:
        matrix = patch_matrix(patch, orientation)
        U, singular_values, Vt = np.linalg.svd(matrix, full_matrices=False)
        max_here = min(max_rank, len(singular_values))
        cumulative = 0.0
        directions: list[Array] = []
        for index in range(max_here):
            matrix_direction = np.outer(U[:, index], Vt[index])
            local = component_from_matrix(matrix_direction, patch.shape, orientation)
            full = np.zeros_like(residual)
            full[region.y0:region.y1, region.x0:region.x1] = local
            norm = float(np.linalg.norm(full))
            if norm <= 1e-14:
                continue
            directions.append(full / norm)
            cumulative += float(singular_values[index] ** 2)
            error = max(0.0, patch_energy - cumulative)
            output.append(
                LocalModel(
                    orientation=orientation,
                    rank=index + 1,
                    parameter_count=model_parameter_count(region, orientation, index + 1, channels),
                    error_squared=error,
                    directions=list(directions),
                    singular_values=[float(value) for value in singular_values[: index + 1]],
                )
            )
    return output


def complement_basis(raw_directions: Sequence[Array], basis: Array, tolerance: float = 1e-10) -> Array:
    if not raw_directions:
        return np.empty((basis.shape[0], 0), dtype=np.float64)
    matrix = np.column_stack([np.asarray(direction, dtype=np.float64).reshape(-1) for direction in raw_directions])
    if basis.shape[1]:
        matrix = matrix - basis @ (basis.T @ matrix)
    if matrix.size == 0:
        return np.empty((basis.shape[0], 0), dtype=np.float64)
    U, singular_values, _ = np.linalg.svd(matrix, full_matrices=False)
    if len(singular_values) == 0:
        return np.empty((basis.shape[0], 0), dtype=np.float64)
    rank = int(np.sum(singular_values > tolerance * max(float(singular_values[0]), 1e-15)))
    return U[:, :rank]


def project_target(target: Array, basis: Array) -> tuple[Array, Array]:
    flat = target.reshape(-1)
    reconstruction = basis @ (basis.T @ flat) if basis.shape[1] else np.zeros_like(flat)
    residual = flat - reconstruction
    return reconstruction.reshape(target.shape), residual.reshape(target.shape)


def build_tree(height: int, width: int, max_depth: int = 3) -> TreeNode:
    def create(region: Region) -> TreeNode:
        node = TreeNode(region)
        if region.depth < max_depth and region.height >= 4 and region.width >= 4:
            node.children = [create(child) for child in split_region(region) if child.height >= 2 and child.width >= 2]
        return node
    return create(Region(0, 0, height, width, 0, 'tree'))


def fill_tree_models(node: TreeNode, residual: Array, max_rank: int = 3) -> None:
    node.models = local_models(residual, node.region, max_rank=max_rank)
    for child in node.children:
        fill_tree_models(child, residual, max_rank=max_rank)


def prune_frontier(states: Sequence[ParetoState], parameter_budget: int, tolerance: float = 1e-12) -> list[ParetoState]:
    """Keep one best state per cost and remove every cost-error dominated state."""
    best_by_cost: dict[int, ParetoState] = {}
    for state in states:
        cost = int(state.parameter_count)
        if cost < 0 or cost > parameter_budget:
            continue
        current = best_by_cost.get(cost)
        if current is None or state.error_squared < current.error_squared - tolerance:
            best_by_cost[cost] = state
    frontier: list[ParetoState] = []
    best_error = math.inf
    for cost in sorted(best_by_cost):
        state = best_by_cost[cost]
        if state.error_squared < best_error - tolerance:
            frontier.append(state)
            best_error = state.error_squared
    return frontier


def merge_frontiers(left: Sequence[ParetoState], right: Sequence[ParetoState], parameter_budget: int) -> list[ParetoState]:
    combined: list[ParetoState] = []
    for a in left:
        remaining = parameter_budget - a.parameter_count
        if remaining < 0:
            continue
        for b in right:
            cost = a.parameter_count + b.parameter_count
            if cost > parameter_budget:
                break
            combined.append(
                ParetoState(
                    parameter_count=cost,
                    error_squared=a.error_squared + b.error_squared,
                    selections=a.selections + b.selections,
                )
            )
    return prune_frontier(combined, parameter_budget)


def exact_tree_frontier(node: TreeNode, parameter_budget: int) -> list[ParetoState]:
    """Exact Pareto frontier for the declared additive tree model.

    The local model costs and squared errors are additive across disjoint terminal
    regions. The recursion therefore enumerates every admissible keep-or-split
    pruning without enumerating them one by one.
    """
    keep = [
        ParetoState(
            parameter_count=model.parameter_count,
            error_squared=model.error_squared,
            selections=[TreeSelection(node.region, model)],
        )
        for model in node.models
        if model.parameter_count <= parameter_budget
    ]
    if not node.children:
        return prune_frontier(keep, parameter_budget)
    split: list[ParetoState] = [ParetoState(0, 0.0, [])]
    for child in node.children:
        child_frontier = exact_tree_frontier(child, parameter_budget)
        split = merge_frontiers(split, child_frontier, parameter_budget)
        if not split:
            break
    return prune_frontier(keep + split, parameter_budget)


def best_budget_state(frontier: Sequence[ParetoState], parameter_budget: int) -> ParetoState | None:
    candidates = [state for state in frontier if state.parameter_count <= parameter_budget]
    if not candidates:
        return None
    return min(candidates, key=lambda state: (state.error_squared, state.parameter_count))


def solve_tree(node: TreeNode, rate_lambda: float) -> tuple[float, int, list[TreeSelection]]:
    if not node.models:
        keep_cost = math.inf
        keep_params = 0
        keep_selection: list[TreeSelection] = []
    else:
        best_model = min(node.models, key=lambda model: model.error_squared + rate_lambda * model.parameter_count)
        keep_cost = best_model.error_squared + rate_lambda * best_model.parameter_count
        keep_params = best_model.parameter_count
        keep_selection = [TreeSelection(node.region, best_model)]
    if not node.children:
        return keep_cost, keep_params, keep_selection
    child_results = [solve_tree(child, rate_lambda) for child in node.children]
    split_cost = sum(item[0] for item in child_results)
    split_params = sum(item[1] for item in child_results)
    split_selection = [selection for item in child_results for selection in item[2]]
    if split_cost < keep_cost:
        return split_cost, split_params, split_selection
    return keep_cost, keep_params, keep_selection


def tree_candidates(root: TreeNode, parameter_budget: int) -> list[tuple[int, list[TreeSelection]]]:
    frontier = exact_tree_frontier(root, parameter_budget)
    return [(state.parameter_count, state.selections) for state in frontier]


def tree_result(image: Array, core_result: atlas.ReconstructionResult, parameter_budget: int, max_depth: int = 3, max_rank: int = 3) -> AMResult:
    value = atlas.ensure_image(image)
    core_basis = spd.core_channel_basis(core_result.active_atoms, value.shape[2])
    _, core_residual = project_target(value, core_basis)
    root = build_tree(value.shape[0], value.shape[1], max_depth=max_depth)
    fill_tree_models(root, core_residual, max_rank=max_rank)
    best: AMResult | None = None
    for params, selection in tree_candidates(root, parameter_budget):
        raw = [direction for item in selection for direction in item.model.directions]
        Q = complement_basis(raw, core_basis)
        basis = np.column_stack([core_basis, Q]) if Q.shape[1] else core_basis
        reconstruction, residual = project_target(value, basis)
        exact_params = sum(item.model.parameter_count for item in selection)
        result = AMResult(reconstruction, residual, [Q[:, i].reshape(value.shape) for i in range(Q.shape[1])], exact_params, [float(np.linalg.norm(core_residual)), float(np.linalg.norm(residual))], [], selection)
        if best is None or np.linalg.norm(result.residual) < np.linalg.norm(best.residual):
            best = result
    if best is None:
        reconstruction, residual = project_target(value, core_basis)
        best = AMResult(reconstruction, residual, [], 0, [float(np.linalg.norm(residual))], [], [])
    return best


def adaptive_block_search(
    image: Array,
    core_result: atlas.ReconstructionResult,
    parameter_budget: int,
    initial_directions: Sequence[Array],
    initial_parameters: int,
    max_actions: int = 16,
    max_rank: int = 3,
    max_regions_per_iteration: int = 24,
    complexity_exponent: float = 0.78,
) -> AMResult:
    value = atlas.ensure_image(image)
    h, w, channels = value.shape
    core_basis = spd.core_channel_basis(core_result.active_atoms, channels)
    initial_Q = complement_basis(initial_directions, core_basis)
    basis = np.column_stack([core_basis, initial_Q]) if initial_Q.shape[1] else core_basis
    reconstruction, residual = project_target(value, basis)
    parameters = int(initial_parameters)
    directions = [initial_Q[:, i].reshape(value.shape) for i in range(initial_Q.shape[1])]
    residual_norms = [float(np.linalg.norm(residual))]
    blocks: list[BlockSelection] = []
    fixed_regions = unique_regions(dyadic_regions(h, w, max_depth=4) + packet_regions(core_result, h, w), h, w)
    selected_regions: list[Region] = []

    for iteration in range(1, max_actions + 1):
        dynamic = residual_regions(residual, max_components=10)
        descendants = [child for region in selected_regions[-4:] for child in perturb_regions(region, h, w)]
        region_pool = unique_regions(fixed_regions + dynamic + descendants, h, w)
        scored_regions = sorted(region_pool, key=lambda region: float(np.sum(residual[region.y0:region.y1, region.x0:region.x1] ** 2)), reverse=True)
        candidates: list[tuple[float, float, int, Region, LocalModel, Array]] = []
        for region in scored_regions[:max_regions_per_iteration]:
            for model in local_models(residual, region, max_rank=max_rank):
                cost = model.parameter_count
                if parameters + cost > parameter_budget:
                    continue
                Q = complement_basis(model.directions, basis)
                if Q.shape[1] == 0:
                    continue
                gain = float(np.sum((Q.T @ residual.reshape(-1)) ** 2))
                if gain <= 1e-14:
                    continue
                score = gain / (max(cost, 1) ** complexity_exponent)
                candidates.append((score, gain, cost, region, model, Q))
        if not candidates:
            break
        score, gain, cost, region, model, Q = max(candidates, key=lambda item: item[0])
        basis = np.column_stack([basis, Q])
        parameters += cost
        directions.extend(Q[:, i].reshape(value.shape) for i in range(Q.shape[1]))
        reconstruction, residual = project_target(value, basis)
        residual_norms.append(float(np.linalg.norm(residual)))
        blocks.append(BlockSelection(iteration, region, model.orientation, model.rank, cost, gain, score, model.singular_values))
        selected_regions.append(region)
        if parameter_budget - parameters < 10:
            break

    return AMResult(reconstruction, residual, directions, parameters, residual_norms, blocks)
