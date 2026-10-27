# Final Euler edition: mathematical-delta audit

**Normalized claim and verdict: proved as written.** The actual reciprocal coefficients are
`G_(N,j)=j! sum t^(Nn)/(Nn+j)!`, `G_(N,j)^(-1)=sum C_(N,j)(n)t^(Nn)/(Nn)!`, and
`E_(Nn)^(N,j)=j! C_(N,j)(n)`. The new congruence, exactness and analytic statements are correct under their stated quantifiers and explicit classical input. No critical or major unresolved issue was found in the reviewed delta. The separate universal ordinary Euler-tail simplicity and actual discriminant-nonvanishing targets remain open and are outside the proved verdict.

This is an internal parallel computational-assistant review. It is not external peer review. The author sources were read only by this reviewer; the authors made the listed corrections. The audit itself supplies reports and exact check artifacts. The JSON companion pins every reviewed current source and the retained raw proof revisions. The strengthening chapter reviewed here has SHA256 `996ca78acb432a8ac58050bea7849cd92edeed21e5e6ba923d4cea41dd183c77` and 1,414 lines.

## Exact claim cards

- For a prime `p`, `N=p^a` with `a>=1`, every `0<=j<N`, row `n>=0`, order `k>=1`, and positive steps `H_i`, the signed sequence `A(n)=(-1)^n C(n)` has ordinary mixed valuation at least `k+sum v_p(H_i)`. Raw original coefficients use `T_H=S^H-(-1)^H` and add `v_p(j!)`. At `p=2`, ordinary raw differences satisfy that bound; the dyadic statement also includes `N=1`.
- At `N=4`, all four normalized addresses have mixed lower bound `k+v_2(k!)+sum v_2(H_i)+beta_j`, with `beta=(0,0,3,1)`. Address two also has `2k+v_2(k!)+floor(k/2)+sum v_2(H_i)`.
- Addresses zero and one attain their mixed factorial baseline exactly iff the order is odd or the number of even steps is even. The remaining class gains at least one bit; no deeper universal equality is asserted. All homogeneous positive steps attain the baseline.
- Address two has exact mixed values at every positive power-of-two order: base exponents `4` at order one, `6` at order two, and `2k+v_2(k!)+k/2` at powers at least four, plus step valuations. Original coefficients add one.
- Every first displacement at ranks two, four and eight has the listed exact metric. All lower-half addresses at every dyadic rank at least four have normalized offset one. Least periods are row periods, and literal Euler-degree periods are `N` times those periods. Larger upper-half constant-scale extrapolation is explicitly refuted.
- Taylor radii are exactly `2` for addresses zero and one and exactly `2^(5/2)` for address two at every integral center. Address three has radius at least `2`; its exact radius is open. Boundary divergence concerns the constructed Taylor expansion and does not prohibit another continuation.

The final original-normalization common-step exponent is
`v_2(k!)+k v_2(H)+A_j(k)`, where
`A=(k,k,max(k+4,2k+floor(k/2)+1),k+2)`.
Its domain is `n>=0`, `k,H>=1`. Exactness is asserted at all orders for addresses zero/one and the power-of-two orders for address two. No positive-order surplus is asserted for an empty difference. Zero ordinary steps are handled separately, avoiding `0*infinity`.

## Dependency graph

1. The actual reciprocal definition and its triangular recurrence fix the object and factorial normalization.
2. Prime-power interior binomial divisibility gives the integral charged product rule. Affine reciprocal differences and the discrete product identity give source flatness. The commuting multinomial expansion isolates a unique highest inverse order; induction in the full Hurwitz lattice gives reciprocal flatness without a row constraint. Sign conversion and finite step polynomials give the all-row mixed theorem.
3. The exact classical Frobenius congruence supplies odd integral divided-power moments for ordinary Euler variables. The explicit Gaussian factorization and component-by-component divided-power algebra give address-zero factorial moments and their leading parity. `Z_2[i] cap Q_2=Z_2` gives the rational descent; no assertion that `Z_2[i]/2` is a field is used.
4. The elementary Stirling denominator argument proves `2B_m` integral. Exact tangent transfer, scaled-binomial coefficient estimates, pointwise discrete products and uniform sums give the address-one extra bit.
5. Central factorials evaluate the Bernoulli moments exactly. Their finite recurrence proves integrality, the digit-sum estimate and the power-of-two parity pattern. The address-two Gaussian transform then gives the paired filtration and its infinite exact power-order family. Cotangent transfer with cancelled poles gives address three.
6. Finite step expansions classify every possible leading tie. The unique leading term proves exact mixed power orders at address two. Separate low-order coefficients settle orders one and two.
7. Newton/Vandermonde dominance, the complete low-coefficient tables and the proved infinite tail give the first-difference metric. Finite quotient bijections give least periods, exact images and residue enumeration. The lower-half proof uses source slopes in `4Z_2` and the central binomial residue six modulo eight.
8. Uniform Stirling conversion produces ordinary Taylor coefficients. Unique diagonal contributions give exact slopes at zero/one; the unbounded power-of-two subsequence gives the exact address-two radius. Integral translation preserves those unique leading terms.
9. The ordinary Euler-tail appendix uses its own `sech` coefficients, exact weighted packet identity, carry minimum and finite preparation. The regular-wall and terminal-family statements retain their source hypotheses and coefficient certificates. Actual quadratic preparation includes the unit-cofactor derivative; its discriminant identity and actual approximation yield a strict-test equivalence, not universal nonvanishing.

