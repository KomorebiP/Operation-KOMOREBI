# Paper I final Lean audit — 10 October 2026

**PASS for the complete current 35-row formal contract.** This is a fresh audit of formal component v1.0.2, not a new mathematical version.

Start with `PAPER_I_FINAL_LEAN_AUDIT.md`, then `VERIFICATION.json`. The source-owned audit covers 1,152 entries and the complete contract maps 84 declarations. All 20 production Lean files remain byte-identical to the authoritative package. All 20 were rebuilt and replayed.

## Contents

`source/main/` contains the complete current formal component and its pinned configuration. `audit/` contains semantic review and the exhaustive declaration crosswalk. `evidence/` contains successful runs, preserved failures, object files, and identity records. `tests/` contains audit programs, mathematical consumers, and deliberately invalid nonproduction fixtures. `scripts/` contains the replay tools. `PROGRESS_LEDGER.md` and `.json` record the next restart.

## Repeat the audit

Linux or WSL, Python 3, and the exact externally provisioned portable kit are required.

```bash
bash scripts/run_audit.sh   /absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2   /absolute/path/to/new-audit-output
```

The new output directory must not already exist. This rebuilds local sources and reuses pinned upstream objects. It does not rebuild Mathlib or use an independently implemented Lean kernel. The wrapper is serial to avoid concurrent memory-heavy Lean processes.

The 35-row contract does not equal the expanded monograph's 108-record inventory. Certificate inputs and noncomputable algorithm boundaries remain explicit. See the semantic review. The inherited license-status file remains unchanged.

The first interrupted build's raw JSON says RUNNING because it was written before interruption. It is not still running. `evidence/RUN_INDEX.json` and the interruption record give its effective status. No work is left running after this handoff.
