# Projector-Resolved Seed Calculus IV: Cyclic Analytic Functions, Reciprocal Families, and Spectral Zero Data

Komorebi P. · Final companion edition October 5, 2026

Imported into a private GitHub staging candidate on October 7, 2026. The final companion PDFs, editable sources, figures, formal project, and verification records below are available for review. No new theorem, proof repair, figure change, or formal coverage is introduced by this import.

| Companion | Pages |
|---|---:|
| [Traditional paper](papers/Paper_IV_Traditional_Final.pdf) | 44 |
| [Visual guide](papers/Paper_IV_Visual_Guide_Final.pdf) | 28 |
| [Lean guide](papers/Paper_IV_Lean_Guide_Final.pdf) | 136 |

Both original component ZIPs remain under [downloads](downloads/) because the available exact archive-replay checker consumes them. Their expanded source trees are also present. A retrieval-only source-selection record is omitted from this distribution; it contains private account metadata. Its original byte hash and omission are disclosed in the import record.

## Source and evidence

- [Selected source](source/complete/)
- [Lean project](source/complete/original_snapshot/lean_release/PRSC_IV/formalization/lean/)
- [Original edition reading guide](README.txt)
- [Edition summary](EDITION.json)
- [Companion map](COMPANION_MAP.json)
- [Computational boundaries](verification/README.txt)
- [Preserved formal project guidance](source/complete/original_snapshot/lean_release/PRSC_IV/formalization/lean/README.md)
- [Import mapping, exact hashes, and omissions](provenance/GITHUB_IMPORT.json)
- [New import identity receipt](verification/GITHUB_IMPORT_CHECK.json)

The original v1.0.0 release reports full scoped formal coverage for all 68 theorem-like manuscript results, a 151-row map, 953 mapped theorem declarations, and 211 constructions. Its raw transcript, 119 Lean source files, pins, and original procedures are preserved. Imported standard fact 11.1 and explicit open questions are outside that contract. The companion edition records exact checks on 818 numeric CSV rows, four cubic brackets, and 1,008 bounded algebra assertions. Original visual/regression suites and fresh Lean were not rerun for that edition. This GitHub import adds file-identity checks only.

Historical files retain their original dates, frozen-series statements, and execution paths. Those statements describe their source snapshot. The central repository catalogue records the current import status.

## Verify and reproduce

From this folder, using Python's standard library:

```sh
python3 scripts/verify_import.py
```

This command verifies only the imported bytes. 
Some original artifacts are deliberately omitted, as individually recorded with their byte hashes. The original edition manifest remains unchanged evidence of the complete archive; its generic checker does not account for these omissions.

Optional bounded exact/static replay uses standard Python and a new output directory:

```sh
python3 -B verification/scripts/verify_available.py --source source --downloads downloads --out /tmp/paper-iv-replay
```

The original complete-edition integrity command expects the omitted retrieval record; use this import's identity checker for the current distribution. Full formal reproduction follows the preserved project README and its `VERIFY.sh` release/archive procedure. For an ordinary source build only, run from `source/complete/original_snapshot/lean_release/PRSC_IV/formalization/lean`:

```sh
lake --wfail build
```

A bare build does not assert the full archive, map, declaration-kind, and kernel audit contract.

Final PDF compilation is documented in the original reading guide and editable companion folders. It requires the stated TeX/fonts and Python packages. No toolchain or third-party build cache is embedded.

## Rights

Original [licensing status](source/complete/original_snapshot/lean_release/PRSC_IV/LICENSE_STATUS.md) is preserved. No license has been selected for that source release and this import adds no license grant.
