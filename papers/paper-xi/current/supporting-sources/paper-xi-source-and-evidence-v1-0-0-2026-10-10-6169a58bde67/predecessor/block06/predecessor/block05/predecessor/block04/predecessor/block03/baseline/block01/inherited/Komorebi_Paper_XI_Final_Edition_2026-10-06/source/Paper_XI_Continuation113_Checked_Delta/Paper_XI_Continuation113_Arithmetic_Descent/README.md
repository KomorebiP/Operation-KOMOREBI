# Paper XI Continuation113 — Arithmetic descent and wild correction

**Status: 65/66. Original Claim16.2 is still open.**

Start with `reports/INTEGRATION113.md` for the mathematical result and
`CONTINUE_HERE113.md` for the next exact task. `STATUS113.json` records the
claim boundaries, evidence paths and hashes.

This round adds four checked Lean modules (76 named exports), a concrete
cubic arithmetic example, a proof that its first proposed simple character
does not occur in the original automorphic induction, and a different
wild-unit correction that passes the full cubic self-twist test. Occurrence
of that corrected character in the original AI(chi_0) remains unproved.

The abstract finite results are Lean-checked. The arithmetic results are
ordinary source-backed proofs with exact rational computations and independent
audits. They are not Lean formalizations of local fields or automorphic
induction. Original theta/kappa and same-completion H5 are not replaced.

## Archive contents

* `formalization/PaperXI/`: the four new Lean sources.
* `reports/`: integration, route reports, independent audits and corrections.
* `evidence/`: exact outputs, original run manifests, logs, failed attempts and
  the four modules' final compiled objects.
* `scripts/`: replay, exact finite models, wild-image computation and packaging.
* `REPLAY_BASE113.json`, `INHERITED_OBJECTS113.json`, `ENVIRONMENT.json`: exact
  inherited dependencies and runtime identity.
* `PACKAGE_MANIFEST113.json`: every included file's size and SHA-256, except
  the manifest itself; packaging selection and exclusions are recorded.

This is a continuation archive. The baseline110,111,112 archives, portable
Lean runtime and supplied source papers are external dependencies identified
by hashes. They are not duplicated. All inherited `objects/` directories,
temporary Python caches and rendered source-page images are omitted. Only
the eight final .olean/.ilean files for the four new modules are retained.
Some original evidence receipts contain absolute paths from the recorded
run; those receipts are historical evidence and have not been rewritten.

## Replay

Use the pinned Lean4.34.0-rc2 portable kit and Mathlib commit in
`ENVIRONMENT.json`. Put the three authenticated baseline archives from
`REPLAY_BASE113.json` in one directory. From this continuation root, run:

```sh
python scripts/verify_new113.py \
  --kit /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --archives /absolute/path/to/baseline_archives \
  --out evidence/replay_on_new_machine
```

The output directory must not already exist. The verifier authenticates the
runtime binary, Mathlib revision, archives and all280 inherited object files;
freshly builds the four new modules; audits every named export; and runs
leanchecker. Inherited modules and Mathlib are reused, not rebuilt. The
delivered passing receipt is in `evidence/final_replay_corrected/replay/`.

The arithmetic and finite scripts use Python standard-library exact integer
and rational arithmetic. Original bounded commands and contracts are retained
with their manifests. Use fresh output directories when replaying; do not
overwrite historical evidence. Source-based implications must also be checked
against the supplied primary papers identified in the route reports.

For the complete failure and wording history read `reports/REVIEW_NOTES113.md`
and `reports/ROOT_VERIFICATION_FAILURES113.md`. The old overwritten arithmetic
receipt is disclosed as unavailable, never reconstructed as a passing record.
