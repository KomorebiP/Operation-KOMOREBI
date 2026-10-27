# Paper VIII computation audit

Author: Komorebi P. Editorial verification date: 2026-10-06 UTC.

The archived finite suites reproduced in the available Python environment. These runs establish bounded code-path assertions and source/evidence consistency. They do not create universal mathematical proofs, recompile Lean, validate a CUDA implementation, or reproduce historical hardware timings.

## Fresh results

| Gate | Actual result | Evidence |
|---|---|---|
| Archived byte manifests | 928 complete-package entries, 723 formal-snapshot entries, and 131 strengthened-package entries match | `runs/integrity-corrected/` |
| Active Lean source / inherited evidence comparison | 40 modules, 392 named theorem declarations, 66 separately counted construction audits, and 458 axiom-audited names match their recorded source, dependency, inventory and log hashes | `runs/static/` |
| Verifier/metadata software suite | 43 unittest tests pass | `runs/unit/` |
| Original Python function tests | 23 baseline and 11 strengthened functions pass by direct invocation, including the real temporary-directory fixture | `runs/test-functions/` |
| Strengthened deterministic finite suite | 37,392 mixed exact, numerical and metadata checks pass in nine groups | `runs/original/` |
| Fourth-block structured mirror | 180 Kronecker, 120 tensor, 96 Walsh, 240 Toeplitz, and 600 clipped-allocation cases pass; 1,800 infeasible budgets are rejected; 96 Fourier cases pass | `runs/structured/` |
| Fifth-block graph/discovery mirror | 820 band cases, 200 DAG/triangular cases, 125 minimum-schedule enumerations, 60 inverse-support cases, 50 Schur cases, 72 exact noncoordinate discovery cases, 64 numerical complex discovery cases and 120 numerical Jacobi cases pass | `runs/fifth/` |
| Sixth-block complex recompression mirror | 182 factor pairs, 638 truncations, 3,190 sampled rank-bounded competitors, nine invalid inputs and two assumption-removal controls pass | `runs/sixth/` |
| Independent final visual-guide exact replay | 208 exact positive assertions and 15 invalid shortcut controls pass on the frozen final source | `runs/visual-guide/` |

Counts in different rows measure different, sometimes overlapping objects. They are not unique theorem or discovery counts. The archival raw trees contain 1,062 preserved files. The three manifest inventories overlap; their row counts should not be summed as unique source files. The initial integrity contract's descriptive entry counts were corrected, while its accurate actual checker output was retained in `runs/integrity/`. `DEVELOPMENT.json` records that metadata correction and the initial rejected randomness contract, which never executed a mathematical run.

The deterministic suite's group counts are: packet semantics 1,350; structured primitives 3,218; low-rank recompression 2,200; graph support 21,531; Schur fill 2,936; tree compilation 3,150; precision allocation 2,203; historical corpus consistency 778; source integrity 26. The 778 corpus and 26 source checks are metadata checks. The corpus checks authenticate neither the original hardware measurements nor the actual source-level execution contract.

All accepted runs use version 2 bounded provenance manifests. Each records the actual argv, UTC start, runtime, exit code, declared input hashes before and after execution, declared result hashes, logs and effective resource caps. The manifest validator accepted every record with the project root supplied. Input files remained unchanged. The eight archival gate caps were 240 wall-clock seconds, 210 CPU seconds per process, 2 GiB address space, one allowed CPU, and a cooperative one-thread numerical-library cap. The final exact guide replay used 30 wall-clock seconds and 20 CPU seconds with the same memory/CPU/thread caps. The thread request is not proof that every library honors it. Source packages are archival file trees without a project Git commit to report.

## Arithmetic, range and tolerances

The structured and graph mirrors use `fractions.Fraction` for their exact rational calculations; Fourier, complex discovery, whitening and recompression checks use NumPy binary64/complex128. The original deterministic suite's own comparisons are preserved: many `allclose`/`isclose` calls retain NumPy's default relative tolerance, while other checks supply explicit absolute and relative tolerances. Passing that suite should not be paraphrased as a uniform machine-epsilon certificate.

The sixth mirror uses seed 60606. It samples dimensions zero through ten, includes empty and zero factors, rectangular/rank-deficient factors, repeated singular values, and ranks zero, one, near full, full and above full. Column-space detection uses a threshold `1e-11 * max(1, largest singular value)`; output numerical rank uses `1e-9 * max(1, ||A||_F)`. Its normalized tolerance is `2e-9`. The largest observed normalized defects were:

| Comparison | Maximum |
|---|---:|
| Compact reconstruction | 1.2730256604370022e-15 |
| Spectral tail | 3.556141234775559e-15 |
| Frobenius tail | 3.660976558279377e-15 |
| Ambient SVD reference | 2.0463133061101735e-15 |
| Isometric lift norm | 1.017973960067893e-15 |
| Compression contraction | 6.729319939515922e-16 |

The fourth Fourier mirror tests lengths one through 24, four complex samples per length, seed 20260906, with absolute tolerance `1e-10`. Its maximum application discrepancy was 2.0388725187405107e-13. The fifth Jacobi tests include coupling parameters zero, 0.05, 0.2, 0.6 and 0.95. Their positive condition-bound discrepancy was 6.661338147750939e-15 and inverse-square-root normalization discrepancy 1.325732848414663e-14, both within the source's declared numerical tolerances. None of these bounded results supplies general SVD existence, exact numerical-rank decisions, a stable QR/SVD algorithm, or proof against every possible ambient competitor.

