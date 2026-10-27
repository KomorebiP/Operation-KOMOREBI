# Independent mathematical audit: diagonal range obstruction

**Normalized claim.** Let `H=lp (fun _ : ℕ => ℝ) 2`, `(Tu)_j=u_j/(j+1)`, `e_j=lp.single 2 j 1`, and `w_j=1/(j+1)`. Then `‖e_j‖=1`, `‖T e_j‖=1/(j+1)→0`, and `ker T={0}`. The actual range `Set.range T` is not closed in the Hilbert topology. Moreover, the genuine images of finite unit prefixes converge in norm to `w`, while `w` is not in the range.

**Primary verdict: proved as written.** This covers the full mathematical paragraph in `publication/source/chapters/05_geometry.tex`, lines 159–163, including the closure/nonattainment example.

This review independently reconstructed the objects from the raw sources and read the imported closed-range criterion. Author attempt logs and verdict reports were not used. No production source was edited. The relevant proof-audit checklist sections were general logic/typing, topology, computation-dependent claims, and source/dependency checks. No `.mathbox` ledger was present in the review workspace or publication root.

## Frozen source and printed scope

The target is `publication/lean/KomorebiSpace/DiagonalRangeObstruction.lean`, SHA-256 `2566dcb3d8bf26f47ded297a84b818b4c7e683516f56cbd3782b77e7a6869db1`. Its two terminal results are `KomorebiSpace.DiagonalRegularization.T_not_closed_range` and `KomorebiSpace.DiagonalRegularization.w_mem_closure_not_range`.

Formal coordinate `j=0,1,2,...` is exactly printed coordinate `n=j+1=1,2,3,...`. The printed operator `D` is the same concrete diagonal operator as formal `T`. The unit vectors are elements of the actual infinite Hilbert space, not tuples in a finite replacement. The prefix vectors used to establish closure membership also live in that same space.

The initial printed source still said these arguments were written examples. During this audit, root updated that editorial status sentence to cite the new declarations. The updated line 165 was reread and matches the actual formal claims. Both the original and current reviewed text hashes are preserved in the JSON. The mathematical paragraph itself is unchanged. No separate protected product-space formalization is claimed by this audit.

## Dependency graph

1. `DiagonalDefinitions` fixes `index j=j+1` and `wCoord j=(index j)⁻¹`.
2. `DiagonalSeriesBounds.summable_wCoord_sq` proves that `w` is a genuine square-summable vector.
3. `InfiniteDiagonalModel` defines `H`, bounded `T`, `w`, and the real finite sum `hardPrefix N`; it proves `T_injective`, genuine coordinate summability, and the exact infinite tail identity for prefix error.
4. `DiagonalRangeObstruction` constructs actual single-coordinate unit vectors, computes their exact images, proves the reciprocal limit and kernel complement membership, and gives a counter-witness to every nonnegative finite gain.
5. `HilbertKernelProjection.not_closed_range_of_unit_witnesses` turns those witnesses into nonclosedness. Its source derives the finite gain from a bounded inverse on the kernel complement under the assumed closed range; the gain is not an extra supplied hypothesis.
6. Independently, the prefix error's infinite tail tends to zero, giving `w` in the closure of the actual range. Any actual preimage of `w` would have every coordinate one, contradicting its required coordinate-square summability.

All mathematical leaves used here are internal proofs or formal-library theorems. There is no external citation requirement, numerical finite-range test, unstated density hypothesis, or circular dependency in this route.

## Decisive independent checks

For each `j`, coordinate evaluation gives `T e_j=(j+1)⁻¹ e_j`. The `lp` single-vector norm is one, and `j+1>0`, so the stated image norm follows exactly. Injectivity follows because no diagonal weight is zero. Consequently the whole space is the orthogonal complement of the kernel. For any real `C≥0`, choose a natural `j>C`; then

`C · ‖T e_j‖ = C/(j+1) < 1 = ‖e_j‖.`

If the actual range were closed, the reviewed abstract theorem would supply a finite nonnegative gain on precisely this kernel complement. The displayed strict inequality contradicts that gain. Both source and target are the complete real Hilbert space `H`, so the abstract theorem's completeness assumptions are satisfied. Since the kernel is zero, the distance from `e_j` to the kernel is also one, as in the printed paragraph.

For the closure witness, the raw `hardPrefix N` is the finite sum of the first `N` actual unit vectors. An independently compiled identity verifies

`T(hardPrefix N)(j) = if j < N then 1/(j+1) else 0.`

Its squared error to `w` is exactly the genuine infinite tail `∑' j, (wCoord(j+N))²`. This tends to zero; the square-root step gives Hilbert norm convergence. Every approximant is literally an image of `T`, so the limiting `w` lies in `closure (Set.range T)`.

