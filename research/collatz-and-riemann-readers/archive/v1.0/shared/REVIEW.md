# Mathematical review of the Collatz and Riemann conjecture pieces

Review date: 2026-10-08. Workflow: Mathbox proof audit in a separate reviewer agent. This is a mathematical manuscript review, not a new formal certificate.

**Final status:** Both complete manuscript bodies have been substantively reviewed. The critical self-contained proofs passed after the corrections and typing clarifications recorded below. The conjectures remain explicitly open.

**Normalized claims and primary verdict:** The conjecture conclusions are **conditional on a named input** in each manuscript. Collatz requires universal actual descent below the original positive odd source. RH requires the all-scale signed bound on the classical Báez–Duarte coefficient, equivalently the declared subexponential zero-packet energy bound. Neither input is proved in these pieces. The exact reductions and barriers listed below passed within their stated domains.

## Scope and provenance

The reviewer reconstructed the critical implications from the definitions, checked exceptional cases, and examined the author drafts. The review took place in a separate agent, but the archived RH barrier issues were supplied as known concerns, so that part was not blind. The repaired proof was independently reconstructed. Agent agreement is not an external mathematical certification.

The author sources were not edited by the reviewer. Corrections were communicated to the writers. Historical Lean reports were read as reports, not replayed builds. No complete historical Collatz or RH archive was recompiled. The archived residue coverage figure was not freshly re-enumerated by this reviewer.

External leaves were checked through the parallel literature workflow recorded in `LITERATURE_CHECK.md`. In particular, the exact Báez–Duarte criterion and Möbius coefficient identity were checked in the primary journal text. The heat-packet explicit formula and unconditional zero count were checked in Bondarenko–Radchenko–Seip. Unavailable Terras and Everett originals are disclosed there; those limitations concern historical background, not a missing premise in the self-contained packet proofs.

## Dependency graph

### Collatz

1. Exact odd acceleration and the offset recurrence imply the affine packet identity (`thm:affine`).
2. The terminal congruence plus odd invertibility at every prefix imply the exact valuation cylinder (`thm:cylinder`).
3. The affine identity gives concatenation and the precise descent budget (`prop:composition`, `thm:descent`).
4. Universal actual descent, together with strong induction, implies convergence to 1 (`thm:induction`). Conversely convergence implies actual descent for every odd source greater than 1.
5. Exact finite iteration verifies the table and first actual descent from 27. This is evidence for one source only.
6. An exact unit-valuation run gives the fixed-horizon obstruction (`lem:run`, `thm:horizon`) and the actual run exit (`thm:exit`).
7. An elementary divisibility induction produces distinct terminating seeds with arbitrarily late exact first descent (`lem:seeddiv`, `thm:seeds`). The exit equation and a separate slope condition lift a certified exit to an infinite arithmetic progression (`thm:lift`).
8. Under permanent coefficient noncrossing, the normalized offset gives a linear height bound in a hypothetical bounded-deficit strip (`lem:height`). The positive affine cycle equation gives injectivity (`lem:injective`). Exact cylinder counts then contradict the number of distinct orbit states under that common height (`thm:boundeddeficit`).
9. Coprimality of the affine slope numerator and denominator gives the same-word smaller-source merger obstruction (`prop:merger`). The alternative-word formula does not supply the open existence of a realizing smaller source.

### Riemann

1. Classical strip bounds and zero counting give Gaussian normal convergence.
2. Normal convergence gives a meromorphic Laplace series whose residues at centered zeros are nonzero. A holomorphic Laplace transform excludes every positive-real-part centered zero. Functional-equation symmetry supplies the other half (`rh:bounded`, `rh:front`).
3. Subexponential unit-band energy gives exponentially weighted integrability in complex `L²([t0,T])`. Its Hilbert-valued Laplace transform has the same nonzero pole obstruction (`rh:energy`).
4. The checked Gaussian explicit formula gives the pole, archimedean and prime-packet terms with the stated constants (`rh:explicit`). The pole annihilator preserves every actual zero mode (`rh:tilde`).
5. The coherent Hermite expansion and Poisson tail give stable compression under the declared shell assumptions (`rh:coherent`, `rh:poisson`, `rh:rate`). Gaussian pairing retains the shifted zero field (`rh:ground`).
6. Squarefree factorization gives the exact prime-cube decomposition (`rh:cube`). Bernoulli's inequality gives the positive tail (`rh:positive`). Squarefree-coprime inclusion and exclusion supplies the actual nonzero Möbius support (`rh:count`). Together they lower-bound the full triangle majorant (`rh:barrier`).
7. The signed cube sum is exactly the classical coefficient for every squarefree Q. The checked Báez–Duarte theorem therefore gives the conditional equivalence (`rh:conditional`).

