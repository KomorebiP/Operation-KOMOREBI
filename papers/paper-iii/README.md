# Projector-Resolved Seed Calculus III: Typed Transfer, Nonlinear Packets, and Obstruction Theory

Komorebi P. · Final companion edition October 5, 2026

Imported into a private GitHub staging candidate on October 7, 2026. The final companion PDFs, editable sources, figures, formal project, and verification records below are available for review. No new theorem, proof repair, figure change, or formal coverage is introduced by this import.

| Companion | Pages |
|---|---:|
| [Traditional paper](papers/Paper_III_Traditional_Final.pdf) | 68 |
| [Visual guide](papers/Paper_III_Visual_Guide_Final.pdf) | 26 |
| [Lean guide](papers/Paper_III_Lean_Guide_Final.pdf) | 47 |

The source preserves the finite v1.0.1 release, strengthened expanded manuscript, historical expanded branch, original visual models, and all final editable companions. Four disclosed local expanded-proof repairs are recorded in [CORRECTIONS.txt](CORRECTIONS.txt).

## Source and evidence

- [Selected source](source/finite/)
- [Lean project](source/finite/formalization/lean/)
- [Original edition reading guide](README.txt)
- [Edition summary](EDITION.json)
- [Companion map](COMPANION_MAP.json)
- [Computational boundaries](verification/computational/README.txt)
- [Preserved formal project guidance](source/finite/formalization/lean/README.md)
- [Import mapping, exact hashes, and omissions](provenance/GITHUB_IMPORT.json)
- [New import identity receipt](verification/GITHUB_IMPORT_CHECK.json)

The delivered edition records a partial computational rerun: original finite static/integrity checks, 11 strengthened verification groups, and three byte-identical canonical figures. Its finite formal contract has 41 rows and 143 mapped declarations: 88 theorems and 55 constructions. The September 3, 2026 formal report and raw transcript are historical. The 124 visual checks, four false controls, 22-plate regeneration, and fresh Lean compilation were not rerun for the edition. This GitHub import adds file-identity checks only. The strengthened nonlinear and analytic development remains beyond the finite formal contract.

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

Optional computational replay and requirements are in [verification/computational/README.txt](verification/computational/README.txt). For a compatible pinned Lean installation, run from `source/finite/formalization/lean`:

```sh
lake --wfail build
python3 scripts/verify_theorem_map.py
lake env lean -E warning KomorebiPaperIII/KernelAudit.lean
```

The inherited Papers I–II declarations are separately pinned and cited; the standalone Paper III project does not recompile those inherited contracts.

Final PDF compilation is documented in the original reading guide and editable companion folders. It requires the stated TeX/fonts and Python packages. No toolchain or third-party build cache is embedded.

## Rights

Original [licensing status](source/finite/LICENSE_STATUS.md) is preserved. No license has been selected for that source release and this import adds no license grant.
