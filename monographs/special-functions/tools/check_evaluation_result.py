#!/usr/bin/env python3
"""Bounded exact source checks for SF-LEAN-B18; not a Python refinement proof.

Run from any directory with --output PATH. Uses standard library only.
The ordinary-coefficient oracle avoids derivative arrays, comb and factorial.
"""
from __future__ import annotations

import argparse
import ast
from fractions import Fraction as Q
import hashlib
import importlib.util
import inspect
import json
from pathlib import Path
import platform
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE_HASHES = {
    "research/coupled_lab.py": "dff2a80db6f459e52dda45bc3399e0be45edf287df2efbeb1a56b57d38dfe20a",
    "research/family_lab.py": "7b546c1cd3159bb59634a3306c116719cd8d8d368c0046af90270c709b08cc8e",
}


def ordinary_coefficients(p, last):
    u, v = [Q(1)], [Q(1)]
    for n in range(1, last+1):
        # Both next coefficients use only the previous prefixes.
        next_rows = [sum((u[i]*v[n-1-i]*s**(2*i+1)*t**(2*(n-1-i)+1)
                          for i in range(n)), Q(0))/Q(2*n+1)
                     for s, t in (p[:2], p[2:])]
        u.append(next_rows[0])
        v.append(next_rows[1])
    return u, v


def recursive_majorant(p, radius, steps=20, bits=2000000):
    # A recursive oracle, rather than the source's mutable ladder/reverse loop.
    if radius < 1:
        return radius/(1-radius**2)
    if steps == 0:
        raise ValueError("majorant recursion exceeds max_steps")
    child = recursive_majorant(p, max(p)*radius, steps-1, bits)
    answer = radius*(1+child**2)
    if max(abs(answer.numerator).bit_length(), answer.denominator.bit_length()) > bits:
        raise ValueError("majorant exact rational exceeds max_bits")
    return answer


