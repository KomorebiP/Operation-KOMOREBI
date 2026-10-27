# Machine-Native Reasoning — Lean Block 13

## Conditional error budgets across an adaptive lineage

**Komorebi P. · Cumulative formal companion 0.13.0 · Reviewed Core 0.2 · 12 October 2026**

Core **7.4** joins the twenty preceding selected results. The admission map covers **21 of 27** selected source results. The reviewed source book and all **56 predecessor substantive modules** remain unchanged. This release's executable assurance is recorded in `evidence/RELEASE_RESULTS_BLOCK13.md` and requires both completed current-source cold gates and their strict production-object comparison.

The new measure-theoretic module proves the source proposition for arbitrary probability spaces and countably many attempts. Almost-sure conditional bounds for actual selected false-acceptance events imply marginal bounds. Countable subadditivity then bounds the probability of ever accepting a false claim by the sum of a deterministic nonnegative summable schedule. Outcome-dependent stopping only removes error events. No independence assumption is used.

A selected-candidate interface retains the conditional premise on the actual selected event. The accompanying exact finite examples show why fixed-candidate marginal labels are insufficient, why null does not mean empty, and why a stopped-event bound does not automatically bound the error conditional on retention. A separate formal counterexample records the divergent real `tsum` trap. Explicit summability prevents it from entering the source theorem.

## Reading and reproduction

Start with `docs/BLOCK13_PROOF_GUIDE.md`, `docs/ASSUMPTION_REVIEW_BLOCK13.md`, `docs/THEOREM_MAP.md`, and the current release results. `PROGRESS_LEDGER.md` records the six remaining selected source results and the exact next restart.

Check the payload before generating new evidence:

```bash
python3 scripts/verify_release.py
```

With the preserved Linux runtime available at the chosen path:

```bash
python3 scripts/verify.py --runtime /absolute/path/Komorebi_Portable_Lean_4.34.0-rc2 --out evidence/my_replay
```

This host additionally required the preserved runtime's `compat/app_path.so` executable-location adapter via `LD_PRELOAD`. Its hash is checked with the actual compiler and imported upstream artifacts. See `docs/RUNTIME.md` and `evidence/runtime13/recovery.json`. The exact Lean compiler and nine dependency revisions are unchanged. The runtime is external to this package.

The cumulative verifier compiles all **59 production modules** from source into an empty local object directory, checks source-facing API statements, audits actual transitive axioms, replays all **58 substantive modules** through `leanchecker`, and checks **135 negative-control contracts**. There are **918 authored theorem declarations**, including 36 new supporting theorems, within 1,401 authored declarations. These counts include examples and supporting lemmas. They are not counts of discoveries or source theorems.

## Scope

Conditional validity is an application premise. This block does not calibrate an evaluator, infer a stochastic law from deterministic checks, prove a data-dependent spending rule, or establish physical-model truth. The arbitrary-gate extension is an outer-measure statement until gate measurability is supplied. Same-kernel replay with preserved dependencies is not independent peer review or an upstream source rebuild.
