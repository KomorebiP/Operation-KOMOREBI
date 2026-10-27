# Paper VII Lean-guide proofreading and verification review

Date: 18 October 2026. Review-only handoff. No release files or Lean sources were modified.

## Outcome

The current Lean-guide prose has been read in full. Six precise corrections are recommended below. The source-to-evidence and catalog checks pass. The preserved 6 September 2026 release records compilation of 25 modules and 323 named theorem declarations covering 19 scoped finite items. The fresh checks in this review reconcile those records with the supplied sources; they do not repeat kernel compilation.

## Recommended corrections

### P7-LG-01: meaning

File: `editable/lean_guide/chapters/channels_recovery.tex`, baseline line 128.

Replace: `a code-independent nonnegative scale $t$`

With: `a nonnegative scale $t$ that is independent of the code-supported operator`

ErrorFamilyCorrectable fixes P and E before existentially choosing t, then universally quantifies rho. The scale may depend on the code. The original Lean doc comment repeats code-independent but the actual predicate is correctly state/operator-independent.

Source evidence: `formalization/ErrorSpanRecovery.lean:168-172; 188-210` (relative to the preserved snapshot).

### P7-LG-02: meaning

File: `editable/lean_guide/chapters/seed_packets.tex`, baseline line 23.

Replace: `For $k$ seeds $C_a$, the allowed generation is`

With: `Continue with a nonempty row index type. For $k$ seeds $C_a$, the allowed generation is`

The full-rank iff, lower bound, and existence iff in this subsection require [Nonempty d], matching the positive-row condition in the preceding subsection. Restating it makes the displayed excerpts and the lower-bound claim unambiguous.

Source evidence: `formalization/SeedOrbit.lean:148-155; 173-175` (relative to the preserved snapshot).

### P7-LG-03: meaning

File: `editable/lean_guide/chapters/finite_limits.tex`, baseline line 45.

Replace: `using a sine-square lower bound`

With: `using the quadratic upper bound for sine squared`

The source uses Real.sin_sq_le_sq to establish nonnegativity of the error, then the cubic sine error for the upper error bound. The guide named the sine-square inequality in the wrong direction.

Source evidence: `formalization/LowModeConvergence.lean:15-28` (relative to the preserved snapshot).

### P7-LG-04: terminology

File: `editable/lean_guide/chapters/reading.tex`, baseline line 12.

Replace: `the type of integers smaller than the natural number`

With: `the type of natural numbers smaller than`

Fin n consists of natural numbers below n, not all integers below n. The exact domain is uniquely determined by Fin n.

### P7-LG-05: grammar

File: `editable/lean_guide/chapters/channels_recovery.tex`, baseline line 52.

Replace: `The finite Knill--Laflamme data consists of`

With: `The finite Knill--Laflamme data consist of`

Subject-verb agreement, consistent with the subsection heading treating data as plural.

### P7-LG-06: navigation

File: `editable/lean_guide/chapters/seed_packets.tex`, baseline line 120.

Replace: `Together the two chapters implement`

With: `Together the two constructions implement`

The cyclic-projector and tensor constructions are two subsections in one teaching chapter, not two chapters.

## Additional traditional-supplement check requested by root

`editable/traditional/parts/03_supplement_03.tex`, line 17, should explicitly continue the positive-row hypothesis stated at line 14. The proposed sentence “Continue under the positive-row hypothesis above.” agrees with the active Lean theorems: `generates_iff_rank` at SeedOrbit.lean:148, `seed_count_lower` at :152 and `exists_generating_seeds_iff` at :173 all require `[Nonempty d]`. If d is empty while m is nonempty, the coefficient space is zero and generation is vacuous although stacked rank is not m. The clarification prevents that unintended broad reading.

## Fresh checks executed

| Check | Result | What it establishes |
|---|---|---|
| Documented `static_check.py --source PATH` on a temporary guide copy | PASS, exit 0 | Source hashes, saved compiler logs, 323 declaration names and axiom sets, transitive local import hashes, 19 ledger entries, nine dependency pins, two saved invalid controls and six constructed-object bindings agree. |
| Exact raw Lean excerpts | PASS, 67 of 67 | Each selection is the exact contiguous source block and matches its inherited raw excerpt. |
| Baseline mathematical-span preservation | PASS, 322 spans | All six teaching chapters retain their delimited mathematics and contract/proof-walk paragraphs before root edits. |
| Independent generated-catalog reconciliation | PASS, 323 names and source lines | Printed catalog names and locations match current declarations. |
| Documented `scripts/test_verifier.py` | PASS, 16 tests, exit 0 | The Python audit parser and source/interface tamper controls work on their finite test cases. |

Logs: `static_check.log`, `verifier_regression.log`, `RUNS.json`, `catalog_reconciliation.json`. The copied script outputs are under `guide_static_copy/generated/`.

## Kernel replay status and exact limitations

Lean, Lake and Elan were absent from PATH. Conventional Lean locations checked were also absent. The bundle deliberately omits the separate portable compiler kit, Mathlib cache and generated interfaces. Its documented replay command requires `--kit /path/to/kit`, with `run.sh`, `toolchain/bin/lean`, and the pinned `workspace` tree. There is no current lakefile in the source snapshot. No compiler process was invoked, no dependency was installed, and no fresh theorem or deliberate compiler-control pass is claimed.

The inherited runtime is Lean 4.34.0-rc2, compiler commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`, with Mathlib `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The saved run began on 6 September 2026 at 15:30:24 UTC and completed its cumulative record at 15:32:49.641452 UTC. All 25 saved compiler exits are zero. All 323 saved theorem axiom sets are contained in `propext`, `Classical.choice`, and `Quot.sound`; `KomorebiPaperVII.Curvature.jet_sandwich_zero` is the single axiom-free recorded theorem. Active source scan finds no admitted proof or added axiom declaration.