def reference(p, x, last, outer):
    s = max(Q(1), 2*x) if outer is None else outer
    u, v = ordinary_coefficients(p, last)
    partials = [sum((c*x**(2*n+1) for n, c in enumerate(row)), Q(0)) for row in (u, v)]
    b = recursive_majorant(p, s)
    tail = b*(x/s)**(2*last+3)
    return {"x": x, "last_index": last, "outer_radius": s, "majorant": b,
            "tail_bound": tail, "U": (partials[0], partials[0]+tail),
            "V": (partials[1], partials[1]+tail)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("--output must be a fresh path")
    observed = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
                for name in SOURCE_HASHES}
    if observed != SOURCE_HASHES:
        raise RuntimeError("Source revision differs from the assessed source")
    sys.dont_write_bytecode = True
    sys.path.insert(0, str(ROOT/"research"))
    spec = importlib.util.spec_from_file_location("assessed_coupled_lab", ROOT/"research/coupled_lab.py")
    lab = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lab)
    checks, rows = [], []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    def raises(name, function, message, exception=ValueError):
        try:
            function()
        except exception as exc:
            check(name, str(exc) == message)
        else:
            raise AssertionError(name+": expected exception")

    def patched(name, replacement, action):
        old = getattr(lab, name)
        setattr(lab, name, replacement)
        try:
            action()
        finally:
            setattr(lab, name, old)

    check("fixed resource defaults", inspect.signature(lab.disk_majorant).parameters["max_steps"].default == 20
          and inspect.signature(lab.disk_majorant).parameters["max_bits"].default == 2000000)
    source_ast = ast.parse((ROOT/"research/coupled_lab.py").read_text(encoding="utf-8"))
    evaluator = next(n for n in source_ast.body if isinstance(n, ast.FunctionDef) and n.name == "certified_evaluation")
    majorant_calls = [n for n in ast.walk(evaluator) if isinstance(n, ast.Call)
                      and isinstance(n.func, ast.Name) and n.func.id == "disk_majorant"]
    check("one call uses resource defaults", len(majorant_calls) == 1 and not majorant_calls[0].keywords)
    families = [tuple(map(Q, values)) for values in [
        ("1/2",)*4, ("1/5", "2/5", "3/5", "7/10"),
        ("1/3", "2/3", "1/2", "3/4"), ("1/3", "2/3", "1/3", "2/3")]]
    for p in families:
        for x in map(Q, ("0", "1/4", "1/2", "1")):
            for last in (0, 1, 2, 4, 6):
                for outer in (None, x+Q(1, 3), x+1):
                    actual = lab.certified_evaluation(*p, x, last, outer)
                    expected = reference(p, x, last, outer)
                    case = f"p={p},x={x},N={last},S={outer}"
                    check("seven field equality: "+case, actual == expected)
                    check("field types: "+case,
                          type(actual["last_index"]) is int
                          and all(type(actual[k]) is Q for k in ("x", "outer_radius", "majorant", "tail_bound"))
                          and all(type(actual[k]) is tuple and len(actual[k]) == 2
                                  and all(type(v) is Q for v in actual[k]) for k in ("U", "V")))
                    rows.append({"scales": list(map(str, p)), "x": str(x), "last_index": last,
                                 "outer_argument": None if outer is None else str(outer),
                                 "result": {k: list(map(str, v)) if type(v) is tuple else str(v)
                                            for k, v in actual.items()}})
    half = families[0]
    default_result = lab.certified_evaluation(*half, Q(1, 4))
    check("default last index is 24", default_result == reference(half, Q(1, 4), 24, None))
    worked = lab.certified_evaluation(*families[1], 1, last=30, outer_radius=2)
    check("manuscript worked call matches independent oracle", worked == reference(families[1], Q(1), 30, Q(2)))
    check("manuscript worked tail bound", worked["tail_bound"] < Q(16, 100000000000000))
    index_error = "last index must be a nonnegative integer"
    scale_error = "analytic certificates require 0 < q,r,a,b < 1"
    raises("last before scales", lambda: lab.certified_evaluation(0, 0, 0, 0, -1, -1, -2), index_error)
    for bad in (True, False, Q(1), 1.0, None, -1):
        raises("exact last classifier "+repr(bad), lambda bad=bad: lab.certified_evaluation(*half, 0, bad), index_error)
    raises("scales before x conversion", lambda: lab.certified_evaluation(0, 0, 0, 0, "bad"), scale_error)
    raises("negative x before outer conversion", lambda: lab.certified_evaluation(*half, -1, 0, "bad"),
           "certified real evaluation requires x>=0")
    for s in (-1, 0, Q(1, 2)):
        raises("reject outer <= x "+str(s), lambda s=s: lab.certified_evaluation(*half, Q(1, 2), 0, s),
               "outer radius must be strictly greater than x")
    # Origin still calls the majorant at S=1 with no resource kwargs.
    calls = []
    old_majorant = lab.disk_majorant
    def spy(*args, **kwargs):
        calls.append((args, kwargs))
        return old_majorant(*args, **kwargs)
    patched("disk_majorant", spy, lambda: lab.certified_evaluation(*half, 0, 0))
    check("origin uses S=1 and default kwargs", len(calls) == 1 and calls[0][0][-1] == 1 and calls[0][1] == {})
    near_one = (Q(999, 1000),)*4
    check("origin with near-unit scales succeeds", lab.certified_evaluation(*near_one, 0, 0)["U"] == (0, 0))
    raises("S=2 default step exhaustion", lambda: lab.certified_evaluation(*near_one, 1, 0),
           "majorant recursion exceeds max_steps")
    sentinel = ValueError("injected majorant failure")
    def fail_majorant(*_args, **_kwargs):
        raise sentinel
    def failure_action():
        try:
            lab.certified_evaluation(*half, 0, 0)
        except ValueError as exc:
            check("same error object propagates", exc is sentinel)
        else:
            raise AssertionError("majorant failure returned a result")
    patched("disk_majorant", fail_majorant, failure_action)
    check("reverse-fold anchor", lab.disk_majorant(*half, 2, max_steps=2) == Q(500, 81))
    check("small seed unchecked", lab.disk_majorant(*half, Q(1, 2), max_bits=1) == Q(2, 3))
    check("zero radius bypasses invalid resources", lab.disk_majorant(*half, 0, max_steps=True, max_bits=0) == 0)
    # Discriminating mutations of the returned fields must disagree with the oracle.
    anchor = reference(families[1], Q(1, 2), 1, None)
    swapped = dict(anchor, U=anchor["V"], V=anchor["U"])
    wrong_exponent = dict(anchor, tail_bound=anchor["majorant"]*(Q(1, 2)/anchor["outer_radius"])**3)
    check("detect swapped components", swapped != anchor)
    check("detect wrong exponent", wrong_exponent != anchor)
    after = {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in SOURCE_HASHES}
    check("source bytes unchanged", after == observed)
    report = {"schema": 1, "status": "passed", "python": sys.version,
              "platform": platform.platform(), "source_hashes": observed,
              "case_count": len(rows), "check_count": len(checks), "checks": checks,
              "cases": rows,
              "named_examples": {name: {k: list(map(str, v)) if type(v) is tuple else str(v)
                                        for k, v in result.items()}
                                 for name, result in (("default_last_24", default_result),
                                                      ("manuscript_last_30", worked))},
              "assertion_tested": "Seven exact fields agree with independent ordinary-coefficient/recursive-majorant oracles on the explicit grid; named runtime boundary cases pass.",
              "non_claims": ["No universal Python source-to-Lean refinement proof.",
                             "No proof of the Python interpreter or Fraction/stdlib internals.",
                             "No numerical sampling of the analytic functions is used as a proof of enclosure."]}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({"status": "passed", "cases": len(rows), "checks": len(checks)}))


if __name__ == "__main__":
    main()