Seeds, finite bounds, coefficient domains, exclusions and actual software versions are in `contracts/`, `ENVIRONMENT.json` and the corresponding manifests/results. The mathematical reduction for best-rank optimality remains the separate manuscript/Lean argument based on exact ordered thin-SVD equations.

## Independent visual model review

The exact portable guide checker was reviewed directly against the printed model definitions and expected values. Its arithmetic in Q(i), conjugation, rational elimination, matrix multiplication, and column-major vectorization match those definitions. The review checked the six-dimensional block-diagonal-plus-rank-one application, Fourier factor of two, Toeplitz padding, complex Kronecker transpose, Walsh normalization, the quadratic BDLR product term, Woodbury denominator, compact range/core reconstruction, spectral/Frobenius residual Grams, two distinct product-error recurrences, signed-path cancellation, staged triangular solution, Schur cancellation, linked Krylov spaces, coherent block errors, continuous/clipped allocations, all 27 precision assignments, five tree prunings, local updates, streaming model, strict reuse threshold, complex core adjoints, inverse closure, shared-family costs and conservative ceilings.

The 15 negative controls falsify concrete displayed shortcuts: omitted Fourier scale, absent Toeplitz padding, adjoint in the vectorization transpose position, unnormalized Walsh norm preservation, omitted quadratic low-rank term, automatic invertibility of an update, unweighted final product errors, unconditional Krylov equality, maximum-block error as total norm, preservation at half-gap equality, an integral ceiling as the strict reuse threshold, omitted required output decoding, transpose as a complex isometry, reachability as exact inverse support, and floor error quantization. These controls are model failures, rather than merely an exception asserted for arbitrary malformed syntax. The decoding control uses synthetic declared times: two plus twelve exceeds the explicit-output baseline of twelve. It does not authenticate the historical benchmark contracts.

After review, the guide checker was strengthened to check the complex residual Gram and rank-one output directly, and to check that its diagonal rank-one competitor annihilates the displayed kernel frame. The frozen final guide passed all 208 exact positive assertions and 15 controls. Its bounded version 2 record pins the final checker and both page-source hashes under `editable/visual_guide/`; the manifest validator accepted the record against the final edition root. `VISUAL_EXACT_MODEL_REVIEW.json` records the independent mathematical review and final inputs. This fresh result is separate from the archived SymPy evidence.

## Inherited and unavailable gates

The inherited accepted Lean run completed on 2026-09-06 at 22:38:55.838919 UTC. Its source records Lean 4.34.0-rc2 (commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`) and Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The active source, inventory, axiom lists and logs match that evidence, and the two inherited false/admitted-proof controls have matching source/log hashes and recorded rejection exits. This is a fresh static consistency audit of inherited evidence, not fresh kernel checking. The pinned runtime, Mathlib cache and compiled local interfaces are absent here. The saved 56-item coverage ledger and four separately tracked classical inputs were not promoted to new formal conclusions.

The reused `QuantumPacketCore.lean` was also compared directly with the source in the preceding finalized Paper VII edition. The files are byte identical at SHA-256 `92e49bb023877ed1f1c2bb34968aa81ee7724fa3a8e1801a831cfc70f1de3595`. `REUSED_FOUNDATION_COMPARISON.json` records both input paths/hashes and the comparison boundary.

The original SymPy visual suite records 190 positive assertions and 11 rejected controls under Python 3.13.5 and SymPy 1.14.0. Its source/report bytes are preserved. SymPy is absent in the current environment; that suite was not rerun. The new standard-library checker is a separate exact implementation of the displayed finite examples.

Pytest is absent. The 34 archived function tests were actually executed by a small direct runner, rather than claiming a pytest session. The archived unittest suite ran through Python's real unittest runner. No Lean, Lake, GPU timing tool, device benchmark, CUDA implementation, or extracted Lean algorithm was executed. Eighteen historical chart pairs were generated in a temporary directory by the baseline chart test and checked as files; those charts replot stored rows and do not constitute benchmark replication.

## Representation boundaries and residual risks

The legacy numerical `PacketIR.support` property reports stored block keys, which can include a zero block. Its exact-zero composition path retains constructed zero blocks. The manuscript's exact mathematical support uses genuinely nonzero projector blocks. Stored structural support, exact nonzero support and thresholded numerical support must therefore be distinguished. The older QR-based `recompress_factors` uses reduced QR widths and does not certify actual-rank compact range dimensions. The sixth mirror separately constructs numerically detected column ranges; the formal construction uses exact column spaces. A passing numerical prototype is not a proof of equality with either formal representation.

The archived Lean executable compiler and budget examples remain inherited because they need the absent pinned Lean runtime. The historical benchmark corpus's schema/fairness checks establish internal record consistency; they do not independently authenticate same-device output and timing contracts. Numerical-library methods share SVD/QR implementations in several comparisons, so the sixth mirror's independent ambient comparison is an independent algebraic route, not an independently implemented numerical SVD library. Roundoff, thresholding and bounded random sampling remain explicit limitations. Actual universal conclusions require the mathematical proofs and their stated hypotheses.

## Reproduction

The reusable entry points are `checks/replay.py`, `checks/check_visual_guide.py`, `checks/run_experiment.py` and `checks/validate_manifest.py`. Use a fresh output directory, retain the declared `--input` list in the selected contract, and validate the generated manifest with the project root supplied. Recorded commands remain available in each manifest; do not treat their historical absolute working paths as paths on a different machine. No dependency installation or synthetic compiler interface is part of this verification.
