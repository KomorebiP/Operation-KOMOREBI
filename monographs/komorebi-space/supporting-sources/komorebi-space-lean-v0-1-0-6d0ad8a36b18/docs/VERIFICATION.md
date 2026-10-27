# Verification and proof boundary

## Recorded result

**PASS — 14 proof modules, one root import, 96 explicitly named theorems.**

Started: `2026-09-27T12:48:42.661765+00:00`  
Finished: `2026-09-27T12:49:05.438855+00:00`

The compiler was actually executed. All project modules were built into a newly emptied output directory. The release does not label uncompiled source as checked.

| Check | Result |
|---|---|
| lean_pin | PASS |
| mathlib_pin | PASS |
| no_project_admissions_or_axioms | PASS |
| clean_compile_all | PASS |
| axiom_audit_complete | PASS |
| only_allowed_axioms | PASS |
| reject_FalseStatement | PASS |
| reject_Placeholder | PASS |
| reject_axiom_injection | PASS |
| sources_unchanged_during_verification | PASS |

## Compiler and library

```text
Lean (version 4.34.0-rc2, x86_64-unknown-linux-gnu, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d, Release)
mathlib: aeb72f1e9981b6d35b426b16dca7759be3e7ba06
Lean executable SHA-256: e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550
```

Every library compilation used `-j1 -DwarningAsError=true -DautoImplicit=false`. Exact argument vectors, durations, exit codes, source hashes, output hashes and log hashes are in `audit/latest/VERIFICATION.json`.

## Axiom audit

`checks/AxiomAudit.lean` requests `#print axioms` for all 96 named theorems. The parsed output covers the complete indexed set. No unexpected axiom was reported. The permitted standard set is `propext`, `Classical.choice`, and `Quot.sound`.

The positive source files contain no proof placeholders, admissions, custom axioms, unsafe declarations, native-decision proofs, or implementation substitutions. The invalid negative fixtures are deliberately excluded from the library.

## Negative controls

- A false integer equality is rejected by Lean.
- A proof placeholder is rejected with warnings treated as errors.
- A theorem made from an injected false axiom is accepted by Lean *as a theorem under that axiom*, but rejected by the certificate audit because the custom axiom is outside the allowed set. This distinction is intentional.

## Mathematical scope

The theorem statements quantify over their mathematical domains; they are not extrapolations from bounded simulations. Several are structural lemmas, definitions-by-construction, or standard results specialized to this framework. The count is a source-declaration count, not a novelty metric.

`docs/CONSOLIDATED_THEORY.md` gives the principal statements. `docs/OUTLINE_STATUS.md` records the boundary of every original outline section.

## Trusted and unverified components

Lean's executable and standard foundation are trusted. Pinned, previously compiled mathlib and dependency `.olean` files were reused. The full dependency library and compiler were not rebuilt from source. The axiom audit does not independently establish that the compiler binary or its cached imports are uncompromised.

This archive contains source and replay tooling, not the multi-gigabyte toolchain/cache. The recorded replay uses the restored offline kit described in the README. A fresh online Lake bootstrap was not executed successfully in this restricted environment.

## Failure history

Initial runtime acquisition and project setup failed before restoration from the Library kit. Development compilation errors were fixed. An initial complete audit failed one negative-control name-matching check, even though library compilation and theorem audits had passed. The check was repaired, and a complete clean verification then passed. The failed receipt remains under `audit/development_failures/`.

## Evidence files

- `audit/latest/VERIFICATION.json`: authoritative clean build and axiom audit.
- `audit/declaration_index.json`: explicit source declarations with locations.
- `audit/computation-manifest.json`: schema-v1 evidence manifest, supplemented with source hashes.
- `FILES.sha256`: complete packaged file integrity list.
- `scripts/check_hashes.py`: checks those hashes.

A separate delivery receipt records any extracted-archive replay. It is external to the archive to avoid a circular archive hash.
