#!/usr/bin/env python3
"""Bounded exact checks supporting regular_address_transversality.md.

This checks identities and examples, not universal Euler simplicity and not
actual Bernoulli coefficients. Universal assertions require the prose proof.
"""
from __future__ import annotations
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import time

BASE = Path(__file__).resolve().parent

def v2(n: int) -> int:
    if n == 0:
        raise ValueError("v2(0) is not requested by the finite checker")
    n = abs(n)
    return (n & -n).bit_length() - 1

def facval(n: int) -> int:
    return n - n.bit_count()

def theta(n: int) -> int:
    assert n >= 1
    return 3*n + 1 + (n-1).bit_count()

def chart(n: int, i: int) -> tuple[int, int]:
    assert 0 <= i < n
    g = facval(i) + facval(n-1-i)
    h = max(i, n-1-i).bit_length()
    return g, h

def product_derivative(a: int, x: int) -> tuple[int, int]:
    p, d = 1, 0
    for i in range(a):
        f = (x-i)*(2*x-2*i-1)
        fp = 4*x-4*i-1
        p, d = p*f, d*f+p*fp
    return p, d

def run() -> dict:
    started = time.monotonic()
    counts = {"lower_partition_points": 0, "lower_skeleton_derivatives": 0,
              "factorial_threshold_identities": 0, "translated_complement_geometry": 0,
              "critical_scale_identities": 0, "record_examples": 0}
    for a in range(1, 65):
        charts = [chart(a,i) for i in range(a)]
        assert min(g+h for g,h in charts) == facval(a)
        counts["factorial_threshold_identities"] += 1
        maxh = max(h for _,h in charts)
        for x in range(1 << (maxh+3)):
            hits = [i for i,(_,h) in enumerate(charts) if (x-i) % (1<<h) == 0]
            assert len(hits) == 1, (a,x,hits)
            ell = hits[0]
            g,h = charts[ell]
            p,d = product_derivative(a,x)
            assert d != 0 and v2(d) == g, (a,x,ell,g,d)
            if p:
                assert v2(p) == g+v2(x-ell)
            counts["lower_partition_points"] += 1
            counts["lower_skeleton_derivatives"] += 1
    # The parity-exclusion geometry depends only on a<2^t and 2^t|k.
    # Check all such lower addresses through 12, t through 7, c in {1,3,5,7}.
    for t in range(1,8):
        for c in (1,3,5,7):
            k = (1<<t)*c
            for a in range(1,min(12,(1<<t)-1)+1):
                for i in range(k):
                    _,H = chart(k,i)
                    assert H >= t
                    for ell in range(a):
                        n = i+a-ell
                        if n % (1<<H) == 0:
                            assert n == (1<<H), (t,c,k,a,i,ell,H,n)
                            counts["translated_complement_geometry"] += 1
    # Formula (12), independent integer arithmetic in small domains. The
    # identity itself does not need t>=Theta(a); validity as a wall does.
    for a in range(1,17):
        for t in range(4,9):
            for c in (1,3,5,7,9):
                k=(1<<t)*c
                for b in range(c):
                    for rho in (0,1,(1<<t)-2,(1<<t)-1):
                        i=(1<<t)*b+rho
                        d=facval(i)+facval(k-1-i)
                        assert d == k-1-t-b.bit_count()-(c-1-b).bit_count()
                        bv=v2(math.comb(c-1,b))
                        for ell in range(a):
                            g,_=chart(a,ell)
                            D=t-theta(a)
                            delta=d+D-g
                            L=theta(k)+delta
                            assert L==4*k+t-theta(a)-g-bv
                            counts["critical_scale_identities"] += 1
    for k,a,expected_t,expected_L in ((256,2,8,777),(4096,3,12,12301)):
        vals=[theta(n) for n in range(1,k+a+1)]
        maximum=max(vals)
        first=vals.index(maximum)+1
        assert first==k and maximum==expected_L and v2(k)==expected_t
        counts["record_examples"] += 1
    assert 4*4096+12-theta(3)==16385
    assert theta(256)==777
    table=[]
    for a in range(1,17):
        regular=all(theta(a)>theta(n) for n in range(1,a))
        if regular:
            table.append({"a":a,"theta_a":theta(a),"factorial_valuation":facval(a),
                          "closed_t_values":list(range(theta(a),theta(a)+facval(a)))})
    return {"status":"PASS","domain":"exact Python integers",
            "claim_scope":"Bounded implementation checks of the skeleton derivative, partition, geometry, critical-scale identity, and examples. Not an Euler coefficient certificate or universal proof.",
            "bounds":{"lower_address_max":64,"lower_x_modulus":"2^(max lower-chart h + 3)",
                      "geometry_t":"1..7","geometry_c":[1,3,5,7],"geometry_a":"1..min(12,2^t-1)",
                      "critical_a":"1..16","critical_t":"4..8","critical_c":[1,3,5,7,9],
                      "critical_rho":"0,1,2^t-2,2^t-1"},
            "counts":counts,"complete_simplicity_bands":table,
            "software":{"python":sys.version,"platform":platform.platform()},
            "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "elapsed_seconds":time.monotonic()-started}

if __name__ == "__main__":
    result=run()
    out=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else BASE/"CHECK_REGULAR_ADDRESS.json"
    out.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({"status":result["status"],"counts":result["counts"],
                      "elapsed_seconds":result["elapsed_seconds"],"output":str(out)},indent=2))