Finally, `T x=w` forces `(j+1)⁻¹ x_j=(j+1)⁻¹`, hence `x_j=1` for every natural `j`. An element `x:H` has summable squared coordinates, which would make the constant-one series summable on infinite `ℕ`. `summable_const_iff` rules this out. The nonattainment assertion concerns an arbitrary possible preimage, not only a selected family of candidate solutions.

A potentially misleading formal-library detail was checked directly: `tendsto_sum_nat_add` requires no summability premise because divergent `tsum`s default to zero. This does not create a loophole here. `summable_wCoord_sq` is proved, and the norm-tail identity itself is obtained using genuine summability of the actual Hilbert residual coordinates. Thus the displayed tail is a convergent sum and its use is mathematically faithful.

## Obligation matrix

| ID | Status | Obligation | Finding and evidence |
|---|---|---|---|
| R01 | passed | Actual domain and operator | H is real lp over all natural coordinates at exponent two; T is the bounded coordinate multiplier 1/(j+1), not a finite matrix. `InfiniteDiagonalModel.lean:20,46-72` |
| R02 | passed | Unit-coordinate witnesses | unitCoordinate j is lp.single 2 j 1, with norm exactly one for every j including zero. `DiagonalRangeObstruction.lean:18-21` |
| R03 | passed | Exact image and norm | T(unitCoordinate j)=wCoord j • unitCoordinate j and its norm is exactly 1/((j:ℝ)+1). Positivity removes the absolute value. `DiagonalRangeObstruction.lean:24-36` |
| R04 | passed | Limit assertion | The sequence of actual image norms tends to zero along all natural j, using the reciprocal shifted-natural limit. `DiagonalRangeObstruction.lean:39-42` |
| R05 | passed | Kernel and required complement | Existing T_injective proves T.ker=bottom. Thus every unit coordinate vector lies in T.ker orthogonal, the exact domain required by the abstract obstruction. `InfiniteDiagonalModel.lean:102-109; DiagonalRangeObstruction.lean:45-51` |
| R06 | passed | All finite gains fail | For every real C>=0 choose natural j>C; then C/(j+1)<1. No bounded range, sampling, or subsequence restriction replaces this quantifier. `DiagonalRangeObstruction.lean:54-59` |
| R07 | passed | Closed-range criterion direction and completeness | HilbertKernelProjection.not_closed_range_of_unit_witnesses assumes Hilbert complete source and Banach target, both supplied by H. Closed range would supply a finite nonnegative gain on the actual kernel complement, contradicting the unit witness. `HilbertKernelProjection.lean:90-118,233-242; DiagonalRangeObstruction.lean:62-66` |
| R08 | passed | Range topology and exactness | The conclusion is not IsClosed(Set.range T) in the actual Hilbert topology. Kernel zero also makes distance to the kernel equal to the unit norm, matching the printed residual-to-distance failure. `DiagonalRangeObstruction.lean:45-66` |
| R09 | passed | Finite truncations remain in H and the true range | hardPrefix N is a finite sum of the same lp unit vectors, and T(hardPrefix N)(j) is if j<N then wCoord j else 0. The latter coordinate identity was independently Lean-checked in the isolated probe. `InfiniteDiagonalModel.lean:260-294; reviews/RangeAuditProbe.lean` |
| R10 | passed | Genuine Hilbert convergence | norm_hardPrefix_residual_sq identifies the error square with the actual infinite reciprocal-square tail. Its tail tends to zero; continuity of sqrt and nonnegative norms yield norm convergence to w. `DiagonalRangeObstruction.lean:69-76; InfiniteDiagonalModel.lean:282-301` |
| R11 | passed | Tail semantics not hiding divergent sums | Mathlib tendsto_sum_nat_add is unconditional because nonsummable tails default to zero, but this application is genuine: summable_wCoord_sq was proved and the norm-tail equality uses summable_coordinates_sq. `DiagonalSeriesBounds.lean:74-75; InfiniteDiagonalModel.lean:250-252,284-301; Mathlib/Topology/Algebra/InfiniteSum/NatInt.lean:242-255` |
| R12 | passed | Closure membership | Every approximant is literally T(hardPrefix N) and thus belongs to Set.range T; the norm limit puts w in its closure. `DiagonalRangeObstruction.lean:79-81` |
| R13 | passed | Actual nonattainment | For arbitrary x:H with T x=w, coordinate comparison and nonzero weights force x j=1 for every j. Since squares of coordinates of x are summable, this would make the constant-one series summable on infinite ℕ, contradicting summable_const_iff. `DiagonalRangeObstruction.lean:84-95; InfiniteDiagonalModel.lean:250-252; Mathlib/Topology/Algebra/InfiniteSum/Group.lean:392-402` |
| R14 | passed | Boundary coordinates and empty prefix | j=0 is printed n=1, giving norm(T e)=1; the denominator never vanishes. N=0 gives the empty finite prefix, and no initial term is omitted from the all-N convergence statement. `DiagonalDefinitions.lean:9; DiagonalRangeObstruction.lean:18-42,69-76` |
| R15 | passed | Source-to-print correspondence | The complete mathematical paragraph in 05_geometry lines 159-163 is covered, including w in closure but outside range. The updated line 165 accurately names the two concrete declarations and coordinate translation. `05_geometry.tex:158-165` |
| R16 | passed | Exact-source compile and axiom inspection | A verbatim frozen-source probe with all twelve theorem checks and axiom prints compiles warning-clean. All theorem reports use only propext, Classical.choice, Quot.sound. `reviews/RangeAuditProbe.lean; reviews/range_math_audit_probe.log` |
| R17 | out of scope | Separate protected product-space interpretation | No separate protected product-space formalization or general realization claim is implied or audited. `Audit scope` |

