# Independent audit: torsion distance and exceptional birth depths

Review date: 2026-10-25.

**Primary verdict: proved as written.** The report's sharp two-term
distance formula, its dictionary to the output valuations, and its
bounded-exponent uniformity counterexample are correct under the stated
hypotheses. The cited primary theorems have the coefficient and
subvariety dependence reported. Their application supplies no additional
uniform bound on the exceptional depths. No conclusion about the
large-`n` target or ABC follows from the counterexample.

One implicit logical step should be stated when quoting the Hensel
argument: its compatible least positive representatives are nondecreasing.
That fact, together with unboundedness, proves that the heights tend to
infinity. Unboundedness alone would not have sufficed.

## Claim card and dependencies

The local claim fixes an odd prime `p`, coprime positive integers
`A>B>=1` with `p` not dividing `AB`, the valuation `v_p(p)=1`, and
`d=ord_p(A/B)`. It asserts the attained optimum

\[
\max_{\zeta\in\mu_\infty}v_p(A-\zeta B)
=v_p(A^d-B^d)=e_p,
\qquad
\min_{\zeta\in\mu_\infty}|A-\zeta B|_p=p^{-e_p}.
\]

Here `mu_infinity` is the group of all roots of unity in `C_p`.
The positive rational `A/B>1` ensures that none of the evaluated forms
vanishes. The maximum ranges over arbitrary torsion orders, including
those divisible by `p`.

The Hensel claim fixes `n=2,p=5,B=1`, varies integer coefficients `A_m`,
and defines `W_2` exactly as in the input note. It asserts a positive
lower limit for `log(W_2)/log(A_m^2+1)` along heights tending to
infinity. The analogous construction uses any fixed prime `p=1 mod 4`.
This is a statement about varying coefficients and bounded exponent.

The dependency graph is:

1. unit reduction and simple-root lifting -> Teichmuller root `omega`;
2. prime-to-`p`/`p`-power decomposition of torsion -> exact competing
   distances -> sharp two-term optimum;
3. `p|A^n+B^n` -> `omega^n=-1` -> factorization dictionary and the
   additional ramified valuation `v_p(n)`;
4. fixed-coefficient / fixed-subvariety source contracts -> applicable
   separation, with no coefficient-uniform transfer;
5. compatible Hensel lifting -> growing coefficient heights and named
   prime depth -> counterexample to uniform height decay at fixed `n`.

The local calculation and the counterexample are internal elementary
proofs. The external leaves are only the exact source contracts, not
unexamined proofs of those papers.

## Independent derivation of the sharp optimum

Put `x=A/B`. Its reduction is in `F_p^*` and has exact order `d`, with
`d|p-1`. The simple root of `T^d-1` lifting that reduction is a unique
`omega in Z_p^*`, and its order is exactly `d`. Thus
`x=omega u` with `u in 1+p Z_p`.

Since `p` does not divide `d`, expansion of `(1+(u-1))^d` shows
`v_p(u^d-1)=v_p(u-1)`: the linear term has a unit coefficient and
every later term has higher valuation. Because `B` and `omega` are
units and `omega^d=1`,

\[
v_p(A-\omega B)=v_p(u-1)
=v_p(u^d-1)=v_p(A^d-B^d)=e_p.
\]

The last number is a finite positive integer: `p` divides the indicated
nonzero positive integer and `A>B` prevents its vanishing.

Every root of unity has a unique decomposition `zeta=nu eta`, with
`nu` of order prime to `p` and `eta` of `p`-power order. The latter
reduces to `1`. If `nu` and `x` have different reductions, then
`A-zeta B` is a unit. If their reductions agree, uniqueness of
prime-to-`p` torsion lifting that residue implies `nu=omega`.

For nontrivial `eta` of exact order `p^r`,

\[
v_p(1-\eta)=\frac1{\varphi(p^r)}
=\frac1{p^{r-1}(p-1)}.
\]

