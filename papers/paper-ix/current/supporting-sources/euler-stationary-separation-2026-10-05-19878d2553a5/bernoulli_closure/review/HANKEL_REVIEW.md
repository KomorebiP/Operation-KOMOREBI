# Independent audit: dyadic Bernoulli Hankel valuations

Reviewer: `radix_review`, 2026-10-05. No author files were edited. No Lean
build was run. The recurrence source was independently authenticated and
the critical infinite-dimensional arguments were reconstructed before
accepting the author's conclusion.

## Claim and verdict

With B_1=-1/2, let

    D(z)=sum_(h>=0) 2^h B_h binom(2z,h),  z in Z_2.

The principal claim is: for every x in Z_2, every nonzero q in Z_2, and
every integer m>=1,

    v_2 det[D(x+(i+j)q)]_(0<=i,j<m)
      =m(m-1)(2+v_2(q))+4 sum_(k=0)^(m-1)v_2(k!).

The second claim concerns **unit-step actual Bernoulli matrices**. For
ordinary r>=1 and m>=1 satisfying

    2r-1 > 4(m-1)+4v_2((m-1)!),

one has

    v_2 det[2B_(2(r+i+j))]_(0<=i,j<m)
      =2m(m-1)+4 sum_(k=0)^(m-1)v_2(k!).

**Primary verdict: proved as written.** The two claims follow from the
authenticated orthogonal recurrence and the completed-lattice proofs in
the reviewed notes. Their quantifiers, normalization, and precision
losses pass the independent audit. The transfer threshold is a sufficient
bound proved by this lattice argument; no optimality of its full range
is asserted. The all-step depleted theorem does not automatically give
the same threshold for actual nonunit-step Bernoulli matrices.

These are auxiliary actual-coefficient theorems. They do **not** prove
the target Phi_r(2^(2r-25))!=0, and the reviewed residual pairing does
not misidentify Phi with a Hankel determinant.

The later actual-chart addition was also independently audited. Its
congruences Xi(U)=1+U mod 2 and Xi(1+8V)/4=1+2V mod 4, and the resulting
constant-times-square exclusion, are proved in the precise fixed-x
scope below. This addition does not change the preceding Hankel verdict.

## 1. Dependency graph and obligations

The proof dependencies are:

1. Bernoulli convention, valuation, and binomial expression -> restricted
   analytic D, with D(n)=(2-4^n)B_(2n).
2. Authenticated Bernoulli orthogonal recurrence -> centered zero-diagonal
   recurrence -> even contraction with exact b_n,a_n.
3. Norm valuation -> orthogonal unit-norm lattice e_n -> bounded
   multiplication operator J=I mod 4 -> continuous dyadic powers J^x.
4. Second factorial lattice f_n -> K=(J-I)/4 has upward coefficient 1 ->
   normalized step V_q=K mod 2 -> unique odd exterior coordinate -> exact
   all-step determinant valuation.
5. Exact ordinary-index undepletion -> explicit loss from dividing by
   c_i c_j -> unit determinant after perturbation -> actual unit-step
   transfer.
6. Actual packet product identity -> exact linear moment pairing for the
   Euler residual. A further arrow from simultaneous linear contact to
   a vanishing Hankel norm or principal Schur complement is missing.

| Obligation | Status | Decisive check |
|---|---|---|
| Restricted analyticity of D | Passed | The h=2n term has Gauss valuation at least n+s_2(n)-1, tending to infinity. |
| D(n), midpoint identity, n=0 convention | Passed | The binomial Bernoulli polynomial identity gives D(n)=4^n B_(2n)(1/2); the value at 0 is1. |
| D=1+4z+16R and 2-by-2 law | Passed | The first four nonzero summands reproduce the displayed polynomial; the remaining Gauss bound is at least 4. |
| Recurrence sign and scaling | Passed | The primary source's t_n is negative; scaling X=2u+1 multiplies it by 4. |
| Even contraction | Passed | Applying the centered recurrence twice gives b_n=rho_(2n)+rho_(2n+1), a_n=rho_(2n)rho_(2n-1). |
| Integral unit-norm lattice | Passed | v_2(a_n)=4+4v_2(n), so dividing P_n by 4^n(n!)^2 gives unit norms. |
| Infinite c_0 completion | Passed | J is uniformly bounded and tridiagonal; the diagonal unit bilinear form and its finite exterior powers are continuous. |
| Dyadic powers and shifted moment identity | Passed | Operator-norm convergence and density of nonnegative integers justify the extension; the group and adjoint identities persist by continuity. |
| Arbitrary nonzero q, including nonunits | Passed | Dividing by 4q gives the displayed convergent operator series, whose coefficients after K are even. |
| Factorial exterior divisibility | Passed | For an increasing tuple i_j, i_j>=j, so product(i_j!/j!)^2 is integral. |
| No cancellation of the leading exterior norm | Passed | After normalization the wedge reduces to precisely one basis vector modulo 2. |
| Actual undepletion precision | Passed | The entry loss is v_2(c_i)+v_2(c_j); the printed strict inequality makes every normalized perturbation entry even. |
| Exact residual pairing and stated Schur example | Passed | Reconstructed from the packet product law and checked directly at r=1,y=1. |
| Actual stationary nonvanishing | Not addressed by the determinant theorem | The residual equations are linear pairings, not the audited Gram determinant. |

