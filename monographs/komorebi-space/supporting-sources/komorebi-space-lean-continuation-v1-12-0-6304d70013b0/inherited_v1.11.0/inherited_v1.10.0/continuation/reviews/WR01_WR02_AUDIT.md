# Independent audit of WR01 and WR02

**Normalized claim.** A bounded approximate preimage sequence for a fixed continuous linear map between real Hilbert spaces has an exact preimage within the same closed norm budget (WR01). Minimum-norm points in a nested sequence of nonempty closed affine subsets of one real Hilbert space have an exact Pythagorean difference identity, and converge strongly to the minimum-norm point of their intersection exactly when their norms are bounded (WR02).

**Primary verdict: proved as written.** No mathematical gap was found in these two printed proofs or in their local weak-subsequence, projection, and adjoint dependencies. This is an independent prose proof audit, not a Lean compilation or a claim of new formal coverage.

Audit date: 12 October 2026. The reviewer read the raw theorem statements and proofs and reconstructed the critical implications. The review was performed by a separate subagent from the continuation author. Independence of review does not substitute for kernel checking.

## Source identity and scope

The supplied base archive identifier is `Komorebi_Space_Complete_v1.7.0.zip`, SHA-256 `914bb768686bc186d4baefd53c1e13690346b0f506560ede916d1fb87d7e6794`. This audit independently hashed the extracted source files below, but did not independently hash the archive itself.

| Artifact, relative to the inherited package | SHA-256 |
|---|---|
| `source/Komorebi_Space_Monograph.tex` | `fe9e9aff531d456f1070445608a72467dcf6fd63d408dd77191a6d8dd2d04d19` |
| `source/chapters/05f_bounded_realization.tex` | `ba8225a03190d4040260eeced4b4c9372d05b85266b27ce53f8cc7ff9ca56acf` |
| `source/chapters/12_proof_tools.tex` | `f98d41969e3048a63a3ed7e19a0e7181ffb309a835ff6cb303a9ced6c5f748bd` |

The monograph loads the bounded-realization chapter at line 65 and the analytic appendix at line 78. Authoritative claim locators in the chapter are `WR01` at lines 59–83, `WR02` at lines 98–140, and `lem:weak-subsequence` at lines 25–57. The appendix dependencies are `lem:projection-tool` and `lem:riesz-tool`, including the adjoint construction immediately following the latter. The inherited source tree was not modified.

No applicable `AGENTS.md` or `.mathbox/` ledger was found in the searched workspace/package. The current `PROGRESS_LEDGER.md`, written-extension status appendix, and historical v1.5/v1.6 review notes were read for scope, but their assertions were not substituted for the raw proofs.

## Exact claim cards

### WR01

- Quantifiers: arbitrary real Hilbert spaces H and Y, a fixed bounded real linear map T : H → Y, and a fixed r ∈ Y.
- Equivalence: r lies in the actual algebraic range of T if and only if there is a sequence a : ℕ → H and a finite real M such that ‖aₙ‖ ≤ M for all n and ‖Taₙ − r‖ → 0.
- Budget conclusion: for every such sequence and bound M, there exists a ∈ H with Ta = r and ‖a‖ ≤ M.
- M need not separately be assumed nonnegative: the existence of a term and ‖aₙ‖ ≤ M already implies M ≥ 0. A Lean statement may make the nonnegative budget assumption explicit without restricting the meaningful instances.
- The domain is complete. The residual converges in norm. The candidate subsequence converges weakly. The operator is fixed along the sequence.
- Neither closed range, separability of H, injectivity, finite dimension, nor strong convergence of the original candidates is assumed or concluded.
- In the protected application H = ker p carries the inherited metric. The continuous map p has a closed kernel, so H is complete, and T is the continuous restriction of d to H. The conclusion then preserves p(f − a) = p(f) literally.

### WR02

