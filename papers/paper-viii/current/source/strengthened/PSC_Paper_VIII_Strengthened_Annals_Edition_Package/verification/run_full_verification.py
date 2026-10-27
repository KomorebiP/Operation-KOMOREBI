from __future__ import annotations

import itertools
import json
from dataclasses import asdict
from pathlib import Path

import numpy as np

from psc_packet.packet_algorithms import (
    DTypeChoice,
    PacketIR,
    PacketLayout,
    TreeNode,
    assign_discrete_precisions,
    block_banded_block_count,
    block_diagonal_projection,
    circulant_apply_fft,
    circulant_matrix,
    clipped_precision_allocation,
    compile_tree_budget,
    compile_tree_lagrangian,
    kronecker_modewise_apply,
    product_chain_error_bound,
    recompress_factors,
    repeated_recompression_bound,
    schur_fill_support,
    support_power,
    toeplitz_apply_embedding,
    topological_levels,
    walsh_hadamard_transform,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = Path(__file__).with_name("benchmark_results_sanitized.json")


class Audit:
    def __init__(self) -> None:
        self.checks = 0
        self.groups: dict[str, int] = {}
        self.current = ""

    def group(self, name: str) -> None:
        self.current = name
        self.groups.setdefault(name, 0)

    def check(self, condition: bool, message: str) -> None:
        self.checks += 1
        self.groups[self.current] += 1
        if not bool(condition):
            raise AssertionError(f"{self.current}: {message}")


def all_prunings(node: TreeNode):
    yield (node.keep_cost, node.keep_error, (node.name,))
    if node.children:
        child_lists = [list(all_prunings(c)) for c in node.children]
        for choices in itertools.product(*child_lists):
            yield (
                node.split_cost + sum(c[0] for c in choices),
                sum(c[1] for c in choices),
                tuple(x for c in choices for x in c[2]),
            )


def random_tree(rng: np.random.Generator, depth: int, name: str = "r") -> TreeNode:
    keep_cost = float(rng.uniform(0.1, 10.0))
    keep_error = float(rng.uniform(0.0, 3.0))
    if depth == 0 or rng.random() < 0.25:
        return TreeNode(name, keep_cost, keep_error)
    count = int(rng.integers(2, 4))
    return TreeNode(
        name,
        keep_cost,
        keep_error,
        float(rng.uniform(0.0, 1.0)),
        tuple(random_tree(rng, depth - 1, f"{name}{j}") for j in range(count)),
    )


def reachability(n: int, support: set[tuple[int, int]]) -> np.ndarray:
    r = np.eye(n, dtype=bool)
    for target, source in support:
        r[source, target] = True
    for k in range(n):
        r |= r[:, [k]] & r[[k], :]
    return r


def run() -> dict:
    a = Audit()
    rng = np.random.default_rng(20260814)

    a.group("packet semantics")
    for _ in range(450):
        sizes = tuple(int(x) for x in rng.integers(1, 6, size=int(rng.integers(2, 6))))
        layout = PacketLayout(sizes)
        blocks = {}
        for beta in range(len(sizes)):
            for alpha in range(len(sizes)):
                if rng.random() < 0.35:
                    blocks[(beta, alpha)] = rng.normal(size=(sizes[beta], sizes[alpha]))
        ir = PacketIR(layout, blocks)
        x = rng.normal(size=(layout.n, int(rng.integers(1, 6))))
        a.check(np.allclose(ir.apply(x), ir.materialize() @ x), "packet application")
        a.check(np.allclose(ir.adjoint().materialize(), ir.materialize().T), "packet adjoint")
        blocks2 = {}
        for beta in range(len(sizes)):
            for alpha in range(len(sizes)):
                if rng.random() < 0.3:
                    blocks2[(beta, alpha)] = rng.normal(size=(sizes[beta], sizes[alpha]))
        ir2 = PacketIR(layout, blocks2)
        a.check(np.allclose(ir.compose(ir2).materialize(), ir.materialize() @ ir2.materialize()), "packet composition")

    a.group("structured primitives")
    for p in range(1, 61):
        for w in range(p):
            enumerated = sum(abs(i - j) <= w for i in range(p) for j in range(p))
            a.check(block_banded_block_count(p, w) == enumerated, "block band count")
    for n in range(1, 65):
        for _ in range(4):
            c = rng.normal(size=n) + 1j * rng.normal(size=n)
            x = rng.normal(size=n) + 1j * rng.normal(size=n)
            a.check(np.allclose(circulant_apply_fft(c, x), circulant_matrix(c) @ x, atol=2e-10), "circulant FFT")
    for n in range(1, 45):
        for _ in range(3):
            c = rng.normal(size=n)
            row = rng.normal(size=n)
            row[0] = c[0]
            x = rng.normal(size=n)
            t = np.empty((n, n))
            for i in range(n):
                for j in range(n):
                    t[i, j] = c[i - j] if i >= j else row[j - i]
            a.check(np.allclose(toeplitz_apply_embedding(c, row, x), t @ x, atol=2e-10), "Toeplitz embedding")
    for _ in range(400):
        m = int(rng.integers(1, 9))
        n = int(rng.integers(1, 9))
        aa = rng.normal(size=(m, m))
        bb = rng.normal(size=(n, n))
        x = rng.normal(size=(n, m))
        lhs = np.kron(aa, bb) @ x.reshape(-1, order="F")
        rhs = kronecker_modewise_apply(aa, bb, x).reshape(-1, order="F")
        a.check(np.allclose(lhs, rhs), "Kronecker modewise identity")
    for exponent in range(0, 10):
        n = 2**exponent
        for _ in range(30):
            x = rng.normal(size=n)
            y = walsh_hadamard_transform(x)
            a.check(np.allclose(walsh_hadamard_transform(y), n * x), "Hadamard involution")
            a.check(np.isclose(np.linalg.norm(walsh_hadamard_transform(x, normalized=True)), np.linalg.norm(x)), "Hadamard norm")

    a.group("low rank recompression")
    for _ in range(500):
        m = int(rng.integers(2, 28))
        n = int(rng.integers(2, 28))
        r = int(rng.integers(1, 18))
        left = rng.normal(size=(m, r))
        right = rng.normal(size=(n, r))
        if r > 2 and rng.random() < 0.4:
            left[:, -1] = left[:, 0] + left[:, 1]
        if r > 2 and rng.random() < 0.4:
            right[:, -1] = right[:, 0] - right[:, 1]
        matrix = left @ right.T
        singular = np.linalg.svd(matrix, compute_uv=False)
        k = int(rng.integers(0, min(r, min(m, n)) + 1))
        result = recompress_factors(left, right, k)
        error2 = np.linalg.norm(matrix - result.materialize(), 2)
        expected2 = singular[k] if k < singular.size else 0.0
        expectedf = np.linalg.norm(singular[k:])
        a.check(np.isclose(error2, expected2, rtol=2e-8, atol=2e-8), "optimal spectral tail")
        a.check(np.isclose(np.linalg.norm(matrix - result.materialize(), "fro"), expectedf, rtol=2e-8, atol=2e-8), "optimal Frobenius tail")
    for _ in range(600):
        count = int(rng.integers(1, 8))
        exact = [rng.normal(size=(4, 4)) / 4 for _ in range(count)]
        approx = [x + 1e-4 * rng.normal(size=(4, 4)) for x in exact]
        p = np.eye(4)
        ph = np.eye(4)
        for x, y in zip(exact, approx, strict=True):
            p = x @ p
            ph = y @ ph
        a.check(np.linalg.norm(ph - p, 2) <= product_chain_error_bound(exact, approx) + 1e-11, "factor chain error")
        errors = [1e-4 * rng.normal(size=(4, 4)) for _ in range(count)]
        p = np.eye(4)
        ph = np.eye(4)
        for x, e in zip(exact, errors, strict=True):
            p = x @ p
            ph = x @ ph + e
        a.check(np.linalg.norm(ph - p, 2) <= repeated_recompression_bound(exact, errors) + 1e-11, "recompression recurrence")

    a.group("graph support")
    n = 3
    all_edges = [(target, source) for target in range(n) for source in range(n)]
    for mask in range(1 << len(all_edges)):
        support = {edge for i, edge in enumerate(all_edges) if mask & (1 << i)}
        base = np.zeros((n, n), dtype=int)
        for target, source in support:
            base[target, source] = 1
        power = base.copy()
        for exponent in range(1, 5):
            predicted = support_power(support, exponent)
            actual = {(i, j) for i in range(n) for j in range(n) if power[i, j] > 0}
            a.check(predicted == actual, "path support Boolean product")
            power = power @ base
    for _ in range(1200):
        n = int(rng.integers(2, 10))
        support = {(i, i) for i in range(n)}
        for target in range(n):
            for source in range(n):
                if target != source and rng.random() < 0.2:
                    support.add((target, source))
        matrix = np.zeros((n, n))
        for target, source in support:
            matrix[target, source] = rng.normal()
        matrix += (n + 1) * np.eye(n)
        inverse = np.linalg.inv(matrix)
        reach = reachability(n, support)
        for source in range(n):
            for target in range(n):
                if not reach[source, target]:
                    a.check(abs(inverse[target, source]) < 1e-10, "inverse support closure")
    for _ in range(600):
        n = int(rng.integers(4, 10))
        order = list(rng.permutation(n))
        position = {v: i for i, v in enumerate(order)}
        edges = set()
        for u in range(n):
            for v in range(n):
                if position[u] < position[v] and rng.random() < 0.22:
                    edges.add((u, v))
        levels = topological_levels(n, edges)
        level_index = {v: i for i, level in enumerate(levels) for v in level}
        a.check(all(level_index[u] < level_index[v] for u, v in edges), "topological levels")

    a.group("Schur fill")
    for _ in range(500):
        n = 7
        retained = [0, 1, 2]
        hidden = [3, 4, 5, 6]
        support = {(i, i) for i in range(n)}
        for target in range(n):
            for source in range(n):
                if target != source and rng.random() < 0.24:
                    support.add((target, source))
        matrix = np.zeros((n, n))
        for target, source in support:
            matrix[target, source] = rng.normal(scale=0.15)
        matrix += 3.0 * np.eye(n)
        rr = np.ix_(retained, retained)
        rh = np.ix_(retained, hidden)
        hr = np.ix_(hidden, retained)
        hh = np.ix_(hidden, hidden)
        schur = matrix[rr] - matrix[rh] @ np.linalg.inv(matrix[hh]) @ matrix[hr]
        predicted = schur_fill_support(retained, hidden, support)
        for bi, beta in enumerate(retained):
            for ai, alpha in enumerate(retained):
                if abs(schur[bi, ai]) > 1e-10:
                    a.check((beta, alpha) in predicted, "Schur support inclusion")

    a.group("tree compilation")
    for _ in range(350):
        tree = random_tree(rng, 3)
        prunings = list(all_prunings(tree))
        lambdas = [0.0, 0.1, 0.5, 1.0, 3.0, 10.0]
        errors = []
        costs = []
        for lam in lambdas:
            plan = compile_tree_lagrangian(tree, lam)
            brute = min(c + lam * e for c, e, _ in prunings)
            a.check(np.isclose(plan.objective, brute), "Lagrangian tree optimum")
            errors.append(plan.error)
            costs.append(plan.cost)
        a.check(all(errors[i + 1] <= errors[i] + 1e-12 for i in range(len(errors) - 1)), "Lagrangian error monotonicity")
        a.check(all(costs[i + 1] >= costs[i] - 1e-12 for i in range(len(costs) - 1)), "Lagrangian cost monotonicity")
        scale = 0.25
        node_error = {}
        stack = [tree]
        while stack:
            node = stack.pop()
            node_error[node.name] = node.keep_error
            stack.extend(node.children)
        quantized = [
            (c, sum(int(np.ceil(node_error[name] / scale - 1e-14)) for name in leaves))
            for c, _, leaves in prunings
        ]
        budget = int(rng.integers(0, max(w for _, w in quantized) + 1))
        feasible = [c for c, w in quantized if w <= budget]
        plan = compile_tree_budget(tree, budget, scale)
        if feasible:
            a.check(plan is not None and np.isclose(plan.cost, min(feasible)), "budget tree optimum")
        else:
            a.check(plan is None, "budget infeasibility")

    a.group("precision allocation")
    for _ in range(600):
        edge_count = int(rng.integers(1, 7))
        options = []
        for e in range(edge_count):
            options.append([
                DTypeChoice(f"e{e}k{k}", float(rng.uniform(0.1, 5.0)), int(rng.integers(0, 8)))
                for k in range(int(rng.integers(2, 5)))
            ])
        budget = int(rng.integers(0, 20))
        result = assign_discrete_precisions(options, budget)
        brute = []
        for choices in itertools.product(*options):
            weight = sum(c.error_units for c in choices)
            if weight <= budget:
                brute.append((sum(c.cost for c in choices), tuple(c.name for c in choices)))
        if brute:
            best = min(brute, key=lambda x: (x[0], x[1]))
            a.check(result is not None and np.isclose(result[0], best[0]), "discrete precision optimum")
        else:
            a.check(result is None, "discrete precision infeasibility")

        m = int(rng.integers(1, 10))
        sens = rng.uniform(0.1, 5.0, size=m)
        costs = rng.uniform(0.1, 5.0, size=m)
        maxima = rng.uniform(0.01, 0.4, size=m)
        tolerance = float(rng.uniform(0.02, 1.0) * np.dot(sens, maxima))
        eps = clipped_precision_allocation(sens, costs, tolerance, maxima)
        a.check(np.all(eps > 0) and np.all(eps <= maxima + 1e-10), "clipped allocation bounds")
        a.check(np.isclose(np.dot(sens, eps), tolerance, rtol=1e-8, atol=1e-8), "clipped allocation budget")
        free = eps < maxima - 1e-8
        if np.count_nonzero(free) >= 2:
            multipliers = costs[free] / (sens[free] * eps[free])
            a.check(np.max(multipliers) - np.min(multipliers) < 1e-6 * max(1.0, np.max(multipliers)), "clipped KKT multiplier")

    a.group("benchmark corpus")
    data = json.loads(CORPUS.read_text())
    rows = data["results"]
    a.check(len(rows) == 154, "row count")
    a.check(len({r["suite"] for r in rows}) == 16, "suite count")
    a.check(sum(r["device"] == "CPU" for r in rows) == 74, "CPU rows")
    a.check(sum(r["device"] != "CPU" for r in rows) == 80, "GPU rows")
    for row in rows:
        a.check(row["status"] == "measured", "measured status")
        a.check(bool(row["case_id"]), "case identifier")
        a.check(bool(row["output_contract"]), "output contract")
        a.check(bool(row["timing_scope"]), "timing scope")
        if row.get("relative_error") is not None:
            a.check(float(row["relative_error"]) < 3e-3, "relative error ceiling")

    def find(case: str, method: str):
        matches = [r for r in rows if r["case_id"] == case and r["method"] == method]
        a.check(len(matches) == 1, f"unique row {case} {method}")
        return matches[0]

    row = find("block_diagonal_matmat|b=64|n=8192|rhs=32|seed=20260711", "gpu_packet_torch_bmm")
    for key, value in {
        "median_ms": 0.046032,
        "speedup_vs_gpu_dense": 14.891901,
        "speedup_vs_cpu_dense": 235.740353,
        "relative_error": 8.168825e-08,
    }.items():
        a.check(np.isclose(float(row[key]), value, rtol=2e-7, atol=2e-10), f"block row {key}")
    row = find("bdlr_matmat|b=64|n=8192|r=8|rhs=32|seed=20260711", "gpu_packet_cuda_graph")
    for key, value in {
        "median_ms": 0.079872,
        "speedup_vs_gpu_dense": 10.935498,
        "speedup_vs_cpu_dense": 153.652725,
    }.items():
        a.check(np.isclose(float(row[key]), value, rtol=2e-7, atol=2e-10), f"BDLR row {key}")

    a.group("source integrity")
    tex = (ROOT / "PSC_Paper_VIII_Strengthened_Annals_Edition.tex").read_text()
    a.check(";" not in tex, "source semicolon")
    a.check("\\begin{proof}" in tex, "proof environments")
    labels = []
    import re
    labels = re.findall(r"\\label\{([^}]+)\}", tex)
    a.check(len(labels) == len(set(labels)), "unique labels")
    refs = []
    for match in re.finditer(r"\\(?:cref|Cref|ref|eqref)\{([^}]+)\}", tex):
        refs.extend(x.strip() for x in match.group(1).split(","))
    a.check(not (set(refs) - set(labels)), "reference closure")
    for figure in re.findall(r"\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}", tex):
        a.check((ROOT / "figures" / figure).exists(), f"figure exists {figure}")

    return {"checks": a.checks, "groups": a.groups, "status": "passed"}


if __name__ == "__main__":
    result = run()
    Path(__file__).with_name("full_verification.json").write_text(json.dumps(result, indent=2) + "\n")
    lines = [f"Paper VIII full verification: {result['checks']}/{result['checks']} checks passed in {len(result['groups'])} groups"]
    lines += [f"{name}: {count}" for name, count in result["groups"].items()]
    text = "\n".join(lines) + "\n"
    Path(__file__).with_name("full_verification_summary.txt").write_text(text)
    print(text, end="")
