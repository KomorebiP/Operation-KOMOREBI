# Arithmetic component completion review

The finite arithmetic bridge is complete within its stated mathematical scope. This pass found no substantive defect in QA01–QA20. It independently rederived the finite Fourier normalization, rational character-order projectors, coefficient-residue and polyphase identities, exact twelve-dimensional filtering, normalized state transport, phase response, and dephased probability. The general identities are supplied as prose theorems. The archived formal development covers the stated q=12 specialization through 96 named declarations.

## Fresh executed evidence

| Check | Result | Evidence |
|---|---|---|
| Original exact Python verifier | 3,003 assertions pass | `visual_results.json` → `source_verifier` |
| Release shell and phase verifier | 5,374 assertions pass | `visual_results.json` |
| Independent exact semantic replay | 472 assertions pass | `exact_supplement.json` |
| Source and guide concordance | 36 checks pass, including 96 declarations and 19 verbatim excerpts | `static_concordance.json` |
| Floating diagnostics | Maximum residual 6.764165321960921e-15, tolerance 1e-12 | `visual_results.json` |
| Computation provenance | Valid v2 record, completed execution | `computation_manifest.json` |

The three assertion totals describe checks, including overlapping verification of the same mathematics. They are not counts of distinct theorems or discoveries. Exact computation used integers, rational fractions and exact cyclotomic or quadratic-field coordinates. Floating diagnostics are recorded separately.

The new independent script uses Q(sqrt(3), i) with Fraction coordinates. It checks every entry of both unitary identities and F D F*, then checks normalization, state preparation and recovery, phase-sensitive probabilities, the q=1 scalar boundary, four exact phase quadrants, and QA20's density-matrix probability 1/3. Two explicit mutations confirm rejection of an incorrect projector scale and an altered signal sign. The continuous phase formula remains supported by its written proof, rather than inferred from four samples.

## Source and mathematical coverage

The review read the complete underlying arithmetic treatment, all 25 visual-panel texts, and the formal guide. It also checked the combined volume's arithmetic introduction and Appendix A scope and trust statements. Exact source hashes and review boundaries are in `quantum-component-review.json`. General theorem proofs were reviewed directly, with q=1, zero character, trivial selectors, nonselected components, and zero-probability branches considered against their stated assumptions.

The 96-declaration source index matches the active module hashes and physical declaration lines. All 19 displayed Lean source excerpts match the actual source ranges byte for byte after outer whitespace normalization. That static check is not a compiler pass. Fresh Lean execution is owned by the separate runtime task and is not asserted in this report.

## Remaining completion actions

1. Incorporate the separate fresh Lean build, axiom audit, module replays and control results when they finish. The manuscript currently correctly reports archived evidence only. The current volume passages at extracted `inputs/volume.txt` lines about 15102, 15933 and 16118 must be updated only to match the actual new result.
2. Preserve the historical runtime-transfer failure and old proof receipts as history. The old `checks/verify_release.py` hard-codes fresh status NOT_RUN and archived file hashes. It is an historical consistency verifier, so a current aggregate release verifier must not interpret that hard-coded condition as the new status.
3. Preserve the distinction between the old false-Fourier-mode operational rejection and a mathematical refutation. The old control regex can match the filename, and the recorded failure involved opaque Decidable reduction. The runtime agent has been asked for a separate positive refutation derived from the checked DFT table.

No mathematical source repair was necessary in this bounded component review. General-modulus Lean theorems, a general measurement API, arbitrary-angle formalization, gate synthesis, hardware implementation, and quantum resource bounds are explicitly separate scope. They are not supplied by this pass and must not be represented as completed formal results.

## Execution and presentation notes

The first exact replay was rerun under explicit bounds to capture complete provenance: 2 GiB address space and 100 CPU seconds per process, 120-second wall timeout, and numerical-library thread counts fixed to one. The controlled run completed in the recorded time. The initial manifest validator rejected an empty declared-results metadata array. That field was corrected to record the output names already fixed in the subprocess arguments before execution. Validation then passed without changing mathematical outputs.

Matplotlib emitted one constrained-layout warning while recreating the scientific figures. The replay was isolated under `replay_project/`, so none of the publication's existing figure files changed. The regenerated images are computational replay outputs and have not been approved as replacement publication artwork.

External-source attributions were not reauthenticated in this pass. The reviewed general identities have self-contained arguments in the manuscript. This review makes no novelty verdict and no claim to cover the other three treatments in the volume.
