#!/usr/bin/env python3
"""Exact finite checks of two infinite-family proofs, stdlib only.

Command: python3 abc_work/routes/counterexample/verify.py
No primality test on exponentially large generated multipliers is performed.
"""
import hashlib
import json
import math
import platform
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
BASE = ROOT / "abc_work/base/ABC_Square_Kernel_Reverse_Realization_2026-10-25/abc_square_kernel_bridge_20261025/PROOF_NOTE.md"

def factor(n):
    ans = {}
    d = 2
    while d*d <= n:
        while n % d == 0:
            ans[d] = ans.get(d,0)+1
            n //= d
        d = 3 if d == 2 else d+2
    if n > 1:
        ans[n] = ans.get(n,0)+1
    return ans

def radical(n):
    return math.prod(factor(n))

def valuation(n,p):
    e = 0
    while n % p == 0:
        n //= p
        e += 1
    return e

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    started = time.monotonic()
    base_before = sha(BASE)
    fixed = []
    # Formula proofs determine the radical exactly, avoiding factorization of
    # enormous values. All generated c are 2*5**odd and rad(c)=10.
    for k in range(5):
        u = 5**(3+486*k)
        c = 10*u*u
        assert (u-125) % 243 == 0
        assert (c-1) % 243 == 0
        h = (c-1)//243
        t = (u-125)//243
        assert 2430*t*t+2500*t+643 == h
        assert math.gcd(h,243) == 1
        assert 10 <= 243//radical(243)
        # R = rad(h)*3*10 is <= h*30; strict hit follows since c=243h+1.
        assert c > h*30
        fixed.append({"k":k,"u_exponent":3+486*k,"h_bits":h.bit_length(),
                      "h_mod_3":h%3,"output_radical":10,"kernel":10,
                      "multiplier_prime_status":"not tested",
                      "multiplier_squarefree_status":"not tested"})
    varying = []
    for p in [5,7,11,13,17,19,23,29,31]:
        assert factor(p) == {p:1}
        B = p+1
        q = min(factor(B*B+B+1))
        assert q != p and q%2 == 1
        rb = radical(B)
        m = math.prod(r for r,e in factor(B).items() if e%2)
        assert m > 1
        # Both t=1,2 satisfy q**t>=rad(B) in this selected finite sample.
        for t in [1,2]:
            if q**t < rb:
                continue
            n = 3*q**t
            c = B**n
            assert (c-1)%p == 0
            Q = (c-1)//p
            assert math.gcd(p,Q) == 1
            assert valuation(Q,q) == valuation(B**3-1,q)+t
            assert valuation(Q,q) >= t+1
            assert q**t >= rb
            # U(Q)>=q**t, so R=p*rad(Q)*rb <= p*Q*rb/q**t < c.
            assert p*Q*rb <= (c-1)*q**t
            varying.append({"p":p,"B":B,"q":q,"t":t,"n":n,
                            "Q_bits":Q.bit_length(),"output_radical":rb,
                            "squarefree_kernel":m,"v_q_Q":valuation(Q,q),
                            "certified_lower_bound_U_Q":q**t,
                            "full_factorization_Q":"not attempted",
                            "quality_above_1_plus_fixed_epsilon":"not asserted"})
    base_after = sha(BASE)
    assert base_before == base_after
    data = {"status":"completed","assertion_tested":"Exact congruences, multiplier coprimality, kernel/radical formulas, and sufficient ordinary-hit inequality for the explicitly listed parameters.",
            "nonclaims":["No proof or disproof of abc","No prime/squarefree assertion on fixed-Q multipliers","No asymptotic claim that actual abc quality tends to one","No Lean compilation"],
            "command":"python3 abc_work/routes/counterexample/verify.py",
            "python":platform.python_version(),"elapsed_seconds":time.monotonic()-started,
            "input_proof_sha256_before":base_before,"input_proof_sha256_after":base_after,
            "code_sha256":sha(Path(__file__)),"fixed_Q_examples":fixed,"varying_Q_examples":varying}
    (OUT/"results.json").write_text(json.dumps(data,indent=2)+"\n")
    print("PASS",len(fixed),"fixed-Q examples;",len(varying),"prime-multiplier varying-Q examples")

if __name__ == "__main__":
    main()
