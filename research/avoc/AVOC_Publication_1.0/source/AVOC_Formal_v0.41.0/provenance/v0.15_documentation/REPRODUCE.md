# Reproduce AVOC v0.15.0

Use Linux x86-64 or WSL, Python 3.10+, Lean 4.34.0-rc2 (commit 6a10ac8c22beadecabdbb0919c2b50214762f91d), and mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. `lake-manifest.json` freezes all nine external package revisions.

The small project archive excludes the portable runtime, dependencies and local binary outputs. The tested runner expects the existing portable kit layout: `toolchain/bin/lean` and `workspace/.lake/packages/`. Set its location:

```bash
export AVOC_LEAN_KIT=/absolute/path/Komorebi_Portable_Lean_4.34.0-rc2
```

From the extracted release root, check delivered bytes before changing evidence:

```bash
python tools/check_manifest.py
python tools/verify_release.py --prepare
python tools/verify_release.py
python tools/verify_release.py --audit
python tools/verify_release.py --negative
python checks/test_model_bridge.py
python tools/summarize_v015.py --baseline /path/to/AVOC_Formal_v0.14.0.zip
```

`--prepare` verifies the nine dependency revisions and deletes only this project's `.lake/build`. It retains the external binary caches. The final graph has **76** local targets. Do not call `--prepare` between build slices. The last summarizer checks compiler evidence, current source/output/log hashes, the full axiom name set, all negative results, tracked dependency state and regression provenance. The final result is `AUDIT.json`.

When the original v0.14 ZIP is absent, the summarizer checks current inherited sources against the delivered baseline-hash comparison record and explicitly records that the old ZIP was not independently reopened in that rerun. Supplying the ZIP enables fresh byte comparison.

## Bounded runs

For hosts with outer execution caps:

```bash
python tools/verify_release.py --start 0 --count 12
python tools/verify_release.py --start 12 --count 12
python tools/verify_release.py --start 24 --count 12
python tools/verify_release.py --start 36 --count 12
python tools/verify_release.py --start 48 --count 12
python tools/verify_release.py --start 60 --count 12
python tools/verify_release.py --start 72 --count 4
python tools/verify_release.py --audit
python tools/verify_release.py --negative --start 0 --count 12
python tools/verify_release.py --negative --start 12 --count 12
python checks/test_model_bridge.py
python tools/summarize_v015.py
```

After an interrupted call, first confirm that its Lean child has stopped, then resume the first unfinished module. The inner runner kills a child process group on its own timeout. A tighter outer host timeout can prevent that handler from finishing, so process cleanup still must be checked after an outer interruption. An import error, timeout, parser error or deprecated-lemma warning is not accepted as a substantive negative proof test.

## Source index and proof boundary

`AVOC/FullAudit.lean` audits all 734 names in `THEOREM_INDEX.md`. `tools/inventory_v015.py` extends the preserved v0.14 name inventory with the seven new modules. The evidence summarizer independently checks the comment-aware per-module declaration count. Regenerating an index is not proof verification: rebuild and rerun the full axiom audit after any Lean source change.

The independent Fraction regression checks all specified binary prior/channel grid combinations, the weighted codec inequality, the rare-observation example, and the imperfect-model action-sequence example for horizons 0 through 7. It is not a universal proof, a real LLM experiment, or a formally extracted executable.

The formal controller uses classical finite maximization. No general efficient planner or global residual-certification procedure is delivered. Reference probabilities and error certificates must be justified separately for an application.

## Integrity after rerunning

Regenerating evidence intentionally changes file bytes and makes the original delivery manifest stale. Verify the delivery before rerunning. Generate a new manifest only after auditing the regenerated results. `.lake/`, `__pycache__/` and `*.pyc` are excluded from the delivery manifest and ZIP.

Historical release and development logs remain under their versioned result paths. Only `results/v0.15.0/clean_*`, the final axiom and negative records, and the current regression support this release's final verification claim.
