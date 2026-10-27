# WR03–WR05 cumulative replay

This directory supplies a source-only assembler, clean cumulative Lean replay, and terminal integrity validator. It creates no new mathematical claim by itself. Completion also requires the separate review of the exported types against the printed WR03–WR05 contract.

## Scope

The assembler checks the entire accepted v1.8 source/control snapshot against its fixed receipt hash. It separately checks that the v1.9 published production sources match that accepted formal snapshot. It copies all inherited bytes, adds the new production modules and controls, and appends imports to the combined entrypoint. Only the combined root, audit helper, and module/control inventory lists are intentionally replaced. Old entrypoints, production modules, and control fixtures are unchanged.

Production modules are discovered from the actual import graph. Every module must be reachable from `KomorebiSpaceCombined`, every local import must exist, and cycles fail. The source scanner rejects `sorry`, `admit`, custom `axiom` declarations, `native_decide`, and `unsafe` in production, and rejects local overrides enabling `autoImplicit` or disabling warnings as errors. The complete Lean environment receives the separate axiom audit.

The replay creates a new empty project object directory. It does not copy or include any predecessor project objects in `LEAN_PATH`. Every discovered project module is compiled in topological order using `-j1 -DwarningAsError=true -DautoImplicit=false`. The exact project object inventory must contain one `.olean` per expected module. Objects are hashed after compilation and again after the audit and all controls.

The audit exports every project declaration and its axiom dependencies. The allowed axiom union is contained in `propext`, `Classical.choice`, and `Quot.sound`. Every new declaration, including definitions and generated helper declarations, has its full type printed with explicit arguments, proof terms, universes and fully qualified names. Empty or ellipsis-truncated new types fail verification. The new declaration catalogue is saved separately for statement review.

All inherited and new controls are executed. Negative controls require exit status 1 and their specified intended error text. Missing objects, missing symbols, typeclass synthesis failures, crashes, heartbeat/depth exhaustion, timeouts, and out-of-memory failures are not accepted as mathematical rejection evidence. New controls are enumerated explicitly in `formal/tests/control_manifest.json` and the manifest must cover every fixture exactly once.

All source/control/helper bytes, toolchain bin/lib files, external compiled cache files, adapter, inventory and compiled project objects receive endpoint preservation checks. Python helpers load `common.py` directly from source, avoiding timestamp-cached bytecode. Each compiler invocation records actual arguments, working directory, status, timeout, elapsed time and log hash. Failures and interrupted runs keep their records. Existing attempt labels cannot be overwritten.

## Commands

Run these commands from the handoff project root, replacing labels only when starting a genuinely new immutable attempt. Freeze source, controls and independently reviewed helpers first.

```bash
python budget_v1.10.0/integration/scripts/assemble.py \
  --base continuation/integration/runs/wr01_wr02_overlay_01 \
  --published output/Komorebi_Space_Monograph_v1.9.0/formal \
  --overlay budget_v1.10.0/formal \
  --label wr03_wr05_01

python budget_v1.10.0/integration/scripts/verify.py \
  --assembly budget_v1.10.0/integration/assemblies/wr03_wr05_01 \
  --runtime runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2 \
  --path-adapter runtime/downloads/Komorebi_Portable_Lean_4.34.0-rc2/compat/app_path.so \
  --label clean_budget_01

python budget_v1.10.0/integration/postflight/validate.py \
  --assembly budget_v1.10.0/integration/assemblies/wr03_wr05_01 \
  --run budget_v1.10.0/integration/runs/clean_budget_01 \
  --reviewed-helpers PATH_TO_INDEPENDENT_REVIEW.json
```

The independent review JSON must have `status: "PASS"` and `files`, a complete mapping from the names in `integration/scripts/` to their reviewed SHA-256 hashes. The reviewer must also review `integration/postflight/validate.py` and supply its hash as `postflight_sha256`; the validator binds itself to that reviewed revision. The postflight imports no replay helper code. It independently reconstructs every expected command and validates exact targets, flags, logs, source inventory, object inventory, declaration catalogue and axiom policy.

## Trust boundaries

The official Lean compiler/kernel, its standard library and the listed standard axioms are trusted. The pinned external package caches are reused and are **not** rebuilt or independently authenticated from source. Their repository revisions and tracked clean status are checked before and after replay. Every file in the toolchain bin/lib trees and actual external cache directories is SHA-256 hashed before and after replay, with file symlink targets bound as well. This establishes endpoint byte preservation, while their initial compiled content remains trusted. System libraries and the Python interpreter remain trusted. The portable executable path adapter is trusted and hashed. This is a Linux run, not a native Windows execution claim.

Endpoint hashes establish equality at the recorded checks. They cannot detect a transient modification restored before a later check. The checker is not a hostile multiuser tamper-proof execution system.

A passing compiler run proves the stated Lean declarations under their actual exported assumptions. It does not by itself show that those declarations express every clause of the printed manuscript, verify a Python implementation, or establish an unrestricted theorem beyond those assumptions. Those claims belong to the separate mathematical/type review.

The one-module exporter smoke run under `development/` verifies exporter compatibility on an inherited module only. It is not a fresh cumulative replay or evidence of a new theorem.
