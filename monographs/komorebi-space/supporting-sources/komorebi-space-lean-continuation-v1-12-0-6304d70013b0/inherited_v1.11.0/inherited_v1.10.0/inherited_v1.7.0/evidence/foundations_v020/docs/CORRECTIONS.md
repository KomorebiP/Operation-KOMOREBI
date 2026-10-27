# Current update — v0.7.0

v0.7 distinction: a section of coarsening C is not a section of the tower differential d. Lossless detail retention does not imply either compression or infinite-depth convergence. See `LOSSLESS_RESIDUAL_EXTENSION.md`.

---

# Corrections made during consolidation

## 1. A vanishing compatibility residual need not preserve information

Zero maps commute with every bonding square in a preadditive category. Therefore an unrestricted residual distance based only on those defects has a zero-cost arrow between every pair of towers. The distance may collapse completely.

**Repair:** protect a specified additive semantic map p and restrict corrections to ker p. Keep optional transport cost distinct from compatibility residual.

**Checked diagnostics:** `Tower.PreHom.exact_zero`, `TransportCost.collapse_of_zero_arrows`.

## 2. A globally defined coboundary is not a nonzero cohomology class

If Ω = δτ globally, then [Ω] = 0 by definition. Earlier language treated such an Ω as potentially intrinsically nonzero without stating restricted corrections or local data.

**Repair:** separate ordinary cohomology from the constrained quotient R/d(ker p). Prove both formulations with their actual hypotheses.

**Checked diagnostics:** `ObstructionComplex.primary_defect_class_zero`, `CorrectionProblem.unrestricted_correction`.

## 3. Exact maps on a fixed schedule are not all pro-morphisms

General pro-morphisms allow source refinement depending on the target level and eventual-equality identifications. The fixed-level construction does not automatically provide that localization.

**Repair:** call the checked object the category of exact levelwise tower transports. Pro-category comparison remains a target.

## 4. The composition defect has a precise law

For actual preadditive tower maps, the defect of a composite is the sum of two appropriately composed defects. No additional unspecified mixed term is needed. Unweighted norm subadditivity requires contractivity; otherwise amplification factors remain.

**Checked:** `Tower.PreHom.defect_comp`, `NormedDefects.horizontal_norm`.

## 5. Operator-valued Stokes requires transport factors

Square defects can inhabit different Hom spaces. They cannot be added until transported into a common Hom space. The correct finite formula is a telescoping sum of terms A_k Ω_k B_k.

**Checked:** `NormedDefects.transported_telescope`, `transported_stokes_bound`.

## 6. Cofinality preserves exact inverse-limit information, not arbitrary residual samples

The sequence with even terms 0 and odd terms 1 has a cofinal all-zero sample but does not tend to zero. Therefore arbitrary obstruction norms or profiles cannot be declared cofinal invariants.

**Repair:** prove inverse-limit equivalence and, separately, vanishing invariance for nonnegative nonincreasing profiles.

**Checked:** `Resolution.cofinalEquiv`, `Profiles.cofinal_vanish_iff`, `Profiles.alternating_does_not_vanish`.

## 7. Distance zero is not exact solvability without closedness

Distance to a boundary subgroup is zero precisely on its closure. Closedness is needed to infer actual membership.

**Checked:** `ObstructionFloor.zero_iff_closure`, `zero_iff_mem_of_closed`.

## 8. Cancellation is not convergence

Residuals may decrease while candidates move without a limit. The exactification proofs explicitly require complete ambient space, lower semicontinuity of the residual, and summable movement bounds. The linear version separately preserves the chosen semantic map.

**Checked:** `Exactification.variable_exactification`, `LinearExactification.geometric_semantic_exactification`.

## 9. Exactness does not imply uniqueness

Multiple points may have zero residual and even the same protected semantics. Path independence requires additional comparison data tending to zero. Equality of limits is proved in a metric space, not asserted for arbitrary pseudometric points.

**Checked:** `PathIndependence.limits_equal_of_budget`.

## 10. Two differential sign conventions were mixed

For anticommuting d and e, use D = d + e. For commuting bicomplex directions, insert the appropriate degree sign. The earlier outline assumed anticommutation and also inserted the sign associated with the other convention.

