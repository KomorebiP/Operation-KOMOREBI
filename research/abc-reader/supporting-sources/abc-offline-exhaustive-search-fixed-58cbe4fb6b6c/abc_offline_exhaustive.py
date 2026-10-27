from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import functools
import json
import math
import multiprocessing as mp
import os
import signal
import sqlite3
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence

import mpmath as mpm
import sympy as sp

TARGET_RECORD = mpm.mpf("1.6299116841270482")
DEFAULT_ALPHA = 1 / TARGET_RECORD
mpm.mp.dps = 120

PROFILES = {
    "quick": {
        "workers": 4,
        "q_min": 1.55,
        "min_c": 10**6,
        "factor_bits": 180,
        "endpoint_factor_bits": 120,
        "factor_timeout": 20,
        "cf": {
            "enabled": True,
            "d_min": 3,
            "d_max": 5,
            "core_limit": 40,
            "core_support": 2,
            "core_pair_mode": "one-sided",
            "q_max": 7,
            "e_min": 2,
            "e_max": 4,
            "max_den": 5_000,
            "max_terms": 36,
            "ray_steps": 0,
            "ray_tail": 0,
            "force_prime_max": 11,
            "force_exp_max": 3,
            "force_residual": True,
        },
        "plateau": {
            "enabled": False,
            "a_limit": 80,
            "a_rad_limit": 30,
            "m_min": 3,
            "m_max": 7,
            "endpoint_max": 10**7,
            "endpoint_prime_max": 43,
            "endpoint_support": 2,
            "endpoint_exp_max": 20,
            "plateau_prime_max": 19,
            "minimum_depth": 2,
        },
        "neighbor": {
            "enabled": True,
            "value_max": 10**10,
            "prime_max": 43,
            "support": 2,
            "exp_max": 18,
            "max_difference": 10**5,
        },
    },
    "deep": {
        "workers": max(2, (os.cpu_count() or 8) - 2),
        "q_min": 1.60,
        "min_c": 2**63,
        "factor_bits": 300,
        "endpoint_factor_bits": 180,
        "factor_timeout": 120,
        "cf": {
            "enabled": True,
            "d_min": 3,
            "d_max": 10,
            "core_limit": 500,
            "core_support": 3,
            "core_pair_mode": "one-sided",
            "q_max": 31,
            "e_min": 3,
            "e_max": 12,
            "max_den": 10**9,
            "max_terms": 80,
            "ray_steps": 0,
            "ray_tail": 0,
            "force_prime_max": 31,
            "force_exp_max": 5,
            "force_residual": True,
        },
        "plateau": {
            "enabled": False,
            "a_limit": 2000,
            "a_rad_limit": 300,
            "m_min": 3,
            "m_max": 14,
            "endpoint_max": 10**20,
            "endpoint_prime_max": 251,
            "endpoint_support": 3,
            "endpoint_exp_max": 40,
            "plateau_prime_max": 97,
            "minimum_depth": 2,
        },
        "neighbor": {
            "enabled": True,
            "value_max": 10**24,
            "prime_max": 251,
            "support": 2,
            "exp_max": 40,
            "max_difference": 10**10,
        },
    },
    "extreme": {
        "workers": max(2, (os.cpu_count() or 8) - 2),
        "q_min": 1.62,
        "min_c": 2**63,
        "factor_bits": 450,
        "endpoint_factor_bits": 220,
        "factor_timeout": 600,
        "cf": {
            "enabled": True,
            "d_min": 2,
            "d_max": 18,
            "core_limit": 15000,
            "core_support": 4,
            "core_pair_mode": "all",
            "q_max": 101,
            "e_min": 2,
            "e_max": 28,
            "max_den": 10**18,
            "max_terms": 140,
            "ray_steps": 5000,
            "ray_tail": 8,
            "force_prime_max": 67,
            "force_exp_max": 8,
            "force_residual": True,
        },
        "plateau": {
            "enabled": False,
            "a_limit": 20000,
            "a_rad_limit": 2000,
            "m_min": 2,
            "m_max": 24,
            "endpoint_max": 10**36,
            "endpoint_prime_max": 1009,
            "endpoint_support": 3,
            "endpoint_exp_max": 80,
            "plateau_prime_max": 251,
            "minimum_depth": 2,
        },
        "neighbor": {
            "enabled": True,
            "value_max": 10**38,
            "prime_max": 1009,
            "support": 2,
            "exp_max": 80,
            "max_difference": 10**18,
        },
    },
}


@dataclass(frozen=True)
class Candidate:
    a: int
    b: int
    c: int
    engine: str
    task_key: str
    metadata: dict[str, object]
    known_radical_lower_bound: int
    priority: float


class FactorTimeout(Exception):
    pass


def _alarm_handler(signum: int, frame: object) -> None:
    raise FactorTimeout()


