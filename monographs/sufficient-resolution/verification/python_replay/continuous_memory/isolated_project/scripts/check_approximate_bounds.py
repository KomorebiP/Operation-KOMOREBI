#!/usr/bin/env python3
"""Deterministic exact-rational controls; universal claims are proved separately in Lean."""
from fractions import Fraction as F
import itertools
import json
import random
from approximate_certificate import Matrix as M, Model, word, envelope, evaluate, validate_bounds, rational, load

rng = random.Random(20260913)
assertions = 0
negative_controls = 0
words_tested = 0


def check(condition):
    global assertions
    assertions += 1
    if not condition:
        raise AssertionError(f'Exact assertion {assertions} failed')


def reject(fn):
    global negative_controls
    try:
        fn()
    except (ValueError, ArithmeticError):
        negative_controls += 1
    else:
        raise AssertionError('Negative control was accepted')


def random_matrix(n, m):
    return M(tuple(tuple(F(rng.randrange(-3, 4), rng.randrange(1, 5)) for _ in range(m)) for _ in range(n)), m)


def response(a, b, n):
    r = F(0)
    for k in range(n):
        r = a*r + b**k
    return r


systems = 30
for case in range(systems):
    x, z, y, alphabet = case % 5, (case//2) % 4, (case//3) % 3, case % 3
    q, O, V = random_matrix(z, x), random_matrix(y, x), random_matrix(y, z)
    T = tuple(random_matrix(x, x) for _ in range(alphabet))
    U = tuple(random_matrix(z, z) for _ in range(alphabet))
    stable = case % 2 == 0
    if stable:
        T = tuple(t.scale(1/(1+t.norm())) for t in T)
        U = tuple(u.scale(1/(2*(1+u.norm()))) for u in U)
    model = Model(q, T, U, O, V)
    a, b, eps, eta = model.automatic_bounds()
    validate_bounds(model, a, b, eps, eta)
    deltas = model.step_errors()
    p = random_matrix(2, z)
    S = tuple(random_matrix(2, 2) for _ in range(alphabet))
    for n in range(5):
        for w in itertools.product(range(alphabet), repeat=n):
            words_tested += 1
            tw, uw = word(T, w, x), word(U, w, z)
            defect = q@tw - uw@q
            # Independent explicit prefix/injection/suffix sum, rather than recursive implementation.
            terms = M.zero(z, x)
            scalar_sum = F(0)
            for j, i in enumerate(w):
                terms += word(U, w[j+1:], z) @ deltas[i] @ word(T, w[:j], x)
                scalar_sum += (F(1) if j+1==len(w) else __import__('math').prod(b[t] for t in w[j+1:])) * eps[i] * __import__('math').prod(a[t] for t in w[:j])
            fine, coarse, bound = envelope(a, b, eps, w)
            check(defect == terms)
            check(bound == scalar_sum)
            check(defect.norm() <= bound)
            out = O@tw - V@uw@q
            check(out == (O-V@q)@tw + V@defect)
            check(out.norm() <= eta*fine + V.norm()*bound)
            check(tw.norm() <= fine and uw.norm() <= coarse)
            check(F(evaluate(model, w)['output_error_bound']) == eta*fine + V.norm()*bound)
            # Composition through another reduced model.
            sw = word(S, w, 2)
            d2 = p@uw - sw@p
            combined = (p@q)@tw - sw@(p@q)
            check(combined == p@defect + d2@q)
            check(combined.norm() <= p.norm()*defect.norm()+d2.norm()*q.norm())
            # Arbitrary initial-state discrepancy.
            xv, zv = random_matrix(x, 1), random_matrix(z, 1)
            direct = O@tw@xv - V@uw@zv
            check(direct == out@xv + V@uw@(q@xv-zv))
            check(direct.norm() <= (eta*fine+V.norm()*bound)*xv.norm()+V.norm()*coarse*(q@xv-zv).norm())
            # Concatenation recurrence for noncommuting operations.
            k = n//2; u, v = w[:k], w[k:]
            tu, tv = word(T, u, x), word(T, v, x)
            uu, uv = word(U, u, z), word(U, v, z)
            check(defect == (q@tv-uv@q)@tu + uv@(q@tu-uu@q))
            A, B, e = max(a, default=F(0)), max(b, default=F(0)), max(eps, default=F(0))
            check(defect.norm() <= e*response(A, B, n))
            if stable:
                check(defect.norm() <= e/(1-F(1, 2)))
                check(out.norm() <= eta+V.norm()*e/(1-F(1, 2)))
    # Invertible coordinate re-encoding, including empty reduced spaces.
    scale = [F(j+2) for j in range(z)]
    enc = M(tuple(tuple(scale[i] if i==j else F(0) for j in range(z)) for i in range(z)), z)
    dec = M(tuple(tuple(1/scale[i] if i==j else F(0) for j in range(z)) for i in range(z)), z)
    Ur = tuple(enc@u@dec for u in U)
    w = tuple(range(alphabet))*2
    tw, uw, rw = word(T, w, x), word(U, w, z), word(Ur, w, z)
    check(dec@enc == M.identity(z))
    check(rw@enc == enc@uw)
    check((enc@q)@tw-rw@(enc@q) == enc@(q@tw-uw@q))
    check(O@tw-(V@dec)@rw@(enc@q) == O@tw-V@uw@q)

rates=[F(0),F(1,2),F(1),F(3,2),F(2)]
for a, b, n in itertools.product(rates, rates, range(13)):
    H=response(a,b,n)
    check(H == sum((a**j*b**(n-1-j) for j in range(n)),F(0)))
    check((a-b)*H == a**n-b**n)
    check(H == response(b,a,n))
    check(H >= 0)
    if a != b:
        check(H == (a**n-b**n)/(a-b))
    if a == b and n:
        check(H == n*a**(n-1))
    if a <= 1 and b <= 1:
        check(H <= n)
    if a <= 1 and b < 1:
        check(H <= 1/(1-b))
    if b <= 1 and a < 1:
        check(H <= 1/(1-a))
    if a >= b:
        check(abs(a**n-b**n) == (a-b)*H)
for e in [F(1,100),F(1,10),F(1,2),F(2)]:
    for n in range(30):
        check(n*e <= (1+e)**n-1)

one=M.identity(1)
known=Model(one,(one.scale(F(2)),),(one,),one,one)
reject(lambda: validate_bounds(known,[F(2)],[F(1)],[F(0)],F(0)))
reject(lambda: validate_bounds(known,[F(1)],[F(1)],[F(1)],F(0)))
reject(lambda: validate_bounds(known,[F(2)],[F(1)],[F(-1)],F(0)))
reject(lambda: validate_bounds(known,[],[F(1)],[F(1)],F(0)))
wrongread=Model(one,(one,),(one,),one.scale(F(2)),one)
reject(lambda: validate_bounds(wrongread,[F(1)],[F(1)],[F(0)],F(0)))
reject(lambda: rational(0.1))
reject(lambda: rational('1/0'))
reject(lambda: rational(True))
reject(lambda: M.parse([[1,2]],1,1))
reject(lambda: word((one,),[1],1))
# Ensure reversing a word would be detected rather than silently accepted.
A=M.parse([[0,1],[0,0]],2,2);B=M.parse([[0,0],[1,0]],2,2)
check(word((A,B),[0,1],2) != word((A,B),[1,0],2))
print(json.dumps({'passed':True,'assertions':assertions,'systems':systems,
                  'words_tested':words_tested,'negative_controls':negative_controls,
                  'seed':20260913,'arithmetic':'exact rational; induced infinity norm',
                  'range':'dimensions 0..4/0..3/0..2; alphabets 0..2; words through length 4; scalar depths 0..29',
                  'boundary':'Finite Python tests, not executable-code verification or proof of universal claims.'}))
