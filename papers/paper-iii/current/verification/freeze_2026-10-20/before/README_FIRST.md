# Paper III — final release 1.0.0

**Projector Resolved Seed Calculus III**  
Komorebi P. · 20 October 2026

This is the final technical manuscript release. It integrates the corrected mathematical paper, current visual and Lean guides, and a fresh verification of the released formal development. The mathematical manuscript is complete under its stated hypotheses. Its formal scope is identified explicitly: the whole monograph is not claimed to be formalized in Lean.

## Read the paper

Start with `publication/Paper_III_Complete_Reading_Edition_v1.0.0.pdf`. Its bookmarks link the release record, monograph, analytic supplement, visual guide, and Lean guide. The four standalone companions are also in `publication/`.

The main paper retains its 167 numbered environments: 98 theorem, proposition, lemma or corollary environments; two classical standard facts; and 67 definitions, examples and other numbered explanations. The statement register binds each environment and its available proof to the actual final chapter source. Manuscript counts are not compiler declaration counts.

## What changed from the release candidate

Section 17 now gives the closed-range argument, the bounded coordinate equivalence, literal continuous jets on the projector ranges, and the sharper restricted norm estimate. The Taylor remainder is derived with its exact factorial normalization. The partition induction, second-order output projector, intermediate labels and support profiles are explicit and correctly typed. The zero-space, empty-family, complex-scalar and zero-direction conventions are retained.

Four Section 17 modules joined the accepted Lean import root. Two previously uncompiled source candidates now compile. The new continuous interface uses actual submodule ranges with inherited norms and mathlib's `iteratedFDeriv`. The composition module proves the complete finite partition identity with every intermediate label, a sufficient vanishing criterion, and one-way structural support inclusion.

The guides now describe the current verification and preserve the finite baseline map with its historical counting units. Earlier readers and candidate records are archived, rather than presented as the current edition.

## Verified evidence

| Layer | Result | Exact record |
|---|---|---|
| Current Lean cold build | 16 production modules passed | `formal/verification/final_release_full/report.json` |
| Compiled ownership and axiom audit | 608 owned declarations, including 33 outside the primary namespace | `formal/verification/final_release_audit/report.json` |
| Kernel replay | 594 logical declarations accepted, starting with upstream imports only and zero owned overlap | `formal/verification/final_release_replay/report.json` |
| Runtime helpers | 14 generated helpers separately inventoried and excluded from logical dependencies | `formal/verification/FINAL_VERIFICATION_SUMMARY.json` |
| Controls | All 14 commands accepted with their designated success or rejection | `formal/verification/final_release_controls/report.json` |
| Exact Section 16 examples | 15,331 assertions passed | `evidence/section16_packet_replay.json` |
| Exact Section 17 examples | 2,622 assertions passed | `evidence/section17_replay.json` |
| Higher calculus examples | 677 assertions passed | `evidence/section17_higher_order_tests.json` |
| Visual models | 124 exact checks passed and four false controls rejected | `guides/visual/checks/EXACT_CHECKS.json` |

The three main exact suites total **18,630 assertions**. Their repetitions, finite ranges, sampled norm inequalities and adverse examples are documented in `evidence/review/computation_review.md`. The figure checks are a separate suite. These computations do not replace a universal proof.

The compiler is Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`. Mathlib is pinned at `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The owned logical dependency audit permits only `propext`, `Classical.choice`, and `Quot.sound`. Full commands, exact source snapshots, raw logs, dependency revisions, compiler provenance and resolved failures are included.

## Mathematical review and formal boundaries

The current source was reviewed in separate scopes: finite transfer and nonlinear coordinates; the corrected Section 17 analysis; the continuous and composition Lean interfaces; and all 59 later results plus two classical standard facts in Sections 18–27. The reports record exact revisions, hypotheses, repairs and reviewer independence limits. These are assistant mathematical audits, not a claim of external peer review.

The packet Taylor remainder and its estimate, the Stirling/Touchard term count, and Sections 18–27 retain their ordinary proof status. The range-norm proposition has partial formal correspondence: the sharper range estimate and ambient product estimate are accepted; its separate restricted-product and Hilbert corollaries are not separately formalized. Reconstruction of the total `iteratedFDeriv` does not by itself assert differentiability of an arbitrary function.

Papers I–II remain explicitly inherited dependencies. Their separate bundle was not recompiled here. No matched expanded Lean source was recovered for the historical October 16 claim of 2,693 declarations and full 98+2 coverage. That historical claim is not certified by this release. The manuscript's 98+2 count itself is verified as a source census.

## Reproduce

For a fresh extraction integrity check, run:

```bash
python3 VERIFY_RELEASE.py
```

For PDF parsing and internal-link checks, install PyMuPDF and add `--pdf`. A receipt can be written outside the frozen tree with `--output /absolute/path/to/receipt.json`.

For a new Lean verification, work in a separate copy and follow `formal/README_CONTINUATION.md`. Restore the exact compiler and nine dependency revisions, then run the full build, ownership audit, replay and controls with fresh labels and an initially empty owned object directory. The archive excludes the downloaded compiler and dependency caches. It retains the owned source, receipts and generated project objects.

For the reading files, follow `metadata/REPRODUCTION.md` and run:

```bash
python3 BUILD_PDFS.py
```

This compiles the active authored sources, refreshes the monograph locators and statement register, then assembles the reader while retaining internal links, outlines and page labels. It does not regenerate mathematical evidence. PDF bytes can vary with the TeX and font environment, so compare content and the newly produced logs if using a different environment.

## Package map

| Directory | Role |
|---|---|
| `manuscript/` | Active TeX, four mathematical chapters, bibliography and visual atlas |
| `guides/` | Active visual and Lean guide sources, figure models and finite source excerpts |
| `docs/` | Analytic supplement, exact composition figure, reader assembly |
| `formal/` | Accepted current source, exact pins, audit and control source, replay scripts and receipts |
| `evidence/` | Fresh computations, mathematical reviews, typesetting and visual QA |
| `metadata/` | Release status, statement register, reproduction notes and closeout record |
| `checkpoint_v0.3.0/` | Unchanged prior checkpoint and its inherited evidence |
| `provenance/rc1_release/` | Preserved release-candidate wrapper, readers, status and evidence |
| `provenance/unverified_oct16_visual/` | Historical visual claim retained without formal certification |

`MANIFEST_SHA256_v1.0.0.json` covers every packaged file except itself. The ZIP and clean-extraction receipt are delivered alongside the package.

## Rights

The existing copyright notices are retained. A project-wide public reuse license has not been selected. This final technical release assigns no new license and makes no public publication or redistribution decision. See `metadata/LICENSING.md`.
