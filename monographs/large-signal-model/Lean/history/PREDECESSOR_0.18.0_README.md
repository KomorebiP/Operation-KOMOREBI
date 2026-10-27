# Large Signal Model formal companion

66/87 complete formal mappings, 1 partial, and 20 unformalized.

Every proposition P1 through P65, together with P68, has a complete formal mapping. P66 remains partial. The full 87-proposition goal remains open. The monograph contains written proofs for all 87 propositions; the Lean companion checks the explicitly mapped formal statements.

This checkpoint adds P58, P59, P60, P61, P62, P63, P64, P65. `COVERAGE.md` gives the exact scope and `ROADMAP_1.0.md` lists every outstanding obligation. Register entries and finite examples do not substitute for kernel proofs.

## Verification

Use the portable Lean 4.34.0-rc2 runtime with mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. The checker validates the pins, removes project build objects, compiles every module with warnings as errors, audits every named declaration, replays each module in the kernel and checks the mathematical rejection controls.

```bash
python3 scripts/verify_hashes.py
python3 scripts/check_metadata.py
python3 scripts/verify.py --kit /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --out .verification-run
```

Run the inventory check before generating new reports or build files. The upstream library is imported at the pinned revision; it is not exhaustively rebuilt or replayed. Windows users can use WSL2 and `Check.ps1` with Linux project and kit paths. See `PORTABLE_LEAN.md`.

Start with `LEAN_GUIDE.md`, `AUDIT.md` and the desired entry in `COVERAGE.md`. `PROGRESS_LEDGER.md` preserves ancestry and restart state. Original theory and register files remain frozen under `source/`; the corrected editable publication body accompanies the monograph. The reference laboratory retains exact rational examples and scientific figures with explicit finite-test limits. Production PR-LASM is a separate artifact.
