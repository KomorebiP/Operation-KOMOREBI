# Block 9 mathematical audit

Komorebi P. · Lean 0.9.0 · 12 October 2026

## Primary verdict

**Proved as written, with the surrounding positive-delay convention made explicit.** This verdict covers the formal statement mappings P14, P15, P16, P17, and P25 against frozen Foundations 1.0.0. It is an author self-review supported by Lean checking, not an independent referee report. The acceptance outcome is recorded separately in the verifier JSON.

The normalized target is the finite autonomous observable-learning sector. It uses actual linear observation maps, actual sampled-column maps, and exact finite-dimensional real Hilbert operators for the perturbation result. No unknown representation, measurement access, global span coverage, or contraction margin is inferred merely from a fitted matrix.

## Dependency graph

- P14: observation kernels → adjacent kernel recurrence → quotient factorization and uniqueness → rank-nullity equivalence → finite-dimensional stabilization → causal output at every horizon.
- P15: kernel compatibility → quotient map on the sampled range → ambient extension and uniqueness on that range. Orthogonal projections → constructed pseudoinverse → four Penrose conditions → the specified fit formula. Extension at an unsampled vector → nonidentification witness.
- P16: variational smallest row singular value → adjoint perturbation lower bound → surjectivity → constructed pseudoinverse norm bound → exact residual identity → operator norm estimate.
- P17: explicit rational shift → exact power formula → nilpotence and delayed scalar response → universal finite-prefix indistinguishability.
- P25: covering data and true successors → data-only learned map equals the true transition → all iterates and realizations. P16's fitted map → actual local defect → P18 product-sum envelope → contraction radius and output decoding.

All new mathematical leaves are internal Lean proofs or declarations from the pinned Mathlib environment. No new theorem is imported merely through a prose citation. The local Mathlib sources for quotient factorization, linear extension, rank-nullity, orthogonal projection, and adjoints were inspected. Their upstream compiled dependencies are trusted at the same boundary as the predecessor package.

## Obligation matrix

| Obligation | Result | Evidence |
|---|---|---|
| Actual observation map and its kernel | Passed | `observation`, `mem_observation_kernel` |
| Range-valued transition and uniqueness | Passed | `transition`, `transition_exists_iff`, `transition_unique` |
| Rank criterion and dimension-bound closure | Passed | `delay_closure_rank_iff`, `dimension_closure` |
| Positive delay and causal warm-up index | Passed | explicit h>0, `causal_future_output` |
| Kernel consistency, sampled span, ambient extension | Passed | `fit_iff_kernel`, `fits_agree_on_range`, `fitted_range` |
| Unsampled direction remains undetermined | Passed | `unseen_direction_not_identified` |
| Actual orthogonal pseudoinverse | Passed | `pinv`, `penrose_one` through `penrose_four` |
| Singular-value normalization and norm convention | Passed | `rowGain_variational_unit`, real Hilbert operator norms |
| Strict perturbation margin derives rank and inverse bound | Passed | `surjective_of_adjoint_lower`, `pinvL_bound` |
| Full residual identity and divided estimate | Passed | `noisy_identification_identity`, `noisy_identification_bound` |
| Every finite horizon, including zero | Passed | `finite_prefix_indistinguishability` |
| Data-only fit, full coverage, and all-time exact prediction | Passed | `learned_eq_true`, `learned_all_horizons`, `delay_table_identifies` |
| Atlas and complete packet preservation | Passed | `learned_atlas_iterates`, `learned_packet_output`, inherited coherent transport |
| Actual recursive noisy rollout and output bound | Passed | `fitted_rollout`, `contracting_rollout`, `decoded_rollout_bound` |
| Executable floating-point solver or production-code equivalence | Out of scope | no such claim |
| Unknown dictionary or unrestricted hidden-state discovery | Out of scope | no such claim |
| Independent external referee or second prover | Not addressed | this is self-review plus Lean checks |

The row singular value is formalized by its variational definition. Equality with a particular SVD implementation or with Mathlib's separately indexed approximation numbers is not claimed or required by these statements. The quotient construction for exact real operators is noncomputable. P45's rational certificate search is still outstanding and cannot be replaced by this construction.

## Decisive boundary evidence

The new exact examples retain a positive-delay boundary, a closed sampled plane on which two distinct operators agree, inconsistent zero inputs, and a delayed response beyond any chosen finite horizon. The scalar perturbation example reaches the denominator bound at input perturbation −1/2 with unit unperturbed input. At perturbation magnitude exactly one the unit input collapses to zero. These support six deliberately invalid proof attempts in `negative_controls/`.

The nilpotent counterexample is parameterized by T and proves the power formula. It is not a bounded search. The scalar sharpness example is exact real arithmetic. It does not claim to verify a numerical SVD routine.

## Development and repairs

Every recorded development compiler invocation has its source snapshot, stdout, stderr, return code and elapsed time under `verification/development_block9/`. Early failures included:

- selecting extensionality that expanded linear maps into basis coordinates instead of arbitrary vectors;
- quotient-range coercions and simplification of linear-map kernels;
- proof terms with unnecessary or unused finite-dimensional assumptions;
- a deprecated continuous-linear-map application lemma and an incorrect adjoint-norm lemma name;
- trying a scalar linear-combination tactic on a vector identity, repaired by the actual vector equality and additive algebra;
- a documentation-comment placement error before an `omit` directive;
- an early compile of a dependent module before its dependency had compiled.

No missing-import failure is classified as a successful negative control. No warning policy, axiom policy, or source exclusion was relaxed. The zero-window issue was caught while developing the delay equivalence and led to an explicit positive-delay hypothesis, already required by the original proof register.

The first documentation-generation script failed with an unterminated Python string in an unnecessary backslash replacement. It wrote no new documentation before failing. Removing the invalid replacement allowed the generator to run. This was a documentation tooling failure, not a mathematical proof failure.

The plain Lean executable initially reported the kit's known application-location error. The supplied path adapter resolved it. The existing local runtime was reused read-only, with the compiler commit and all nine dependency revisions checked by the cumulative verifier. A new runtime extraction is not claimed.

## Verification and remaining gap

The source-candidate result is `verification/block9_release_run/report.json`. Metadata checks are in `verification/block9_metadata.json`. The delivered archive is additionally checked from a fresh extraction, with no copied project object files. Its external delivery report identifies the exact ZIP hash and the actual replay outcome.

The cumulative target is 74 project modules, one root import, 1,256 explicit axiom records, 74 project kernel replays and 68 genuine negative-control rejections. The compiler policy treats warnings as errors. All permitted axioms remain `propext`, `Classical.choice`, and `Quot.sound`.

The formalization now maps 35 of 87 numbered statements, leaving 52. The next restart is P45, exact rational certificate search. The frozen theory, all 67 predecessor proof files, all 1,178 predecessor declaration records, and all 62 predecessor controls retain their identities.

## Mathematical proofreading

Self-review covered the new guide, this audit, the coverage descriptions and publication clarification. Routine changes clarified real Hilbert norms, positive delay, causal indexing and the distinction between a symbolic operator and executable arithmetic. No mathematical tokens in the frozen manuscript were edited. Its stale publication sentences remain flagged in `PUBLICATION_STATUS.md`. No PDF rendering or visual revision is claimed.

Accepted source-candidate result: PASS, 218 stages, no subprocess timeouts. Metadata: PASS, 72 checks. Development: 20 successful and 16 failed compiler invocations, all retained.
