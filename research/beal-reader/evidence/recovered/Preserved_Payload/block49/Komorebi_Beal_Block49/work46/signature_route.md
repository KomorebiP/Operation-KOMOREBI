# Block 46: exponent-sensitive global route for signature (3,5,7)

Date checked: 2026-09-19. This is a closure attempt, not a proof of Beal.

## Exact outcome

The dihedral quartic can be supplemented by an exponent-sensitive genus-two curve

\[
 Z^2=F_{A,B}(X):=X^6+10BX^3+12AX+5B^2.
\]

An exact computation and polynomial argument establish

\[
\operatorname{disc}(F_{A,B})
 =2^{12}3^6 5^5(A^3+B^5)^2.
\]

Thus a hypothetical solution of \(A^3+B^5=C^7\) gives

\[
\boxed{\operatorname{disc}(F_{A,B})=2^{12}3^6 5^5 C^{14}.}
\]

This removes the primes of A and B from this polynomial discriminant. It supplies an object that records the seventh-power condition through a discriminant exponent divisible by seven. It does **not** by itself establish residual irreducibility, the residual conductor, a modular elimination theorem at seven, or nonexistence of the initial solution.

A separate written argument now proves absolute irreducibility at seven when C is odd, using the displayed model, exact local computations, and explicitly identified arithmetic inputs. The proof and its collaborative review boundary are in `mod7_oddC_written_proof.md`. Its final form uses the norm of the rank-two determinant, so it needs neither an unverified determinant normalization nor a maximal specialized integral endomorphism order. This closes one representation-theoretic branch; it does not prove the initial Diophantine equation insoluble.

The curve comes from the integral equation

\[
y^2+y(X^3+B)=2BX^3+3AX+B^2
\]

by setting \(Z=2y+X^3+B\). Direct expansion gives the displayed sextic. Its discriminant is nonzero when A,B are positive, so its smooth projective hyperelliptic model has genus two in characteristic zero.

## Proof of the discriminant identity

The discriminant is a polynomial in A and B with integer coefficients. Give X,A,B weights 1,5,3. Then

\[
 F_{\lambda^5 A,\lambda^3 B}(\lambda X)=\lambda^6F_{A,B}(X).
\]

The six roots scale by \(\lambda\); their fifteen squared differences show that the discriminant has weight 30. Consequently its only possible monomials are

\[
A^6,\quad A^3B^5,\quad B^{10}.
\]

Three exact 11 by 11 Sylvester determinant evaluations give

| A | B | discriminant |
|---:|---:|---:|
| 0 | 1 | 9,331,200,000 |
| 1 | 0 | 9,331,200,000 |
| 1 | 1 | 37,324,800,000 |

Writing \(K=9,331,200,000=2^{12}3^6 5^5\), these determine the coefficients as K, 2K, K. This proves the polynomial identity universally. This is exact interpolation with a proved monomial space, not a bounded numerical inference. An independent test at (2,3) gives 587,874,931,200,000 = K times 251 squared.

This is the discriminant of the sextic polynomial. No claim here identifies it with a minimal discriminant, a field discriminant, or the conductor of a Jacobian.

## Primary-source comparison and the exact limitation at seven

Pacetti and Villagra Torcomian, *On the generalized Fermat equation of signature (5,p,3)*, arXiv:2512.17845v1, dated 2025-12-19, provides the genus-two family and its hypergeometric comparison (Section 7.1). Its Theorems A and B both exclude p=7. Theorem 7.18 does apply at seven: for our primitive triple with \(3\nmid A\), the mod-seven motive at \(t_0=-B^5/A^3\) is not congruent to the motives at \(-1/8\) or \(9/8\). These are two specific exclusions, not an exhaustive elimination. The variable dictionary is \((a,b,c,p)=(B,-C,A,7)\). Their Remark 7.15 reports full finite-field parameter sets in experiments with distinct prime exponents. The explicit identity below proves that saturation for this signature.