## 2. Reconstruction of the critical infinite-lattice proof

Write rho_n=-n^4/(4n^2-1), with rho_0=0, and let P_n be the monic
orthogonal polynomials for L(U^n)=D(n). Their norms satisfy

    L(P_n^2)=product_(k=1)^n a_k,
    v_2 L(P_n^2)=4n+4v_2(n!).

For c_n=4^n(n!)^2 and e_n=P_n/c_n, the diagonal norms are units.
The upward and downward entries of multiplication by U are respectively
4(n+1)^2 and a_n/(4n^2), and b_n=1 mod 4. Thus J=I+4K is bounded on
c_0(e). The bilinear form sum h_i u_i v_i converges for u,v in c_0(e)
and is bounded by the product of their supremum norms. No real
positivity or Hilbert-space spectral theorem is needed.

For each z in Z_2, the series defining J^z converges uniformly in
operator norm. It is continuous in z. Ordinary powers establish both
J^(x+y)=J^x J^y and self-adjointness; continuity extends them to dyadic
x,y. The equality D(z)=<e_0,J^z e_0> likewise holds first on dense
ordinary nonnegative integers, then throughout Z_2. Consequently the
all-step matrix is the J^x-weighted Gram matrix of J^(iq)e_0.

The second basis f_n=(n!)^2 e_n is important. Direct substitution gives
for K in this basis: upward coefficient 1, downward coefficient a_n/16,
and diagonal (b_n-1)/4. All are integral and uniformly bounded. The
diagonal map from c_0(f) to c_0(e) is bounded and intertwines K, J, and
their convergent power series.

For q!=0,

    V_q=(J^q-I)/(4q)
       =K+sum_(l>=2) 4^(l-1)/l * binom(q-1,l-1) K^l.

The binomial factor is integral for q in Z_2. The remaining scalar has
valuation 2l-2-v_2(l)>=1 and tends to zero in norm. Thus V_q=K mod 2
on c_0(f), even when q is highly divisible by 2.

Now take the wedge of V_q^i f_0, for 0<=i<m. Modulo2, its ith column
is K^i f_0, supported in indices0,...,i and with coefficient 1 at i.
Hence the exterior coefficient at I_0=(0,...,m-1) is odd, and every
other increasing-tuple coefficient is even. This follows from the
triangular support, not from a finite experimental rank.

Let d_I=product_(i in I)(i!)^2. For I=(i_0<...<i_(m-1)), each i_j>=j,
so d_I/d_I0 is integral. After passage to the e exterior basis and
division by d_I0, the wedge therefore remains a c_0 vector and reduces
to e_I0 modulo 2. The weighted exterior form has diagonal unit entries
modulo 2 because J^x=I mod 4. Its value on that normalized wedge is odd.
There is consequently no cancellation at the claimed leading
valuation 2v_2(d_I0)=4 sum v_2(i!).

Finite exterior powers cause no completion problem: construct them on
finite-support vectors with the supremum norm, where the determinant
identities are finite, then extend by continuity. All operators used
above have norm at most1. The diagonal map after division by d_I0 also
has norm at most1 on this fixed exterior degree. Thus all infinite sums
are limits of valid finite identities.

Finally J^(iq)=(I+4qV_q)^i. The finite triangular change of the m
vectors has determinant product_(i<m)(4q)^i, and this determinant is
squared in the Gram determinant. Its valuation is
m(m-1)(2+v_2(q)), giving exactly the claimed formula. The case m=1
reduces to the already proved unit property of D. The excluded case
q=0 would have determinant zero for m>1 and is not silently included.

## 3. Actual ordinary-index transfer and its limits

For ordinary r>=1, the exact identity is

    2B_(2(r+n))=D(r+n)/(1-2^(2r+2n-1)).