The sole external arithmetic input in the new factorial route is Frobenius's exact ordinary Euler congruence. The preserved primary-source check authenticates Gessel's arXiv version and the required `sech` normalization and all-starting-index statement. This pass reused that durable check and did not retrieve an external paper anew. Address-two and address-three arithmetic is derived internally. The separate classical tail weights retain the earlier Bernoulli denominator dependency and formal endpoint; this audit does not claim a fresh source or kernel execution for that dependency.

## Obligation matrix

| Obligation | Result |
|---|---|
| Actual coefficients, degrees, row shifts, `j!` and address ranges | Passed |
| Full-lattice reciprocal induction, signs and source flatness | Passed |
| Gaussian divided powers, functional linearity, rational descent | Passed |
| Central-factorial Bernoulli integrality and parity | Passed |
| Factorial/mixed exponents and leading-cancellation criterion | Passed |
| Low and large address-two power orders at all rows and steps | Passed |
| Metric criterion, finite cutoffs, least periods and exact images | Passed |
| All-rank lower-half proof and explicit upper-half counterexamples | Passed |
| Uniform Taylor conversion, exact slopes, centers and radius interpretation | Passed |
| Classical-tail reduction and exact residual open obligation | Passed within the preserved hypotheses |
| Inherited formal coverage versus new uncompiled endpoints | Passed |
| Universal tail simplicity or discriminant nonvanishing | Not addressed; expressly open |
| Fresh Lean compiler run and full inherited IX re-audit | Out of scope |
| Final PDF layout | Out of scope here; separate release visual review |

## Corrections and final state

Five local issues were reported and resolved by the respective authors:

1. The retained tail paragraph had to recognize the later exact finite-polynomial reduction, leaving explicit root/simplicity classification open.
2. The retained analyticity paragraph had to point to the completed factorial/Taylor argument.
3. The prior 54-proof review and regression counts had to be identified as inherited prior-edition evidence, with the strengthened-edition checks separate.
4. The Lean guide's display had to exclude zero steps while describing its separate finite `padicValNat 2 0=0` boundary convention.
5. The final first-order sentence had to say the displayed bounds are exact, rather than claiming a stricter bound with identical offsets.

The revised open-questions section correctly distinguishes solved address-zero/one classification, address-two power orders, remaining address-two/three questions, completed small-rank/lower-half metric families, and the refuted upper-half extrapolation. No corrective change to a load-bearing algebraic proof or exponent was needed.

## Fresh exact arithmetic and provenance

`evidence/delta_boundary_checks.py` independently constructs the reciprocal from the defining triangular recurrence using `fractions.Fraction`, then computes signed stencils directly. Its bounded runner passed:

| Finite family | Cases |
|---|---:|
| Exact homogeneous address-zero/one laws | 192 |
| Mixed leading-parity address-zero/one laws | 720 |
| Exact mixed address-two orders `1,2,4,8` | 834 |
| Generic dyadic/signed prime-power lower bounds | 480 |
| Ordinary Euler-tail source units | 25 |

The run contains 2,251 family cases, three additional initial-definition checks and one mixed-cancellation control. The control independently recovers `Delta_1 Delta_2 C_0(0)=-33728`, valuation six, baseline four. The exact ranges are in `delta_boundary_contract.json`. The separately executed metric-table gate recomputed all 47 low Newton valuations printed for ranks two, four and eight and all six first/two-row upper-half counterexample valuations. It also recovers the printed rank-sixteen rational differences exactly.

The counting unit is a parameter case or coefficient certificate, rather than a literal count of Python assertion statements. Both runs have validated version-two manifests, declared input and result hashes, actual Python version, exact bounds, no randomness, and enforced execution limits. They are separate overlapping checks and are not added to the inherited million-case regression totals. The metric finite coefficients supply precisely the low-order certificates; the universal conclusion still uses the proved infinite-tail criterion. No finite check proves every row, every step or an analytic radius by itself.

## Fresh versus inherited evidence

The fresh manuscript review includes all thirteen explicit proof environments in the new strengthening chapter, the four in the root appendix, and their detailed intervening algebraic proof paragraphs. Those are TeX-environment counts, not counts of discoveries. The broader prior 54-proof review, 82 preserved historical proof bodies, formal compiler frontiers and archived numerical gates remain inherited evidence. This reviewer did not re-audit the entire retained historical Paper IX or execute Lean/Lake. Static source and log reconciliation does not expand formal coverage.

Actual inherited formal coverage includes the completed Nishibuchi capstone, the rank-four all-row homogeneous `k(1+v_2(H))` bound, sharp first differences, least periods and isometry/image conclusions. The general prime-power, heterogeneous mixed, factorial, exact higher-order, broader-rank and Taylor-radius endpoints remain uncompiled in this edition. The guide now states this claim by claim.

## Exact remaining boundary

There is no missing implication in the reviewed new congruence/analytic delta. The open work is expressly outside those claims: full address-two non-power-of-two and address-three valuation classifications; exact address-three radius; larger-rank upper-half metric classification; nonzero actual stationary discriminants for every admitted ordinary index; universal classical tail simplicity; and the separate Native 13.2/13.3 general programs. In particular, convergent nonzero models, nonzero integer representatives and necessary multiplier residue classes are not promoted to a universal nonvanishing proof.

The cheapest check for a later edited manuscript is to compare its hashes with the JSON companion and re-review changed mathematical tokens before treating this audit as current. A later formal completion additionally requires actual compiler acceptance and matched theorem/axiom/contract evidence for the new endpoints.