This familiar elementary identity follows, for example, by evaluating
the cyclotomic product at `1`: its product is `p`, and the conjugate
primitive factors have the same valuation. Since `p` is odd, this
valuation is strictly below `1`, whereas `e_p>=1`. Applying the
unequal-valuation triangle rule to `u-eta=(u-1)-(eta-1)` therefore gives
the report's exact value for every nontrivial neighbor. The unique
maximizing root is `omega`, proving both extrema and their attainment.

The oddness assumption matters. At `p=2`, a torsion neighbor can have
valuation at least `1`, and the displayed comparison no longer proves
the same formula. No such endpoint is claimed. The assumption
`p` not dividing `AB` likewise supplies the unit normalization used
throughout. Scaling coefficients cannot remove the problem in a
normalized form: here both already have absolute value `1`.

For a two-term form with two varying torsion multipliers,
`A zeta_1-B zeta_2`, multiplication by the unit `zeta_1^-1` reduces
exactly to this calculation with `zeta=zeta_2/zeta_1`. Thus the
computed optimum is also the optimal positive lower constant for this
specific two-term instance of the cited linear-form theorem.

## Exact transfer to the common-power input

Suppose now that the same odd `p` divides `A^n+B^n`. Reduction gives
`x^n=-1`, and hence `omega^n=-1`: both sides are prime-to-`p`
torsion with the same reduction, whose lifts are unique. Therefore the
root of deepest contact occurs in the exact factorization

\[
A^n+B^n=\prod_{\zeta^n=-1}(A-\zeta B).
\]

For completeness, write `n=p^s m` with `p` not dividing `m`. The
factors reducing to the contact root are precisely
`zeta=omega eta` with `eta in mu_(p^s)`. Every other factor is a
unit. The `eta=1` factor contributes `e_p`. For each `1<=r<=s`,
there are `phi(p^r)` factors with `eta` of exact order `p^r`, each
contributing `1/phi(p^r)`. Their total contribution is therefore `s`.
This proves directly that

\[
v_p(A^n+B^n)=e_p+s=e_p+v_p(n).
\]

In particular the report's separable case `p` not dividing `n` and
its statement about ramified neighbors are exact, with no lost
valuation. This also shows why a determinant estimate accounting for
ramification does not estimate the already unramified contact `e_p`.

## Primary-source contracts and their application

The following are short contract checks, not whole-paper proof audits.
The author-hosted PDFs were opened directly on 2026-10-25; their titles,
authors, relevant statements, and displayed version information were
checked. No complete source text was copied into the project.