Since D(r+n) is a unit, the difference from D(r+n) has valuation
exactly 2r+2n-1. For any integral polynomial P, the resulting functional
error has valuation at least 2r-1. The P_i have integral coefficients,
so application to P_iP_j and division by c_i c_j loses at most

    v_2(c_i)+v_2(c_j)
       <=4(m-1)+4v_2((m-1)!).

The printed strict inequality makes the normalized perturbation even.
The depleted shifted Gram determinant is a unit in the e basis, so
the actual one remains a unit. Returning to monomials multiplies the
determinant by product c_i^2 and establishes the stated valuation.

This precision reasoning is valid entry by entry and needs no estimate
on the huge ordinary value of r beyond the displayed inequality. It
does not prove the same transfer for a nonunit or general dyadic step.
For m=2, actual r=1 and r=2 give valuations 1 and 3 instead of 4; r=3
satisfies the criterion and gives 4. Those controls confirm that
undepletion cannot simply be suppressed at all indices. They do not
establish optimality of the threshold at every m.

## 4. Exact source authentication

The source independently inspected is Karl Dilcher and Lin Jiu,
*Hankel Determinants of shifted sequences of Bernoulli and Euler
numbers*, arXiv:2105.01880v1, stamped 5 May 2021. The official PDF opened
at https://arxiv.org/pdf/2105.01880 carries that exact version stamp.
The direct versioned URL initially failed to fetch; the version was
authenticated from the PDF itself rather than inferred from the URL.
Checked 2026-10-05.

The extracted input is Eq. (2.4), together with the displayed recurrence
coefficients in the proof of Proposition 3.1, printed p.8 immediately
after Eq. (3.11): their convention is P_(n+1)=(y+s_n)P_n-t_n P_(n-1),
with s_n=1/2 and t_n=-n^4/[4(2n+1)(2n-1)]. The source attributes this
recurrence to Touchard. Its Bernoulli convention is B_1=-1/2.

The notation translation is X=2y+1 and Q_n(X)=2^n P_n((X-1)/2).
The diagonal disappears and the subdiagonal becomes 4t_n=rho_n.
Applying this recurrence twice gives the contracted a_n,b_n used in
the proof. This translation was reconstructed directly.

Authentication, extraction, and application all pass for this recurrence
input. The source does not supply the present dyadic shifted-lattice
theorem or an Euler stationary-value theorem. The check is an exact
theorem/notation verification, not a novelty search. No global novelty
conclusion is made. No local PDF file was created by this reviewer, so
no PDF content hash is asserted. The official URL, version stamp, and
exact formula locator are recorded instead.

## 5. Residual bridge audit

With the source-packet polynomial distinguished from the orthogonal
P_n, the packet product law is

    P_(r+q)(r+y)=P_r(r+y)P_q(y).

For gamma_n=8^n beta_n/D(n), the coefficientwise moment pairing
L_r(U^q)=D(r+q) therefore gives precisely the analytically continued
Euler tail divided by P_r. Its y derivative is also legitimate: the
coefficient valuations grow at least 3(r+q), and the source factors and
their derivatives are integral restricted analytic.

The example W_1(1,U)=40/3+(64/7)U was checked independently. Its mean
is -8/45, the relevant moment determinant is 48/175, and the displayed
Schur complement is -589824/8575. For an ordinary odd y the exact
degree of W_r(y,U) is odd, so it is not a nonzero scalar times a
polynomial square. This excludes only that literal representation.

A zero linear pairing L_r(w)=0 is fully compatible with a nonzero norm
L_r(w^2). The vector U-D(r+1)/D(r) is an explicit example. Thus the
reviewed distinction between the contact equations and a Gram/Schur
nonvanishing theorem is necessary and correct. The remaining Euler
gap is an additional, actual-coefficient identity converting contact
into a forbidden Gram degeneracy; that identity is absent here.

## 5a. Uniform actual-chart square obstruction

This addition concerns the admitted actual terminal161 family
r=(17659+2^18 T)2^640-161, ordinary T>=0, mu_r=-154, and every fixed
x=10202+2^15 Z with Z in Z_2. Let gamma_(r,q) be the prescribed
normalized coefficients of G_r, and define

    Psi_(r,x)(U)=sum_q gamma_(r,q)P_q(x)A(x-q)/D(r+q) U^q,
    Xi_(r,x)(U)=D(r)2^(-154)Psi_(r,x)(U).

The moment pairing is exactly L_r(Psi)=G_r(x). This section's U and V
congruences are coefficientwise for each fixed x, uniformly in x. They
do not claim a joint Gauss congruence in Z; the pointwise integer-valued
polynomial bound P_q(x) in q!Z_2 would not alone justify that stronger
interpretation.

