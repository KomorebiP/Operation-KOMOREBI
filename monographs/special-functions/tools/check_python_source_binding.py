#!/usr/bin/env python3
"""Adversarial finite controls for the source binder, not a compiler proof."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys

from bind_python_source import ROOT, generate


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("--output must be a new path")
    coupled = (ROOT/"research/coupled_lab.py").read_bytes().decode("utf-8")
    family = (ROOT/"research/family_lab.py").read_bytes().decode("utf-8")
    expected = (ROOT/"lean/CoupledPythonSource.lean").read_bytes().decode("utf-8")
    assert generate(coupled, family) == expected
    cases = [
        ("omit inclusive last coefficient", "coupled", "for n in range(1, last+1):", "for n in range(1, last):"),
        ("old-array index off by one", "coupled", "*u[i]*v[n-1-i]", "*u[i]*v[n-i]"),
        ("wrong derivative binomial", "coupled", "comb(2*n, 2*i+1)", "comb(2*n+1, 2*i+1)"),
        ("wrong product exponent", "coupled", "2*(n-1-i)+1) for i in range(n)", "2*(n-1-i)+3) for i in range(n)"),
        ("wrong second row scales", "coupled", "c*a**i*b**j", "c*a**i*r**j"),
        ("wrong seed denominator", "coupled", "bound = x/(1-x*x)", "bound = x/(1+x*x)"),
        ("wrong majorant update", "coupled", "bound = x*(1+bound*bound)", "bound = x*(1-bound*bound)"),
        ("forward ladder fold", "coupled", "for x in reversed(ladder):", "for x in ladder:"),
        ("late step guard", "coupled", "len(ladder) >= max_steps", "len(ladder) > max_steps"),
        ("changed bit guard", "coupled", ") > max_bits:", ") >= max_bits:"),
        ("unvalidated zero bit limit", "coupled", "max_bits < 1", "max_bits < 0"),
        ("changed default step limit", "coupled", "max_steps=20,", "max_steps=19,"),
        ("changed default bit limit", "coupled", "max_bits=2_000_000", "max_bits=2_000"),
        ("changed default last index", "coupled", "x, last=24,", "x, last=25,"),
        ("changed default outer radius", "coupled", "else max(Q(1),2*x)", "else max(Q(1),3*x)"),
        ("wrong first omitted exponent", "coupled", "tail = majorant*(x/s)**(2*last+3)", "tail = majorant*(x/s)**(2*last+1)"),
        ("wrong partial-series exponent", "coupled", "c*x**(2*n+1) for n,c", "c*x**(2*n+3) for n,c"),
        ("wrong dictionary component", "coupled", '"U":(partial[0],partial[0]+tail)', '"U":(partial[1],partial[1]+tail)'),
        ("wrong dictionary key", "coupled", '"last_index":last', '"retained_count":last'),
        ("wrong dictionary upper endpoint", "coupled", '"V":(partial[1],partial[1]+tail)', '"V":(partial[1],partial[1]-tail)'),
        ("wrong factorial normalization", "family", "Q(a, factorial(2*n+1))", "Q(a, factorial(2*n))"),
        ("invalid-index type guard", "coupled", "type(n) is not int", "not isinstance(n, int)"),
        ("accept equality of outer radius", "coupled", "if s <= x:", "if s < x:"),
    ]
    records = []
    for name, source, before, after in cases:
        text = coupled if source == "coupled" else family
        if before not in text:
            raise AssertionError("Mutation anchor missing: "+name)
        mutated = text.replace(before, after, 1)
        c, f = (mutated, family) if source == "coupled" else (coupled, mutated)
        try:
            # Bypass the whole-file hash deliberately: test structural/translation
            # discrimination, rather than succeeding merely by hash mismatch.
            produced = generate(c, f, require_hash=False)
            rejected = produced != expected
            mechanism = "translated artifact differs"
        except (ValueError, AttributeError, IndexError, TypeError) as exc:
            rejected = True
            mechanism = "closed-fragment rejection: "+str(exc)
        if not rejected:
            raise AssertionError("Undetected mutation: "+name)
        records.append({"name": name, "rejected": True, "mechanism": mechanism})
    # The crucial list is eager, so both rows use one snapshot, not a consumed
    # or later-evaluated generator. This changes structure rather than arithmetic.
    eager = "products = [(comb(2*n, 2*i+1)*u[i]*v[n-1-i], 2*i+1,\n                     2*(n-1-i)+1) for i in range(n)]"
    assert eager in coupled
    lazy = eager.replace("= [", "= (", 1)[:-1]+")"
    try:
        produced = generate(coupled.replace(eager,lazy,1),family,require_hash=False)
        assert produced != expected, "lazy shared products undetected"
        mechanism = "translated artifact differs"
    except (ValueError, AttributeError, IndexError, TypeError) as exc:
        mechanism = "closed-fragment rejection: "+str(exc)
    records.append({"name":"lazy instead of materialized shared products","rejected":True,"mechanism":mechanism})
    # Comments/docstrings do not contribute to the fragment's semantics. The
    # normal pinned-byte mode still rejects an unreviewed file-byte change.
    assert generate("# semantic no-op\n"+coupled, family, require_hash=False) == expected
    report = {"status":"passed", "python":sys.version, "negative_controls":len(records),
              "controls":records,"positive_controls":2,
              "translation_sha256":hashlib.sha256(expected.encode("utf-8")).hexdigest(),
              "limits":"Finite adversarial controls of a trusted binder/template, not proof of compiler correctness."}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"status":"passed","negative_controls":len(records),"positive_controls":2}))


if __name__ == "__main__":
    main()
