# Quadratic-Form Engine / K-COS

Komorebi P. · Final companion edition October 7, 2026

Imported into a private GitHub staging candidate on October 7, 2026. The final companion PDFs, editable sources, figures, formal project, and verification records below are available for review. No new theorem, proof repair, figure change, or formal coverage is introduced by this import.

| Companion | Pages |
|---|---:|
| [Traditional paper](traditional/Quadratic_Form_KCOS_Traditional.pdf) | 85 |
| [Visual guide](visual/Quadratic_Form_KCOS_Visual_Guide.pdf) | 18 |
| [Lean guide](lean/Quadratic_Form_KCOS_Lean_Guide.pdf) | 7 |

The final corrected engine is browsable under [engine](engine/). The packetization v0.1 source was recoverable only inside a nested source ZIP. Its manuscript, two Python modules, figures, and recorded CSVs are now browsable at [source/query-adaptive-v0.1](source/query-adaptive-v0.1/). That historical floating packet implementation remains separate from the corrected final directed backend. The positive directed contract requires a positive spectrum of rank greater than two, admissible positive tilt, nonnegative threshold, and support endpoint above the threshold. The automatic planner handles upper-tail queries above the mean. The verified spectral bridge encloses stored binary64 factors as exact dyadic inputs.

## Source and evidence

- [Selected source](engine/)
- [Lean project](lean/)
- [Original edition reading guide](README_ARCHIVE.md)
- [Final validation and limits](verification/FINAL_VALIDATION.md)
- [Numerical replay and recorded evidence](verification/numerical/README.md)
- [Lean build/audit receipt](lean/verification/BUILD_AUDIT.json)
- [Original reading guide](README_ARCHIVE.md)
- [Import mapping, exact hashes, and omissions](provenance/GITHUB_IMPORT.json)
- [New import identity receipt](verification/GITHUB_IMPORT_CHECK.json)

The delivered October 7, 2026 edition records 58 selected unittest methods, two deep-tail controls, and a Lean build/audit of 26 exact finite-real algebra and enclosure/error-budget theorems plus eight definitions. The 34 declaration audit, successful logs, failed initial attempts, and negative controls are preserved. They are producer evidence from the source edition; this GitHub import did not execute Lean or rerun numerical suites. The Lean project does not formalize Gaussian laws, the infinite COS series, the transcendental interval backend, or the entire Python engine.

Historical files retain their original dates, frozen-series statements, and execution paths. Those statements describe their source snapshot. The central repository catalogue records the current import status.

## Verify and reproduce

From this folder, using Python's standard library:

```sh
python3 scripts/verify_import.py
```

This command verifies only the imported bytes. 
Some original artifacts are deliberately omitted, as individually recorded with their byte hashes. The original edition manifest remains unchanged evidence of the complete archive; its generic checker does not account for these omissions.

Optional numerical replay requires the recorded environment:

```sh
python3 -m pip install -r verification/numerical/requirements.txt
python3 verification/numerical/replay.py --include-controls
```

The replay writes new timestamped evidence. Lean replay uses the pinned Lean `v4.34.0-rc2` and Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Run from `lean`:

```sh
lake update
lake exe cache get
python3 verify.py
```

The verifier covers the build, direct source checks, declaration and axiom audit, and positive/negative controls. Shared mpmath interval precision requires sequential calls for the directed backend. Authoritative enclosure values are outward literal endpoints, while floating summary fields are display values.

Final PDF compilation is documented in the original reading guide and editable companion folders. It requires the stated TeX/fonts and Python packages. No toolchain or third-party build cache is embedded.

## Rights

No project license grant was found in this source package. This import adds no license and retains original attribution and publication records.
