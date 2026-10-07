# Projector-Resolved Seed Calculus I: Typed Operator Systems, Seed Rank, and Exact Packet Coordinates

Komorebi P. · Final companion edition October 5, 2026

Imported into a private GitHub staging candidate on October 7, 2026. The final companion PDFs, editable sources, figures, formal project, and verification records below are available for review. No new theorem, proof repair, figure change, or formal coverage is introduced by this import.

| Companion | Pages |
|---|---:|
| [Traditional paper](papers/Paper_I_Traditional_Final.pdf) | 93 |
| [Lean guide](papers/Paper_I_Lean_Guide_Final.pdf) | 37 |
| [Machine-native companion](papers/Paper_I_Machine_Native_Final.pdf) | 94 |

The integrated traditional paper includes the visual atlas. The operative machine runtime is [source/machine_v1.0.1](source/machine_v1.0.1/); [v1.0.0](source/machine_v1.0.0/) remains a historical predecessor. The runtime implements six exact finite actions and two profile gates. Its transport PASS does not establish target hypotheses or inspect all transitive dependencies.

## Source and evidence

- [Selected source](source/traditional_v1.3.1/)
- [Lean project](source/traditional_v1.3.1/formalization/lean/)
- [Original edition reading guide](README.txt)
- [Edition summary](RELEASE_SUMMARY.json)
- [Companion crosswalk](COMPANION_CROSSWALK.json)
- [Bounded mathematical audit](verification/mathematical_audit/Paper_I_scoped_mathematical_audit.md)
- [Preserved formal project guidance](source/traditional_v1.3.1/formalization/lean/README.md)
- [Import mapping, exact hashes, and omissions](provenance/GITHUB_IMPORT.json)
- [New import identity receipt](verification/GITHUB_IMPORT_CHECK.json)

The delivered edition records 33 Python tests and the machine release gate, exact fixtures, and nonzero-packet regressions. Its Lean guide documents the 35-row scoped formal contract and 84 mapped targets. Those edition checks are preserved evidence. No fresh Lean compilation was performed for that companion edition or this GitHub import. The expanded written proofs, finite computational tests, contract rows, and mapped declarations are distinct evidence categories.

Historical files retain their original dates, frozen-series statements, and execution paths. Those statements describe their source snapshot. The central repository catalogue records the current import status.

## Verify and reproduce

From this folder, using Python's standard library:

```sh
python3 scripts/verify_import.py
```

This command verifies only the imported bytes. 
Some original artifacts are deliberately omitted, as individually recorded with their byte hashes. The original edition manifest remains unchanged evidence of the complete archive; its generic checker does not account for these omissions.

```sh
cd source/machine_v1.0.1
python3 runtime/verify_release.py
python3 runtime/exact_fixture_suite.py
python3 runtime/nonzero_packet_regression.py
```

The machine checks need the component's documented dependencies. The original traditional distribution checker expects its omitted predecessor ZIP; use this import's identity checker for the present distribution. For a compatible pinned Lean installation, run from `source/traditional_v1.3.1/formalization/lean`:

```sh
lake --wfail build
lake env lean -DwarningAsError=true KomorebiVerification/KernelAudit.lean
```

These commands do not replace the complete fresh-object, map, and control procedure documented in the original formal README.

Final PDF compilation is documented in the original reading guide and editable companion folders. It requires the stated TeX/fonts and Python packages. No toolchain or third-party build cache is embedded.

## Rights

Original [licensing status](source/traditional_v1.3.1/LICENSE_STATUS.md) is preserved. No license has been selected for that source release and this import adds no license grant.
