"""Exact examples for the PR-LASM foundations supplement.

Run: python checks/exact_foundation_checks.py
Requires SymPy. No random inputs, floating-point tolerances, downloads or ARC data.
The output checks finite identities and counterexamples, not general Lean proofs.
"""
from __future__ import annotations

import itertools
import json
import platform
from pathlib import Path
from typing import Sequence

import sympy as sp

Matrix = sp.Matrix
ROOT = Path(__file__).resolve().parents[1]
RESULTS: list[dict[str, object]] = []


def zero(matrix: sp.MatrixBase) -> bool:
    return all(sp.simplify(v) == 0 for v in matrix)


def check(name: str, statement: bool, proposition: str, detail: str = "") -> None:
    if not statement:
        raise AssertionError(f"{name}: {detail}")
    RESULTS.append({"name": name, "proposition": proposition, "passed": True,
                    "scope": detail or "Exact finite example, not a general proof certificate."})


def rows_basis(matrix: sp.MatrixBase) -> sp.MatrixBase:
    rows = matrix.rowspace()
    return Matrix.vstack(*rows) if rows else sp.zeros(0, matrix.cols)


def minimal_linear_closure(
    initial: sp.MatrixBase, operators: Sequence[sp.MatrixBase]
) -> tuple[sp.MatrixBase, list[int], list[sp.MatrixBase]]:
    """Small exact reference algorithm for rational linear operators.

    Returns a row basis R, its dimension trace, and matrices B_u with R L_u=B_u R.
    Intended for small theorem examples, not high-dimensional numeric estimation.
    """
    d = initial.cols
    if d < 1 or any(operator.shape != (d, d) for operator in operators):
        raise ValueError("Initial summary and square operators must share a positive state dimension.")
    if any(not value.is_Rational for matrix in [initial, *operators] for value in matrix):
        raise ValueError("This reference routine accepts exact rational entries only.")
    basis = rows_basis(initial)
    trace = [basis.rows]
    for _ in range(d + 1):
        expanded = Matrix.vstack(basis, *(basis * op for op in operators)) if operators else basis
        next_basis = rows_basis(expanded)
        if next_basis.rows == basis.rows:
            if basis.rows == 0:
                return basis, trace, [sp.zeros(0, 0) for _ in operators]
            right_inverse = basis.T * (basis * basis.T).inv()
            reduced = [basis * op * right_inverse for op in operators]
            if any(not zero(basis * op - small * basis)
                   for op, small in zip(operators, reduced, strict=True)):
                raise ArithmeticError("Exact closure certificate failed.")
            return basis, trace, reduced
        basis = next_basis
        trace.append(basis.rows)
    raise ArithmeticError("Finite-dimensional closure did not stabilize.")


Partition = tuple[tuple[int, ...], ...]


def canonical(groups: Sequence[Sequence[int]]) -> Partition:
    return tuple(sorted((tuple(sorted(group)) for group in groups), key=lambda b: b[0]))


def validate_partition(partition: Partition, n: int) -> None:
    flat = [i for block in partition for i in block]
    if not partition or any(not block for block in partition) or sorted(flat) != list(range(n)):
        raise ValueError("A partition must cover each state exactly once, with nonempty blocks.")


def refines(fine: Partition, coarse: Partition) -> bool:
    return all(any(set(block) <= set(outer) for outer in coarse) for block in fine)


def split_partition(partition: Partition, signatures: Sequence[tuple]) -> Partition:
    groups: list[tuple[int, ...]] = []
    for block in partition:
        buckets: dict[tuple, list[int]] = {}
        for i in block:
            buckets.setdefault(signatures[i], []).append(i)
        groups.extend(tuple(value) for value in buckets.values())
    return canonical(groups)


