#!/usr/bin/env python3
"""Independent exact primal/dual sanity checks on every Boolean function at n<=3.

This finite check is not the proof of the universal evaluation-span theorem.
Run from the publication directory as:
  python scripts/core_dual_checks.py --output reviews/core_dual_checks.json
"""
import argparse
import json
from pathlib import Path


def anf_degree(function, n):
    coefficients = [(function >> x) & 1 for x in range(1 << n)]
    for i in range(n):
        for x in range(1 << n):
            if (x >> i) & 1:
                coefficients[x] ^= coefficients[x ^ (1 << i)]
    return max((s.bit_count() for s, c in enumerate(coefficients) if c), default=-1)


def span_contains(rows, vector):
    basis = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in basis:
                row ^= basis[pivot]
            else:
                basis[pivot] = row
                break
    while vector:
        pivot = vector.bit_length() - 1
        if pivot not in basis:
            return False
        vector ^= basis[pivot]
    return True


def check():
    result = {
        "status": "PASS",
        "arithmetic": "exact F2",
        "range": "all truth tables on n=0,1,2,3; all positive v; d=0..n",
        "assertions": [
            "beta_v(f)>d iff v_d(v) belongs to the negative evaluation span",
            "betaStar(f)<=n for every tested function",
            "beta(f)<=n-1 when f has at least two positives",
        ],
        "universal_proof": False,
        "zero_degree_convention": -1,
        "beta_zero_convention": 0,
        "records": [],
    }
    checks = 0
    for n in range(4):
        size = 1 << n
        limit = 1 << size
        degrees = [anf_degree(f, n) for f in range(limit)]
        affine = [f for f in range(limit) if degrees[f] <= 1]
        betas = []
        count_start = checks
        for f in range(limit):
            pointwise = {v: None for v in range(size) if (f >> v) & 1}
            for d in range(n + 1):
                monomials = [s for s in range(size) if s.bit_count() <= d]
                evaluations = [
                    sum(int((x & s) == s) << j for j, s in enumerate(monomials))
                    for x in range(size)
                ]
                negatives = [evaluations[u] for u in range(size) if not ((f >> u) & 1)]
                cover = 0
                for h in range(limit):
                    if degrees[h] <= d and (h & ~f) == 0:
                        cover |= h
                for v in pointwise:
                    dual = span_contains(negatives, evaluations[v])
                    primal = not bool((cover >> v) & 1)
                    if dual != primal:
                        raise AssertionError((n, f, d, v, dual, primal))
                    if not primal and pointwise[v] is None:
                        pointwise[v] = d
                    checks += 1
            if any(d is None for d in pointwise.values()):
                raise AssertionError((n, f, "missing point indicator"))
            betas.append(max(pointwise.values(), default=0))
        stars = [max(betas[f ^ mask] for mask in affine) for f in range(limit)]
        if not all(b <= n for b in stars):
            raise AssertionError((n, "betaStar upper bound"))
        if not all(betas[f] <= n - 1 for f in range(limit) if f.bit_count() >= 2):
            raise AssertionError((n, "two-positive upper bound"))
        result["records"].append({
            "n": n,
            "functions": limit,
            "affine_masks": len(affine),
            "dual_checks": checks - count_start,
            "max_beta": max(betas),
            "max_betaStar": max(stars),
            "betaStar_zero": stars[0],
        })
    result["functions_total"] = sum(r["functions"] for r in result["records"])
    result["dual_checks_total"] = checks
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = check()
    serialized = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(serialized)
    print(serialized, end="")
