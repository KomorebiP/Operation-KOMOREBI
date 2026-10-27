# Paper XII — completion reverified

This is the cumulative **v0.17.1** evidence release for the revised 49-claim formalization.
Both formerly disputed completion claims pass a fresh source replay. Read
`LATEST_STATUS.md` and `COMPLETION_CONTRACT_REVIEW.md` for the exact scope.

## Replay

Use the existing offline kit pinned to Lean 4.34.0-rc2 and Mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

```bash
bash Run-Portable.sh /path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 checks/verify_contracts.py /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The first command starts from an empty project build directory and rebuilds all
registered modules. Its report is not PASS until every module, axiom audit and negative
control succeeds. The second verifies the three explicit contract tests against those
freshly checked dependencies. Both commands require a final exit code of zero.

For execution environments with short per-call limits, use the verifier's `--start
--batch 2` and then `--resume --batch 2` interface as documented in its source. A RUNNING
record is not a proof certificate. Interrupted modules must be recompiled.

## Contents

`lean/` contains all 96 production modules unchanged from v0.17.0. `checks/` contains
the replay tools and three added direct contract tests. `build/`, `logs/`, and the JSON
records preserve the fresh verification evidence. `paper/` contains the unchanged
manuscript and editable source. `upstream/` preserves earlier verification and coverage
records. `development/` preserves corrected failures, not accepted production proofs.

This release changes evidence and status reconciliation, not the mathematics or the
original-versus-revised boundaries. It does not rebuild Mathlib, claim historical
novelty, or establish the external arithmetic prerequisites.