- Quantifiers: one real Hilbert space H and a sequence Aₙ of nonempty closed affine subsets, with Aₘ ⊆ Aₙ whenever n ≤ m.
- Each aₙ is the unique minimizer of x ↦ ‖x‖ on Aₙ. These points are constructed by the projection theorem, not assumed without existence evidence.
- mₙ = ‖aₙ‖ is nonnegative and nondecreasing. For n ≤ m, ‖aₘ − aₙ‖² = mₘ² − mₙ².
- The intersection is nonempty if and only if the set of numbers {mₙ} is bounded above. The printed notation `supₙ mₙ < ∞` denotes this ordinary extended-real boundedness condition. In Lean, use `BddAbove (Set.range ...)` or an explicit real bound rather than comparing a real `sSup` with an infinity that does not inhabit ℝ.
- Under that bound there is a unique least-norm a* in the intersection, aₙ → a* in norm, and ‖a* − aₙ‖² = ‖a*‖² − ‖aₙ‖².
- If the intersection is empty, mₙ tends to positive infinity. This is stronger than being unbounded and follows from monotonicity.
- No dimension or uniform operator inverse bound is assumed. All constraints and norms belong to the same ambient Hilbert space.

## Dependency graph

| Node | Inputs | Role and disposition |
|---|---|---|
| Closed convex projection | Parallelogram identity, real infimum approximation, completeness, closedness, convexity | Internally proved in `lem:projection-tool`; checked. |
| Orthogonal projection onto a closed subspace | Closed convex projection and linear-subspace structure | Internal construction immediately after that lemma; checked. |
| Riesz representation and adjoint | Closed kernel, orthogonal projection, Cauchy–Schwarz | Internally proved in `lem:riesz-tool` and the following paragraphs; checked. |
| Weakly convergent subsequence | Countable span, Gram–Schmidt, scalar bounded-subsequence selection, Bessel inequality, completeness, subspace projection | Internally argued in `lem:weak-subsequence`; checked, including nonseparable ambient spaces. |
| WR01 exact preimage | Weak subsequence with preserved budget, adjoint identity, independent strong convergence of the images, separation by inner products | Checked directly. |
| WR01 escape consequence | WR01 applied to any bounded subsequence; negation of divergence to infinity | Checked directly. |
| Affine minimum orthogonality | Projection existence and two-sided feasible line variation | Checked directly. |
| WR02 finite energy identity | Affine orthogonality and nesting | Checked directly. |
| WR02 strong limit | Monotone bounded real energies, energy identity, completeness | Checked directly. |
| WR02 intersection and minimality | Tail membership, closedness, norm continuity, convex uniqueness | Checked directly. |
| WR02 divergence | Equivalence plus monotonicity of nonnegative minimum norms | Checked directly. |

The ordinary elementary leaves are Cauchy–Schwarz, parallelogram expansion, bounded scalar subsequence selection, convergence of bounded monotone real sequences, and continuity of finite sums and the norm. Bessel's finite inequality follows by expanding the nonnegative squared norm of the orthogonal remainder. No unverified named external theorem supplies the decisive WR01 or WR02 implication. The bibliography is contextual here because the needed analytic dependencies have internal arguments. No new external-source or novelty claim is made.

There is no circular dependency: projection follows from a Cauchy minimizing sequence, before Riesz and the weak-subsequence argument use it. WR02 can be proved from projection and the energy identity without using WR01 at all.

## Obligation matrix

