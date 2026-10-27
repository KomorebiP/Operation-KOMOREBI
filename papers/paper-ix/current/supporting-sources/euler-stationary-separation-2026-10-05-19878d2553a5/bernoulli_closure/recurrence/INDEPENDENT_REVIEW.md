# Independent review of the constrained tangent and contiguous contact

Review date: 2026-10-05. This separate subagent review was read-only until
creation of this note. It used the proof-audit skill. Proposed numerical units
were supplied with the task, so the review was independent but not blind.

**Normalized claim.** For every admitted ordinary index
`r=(17659+2^18 T)2^640-161` with true terminal161, the recurrence-compatible
scale direction has the stated nonzero stationary jets, and the adjacent-index
logarithmic mismatch is exactly the original critical-value valuation plus25.

**Primary verdict: conditional on a named input.** The new algebra, unit
computations, and precision accounting pass, conditional on the inherited
actual quadratic-chart theorem and packet/source bounds cited in Sections5-6.
This review did not reprove the entire inherited chart certificate or compile
Lean. No error remains in the new implications reviewed here. In particular,
this is not a proof of actual critical-value nonvanishing or universal simplicity.

## Pinned artifacts and provenance

| Artifact | SHA256 |
| --- | --- |
| `CONSTRAINED_TANGENT_AND_CONTIGUOUS_CONTACT.md` | `84e3cf9cd9394fe2d4a1847ccf1011785cd9f6c2c8bc0262b55d3c64f329f0b2` |
| `check_constrained_tangent.py` | `75e152aa24341043e70db4131496758279cea4667786d4ed4536fd9f60d0da3d` |
| `frozen_run/manifest.json` | `eb43be2a5f3281ea0b68fb08282f1810b991d4e03e1167db4c779fdc5d367cd4` |

The proof/checker hashes were read directly during review. The coordinating
agent reported successful validation of the frozen manifest and its hash.
`certified_run` is historical and superseded by `frozen_run` after correction
of the inherited source locator from Section4 to Section3. `RUN_STATUS.md`
records the run history. This review is separate from the evidence it reviews.

## Dependency and obligation checks

The dependency chain is: Riccati recurrence -> unique coefficient scaling ->
weighted packet jets -> stationary cancellation and inherited quadratic unit
-> implicit-center and Schur formulas. Independently, the scalar coefficient
ratio and packet factorization -> contiguous identity -> exact logarithmic
mismatch. Neither chain proves nonvanishing of the critical value itself.

| Obligation | Finding |
| --- | --- |
| Riccati coefficient comparison and fixed-beta1 rigidity | Passed: induction gives `a_n(v)=v^n a_n(1)`; fixing beta1 fixes v. |
| Coordinate/scale powers in the three partial derivatives | Passed: powers are `2^-154`, `2^-139`, `2^-130`. |
| gamma2 unit and source congruences | Passed: denominator odd product and Bernoulli ratio give unit1; the cited source expansion gives the required shifted units. |
| Stationary mixed derivative | Passed: packets0,2,162 contribute `-1+4+4=7 mod8` after division by `2^155`. |
| Center derivative and Schur complement | Passed: mixed valuation16/unit7 gives center valuation15/unit1; correction valuation31/unit1 changes direct curvature unit7 to critical curvature unit3 at valuation29. |
| Contiguous identity and logarithmic formula | Passed by the exact derivation below. |
| Bounded replay and precision | Passed in the stated three-case scope; details below. |
| Inherited uniform actual quadratic chart | Conditional named input; cited sources inspected, full inherited certificate not re-audited. |
| Universal simplicity, actual nonvanishing, Lean compilation | Out of scope and not claimed. |

For packet162, the nearest falling-factor point is90 and `v2(x-90)=7`.
Removing that factor leaves valuation `v2(90!)+v2(71!)=153`; all other
derivative terms have larger valuation. Thus its derivative has exact
valuation153, and scalar valuation4 gives the required contribution at157.
Direct integer falling-product evaluation at x=10202 also gave valuations
160 and153 for P and P' for both q161 and q162. This is corroboration of
the argument, not coverage of the entire chart.

