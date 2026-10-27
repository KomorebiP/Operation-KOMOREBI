# Projector Resolved Seed Calculus II

**Refinement towers, weighted transfer, and integral separation of operator packets**  
Komorebi P.

| Read | Pages |
|---|---:|
| [Traditional manuscript](papers/Paper_II_Traditional_Final.pdf) | 80 |
| [Visual guide](papers/Paper_II_Visual_Guide_Final.pdf) | 26 |
| [Lean guide](papers/Paper_II_Lean_Guide_Final.pdf) | 51 |

The three readers contain 157 pages. The traditional manuscript includes twenty-four worked plates. Open [START_HERE.html](START_HERE.html) for the reading index.

## Sources and evidence

- [Editable sources](editable/) and [current Lean source](formal/current/)
- [Current correspondence map](formal/coverage/Paper_II_Current_Correspondence_2026-10-19.json)
- [Accepted replay](verification/closeout_2026-10-19/attempt02_m4096/verification.json)
- [Release status](RELEASE_STATUS.json) and [reproduction instructions](REPRODUCIBILITY.md)
- [Freeze record](FREEZE_RECORD.json) and [progress ledger](PROGRESS_LEDGER.md)

All fifty-three enumerated proof-level records have accepted exact-source correspondence under their displayed hypotheses. The accepted October 19 run records seventy-five production modules, 2,112 logical declarations replayed and nine negative controls. Canonical values require the stated admissible data. No general admissible-contour existence theorem is added by the release or this freeze.

## Verify the frozen package

Extract this single complete ZIP, enter its root directory, and run:

```sh
python3 scripts/verify_frozen_release.py
```

This standard-library command checks the exact file set, sizes, SHA-256 values and preservation of the complete accepted baseline. The original manifest is retained under `verification/freeze_2026-10-20/before/`. Earlier receipts identify their original inputs; the current complete-package inventory is the root `MANIFEST_SHA256.json`.

Fresh freeze checks authenticate the baseline and linked evidence, current reader identities and selected renders, and the cleanly extracted ZIP. The existing forty-eight Python tests retain their successful October 20 execution record. This freeze does not repeat Lean, Python experiments, a TeX rebuild or a whole-paper proof audit. The accepted sources, PDFs and license notices retain their reviewed bytes.

## Open use and reproduction

Original software and machine-readable material use MIT. Original papers, guides, figures and explanatory writing use CC BY 4.0. See [LICENSE.md](LICENSE.md) for full scope and third-party exceptions, and [LICENSES/](LICENSES/) for the complete terms.

Formal replay needs the external pinned Lean 4.34.0-rc2 Linux runtime and dependency cache. Use a separate working copy for rebuilding or running commands that create files. [REPRODUCIBILITY.md](REPRODUCIBILITY.md) gives the exact recorded commands and their trust boundaries.

Reading edition: October 19, 2026. Accepted open release: 1.1.1, October 20, 2026. Frozen distribution: October 20, 2026. Dated source, maps and reports preserve their historical scope.
