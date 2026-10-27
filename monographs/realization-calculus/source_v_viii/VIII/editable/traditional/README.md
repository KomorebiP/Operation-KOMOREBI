# 10 October 2026 release addendum

This companion retains all mathematical text from the 9 October edition.
The current build resolves installed fonts into a disposable build directory.
It does not download or install dependencies, and no standalone font binaries
are distributed. See `FONT_DEPENDENCIES.json` and the release root
`BUILD_AND_REPLAY.md`. The older build records below remain historical.

The release rechecks the exact source excerpts and body-content sequence.
Pagination within the Lean guide has small line-break changes compared with
the predecessor, while its 94-page count and content are preserved. Current
output hashes belong to `EDITION.json` and `verification/RELEASE_CLOSURE.json`.

---

# Paper VIII modern monograph

This directory contains the authored 9 October 2026 traditional volume. It preserves all seven retrieved mathematical source parts byte for byte, with 85 main numbered records and 56 explicit main proof bodies. The six supplementary mathematical bodies remain complete. The main section and item numbers are unchanged.

The wrapper uses the shared modern monograph profile and bundled relative fonts. Three introductory exact finite examples are followed by the complete manuscript, Appendices A–F, a 32-page worked visual atlas, and the references. Examples are illustrative declared mathematical models, not fresh GPU observations or actual precision-kernel certificates. Four inherited figure presentations were repaired without changing their values or captions; details are recorded separately in the verification report.

## Compile the authored sources

An existing TeX distribution with XeLaTeX and BibTeX is required. No downloads or source regeneration occur during compilation.

```console
python build.py
python map_pages.py
```

`build.py` copies the authored tree into an isolated temporary directory, uses bundled fonts and relative assets, performs four XeLaTeX passes and a BibTeX pass, then writes the resulting PDF and auxiliary records beside this file. The default fixed source date makes this build deterministic within the recorded environment.

```console
python build.py --output-directory /path/to/rebuild
python build.py --check-only
```

The output-directory mode writes products to the selected location. Check-only compiles in isolation without replacing delivered files. The legacy `--assemble` flag compiles these authored sources and does not run the historical assembler.

`map_pages.py` reads the local PDF and auxiliary file to write `canonical_label_to_final.json`, `current_source_records.json`, and the current `evidence/FINAL_PAGE_MAP.json`. Actual PDF page labels and physical page positions are verified separately from named destinations. The final map is consumed by the visual and Lean companions.

## Reproduce the new exact models

```console
python generate_monograph_examples.py
```

Python with Matplotlib and NumPy regenerates the three figure pairs and JSON/CSV records. All model arithmetic is performed with `fractions.Fraction`; conversion to plotting coordinates happens after the checks. The models include an exact Woodbury action and inverse, a finite budget optimum unsupported by any Lagrangian multiplier, and an eight-assignment precision model. Five intentionally false controls are rejected. Independent exact checks are stored in the package verification directory.

## Evidence scope

The inherited formal checkpoint covers 56 finite manuscript-proved items, with 392 named theorem declarations across 40 modules, 66 construction audits, and four separately recorded classical inputs. These counts use different units. This monograph does not report a fresh Lean compilation. Hardware timings remain inherited archived observations with their matching-metadata limitations. Three broader discovery, nonlocal-compilation, and communication targets remain open.

The current preservation and layout evidence is in the package `verification/` directory. `historical_assembly/` retains the prior assembler, builder, map script, and superseded presentation reports. They describe the retrieved edition and are not the current monograph replay contract. They must not be substituted for `build.py` or the final page map.
