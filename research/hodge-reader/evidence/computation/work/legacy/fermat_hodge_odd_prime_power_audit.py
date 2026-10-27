from __future__ import annotations

import itertools
import json
import math
from collections import Counter
from pathlib import Path

def units(m: int) -> list[int]:
    return [u for u in range(1, m) if math.gcd(u, m) == 1]

def lpr(x: int, m: int) -> int:
    r = x % m
    return m if r == 0 else r

def balanced(t: tuple[int, ...], m: int) -> bool:
    target = (len(t) // 2) * m
    return all(sum(lpr(u * a, m) for a in t) == target for u in units(m))

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
    return min(tuple(sorted(lpr(u * a, m) for a in t)) for u in units(m))

def balanced_packets(m: int, length: int) -> list[tuple[int, ...]]:
    target = (length // 2) * m
    us = units(m)
    out = []
    for t in itertools.combinations_with_replacement(range(1, m), length):
        if sum(t) != target:
            continue
        if all(sum(lpr(u * a, m) for a in t) == target for u in us[1:]):
            out.append(t)
    return out

def gamma3(r: int, b: int) -> tuple[int, ...]:
    m = 3 ** r
    q = m // 3
    return tuple(sorted((b, b + q, b + 2*q, 3*(q-b))))

def alpha5(r: int) -> tuple[int, ...]:
    m = 5 ** r
    q = m // 5
    return tuple(sorted((1, 1+q, 1+2*q, 1+3*q, 1+4*q, 5*q-5)))

def quasi_certificate(t: tuple[int, ...], m: int, fours: list[tuple[int, ...]]) -> bool:
    c4 = [Counter(x) for x in fours]
    pair_sums = {}
    for i, a in enumerate(fours):
        for j in range(i, len(fours)):
            pair_sums[tuple(sorted((c4[i] + c4[j]).items()))] = True
    ct = Counter(t)
    for r in range(1, m):
        key = tuple(sorted((ct + Counter((r, m-r))).items()))
        if key in pair_sums:
            return True
    return False

def audit() -> dict:
    result = {"checks": {}}

    for m in (9, 27):
        b4 = balanced_packets(m, 4)
        b6 = balanced_packets(m, 6)
        nonpair = [t for t in b6 if full_conductor(t, m) and not paired(t, m)]
        result[f"degree_{m}"] = {
            "balanced_four_count": len(b4),
            "balanced_six_count": len(b6),
            "full_conductor_nonpair_count": len(nonpair),
            "all_nonpair_quasi": all(quasi_certificate(t, m, b4) for t in nonpair),
        }
        result["checks"][f"degree_{m}_all_nonpair_quasi"] = result[f"degree_{m}"]["all_nonpair_quasi"]

    m = 25
    b6 = balanced_packets(m, 6)
    nonpair = [t for t in b6 if full_conductor(t, m) and not paired(t, m)]
    reps = sorted({canonical_unit(t, m) for t in nonpair})
    result["degree_25"] = {
        "balanced_six_count": len(b6),
        "full_conductor_nonpair_count": len(nonpair),
        "unit_orbit_representatives": reps,
    }
    result["checks"]["degree_25_unique_nonpair_orbit"] = reps == [(1,6,11,16,20,21)]

    for r in (2, 3, 4):
        a = alpha5(r)
        result["checks"][f"alpha5_r{r}_balanced"] = balanced(a, 5**r)
        result["checks"][f"alpha5_r{r}_full_conductor"] = full_conductor(a, 5**r)

    for r in (2, 3, 4, 5):
        q = 3**(r-1)
        candidates = [b for b in range(1, min(q, 20)) if math.gcd(b, 3) == 1]
        result["checks"][f"gamma3_r{r}_balanced"] = all(balanced(gamma3(r, b), 3**r) for b in candidates)

    result["passed"] = all(result["checks"].values())
    return result

def main() -> None:
    data = audit()
    path = Path("Fermat_Hodge_Odd_Prime_Power_VERIFICATION.json")
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps(data, indent=2))
    if not data["passed"]:
        raise SystemExit("verification failed")

if __name__ == "__main__":
    main()