def coarsest_joint_partition(
    kernels: Sequence[sp.MatrixBase], likelihoods: Sequence[sp.MatrixBase], initial: Partition
) -> tuple[Partition, list[Partition]]:
    """Exact finite prediction/update quotient for known rational kernels.

    At least two mandatory blocks and strictly positive likelihoods are required,
    matching the necessity statement in Proposition 9 rather than its trivial
    one-block exception. All arithmetic is rational and exact.
    """
    if not kernels:
        raise ValueError("Supply at least one known transition kernel.")
    n = kernels[0].rows
    validate_partition(initial, n)
    if len(initial) < 2:
        raise ValueError("The joint-minimality contract requires at least two mandatory blocks.")
    for kernel in kernels:
        if kernel.shape != (n, n) or any(not v.is_Rational or v < 0 for v in kernel):
            raise ValueError("Kernels must be nonnegative rational square matrices of equal size.")
        if any(sum(kernel[i, j] for j in range(n)) != 1 for i in range(n)):
            raise ValueError("Every kernel row must sum to one.")
    for likelihood in likelihoods:
        if likelihood.shape != (n, 1) or any(not v.is_Rational or v <= 0 for v in likelihood):
            raise ValueError("Likelihoods must be strictly positive rational column vectors.")
    part = split_partition(initial, [tuple(l[i] for l in likelihoods) for i in range(n)])
    trace = [part]
    for _ in range(n + 1):
        signatures = [tuple(sum(kernel[i, j] for j in block)
                            for kernel in kernels for block in part) for i in range(n)]
        refined = split_partition(part, signatures)
        if refined == part:
            return part, trace
        part = refined
        trace.append(part)
    raise ArithmeticError("Finite partition refinement did not stabilize.")


def aggregation(partition: Partition, n: int) -> sp.MatrixBase:
    return Matrix([[int(i in block) for i in range(n)] for block in partition])


def quotient_kernel(kernel: sp.MatrixBase, partition: Partition) -> sp.MatrixBase:
    validate_partition(partition, kernel.rows)
    for block in partition:
        signatures = [tuple(sum(kernel[i, j] for j in target) for target in partition) for i in block]
        if any(signature != signatures[0] for signature in signatures[1:]):
            raise ValueError("Partition is not lumpable for this kernel.")
    return Matrix([[sum(kernel[block[0], j] for j in target) for target in partition]
                   for block in partition])


def posterior(prior: sp.MatrixBase, likelihood: sp.MatrixBase) -> sp.MatrixBase:
    numerator = prior.multiply_elementwise(likelihood)
    evidence = sum(numerator)
    if evidence == 0:
        raise ValueError("Bayesian evidence must be positive.")
    return numerator / evidence


def all_partitions(items: tuple[int, ...]):
    if not items:
        yield ()
        return
    head, tail = items[0], items[1:]
    for rest in all_partitions(tail):
        yield canonical(((head,), *rest))
        for i in range(len(rest)):
            yield canonical((*rest[:i], (head, *rest[i]), *rest[i + 1:]))