## Obligation matrix

| Obligation | Status | Decisive check |
|---|---|---|
| Odd map and iteration clocks | Passed | Every accelerated step strips all powers of 2. The 27 example uses 37 odd steps and 59 shortcut steps. |
| Affine offset and order | Passed | `C_(j+1)=3 C_j+2^S_j`; the positive additive term is retained in descent. |
| Exact word realizability | Passed | Modulus is `2^(S+1)`, retaining the odd terminal quotient. Backward prefix congruences establish exact, not lower-bounded, valuations. |
| Actual versus coefficient descent | Passed | Actual descent is `(2^S−3^k)n>C`; coefficient contraction alone is not sufficient. |
| Universal Collatz conclusion | Conditional | Requires universal actual descent for every odd source greater than 1. |
| Unit runs and fixed-horizon obstruction | Passed | Explicit positive odd witnesses avoid every prescribed finite strict-descent horizon. Finite algorithms with input-dependent unbounded clocks remain possible. |
| Delayed terminating seeds | Passed | Divisibility of `2^(3^j)+1` by `3^(j+1)` follows by factoring `u³+1`; exact first-descent times imply distinct seeds. |
| Progression lifts | Passed | The lifted target stays odd and the separate slope inequality preserves strict descent for every integer parameter. Arbitrary exits are not claimed to terminate. |
| Modulo-4096 example | Passed | The first six valuations are exact; the last odd-part bound allows a larger final valuation and still proves uniform descent. |
| Permanent coefficient noncrossing | Passed | The hypothesis is `2^S_r/3^r≤1` at every time. Actual nondescending values alone do not imply it. |
| Bounded-deficit exclusion | Passed | No-cycle injectivity and the independently derived height bound combine with the exact rare-cylinder count. The rational decay factor is `65536/84375<1`. |
| Same-word merger obstruction | Passed | `2^S` divides the positive source difference. The different-word existence obligation remains open. |
| Heat convergence and symmetry | Passed | Gaussian decay dominates the unconditional zero count on positive heat strips. |
| Heat Laplace pole noncancellation | Passed | A repeated zero contributes its multiplicity times a nonzero exponential, not opposing residues at one pole. |
| Local energy criterion | Passed | Weighted Hilbert-valued integrability gives a holomorphic transform; each residue is a nonzero complex L² function. |
| Explicit-formula normalization | Passed | Prime prefactor is `1/(2√(πt))`; pole term is `2e^(t/4)cosh(u/2)`; gamma term has prefactor `1/(2π)`. |
| Hermite compression domain | Passed after clarification | `C>0` and fixed `q>α`; a declared active shell is required. Pole annihilation adds polynomial ladder factors, not an arithmetic saving. |
| Gaussian ground pairing | Passed | Exact completion of the square gives the heat shift. No global L² membership of an unconditional zero packet is asserted. |
| Cube decomposition | Passed | Absolute convergence and squarefree factorization justify regrouping. |
| Positive cube tail | Passed | Error at most `ζ(4)/R²`; `κ_R>0` is required for the barrier. |
| Squarefree coprime count | Passed | Main density is `(φ(Q)/Q)∏_(p∤Q)(1−p^−2)`; uniform error is `O_R(2^d√M)`. |
| Full majorant barrier | Passed | With `d=o(log M)`, the support count gives the stated `M^(−1−o(1))` lower bound on the exact absolute majorant. |
| Signed amplitude lower bound | Out of scope | The barrier gives no lower bound on the signed coefficient. |
| RH signed conclusion | Conditional | Requires the all-K signed estimate, equivalent to RH via the primary criterion. |
| Raw fourth moment | Passed after precision fix | The exact claim uses Cauchy–Schwarz on a probability space, avoiding positivity assumptions about arbitrary grouped collision coefficients. |
| Historical Lean receipts and residue count | Not replayed | Their historical labels remain explicit. |

