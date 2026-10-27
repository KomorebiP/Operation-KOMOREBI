# Verification and proof boundary — v0.2.0

## Actual current source build

**PASS: 20 proof modules, one root import, 156 explicitly named theorem declarations.**

Started: `2026-09-27T15:33:42.842525+00:00`  
Finished: `2026-09-27T15:34:37.477172+00:00`

All six new modules and all 14 unchanged baseline modules were compiled into an emptied output directory. No compiled project file was reused for this clean build. Compiler and dependency cache files were reused.

| Check | Result |
|---|---|
| `lean_pin` | PASS |
| `mathlib_pin` | PASS |
| `no_project_admissions_or_axioms` | PASS |
| `clean_compile_all` | PASS |
| `axiom_audit_complete` | PASS |
| `only_allowed_axioms` | PASS |
| `reject_FalseStatement` | PASS |
| `reject_Placeholder` | PASS |
| `reject_axiom_injection` | PASS |
| `sources_unchanged_during_verification` | PASS |

## Toolchain

```text
Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)
mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06
lean executable SHA-256: e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550
```

Command used for this run:

```bash
python3 scripts/verify.py \
  --runtime /mnt/data/runtime/Komorebi_Portable_Lean_4.34.0-rc2 \
  --audit-dir audit/current --timeout 120
```

Every library compile uses `-j1 -DwarningAsError=true -DautoImplicit=false`. Exact per-process arguments, exit codes, durations, source hashes, compiled hashes, and log hashes are in `audit/current/VERIFICATION.json`. Each timeout is a process execution limit, not a proof hypothesis. No timeout occurred in the complete run.

## Axiom checks and controls

`checks/AxiomAudit.lean` requests `#print axioms` for the entire indexed set of 156 named theorems. The returned names match that set, with dependencies restricted to `propext`, `Classical.choice`, and `Quot.sound`.

The positive library has no `sorry`, `admit`, custom `axiom`, `unsafe`, `native_decide`, or `implemented_by` tokens outside comments. Negative fixtures are deliberately excluded from the library. A false statement and a proof placeholder fail as expected. The injected custom axiom is accepted by Lean as an assumption but detected and rejected by the audit, as intended.

## What the new result proves

Actual Banach-tower differential construction and boundedness, agreement with the previous exact tower core, constructed iterative repair under explicit correction-operator assumptions, a bounded projection onto the exact kernel, semantic preservation, splitting, and actual inverse-limit realization. Two concrete models and a nonuniqueness diagnostic are included. The source signatures are authoritative.

No universal correction-operator existence, unrestricted pro-category equivalence, stack/descent theorem, higher obstruction construction, or arithmetic correspondence is claimed. A fixed scheme produces a specified limit; scheme-independent canonicity requires the stated separation hypothesis.

## Provenance and delivery

The unchanged v0.1.0 modules were independently rebuilt first in this continuation. The original ZIP and receipt and the fresh baseline replay are under `provenance/`. They are not substituted for current evidence. `provenance/BASELINE_COMPARISON.json` checks that all 14 original proof modules remain byte-identical.

The delivered ZIP is replayed from a separate freshly extracted directory. Its report, archive hash, and source/compiled-output comparison are recorded in the separate delivery receipt, avoiding a circular archive hash.

## Trust boundary

The Lean executable and cached imported declarations remain trusted. Neither the compiler nor the entire mathlib dependency closure was rebuilt from source. The axiom audit is not a separate kernel implementation. The declaration indexer is specific to this project's namespace/section style. SHA-256 checks establish file consistency, not independent theorem truth.

The archive omits the multi-gigabyte runtime/cache. The portable runtime is Linux x86-64. The recorded route is offline direct-compiler replay, not a newly verified online Lake bootstrap or native Windows run.

The v1 computation manifest includes complete source hashes and a link to the per-process verification report. Its project-local schema validation is not a replacement for the Lean run and does not upgrade it to a version-2 bounded-runner record.

## Failure log

`docs/CORRECTIONS.md`, sections 12–14, distinguishes the historical failures from this continuation's failed setup and development runs. Current development logs are under `audit/development_v0.2.0/`. Every final source was recompiled after its last edit.