def main() -> None:
    q = sp.Rational
    I2 = sp.eye(2)
    A = Matrix([[1, 0], [0, 1], [1, 1]])
    S = (A.T * A).inv() * A.T
    Pi = A * S
    check("left inverse", zero(S * A - I2), "1")
    check("redundant consistency projection", zero(Pi * Pi - Pi) and zero(Pi.T - Pi), "1")
    oblique_A = Matrix([[1], [0]])
    oblique_S = Matrix([[1, 1]])
    oblique = oblique_A * oblique_S
    check("left inverse does not imply orthogonality", zero(oblique * oblique - oblique)
          and not zero(oblique.T - oblique), "1", "Exact counterexample to the stronger false claim.")

    U = Matrix([[1, 1], [1, -1]]) / sp.sqrt(2)
    V = Matrix([[q(3, 5), q(-4, 5)], [q(4, 5), q(3, 5)]])
    L = Matrix([[q(1, 2), 1], [q(1, 4), q(1, 3)]])
    F_U, F_V, T = U * L * U.T, V * L * V.T, V * U.T
    check("operator naturality", zero(F_V * T - T * F_U), "2")
    check("transport composition", zero(A * V.T * V * U.T - A * U.T), "2")
    check("independently changed atlas operator is incoherent",
          not zero((F_V + I2) * T - T * F_U), "2", "Exact negative control.")

    I4 = sp.eye(4)
    H4 = Matrix([[1, 1, 1, 1], [1, -1, 1, -1], [1, 1, -1, -1], [1, -1, -1, 1]]) / 2
    nodes = {"": I4, "0": sp.diag(1, 1, 0, 0), "1": sp.diag(0, 0, 1, 1)}
    for index, path in enumerate(["00", "01", "10", "11"]):
        nodes[path] = sp.diag(*[int(i == index) for i in range(4)])
    nodes = {path: H4.T * value * H4 for path, value in nodes.items()}
    prunings = [("",), ("0", "1"), ("00", "01", "1"), ("0", "10", "11"),
                ("00", "01", "10", "11")]
    x4 = Matrix([1, 2, -3, 4])
    for pruning in prunings:
        total = sum((nodes[p] for p in pruning), sp.zeros(4))
        energy = sum((nodes[p] * x4).dot(nodes[p] * x4) for p in pruning)
        check("complete pruning " + str(pruning), zero(total - I4) and energy == x4.dot(x4), "3")
    check("incomplete pruning loses information", not zero(nodes["00"] + nodes["1"] - I4), "3")

    P, Q = sp.diag(1, 0), sp.diag(0, 1)
    M = Matrix([[2, -1], [3, 4]])
    projectors = [P, Q]
    blocks = sum((left * L * right for left in projectors for right in projectors), sp.zeros(2))
    composed = sum((P * M * middle * middle * L * Q for middle in projectors), sp.zeros(2))
    check("transfer block reconstruction", zero(blocks - L), "4")
    check("transfer block composition", zero(composed - P * M * L * Q), "4")
    u, v = sp.symbols("u v")
    check("quadratic cross interaction", sp.expand((u + v)**2 - u**2 - 2*u*v - v**2) == 0, "5")
    check("independent nonlinear packets lose a cross term", sp.expand((u + v)**2 - u**2 - v**2) == 2*u*v, "5")

    x, xp = Matrix([0, 0]), Matrix([0, 1])
    check("equal summaries can have different successors", zero(P*x - P*xp) and not zero(P*L*x - P*L*xp), "6")
    ls = Matrix(2, 2, sp.symbols("l0:4"))
    ms = Matrix(2, 2, sp.symbols("m0:4"))
    check("symbolic compression composition defect", zero(P*ls*ms*P - P*ls*P*ms*P - P*ls*Q*ms*P), "7",
          "Polynomial identity for arbitrary symbolic 2x2 matrices, with this fixed projector.")
    check("two-step return block", (P*L*L*P - P*L*P*L*P)[0, 0] == q(1, 4), "7")
    amplified = Matrix([[0, 1000], [0, 0]]) * Matrix([0, q(1, 1000)])
    check("small energy can matter predictively", amplified[0] == 1, "7")

    L3 = sp.diag(L, q(5, 6))
    C0 = Matrix([[1, 0, 0]])
    R, linear_trace, reduced = minimal_linear_closure(C0, [L3])
    check("minimal closed refinement can omit a coordinate", linear_trace == [1, 2] and R.rows == 2
          and zero(R*L3 - reduced[0]*R), "8")
    La = Matrix([[0, 1, 0], [0, 0, 0], [0, 0, 0]])
    Lb = Matrix([[0, 0, 0], [0, 0, 1], [0, 0, 0]])
    _, switched_trace, _ = minimal_linear_closure(C0, [La, Lb])
    check("action-family closure needs iterated observables", switched_trace == [1, 2, 3], "8")

    K = Matrix([[0, 0, q(1, 2), q(1, 2), 0, 0],
                [0, 0, 0, 0, q(1, 2), q(1, 2)],
                [1, 0, 0, 0, 0, 0], [0, 1, 0, 0, 0, 0],
                [q(1, 4), q(1, 4), 0, 0, q(1, 4), q(1, 4)],
                [q(1, 4), q(1, 4), 0, 0, q(1, 4), q(1, 4)]])
    likelihood = Matrix([1, 1, 2, 2, 3, 3])
    initial = ((0, 1, 2, 3), (4, 5))
    final, partition_trace = coarsest_joint_partition([K, sp.eye(6)], [likelihood], initial)
    expected = ((0,), (1,), (2,), (3,), (4, 5))
    check("joint quotient partition", final == expected and [len(p) for p in partition_trace] == [3, 4, 5], "9")
    Cpi = aggregation(final, 6)
    for index, kernel in enumerate([K, sp.eye(6)]):
        coarse = quotient_kernel(kernel, final)
        check(f"exact stochastic prediction commuting square {index}", zero(Cpi*kernel.T - coarse.T*Cpi), "9")
    p_symbolic = Matrix(sp.symbols("p0:6", positive=True))
    coarse_likelihood = Matrix([likelihood[block[0]] for block in final])
    check("symbolic Bayesian update commuting square", zero(Cpi*posterior(p_symbolic, likelihood)
          - posterior(Cpi*p_symbolic, coarse_likelihood)), "9",
          "Identity of rational functions for arbitrary positive prior weights on this finite model.")
    admissible = []
    candidates = [part for part in all_partitions(tuple(range(6))) if refines(part, initial)]
    for part in candidates:
        if any(len({likelihood[i] for i in block}) != 1 for block in part):
            continue
        try:
            for kernel in [K, sp.eye(6)]:
                quotient_kernel(kernel, part)
        except ValueError:
            continue
        admissible.append(part)
    check("finite exhaustive joint minimality", len(candidates) == 30 and bool(admissible)
          and all(refines(part, final) for part in admissible), "9",
          f"All {len(candidates)} partitions refining the mandatory partition were checked; {len(admissible)} are admissible.")

    trajectory = [Matrix([1, 0])]
    for _ in range(10):
        trajectory.append(L*trajectory[-1])
    a, b, c, d = q(1, 2), sp.Integer(1), q(1, 4), q(1, 3)
    for q0 in [0, q(2, 7)]:
        states = [Matrix([1, q0])]
        for _ in range(10):
            states.append(L*states[-1])
        for t in range(10):
            memory = a*states[t][0] + sum(b*d**k*c*states[t-1-k][0] for k in range(t)) + b*d**t*q0
            check(f"exact memory q0={q0} t={t}", sp.simplify(memory - states[t+1][0]) == 0, "10")
    check("worked signal sequence", [state[0] for state in trajectory[:4]] == [1, q(1, 2), q(1, 2), q(11, 24)], "10")
    t, H = 8, 2
    omitted = sum(b*d**k*c*trajectory[t-1-k][0] for k in range(H, t))
    Z = max(abs(trajectory[s][0]) for s in range(t))
    bound = abs(b*c)*Z*d**H/(1-d)
    check("memory tail bound on fixed exact history", abs(omitted) <= bound, "10")

    target = [0, 2, 1, 5]
    coarse_mean = q(sum(target), 4)
    fine_mean = [1, 1, 3, 3]
    coarse_risk = sum((y-coarse_mean)**2 for y in target)/4
    fine_risk = sum((y-m)**2 for y, m in zip(target, fine_mean, strict=True))/sp.Integer(4)
    gain = sum((m-coarse_mean)**2 for m in fine_mean)/4
    check("nested conditional mean risk identity", sp.simplify(coarse_risk - fine_risk - gain) == 0, "11")

    prior = Matrix([q(1, 10), q(2, 10), q(3, 10), q(4, 10)])
    fine_l = Matrix([1, 4, 2, 3])
    Ca = aggregation(((0, 1), (2, 3)), 4)
    Pc = Ca*prior
    effective = Matrix([(sum(prior[i]*fine_l[i] for i in block))/Pc[a]
                        for a, block in enumerate(((0, 1), (2, 3)))])
    declared = Matrix([2, 2])
    bar_b = posterior(Pc, declared)
    delta = effective - declared
    defect = (sp.diag(*Pc) - bar_b*Pc.T)*delta/(effective.dot(Pc))
    actual = Ca*posterior(prior, fine_l) - bar_b
    check("Bayesian information loss factorization", zero(actual-defect) and actual == Matrix([q(1, 30), q(-1, 30)]), "12")
    check("common likelihood scale is annihilated", zero((sp.diag(*Pc)-bar_b*Pc.T)*declared), "12")
    Csingle = sp.ones(1, 4)
    check("one-block necessity exception", Csingle*posterior(prior, fine_l) == Matrix([1])
          and len(set(fine_l)) > 1, "12")

    for n in range(1, 6):
        Pn = sp.diag(*([1]*n + [0]*(6-n)))
        witness = sp.eye(6)[:, n]
        check(f"strong versus uniform norm witness n={n}", ((sp.eye(6)-Pn)*witness).dot((sp.eye(6)-Pn)*witness) == 1, "13",
              "Finite witness for the coordinate-projection norm obstruction; the infinite statement is proved in prose.")

    report = {"supplement": "0.1.0", "software_predecessor": "2.3.0", "status": "PASS",
              "arithmetic": "exact rational and symbolic SymPy expressions", "sympy": sp.__version__,
              "python": platform.python_version(), "checks_passed": len(RESULTS),
              "lean_kernel_verification": False, "core_software_modified": False,
              "general_proofs": "theory/FOUNDATIONS.md", "linear_closure_dimension_trace": linear_trace,
              "switched_closure_dimension_trace": switched_trace,
              "joint_partition_trace": partition_trace, "joint_coarse_kernel":
                  [[str(v) for v in row] for row in quotient_kernel(K, final).tolist()],
              "checks": RESULTS}
    destination = ROOT / "verification" / "exact_checks.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"PASS: {len(RESULTS)} exact example/identity checks. No general proof-kernel claim.")
    print(f"Linear closure dimensions: {linear_trace}; switched closure: {switched_trace}")
    print(f"Joint finite partition block counts: {[len(p) for p in partition_trace]}")
    print(destination)


if __name__ == "__main__":
    main()
