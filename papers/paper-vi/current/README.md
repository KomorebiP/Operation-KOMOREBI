# Transfer Semigroups and Memory

**Probabilistic refinement, fractional operators, and exact hidden-state elimination**  
Paper VI · Komorebi P.

| Read | Pages |
|---|---:|
| [Traditional manuscript](papers/Paper_VI_Traditional_Final.pdf) | 152 |
| [Visual guide](papers/Paper_VI_Visual_Guide_Final.pdf) | 44 |
| [Lean and evidence guide](papers/Paper_VI_Lean_Guide_Final.pdf) | 64 |
| Total | 260 |

Open [START_HERE.html](START_HERE.html) for the reading index.

## Accepted publication and scientific scope

The accepted release is 1.0.0, dated October 20, 2026; its mathematical body edition remains October 9. This freeze preserves its manuscripts, figures, scientific source, history, licenses and evidence. All 184 numbered records, 140 proof bodies, 739 original scientific source files and three original archives remain unchanged.

The inherited formal contract covers 33 scoped results, 341 theorem targets, 47 production modules and 782 namespace declarations. Its compiler and axiom evidence is the September 6 `0.5.0-checked-fifth-block` release. The broader 142 theorem-like records and 140 written proofs do not enlarge this finite contract. Full-paper Lean formalization is incomplete.

The accepted closeout's eleven bounded records retain their own input sets, units and dates. They include overlapping dispatcher checks and are not an independent theorem count. Floating residuals are not interval certificates. Finite-state, common-gap, fixed-partition and other stated assumptions remain in force. Classical conditional expectation, martingale convergence and stable subordination retain their ordinary classical scope; no arbitrary-martingale L2 convergence is asserted.

- [Editable manuscripts and guides](editable/)
- [Accepted closeout status](verification/closeout_2026-10-20/RELEASE_STATUS.json)
- [Source preservation](verification/closeout_2026-10-20/SOURCE_PRESERVATION.json)
- [Original reproduction instructions](README.txt) and [font prerequisites](FONT_DEPENDENCIES.txt)
- [Freeze record](FREEZE_RECORD.json) and [progress ledger](PROGRESS_LEDGER.md)

## Verify the frozen package

Extract this single complete ZIP, enter its root directory and run:

```sh
python3 -B scripts/verify_integrity.py --strict
```

This unchanged portable standard-library verifier checks exact regular-file membership, safe paths, sizes and SHA-256 values. The current root manifest retains the accepted strict schema. The root checksum list covers every other payload file except the root manifest, which additionally authenticates the list. Both original administrative indexes are preserved under `verification/freeze_2026-10-20/before/`.

For recorded source, navigation, PDF and evidence bindings, run:

```sh
python3 -B scripts/verify_release.py
```

That command also needs PyMuPDF. It reconciles static source and authenticates stored records without compiling Lean, running finite suites or rebuilding PDFs. The accepted 21 integrity controls bind the unchanged verifier and harness; this freeze does not rerun them. Fresh freeze checks cover the baseline, current readers, complete file set and clean extraction.

Use a separate working copy and external output directories for other reproduction commands. The pinned runtime, dependency binaries, TeX/Python tools and declared fonts remain external prerequisites. The corrected builders and font instructions from the accepted release are unchanged.

## Research, history and open use

Three research questions remain open: transfer-semigroup realization on completed state spaces, uniform refinement control, and latent-packet closure for stable infinite systems.

The dated original ledger and closeout JSON refer to IX as the next incomplete paper and X as a source-recovery hold. Those workflow pointers are historical: IX and X subsequently closed within their selected scopes. The current sequential freeze continues with VII. Original audit lineage and its disclosed historical whole-file reconstruction limits remain intact; this freeze does not reconstruct a missing historical assembled file or repeat a semantic proof audit.

Original software and machine-readable material use MIT. Original writing, figures and editable writing sources use CC BY 4.0. The unchanged grants and third-party/font exceptions are in [LICENSE.md](LICENSE.md), [LICENSE_STATUS.json](LICENSE_STATUS.json) and [LICENSES/](LICENSES/).

This distribution is frozen as of October 20, 2026, America/Chicago. Actual verification timestamps retain UTC dates. No fresh Lean execution, finite experiment, control suite, TeX rebuild or whole-paper proof audit is claimed. No public website or repository is published by this task.
