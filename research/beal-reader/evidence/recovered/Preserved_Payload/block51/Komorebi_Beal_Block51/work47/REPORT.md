# Komorebi Beal Block 47: polyphase, cancellation and stratification

Research date: 2026-09-19. Target: primitive positive solutions of
\(A^3+B^5=C^7\). This is a continuation of Block 46, not a proof of Beal.
No primitive solution has been ruled out by a completed modular elimination.

The strongest advance is a written proof that the associated mod-seven RM
representation is absolutely irreducible whenever 14 does not divide C.
It combines exact cancellation, stable reduction, finite-flat transport and
a single global residual character. The coefficient-only local strategy
also now has a complete solvability criterion and explicit survivors at
every prime.

## 1. A cancellation with arithmetic content

For the genus-two model

\[
Y^2=f(X)=X^6+10BX^3+12AX+5B^2,
\]

the coefficients of \(f^3\) controlling Cartier at seven are

\[
[X^6]f^3=1575B^4,\quad [X^5]f^3=4320A^2B,\quad
[X^{13}]f^3=36A,\quad [X^{12}]f^3=315B^2.
\]

Thus the diagonal coefficient lanes vanish modulo seven, leaving

\[
\boxed{M=\begin{pmatrix}0&A^2B\\A&0\end{pmatrix},\qquad
M^2=A^3B I_2.}
\]

