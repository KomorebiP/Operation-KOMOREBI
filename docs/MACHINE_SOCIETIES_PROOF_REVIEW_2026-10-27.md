# Machine Societies: three additional proof reviews

**27 October 2026 · Komorebi P. · AI-assisted self-review**

Three previously unlisted statement/proof pairs in the final 1.0.0 manuscript were reviewed at [commit ad2b5089b273](https://github.com/KomorebiP/Operation-KOMOREBI/commit/ad2b5089b2738bbe1c67345aaa634a45075995a2). Each has the primary verdict **proved as written** under its stated hypotheses. The [review record](../manifests/machine-societies-review-2026-10-27.json) pins the manuscript, exact statement/proof blocks, and prior review records.

The earlier review lists 15 claims. These three labels are disjoint from that list and refer to the same source hash, so the two records cover **18 distinct pairs out of 62**. **44 pairs remain outside these targeted reviews.** This is a coverage count, not a whole-book confidence percentage. The manuscript and earlier review are preserved unchanged.

<a id="deterministic-quotient-criterion--propdet"></a>

## Deterministic quotient criterion: `prop:det`

**Claim.** Given maps $F_u:X\to X$ and a surjection $\pi:X\to Z$, unique maps $\overline F_u:Z\to Z$ with $\pi F_u=\overline F_u\pi$ exist exactly when $\pi(x)=\pi(x')$ implies $\pi(F_u(x))=\pi(F_u(x'))$ for every $u,x,x'$. Source: [publication manuscript](../monographs/machine-societies/publication/Machine_Societies_v1.0.0.tex), line 297.

**Primary verdict: proved as written.** Necessity follows by applying the proposed map to an equal macrostate. For sufficiency the fibre condition makes the proposed value independent of the representative. Surjectivity supplies a representative for every target point and forces uniqueness. This is a well-defined function by uniqueness of the value, without requiring a globally chosen section.

**Dependencies:** map typing and surjectivity → each target fibre is inhabited → the stated condition makes its output value unique → the quotient map exists and intertwines → surjectivity forces uniqueness. All leaves are explicit hypotheses or the internal argument.

**Boundary checks:** singleton fibres, constant surjection, and the empty-to-empty surjection. Dropping surjectivity can leave arbitrary values outside the image. Dropping fibre constancy prevents the map from being well-defined. Neither hypothesis is silently removed.

**Remaining gap:** none for this implication. The theorem does not show that a proposed real-world macrostate satisfies the fibre condition. A next applied check would inspect that condition for the declared transition maps and allowed controls.

<a id="exact-reconstruction-after-erasure--properasure"></a>

## Exact reconstruction after erasure: `prop:erasure`

**Claim.** A finite state set has at least two elements, and $E(z)=(E_1(z),\ldots,E_n(z))$. Let $d_E$ be the minimum number of differing coordinates over distinct states. For integer $0\leq k\leq n$, all known erasure sets of size at most $k$ admit exact reconstruction exactly when $d_E>k$. Source: manuscript line 472 and its immediately preceding definition.

**Primary verdict: proved as written.** If $d_E>k$, every pair of states remains distinguishable outside each erased set, so the surviving tuple identifies a unique state. Conversely the finite minimum is attained. Erasing a minimizing pair's differing coordinates makes the observations identical and defeats any exact decoder.

**Dependencies:** finite nontrivial state set → an attained minimum distance → pairwise distinguishability after each permitted erasure ↔ injectivity of every surviving-coordinate map ↔ exact reconstruction on its image. Every leaf is a definition, finite-set fact, or the internal proof.

**Boundary checks:** $k=0$ tests injectivity of the full encoding. Duplicate codewords have $d_E=0$ and fail even then. At $k=n$ reconstruction is impossible for two or more states. If zero components are allowed, the empty encoding also has distance zero and fails. The boundary $d_E=k$ fails. Strict inequality is necessary. Known erasures are distinct from unknown-location corruptions.

**Remaining gap:** none for the stated coding criterion. It does not supply an authorized or timely operational repair procedure. A next implementation check would test the actual decoder on its declared erasure patterns.

<a id="repair-budget--proprepair"></a>

## Repair budget: `prop:repair`

**Claim.** Nonnegative errors satisfy $e_{t+1}\leq a_t e_t+b_t$ with nonnegative $a_t,b_t$. For every integer $T\geq0$,

$$
e_T\leq e_0\prod_{t=0}^{T-1}a_t+
\sum_{j=0}^{T-1}b_j\prod_{t=j+1}^{T-1}a_t.
$$

If $0\leq a_t\leq\bar a<1$ and $0\leq b_t\leq\bar b$, this implies $e_T\leq\bar a^T e_0+\bar b(1-\bar a^T)/(1-\bar a)$. Source: manuscript line 491 and the preceding recurrence.

**Primary verdict: proved as written.** The source's repeated-substitution argument is induction: multiply the previous bound by the nonnegative next coefficient and add the next disturbance. This extends each old product and adds the final empty-product term. Nonnegativity then permits replacement by the uniform bounds. The finite geometric sum gives the displayed estimate.

**Dependencies:** recurrence plus nonnegativity → monotonic substitution → finite product–sum expansion → uniform coefficient bounds → finite geometric identity. No convergence limit or external stability theorem is used.

**Boundary checks:** $T=0$ uses empty product one and empty sum zero. $T=1$ recovers the hypothesis. Zero coefficients and zero disturbances are allowed. The denominator is positive because $0\leq\bar a<1$. Negative multipliers would invalidate the inequality propagation and are excluded.

**Remaining gap:** none for the conditional recurrence bound. No claim follows that an actual monitor measures the intended error or that a deployed repair action satisfies the recurrence. Those are separate empirical obligations.

## Obligation matrix and provenance

| Obligation | Quotient | Erasure | Repair budget |
|---|---|---|---|
| Objects, quantifiers, and stated hypotheses | Passed | Passed | Passed |
| Written implication chain | Passed | Passed | Passed |
| Degenerate and equality cases | Passed | Passed | Passed |
| Hidden external theorem or load-bearing computation | None needed | None needed | None needed |
| Deployment assumptions and empirical effectiveness | Out of scope | Out of scope | Out of scope |

No numerical experiment, Lean replay, literature-priority claim, or independent peer review is part of this pass. The source identifies these elementary results as parts of a theoretical framework. This review makes no novelty claim. The strongest safe conclusion is precisely the three stated implications. The next bounded written-proof targets can be the finite-memory and compositional-closure propositions, with their definitions and admissible controls checked first.
