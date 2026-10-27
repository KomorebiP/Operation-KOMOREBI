# Large Signal Model formal companion

48/87 complete formal mappings, 1 partial, and 38 unformalized.

The monograph contains 87 propositions with written proofs. This companion checks the mapped formal statements in Lean. Every proposition P1 through P45 has a complete formal mapping. The full 87-proposition formalization remains open.

The current checkpoint adds complete mappings for P11, P23, P24, P31, P35, P37, P48, P57, P68. `COVERAGE.md` states the exact scope of every mapping, and `ROADMAP_1.0.md` lists the outstanding work. A register entry or a finite example is not a kernel proof.

## Verify with the portable runtime

Restore the matching portable Lean kit and pass its root folder to the checker. The supported runtime is Lean 4.34.0-rc2 with mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The checker validates those pins, removes its project build objects, compiles every proof module with warnings treated as errors, audits every named declaration, replays each module in the kernel and checks the false-claim controls.

```bash
python3 scripts/verify_hashes.py
python3 scripts/check_metadata.py
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out .verification-run
```

Run the inventory check before generating new reports or build files. Verification reports and compiler output state their scope; the upstream library is pinned and imported, rather than rebuilt or exhaustively replayed.

On Windows, use WSL2 and the supplied `Check.ps1`, passing the Linux paths of this project and the restored kit. `PORTABLE_LEAN.md` explains the runtime layout and startup recovery.

## Read the result

Start with `LEAN_GUIDE.md`, then the mapped proposition in `COVERAGE.md`. `AUDIT.md` records review boundaries and `PROGRESS_LEDGER.md` preserves the restart state. The original manuscript and its source register are retained unchanged under `source/`. The corrected editable publication body is supplied separately with the monograph.

The reference laboratory includes exact rational examples, certificates and scientific figures. Its finite runs support reproducibility and boundary checks, while the Lean files prove their stated universal claims. The production PR-LASM software is a separate artifact.