Six proof-bearing constructions have a separate inherited audit: `RangeBundle.fiber`, `RangeBundle.project`, `RangeBundle.localProduct`, `RangeBundle.fiberEquiv`, `GlobalConnection.covariant`, and `BundleCompletion.fiberCurvature`. These are additional object audits, not six additional theorem declarations.

## Active module coverage

Only the following 25 current files count toward the 323-declaration inventory. Historical assembly, development snapshots and earlier supplements do not add to that count.

| Active module | Named theorem declarations |
|---|---:|
| CanonicalConnection | 9 |
| ComputationalSeed | 14 |
| ConstraintAudit | 7 |
| CyclicProjectors | 18 |
| ErrorSpanRecovery | 9 |
| EuclideanTransfer | 12 |
| GlobalProjectedConnection | 10 |
| GlobalRangeBundle | 22 |
| KnillLaflammeExamples | 8 |
| KnillLaflammeNecessity | 7 |
| KnillLaflammeSufficiency | 22 |
| KrausChannels | 7 |
| LeakageBound | 17 |
| LocalProjectedCurvature | 6 |
| LowModeConvergence | 2 |
| ManifoldProjectedCurvature | 17 |
| MovingFrames | 9 |
| ProjectedBundleCompletion | 12 |
| ProjectedCurvature | 20 |
| QuantumPacketCore | 19 |
| QuantumStateBridge | 9 |
| SchurFeshbach | 4 |
| SeedOrbit | 34 |
| SyndromeRecovery | 18 |
| TensorRefinement | 11 |
| **Total** | **323** |

Full declaration names, source lines and source/log SHA-256 identities are in `module_inventory.json`.

## All 19 scoped items

| Ledger item | Subject | Status interpretation |
|---|---|---|
| 2.1 | Orbit dimension of one quantum seed | Inherited LEAN_CHECKED under its recorded assumptions |
| 2.2 | Quantum seed-rank formula | Inherited LEAN_CHECKED under its recorded assumptions |
| 2.3 | Local orbit and Schmidt rank | Inherited LEAN_CHECKED under its recorded assumptions |
| 2.4 | One seed for the computational basis | Inherited LEAN_CHECKED under its recorded assumptions |
| 3.1 | Cyclic quantum projectors | Inherited LEAN_CHECKED under its recorded assumptions |
| 3.2 | Tensor/polyphase refinement | Inherited LEAN_CHECKED under its recorded assumptions |
| 4.1 | Exact circuit path expansion | Inherited LEAN_CHECKED under its recorded assumptions |
| 4.2 | Packetwise unitarity conservation | Inherited LEAN_CHECKED under its recorded assumptions |
| 5.1 | Exact symmetry packets | Inherited LEAN_CHECKED under its recorded assumptions |
| 5.2 | Commutator leakage bound | Inherited LEAN_CHECKED under its recorded assumptions |
| 6.1 | Moving-frame Hamiltonian | Inherited LEAN_CHECKED under its recorded assumptions |
| 6.3 | Canonical packet connection | Inherited LEAN_CHECKED under its recorded assumptions |
| 6.4 | Projected connection | Inherited LEAN_CHECKED under its recorded assumptions |
| 7.1 | Block-diagonal measurement invariance | Inherited LEAN_CHECKED under its recorded assumptions |
| 7.2 | Finite Kraus channel | Inherited LEAN_CHECKED under its recorded assumptions |
| 8.1 | Finite Knill-Laflamme criterion | Inherited LEAN_CHECKED under its recorded assumptions |
| 9.1 | Exact Feshbach resolvent | Inherited LEAN_CHECKED under its recorded assumptions |
| 10.1 | Finite Euclidean transfer | Inherited LEAN_CHECKED under its recorded assumptions |
| 11.1 | Low-mode second-order bound | Inherited LEAN_CHECKED under its recorded assumptions |

The exact preserved scope text accompanies this report in `scoped_result_ledger.json`. The source explicitly includes the full finite complex-matrix Knill–Laflamme criterion, actual spectral recovery construction, its necessity proof, the density-operator bridge, every finite reference dimension and the fixed recovery for normalized channels in an error span. It also includes the global real boundaryless manifold projected-connection construction, atlas, gluing and curvature within the recorded complete-space hypotheses. The range atlas is explicit and is not registered as a Mathlib `ContMDiffVectorBundle` instance. The Feshbach theorem retains both eliminated-block and full-resolvent invertibility assumptions.

The five original physical continuum targets remain open: anomaly-free refinement, uniform Feshbach control, Lorentzian reconstruction, an Einstein infrared limit and a massless spin-two sector. The 323 count includes supporting lemmas, seven constraint-audit declarations and four Schur–Feshbach declarations. It is not a count of 323 separately stated manuscript theorems.

## Coverage and preservation notes

Full current guide coverage comprises the main front matter, preamble, README, reading, seed_packets, dynamics, geometry, channels_recovery, finite_limits and replay chapters, plus generated catalog, finite-result map and dependency register. Raw excerpts were checked for exact fidelity. The full file list with baseline hashes is in `review_coverage.json`. This was conservative guide proofreading and static scope reconciliation, not a new adversarial audit of all 323 Lean proofs. PDF layout and page locator refresh remain with the root build workflow.

No mathematical display or Lean token was edited by this reviewer. Proposed corrections clarify prose scope and terminology. One inaccurate comment in preserved `ErrorSpanRecovery.lean:168` remains a historical source-comment erratum (“code-independent” instead of independence from the supported operator). The actual formal predicate is correct. Recording that distinction in the new proofreading report preserves source hashes and the inherited evidence chain.
