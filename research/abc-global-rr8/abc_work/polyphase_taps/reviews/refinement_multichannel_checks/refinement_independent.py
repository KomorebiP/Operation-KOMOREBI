#!/usr/bin/env python3
"""Direct finite checks independent of either author's verifier functions."""
from hashlib import sha256
from math import gcd, lcm, prod
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ROUTE = ROOT / "routes/refinement"


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def factors(n):
    out = {}
    q = 2
    while q*q <= n:
        while n % q == 0:
            out[q] = out.get(q, 0) + 1
            n //= q
        q += 1
    if n > 1:
        out[n] = out.get(n, 0) + 1
    return out


def valuation(n, p):
    assert n != 0
    count = 0
    while n % p == 0:
        n //= p
        count += 1
    return count


def phi(n):
    return sum(gcd(i, n) == 1 for i in range(1, n+1))


def packet(A, B, n):
    c = A**n + B**n
    fs = factors(c)
    contacts = {}
    for p in fs:
        if p == 2:
            continue
        # Directly search the order through 2n; no cyclotomic allocation.
        d = next(j for j in range(1, 2*n+1) if pow(A, j, p) == pow(B, j, p))
        contacts[p] = (d, valuation(A**d - B**d, p))
    occupied = {d for d, s in contacts.values() if s >= 2}
    return {
        "c": c, "U": c // prod(fs),
        "B2": 2**max(0, fs.get(2, 0)-1),
        "W": prod(p**(s-1) for p, (d, s) in contacts.items()),
        "G": prod(p**valuation(n, p) for p in contacts),
        "E": occupied, "degree": sum(phi(d) for d in occupied),
        "contacts": contacts,
    }


def multiply(a, b):
    result = [0]*(len(a)+len(b)-1)
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            result[i+j] += ai*bj
    return result


def exact_monic_quotient(a, b):
    a = a[:]
    assert b[-1] == 1
    quotient = [0]*(len(a)-len(b)+1)
    for i in range(len(quotient)-1, -1, -1):
        q = a[i+len(b)-1]
        quotient[i] = q
        for j, bj in enumerate(b):
            a[i+j] -= q*bj
    assert not any(a)
    return quotient


def main():
    before = {n: digest(ROUTE/n) for n in ["PROOF_NOTE.md", "verify.py", "verification.json"]}
    phase_checks = child_checks = polynomial_checks = blocks = compressions = 0
    for A, B, p in [(2,1,3), (7,1,5), (3,1,7), (8,1,3)]:
        d = next(j for j in range(1, p) if pow(A,j,p) == pow(B,j,p))
        s = valuation(A**d-B**d, p)
        for k in range(1, 4):
            L = d*p**max(0, k-s)
            for radix in [1, 2, 3, 5, 6]:
                for level in range(3):
                    M = radix**level
                    g = gcd(M,L)
                    for j in range(M):
                        period = L//g
                        actual = [t for t in range(period) if (pow(A,M*t+j,p**k)+pow(B,M*t+j,p**k)) % (p**k) == 0]
                        compatible = (L//2-j) % g == 0
                        assert len(actual) == (1 if compatible else 0)
                        for t in range(period):
                            assert ((M*t+j-L//2) % L == 0) == (t in actual)
                            phase_checks += 1
                        child_count = 0
                        for a in range(radix):
                            child_M = M*radix
                            child_j = j+M*a
                            child_period = L//gcd(child_M,L)
                            child_count += any((pow(A,child_M*t+child_j,p**k)+pow(B,child_M*t+child_j,p**k)) % (p**k) == 0 for t in range(child_period))
                        assert child_count == (radix*g//gcd(M*radix,L) if compatible else 0)
                        child_checks += 1
    # Symbolic identity for all r, including r=1, not just allowed plus orders.
    cyclo = {}
    for d in range(1,49):
        numerator = [-1] + [0]*(d-1) + [1]
        denominator = [1]
        for j in range(1,d):
            if d % j == 0:
                denominator = multiply(denominator, cyclo[j])
        cyclo[d] = exact_monic_quotient(numerator, denominator)
    for M in range(1,7):
        for r in range(1,9):
            left = [0]*((len(cyclo[r])-1)*M+1)
            for j, v in enumerate(cyclo[r]):
                left[j*M] = v
            right = [1]
            for d in range(1,M*r+1):
                if d//gcd(d,M) == r:
                    right = multiply(right, cyclo[d])
            assert left == right
            polynomial_checks += 1
    for A in range(2,7):
        for B in range(1,A):
            if gcd(A,B) != 1:
                continue
            for n in range(1,11):
                old = packet(A,B,n)
                assert old["U"] == old["B2"]*old["W"]*old["G"]
                for M in range(1,n+1):
                    if n % M:
                        continue
                    new = packet(A**M,B**M,n//M)
                    H = prod(p**valuation(M,p) for p in old["contacts"])
                    assert new["W"] == old["W"]*H
                    assert old["G"] == new["G"]*H
                    assert old["B2"] == new["B2"]
                    for p,(d,s) in old["contacts"].items():
                        assert new["contacts"][p] == (d//gcd(d,M),s+valuation(M,p))
                    assert old["degree"] <= M*new["degree"]
                    blocks += 1
                m = lcm(2**valuation(n,2), *(d//2 for d in old["E"]))
                small = packet(A,B,m)
                assert n % m == 0 and (n//m) % 2 == 1
                assert old["c"] % small["c"] == 0
                assert old["W"] == small["W"] and old["B2"] == small["B2"]
                assert old["G"] % small["G"] == 0
                assert n % (old["G"]//small["G"]) == 0
                assert old["degree"] <= m
                compressions += 1
    after = {n: digest(ROUTE/n) for n in before}
    assert before == after
    result = {"status":"passed", "full_period_phase_membership_checks":phase_checks,
        "direct_child_existence_checks":child_checks, "symbolic_cyclotomic_identities":polynomial_checks,
        "direct_output_blocking_checks":blocks, "direct_output_compressions":compressions,
        "scope":{"phases":"four listed local examples, k=1..3, N=1,2,3,5,6, r=0..2; every phase and complete residual period including n=0", "symbolic":"M=1..6,r=1..8 over Z[z]", "output":"coprime 1<=B<A<=6,n=1..10,every M|n"},
        "source_sha256_before":before,"source_sha256_after":after,"script_sha256":digest(Path(__file__)),
        "nonclaims":["Finite corroboration only","No ABC proof or universal contact-height bound"]}
    (HERE/"refinement_independent_results.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__ == "__main__":
    main()