## Exact adjacent-index derivation

Let `cost_r(q)=3q+s2(r+q)-s2(r)`. Since r has exactly five trailing binary
ones, `s2(r+1)-s2(r)=-4`, and therefore

    cost_(r+1)(q)=cost_r(q+1)+1.

The true minimum -154 at final index161 transfers to minimum -153 at final
index160. The exact scalar formula, including these normalizations, gives

    gamma^(r)_(q+1)=(gamma^(r)_1/2^153) gamma^(r+1)_q.

Together with `P_(q+1)(x)=P_1(x)P_q(x-1)`, this proves the contiguous
identity as a convergent restricted-series identity. It is not inferred from
the three sampled modular equalities.

Write `C=2^154`, `P=P_1`, and `F=G_(r+1)(x-1)`. From
`G=C A+u P F`, the chart bounds give `v2(F)=153`. At `G'=0`, the term
`P'F` has valuation153 and `C A'` has valuation155, so `P F'` has
valuation153 and `v2(F')=152`. Dividing the stationary differentiated
identity by `G-C A=u P F` yields

    P'/P+F'/F=-C A'/(G-C A),
    L=(A'/A) G/(G-C A).

Here A is a unit, `v2(A')=1`, and `v2(G-C A)=154`, whereas
`G=2^178 Phi(0)`. Consequently `v2(L)=25+v2(Phi(0))`, with infinity
on both sides when the critical value is zero. The denominator stays nonzero.

## Replay and precision

Independent replay command, exit status0:

    python bernoulli_closure/recurrence/check_constrained_tangent.py /tmp/tangent-review.json

The checker tested recurrence degrees1 through24 at scales1,3,5/9 and actual
T values0,718787533,22831001499602523078606181325. Critical-value valuations
were0,30,91 and contact valuations25,55,116. Every claimed normal-direction
valuation and unit passed. The neighboring coefficients were rebuilt rather
than obtained by solving the contiguous identity; both reconstructions still
share the inherited Bernoulli/source arithmetic, which this review does not
describe as implementation-independent.

The omitted scalar packets vanish coefficientwise modulo `2^320` by the
stated digit-sum cutoff. Integer weights and ordinary differentiation preserve
that bound. K therefore has142 bits, its half derivative141, and the physical
center error has valuation at least156. The raw normalized V, V_Z and W
computations retain respectively166,166,190 bits. K_ZZ is evaluated to120
bits; division by2 leaves119 bits, sufficient for the100-bit Schur calculation.

The center-substitution bounds in Section5 are sufficient: K changes only at
valuation at least282; normalized V, V_Z and W retain at least157,161,182
bits. In particular `V_ZZ>=174` follows from `158-2*7+30`, and
`W_Z>=171` follows from `158-7+5+15` at the leading upper packet.
The analogous third-derivative bound gives `K_ZZZ>=4`, so changing c at
valuation141 affects K_ZZ only at valuation at least145, beyond120 bits.

The neighbor's value and normalized derivative retain at least155 and148
bits under center substitution. Extracting F_x from the affine derivative
loses15 global bits; normalizing by `2^152` then leaves153 bits, beyond
the140-bit adjacent comparison. As a separate consistency check, stationarity
at the computed representative implies `v2(G_x)>=305`; its error in the
displayed formula for 2L has valuation at least152, also beyond140 bits.
The logarithmic generating-series proof of the factorial derivative bound
supports the first, second and third derivative bounds used here.

## Remaining implication

The strongest supported conclusion is the stated normal-direction certificate
and exact contiguous reduction, under the inherited admitted-chart input.
The remaining arithmetic obligation is still `Phi(0)!=0` for every admitted
actual ordinary index. A nonzero scale derivative and a regular neighbor
provide no implication forcing this. No additional parameter digits or search
were used, and no further computation can convert the displayed identity for L
into an independent contact obstruction without a new mathematical input.