When \(7\nmid C\), the curve has good reduction. It is ordinary when
\(7\nmid AB\), and has 7-rank zero when \(7\mid AB\). There is no
7-rank-one stratum. The geometric interpretation uses the Cartier/Hasse–Witt
conventions in [Achter–Howe, §2.5](https://arxiv.org/pdf/1710.10726v5).

Nine Lean theorems establish the actual polynomial and matrix identities.
The geometric interpretation is a written application of external theorems.
Two independently written exact calculations check every residue pair,
including point counts over F7 and F49 for all 42 smooth fibers.

## 2. What the irreducibility argument establishes

The final theorem proves absolute irreducibility of the associated residual
RM representation whenever

\[
\boxed{14\nmid C.}
\]

This means C odd or 7 not dividing C. The sole remaining parity/divisibility
branch for this irreducibility argument is 14 dividing C. The canonical
proof is `notes/mod7_good_reduction_irreducibility.md`; the fresh independent
audit is `notes/final_irreducibility_audit.md`.

The new ingredients are a stable model at two when C is even, and the
finite-flat obstruction at seven. The former has exactly two ordinary nodes
and two smooth points at infinity. The latter follows from
[Raynaud's finite-flat uniqueness theorem, Theorem 3.3.3](https://www.numdam.org/article/BSMF_1974__102__241_0.pdf)
under the checked hypothesis \(e=1<6\).

The argument retains the Frobenius label of the same character.
For good reduction at seven, finite-flat transport and the full Frobenius
annihilating polynomial give

\[
\nu(\operatorname{Frob}_{(7)})=A^3B\pmod7
\]

for any unramified associated constituent. Global reciprocity on
\(\phi^4\) and \(2/7\), with \(\phi=(1+\sqrt5)/2\), gives
\(\nu(\operatorname{Frob}_{(2)})=\nu(\operatorname{Frob}_{(7)})\).
For even C the torus calculation forces the value at two to be -1. Hence
\(A^3B=-1\bmod7\), which forces \(A^3+B^5=0\bmod7\), contradicting good
reduction at seven. Together with the predecessor's odd-C proof, this gives
the stated scope. Earlier notes retain their narrower intermediate claims.

Irreducibility is an input to modular elimination. It does not exclude the
hypothetical integer solution. The conductor, associated-character and
reciprocity inputs remain explicit written-theorem dependencies. They have
not been formalized in Lean.

## 3. Exact stratification, including its limit

Write \(A=au^2,B=bv^2,C=cw^2\), with positive pairwise-coprime squarefree
coefficients. Then

\[
a^3u^6+b^5v^{10}=c^7w^{14}.
\]

The complete criterion for nonzero primitive local roots is:

| Place | Necessary and sufficient coefficient condition |
|---|---|
| 2, with A even | b,c odd and b=c modulo 8 |
| 2, with B even | a,c odd and a=c modulo 8 |
| 2, with C even | a,b odd and a+b=0 modulo 8 |
| Odd p dividing a | Legendre symbol (bc/p)=1 |
| Odd p dividing b | Legendre symbol (ac/p)=1 |
| Odd p dividing c | Legendre symbol (-ab/p)=1 |
| Odd p not dividing abc | Always locally soluble |

An even coefficient forces its base's parity phase. With all coefficients
odd, any admissible dyadic row can be used. Simple-root lifting at every
odd prime, including 3,5,7, and the square-unit criterion at two prove that
no further coefficient exclusions appear at higher prime-power precision.

In particular,

\[
\boxed{(a,b,c)=(3,5,2)\quad\text{and}\quad(2,3,11)}
\]

admit primitive solutions over every Z_p and positive real solutions. These
are locally soluble coefficient families, not integer solutions or Beal
counterexamples. They survive the earlier square-product exclusions. This
proves that refining these projected local coefficient classes alone cannot
finish the argument.

Keeping joint phases nevertheless matters: among all-odd coefficient
triples modulo 8, the joint criterion admits 36 of 64, while every individual
coordinate marginal is full. Discarding the correlation loses 28 valid
exclusions. The full proof and finite checks are in `notes/stratification.md`.

## 4. What can be recovered from modular correlations

The pinned published elimination replaces Hecke values by minimal
polynomials and resultants and uses one prime above each auxiliary rational
prime. This can lose a consistent prime/embedding label and paired traces.
It is a sound relaxation, not an error in the published exclusions.

The effect must be assessed form by form. Seven is inert in Q(sqrt5), and
for some forms the conjugate-prime condition may be automatic. The public
files lack the exact coefficient fields and labelled Hecke exports needed
to perform the proposed refinement on all indexed surviving forms. No such
form was eliminated in this block.

There are two exact conditional improvements:

| Rank-two modular condition | Necessary Beal residue condition |
|---|---|
| Trace zero at a prime above11 | 11 divides A |
| Trace zero at a prime above19 | 19 divides B |

These assume the modular comparison and the standard multiplicative-prime
trace relation. Full Jacobian polynomials were counted independently on all
110 smooth pairs at 11 and all 342 at 19. The criterion checked was
\((T^2+q)^2\bmod7\), not merely zero four-dimensional trace. CM by
K(sqrt(-3)) supplies the trace-zero condition at 11, hence a conditional
divisibility restriction, not a contradiction.

The audit also found a parameter-label issue: at 11 the explicit curve and
the hypergeometric table match after inversion of t, although their
unlabelled multisets agree. Resolve that dictionary before attaching refined
lanes to the imported trace polynomials. For 21 of 36 audited auxiliary
primes the imported regular trace support already fills F49; extra scalar
tests at those particular primes add no exclusion of F49-valued traces.

Source: [pinned PV code and data](https://github.com/lucasvillagra/GFE-5p3/tree/e88f914c577ab6cf9a45e5cdd82c1993477fb423).
The broader-prime data are imported outputs, not a fresh GP or Magma replay.

## 5. Transfers that fail, and why

The actual period is proportional to
\(t^{1/5}{}_2F_1(8/15,-2/15;7/5;t)\). Its seven-section equations are
exact, but its first nonconstant coefficient is \(-16/315\), with
7-adic valuation -1. The older factorial example's unit-denominator result
therefore does not apply directly. A new integral normalization would be
needed. No claim about an unbounded denominator sequence is inferred from
a finite scan.

Moreover, for every ring in which t and 1-t are units,

\[
A=t^{28}(1-t)^{30},\quad B=-t^{17}(1-t)^{18},\quad
C=t^{12}(1-t)^{13}
\]

gives a unit solution and motive parameter \(-B^5/A^3=t\). Thus every
regular parameter lane is locally populated at every prime-power depth.
This identity does not produce primitive positive integer solutions.

The exact rational scaling criterion identifies the retained global defect:
for 0<t<1, positive valuations of t must be multiples of 3, those of1-t
multiples of 5, and denominator valuations multiples of 7. Lane reconstruction
does not impose these conditions. SRIC's descent theorem also requires
actual sheaf/torsor and effective-descent hypotheses, which have not been
constructed for this Diophantine problem.

## 6. Verification and concrete remaining work

- 21 new Lean theorems: 12 certificate/correlation results and 9 actual
  characteristic-seven algebra results. Clean compilation, separate kernel
  replay, axiom audit and three negative controls passed.
- Exact standard-library computations have explicit finite ranges and
  recorded input/output hashes. No numerical approximation is used in the
  independently counted local Frobenius polynomials.
- Written proofs and external arithmetic dependencies are reviewed
  separately. Neither the Lean theorem count nor agent agreement certifies
  Beal nonexistence.

The next modular calculation needs exact per-form coefficient fields,
primes above seven and compatible Hecke-value embeddings. It must keep one
candidate throughout all tests and certify the complete lane coverage.
There also remains the irreducibility branch 14 dividing C. The applicability of every
level-lowering input at seven must be closed before eliminating forms.

Even a completed result for (3,5,7) would settle only that signature and
its exponent multiples. It would not settle all exponent triples in Beal.

Detailed proofs, reviews, exact scripts, Lean source and verification records
are included in the accompanying archive. `notes/toolkit_transfer_map.md`
records the Komorebi sources actually inspected and the hypotheses retained.