For Xi=sum a_q U^q, the exact q=0 term is A(x). Direct cancellation of
the actual Bernoulli factors in the q=1 term gives

    a_1=16P_1(x)A(x-1)/((2r-1)(r+1))
              * (1-epsilon)/(1-4epsilon),
    epsilon=2^(2r-1).

This cancellation uses the actual beta coefficients and
D(n)=2(1-2^(2n-1))B_(2n); it introduces no free coefficients.

The low-index valuation formula was independently reconstructed as
v_2(gamma_(r,q))=5q-164+v_2((321-2q)!) for 1<=q<=160. Adding the
pointwise bound v_2(P_q(x))>=v_2(q!) and subtracting 154 gives

    v_2(a_q)>=4q+3-s_2(321-2q)-s_2(q).

The values at q=2,3,4 are 4,7,13. For 5<=q<=160, the elementary
digit-sum estimates in the note give at least 3q-4>=11. For q>=161,
the true-terminal hypothesis gives v_2(gamma_(r,q))>=0 and the
factorial bound gives v_2(a_q)>=v_2(q!)-154>=4, tending to infinity.
Thus every coefficient with q>=2 is divisible by 16 and the U series
converges. This tail statement is a proof, not an extrapolation of the
finite chart samples.

The source computations give A(10202)=5 mod 16 and A(10201)=7 mod 16.
After removing the fixed factor 2^5 from r+1, the q=1 expression is a
dyadic unit and gives a_1=15 mod 16. The same conclusion follows from
(9^10202-1)/25840 mod 16. The changes in r are divisible by 2^640 and
the changes in x by 2^15; after the displayed fixed denominator losses,
both residues remain unchanged. The undepletion factor is 1 modulo 16.
Consequently, for all chart points,

    Xi(U)=1+U mod 2,
    Xi(1+8V)=4+8V mod 16,
    F(V):=Xi(1+8V)/4=1+2V mod 4.

All three congruences pass. The first excludes a nonzero scalar times
a square in Q_2<U>: normalize the Gauss valuations, then reduce modulo 2;
a square polynomial in characteristic 2 has no odd-degree monomial,
whereas 1+U does.

The stronger natural-disc exclusion has an even simpler pointwise
proof. F(0) and F(1) are units with F(1)/F(0)=3 modulo 4. If
Xi(1+8V)=c H(V)^2 for any fixed nonzero c in Q_2 and Q_2-valued H
at these two arguments, that ratio would be a dyadic square. A unit
square is 1 modulo 8, a contradiction. Thus the exclusion holds even
without analytic regularity of H, on the two actual odd-square
arguments U=1 and U=9. The claimed analytic-square exclusion is valid.

The reviewer independently recomputed a_0=5, a_1=15 modulo 16 at the
actual base index, the q=3,...,160 lower-bound minimum 7, and the
q>=161 lower bound 4. The author's expanded checker additionally
verifies nine ordinary chart representatives. The uniformity comes
from the algebra and valuation bounds above, not those nine samples.

This closes the literal constant-times-square kernel proposal. It
does not exclude a different weight, a sum of squares, an operator
representation, or an identity available only under stationarity.
The companion quadratic-form classification mentioned in the author's
new section is covered by its separate independent review; it is not
rederived in this report.

## 6. Computation replay and independent dyadic check

Both author checkers were inspected and replayed with temporary output
paths, leaving author files unchanged. Both outputs were byte-identical
to the current certified results. For hankel_bridge the current run is
certified_run_final, after the actual-chart addition; certified_run is
superseded development evidence.

- nonintersection: 36 exact orthogonality checks, 9 unit-norm checks,
  72 depleted unit-step checks, and 232 actual transfer checks.
- hankel_bridge: 300 exact determinant checks, 54 exact actual-row checks,
  12 factorial-lattice checks, and 9 actual-chart representatives.

Both manifests passed artifact verification with:

```
python3 audit_helpers/validate_manifest.py --root /workspace/scratch/fa86fc5a0e51 bernoulli_closure/nonintersection/certified_run/manifest.json
python3 audit_helpers/validate_manifest.py --root /workspace/scratch/fa86fc5a0e51 bernoulli_closure/hankel_bridge/certified_run_final/manifest.json
```

The reviewer separately evaluated the defining Bernoulli series modulo
2^96 at genuinely nonintegral dyadic shifts and steps, without using
the Jacobi recurrence to generate the moments. Bernoulli numbers were
generated by their elementary rational recurrence; only h<192 was
retained. Every omitted even term h=2n>=192 has Gauss valuation at
least n+s_2(n)-1>=96, and odd h>1 vanish. Integer Bareiss elimination
then computed the determinant residue. All predicted valuations were
strictly below 96.

