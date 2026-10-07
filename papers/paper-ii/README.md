# Projector-Resolved Seed Calculus II: Refinement Towers, Weighted Transfer, and Integral Separation of Operator Packets

Komorebi P. · Final companion edition October 5, 2026

Imported into a private GitHub staging candidate on October 7, 2026. The final companion PDFs, editable sources, figures, formal project, and verification records below are available for review. No new theorem, proof repair, figure change, or formal coverage is introduced by this import.

| Companion | Pages |
|---|---:|
| [Traditional paper](papers/Paper_II_Traditional_Final.pdf) | 54 |
| [Visual guide](papers/Paper_II_Visual_Guide_Final.pdf) | 26 |
| [Lean guide](papers/Paper_II_Lean_Guide_Final.pdf) | 43 |

The 97-file canonical source, expanded manuscript, original visual models, final editable companions, local correction records, and computational receipts remain browsable. No machine-native Paper II companion is included.

## Source and evidence

- [Selected source](source/canonical_v1.2.1/)
- [Lean project](source/canonical_v1.2.1/formalization/lean/)
- [Original edition reading guide](README.txt)
- [Edition summary](EDITION.json)
- [Companion map](COMPANION_MAP.json)
- [Computational evidence and replay](verification/computational/README.md)
- [Preserved formal project guidance](source/canonical_v1.2.1/formalization/lean/README.md)
- [Import mapping, exact hashes, and omissions](provenance/GITHUB_IMPORT.json)
- [New import identity receipt](verification/GITHUB_IMPORT_CHECK.json)

The delivered edition records 48 Python tests, 118 exact visual assertions, and 22 byte-identical regenerated TikZ files. Its current formal evidence is static source/map reconciliation for the 25-row contract and 160 lexical declaration names. The September 3, 2026 formal report is historical; its raw Lean execution transcripts were not recovered. No fresh Lean compilation or kernel audit was performed for the edition or this GitHub import. The expanded inverse-limit, general-DVR, holomorphic, exponential, and multilevel arguments retain their stated ordinary mathematical scope.

Historical files retain their original dates, frozen-series statements, and execution paths. Those statements describe their source snapshot. The central repository catalogue records the current import status.

## Verify and reproduce

From this folder, using Python's standard library:

```sh
python3 scripts/verify_import.py
```

This command verifies only the imported bytes. 
The full original edition identity check also remains valid:

```sh
python3 scripts/verify_integrity.py
```

For optional numerical/visual replay, follow [verification/computational/README.md](verification/computational/README.md) and its exact dependency requirements. For a compatible pinned Lean installation, run from `source/canonical_v1.2.1/formalization/lean`:

```sh
lake exe cache get
lake build
python3 scripts/verify_theorem_map.py
lake env lean -E warning KomorebiVerification/PaperII/KernelAudit.lean
```

Final PDF compilation is documented in the original reading guide and editable companion folders. It requires the stated TeX/fonts and Python packages. No toolchain or third-party build cache is embedded.

## Rights

Original [licensing status](source/canonical_v1.2.1/LICENSE_STATUS.md) is preserved. No license has been selected for that source release and this import adds no license grant.