| Obligation | Status | Decisive reason |
|---|---|---|
| Objects and scalar conventions type correctly | Passed | Real Hilbert spaces throughout, with a fixed bounded real linear T. |
| Protected candidates remain admissible | Passed | Corrections lie in the closed kernel before solving or optimizing. |
| No hidden ambient separability assumption | Passed | All candidate terms lie in their separable closed span; ambient test vectors are projected into it. |
| Diagonal subsequence gives every fixed coordinate limit | Passed | Subsequences are nested and original indices increase. |
| Coordinate limits reconstruct an actual Hilbert vector | Passed | Bessel bounds every finite energy sum, making the orthogonal partial sums Cauchy. |
| Coordinate convergence upgrades to weak convergence | Passed | Approximate each test vector first; the uniform 2M bound controls the remaining error. |
| Norm budget survives passage to the limit | Passed | Test weak convergence against a/‖a‖ when a ≠ 0; treat a = 0 separately. |
| Weak and strong image convergence are not conflated | Passed | Strong convergence of Taₙ is a separate hypothesis used to identify the weak image. |
| WR01 equivalence includes the easy direction | Passed | An exact preimage supplies a constant sequence. |
| WR01 escape means divergence, not only unboundedness | Passed | Failure to diverge supplies infinitely many terms in one ball. |
| Minimum-norm points in Aₙ exist uniquely | Passed | Nonempty, closed, affine implies nonempty, closed, convex. |
| Affine direction and signs are correct | Passed | Both positive and negative line variations are feasible. |
| Exact finite energy identity | Passed | aₘ − aₙ is a direction of Aₙ and is orthogonal to aₙ. |
| Bounded energies produce a full Cauchy sequence | Passed | For either order of two indices, symmetry reduces to m ≥ n and the monotone energy tail estimate applies. |
| Strong limit lies in every constraint set | Passed | For each fixed n, the entire tail lies in closed Aₙ. |
| Least-norm characterization and uniqueness | Passed | Pass finite minimality to the norm limit; use convex projection uniqueness. |
| Limiting energy identity | Passed | For fixed n, pass m → ∞ through continuous squared norms. |
| Empty intersection implies norm divergence | Passed | Contrapositive gives unboundedness, monotonicity upgrades it to divergence. |
| New Lean counterparts and axiom audit | Not addressed | This audit is limited to prose proof validity and formalization decomposition. |
| Numeric suite coverage as universal proof | Out of scope | No computational test is used to prove these infinite statements. |

## Reconstructed critical steps and boundary cases

For WR01, obtain a weak subsequential limit a with the retained norm bound. For every y ∈ Y,

    ⟨Ta − r, y⟩ = limₖ ⟨Taₙₖ − r, y⟩ = 0.

The first equality uses the adjoint identity, and the second uses the assumed norm convergence of the residual. Setting y = Ta − r forces its norm squared to vanish. The construction does not assume compactness in the strong topology.

For WR02, write c = ⟨aₙ, ℓ⟩ and q = ‖ℓ‖² for a feasible affine direction ℓ. Minimality gives 0 ≤ 2tc + t²q for every real t. If q = 0, then ℓ = 0 and c = 0. If q > 0 and c ≠ 0, choosing t = −c/q gives −c²/q < 0, a contradiction. Thus the printed two-sided variation step is valid without a differentiability assumption. Apply this to ℓ = aₘ − aₙ, which is feasible by nesting. The Pythagorean identity yields the energy formula. Bounded monotone energies then give the Cauchy estimate and completeness supplies the actual common-space limit.

- Zero space, zero map, and zero budget are covered: in WR01 the image condition forces r = 0 when T = 0, and M = 0 forces the candidate sequence and resulting preimage to be zero.
- The empty orthonormal basis case is the zero closed span and causes no failure of the finite-dimensional branch of the weak-subsequence argument.
- Singleton affine sets and eventually constant nested systems satisfy the WR02 identity, including the n = m case.
- Arbitrary bounded accurate candidates need not converge strongly: for T(eₙ) = eₙ/n on ℓ², aₙ = eₙ gives residual norm 1/n, candidate norm 1, and pairwise distance √2. This validates the manuscript's warning.
- Affineness is essential for the equality. For closed convex sets A₁ = [1,∞) and A₂ = [2,∞) in ℝ, minimizers are 1 and 2. The squared difference is 1 but the difference of squared norms is 3. A convex-set formalization cannot silently claim the affine energy equality.
- Completeness cannot be discarded. In c₀₀ with its ℓ² norm, fixing the first n coordinates to 1/j produces nonempty closed affine nested sets with minimum squared norms ∑_{j≤n}1/j² ≤ 2 but an empty intersection in c₀₀. The same inclusion c₀₀ → ℓ² with truncated (1/j) gives bounded approximate feasibility without a preimage in c₀₀.
- Nesting cannot be discarded: the sequence of singleton sets alternating between {0} and {1} has bounded minimum norms and empty intersection.

