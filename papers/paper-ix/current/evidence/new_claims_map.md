# Integrated Euler strengthening: claim and dependency map

This map concerns `sources/strengthening.tex`. It records the exact theorem boundaries in the new integrated chapter, rather than a historical priority claim. A matching inherited Lean result can verify a statement already present in an earlier release without verifying the new written proof route or a larger parameter family.

The authoring source is 1,414 lines. The final reviewed source SHA-256 is `996ca78acb432a8ac58050bea7849cd92edeed21e5e6ba923d4cea41dd183c77`. It compiles in isolation with the integrated main-paper preamble: 18 pages, no overfull or underfull box, and no remaining warning after two passes. The final integrated edition has its own render and review records.

## Objects and normalization

The objects are the actual reciprocal coefficients

\[
G_{N,j}(t)=j!\sum_{n\ge0}\frac{t^{Nn}}{(Nn+j)!},\qquad
G_{N,j}(t)^{-1}=\sum_{n\ge0}C_{N,j}(n)\frac{t^{Nn}}{(Nn)!}.
\]

The original convention is `E_{Nn}^{(N,j)} = j! C_{N,j}(n)`. The difference operators act on the row index `n`. Every positive-order original valuation gains `v_p(j!)`. Zero values have infinite valuation. All rows start at zero. Mixed steps are positive integers; a zero ordinary step makes the nonempty stencil zero. Empty differences assert integrality and do not receive the additional positive-order offsets.

## Statements

| Label in strengthening.tex | Exact claim | Proof dependency | Formal coverage in this edition |
|---|---|---|---|
| `lem:translated-hurwitz-product` | For `N=p^a`, translated types add under the integral Hurwitz product | Interior binomial divisibility; exact commuting tensor operators and multinomial expansion | Newly written general prime-power proof; no new Lean compilation claimed |
| `lem:translated-hurwitz-inverse` | A unit-constant lambda-flat source has a negative-lambda-flat reciprocal | Unique highest inverse-order term; induction in the full Hurwitz lattice | Newly written general prime-power proof; no new Lean compilation claimed |
| `thm:all-prime-power-transfer` | `A(n)=(-1)^n C_{p^a,j}(n)` has mixed ordinary bound `k + sum v_p(H_i)`; original raw coefficients have the matching sign-twisted bound plus `v_p(j!)` | Exact affine reciprocal formula; source products; translated reciprocal; finite step polynomial | General prime-power parameter family is new written coverage, awaiting dedicated Lean formalization |
| `cor:all-dyadic-final` | Every dyadic rank and address has ordinary mixed bound `v_2(j!)+k+sum v_2(H_i)` from row zero | `L_1=L_{-1}-1` at `p=2`; same finite step polynomial | Recovered Lean release covers rank-four homogeneous bound; general all-rank and general mixed theorem here are not newly Lean formalized |
| `thm:four-factorial-bound` | For `N=4`, normalized offsets `(0,0,3,1)` in `k+v_2(k!)+sum v_2(H_i)`; address two additionally `2k+v_2(k!)+floor(k/2)+sum v_2(H_i)` | Euler divided-power algebra for lane zero; exact tangent transfer for lane one; central-factorial Bernoulli algebra for lane two; exact cotangent transfer for lane three | New factorial and filtered results are written proofs with audits and exact tests; no dedicated Lean formalization |
| `lem:bernoulli-central-pd` | `mu_m=L((Z(Z+1))^m/m!)` is integral, has valuation at least `s_2(m)-1`, and is odd iff `m=0` or a power of two | Central-factorial basis; finite Vandermonde/beta identity; recurrence divisibility and parity | Internal finite algebra proof; no imported generalized Bernoulli congruence or new Lean verification |
| `thm:zero-one-exact-mixed` | Addresses zero/one attain factorial baseline iff `k` odd or the number of even steps is even; otherwise gain at least one bit; homogeneous steps always exact | Exact Euler divided-power parity and classification of tied local multi-indices | New statement, not part of inherited threshold-free bound |
| `thm:two-exact-power-orders` | Address two has exact mixed precision at every positive power-of-two order: `4` at `k=1`, `6` at `k=2`, `2k+v_2(k!)+k/2` at larger powers, plus step valuations | Bernoulli moment parity; normalized filtration; unique leading term; exact low coefficients | New written infinite-family theorem; no complete all-order formula and no new Lean compilation |
| `lem:newton-exact-isometry-criterion` | A noncancelling first Newton coefficient and logarithmic stronger tail imply exact first differences | Finite Newton/Vandermonde formula; closed-unit limit for the dyadic extension | New exposition of the criterion; matching rank-four conclusions have inherited formal coverage |
| `thm:rank-four-exact-periods` | Normalized first offsets `(1,1,4,2)`, original offsets `(1,1,5,3)`, least row periods `2^max(0,r-B_j)` | Exact low Newton coefficients plus proved infinite tail | Matching rank-four statements are inherited Lean results in recovered final strengthening/least-period modules; no fresh Lean execution inferred from this prose proof |
| `cor:four-exact-images` | Normalized continuation bijects `Z_2` onto `1+2^{b_j}Z_2`; original onto `j!+2^{B_j}Z_2`; one least period enumerates the exact coset once | Exact metric law; bijections on finite dyadic quotients and inverse limit | Matching rank-four isometry/image conclusions have inherited Lean coverage |
| `thm:lower-half-all-dyadic-isometry` | Every `N=2^a>=4`, `j<N/2` has exact normalized first offset one | Slopes in `4Z_2`; central binomial coefficient is six mod eight; two initial Newton coefficients and generic tail | New all-rank parameter family; no dedicated Lean formalization |
| `prop:two-four-eight-isometry-table` | Complete exact first-difference law at ranks two, four, eight with listed offsets | Exact rational finite coefficients and universal tail; full coefficient certificate retained | Rank-four inherited result; full rank-two/rank-eight extensions are not newly Lean formalized |
| `thm:four-taylor-radii` | Radius exactly two at addresses zero/one, exactly `2^(5/2)` at address two, at every integral center; address-three radius at least two | Uniform Stirling conversion; unique leading coefficients, with infinite power-of-two subsequence at lane two | New analytic theorem; no exact lane-three radius or new Lean compilation |
| `cor:final-euler-congruence` | Original homogeneous modulus `2^{v_2(k!)+k v_2(H)+A_j(k)}`, with `A=(k,k,max(k+4,2k+floor(k/2)+1),k+2)` | Previous factorial/filtered bounds multiplied by `j!` | Exact written consequence; inherited Lean threshold-free formula is weaker |