| x | q | valuations at m=1,2,3,4 |
|---|---|---|
| -1/3 | 1/3 | 0,4,16,32 |
| 2/5 | -2/7 | 0,6,22,44 |
| -4/3 | 4/5 | 0,8,28,56 |
| 3/7 | -1 | 0,4,16,32 |

All 16 cases passed. These checks support the infinite proof but do not
replace it. The independent code is included below for reproducibility.

```python
from fractions import Fraction as F
from math import comb, factorial
from functools import lru_cache

M = 96
modulus = 1 << M
B = [F(1)]
for n in range(1, 2*M+1):
    B.append(-sum(comb(n+1, j)*B[j] for j in range(n))/F(n+1))

def vi(n):
    if not n:
        return None
    return (abs(n) & -abs(n)).bit_length()-1

@lru_cache(None)
def D(z):
    b, value = F(1), 0
    for h in range(2*M):
        term = 2**h * B[h] * b
        if term:
            assert term.denominator % 2
            value = (value + term.numerator *
                     pow(term.denominator, -1, modulus)) % modulus
        b = b*(2*z-h)/F(h+1)
    return value

def determinant(a):
    a = [row[:] for row in a]
    previous, sign = 1, 1
    for k in range(len(a)-1):
        if not a[k][k]:
            j = next(j for j in range(k+1, len(a)) if a[j][k])
            a[k], a[j] = a[j], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k+1, len(a)):
            for j in range(k+1, len(a)):
                value = a[i][j]*pivot-a[i][k]*a[k][j]
                assert value % previous == 0
                a[i][j] = value//previous
        for i in range(k+1, len(a)):
            a[i][k] = 0
        previous = pivot
    return sign*a[-1][-1]

pairs = [(F(-1,3), F(1,3)), (F(2,5), F(-2,7)),
         (F(-4,3), F(4,5)), (F(3,7), F(-1))]
for x, q in pairs:
    for m in range(1,5):
        expected = m*(m-1)*(2+vi(q.numerator))
        expected += 4*sum(vi(factorial(k)) for k in range(m))
        value = determinant([[D(x+(i+j)*q) for j in range(m)]
                             for i in range(m)]) % modulus
        assert expected < M and vi(value) == expected
print("16 independently truncated dyadic determinant checks passed")
```

## 7. Reviewed revisions

All paths in this table are relative to bernoulli_closure/.

| Artifact | SHA256 |
|---|---|
| TARGET.md | 644833029ec275f29d2856ced097398bcba2b01be2bb8b4fa6e2531266ce324f |
| nonintersection/BERNOULLI_HANKEL_SEPARATION.md | 551af0af45e7f2b13976cd63922234bc29afa837d5f0649b22eabfa16fa76b78 |
| nonintersection/check_hankel_separation.py | 31a6f8ef9eccd8e2f82cf16a8533d448e15c63934c35753e9ee43bbcd1e1fd55 |
| nonintersection/certified_run/manifest.json | 6f3308683a0f99930e0bdd0dcc6b9b888e6ca3bb47fb07ac26e9f0ee6cb9b29d |
| nonintersection/certified_run/results.json | 85066a75c4d8bedb6f314693437b96e80c8bcf5c8834a46f82a17ada1bfd260e |
| hankel_bridge/ALL_STEP_HANKEL_AND_RESIDUAL_BRIDGE.md | 2b40608d469015294747866baf3747154c34b17539a261e7f2556b87b82f4d84 |
| hankel_bridge/check_hankel_bridge.py | 87681c4e1bb319d46cfd22486db23ba34536e6c733f1112f5e6204049ec0e1b6 |
| hankel_bridge/certified_run_final/manifest.json | fad3de292b1970a34df72eb2e95b5a9544a0a90b70c66367b0285bfbaaee5265 |
| hankel_bridge/certified_run_final/results.json | 5e27995884f927779127f454ff0f44b7d9ee6d9e18cce0d132588b118a1e18c5 |

## 8. Safe conclusion

The new determinant valuations and the scoped actual Bernoulli transfer
are established by the reviewed arguments. The smallest remaining
implication toward Euler closure is a valid identity turning the actual
stationary residual contact into a vanishing determinant or norm to
which these theorems apply. The next useful check is of that identity
and its lattice/precision losses, not a larger table of Hankel values.

Self-review: reviewed the new report for notation, quantifiers, formula
scaling, source locators, and computation ranges. No unresolved local
proofreading issue or substantive mathematical correction remains.