**Checked repair:** `Differential.anticommuting_sum_square_zero`.

## 11. Categorical vocabulary is not a construction

A pro-object, a fibration, a stack, a homotopy limit, and a metric completion are not synonyms. None is obtained merely by assigning those names to representation and resolution data.

**Repair:** separate the checked constructions and retain the advanced proposals as explicit targets.

## 12. Original v0.1.0 operational failures and their resolution

No compiler was initially present on PATH. The attempted online installation could not retrieve the required binaries in this environment. The five previously available offline runtime parts were materialized from the user's Library and restored into a working Lean 4.34.0-rc2 runtime with pinned mathlib.

An initial project-path/dependency initialization failed. A broad Mathlib import was impractical under the execution limits. Subsequent source development exposed and corrected elaboration, import, and linter errors. The final project uses narrow imports and a clean direct-compiler replay.

The first complete release audit passed every library compilation and theorem axiom check but failed its axiom-injection negative-control assertion. Lean printed the injected name in abbreviated form (`injected`) within its namespace, while the test expected the fully qualified name. The parser/check was corrected to detect the nonstandard injected axiom in either spelling. The failed receipt and log are retained inside the original archive under `provenance/Komorebi_Space_Lean_v0.1.0.zip`.

All final assertions of successful verification refer to the clean release verification, not to those failed attempts. Development-run records are retained and are not presented as complete immutable snapshots of every intermediate source version.

## 13. v0.2.0 canonicity boundary

A fixed correction scheme determines its limit, but preserving semantics alone need not determine a unique exact candidate. Scheme-independent canonicity is proved only when the protected semantic map separates exact candidates. The finite-coordinate counterexample is `RepairExamples.semantics_alone_not_unique`. The resulting projection need not be orthogonal or an optimal approximation.

## 14. v0.2.0 operational failures and resolution

The compiler was absent from the initial filesystem. Direct network retrieval failed at DNS resolution. Library title searches did not locate the ZIP parts; a size-sorted listing did. One Files pagination call reported that its apparent cursor was unavailable. The five existing compact parts were restored, their combined SHA-256 matched the expected value, and the actual toolchain version and mathlib revision were checked. A requested interactive container execution mode was unsupported, so ordinary processes were used.

Initial development builds failed on a dependency search-path layout, missing scoped notation, missing operator-norm imports, elaboration of pointwise linearity, eta-expansion in convergence statements, a reflexivity goal after rewriting, and warnings treated as errors. Each was repaired. The development logs are retained; they are not presented as successful verification or as mathematical counterexamples. An error message mentioning a compiler-inserted recovery placeholder in a failed build is not a placeholder in the final source.

The complete v0.2.0 clean compilation, all 156 theorem axiom checks, and all three negative controls passed. The v0.1.0 audit-parser failure described above was historical and did not recur in this continuation. The standalone archive replay is reported separately in its delivery receipt.


## v0.3.0 corrections and failure log

The runtime was initially absent. Saved offline archive parts were located through Library metadata after filename search returned no results. Their concatenated XZ archive hash matched the recorded bundle. A container streaming invocation failed; a direct local extraction subsequently succeeded. The compiler and cached dependencies were reused as trusted inputs.

Development proof drafts encountered type elaboration, unfolding, arithmetic-normalization, unused simp-argument and linter errors. Corrected sources were compiled with warnings treated as errors. Logs remain under `audit/development_v0.3.0/`.

The first clean whole-project build compiled all 25 proof modules but failed on the root import file: appended imports appeared after `set_option autoImplicit false`. This was a packaging/entry-point error, not a mathematical counterexample. The imports were moved to the header and the complete verification rerun. The failed build report remains in `audit/root_import_order_failure/`.

A genuine mathematical boundary was proved separately: for identity-bonding real towers, the bounded unit residual has no bounded primitive. Therefore an unrestricted right-inverse claim would be false. The split-tower theorem keeps its strict propagation-gap hypothesis.

The coordinate theorem is canonical only relative to the selected splitting and observable. It does not identify all choices of resolutions, all norms or all semantic doctrines. The source factor one half in the growing model is not silently removable.