**S1.** John Tate and Jose Felipe Voloch,
[*Linear forms in p-adic roots of unity*](https://web.ma.utexas.edu/users/voloch/Preprints/root10.pdf),
author manuscript `root10.pdf`. Theorem 2, printed page 9, fixes the
finite coefficient tuple in `C_p` before choosing a positive lower
bound for all nonzero torsion evaluations. Lemma 2, page 11, bounds a
ramified Vandermonde valuation by `r(r-1)/(2(p-1))`. Proposition 3,
pages 12-13, assumes an unramified coefficient field,
`p>N(N-1)/2+1`, and finite relevant `V_m`, before reducing a close
evaluation to a common `p`-power twist of prime-to-`p` roots. Section 4,
page 15, poses global weighted-series convergence as a question for
`N>=3`; it does not prove that convergence. No revision date was
identified on these inspected statements.

**S2.** Thomas Scanlon,
[*The conjecture of Tate and Voloch on p-adic proximity to torsion*](https://math.berkeley.edu/~scanlon/papers/tvfo20m99.pdf),
dated 4 February 1999, revised 20 March 1999. The Main Theorem, page 1,
fixes a finite extension `K/Q_p`, a semiabelian `G/K`, and a closed
`X/G` defined over `C_p`. It then bounds the proximity of every
torsion point outside `X`, with a constant depending on `X`. The
statement permits all torsion orders and does not assert uniformity
as `X` varies.

Both source contracts are **verified** in these exact versions.
The transfer of their constants to an independent coefficient-uniform
depth estimate is **inapplicable** without additional quantitative input.

Our `Q_p` unit coefficients give `N=2`, independently of `n`.
The relevant `V_m` lies in one projective point for `m>=1`, so the
Proposition 3 conditions hold at every odd `p`. The possible
Vandermonde loss is at most `1/(p-1)`. The maximizing `omega` already
lies in `Q_p`; removing ramification therefore leaves `e_p` untouched.

For Scanlon's theorem, `G=G_m^2` is defined over `Q_p`, and
`X_(A,B): AX-BY=0` is a permitted fixed closed subvariety for each
fixed pair. The points `(1,zeta)` are torsion and lie outside that
subvariety. With the natural primitive equation/unit-coordinate
normalization, its local evaluation is precisely the form computed
above. Different conventions for the proximity function may change an
additive normalization; no exact optimal Scanlon constant for every
such convention is being asserted. The unbounded local contacts under
varying `A,B` remain decisive.

Fixing the diagonal instead would require moving `A/B` into point
coordinates. Such a point is not torsion, because `A/B>1` is not a
root of unity. Adding the coefficients as coordinates also loses the
torsion hypothesis. Thus the report correctly identifies both possible
dictionary failures: a varying subvariety or a nontorsion point.

## Independent check of the Hensel construction and its scope

For `p=5`, start with `A_1=2`. If `A_m` is fixed modulo `p^m`, a
lift has the form `A_m+t_m p^m`, with `0<=t_m<p`. Expanding its
square gives a unique digit solving

\[
(A_m^2+1)/p^m+2A_m t_m=0\pmod p,
\]

because `2A_m` is a unit. The representatives therefore satisfy all
the stated congruences and `1<=A_m<p^m`.

They are nondecreasing, since `A_(m+1)=A_m+t_m p^m` with nonnegative
digit. If bounded, they would eventually be a fixed integer `A`, and
`p^m` would divide `A^2+1` for arbitrarily large `m`, impossible.
Hence `A_m` tends to infinity, and so does `c_m=A_m^2+1`. Occasional
equal consecutive representatives are allowed; strict increase at
every index is neither true nor needed.

The reduction has order exactly `4` because `A_m^2=-1 mod p` and
`p` is odd. Moreover `A_m^2-1=-2 mod p` is a unit, so

\[
e_p=v_p(A_m^4-1)=v_p(A_m^2+1)\ge m.
\]

All other factors of `W_2` are positive integers at least `1`.
Thus `W_2>=p^(m-1)`, while `c_m<2p^(2m)`. Dividing their positive
logarithms proves the displayed ratio bound, also at `m=1`, when
its lower numerator is zero. Its right side tends to `1/2`.
Consequently the claimed lower limit is at least `1/2`; neither
convergence nor equality is implied.

For any prime `p=1 mod 4`, start with either primitive fourth root
modulo `p`. The same proof applies. Such primes occur above every
fixed cutoff: an elementary Euclid argument uses a prime divisor of
`(2P)^2+1`, where `P` is the product of a hypothetical finite list;
the divisor has an element of order `4` modulo it and is outside the
list. Thus no appeal to a prime-distribution theorem is required.

The exact uniformity conclusions are:

- It refutes `log W_n=o(log c)` as `c` tends to infinity uniformly
  over coefficients and all admissible `n`, since `n=2` already fails.
- It also refutes that assertion uniformly in the coefficients with
  `n=2` fixed, even after removing any fixed finite set of primes.
- It does not refute a statement whose limit parameter is `n` tending
  to infinity, a statement with fixed coefficients, or a statement
  discarding a prime cutoff that itself grows with height.
- It does not refute ABC. The input radical `D=rad(A_m)` has not
  been bounded, and it is part of the ABC radical budget. In fact,
  here `W_2=U(c_m)`, but that identity alone controls only the output.

## Obligation matrix

| Obligation | Status | Decisive evidence |
| --- | --- | --- |
| Teichmuller root and exact local depth | Passed | Simple-root lift; unit linear coefficient |
| All torsion orders covered | Passed | Unique prime-to-`p` / `p`-power decomposition |
| Sharp maximum/minimum and nonvanishing | Passed | Unique maximizing `omega`; `A/B>1` |
| Factorization and `v_p(n)` contribution | Passed | Exact sum over neighboring root orders |
| Tate-Voloch source contract | Passed | Theorem 2, Lemma 2, Proposition 3 in author PDF |
| Scanlon source contract | Passed | Main Theorem in dated/revised author PDF |
| Uniform coefficient/subvariety transfer | Inapplicable | The cited quantifiers permit their constants to vary |
| Hensel coefficient family and depth | Passed | Unique lift digit; order `4`; exact valuation factorization |
| Heights tend to infinity | Passed | Compatibility gives monotonicity before unboundedness |
| Ratio lower limit and fixed-cutoff scope | Passed | Named-prime lower bound; explicit height upper bound |
| Refutation of a large-`n` statement or ABC | Not addressed | Construction has `n=2`; input radical is uncontrolled |
| Finite verifier interpretation | Passed | Exact listed cases only, with no full-output factorization claim |

## Computation check and exact revisions

The verifier was inspected and executed with only its intended
`results.json` write intercepted. Its exact 40 cases reproduced the
stored case data and input hash. The two primes were `5,101`, and
the indices were `m=1,...,20`. Additional exact checks confirmed the
nondecreasing compatible representatives in those ranges. These
finite checks are auxiliary; the universal derivations above do not
depend on their range.

The original report, verifier, result, manifest, and input note were
unchanged before and after this execution. Audited SHA-256 values:

| Path under `abc_work/` | SHA-256 |
| --- | --- |
| `roots_unity/routes/torsion_distance/TRANSFER_REPORT.md` | `73e69d7c7f004cbc2f6e2305421f2540086e0b54ce5d6a70090af32466617a60` |
| `roots_unity/routes/torsion_distance/verify.py` | `abb9ce03da6db1bb34f6c5dd9f4b61ba09f84cb2966bfb2a3dd23509959e6834` |
| `roots_unity/routes/torsion_distance/results.json` | `70cf60c8ad390bc47ca40a10ced7fdaddb5d621f7fc6d1c1388a9444f888c4f0` |
| `roots_unity/routes/torsion_distance/SHA256SUMS.json` | `0ad649facf3fbd4c72279b2a96df818833c71d518266f3f680deab0073755fab` |
| `routes/global/PROOF_NOTE.md` | `f4b1c1eb8d4e52ee43634b454ea5fa3e12e88488dc148d76ea68e79a58e29bfc` |

External PDFs were authenticated and read through their author URLs;
their bytes were not retained, and no PDF checksum is claimed. This
review verifies their stated contracts and the application, rather than
auditing the complete proofs. Historical priority was outside scope.

This was an independent review of raw claims without a supplied desired
verdict. A fresh subagent additionally received only the exact Hensel
construction and independently checked its domain, height limit, ratio,
and uniformity scope. Agreement is supplementary to the displayed proofs.

## Remaining gap and cheapest next check

The report correctly leaves open a bound on exceptional local depths
coupled to the varying input radical, or a separate estimate in the
large-`n` regime. The fixed-coefficient separation theorems do not supply
that coupling. Before transferring any proposed stronger theorem,
write its coefficient, prime, torsion-order, and height quantifiers
explicitly, and test the bounded-`n` Hensel family against the claimed
range. The family prevents overlooking that range; it is not a general
impossibility result for torsion methods.
