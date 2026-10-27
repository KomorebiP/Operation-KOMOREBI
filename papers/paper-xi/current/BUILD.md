# Building and verifying Paper XI 1.1.0

## Reader build

Install Python 3.10 or newer with PyMuPDF, XeLaTeX, pdfLaTeX, BibTeX, URW P052/Nimbus Sans OTF fonts and DejaVu fonts. The source uses ordinary TeX packages recorded in the build inputs. The builder discovers the installed URW font directory with `fc-match`; alternatively pass `--font-dir /absolute/font/directory`.

From the extracted release root, run:

```sh
python3 tools/build_readers.py --output /absolute/new/paperxi-build
```

The output must be outside the release and initially empty. The builder stages source copies, uses TeX without shell escape, runs the required bibliography and reference passes, resolves companion links to actual destinations, and writes three rebuilt PDFs plus the two preserved research companions. It records each source-tree fingerprint, command, local input file, diagnostic, page count and PDF hash. It does not run a Lean compiler or regenerate figures.

For separately scheduled compilation, use `--stage traditional`, `--stage visual_guide`, `--stage lean_guide`, and finally `--stage assemble`, all with the same output directory. A stage refuses reuse of an existing compilation receipt. The `https://komorebi.invalid/b07/` strings in TeX are internal route keys inherited from the first synchronized edition. The assembler resolves them to local PDF actions; they are not public URLs or unresolved links in the delivered readers.

Keep all five final PDFs together with their delivered filenames. The resolved companion routes for the three rebuilt readers are in `evidence/release_1_1/BUILD_RECORD.json`; the package verifier separately inspects actions in all five PDFs. Reproduction promises matched sources and checked outputs, not byte-identical PDFs on every TeX/font/runtime installation.

## Lean replay

The portable project is under `formalization/`. Read its `README.md` and exact check contract before running the provided scripts. It retains the selected source hashes, the Lean toolchain pin and all Mathlib dependency pins. Lean runtime binaries, external dependency caches and generated objects are intentionally not bundled. A fresh local environment must obtain the pinned public dependencies before replay.

The 423 selected modules, recovered terminal target and one-candidate supplement have separate result groups. Compilation from fresh Paper XI outputs and the owning-module axiom audit have separate receipts. An accepted theorem proves its stated implication; imported arithmetic interfaces are not silently instantiated. The external Mathlib cache is not a claim of recompiling all Mathlib sources.

## Package verification

The final root `MANIFEST.json` lists every other packaged file with its length and SHA-256. Run the portable verifier with output outside the release:

```sh
python3 tools/verify_release.py --root /absolute/extracted/release --output /absolute/new/verification-report.json
```

The verifier checks the exact file inventory, source and excerpt hashes, fresh reader build fingerprints, PDF link targets and final diagnostics. Its lexical placeholder scan supplements the executed axiom audit; it does not replace it. Consult `verification/` for the named executed scopes and `evidence/release_1_1/VISUAL_REVIEW.json` for the rendering review.

## Earlier evidence and bounded computation

`historical/Paper_XI_Source_and_Evidence_v1.0.0_2026-10-10.zip` preserves the complete recovered predecessor tree. Its own integrity manifest was freshly verified before work began. The six selected inherited replay suites passed 117 methods in this session; the receipts are under `verification/baseline_replay/`. Their tested ranges and contracts remain those of the original suites. These bounded computations do not prove an arbitrary arithmetic realization theorem.

Historical source paths and environment paths inside that archive remain provenance records, not current working directories. Extract the archive separately to rerun its existing `tools/verify_package.py` and `tools/replay_release.py`. Do not rewrite old receipts to represent a new run.
