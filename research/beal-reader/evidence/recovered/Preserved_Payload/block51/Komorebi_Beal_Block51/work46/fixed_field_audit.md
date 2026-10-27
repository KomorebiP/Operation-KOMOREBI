# Independent audit: complementary pairs with the same quartic and splitting fields

**Primary verdict: proved as written.** Here “the quartic field” uses the specified root
`u' = u(r+s sqrt(a))`. The rational parametrization is defined only when its denominator
is nonzero. A separate convention warning concerning *positive* real square roots is
given below; the positive family can be restricted to integer parameters `t >= 1`
to satisfy that convention too.

**Evidence level:** complete elementary mathematical proof in this file, with exact
rational sample checks. This is not a Lean field-extension theorem, and this audit
does not claim kernel checking of its mathematical conclusions.

**Base checkpoint:** `inputs/Komorebi_Beal_Block45_Arithmetic_Lift_v4.5.0.zip`, SHA256
`eb8f9537a827c7487875f51f77eb202e3b2008e677f4993f724cc4fc0321349f`.
The digest was checked directly with `sha256sum`. Relevant authoritative prior text:
`base45/Komorebi_Beal_Block45_v4.5.0/ARITHMETIC_THEOREMS.md`, Sections 4–7.
That text already distinguishes its elementary field argument from its formalized
polynomial identities. No project instruction file was present at the workspace
root or its inspected ancestors.

## 1. Normalized claim

Let `a,b` be nonzero rational numbers with `a+b=1`, and assume that `a`, `b`, and
`ab` are nonsquares in Q. Work in a fixed algebraic closure of Q. Choose

\[
 A^2=a,\quad u^2=1+A,\quad v^2=1-A,\quad B=uv,\quad B^2=b.
\]

Set `K=Q(u)` and `L=Q(u,v)`. For any rational solution

\[
 C:=r^2+2ars+as^2=1,
\]

define

\[
 q=r^2+2rs+as^2,\qquad h=r^2-as^2,
 \qquad a'=a q^2,\qquad b'=b h^2.
\]

Then `q,h` are nonzero; `a',b',a'b'` are nonsquares; `a'+b'=1`; and

\[
 u'=u(r+sA),\qquad v'=v(r-sA)
\]

satisfy

