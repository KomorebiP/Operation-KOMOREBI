# Multiresolution Signal Calculus

**Exact coordinates, singular packets, and stable reconstruction**  
Paper V · Komorebi P.

| Read | Pages |
|---|---:|
| [Traditional manuscript](papers/Paper_V_Traditional_Final.pdf) | 131 |
| [Visual guide](papers/Paper_V_Visual_Guide_Final.pdf) | 43 |
| [Lean and evidence guide](papers/Paper_V_Lean_Guide_Final.pdf) | 60 |
| Total | 234 |

Open [START_HERE.html](START_HERE.html) for the reading index.

## Source and accepted scope

The accepted publication edition is release 1.2.0, dated October 20, 2026. This freeze preserves its manuscripts, figures, code, source history, open licenses and evidence. The closeout's corrected normalized Gibbs example and its reviewed locators remain unchanged.

The inherited formal contract has twenty scoped manuscript results, 225 targets and twenty-three proof modules. September 6 compiler evidence remains inherited. The broader sixty-three prose proof records are outside full Lean certification. Stable edge-packet recovery and the edge-packet approximation-class conjecture remain open; separated-jump results retain their stated model, gap and grid assumptions.

- [Editable manuscripts and guides](editable/)
- [Accepted closeout status](verification/closeout_2026-10-20/RELEASE_STATUS.json)
- [Current source preservation](verification/closeout_2026-10-20/SOURCE_PRESERVATION.json)
- [Original reproduction instructions](README.txt)
- [Freeze record](FREEZE_RECORD.json) and [progress ledger](PROGRESS_LEDGER.md)

## Verify the frozen package

Extract this single complete ZIP, enter its root directory and run:

```sh
python3 -B scripts/verify_integrity.py --strict
```

This unchanged portable standard-library verifier checks exact regular-file membership, safe paths, sizes and SHA-256 values. The complete inventory uses its existing strict manifest schema. The previous manifest is retained under `verification/freeze_2026-10-20/before/`.

For the recorded source, navigation, current PDF and evidence checks, run:

```sh
python3 -B scripts/verify_release.py
```

That command also needs PyMuPDF. It authenticates stored records and does not run Lean, the finite suites or a PDF compiler. The accepted twenty-one integrity controls are bound to the unchanged verifier and are not rerun by this freeze. Fresh freeze checks authenticate the baseline and readers, the complete file set and clean extraction.

Use a separate working copy and new external output directories for other reproduction commands in [README.txt](README.txt). The pinned Lean runtime, dependency cache, Python/TeX dependencies and declared fonts remain external prerequisites.

## Historical recovery and open use

Seventeen original October 5 verification artifacts remain unrecovered and are listed in [provenance/HISTORICAL_RECOVERY_GAPS.json](provenance/HISTORICAL_RECOVERY_GAPS.json). Current mathematical manuscripts, figures and original Lean source are present. New evidence does not authenticate the missing historical bytes.

Original software and machine-readable material use MIT. Original papers, guides, figures and explanatory writing use CC BY 4.0. The unchanged grants and third-party exceptions are in [LICENSE.md](LICENSE.md), [LICENSE_STATUS.json](LICENSE_STATUS.json) and [LICENSES/](LICENSES/).

This distribution was frozen on October 20, 2026, America/Chicago. The accepted formal, finite, publication and tooling events retain their own dates and scopes. No new Lean run, finite experiment, TeX rebuild or whole-paper proof audit is claimed. The next sequential freeze is Paper VI.
