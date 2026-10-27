# Signal Reconstruction

**Komorebi P. · Operation Komorebi / Realization Calculus · 2026-10-06**

The publication set develops signal reconstruction through packet coordinates, transfer blocks, polyphase sampling, sparse singularity models, unknown-edge recovery and self-calibration. The mathematical ingredients remain connected to Fourier analysis, Prony reconstruction, finite-rate-of-innovation sampling, sparse uniqueness and classical perturbation theory. The contribution is the assembled realization framework and the explicit reconstruction contracts developed here; the release does not assert that every ingredient is historically new.

The three companion documents are:

- `traditional/Signal_Reconstruction_Traditional.pdf`: precise hypotheses, statements, proofs and limitations.
- `visual/Signal_Reconstruction_Visual_Guide.pdf`: reproducible mathematical figures and worked examples.
- `lean/Signal_Reconstruction_Lean_Guide.pdf`: related existing formal results, exact source correspondence and the remaining formalization obligations.

**The `.md` files are included.** Each companion has an editable Markdown version and TeX source. The bundle also includes figure-generation code, claim concordances, preserved earlier manuscripts and programs, bounded computational checks, provenance and review records. A machine-native companion is deferred.

## Reading the evidence

The current traditional manuscript and its claim concordance state the publication's mathematical claims. The older materials under `sources/` are preserved evidence, and can contain statements corrected in this edition. Historical benchmark results are distinguished from fresh bounded executions. Numerical experiments do not certify untested ranges or universal claims.

Related Paper V formal sources are under `related_formal/paper_v/`. They support packet and known-edge infrastructure. They do not constitute a Lean formalization of the present unknown-edge and self-calibration reconstruction claims. Their build records are historical; there is no fresh Signal Lean certificate in this release. See the Lean guide and `verification/FRESH_LEAN_STATUS.json` for the exact scope.

The latest Paper V final archive available for this task was malformed despite matching its advertised length. Its failure is recorded in `provenance/PAPER_V_FINAL_ARCHIVE_FAILURE.json`. A separately validated earlier v1.1.0 checkpoint supplies the related formal sources, with exact member and payload hashes in `provenance/PAPER_V_CHECKED_CHECKPOINT.json`. The malformed archive has not been silently repaired or substituted as a verified final edition.

## Corrections and boundaries

The release corrects the older periodic mean-zero edge-location L1 bound, handles sparse-injectivity boundary cases, states separation-dependent stability conditions, and distinguishes a conditional root-perturbation theorem from an available-data certificate. The corrected mathematical statements and their proofs appear in the traditional manuscript; the inherited source association map identifies their antecedents.

Finite image and infinite-packet programs are experimental implementations. In particular, the default packet refit is regularized, pixel-residual completion uses the full reference image, and clipping is nonlinear. These facts limit the interpretation of those experiments. The older per-method runtime table has a key mismatch; its zero cells do not support timing comparisons.

## Rebuilding and verifying

Run `python3 build_release.py` from any working directory with pdfLaTeX installed. It performs three passes for each PDF with a fixed publication date. `--only traditional`, `--only visual` and `--only lean` select one document. Figure-generation and bounded computation instructions are included with the corresponding source and verification files.

Run `python3 audit_release.py` with `requirements-publication.txt` installed to check the current publication integration, source hashes, concordances, PDF bounds and evidence records. This audit checks publication consistency; it is not a proof checker. Run `python3 package_release.py` to create the source ZIP and verify every indexed payload hash and ZIP CRC.

The publication sources can be regenerated with `traditional/assemble_traditional.py`, `visual/build_guide.py` and `lean/build_lean_guide.py`, followed by `build_release.py`. Traditional Markdown conversion uses Pandoc. The visual generator and scientific controls use the separately pinned `requirements-verification.txt`. Regeneration can overwrite the corresponding generated files; edit their canonical content inputs or builders when maintaining parallel formats.

`BUNDLE_INDEX.json` and `SHA256SUMS.txt` index the release payloads, excluding the two index files themselves. Compilation caches and local preview images are excluded from the distributable archive. No new license or publication to an external repository is asserted by this release.