## Formal source check

The isolated `reviews/RangeAuditProbe.lean` contains the exact frozen source verbatim, an additional proof of the prefix-image coordinate identity, declaration checks for all twelve theorems, and axiom inspection of those theorems plus the imported abstract criterion. Command:

```sh
/workspace/scratch/5d9f7f8127b0/komorebi_diagonal_formalization/scripts/lean_env.sh lake env lean -j1 -DwarningAsError=true -DautoImplicit=false /workspace/scratch/5d9f7f8127b0/publication_v115/reviews/RangeAuditProbe.lean
```

It ran from the publication's new Lean directory and exited **0**, with `warningAsError=true`, `autoImplicit=false`, and one worker. All printed theorem axiom sets are `[propext, Classical.choice, Quot.sound]`; no `sorryAx` or custom axiom appears. The theorem types are unconditional concrete declarations apart from the expected explicit index or finite-gain inputs. The source of the imported abstract criterion was also read, including its direction from closed range to a finite complementary-space gain.

This is fresh elaboration of the target source against the existing dependency oleans, together with inspection of the relevant raw dependency sources; it is not a claim of a fresh whole-project build. The probe and its complete output are `reviews/RangeAuditProbe.lean` and `reviews/range_math_audit_probe.log`.

## Remaining gap and safe conclusion

**Exact remaining gap: none for the frozen source and printed mathematical paragraph.** The strongest safe statement is the concrete infinite diagonal unit-witness obstruction and actual closure/nonattainment pair above. The updated publication status paragraph is accurate. No mathematical repair or additional theorem is needed for this authorized connection. Separate protected product-space interpretations remain outside this audit's scope.

## Input hashes

| Input | SHA-256 |
|---|---|
| `publication/lean/KomorebiSpace/DiagonalRangeObstruction.lean` | `2566dcb3d8bf26f47ded297a84b818b4c7e683516f56cbd3782b77e7a6869db1` |
| `publication/lean/KomorebiSpace/HilbertKernelProjection.lean` | `5a30a4de9c18ed34169cea586150d3445f37a4be1f3737ae3243c5341f5cd2a1` |
| `publication/lean/KomorebiSpace/InfiniteDiagonalModel.lean` | `da72d7f6ccaa870581c23409837955e54db8be2a732354716e908fe9266501d2` |
| `publication/lean/KomorebiSpace/DiagonalDefinitions.lean` | `751bf02816f74e2fe8a8bc9f45c22f9538d087d1af536af3835e4906f4015f54` |
| `publication/lean/KomorebiSpace/DiagonalSeriesBounds.lean` | `fc606b9db34f39179ba3cedcc43504325bd14dfdba6de8c46ad7bd6a70a31cb2` |
| `publication/source/chapters/05_geometry.tex` | `04eb9896d549e39afb98119473d57d7edcfe105c10761bb6a2ba4db9597a80a1` |
| `publication/lean/lean-toolchain` | `8190e75a201741065fe508b28955dd64dd72d090babe5f70ce6848879d68ae88` |
| `publication/lean/lake-manifest.json` | `7e28e00cb45e028f411ea69972d18a9964f4c3affaf0212389afa9d1fe13df47` |
| `publication/lean/.lake/packages/mathlib/Mathlib/Topology/Algebra/InfiniteSum/NatInt.lean` | `bb9cfc34434d5c37f0085ca0d64a01bfc4afed88bab0fe1961dc496f7a30e5c1` |
| `publication/lean/.lake/packages/mathlib/Mathlib/Topology/Algebra/InfiniteSum/Group.lean` | `f076038e732fb9432224fbac1f8ad6435cbc175b9211090a5e3b32081c96694f` |

Initial printed source hash before root updated the status sentence: `0ba4db5639a705111006d7e86524f3a207943c8fdd7af8c0bea40b90bd701334`.

Parent immutable publication SHA-256: `73e9c5caa36f4ba05029c01481b345ce24cf9b1905dfb012ed21dd4bcfe86dc0`.
