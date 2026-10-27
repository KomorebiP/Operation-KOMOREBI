# A classical effective budget for the same global source

This companion strengthens the existence-only budget in PROOF_NOTE.md
using a second checked external input. It is an integration into Komorebi,
not a new arithmetic estimate.

**External theorem.** Stewart and Yu, *On the abc conjecture, II*, Duke
Mathematical Journal 108 (2001), 169–181, Theorem 1, printed page 170,
prove that some effectively computable absolute K>0 satisfies

\[
\log c<K R^{1/3}(\log R)^3,\qquad R=\operatorname{rad}(abc),
\]

for every positive a+b=c with gcd(a,b,c)=1. These hypotheses are the
ordinary source hypotheses of this program. Under a+b=c, this gcd
condition is equivalent to gcd(a,b)=1.

The published 13-page PDF was opened from the primary institutional host:
https://uwaterloo.ca/pure-mathematics/sites/default/files/uploads/documents/s0012-7094-01-10815-6.pdf .
The first two pages identify authors, journal, publication year and exact
theorem. DOI: https://doi.org/10.1215/S0012-7094-01-10815-6 . No PDF bytes
were retained, so no byte hash is asserted. The theorem and its hypotheses
were checked; its proof and cited logarithmic-form estimates were not
reaudited. No numerical value of K was extracted. Web reference for the
coordinator: `turn113view0`.

## Exact integral budget conversion

Choose an effectively computable positive integer K0 at least K. For a
finite support S set Q=max(2,R(S)). Let q be the smallest positive integer
with q cubed at least Q, and let L be the smallest positive integer with
2^L at least Q. Define the integer

\[
B_{\rm SY}(S)=4^{K_0 q L^3}.
\]

For any triple in T_S, monotonicity on R at least 2 gives

\[
\log c<K Q^{1/3}(\log Q)^3
\leq K_0 q L^3<\log B_{\rm SY}(S),
\]

where log Q is at most L log 2 and hence at most L, and log 4 exceeds 1.
Consequently c is at most B_SY(S). The conversion uses only exact integer
arithmetic once the external constant K0 is supplied. It does not purport
to have evaluated that constant in this checkpoint.

Use B=B_SY(S) in the support-retaining factorial views of Proposition 2.
Their coherent sections then equal the complete intended source T_S,
and the level N at least B+1 is an explicit safe stabilization bound
relative to the specified external constant. This reconstructs genuine
integer points with a radical-controlled budget, without admitting the
RR7 non-diagonal adelic family or discarding carries.

## Finite source realization from a radical threshold

More directly, fix an integer T at least 2, and put q=ceil(T^(1/3)) and
L=ceil(log_2 T). These ceilings denote the least positive integers
satisfying q^3 at least T and 2^L at least T, so they can be computed
without real arithmetic. Set A=K0 q L^3, B=4^A, and M=2B. The modulus M
is itself a power of 2 and exceeds B.

Take a category with two objects, a raw view r and a defect view d,
and one nonidentity arrow d to r. Define the contravariant Set-valued
view system by

\[
F(r)=\{(a,b,c)\in\mathbf Z_{>0}^3:
a,b\leq c\leq B,\ \gcd(a,b,c)=1,\ \operatorname{rad}(abc)\leq T\},
\qquad F(d)=\mathbf Z/M\mathbf Z,
\]

with restriction (a,b,c) mapped to a+b-c modulo M. Protect the d-view
at zero. The budget, primitive condition and radical constraint are
declared nonlinear conditions on the finite raw view. They have not
been replaced by a linear observable or inferred from the residue.

**Finite realization theorem.** The protected coherent extensions are in
bijection with all ordinary positive primitive integer triples satisfying
a+b=c and rad(abc) at most T.

**Proof.** On the raw domain, |a+b-c| is at most c, hence at most B, which
is strictly smaller than M. Zero defect modulo M therefore forces exact
integer addition. Its gcd condition is then the intended primitive
condition. Conversely the checked Stewart–Yu bound puts every intended
triple under the stated budget B. Such a triple gives a unique raw view
and the protected zero defect, so the comparison is bijective. \(\square\)

This finite diagram is an actual conductor-supplied realization of the
intended source. Its completeness depends on the external arithmetic bound.
It does not infer a height bound for arbitrary unbounded local raw data,
and a residue-only observer without the bounded integer raw view would
not have the same theorem.

The growth rate remains far above the required ABC rate. In logarithmic
height the imported budget has scale R^(1/3)(log R)^3; the target has scale
log R. Thus a global cost bound is available, but the sharp cost improvement
is unresolved. This checkpoint supplies no new unrestricted pointwise
arithmetic exponent.