## Lean-friendly proof decomposition

These are logical interfaces, not assertions about existing mathlib declaration names.

### WR01 implementation blocks

1. Use complete real inner-product spaces H and Y and a continuous linear map `T : H →L[ℝ] Y`.
2. Isolate a closed-ball preservation statement: from a weakly convergent sequence whose every norm is ≤ M, derive the same bound for its limit. Keep this helper independent of the range theorem.
3. Obtain a weakly convergent subsequence of a bounded sequence by the available Hilbert/reflexive-space machinery, or formalize the printed separable-span proof. Do not assume compactness of a norm ball in the norm topology.
4. Prove the image identification helper: weak convergence `a ∘ φ → a*` plus norm convergence `T ∘ a → r` implies `T a* = r`, using the adjoint pairing or weak continuity and uniqueness of weak limits. Strict monotonicity of φ supplies convergence along the subsequence.
5. Package the budgeted existence theorem before the existential bounded-sequence equivalence. This retains the quantitative norm conclusion.
6. Derive the escape corollary separately, constructing a bounded subsequence from failure of `Tendsto (fun n => ‖a n‖) atTop atTop`.
7. Add the protected-kernel corollary with the actual restricted map, making kernel completeness and ambient norm preservation explicit.

### WR02 implementation blocks

1. Represent the family as closed affine subspaces with explicit nonemptiness and an antitone nesting condition. The natural-number index may begin at 0 without changing the theorem.
2. Construct each minimum-norm point by nearest-point projection of zero. Expose membership and comparison with every feasible point.
3. Prove minimum-point orthogonality against the affine direction, then `‖a m − a n‖² = ‖a m‖² − ‖a n‖²` for n ≤ m.
4. Deduce monotonicity of the squared norms and of the norms, using nonnegativity. Establish boundedness equivalence for these two scalar families.
5. From a bound, take the finite real limit L of the squared norms. Prove `CauchySeq a` from the epsilon-squared energy tail estimate, explicitly handling arbitrary order of the two indices by symmetry.
6. Obtain a norm limit using completeness and prove membership in each Aₙ by closedness and eventual membership. Form the intersection only after this witness is established.
7. Pass the finite minimum property to the limit, prove uniqueness, and pass the finite Pythagorean equality to the limit for each fixed n.
8. Derive the nonempty-intersection equivalence and the empty-intersection divergence theorem as separate named results. The printed group is not fully covered until these final conclusions and the limiting identity are included.

The cheapest correctness check during formalization is to compile the exact public theorem types after each block, rather than count helper declarations. In particular, the final WR01 theorem must retain the same budget M, and the final WR02 theorem must quantify over arbitrary nested nonempty closed affine constraints in one complete space. Finite-dimensional substitutes would be strictly weaker.

## Source and computation checks

The review used direct `rg` searches for `WR01`, `WR02`, the input chapter, and the proof-tool labels; `cat`, `sed`, and numbered source reads for the current chapter and appendix; and Python `hashlib.sha256` for the three source identities above. Historical reviews were searched for these claim identifiers and no failed mathematical predecessor was found in those records.

An initial search of the monograph entrypoint alone found no theorem bodies because they are included from chapter files. This was resolved by reading the actual included chapter. A search for a not-yet-created continuation directory returned a missing-directory error; it was only an inventory query and supplied no proof evidence. No mathematical or compiler failure occurred during this audit. No numerical experiment, fresh Lean run, axiom audit, or external-source verification was performed.

## Remaining gap and strongest safe statement

There is no identified gap in the written WR01 or WR02 argument under its declared hypotheses. The outstanding work is formalization and accepted compilation/audit of the resulting declarations, plus exact statement-to-source matching. The prose-audit verdict does not promote either theorem group's inherited written-only status.

The strongest safe continuation claim is: **WR01 and WR02 have complete written Hilbert-space proofs that passed this independent logical review; their unrestricted Hilbert-space formal counterparts must still be demonstrated by the continuation's own compiler evidence.**
