# Source check: exact quartic packets and Euler coefficient coordinates

EULER-CASE-006 · checked 29 October 2026. Scope: selected results in Komorebi
P., **Paper IX, Euler Congruences: Completion, factorial strengthening, and
sharp dyadic geometry**, and pinned Komorebi Math implementations. This is not
a global novelty search. Exact revisions and hashes are in
[LITERATURE_ATLAS.json](LITERATURE_ATLAS.json).

## Sources and exact extraction

The collection source revision is
`4b1afc89549ae9c8e101f32459fb514203baaabd`. The author/title and the relationship
between normalized C_(N,j), original U_(N,j), and classical Euler coefficients
were checked in the README and the actual arithmetic definitions.

**20_arithmetic.tex**, under `papers/paper-ix/current/sources/main/parts/`:

- `def:arith-euler`, `eq:arith-kernel`, `eq:arith-triangular`: definitions and
  source/product normalization. C_(N,j)(0)=1, U_(N,j)=j! C_(N,j).
- `thm:arith-dyadic-differences`: source theorem used as a universal input, with
  N=4, 0<=j<4, n,k natural and positive step u. It has no row cap. The source
  proof was read through the odd denominators, pointwise difference closure,
  charged Hurwitz product/inverse closure, coefficient extraction and step
  amplification. Inversion uses separately established integrality, avoiding a
  circular integrality assumption. This extension does not rerun Lean.
- `lem:arith-dominance`, `thm:arith-exact`: the finite Newton dominance envelope,
  finite prefix valuations, exact nonzero displacement, gains c=(1,1,4,2) and
  original gains d=(1,1,5,3). All finite prefix entries used by the source proof
  were independently recomputed from the recurrence.
- `cor:arith-least-period`: all positive packet periods, not just sufficient
  powers of two. The precise index is compressed n, not full degree.
- `thm:arith-isometry`, `cor:arith-affine-image`: unique continuous isometric
  bijections of Z_2 and original affine images. The worked extension supplies a
  constructive inverse-limit argument and an explicit binary inverse.

**72_recovered.tex**, in the same folder:

- `hist:def:hurwitz_ring`, `hist:prop:mode_addition`,
  `hist:thm:mode_group_algebra`, `hist:prop:augmentation_criterion`, and
  `hist:cor:finite_inverse_formula`: Hurwitz sequences in characteristic p,
  faithful finite additive mode algebra and nilpotent geometric inversion.
  The exact proofs and their hypotheses were read. The paragraph about a dated
  unrestricted difference problem does not restrict these algebra identities,
  and is not used as support for any unresolved general family.
- `hist:def:amice_pullback_unified`, `hist:thm:amice_derivative_unified`:
  F(log(1+T)) and its formal derivative conjugacy. The adjacent weighted
  convergence statement is not used to assert convergence here.

Pinned software source revision:
`a3aa04ac18a523f30c50c7f5dba709f88e904eff` in KomorebiP/komorebi-math.
The analytic Appell implementation supplies an independent logarithmic route to
quartic coefficients. The Hurwitz implementation supplies modular inverse and
product values. The combinatorial and formal coordinate implementations supply
Stirling entries, log pullbacks, inverse jets and substitution matrices. These
are finite implementation comparisons, not substitutes for source proofs.

## Translation and application verdicts

| Application | Translation / hypotheses | Verdict and overlap |
|---|---|---|
| Four quartic addresses | C_j means C_(4,j), U_j=j!C_j; odd rational denominators, j=0..3 | **Verified; known after translation of notation.** These are not the classical E_(2n) sequence. |
| Universal displacement law | Positive T, all natural rows, nonzero first Newton coefficient and source all-row bound plus finite prefix | **Verified; known after translation of notation.** Written dominance argument reproduces the exact source reduction. Finite tests alone do not establish the all-row input. |
| Least periods and affine images | Modulo 2^r in Z_(2); compressed packet shifts, continuous extension to Z_2 | **Verified; known after translation of notation.** The r=10 period table follows from the universal proof, whereas the finite program tests actual period data only through r=8. |
| Binary inverse and row-21 witness | Phi_2=(U_2-2)/32; target 13 modulo 64; odd triangular diagonal | **Verified; formal corollary not stated.** Six lifts and independent 21-term triangular row give n=21 and U_2=418 modulo 2048. |
| Euler finite mode formula modulo five | Odd prime; cosh source in full-index Hurwitz coordinates; epsilon_0=delta with 0^0=1 | **Verified; formal corollary not stated.** The source's finite inverse gives weights (1,1,-1,-1,1). No division by p! or precision lifting is inferred. |
| Positive-tail period boundary | Full-index n>0, or compressed even n>=1 | **Verified; formal corollary not stated.** E_0=1 but E_4=0 modulo five, so the tail period does not include row zero. |
| Stirling logarithmic coordinates | Formal Q[[T]], full-index Euler coefficients, signed first Stirling convention | **Verified; formal corollary not stated.** Recurrences for both Stirling kinds establish the substitution and its inverse; no analytic hypothesis is hidden. |
| Rational log series and integer recurrence | sech(log(1+T))=(1+T)/(1+T+T^2/2); Hurwitz numerators retain factorial normalization | **Verified; formal corollary not stated.** The worked E_8 reconstruction is an exact coefficient calculation. |
| Derivative transport | Forward shift of full Hurwitz coefficients; target D+N with N diagonal n | **Verified; known after translation of notation.** The final checked derivative row uses input degree 17. No convergence conclusion is drawn. |

Authentication uses immutable Git objects fetched from origin and public source
content checks. Exact statement/proof extraction, notation translation and
application were performed. The source all-row theorem is a stated proof input,
not a claim newly certified by this assistant or by sampled data. There is no
independent review, new formal build, priority or speed claim, or unresolved
source hypothesis for the selected applications.
