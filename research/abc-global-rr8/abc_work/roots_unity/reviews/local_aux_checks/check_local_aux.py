#!/usr/bin/env python3
"""Independent audit checks; redirect author-script outputs to this directory."""
from pathlib import Path
from fractions import Fraction
from math import gcd
import contextlib
import hashlib
import io
import json
import runpy

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]
WORK = PROJECT.parent
TRACKED = [PROJECT/'routes'/route/name for route in ('padic', 'auxiliary')
           for name in ('PROOF.md', 'verify.py', 'results.json')]
TRACKED += [WORK/'LATEST.md', WORK/'routes/global/PROOF_NOTE.md']

def hashes():
    return {str(p.relative_to(WORK)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in TRACKED}

def vp(x, p):
    if x == 0:
        return None
    e = 0
    while x % p == 0:
        x //= p
        e += 1
    return e

def truncated_vp(x, p, k):
    x %= p**k
    return k if x == 0 else vp(x, p)

def ord_mod(a, p):
    return next(d for d in range(1, p) if pow(a, d, p) == 1)

def brute_lift(x, d, p, k):
    modulus = p**k
    candidates = [x+j*modulus for j in range(p)
                  if pow(x+j*modulus, d, p*modulus) == 1]
    assert len(candidates) == 1
    return candidates[0]

def determinant(matrix):
    mat = [[Fraction(x) for x in row] for row in matrix]
    ans = Fraction(1)
    for col in range(len(mat)):
        pivot = next((r for r in range(col, len(mat)) if mat[r][col]), None)
        if pivot is None:
            return 0
        if pivot != col:
            mat[pivot], mat[col] = mat[col], mat[pivot]
            ans = -ans
        pivot_value = mat[col][col]
        ans *= pivot_value
        for j in range(col, len(mat)):
            mat[col][j] /= pivot_value
        for row in range(col+1, len(mat)):
            multiple = mat[row][col]
            for j in range(col, len(mat)):
                mat[row][j] -= multiple*mat[col][j]
    assert ans.denominator == 1
    return ans.numerator

before = hashes()
author_runs = {}
original_write_text = Path.write_text
redirects = {PROJECT/'routes'/route/'results.json': HERE/(route+'_rerun.json')
             for route in ('padic', 'auxiliary')}

def redirected_write_text(path, data, *args, **kwargs):
    target = redirects.get(path.resolve())
    assert target is not None, ('Unexpected author-script write', str(path))
    return original_write_text(target, data, *args, **kwargs)

Path.write_text = redirected_write_text
try:
    for route in ('padic', 'auxiliary'):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            runpy.run_path(str(PROJECT/'routes'/route/'verify.py'), run_name='__main__')
        author_runs[route] = stdout.getvalue().strip()
finally:
    Path.write_text = original_write_text

# Inspect the exact saved examples, independently of the generator's lift formula.
padic_saved = json.loads((PROJECT/'routes/padic/results.json').read_text())
padic_rerun = json.loads((HERE/'padic_rerun.json').read_text())
assert padic_saved['examples'] == padic_rerun['examples']
assert padic_saved['code_sha256'] == before['roots_unity/routes/padic/verify.py']
assert padic_saved['input_hashes_before'] == padic_saved['input_hashes_after']
assert padic_saved['input_hashes_after'] == {
    'LATEST.md': before['LATEST.md'],
    'routes/global/PROOF_NOTE.md': before['routes/global/PROOF_NOTE.md']}
for row in padic_saved['examples']:
    p,n,e,A = (row[x] for x in ('p','n','depth','A'))
    assert vp(A**n+1,p) == vp(A**(2*n)-1,p) == e
    assert ord_mod(A,p) == 2*n
    assert p**e <= A < 3*p**e
    assert p**(e-1) < A

# All units modulo p^k for the indicated finite domain; covers d=1 exactly.
torsion_cases = 0
projection_cases = 0
for p in (3,5,7,11,13,17,19):
    roots = {}
    for residue in range(1,p):
        d = ord_mod(residue,p)
        x = residue
        for k in range(1,4):
            roots[residue,k] = x
            x = brute_lift(x,d,p,k)
    for k in range(1,4):
        modulus = p**k
        for t in range(1,modulus):
            if t % p == 0:
                continue
            d = ord_mod(t,p)
            z = roots[t%p,k]
            u = t*pow(z,-1,modulus) % modulus
            depth = truncated_vp(pow(t,d,modulus)-1,p,k)
            assert depth == truncated_vp(t-z,p,k)
            assert depth == truncated_vp(u-1,p,k)
            torsion_cases += 1
    for residue in range(1,p):
        d = ord_mod(residue,p)
        for k in (1,2):
            modulus = p**k
            z = roots[residue,k]
            for r in range(d):
                for m in range(2*d+2):
                    total = sum(pow(z,j*(m-r),modulus) for j in range(d))
                    coefficient = total*pow(d,-1,modulus) % modulus
                    assert coefficient == (int((m-r)%d == 0) % modulus)
                    projection_cases += 1

# Direct small-base exponent-lifting identity, including n=1 and p|n.
lifting_cases = 0
for p in (3,5,7,11,13,17,19):
    for A in range(2,31):
        for B in range(1,A):
            if (A*B)%p == 0:
                continue
            d = ord_mod(A*pow(B,-1,p)%p,p)
            for n in range(1,31):
                if (pow(A,n,p)+pow(B,n,p))%p:
                    continue
                assert d%2 == 0
                assert (2*n)%d == 0 and ((2*n)//d)%2 == 1
                assert vp(A**n+B**n,p) == vp(A**d-B**d,p)+vp(n,p)
                lifting_cases += 1

# Direct brute Hensel search for missing smallest n=1,p=3 and n=2,p=5.
boundary_contacts = []
for n,p,residue in ((1,3,2),(2,5,2)):
    x = residue
    for e in range(1,6):
        candidates = [x+j*p**e for j in range(p)
                      if (pow(x+j*p**e,n,p**(e+1))+1)%p**(e+1) == 0]
        assert len(candidates) == 1
        next_x = candidates[0]
        j = (next_x-x)//p**e
        k = 2 if j == 1 else 1
        A = x+k*p**e
        assert vp(A**n+1,p) == vp(A**(2*n)-1,p) == e
        assert ord_mod(A,p) == 2*n
        assert p**e <= A < 3*p**e
        boundary_contacts.append({'n':n,'p':p,'e':e,'x':x,'j':j,'A':A})
        x = next_x

# At n=1 the entire W is exactly p^(e-1), with no factorization oracle.
small_n_cases = 0
for p in (3,5,7,11):
    for e in range(1,13):
        A = p**e-1
        assert A+1 == p**e and ord_mod(A,p) == 2
        assert vp(A*A-1,p) == e
        small_n_cases += 1

# Auxiliary A3, extended range, enumerated independently by first attainable height.
minimum_cases = []
for M in range(1,201):
    observed = None
    for H in range((M+2)//3+1):
        witnesses = [(u,v) for u in range(-H,H+1) for v in range(-H,H+1)
                     if u+2*v and (u+2*v)%M == 0]
        if witnesses:
            observed = H
            break
    assert observed == (M+2)//3
    minimum_cases.append((M,observed))

# All maximal minors of the adjacent-relation matrix: gcd 1 proves saturation.
# Domain includes equality A=B=1 and reverse order, absent from authors' finite run.
integral_basis_cases = 0
for A in range(1,11):
    for B in range(1,11):
        if gcd(A,B) != 1:
            continue
        for D in range(1,7):
            rows = []
            coeff = [A**j*B**(D-j) for j in range(D+1)]
            for j in range(D):
                row = [0]*(D+1)
                row[j],row[j+1] = -A,B
                assert sum(u*v for u,v in zip(row,coeff)) == 0
                rows.append(row)
            signed_minors = [(-1)**j*determinant([[row[k] for k in range(D+1) if k!=j]
                                                 for row in rows])
                             for j in range(D+1)]
            assert signed_minors == coeff
            assert gcd(*signed_minors) == 1
            integral_basis_cases += 1

M = 1093**2
assert M == 1194649 and (M+2)//3 == 398217
assert (pow(2,182,M)+1)%M == 0
assert (pow(2,182,1093**3)+1)%1093**3 != 0
assert ord_mod(2,1093) == 364
assert (-2)+2*1 == 0

auxiliary_saved = json.loads((PROJECT/'routes/auxiliary/results.json').read_text())
auxiliary_rerun = json.loads((HERE/'auxiliary_rerun.json').read_text())
assert auxiliary_rerun['minimum_height_cases'] == 100
assert auxiliary_rerun['independent_zero_vector_cases'] == 186
assert auxiliary_saved['input_sha256_before']['verify.py'] == before['roots_unity/routes/auxiliary/verify.py']

assert hashes() == before, 'Author artifacts changed during this audit run'
summary = {
    'status':'passed',
    'author_runs_redirected':author_runs,
    'author_artifacts_unchanged':True,
    'source_sha256':before,
    'checks':{
        'saved_padic_examples':len(padic_saved['examples']),
        'all_units_truncated_torsion':{'primes':[3,5,7,11,13,17,19],'k':[1,3],'cases':torsion_cases},
        'monomial_projection':{'primes':[3,5,7,11,13,17,19],'k':[1,2],'r':'0..d-1','m':'0..2d+1','cases':projection_cases},
        'plus_lifting':{'primes':[3,5,7,11,13,17,19],'A':[2,30],'B':'1..A-1, p not dividing AB','n':[1,30],'cases':lifting_cases},
        'n1_small_prime_boundaries':boundary_contacts,
        'small_n_W_exact_cases':small_n_cases,
        'auxiliary_minimum_height':{'M':[1,200],'cases':len(minimum_cases)},
        'auxiliary_integral_basis':{'A':[1,10],'B':[1,10],'coprime':True,'D':[1,6],'cases':integral_basis_cases},
        '1093_example':{'modulus':M,'minimum_nonzero_evaluation_height':398217,'order':364,'valuation':2}
    },
    'auxiliary_saved_result_hash_matches_current_proof':auxiliary_saved['input_sha256_before']['PROOF.md'] == before['roots_unity/routes/auxiliary/PROOF.md'],
    'nonclaims':['No universal height estimate or ABC claim is computationally proved.','Integral basis uniform statement is proved separately in the review, not inferred from finite minors.']
}
(HERE/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
