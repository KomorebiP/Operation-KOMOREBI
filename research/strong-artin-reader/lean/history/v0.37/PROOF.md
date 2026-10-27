# Effective scalar survival: proof and conventions

Evidence: the statements identified below are proved in the new Lean sources.
This text is a self-reviewed explanation of those statements, not a substitute
for the compiler records. Mathematical depths are exponents m in Z/(p^m).
The inherited v0.36 tower used index m-1 for the same exponent.

## 1. Exact local scaling

Let P be a polynomial in Z_p[X], a,z in Z_p, and delta=|P'(a)|_p.
If |z-a|_p<delta, then

\[
|P(z)-P(a)|_p=\delta |z-a|_p.
\]

Put h=z-a. Polynomial expansion over Z_p supplies q in Z_p with

\[
P(a+h)-P(a)=(P'(a)+qh)h.
\]

Since |q|_p<=1, the assumption implies |qh|_p<|P'(a)|_p.
The strong triangle law gives |P'(a)+qh|_p=|P'(a)|_p, proving the formula.
This is `polynomial_norm_difference`. It is a scalar commutative statement.

## 2. Exact image of a small ball

Fix 0<=rho<delta. Then

\[
\exists!z\in\mathbf Z_p:
P(z)=0,\quad |z-a|_p\le\rho
\quad\Longleftrightarrow\quad
|P(a)|_p\le\delta\rho.
\]

Necessity follows from the scaling formula. For sufficiency,
|P(a)|_p<=delta rho<delta^2. Mathlib's `hensels_lemma` supplies a root z
with |z-a|_p<delta and proves uniqueness in that open ball. The scaling formula
then yields delta |z-a|_p=|P(a)|_p<=delta rho. As delta>0, z lies in the
smaller closed ball. Every root in that ball lies in the uniqueness region.
This is `polynomial_ball_root_iff`.

The external input is the actual formal Hensel theorem, not a derivative-surjectivity
assumption. Its exact inequality and uniqueness region are retained. See
`LITERATURE_BOUNDARY.md` for the source and pinned revision.

## 3. Congruence form

The kernel of Z_p -> Z/(p^m) is p^m Z_p. Hence

\[
x\equiv y\pmod{p^m}\iff |x-y|_p\le p^{-m}.
\]

Suppose |P'(a)|_p=p^{-s} and m>s. Applying the preceding theorem with
rho=p^{-m} proves

\[
\exists!z\equiv a\pmod{p^m},\ P(z)=0
\iff P(a)\equiv0\pmod{p^{m+s}}.
\]

The Lean reduction is `polynomial_prefix_root_iff`. Neither division by p
inside a residue field nor a splitting of a mixed-characteristic ring is used.

For P(X)=X^d-U, d>0, and a a unit, P'(a)=d a^(d-1) has valuation
s=v_p(d). This proves `scalar_deep_prefix_root_iff`. Applying the scaling
formula to any existing root also gives the existence-only version. Thus
absence of a unique root is not being incorrectly used to infer nonexistence.

## 4. Uniform effective horizon for any positive unit prefix

Fix m>=1, a in Z_p^×, and U in Z_p. Let

\[
s=v_p(d),\qquad k=\max(m,s+1),\qquad H=k+s.
\]

A genuine root reduces to a finite root at H, proving one direction.
Conversely, suppose b in Z/(p^H) is a root and b=a modulo p^m.
Choose its least nonnegative representative B, regarded as an element of Z_p.
Because m>=1, B has the same nonzero residue as a and is a unit. The finite
root equation is B^d=U modulo p^(k+s). Since k>s, the deep-prefix theorem
constructs a unique root z above B modulo p^k. Reducing from k to m preserves
the original prescribed prefix a.

This is `scalar_root_iff_finite_horizon`. It is uniform in U, including U's
unknown higher digits. If U is nonunit, neither side can hold for a unit prefix.
The explicit finite condition uses only U modulo p^H and a modulo p^m.

The constructed root need only agree with B modulo p^k, not modulo p^H.
For example, with p=d=3 and m=1, H=3. The finite root b=10 modulo 27
certifies survival of 1 modulo 3, but b itself does not extend: its three lifts
modulo 81 all cube to 28. The true root 1 preserves the required prefix and the
refinement B modulo 9, as the proof promises.

Reducing a constructed p-adic root at every r>=m proves
`scalar_horizon_iff_all_deeper_levels`. Conversely, the all-depth premise can
be specialized at H. Thus the earlier compactness input becomes a single
computable condition in this sector.

## 5. Fixed diagonal matrix algebra

For a finite index set, let A=diag(a_i) with each a_i a unit and U=diag(u_i).
Solve the scalar finite problem for every coordinate at the same horizon H.
Choose corresponding scalar roots x_i, and set F=diag(x_i). Positive prefix
preservation makes each x_i a unit. Consequently F is a unit in the actual
matrix ring over Z_p, F^d=U, and F=A modulo p^m.

Conversely, a root constrained to this diagonal algebra gives the coordinate
finite certificates by reduction. This proves `diagonal_root_iff_finite_horizon`.
`exists_diagonal_matrix_unit_root` packages F as an actual Lean `Units` value
and checks the full matrix reduction. This is not a statement that every root
of a diagonal target is diagonal, or a classification of arbitrary matrix roots.

## 6. Executable scalar correction

The CLI enumerates canonical representatives B modulo p^k above the original
prefix. It accepts precisely those satisfying B^d=U modulo p^(k+s).
The deep-prefix theorem proves that these are exactly the surviving refined
prefixes. Every genuine root gives one such canonical representative by the
same existence-only criterion, so this smaller enumeration is complete.

For an integer target, start from a surviving representative x at precision j=k.
To obtain one more root digit, calculate

\[
q=(x^d-U)/p^{j+s}\pmod p,\qquad
c=(d/p^s)x^{d-1}\pmod p,\qquad
t=-q c^{-1}\pmod p.
\]

The coefficient c is nonzero. Replace x by x+t p^j. Terms beyond the linear
one have valuation at least 2j>=j+s+1 because j>s. The new equation holds
modulo p^(j+s+1), preserving all earlier root digits. The Python implementation
uses a modular residual to compute q exactly without floating arithmetic.
This implementation has finite exact tests; its algorithm code is not extracted
from Lean. The universal existence and image assertions are supplied by Lean.