## External arithmetic input

The sole external arithmetic input to the new factorial route is Frobenius's exact congruence for ordinary even-index Euler numbers in the `sech(t)` convention. The primary source checked in the preserved audit is Ira M. Gessel, *Applications of the classical umbral calculus*, arXiv:math/0108121v3 (22 November 2001), Section 9: printed page 26 gives the all-starting-index exact statement; printed pages 29–30 derive it after Theorem 9.2.

This input is used for addresses zero and one, including their exact factorial parity. The address-two divided-power lemma, stronger filtration, power-order sharpness, and exact radius are proved internally by Bernoulli central factorials. Address three transfers from address two. The elementary bound `2B_m in Z_2` is proved from the Stirling formula, so no von Staudt–Clausen input is needed for these transfers.

The historical full Paper IX contains other named dependencies; this sentence describes only the new strengthening route.

## Source revisions and audit evidence

The integrated chapter translates and combines the following preserved sources from the threshold-free checkpoint, leaving those originals unchanged:

- `combinatorial/THRESHOLD_FREE_EIGENFLAT_PROOF.md`: integral reciprocal transfer and the all-dyadic family.
- `GENERAL_PRIME_POWER_TRANSFER.md`: signed prime-power and mixed-step extension.
- `measure/factorial_route.md`: full four-address divided-power route, parity, filtration, exact power orders, and radii. Frozen 599-line proof SHA-256: `67e112cc0d9bceb49446ffa856f15679c1a46de3cc0a584f5cbd7284f4689b82`.
- `sharp_periods/SHARP_PERIOD_LEMMA.md` and `sharp_periods/PUBLIC_THEOREMS.md`: exact first differences, least periods, isometric images, all-rank lower-half family, and small-rank extension.
- `sharp_periods/low_mahler_verified.json` and `sharp_periods/all_rank_extensions_verified.json`: complete exact rational finite certificates supplying the low-coefficient obligations.
- `review/GLOBAL_PROOF_AUDIT.md`, `PRIME_POWER_AUDIT.md`, `SHARP_PERIOD_AUDIT.md`, `FACTORIAL_ROUTE_AUDIT.md`, and `FACTORIAL_ROUTE_CRITICAL_AUDIT.md`: source-specific mathematical audits with frozen proof hashes.

The final edition has a separate mathematical-delta audit of the translated source, with its own source hash and bounded exact sanity checks. Parallel AI review is described as an audit, not independent external peer review.

## Boundaries and refutations

1. At odd primes raw ordinary step-one divisibility is false: `C_{N,0}(1)-C_{N,0}(0)=-2`. The proved arbitrary-prime theorem is sign-twisted.
2. Ordinary mixed factorial baseline equality is false without the parity condition: `Delta_1 Delta_2 C_0(0)=-33728` has valuation six, baseline four.
3. Address-two exact power orders do not decide every other order. No numerical all-order pattern is promoted to a theorem.
4. The naive all-rank upper-half exact metric law fails at `(N,j)=(16,9),(32,18),(32,19)` with exact rational certificates. These failures concern a stronger proposal, not the universal lower bound or completed external conjecture.
5. The address-three radius is bounded below, not determined exactly.
6. The separate Euler-tail universal simplicity/nonvanishing problem and native Paper IX conjectures beyond the completed external Conjecture 3.9 are not closed by these congruence results.
7. Taylor-boundary divergence is about the constructed ordinary expansion and does not exclude another analytic continuation.
