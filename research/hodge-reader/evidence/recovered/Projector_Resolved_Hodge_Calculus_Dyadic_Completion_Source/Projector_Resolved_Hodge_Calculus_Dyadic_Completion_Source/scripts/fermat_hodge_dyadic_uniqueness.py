from __future__ import annotations

import argparse
import itertools
import json
import math
import random
import subprocess
import sys
import tempfile
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Iterable


def units_half(m: int) -> list[int]:
    return [u for u in range(1, m // 2) if math.gcd(u, m) == 1]


def lpr(x: int, m: int) -> int:
    r = x % m
    return m if r == 0 else r


def rho(x: int, m: int) -> int:
    return lpr(x, m) - m // 2


def balanced(t: tuple[int, ...], m: int) -> bool:
    target = (len(t) // 2) * m
    return all(sum(lpr(u * a, m) for a in t) == target for u in units_half(m))


def full_conductor(t: tuple[int, ...], m: int) -> bool:
    g = m
    for a in t:
        g = math.gcd(g, a)
    return g == 1


def paired(t: tuple[int, ...], m: int) -> bool:
    c = Counter(t)
    for a in range(1, m):
        if 2 * a == m:
            if c[a] % 2:
                return False
        elif c[a] != c[m - a]:
            return False
    return True


def canonical_unit(t: tuple[int, ...], m: int) -> tuple[int, ...]:
    return min(
        tuple(sorted(lpr(u * a, m) for a in t))
        for u in range(1, m)
        if math.gcd(u, m) == 1
    )


def defect(t: tuple[int, ...], m: int) -> dict[int, int]:
    h = m // 2
    d: Counter[int] = Counter()
    for a in t:
        if a == h:
            continue
        if a < h:
            d[a] += 1
        else:
            d[m - a] -= 1
    return {r: v for r, v in d.items() if v}


def reduced_multiset(d: dict[int, int], m: int) -> tuple[int, ...]:
    out: list[int] = []
    for r, v in sorted(d.items()):
        if v > 0:
            out.extend([r] * v)
        elif v < 0:
            out.extend([m - r] * (-v))
    return tuple(sorted(out))


def kappa(m: int, b: int) -> dict[int, int]:
    h = m // 2
    out: Counter[int] = Counter()

    def add_oriented(a: int, c: int) -> None:
        a %= m
        if a == 0 or a == h:
            return
        if a < h:
            out[a] += c
        else:
            out[m - a] -= c

    add_oriented(2 * b, 1)
    add_oriented(b, -1)
    add_oriented(h - b, 1)
    return {r: v for r, v in out.items() if v}


def add_defects(*parts: dict[int, int]) -> dict[int, int]:
    out: Counter[int] = Counter()
    for part in parts:
        out.update(part)
    return {r: v for r, v in out.items() if v}


def scale_defect(part: dict[int, int], c: int) -> dict[int, int]:
    return {r: c * v for r, v in part.items() if c * v}


def dyadic_tree(m: int) -> dict:
    if m < 8 or m & (m - 1):
        raise ValueError("m must be a power of two with m >= 8")
    q = m // 4
    root = q // 2
    parent: dict[int, int] = {}
    edge_sign: dict[int, int] = {}
    children: dict[int, list[int]] = defaultdict(list)
    for b in range(1, q):
        if b == root:
            continue
        if b < root:
            p, sign = 2 * b, 1
        else:
            p, sign = 2 * (q - b), -1
        parent[b] = p
        edge_sign[b] = sign
        children[p].append(b)

    gauge = {root: 1}
    queue = deque([root])
    while queue:
        p = queue.popleft()
        for b in sorted(children[p]):
            gauge[b] = edge_sign[b] * gauge[p]
            queue.append(b)

    adjacency = {b: set(children[b]) for b in range(1, q)}
    for b, p in parent.items():
        adjacency[b].add(p)
        adjacency[p].add(b)

    return {
        "q": q,
        "root": root,
        "parent": parent,
        "edge_sign": edge_sign,
        "children": children,
        "gauge": gauge,
        "adjacency": adjacency,
    }


def coefficients_from_defect(d: dict[int, int], m: int) -> tuple[dict[int, int], dict[int, int]]:
    tree = dyadic_tree(m)
    root = tree["root"]
    children = tree["children"]
    edge_sign = tree["edge_sign"]
    gauge = tree["gauge"]

    z = {root: d.get(2 * root, 0)}
    queue = deque([root])
    while queue:
        p = queue.popleft()
        for b in children[p]:
            z[b] = d.get(2 * b, 0) + edge_sign[b] * z[p]
            queue.append(b)

    y = {b: gauge[b] * value for b, value in z.items() if value}

    rebuilt: Counter[int] = Counter()
    for b, value in z.items():
        if value:
            for r, c in kappa(m, b).items():
                rebuilt[r] += value * c
    rebuilt_clean = {r: v for r, v in rebuilt.items() if v}
    if rebuilt_clean != d:
        raise AssertionError("defect is not in the dyadic balanced lattice")
    return z, y


def tree_variation(y: dict[int, int], m: int) -> int:
    tree = dyadic_tree(m)
    q = tree["q"]
    root = tree["root"]
    parent = tree["parent"]
    values = {b: y.get(b, 0) for b in range(1, q)}
    total = abs(values[root])
    total += sum(abs(values[b] - values[p]) for b, p in parent.items())
    total += 2 * sum(abs(values[b]) for b in range(1, q, 2))
    return total


def low_variation_type(y: dict[int, int], m: int) -> dict:
    tree = dyadic_tree(m)
    adjacency = tree["adjacency"]
    nz = {b: v for b, v in y.items() if v}
    if not nz:
        return {"kind": "zero"}
    if len(nz) == 1 and abs(next(iter(nz.values()))) == 2:
        return {"kind": "double_single", "vertex": next(iter(nz))}
    if not all(abs(v) == 1 for v in nz.values()):
        return {"kind": "forbidden", "values": sorted(nz.items())}

    components: list[tuple[int, set[int]]] = []
    seen: set[int] = set()
    for start, sign in nz.items():
        if start in seen:
            continue
        comp = {start}
        seen.add(start)
        queue = [start]
        while queue:
            v = queue.pop()
            for w in adjacency[v]:
                if w in nz and nz[w] == sign and w not in seen:
                    seen.add(w)
                    comp.add(w)
                    queue.append(w)
        components.append((sign, comp))

    if len(components) == 2 and all(len(comp) == 1 for _, comp in components):
        return {
            "kind": "two_singles",
            "vertices": sorted(next(iter(comp)) for _, comp in components),
        }
    if len(components) != 1:
        return {"kind": "forbidden", "components": [sorted(c) for _, c in components]}

    sign, support = components[0]
    degrees = {v: sum(w in support for w in adjacency[v]) for v in support}
    if len(support) == 4 and sorted(degrees.values()) == [1, 1, 1, 3]:
        center = next(v for v, degree in degrees.items() if degree == 3)
        return {"kind": "star4", "sign": sign, "center": center, "support": sorted(support)}
    return {
        "kind": f"connected_{len(support)}",
        "sign": sign,
        "support": sorted(support),
        "degrees": sorted(degrees.values()),
    }


def sat2_tree_prediction(t: tuple[int, ...], m: int) -> tuple[bool, dict]:
    d = defect(t, m)
    _, y = coefficients_from_defect(d, m)
    variation = tree_variation(y, m)
    if variation != sum(abs(v) for v in d.values()):
        raise AssertionError("tree variation does not equal defect mass")
    classification = low_variation_type(y, m)
    return classification["kind"] != "star4", classification


def exact_sat2(t: tuple[int, ...], m: int, balanced_four: set[tuple[int, ...]]) -> bool:
    ct = Counter(t)
    for r in range(1, m // 2 + 1):
        total = ct + Counter((r, m - r))
        items = sorted(total.items())
        chosen: list[int] = []

        def subsets(i: int, remaining: int) -> Iterable[tuple[int, ...]]:
            if remaining == 0:
                yield tuple(chosen)
                return
            if i == len(items):
                return
            value, count = items[i]
            for take in range(min(count, remaining) + 1):
                chosen.extend([value] * take)
                yield from subsets(i + 1, remaining - take)
                if take:
                    del chosen[-take:]

        for gamma in subsets(0, 4):
            if gamma not in balanced_four:
                continue
            remainder = total - Counter(gamma)
            if sum(remainder.values()) != 4:
                continue
            other = tuple(sorted(remainder.elements()))
            if other in balanced_four:
                return True
    return False


def balanced_packets_mitm(m: int, length: int) -> list[tuple[int, ...]]:
    if length not in (4, 6):
        raise ValueError("only lengths four and six are supported")
    units = units_half(m)
    half_length = length // 2
    values = range(1, m)

    p1 = 2_305_843_009_213_693_951
    p2 = 2_305_843_009_213_693_921
    rng = random.Random(12_345 + m + length)
    coeff1 = [rng.randrange(1, p1) for _ in units]
    coeff2 = [rng.randrange(1, p2) for _ in units]

    hashes: dict[int, tuple[int, int]] = {}
    for a in values:
        vector = [lpr(u * a, m) for u in units]
        hashes[a] = (
            sum(c * x for c, x in zip(coeff1, vector)) % p1,
            sum(c * x for c, x in zip(coeff2, vector)) % p2,
        )

    target_vector = [(length // 2) * m] * len(units)
    target_hash = (
        sum(c * x for c, x in zip(coeff1, target_vector)) % p1,
        sum(c * x for c, x in zip(coeff2, target_vector)) % p2,
    )

    groups: dict[tuple[int, int], list[tuple[int, ...]]] = defaultdict(list)
    blocks = list(itertools.combinations_with_replacement(values, half_length))
    for block in blocks:
        key = (
            sum(hashes[a][0] for a in block) % p1,
            sum(hashes[a][1] for a in block) % p2,
        )
        groups[key].append(block)

    out: set[tuple[int, ...]] = set()
    target_sum = (length // 2) * m
    for block in blocks:
        key = (
            sum(hashes[a][0] for a in block) % p1,
            sum(hashes[a][1] for a in block) % p2,
        )
        complement = ((target_hash[0] - key[0]) % p1, (target_hash[1] - key[1]) % p2)
        for other in groups.get(complement, ()):
            packet = tuple(sorted(block + other))
            if sum(packet) == target_sum and balanced(packet, m):
                out.add(packet)
    return sorted(out)


def expected_residual(m: int) -> tuple[int, ...]:
    return tuple(
        sorted(
            (
                1,
                m // 4 + 1,
                m // 2 + 1,
                m // 2 + 4,
                3 * m // 4 + 1,
                m - 8,
            )
        )
    )


def sat3_identity(m: int) -> tuple[tuple[int, ...], tuple[int, ...]]:
    a = expected_residual(m)
    left = tuple(sorted(a + (2, m - 2) + (4, m - 4) + (m // 2, m // 2)))
    right = tuple(
        sorted(
            (1, m // 2, m // 2 + 1, m - 2)
            + (2, m // 4 + 1, 3 * m // 4 + 1, m - 4)
            + (4, m // 2, m // 2 + 4, m - 8)
        )
    )
    return left, right


def valuation_two(a: int) -> int:
    value = 0
    while a and a % 2 == 0:
        value += 1
        a //= 2
    return value


def symbolic_checks(max_s: int) -> dict:
    checks: dict[str, bool] = {}
    star_data: dict[str, dict] = {}
    for s in range(3, max_s + 1):
        m = 2**s
        q = m // 4
        h = m // 2
        tree = dyadic_tree(m)

        triangle_ok = all(
            rho(2 * u * b, m) - rho(u * b, m) + rho(u * (h - b), m) == 0
            for b in range(1, q)
            for u in units_half(m)
        )
        checks[f"m{m}_triangle_identity"] = triangle_ok

        # The root/edge recovery map is unimodular because coefficients are
        # recovered recursively from the root to every child.
        reached = {tree["root"]}
        queue = deque([tree["root"]])
        while queue:
            p = queue.popleft()
            for b in tree["children"][p]:
                reached.add(b)
                queue.append(b)
        checks[f"m{m}_tree_connected"] = reached == set(range(1, q))
        checks[f"m{m}_tree_edge_count"] = len(tree["parent"]) == q - 2

        if s >= 5:
            a = expected_residual(m)
            left, right = sat3_identity(m)
            checks[f"m{m}_A_balanced"] = balanced(a, m)
            checks[f"m{m}_A_full_conductor"] = full_conductor(a, m)
            checks[f"m{m}_sat3_multiset_identity"] = left == right
            checks[f"m{m}_sat3_right_packets_balanced"] = all(
                balanced(gamma, m)
                for gamma in (
                    (1, m // 2, m // 2 + 1, m - 2),
                    (2, m // 4 + 1, 3 * m // 4 + 1, m - 4),
                    (4, m // 2, m // 2 + 4, m - 8),
                )
            )

            full_star_canonicals = set()
            gcd_rule = True
            star_packet_formula = True
            for center, neighbors in tree["adjacency"].items():
                if len(neighbors) != 3:
                    continue
                support = {center, *neighbors}
                d = Counter()
                for b in support:
                    z = tree["gauge"][b]
                    for r, c in kappa(m, b).items():
                        d[r] += z * c
                clean = {r: v for r, v in d.items() if v}
                g = m
                for r in clean:
                    g = math.gcd(g, r)
                gcd_rule &= g == 2 ** (valuation_two(center) - 1)
                packet = reduced_multiset(clean, m)
                if valuation_two(center) == 1:
                    a_center = center // 2
                    formula = tuple(
                        sorted(
                            (
                                8 * a_center,
                                q - a_center,
                                2 * q - a_center,
                                2 * q - 4 * a_center,
                                3 * q - a_center,
                                4 * q - a_center,
                            )
                        )
                    )
                    formula_conjugate = tuple(sorted(lpr(-x, m) for x in formula))
                    star_packet_formula &= packet in {formula, formula_conjugate}
                if g == 1:
                    odd_part = center // 2
                    u = pow(odd_part, -1, h)
                    image = tuple(sorted(lpr(u * x, m) for x in packet))
                    conjugate_image = tuple(sorted(lpr(-u * x, m) for x in packet))
                    if image == a or conjugate_image == a:
                        full_star_canonicals.add(a)
                    else:
                        full_star_canonicals.add(min(image, conjugate_image))
            checks[f"m{m}_star_conductor_rule"] = gcd_rule
            checks[f"m{m}_star_packet_formula"] = star_packet_formula
            checks[f"m{m}_unique_full_star_orbit"] = full_star_canonicals == {a}
            star_data[str(m)] = {
                "full_star_orbit_count": len(full_star_canonicals),
                "canonical_packet": list(next(iter(full_star_canonicals))) if full_star_canonicals else None,
            }

    return {"checks": checks, "star_data": star_data, "passed": all(checks.values())}


def exhaustive_checks(max_m: int) -> dict:
    degrees = [m for m in (8, 16, 32, 64, 128) if m <= max_m]
    result: dict[str, dict] = {}
    all_passed = True
    for m in degrees:
        balanced_four = balanced_packets_mitm(m, 4)
        balanced_six = balanced_packets_mitm(m, 6)
        four_set = set(balanced_four)
        representatives = sorted(
            {canonical_unit(t, m) for t in balanced_six if full_conductor(t, m)}
        )

        counts = Counter()
        mismatches = []
        residuals = []
        for packet in representatives:
            tree_sat2, classification = sat2_tree_prediction(packet, m)
            if paired(packet, m):
                exact_closed = True
                counts["pair"] += 1
            else:
                exact_closed = exact_sat2(packet, m, four_set)
                counts["sat2" if exact_closed else "star"] += 1
            counts[classification["kind"]] += 1
            if tree_sat2 != exact_closed:
                mismatches.append(
                    {
                        "packet": list(packet),
                        "tree_classification": classification,
                        "exact_closed": exact_closed,
                    }
                )
            if not exact_closed:
                residuals.append(packet)

        expected = [] if m < 32 else [expected_residual(m)]
        degree_passed = not mismatches and residuals == expected
        all_passed &= degree_passed
        result[str(m)] = {
            "balanced_four_count": len(balanced_four),
            "balanced_six_count": len(balanced_six),
            "full_conductor_orbits": len(representatives),
            "pair": counts["pair"],
            "sat2": counts["sat2"],
            "star": counts["star"],
            "tree_types": {
                key: value
                for key, value in sorted(counts.items())
                if key not in {"pair", "sat2", "star"}
            },
            "residuals": [list(t) for t in residuals],
            "mismatches": mismatches,
            "passed": degree_passed,
        }
    return {"degrees": result, "passed": all_passed}


def audit(max_symbolic_s: int, max_exhaustive_m: int) -> dict:
    # Run the two large audits in fresh interpreters.  This keeps the verifier
    # stable on memory-constrained systems whose Python allocators retain arenas
    # after the MITM and high-modulus symbolic phases.
    script = Path(__file__).resolve()
    with tempfile.TemporaryDirectory(prefix="dyadic_uniqueness_") as tmp:
        tmpdir = Path(tmp)
        exhaustive_path = tmpdir / "exhaustive.json"
        symbolic_path = tmpdir / "symbolic.json"
        print("[dyadic audit] exhaustive packet phase", file=sys.stderr, flush=True)
        subprocess.run(
            [
                sys.executable,
                str(script),
                "--phase",
                "exhaustive",
                "--max-exhaustive-m",
                str(max_exhaustive_m),
                "--out",
                str(exhaustive_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        print("[dyadic audit] symbolic all-degree phase", file=sys.stderr, flush=True)
        subprocess.run(
            [
                sys.executable,
                str(script),
                "--phase",
                "symbolic",
                "--max-symbolic-s",
                str(max_symbolic_s),
                "--out",
                str(symbolic_path),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
        )
        print("[dyadic audit] assembling certificate", file=sys.stderr, flush=True)
        exhaustive = json.loads(exhaustive_path.read_text(encoding="utf-8"))
        symbolic = json.loads(symbolic_path.read_text(encoding="utf-8"))

    return {
        "title": "All-Degree Dyadic Uniqueness Audit",
        "theorem": (
            "Every full-conductor balanced six-packet at modulus 2^s is pair-decomposable "
            "or SAT(2), except for one unit orbit A_m when s>=5; A_m is SAT(3)."
        ),
        "symbolic_max_s": max_symbolic_s,
        "exhaustive_max_m": max_exhaustive_m,
        "symbolic": symbolic,
        "exhaustive": exhaustive,
        "passed": symbolic["passed"] and exhaustive["passed"],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify the all-degree dyadic uniqueness theorem.")
    parser.add_argument("--max-symbolic-s", type=int, default=14)
    parser.add_argument("--max-exhaustive-m", type=int, default=128, choices=(8, 16, 32, 64, 128))
    parser.add_argument("--phase", choices=("all", "symbolic", "exhaustive"), default="all")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("Fermat_Hodge_Dyadic_Uniqueness_VERIFICATION.json"),
    )
    args = parser.parse_args()

    if args.phase == "symbolic":
        data = symbolic_checks(args.max_symbolic_s)
    elif args.phase == "exhaustive":
        data = exhaustive_checks(args.max_exhaustive_m)
    else:
        data = audit(args.max_symbolic_s, args.max_exhaustive_m)

    args.out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps(data, indent=2))
    if not data["passed"]:
        raise SystemExit("dyadic uniqueness verification failed")


if __name__ == "__main__":
    main()
