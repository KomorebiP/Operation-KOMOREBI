# Machine-Native Reasoning — Lean Block 14

## Target-relative joint reconstruction

**Komorebi P. · Cumulative formal companion 0.14.0 · Reviewed Core 0.2 · 12 October 2026**

Core **8.1** joins the twenty-one preceding selected results. The admission map covers **22 of 27** selected source results. The reviewed source book and all **58 predecessor substantive modules** remain unchanged. Release assurance is recorded in `evidence/RELEASE_RESULTS_BLOCK14.md` and requires both completed current-source cold gates and their strict production-object comparison.

For actual field-linear maps A and Q, a full-record-space linear decoder D with Q = D ∘ A exists exactly when ker A ≤ ker Q. The proof constructs a decoder through the kernel quotient and attainable range, then extends it to the whole record space. The source-facing theorem retains finite-dimensional states and a finite participant family. Full-state recovery is equivalent to injectivity, and the joint kernel is the intersection of participant kernels.

Exact F₂ examples distinguish individual from joint reconstruction, target recovery from full-state recovery, and unique image-level reconstruction from potentially nonunique extensions. The source's invertible two-dimensional example recovers s as well as b; a separate third nuisance coordinate demonstrates genuine residual ambiguity. The companion records this prose caveat without editing the manuscript.

## Reading and reproduction

Start with `docs/BLOCK14_PROOF_GUIDE.md`, `docs/ASSUMPTION_REVIEW_BLOCK14.md`, `docs/THEOREM_MAP.md` and the current release results. `PROGRESS_LEDGER.md` records the five remaining selected source results and the exact next restart.

Check the payload before generating new evidence:

```bash
python3 scripts/verify_release.py
```

With the preserved Linux runtime available at the chosen path:

```bash
LD_PRELOAD=/absolute/runtime/compat/app_path.so python3 scripts/verify.py --runtime /absolute/runtime --out evidence/my_replay
```

This host requires the preserved executable-location adapter shown above. Its hash is checked with the actual compiler and imported upstream artifacts. See `docs/RUNTIME.md` and `evidence/runtime14/recovery.json`. The Lean compiler and all nine dependency revisions are unchanged. The runtime is external to this package.

The cumulative verifier compiles all **61 production modules** from source into an empty local object directory, checks source-facing APIs, audits transitive axioms, replays all **60 substantive modules** through `leanchecker`, and checks the full negative-control manifest. The current release-results table reports actual declaration and control counts. These include examples and supporting lemmas; they are not counts of discoveries or source theorems.

## Scope

Algebraic existence does not communicate records, authorize disclosure, authenticate interpretations, install a bounded executable recipient decoder or guarantee a stable noisy inverse. Same-kernel replay with pinned upstream objects is not independent peer review, an independent kernel or an upstream source rebuild. Core 8.2 is next; this version does not claim a complete-book formalization.