\[
 \mathbb Q(u')=K,\qquad \mathbb Q(u',v')=L.
\]

The latter field is the splitting field of `X^4-2X^2+b'`. Both old and new root
fields have degree four, and both splitting fields have degree eight with group
`D4` (the dihedral group of order eight).

For `a=1/3`, `b=2/3`, the given rational parametrization produces positive
complementary pairs for every finite rational parameter. Its image is infinite
and has unbounded rational height. Integer parameters `t=1,2,...` already give
heights tending to infinity and preserve the positive-root convention for `K`.

## 2. Dependency graph and obligation matrix

Dependencies are all elementary and proved below:

1. Complementary identity -> transformed roots and square-class preservation.
2. Nonzero `q,h` -> explicit recovery of the original roots -> equality of fields.
3. Independence of the original square classes -> degree four/eight and `D4`.
4. Conic parametrization -> infinite parameter domain.
5. Nonconstant rational output -> finite fibers -> infinitely many outputs.
6. Finiteness of bounded-height rational numbers -> unbounded output height.
7. Identical fields + unbounded parameter height -> no height bound depending
   only on their field discriminants on this full complementary-pair domain.

| Obligation | Result | Evidence |
|---|---|---|
| Complementary identity | passed | Polynomial identity in Section 3 |
| Root formulas and exact embedded-field equality | passed | Explicit inverse formulas in Section 3 |
| Nonvanishing and independent square classes | passed | Nonsquare contradiction and multiplication by rational squares |
| Quartic irreducibility and splitting degree | passed | Norm and quadratic-extension argument in Section 4 |
| Parameter exceptional set and coverage | passed | Section 5 |
| Positivity, nonconstancy, infinitely many pairs | passed | Section 6 |
| Heights unbounded, indeed tending to infinity on integer parameters | passed | Finite fibers and finite bounded-height sets |
| Positive real root convention | passed after explicit convention choice | Restriction `t >= 1`, Section 7 |
| Unrestricted discriminant-to-height bound | refuted | Section 8 |
| Restriction to primitive Beal perfect powers | not addressed | No such property is established for the family |
| Lean formalization of the field theorem | not addressed | No Lean claim is made |

## 3. Exact identities and preservation of fields

The unconstrained polynomial identity

\[
 a(r^2+2rs+as^2)^2+(1-a)(r^2-as^2)^2
 =(r^2+2ars+as^2)^2
\]

follows by expansion. Thus `a q^2+b h^2=1` when `C=1`.
If `q=0`, then `b=1/h^2`, a rational square; if `h=0`, then `a=1/q^2`, a
rational square. Both contradict the assumptions. This proves that the raw
claim's explicit condition `qh != 0` is automatic on its rational conic.

Direct multiplication gives

\[
 u'^2=(1+A)(r+sA)^2=C+Aq=1+Aq,
\]
\[
 v'^2=(1-A)(r-sA)^2=C-Aq=1-Aq,
 \qquad u'v'=Bh.
\]

Consequently `(u'^2-1)^2=a'`, and `u',-u',v',-v'` are the four roots of
`X^4-2X^2+b'`. They are distinct: `b' != 0` makes both squared roots nonzero,
and `Aq != 0` makes their squares different. Moreover,

\[
 A=\frac{u'^2-1}{q},\qquad
 (r+sA)^{-1}=\frac{r-sA}{h},\qquad
 (r-sA)^{-1}=\frac{r+sA}{h}.
\]

Therefore `u'=u(r+sA)` belongs to `K`, while

\[
 u=\frac{u'(r-sA)}h
\]

belongs to `Q(u')`. This proves equality of the embedded quartic fields.
Both `u',v'` belong to `L`; conversely, their field recovers `A`, then `u`, and
then `v=v'(r+sA)/h`. Hence the splitting fields are equal as embedded fields,
not merely isomorphic. The same proof gives `Q(v')=Q(v)`.

Because `q,h` are nonzero rational numbers,

\[
 [a']=[a],\qquad [b']=[b],\qquad [a'b']=[ab]
 \quad\hbox{in }\mathbb Q^*/\mathbb Q^{*2}.
\]

Thus all three nonsquare conditions are preserved. The ordered Kummer
characters of `a,b` are preserved as well. This observation does not assert
that all possible additional arithmetic markings or integral orders agree.

## 4. Degree and Galois group, with all leaves proved internally

Let `E=Q(A)`. This is quadratic. The norm of `1+A` to Q is `b`, a nonsquare;
thus `1+A` cannot be a square in `E`. It follows that `[K:E]=2` and `[K:Q]=4`.

The independence of `[a],[b]` follows from the three nonsquare conditions.
Explicitly, if `b=(x+yA)^2` for rational `x,y`, comparison of the `A`
coefficient yields `xy=0`; either `b` or `b/a` is then a rational square,
contradicting respectively the conditions on `b` or `ab`. Therefore
`F=Q(A,B)` has degree four over Q.

For any field `E` of characteristic different from two and any nonsquare
`d in E`, an element `c in E*` becomes a square in `E(sqrt(d))` only if `c`
or `c/d` is already a square in `E`. Indeed, expand `(x+y sqrt(d))^2=c` and
use `2xy=0`. Apply this with `d=b` and `c=1+A`. Neither `c` nor `c/b` is a
square in `E`, since their norms to Q are `b` and `1/b`, both nonsquares.
Hence `1+A` remains nonsquare in `F` and `[F(u):Q]=8`.

Since `A=u^2-1`, `B=uv`, and `v=B/u`, one has `L=F(u)`. This is the splitting
field of the four distinct roots of `X^4-2X^2+b`, so it is Galois.
Its automorphisms act faithfully by permutations of the roots preserving
the partition into opposite pairs `{u,-u}` and `{v,-v}`. The full permutation
group preserving this partition has order eight and is the symmetry group of
a square. Since `Gal(L/Q)` also has order eight, it is that group, `D4`.

## 5. Parametrization and exceptional values

Write

\[
 D(t)=t^2+2at+a,
 \qquad r(t)=\frac{a-t^2}{D(t)},
 \qquad s(t)=\frac{-2(t+a)}{D(t)}.
\]

The formula is defined for every rational `t` with `D(t) != 0`. Its excluded
finite parameters are exactly

\[
 t=-a\pm\sqrt{-ab}
\]

when `-ab` is a rational square; otherwise there are no excluded rational
parameters. These two roots are distinct, since `ab != 0`. There is no hidden
removable common zero: at a zero of `D`, the numerator `t+a` of `s` cannot
vanish, because `D(-a)=ab != 0`.

To verify the parametrization, substitute `r=1+ts` into the conic. The result is

\[
 r^2+2ars+as^2-1=s\bigl(2(t+a)+D(t)s\bigr).
\]

Taking the displayed `s` makes this zero and gives the displayed `r`.
Conversely, for any conic point with `s != 0`, taking `t=(r-1)/s` recovers it;
the equation forces `D(t) != 0`. The only points with `s=0` are `(1,0)` and
`(-1,0)`. The first occurs at `t=-a`, and the second occurs at the projective
parameter `t=infinity`. Both give `q=h=1`. Thus the parametrization accounts
for all rational conic points after adjoining infinity.

There are no additional rational parameter exclusions coming from `q` or `h`
under the nonsquare hypotheses, by Section 3.

## 6. An explicit positive family and its height

Take `a=1/3`, `b=2/3`. The square classes are independent: their classes may be
represented by `3,6,2`, none a rational square. Here

\[
 D(t)=\left(t+\frac13\right)^2+\frac29>0
\]

for every real `t`, so every finite rational parameter is allowed. Put
`d(t)=3t^2+2t+1`. The explicit formulas are

\[
 r=\frac{1-3t^2}{d},\qquad s=\frac{-2(3t+1)}d,
\]
\[
 q=\frac{27t^4+108t^3+54t^2-12t-5}{3d^2},
 \qquad
 h=\frac{27t^4-54t^2-24t-1}{3d^2}.
\]

Since `a'=q^2/3` and `b'=2h^2/3` are nonzero and sum to one, both lie strictly
between zero and one. Every member remains on the independent square-class
branch and has the same selected quartic field and splitting field.

For example, exact rational arithmetic gives:

| Parameter `t` | `q` | `h` | `a'` | `b'` |
|---|---:|---:|---:|---:|
| `-1/3` | `1` | `1` | `1/3` | `2/3` |
| `0` | `-5/3` | `-1/3` | `25/27` | `2/27` |
| `1` | `43/27` | `-13/27` | `1849/2187` | `338/2187` |
| `2` | `1483/867` | `167/867` | `2199289/2255067` | `55778/2255067` |

The first two values prove that the rational function `a'(t)` is nonconstant.
Writing

\[
 N(t)=27t^4+108t^3+54t^2-12t-5,
 \qquad a'(t)=\frac{N(t)^2}{27d(t)^4},
\]

shows that every prescribed rational output `c` has at most eight finite
parameter preimages: they are roots of the nonzero polynomial
`N(t)^2-27c d(t)^4`, of degree at most eight. Nonconstancy ensures this
polynomial is never identically zero. The image of the rational parameters,
and even of the positive integer parameters, is therefore infinite.

For a reduced rational number `x=m/n`, with `n>0`, define
`H(x)=max(|m|,n)` and `h_abs(x)=log H(x)`. For a positive complementary pair,
the two coordinates have the same reduced denominator, and that denominator
equals both heights. Indeed, `1-m/n=(n-m)/n` remains reduced.
There are only finitely many rational numbers of height at most any fixed
constant. Combined with finite fibers, this proves

\[
 H(a'(n))=H(b'(n))\longrightarrow\infty
 \quad\hbox{as integers }n\longrightarrow\infty.
\]

The same holds for the logarithmic height. This conclusion does not assert
that all integer-parameter outputs are distinct or that their heights are
monotone. For example, `t=2` and `t=3` have equal denominator but different
outputs. A subsequence with distinct pairs can be selected because the image
is infinite.

## 7. The positive-root convention must not be silently changed

The exact embedded-field statement concerns the root `u'` constructed above,
whose square is `1+qA`. If `a>0`, `A` is chosen positive, and the new quartic
field is instead defined canonically as

\[
 K_+(a')=\mathbb Q\bigl(\sqrt{1+\sqrt{a'}}\bigr)
\]

using positive real square roots, then `sqrt(a')=|q|A`. When `q<0`, this
canonical field is `Q(v')=Q(v)`, rather than the embedded field `K=Q(u)`.
These embedded fields are distinct: equality would put both `u` and `v` in
the degree-four field `K`, contradicting `[L:Q]=8`. They are conjugate and
isomorphic as abstract number fields.

This convention issue is absent on the explicit infinite family `t=n>=1`.
There the numerator of `q` is strictly positive: for `n>=1`,
`54n^2-12n-5 >= 42n-5 > 0`, and the remaining terms are positive.
Thus `q>0` and the canonical positive-root quartic field also equals `K`
as an embedded field for the entire sequence used to prove height divergence.

## 8. Exactly what the example rules out

Let `D_K` and `D_L` denote the absolute field discriminants of the two fixed
number fields. They are constant throughout the integer-parameter family.
Consequently there is no finite-valued function `F` such that

\[
 H(a,b)\le F(D_{K(a,b)},D_{L(a,b)})
\]

for every positive independent rational complementary pair, where
`H(a,b)=max(H(a),H(b))` and the selected-root convention is respected. The
same counterexample applies to any proposed bound depending only on these
fixed fields, their degrees, or invariants determined by these fields alone.
An effective finite list of possible fields does not by itself give finitely
many complementary pairs or a height bound on their presentations.

The normalized polynomial discriminant is a different object:

\[
 \operatorname{disc}(X^4-2X^2+b')=256(a')^2 b'.
\]

Indeed, multiplying the six squared root differences for `u',-u',v',-v'`
gives `16 u'^2 v'^2 (u'^2-v'^2)^4 = 16 b' (2qA)^4`.

It varies with the rational presentation, and clearing denominators introduces
an integral generator and an order whose index is not controlled by the field
discriminant alone. In particular, the fixed-field theorem must not be
misreported as constancy of polynomial discriminants or integral orders.

The example does **not** show any of the following:

- That any pair in this family is the normalization of a primitive Beal triple
  `A^3+B^5=C^7`, or of a solution with other exponents greater than two.
- That infinitely many such perfect-power pairs lie in one field fiber.
- That a discriminant-to-height estimate restricted to the Beal perfect-power
  branch is false, or that an estimate using additional generator, order,
  valuation, conductor-with-extra-data, or perfect-power information is false.
- That the radical of numerator and denominator supports is bounded. Their
  square classes and the fields' ramification are fixed; the full prime
  supports of the rational presentations need not be fixed.
- That a radical-scale bound involving the actual `rad(ABC)` is impossible.
- That the Beal conjecture has been proved, refuted, or newly excluded on a
  full integer family.

The smallest remaining implication for a Beal application is an independently
proved restriction on the intersection of this rational-presentation space
with the primitive perfect-power conditions. Field discriminants alone do not
supply that restriction. Determining this intersection is a separate
Diophantine problem; it has not been solved by this audit.

## 9. Source and computation checks; safe status

No external theorem or bibliographic assertion is needed for the fixed-field
and unbounded-height proof. The only field facts used are proved above or are
elementary definitions and degree multiplicativity. The argument was derived
from the raw claim, then compared with Block 45 Sections 4–7. It does not rely
on any prior status label as evidence.

Checks actually run:

- `sha256sum inputs/Komorebi_Beal_Block45_Arithmetic_Lift_v4.5.0.zip` returned
  the exact base digest recorded above.
- A Python `fractions.Fraction` check evaluated `t=-1/3,0,1,2,3,10` and checked
  both the conic equation and `a q^2+b h^2=1` exactly. The four displayed sample
  rows agree with that check. This finite check is corroboration, not the proof
  of the universal identities or infinitude.
- A requested SymPy import was unavailable in both the default and supplied
  primary Python runtime. No symbolic-computation success is claimed. The
  polynomial identities and displayed rational formulas were expanded by hand.
- No Lean code was written or compiled in this subtask.

Strongest safe statement: the elementary fixed-field deformation and the
positive infinite family with unbounded height are proved; unrestricted
field-discriminant-only height control fails on complementary rational pairs.
The Beal-restricted arithmetic implication remains open here.

Proofreading self-review: this file alone was reviewed for notation, domain,
root-sign conventions, and consistency of the explicit fractions. No separate
mathematical-token correction was required after the review.
