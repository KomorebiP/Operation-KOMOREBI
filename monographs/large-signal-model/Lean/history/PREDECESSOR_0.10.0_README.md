# Komorebi Large Signal Model — Lean 0.10.0

Author: Komorebi P. · Frozen mathematical source: Foundations 1.0.0.

Block 10 completes P45, rational finite-certificate search. Cumulative coverage is **36 complete, 0 partial and 51 unformalized**, out of the unchanged 87-proposition target. This is not completion of the whole framework.

The four new modules add 30 named theorems, including eight example theorems. The cumulative source has 78 proof modules, 1,304 explicitly named declarations and 998 named theorems. Seventy-two negative controls include four new certificate-boundary controls.

## Read and continue

- `LEAN_GUIDE.md`: the P45 proof and executable interface, with inherited guides in `history/`.
- `AUDIT.md`: statement mapping, assumptions, dependency obligations and failed attempts.
- `PROGRESS.md` and `PROGRESS.json`: cumulative progress and restart.
- `COVERAGE.json`: exact frozen-statement mapping to Lean declarations.
- `CONTINUE_HERE.md`: next target, P32–P34.
- `verification/block10_release_run/report.json`: source-candidate verification.
- External delivery verification JSON: independent archive extraction and cumulative replay result for the exact delivered ZIP.

## Reproduce

Use the pinned Lean 4.34.0-rc2 portable kit and its unchanged nine dependency pins. Before generating any caches, run `python3 scripts/verify_hashes.py`. Then run `python3 scripts/build_inventory.py`, `python3 scripts/check_metadata.py`, and `python3 scripts/verify.py --kit PATH_TO_KIT --out OUTSIDE_SOURCE_DIRECTORY`. This host uses the kit's supplied `compat/app_path.so` executable-location adapter through `LD_PRELOAD`; no kernel check is bypassed. The runtime itself is reused read-only, not freshly reconstructed for this block.

The verifier rebuilds all 79 project targets, runs the executable rational examples, audits every explicitly named declaration, replays all 78 modules through LeanChecker, and checks 72 isolated expected proof rejections. Allowed foundational axioms remain `propext`, `Classical.choice` and `Quot.sound`. Runtime examples are regression checks, not additional mathematical proofs.

The original theory, its proof register, predecessor proof sources and production PR-LASM 2.3.0 are unchanged. `PUBLICATION_STATUS.md` explains inherited publication metadata. No training, sensor experiment, statistical coverage test, external publication, independent referee or second-prover claim is made.