def factor_with_timeout(n: int, timeout: int) -> tuple[dict[int, int], bool]:
    if n < 1:
        raise ValueError("factorization input must be positive")
    if n == 1:
        return {}, True
    old = signal.signal(signal.SIGALRM, _alarm_handler)
    signal.alarm(max(1, timeout))
    try:
        factors = {int(p): int(e) for p, e in sp.factorint(n).items()}
        return factors, math.prod(p**e for p, e in factors.items()) == n
    except FactorTimeout:
        partial = {int(p): int(e) for p, e in sp.factorint(n, limit=1_000_000).items()}
        complete = math.prod(p**e for p, e in partial.items()) == n and all(sp.isprime(p) for p in partial)
        return partial, complete
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old)


def radical_from_factors(factors: dict[int, int]) -> int:
    return math.prod(factors) if factors else 1


def factor_string(factors: dict[int, int]) -> str:
    return " ".join(f"{p}^{e}" for p, e in sorted(factors.items()))


def quality(c: int, radical: int) -> float:
    return float(mpm.log(c) / mpm.log(radical))


def config_hash(config: dict[str, object]) -> str:
    payload = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()[:16]


@functools.lru_cache(maxsize=128)
def primes_up_to(limit: int) -> tuple[int, ...]:
    return tuple(int(p) for p in sp.primerange(2, limit + 1))


def make_spf(limit: int) -> list[int]:
    spf = list(range(limit + 1))
    if limit >= 1:
        spf[1] = 1
    for p in range(2, int(limit**0.5) + 1):
        if spf[p] == p:
            for value in range(p * p, limit + 1, p):
                if spf[value] == value:
                    spf[value] = p
    return spf


def factor_spf(n: int, spf: Sequence[int]) -> dict[int, int]:
    result: dict[int, int] = {}
    value = n
    while value > 1:
        p = int(spf[value])
        result[p] = result.get(p, 0) + 1
        value //= p
    return result


def generated_cores(limit: int, support_max: int, d: int) -> list[tuple[int, int]]:
    spf = make_spf(limit)
    output: list[tuple[int, int]] = [(1, 1)]
    for n in range(2, limit + 1):
        factors = factor_spf(n, spf)
        if len(factors) > support_max or any(e >= d for e in factors.values()):
            continue
        output.append((n, radical_from_factors(factors)))
    return output


def low_radical_numbers(
    value_max: int,
    prime_max: int,
    support_max: int,
    exp_max: int,
) -> list[tuple[int, int, tuple[tuple[int, int], ...]]]:
    primes = primes_up_to(prime_max)
    output: list[tuple[int, int, tuple[tuple[int, int], ...]]] = [(1, 1, ())]

    def recurse(start: int, depth: int, value: int, radical: int, factors: tuple[tuple[int, int], ...]) -> None:
        if depth >= support_max:
            return
        for index in range(start, len(primes)):
            p = primes[index]
            current = value
            for exponent in range(1, exp_max + 1):
                if current > value_max // p:
                    break
                current *= p
                next_factors = factors + ((p, exponent),)
                output.append((current, radical * p, next_factors))
                recurse(index + 1, depth + 1, current, radical * p, next_factors)

    recurse(0, 0, 1, 1, ())
    output.sort(key=lambda row: row[0])
    dedup: list[tuple[int, int, tuple[tuple[int, int], ...]]] = []
    last = -1
    for row in output:
        if row[0] != last:
            dedup.append(row)
            last = row[0]
    return dedup


def all_roots_prime_power(B: int, C: int, d: int, q: int, exponent: int) -> list[int]:
    roots = [r for r in range(q) if (C * pow(r, d, q) - B) % q == 0]
    modulus = q
    for _ in range(1, exponent):
        next_modulus = modulus * q
        lifted: list[int] = []
        for root in roots:
            for digit in range(q):
                candidate = root + digit * modulus
                if (C * pow(candidate, d, next_modulus) - B) % next_modulus == 0:
                    lifted.append(candidate)
        roots = sorted(set(lifted))
        modulus = next_modulus
        if not roots:
            break
    return roots


def all_roots_levels(B: int, C: int, d: int, q: int, e_max: int) -> dict[int, list[int]]:
    levels: dict[int, list[int]] = {}
    roots = [r for r in range(q) if (C * pow(r, d, q) - B) % q == 0]
    modulus = q
    levels[1] = sorted(set(roots))
    for exponent in range(2, e_max + 1):
        next_modulus = modulus * q
        lifted: list[int] = []
        for root in roots:
            for digit in range(q):
                candidate = root + digit * modulus
                if (C * pow(candidate, d, next_modulus) - B) % next_modulus == 0:
                    lifted.append(candidate)
        roots = sorted(set(lifted))
        levels[exponent] = roots
        modulus = next_modulus
        if not roots:
            for remaining in range(exponent + 1, e_max + 1):
                levels[remaining] = []
            break
    return levels