Source: [versioned primary preprint](https://arxiv.org/html/2512.17845v1). Exact sections and hypotheses were read; no source PDF is retained by this subtask. Classification: known construction after translating notation; an independently checked discriminant identity; partial arithmetic exclusions. No newness claim.

## Concrete modular continuation targets

The authors' [pinned output transcript](https://github.com/lucasvillagra/GFE-5p3/blob/e88f914c577ab6cf9a45e5cdd82c1993477fb423/Outputs/TheoremA.txt) was imported and parsed, not freshly replayed in Magma. The following indices are meaningful only in that pinned data set. They describe what the recorded elimination did not remove; they are not canonical form identifiers or a newly certified elimination theorem.

| Level | Recorded survivors at seven |
|---|---|
| 3^2 (sqrt(5))^2 | 3, 9, 12 |
| 3^3 (sqrt(5))^2 | 21, 22, 26, 33, 61, 65, 78, 92, 98 |
| 3^2 (sqrt(5))^3 | Exact seven-specific list not recoverable from this aggregate transcript |
| 3^3 (sqrt(5))^3 | Exact seven-specific list not recoverable from this aggregate transcript |

The second row comes from 111 indexed newform records, not a vector-space dimension. Of these, seven list seven as an exceptional exponent; indices 65 and 78 survive every recorded auxiliary-prime test. The other two levels with incomplete seven-specific data have seven in the aggregate exception list, so their short all-prime survivor lists cannot safely be treated as complete at seven.

`computations/author_transcript_extract.py` reproduces this extraction from the cached connector text, checks every index from 1 through 111, and records its SHA256 in `signature_source_extract.json`. A fresh modular computation still needs the authors' data and Magma, full local-level applicability at seven, and elimination of every surviving form.

## A universal local-saturation theorem

For any commutative ring and any element t, put s=1-t and define

\[
A_0=t^{12}s^{28},\qquad B_0=t^7s^{17},\qquad C_0=t^5s^{12}.
\]

Then

\[
 A_0^3+B_0^5
 =t^{35}s^{84}(t+s)
 =t^{35}s^{84}=C_0^7.
\]

In a field with t nonzero and t not equal to one, all three coordinates are nonzero and

\[
\boxed{A_0^3/C_0^7=t.}
\]

Therefore, over every finite field, the parameter \(A^3/C^7\) of nonzero local solutions takes every value other than zero and one. There can be no elimination of these parameter values using only the existence of a nonzero solution over that finite field. The same polynomial construction works modulo an arbitrary modulus whenever t and 1-t are units. This does not rule out global methods linking primes, conductor conditions, or Frobenius data against a fixed representation.

This also gives a rational parametrization with weighted scaling. For any nonzero rational solution set

\[
t=A^3/C^7,\qquad \lambda=C^8/(AB^4).
\]

Then

\[
A=\lambda^{35}A_0,\quad B=\lambda^{21}B_0,\quad C=\lambda^{15}C_0.
\]

All three formulas follow by substituting t and 1-t into the monomials. Conversely these formulas yield a rational solution for any nonzero \(\lambda,t,1-t\). The missing condition is primitive integrality, not rational existence.

For t=1/2 and lambda=4, this gives

\[
(A,B,C)=(2^{30},2^{18},2^{13}),
\]

which satisfies the equation and has common divisor \(2^{13}\). It is a negative control against reading the parametrization as a primitive Beal counterexample. Dividing by an ordinary common divisor does not preserve an equation with different exponents.

An exact finite replay tested every nondegenerate t for all 168 primes at most 997: 75,791 parameter realizations passed. The proof above is the universal justification; the finite replay checks the implementation.

## Exact height target and why a generic radical ceiling fails

For a primitive positive solution let

\[
H=C^7,\qquad R=\operatorname{rad}(ABC).
\]

Positivity implies \(A<H^{1/3}\), \(B<H^{1/5}\), and \(C=H^{1/7}\). Hence

\[
R\le ABC < H^{71/105},\qquad
\boxed{\log H/\log R>105/71.}
\]

Suppose, as an additional hypothesis, one had an abc-type estimate

\[
H\le K_\varepsilon R^{1+\varepsilon}.
\]

For \(0<\varepsilon<34/71\), it follows that

\[
H<K_\varepsilon^{105/(34-71\varepsilon)},\qquad
C<K_\varepsilon^{15/(34-71\varepsilon)}.
\]

For example, epsilon=1/10 gives \(C<K_{1/10}^{150/269}\). This is only a conditional reduction to a finite range. It does not become a proof without the stated bound, an explicit constant, and a certified exhaustion below it.

A tempting universal estimate \(c\le\operatorname{rad}(abc)^{105/71}\) for all primitive positive a+b=c is false. The exact triple

\[
2+3^{10}\cdot109=23^5
\]

has radical 15,042 and satisfies \(c^{71}>15042^{105}\); its logarithmic quality is approximately 1.6299116841. This triple is not a counterexample to the (3,5,7) equation. It proves that a closure estimate at the needed strength must use the exponent conditions, or allow explicit exceptions/constants.

## Scope of the attempt

Even eliminating primitive positive (3,5,7) solutions would settle only one signature and those obtained by absorbing multiples into the bases. Full Beal requires all exponent triples greater than two. A general reduction retains odd prime exponents and exponent four; it does not reduce every case to (3,5,7).

The odd-C reducibility branch is now handled by the separate written proof. The remaining genus-two route needs complete local-level and level-lowering applicability at seven, elimination of all surviving modular forms, and a treatment of the C-even branch. Main theorems whose hypotheses exclude seven cannot remove these obligations.

## Reproduction code

The canonical reusable program is `computations/signature_audit.py`, with output `signature_audit.json`; its contract is `signature_computation_contract.md`. The shorter code below records the initial algebra checks. Both use only the Python standard library. Bareiss elimination evaluates each Sylvester determinant with exact integers. The canonical program additionally checks the nodal factorization, characteristic-two counts, order-sixteen unit, weight restrictions, and Frobenius resultants for the odd-C proof. Its `arithmetic_hypotheses_verified: false` records the scope of the Python computation, not a rejection of the separately reviewed written arithmetic proof.

```python
from fractions import Fraction
from math import gcd, isqrt

def determinant(M):
    a = [row[:] for row in M]
    sign, old = 1, 1
    for k in range(len(a)-1):
        if a[k][k] == 0:
            candidates = [i for i in range(k+1,len(a)) if a[i][k]]
            if not candidates:
                return 0
            q = candidates[0]
            a[k], a[q] = a[q], a[k]
            sign = -sign
        pivot = a[k][k]
        for i in range(k+1,len(a)):
            for j in range(k+1,len(a)):
                num = a[i][j]*pivot-a[i][k]*a[k][j]
                assert num % old == 0
                a[i][j] = num//old
            a[i][k] = 0
        old = pivot
    return sign*a[-1][-1]

def sextic_discriminant(A,B):
    f = [1,0,0,10*B,0,12*A,5*B*B]
    df = [6,0,0,30*B,0,12*A]
    sylvester = [[0]*k+f+[0]*(4-k) for k in range(5)]
    sylvester += [[0]*k+df+[0]*(5-k) for k in range(6)]
    return -determinant(sylvester)

K = 2**12*3**6*5**5
for A,B in [(0,1),(1,0),(1,1),(2,3),(-1,1)]:
    assert sextic_discriminant(A,B) == K*(A**3+B**5)**2

primes = [p for p in range(2,1000)
          if all(p%d for d in range(2,isqrt(p)+1))]
checks = 0
for p in primes:
    for t in range(2,p):
        s = (1-t)%p
        A = pow(t,12,p)*pow(s,28,p)%p
        B = pow(t,7,p)*pow(s,17,p)%p
        C = pow(t,5,p)*pow(s,12,p)%p
        assert A*B*C%p
        assert (pow(A,3,p)+pow(B,5,p)-pow(C,7,p))%p == 0
        assert pow(A,3,p)*pow(pow(C,7,p),-1,p)%p == t
        checks += 1
assert len(primes) == 168 and checks == 75791

t = Fraction(1,2)
s = 1-t
A,B,C = (t**12*s**28*4**35,
         t**7*s**17*4**21,
         t**5*s**12*4**15)
assert A**3+B**5 == C**7
assert (A,B,C) == (2**30,2**18,2**13)
assert gcd(gcd(A.numerator,B.numerator),C.numerator) == 2**13

a,b,c = 2,3**10*109,23**5
R = 2*3*109*23
assert a+b == c and gcd(a,b) == 1
assert c**71 > R**105
print('PASS: exact discriminants, local saturation, negative controls')
```

Implementation failure recorded: the first attempt to use SymPy failed because the module is absent in both available Python runtimes. The successful method above replaced that dependency with exact standard-library Bareiss elimination. No Lean verification was performed by this subtask.

## Search boundary

Queries included exact signature spellings, the explicit equation, generalized Fermat surveys, and current (5,p,3) work. The current primary preprint was read at the versioned HTML URL, including the full relevant theorem hypotheses and the signature dictionary. Older MathOverflow and survey hits were discovery aids, not proof authorities. This search establishes applicability/nonapplicability of the named source, not an exhaustive theorem of current literature status or novelty.