## Corrections and resolved issues

1. The archived parity report compared the absolute value of the complete signed sum with an absolute mass on one interval. An interval mass is not an upper bound for the complete sum. The new manuscript instead defines the full triangle majorant and lower-bounds it by the tail interval.
2. The archived interval count included nonsquarefree bases whose Möbius coefficients vanish. The new manuscript retains `|μ(m)|` and proves a squarefree-coprime count before lower-bounding the exact majorant.
3. The Hermite rate uses `log(q/α)`. The writer explicitly declared `C>0`, hence `α>0`, and fixed `q>α`.
4. The Hilbert-valued energy proof now explicitly uses complex scalars. This clarifies the typing of meromorphic residues.
5. The fourth-moment discussion now gives its exact probability-space inequality. It does not assume all grouped off-diagonal collision terms are positive for arbitrary signed coefficients.
6. A Collatz prose sentence suggested that `C/G` and its floor are always different. They can coincide, as for the word `(2)` with fixed point 1. The final text explicitly states both the floor relationship and the integer-equality case.
7. The final Collatz text makes the integer domains of the progression parameters, the deficit and tail parameters, and the rare-word block parameter explicit.

These repairs do not prove either open conjecture. They make the stated reductions and method barriers accurate within their scope. Archived sources remain historical evidence and should not be read as overriding the corrected manuscript.

## Fresh exact arithmetic

Reproduce the reviewer checks with:

```bash
python shared/review_checks.py
```

Results are in `shared/review_check_results.json`.

The fresh run passed 1,705 exact cylinder/affine/descent cases, covering word lengths 0 through 4, exponents 1 through 4, and five positive progression representatives for each word. It passed nine rational rare-word density bounds and 5,151 explicit fixed-horizon prefix cases for horizons 0 through 100. It also independently verified every displayed first-ten row from 27, its first actual descent at odd time 37, endpoint 23, total valuation 59, and exact offset `1100931843921811423`.

An initial ad hoc reviewer check incorrectly guessed that the last valuation at the 37th odd step was 4. The actual exact valuation is 3. That assertion failed because the reviewer expectation was wrong. The manuscript did not state the guessed value. The expectation was corrected, and all displayed manuscript data passed. This resolved check failure is preserved in the result JSON.

These are bounded arithmetic checks, not a proof of universal descent, a full residue-cover audit, an RH test, or a Lean replay.

## Exact remaining gaps and strongest supported statements

For Collatz, the required global theorem is actual descent below the original source for every positive odd source greater than 1. Finite arithmetic progression certificates and arbitrarily delayed growing prefixes can coexist. Neither a finite partial cover nor a bounded computation fills the universal quantifier.

For RH, the required arithmetic theorem is a signed estimate on the actual Möbius coefficient for all scales, or equivalently the declared subexponential heat energy bound. The prime cube barrier rules out its exact sign-discarding majorant at subpolynomial cube dimension. It does not lower-bound the signed sum or exclude a signed-correlation proof.

The strongest supported universal manuscript statements include the exact conditional equivalences, the fixed-horizon obstruction, the noncrossing bounded-deficit exclusion, and the repaired absolute cube barrier. None supplies the missing actual Collatz descent or signed RH estimate.

The cheapest next validation is to replay the supplied exact scripts. Fresh Lean claims would require the pinned toolchains and complete module dependencies, followed by compilation and axiom audits; no such claims are made here. A mathematical continuation must attack the named unproved arithmetic inputs, rather than reclassify bounded computations or historical source counts as those inputs.

## Reviewed revisions

The final reviewed content is pinned by SHA-256:

| Artifact | SHA-256 |
|---|---|
| `collatz/body.tex` | `806c17105e31d31aab3ea6c761ce9554d3caa8bab04efc2cb5850b5bde0f0c29` |
| `riemann/body.tex` | `07b46287f328d5833e26962167b0df5b3221cde86e910b17c35a55122dfeb219` |

Layout wrappers, PDFs, bibliography metadata, and later editorial edits are outside these mathematical content hashes. No novelty claim, unrestricted historical archive audit, or new Lean certification is inferred from this review.