def continued_fraction_terms(value: mpm.mpf, max_terms: int) -> list[int]:
    result: list[int] = []
    x = mpm.mpf(value)
    for _ in range(max_terms):
        digit = int(mpm.floor(x))
        result.append(digit)
        fraction = x - digit
        if abs(fraction) < mpm.mpf("1e-110"):
            break
        x = 1 / fraction
    return result


def convergents_and_semiconvergents(value: mpm.mpf, max_den: int, max_terms: int) -> list[tuple[int, int, bool]]:
    cf = continued_fraction_terms(value, max_terms)
    p_m2, p_m1 = 0, 1
    q_m2, q_m1 = 1, 0
    output: list[tuple[int, int, bool]] = []
    for index, digit in enumerate(cf):
        if index == 0:
            p = digit
            q = 1
            if q <= max_den:
                output.append((p, q, True))
            p_m2, p_m1 = p_m1, p
            q_m2, q_m1 = q_m1, q
            continue
        max_t = digit
        if q_m1 > 0:
            max_t = min(max_t, max(0, (max_den - q_m2) // q_m1))
        for t in range(1, max_t + 1):
            p = p_m2 + t * p_m1
            q = q_m2 + t * q_m1
            if q <= 0 or q > max_den:
                continue
            output.append((p, q, t == digit))
        p = digit * p_m1 + p_m2
        q = digit * q_m1 + q_m2
        p_m2, p_m1 = p_m1, p
        q_m2, q_m1 = q_m1, q
        if q > max_den:
            break
    seen: set[tuple[int, int]] = set()
    unique: list[tuple[int, int, bool]] = []
    for p, q, full in output:
        key = (p, q)
        if key not in seen:
            seen.add(key)
            unique.append((p, q, full))
    unique.sort(key=lambda row: (row[1], row[0]))
    return unique


def merge_factor_maps(*maps: dict[int, int]) -> dict[int, int]:
    result: dict[int, int] = {}
    for mapping in maps:
        for p, e in mapping.items():
            result[p] = result.get(p, 0) + e
    return result


def scaled_factor_map(mapping: dict[int, int], scale: int) -> dict[int, int]:
    return {p: e * scale for p, e in mapping.items()}


@functools.lru_cache(maxsize=250_000)
def endpoint_factor_lower_bound(n: int, exact_bits: int) -> tuple[tuple[int, int], ...]:
    if n <= 1:
        return ()
    if n.bit_length() <= exact_bits:
        return tuple(sorted((int(p), int(e)) for p, e in sp.factorint(n).items()))
    factors: dict[int, int] = {}
    remaining = n
    for p in primes_up_to(1000):
        if remaining % p == 0:
            exponent = 0
            while remaining % p == 0:
                remaining //= p
                exponent += 1
            factors[p] = exponent
    if remaining > 1 and sp.isprime(remaining):
        factors[int(remaining)] = 1
    else:
        perfect = sp.perfect_power(remaining) if remaining > 1 else False
        if perfect:
            base, exponent = perfect
            if int(base).bit_length() <= exact_bits:
                for p, e in sp.factorint(int(base)).items():
                    factors[int(p)] = factors.get(int(p), 0) + int(e) * int(exponent)
    return tuple(sorted(factors.items()))


def primitive_endpoint_radicals(
    B: int,
    C: int,
    d: int,
    x: int,
    y: int,
    exact_bits: int,
) -> tuple[int, int, dict[int, int], dict[int, int]]:
    fB = dict(endpoint_factor_lower_bound(B, exact_bits))
    fC = dict(endpoint_factor_lower_bound(C, exact_bits))
    fx = dict(endpoint_factor_lower_bound(x, exact_bits))
    fy = dict(endpoint_factor_lower_bound(y, exact_bits))
    left = merge_factor_maps(fC, scaled_factor_map(fx, d))
    right = merge_factor_maps(fB, scaled_factor_map(fy, d))
    common = {p: min(left.get(p, 0), right.get(p, 0)) for p in set(left) | set(right)}
    for p, e in common.items():
        if e:
            left[p] -= e
            right[p] -= e
            if left[p] == 0:
                del left[p]
            if right[p] == 0:
                del right[p]
    return radical_from_factors(left), radical_from_factors(right), left, right


def safe_candidate(
    left: int,
    right: int,
    engine: str,
    task_key: str,
    metadata: dict[str, object],
    known_radical_lower_bound: int,
    q_min: float,
    min_c: int,
) -> Candidate | None:
    if left == right:
        return None
    common = math.gcd(left, right)
    left //= common
    right //= common
    a = abs(left - right)
    b = min(left, right)
    c = max(left, right)
    if a <= 0 or b <= 0 or c < min_c or math.gcd(a, b) != 1:
        return None
    alpha = 1 / q_min
    optimistic_margin = alpha * mpm.log(c) - mpm.log(max(known_radical_lower_bound, 2))
    if optimistic_margin <= 0:
        return None
    priority = float(optimistic_margin - mpm.log(max(a, 1)) * mpm.mpf("0.05"))
    return Candidate(a, b, c, engine, task_key, metadata, known_radical_lower_bound, priority)


def sum_candidate(
    a: int,
    b: int,
    c: int,
    engine: str,
    task_key: str,
    metadata: dict[str, object],
    known_radical_lower_bound: int,
    q_min: float,
    min_c: int,
) -> Candidate | None:
    if a <= 0 or b <= 0 or a + b != c or c < min_c or math.gcd(a, b) != 1:
        return None
    if a > b:
        a, b = b, a
    alpha = 1 / q_min
    optimistic_margin = alpha * mpm.log(c) - mpm.log(max(known_radical_lower_bound, 2))
    if optimistic_margin <= 0:
        return None
    priority = float(optimistic_margin - mpm.log(max(a, 1)) * mpm.mpf("0.05"))
    return Candidate(a, b, c, engine, task_key, metadata, known_radical_lower_bound, priority)


def cf_task_worker(payload: tuple[dict[str, object], tuple[int, int, int, int]]) -> tuple[str, dict[str, int], list[Candidate]]:
    config, task = payload
    B, C, d, q = task
    cf_config = config["cf"]
    e_min = int(cf_config["e_min"])
    e_max = int(cf_config["e_max"])
    task_key = f"cf:{B}:{C}:{d}:{q}:{e_min}-{e_max}"
    roots_by_level = all_roots_levels(B, C, d, q, e_max)
    stats = {"roots": sum(len(roots_by_level[e]) for e in range(e_min, e_max + 1)), "approximants": 0, "ray_states": 0, "candidates": 0}
    candidates: list[Candidate] = []
    alpha = mpm.power(mpm.mpf(B) / C, mpm.mpf(1) / d)
    q_min = float(config["q_min"])
    min_c = int(config["min_c"])
    force_primes = primes_up_to(int(cf_config["force_prime_max"]))
    force_exp_max = int(cf_config["force_exp_max"])

    for exponent in range(e_min, e_max + 1):
        modulus = q**exponent
        for root in roots_by_level.get(exponent, []):
            delta = (alpha - root) / modulus
            approximants = convergents_and_semiconvergents(delta, int(cf_config["max_den"]), int(cf_config["max_terms"]))
            stats["approximants"] += len(approximants)
            full_convergents: list[tuple[int, int]] = []
            for t, y, full in approximants:
                x = root * y + modulus * t
                if x <= 0 or y <= 0 or math.gcd(x, y) != 1:
                    continue
                left = C * pow(x, d)
                right = B * pow(y, d)
                rad_left, rad_right, left_factors, right_factors = primitive_endpoint_radicals(
                    B, C, d, x, y, int(config.get("endpoint_factor_bits", 160))
                )
                known = rad_left * rad_right
                candidate = safe_candidate(
                    left,
                    right,
                    "cf",
                    task_key,
                    {"B": B, "C": C, "d": d, "q": q, "e": exponent, "root": root, "x": x, "y": y, "kind": "convergent" if full else "semiconvergent", "left_factors": left_factors, "right_factors": right_factors},
                    known,
                    q_min,
                    min_c,
                )
                if candidate is not None:
                    candidates.append(candidate)
                if full:
                    full_convergents.append((t, y))

            ray_steps = int(cf_config["ray_steps"])
            if ray_steps <= 0 or len(full_convergents) < 2:
                continue
            ray_tail = int(cf_config.get("ray_tail", 0))
            ray_source = full_convergents[-(ray_tail + 1):] if ray_tail > 0 else full_convergents
            for (t0, y0), (t1, y1) in zip(ray_source[:-1], ray_source[1:]):
                x0 = root * y0 + modulus * t0
                x1 = root * y1 + modulus * t1
                if min(x0, x1, y0, y1) <= 0:
                    continue
                for px in force_primes:
                    if px == q:
                        continue
                    for py in force_primes:
                        if py in (q, px):
                            continue
                        for ex in range(2, force_exp_max + 1):
                            mx = px**ex
                            if math.gcd(x1, mx) != 1:
                                continue
                            kx = (-x0 * pow(x1, -1, mx)) % mx
                            for ey in range(2, force_exp_max + 1):
                                my = py**ey
                                if math.gcd(y1, my) != 1:
                                    continue
                                ky = (-y0 * pow(y1, -1, my)) % my
                                if math.gcd(mx, my) != 1:
                                    continue
                                step = mx * my
                                k0 = (kx + mx * (((ky - kx) * pow(mx, -1, my)) % my)) % step
                                for j in range(ray_steps):
                                    k = k0 + j * step
                                    if k < 1:
                                        continue
                                    x = x0 + k * x1
                                    y = y0 + k * y1
                                    if math.gcd(x, y) != 1:
                                        continue
                                    stats["ray_states"] += 1
                                    left = C * pow(x, d)
                                    right = B * pow(y, d)
                                    rad_left, rad_right, left_factors, right_factors = primitive_endpoint_radicals(
                                        B, C, d, x, y, int(config.get("endpoint_factor_bits", 160))
                                    )
                                    known = rad_left * rad_right
                                    candidate = safe_candidate(
                                        left,
                                        right,
                                        "ray",
                                        task_key,
                                        {"B": B, "C": C, "d": d, "q": q, "e": exponent, "root": root, "x": x, "y": y, "px": px, "ex": ex, "py": py, "ey": ey, "k": k, "left_factors": left_factors, "right_factors": right_factors},
                                        known,
                                        q_min,
                                        min_c,
                                    )
                                    if candidate is not None:
                                        candidates.append(candidate)
    dedup: dict[tuple[int, int, int], Candidate] = {}
    for candidate in candidates:
        key = (candidate.a, candidate.b, candidate.c)
        if key not in dedup or candidate.priority > dedup[key].priority:
            dedup[key] = candidate
    result = list(dedup.values())
    stats["candidates"] = len(result)
    return task_key, stats, result


def plateau_worker(payload: tuple[dict[str, object], tuple[int, int, int, int, tuple[tuple[int, int], ...]]]) -> tuple[str, dict[str, int], list[Candidate]]:
    config, task = payload
    a, m, x, rad_x, factors_x = task
    task_key = f"plateau:{a}:{m}:{x}"
    plateau = config["plateau"]
    n = pow(x, m) - a
    stats = {"tested": 1, "candidates": 0}
    if n <= 0 or math.gcd(a, x) != 1:
        return task_key, stats, []
    remaining = n
    forced: dict[int, int] = {}
    for p in primes_up_to(int(plateau["plateau_prime_max"])):
        exponent = 0
        while remaining % p == 0:
            remaining //= p
            exponent += 1
        if exponent >= int(plateau["minimum_depth"]):
            forced[p] = exponent
    if not forced:
        return task_key, stats, []
    known = radical_from_factors({int(p): int(e) for p, e in sp.factorint(a).items()}) if a > 1 else 1
    known *= rad_x * math.prod(forced)
    candidate = sum_candidate(
        a,
        n,
        pow(x, m),
        "plateau",
        task_key,
        {"a_seed": a, "m": m, "x": x, "x_factors": list(factors_x), "forced": forced},
        known,
        float(config["q_min"]),
        int(config["min_c"]),
    )
    if candidate is None:
        return task_key, stats, []
    stats["candidates"] = 1
    return task_key, stats, [candidate]


def neighbor_worker(payload: tuple[dict[str, object], list[tuple[int, int, tuple[tuple[int, int], ...]]], tuple[int, int]]) -> tuple[str, dict[str, int], list[Candidate]]:
    config, values, bounds = payload
    start, end = bounds
    task_key = f"neighbor:{start}:{end}"
    maximum_difference = int(config["neighbor"]["max_difference"])
    q_min = float(config["q_min"])
    min_c = int(config["min_c"])
    numbers = [row[0] for row in values]
    index = {value: row for value, *row in values}
    candidates: list[Candidate] = []
    pairs = 0
    import bisect

    for ci in range(start, end):
        c, rad_c, factors_c = values[ci]
        if c < min_c:
            continue
        lower = c - maximum_difference
        first = bisect.bisect_left(numbers, max(1, lower), 0, ci)
        for bi in range(first, ci):
            b, rad_b, factors_b = values[bi]
            a = c - b
            if a <= 0:
                continue
            pairs += 1
            if math.gcd(a, b) != 1:
                continue
            known = rad_b * rad_c
            candidate = sum_candidate(
                a,
                b,
                c,
                "neighbor",
                task_key,
                {"b_factors": list(factors_b), "c_factors": list(factors_c)},
                known,
                q_min,
                min_c,
            )
            if candidate is not None:
                candidates.append(candidate)
    dedup = {(c.a, c.b, c.c): c for c in candidates}
    return task_key, {"pairs": pairs, "candidates": len(dedup)}, list(dedup.values())


def init_database(path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(path)
    connection.execute("PRAGMA journal_mode=WAL")
    connection.execute("PRAGMA synchronous=NORMAL")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS tasks(
            task_key TEXT PRIMARY KEY,
            engine TEXT NOT NULL,
            status TEXT NOT NULL,
            stats_json TEXT,
            finished_at REAL
        );
        CREATE TABLE IF NOT EXISTS candidates(
            a TEXT NOT NULL,
            b TEXT NOT NULL,
            c TEXT NOT NULL,
            engine TEXT NOT NULL,
            task_key TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            known_radical_lower_bound TEXT NOT NULL,
            priority REAL NOT NULL,
            factor_status TEXT NOT NULL DEFAULT 'pending',
            PRIMARY KEY(a,b,c)
        );
        CREATE TABLE IF NOT EXISTS triples(
            a TEXT NOT NULL,
            b TEXT NOT NULL,
            c TEXT NOT NULL,
            radical TEXT,
            quality REAL,
            factor_a TEXT,
            factor_b TEXT,
            factor_c TEXT,
            complete INTEGER NOT NULL,
            engine TEXT NOT NULL,
            metadata_json TEXT NOT NULL,
            verified_at REAL,
            PRIMARY KEY(a,b,c)
        );
        """
    )
    return connection


def task_done(connection: sqlite3.Connection, task_key: str) -> bool:
    row = connection.execute("SELECT status FROM tasks WHERE task_key=?", (task_key,)).fetchone()
    return row is not None and row[0] == "done"


def save_task_result(connection: sqlite3.Connection, task_key: str, engine: str, stats: dict[str, int], candidates: Sequence[Candidate]) -> None:
    with connection:
        for candidate in candidates:
            connection.execute(
                """
                INSERT INTO candidates(a,b,c,engine,task_key,metadata_json,known_radical_lower_bound,priority)
                VALUES(?,?,?,?,?,?,?,?)
                ON CONFLICT(a,b,c) DO UPDATE SET
                    priority=MAX(priority,excluded.priority),
                    metadata_json=CASE WHEN excluded.priority>priority THEN excluded.metadata_json ELSE metadata_json END,
                    engine=CASE WHEN excluded.priority>priority THEN excluded.engine ELSE engine END,
                    task_key=CASE WHEN excluded.priority>priority THEN excluded.task_key ELSE task_key END
                """,
                (
                    str(candidate.a), str(candidate.b), str(candidate.c), candidate.engine, candidate.task_key,
                    json.dumps(candidate.metadata, sort_keys=True), str(candidate.known_radical_lower_bound), candidate.priority,
                ),
            )
        connection.execute(
            "INSERT OR REPLACE INTO tasks(task_key,engine,status,stats_json,finished_at) VALUES(?,?,?,?,?)",
            (task_key, engine, "done", json.dumps(stats, sort_keys=True), time.time()),
        )


def factor_candidate_worker(payload: tuple[str, str, str, int]) -> dict[str, object]:
    a_text, b_text, c_text, timeout = payload
    a, b, c = int(a_text), int(b_text), int(c_text)
    fa, ca = factor_with_timeout(a, timeout)
    fb, cb = factor_with_timeout(b, timeout)
    fc, cc = factor_with_timeout(c, timeout)
    complete = ca and cb and cc
    radical = radical_from_factors(fa) * radical_from_factors(fb) * radical_from_factors(fc) if complete else None
    q = quality(c, radical) if complete and radical and radical > 1 else None
    return {
        "a": a_text, "b": b_text, "c": c_text,
        "factor_a": factor_string(fa), "factor_b": factor_string(fb), "factor_c": factor_string(fc),
        "complete": complete, "radical": str(radical) if radical is not None else None, "quality": q,
    }


def factor_pending(connection: sqlite3.Connection, config: dict[str, object], workers: int, limit: int | None = None) -> None:
    query = "SELECT a,b,c,engine,metadata_json FROM candidates WHERE factor_status='pending' ORDER BY priority DESC"
    if limit is not None:
        query += f" LIMIT {int(limit)}"
    rows = connection.execute(query).fetchall()
    if not rows:
        return
    factor_bits = int(config["factor_bits"])
    timeout = int(config["factor_timeout"])
    eligible = [row for row in rows if max(int(row[0]).bit_length(), int(row[1]).bit_length(), int(row[2]).bit_length()) <= factor_bits]
    ineligible = [row for row in rows if row not in eligible]
    with connection:
        for row in ineligible:
            connection.execute("UPDATE candidates SET factor_status='deferred' WHERE a=? AND b=? AND c=?", row[:3])
    with ProcessPoolExecutor(max_workers=workers) as executor:
        futures = {executor.submit(factor_candidate_worker, (row[0], row[1], row[2], timeout)): row for row in eligible}
        for future in as_completed(futures):
            row = futures[future]
            try:
                result = future.result()
            except Exception as exc:
                with connection:
                    connection.execute("UPDATE candidates SET factor_status='error' WHERE a=? AND b=? AND c=?", row[:3])
                print(f"factor error {row[:3]}: {exc}", file=sys.stderr)
                continue
            with connection:
                connection.execute(
                    """
                    INSERT OR REPLACE INTO triples(a,b,c,radical,quality,factor_a,factor_b,factor_c,complete,engine,metadata_json,verified_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    (
                        result["a"], result["b"], result["c"], result["radical"], result["quality"],
                        result["factor_a"], result["factor_b"], result["factor_c"], int(result["complete"]),
                        row[3], row[4], time.time(),
                    ),
                )
                connection.execute(
                    "UPDATE candidates SET factor_status=? WHERE a=? AND b=? AND c=?",
                    ("complete" if result["complete"] else "partial", row[0], row[1], row[2]),
                )


def export_results(connection: sqlite3.Connection, output: Path, q_min: float) -> dict[str, object]:
    output.mkdir(parents=True, exist_ok=True)
    triples = connection.execute(
        "SELECT a,b,c,radical,quality,factor_a,factor_b,factor_c,engine,metadata_json,complete FROM triples ORDER BY quality DESC"
    ).fetchall()
    with (output / "verified_triples.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["a", "b", "c", "radical", "quality", "factor_a", "factor_b", "factor_c", "engine", "complete", "metadata"])
        for row in triples:
            writer.writerow([*row[:9], row[10], row[9]])
    candidates = connection.execute(
        "SELECT a,b,c,engine,priority,factor_status,known_radical_lower_bound,metadata_json FROM candidates ORDER BY priority DESC"
    ).fetchall()
    with (output / "all_candidates.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["a", "b", "c", "engine", "priority", "factor_status", "known_radical_lower_bound", "metadata"])
        writer.writerows(candidates)
    task_counts = dict(connection.execute("SELECT engine,COUNT(*) FROM tasks WHERE status='done' GROUP BY engine").fetchall())
    complete_count = sum(int(row[10]) for row in triples)
    beats = [row for row in triples if row[4] is not None and row[4] > float(TARGET_RECORD)]
    summary = {
        "tasks_completed": task_counts,
        "candidates": len(candidates),
        "verified_rows": len(triples),
        "complete_factorizations": complete_count,
        "quality_threshold": q_min,
        "record_target": float(TARGET_RECORD),
        "record_beats": len(beats),
        "best_quality": triples[0][4] if triples else None,
        "best_triple": list(triples[0][:5]) if triples else None,
    }
    (output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def generate_cf_tasks(config: dict[str, object]) -> list[tuple[int, int, int, int]]:
    cf = config["cf"]
    tasks: list[tuple[int, int, int, int]] = []
    primes = primes_up_to(int(cf["q_max"]))
    for d in range(int(cf["d_min"]), int(cf["d_max"]) + 1):
        cores = generated_cores(int(cf["core_limit"]), int(cf["core_support"]), d)
        pairs: list[tuple[int, int]] = []
        if cf["core_pair_mode"] == "all":
            for B, _ in cores:
                for C, _ in cores:
                    if B < C or math.gcd(B, C) != 1 or B == C:
                        continue
                    pairs.append((B, C))
        else:
            for value, _ in cores:
                if value != 1:
                    pairs.extend([(value, 1), (1, value)])
        for B, C in pairs:
            for q in primes:
                if math.gcd(B * C, q) != 1:
                    continue
                tasks.append((B, C, d, q))
    return tasks


def run_search(config: dict[str, object], workdir: Path, hours: float | None, factor_limit: int | None) -> dict[str, object]:
    workdir.mkdir(parents=True, exist_ok=True)
    connection = init_database(workdir / "search.sqlite")
    workers = int(config["workers"])
    deadline = time.time() + hours * 3600 if hours else None

    if config["cf"]["enabled"]:
        tasks = generate_cf_tasks(config)
        pending = [task for task in tasks if not task_done(connection, f"cf:{task[0]}:{task[1]}:{task[2]}:{task[3]}:{int(config['cf']['e_min'])}-{int(config['cf']['e_max'])}")]
        print(f"CF/Ray tasks pending: {len(pending)}")
        with ProcessPoolExecutor(max_workers=workers) as executor:
            futures = {}
            iterator = iter(pending)
            for _ in range(min(workers * 2, len(pending))):
                try:
                    task = next(iterator)
                except StopIteration:
                    break
                futures[executor.submit(cf_task_worker, (config, task))] = task
            while futures:
                done = next(as_completed(futures))
                task = futures.pop(done)
                try:
                    task_key, stats, candidates = done.result()
                    save_task_result(connection, task_key, "cf", stats, candidates)
                except Exception as exc:
                    print(f"task failed {task}: {exc}", file=sys.stderr)
                if deadline and time.time() >= deadline:
                    for future in futures:
                        future.cancel()
                    break
                try:
                    next_task = next(iterator)
                except StopIteration:
                    continue
                futures[executor.submit(cf_task_worker, (config, next_task))] = next_task

    if not deadline or time.time() < deadline:
        if config["plateau"]["enabled"]:
            plateau = config["plateau"]
            spf = make_spf(int(plateau["a_limit"]))
            a_values: list[int] = []
            for a in range(1, int(plateau["a_limit"]) + 1):
                factors = factor_spf(a, spf) if a > 1 else {}
                if radical_from_factors(factors) <= int(plateau["a_rad_limit"]):
                    a_values.append(a)
            endpoints = low_radical_numbers(
                int(plateau["endpoint_max"]), int(plateau["endpoint_prime_max"]),
                int(plateau["endpoint_support"]), int(plateau["endpoint_exp_max"]),
            )
            tasks = []
            for a in a_values:
                for m in range(int(plateau["m_min"]), int(plateau["m_max"]) + 1):
                    for x, rad_x, factors_x in endpoints:
                        if x > 1:
                            tasks.append((a, m, x, rad_x, factors_x))
            pending = [task for task in tasks if not task_done(connection, f"plateau:{task[0]}:{task[1]}:{task[2]}")]
            print(f"Plateau tasks pending: {len(pending)}")
            with ProcessPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(plateau_worker, (config, task)): task for task in pending[: workers * 4]}
                index = workers * 4
                while futures:
                    done = next(as_completed(futures))
                    task = futures.pop(done)
                    try:
                        task_key, stats, candidates = done.result()
                        save_task_result(connection, task_key, "plateau", stats, candidates)
                    except Exception as exc:
                        print(f"plateau failed {task}: {exc}", file=sys.stderr)
                    if deadline and time.time() >= deadline:
                        for future in futures:
                            future.cancel()
                        break
                    if index < len(pending):
                        next_task = pending[index]
                        index += 1
                        futures[executor.submit(plateau_worker, (config, next_task))] = next_task

    if not deadline or time.time() < deadline:
        if config["neighbor"]["enabled"]:
            neighbor = config["neighbor"]
            values = low_radical_numbers(
                int(neighbor["value_max"]), int(neighbor["prime_max"]),
                int(neighbor["support"]), int(neighbor["exp_max"]),
            )
            chunk = max(1000, len(values) // max(1, workers * 8))
            ranges = [(start, min(len(values), start + chunk)) for start in range(0, len(values), chunk)]
            pending = [bounds for bounds in ranges if not task_done(connection, f"neighbor:{bounds[0]}:{bounds[1]}")]
            print(f"Neighbor chunks pending: {len(pending)} over {len(values)} generated values")
            with ProcessPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(neighbor_worker, (config, values, bounds)): bounds for bounds in pending}
                for future in as_completed(futures):
                    bounds = futures[future]
                    try:
                        task_key, stats, candidates = future.result()
                        save_task_result(connection, task_key, "neighbor", stats, candidates)
                    except Exception as exc:
                        print(f"neighbor failed {bounds}: {exc}", file=sys.stderr)
                    if deadline and time.time() >= deadline:
                        break

    factor_pending(connection, config, workers, factor_limit)
    summary = export_results(connection, workdir / "results", float(config["q_min"]))
    coverage = {"config": config, "config_hash": config_hash(config), "summary": summary, "generated_at": time.time()}
    (workdir / "coverage.json").write_text(json.dumps(coverage, indent=2) + "\n", encoding="utf-8")
    connection.close()
    return summary


def load_config(args: argparse.Namespace) -> dict[str, object]:
    if args.config:
        config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    else:
        config = json.loads(json.dumps(PROFILES[args.profile]))
    if args.workers:
        config["workers"] = args.workers
    if args.q_min:
        config["q_min"] = args.q_min
    return config


def main() -> None:
    parser = argparse.ArgumentParser(description="Bounded exhaustive offline abc search suite")
    parser.add_argument("--profile", choices=sorted(PROFILES), default="quick")
    parser.add_argument("--config")
    parser.add_argument("--workdir", default="abc_offline_run")
    parser.add_argument("--workers", type=int)
    parser.add_argument("--q-min", type=float)
    parser.add_argument("--hours", type=float)
    parser.add_argument("--factor-limit", type=int)
    parser.add_argument("--write-profile", choices=sorted(PROFILES))
    parser.add_argument("--plan", action="store_true")
    parser.add_argument("--factor-only", action="store_true")
    parser.add_argument("--export-only", action="store_true")
    args = parser.parse_args()
    if args.write_profile:
        Path(f"{args.write_profile}_profile.json").write_text(json.dumps(PROFILES[args.write_profile], indent=2) + "\n")
        return
    config = load_config(args)
    workdir = Path(args.workdir).resolve()
    if args.plan:
        cf_tasks = len(generate_cf_tasks(config)) if config["cf"]["enabled"] else 0
        neighbor_values = len(low_radical_numbers(
            int(config["neighbor"]["value_max"]), int(config["neighbor"]["prime_max"]),
            int(config["neighbor"]["support"]), int(config["neighbor"]["exp_max"]),
        )) if config["neighbor"]["enabled"] else 0
        print(json.dumps({"config_hash": config_hash(config), "cf_tasks": cf_tasks, "neighbor_values": neighbor_values, "plateau_enabled": config["plateau"]["enabled"]}, indent=2))
        return
    if args.factor_only or args.export_only:
        connection = init_database(workdir / "search.sqlite")
        if args.factor_only:
            factor_pending(connection, config, int(config["workers"]), args.factor_limit)
        summary = export_results(connection, workdir / "results", float(config["q_min"]))
        connection.close()
    else:
        summary = run_search(config, workdir, args.hours, args.factor_limit)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
