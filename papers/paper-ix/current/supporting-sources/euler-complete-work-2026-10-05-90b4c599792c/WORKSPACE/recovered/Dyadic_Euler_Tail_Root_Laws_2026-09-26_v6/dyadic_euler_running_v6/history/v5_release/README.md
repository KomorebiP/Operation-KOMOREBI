# Dyadic Euler tails — running research record, version 5

Komorebi P. · Operation Komorebi · 26 September 2026

## Read first

- `manuscript/Dyadic_Euler_Tails_Running_v5.pdf`: the 58-page cumulative manuscript. It includes a notation guide, correction register, reconstructed starting mathematics, the full recovered v1–v4 proof notes, and Continuation V.
- `manuscript/Dyadic_Euler_Tails_Appendix_v5.pdf`: the separate 17-page current continuation and reproduction appendix.
- The matching `.md` and `.tex` files are editable sources. `manuscript/CONTINUATION_05.md` is the new proof note alone.

This is a cumulative research record, not a claim that every arbitrary-depth problem is solved. Earlier notes are preserved with historical-status notices. Later corrections take precedence over earlier interpretations. Do not count inherited execution records as newly executed evidence.

## New results

1. If the prepared monic polynomial has nonzero resultant with its derivative and resultant valuation D, the constant-or-simple-root subdivision is certified to terminate by binary depth D+1 with coefficient precision at least 2D+2. This is conditional on a nonzero resultant; no universal squarefreeness theorem is asserted.
2. A completed valuation atlas determines an exact rational valuation generating function and exact Haar survival probabilities. The saturated five-root family has residual survival probability 24/2^h for h at least six.
3. A completely separated shifted wall at r=2^L-j has exact Haar mean full-tail valuation 4·2^L. This is an average over dyadic offsets, not a stronger worst-case modulus and not an assertion about uncapped integer-prefix averages.
4. Whole-ball coefficient certificates resolve the next irregular labels, j=33 and j=49. Together with the regular-wall theorem and the inherited j=17 certificates, the shifted-wall classification now covers labels 1 through 64 at every valid scale.
5. General monotone root emergence is false: at j=33, distances 26, 27 and 28 have respectively one, zero and two dyadic roots.

## Evidence boundary

The general results have prose proofs. Finite irregular-wall classifications are computer-assisted: their exact coefficient certificates cover entire dyadic balls, and the proved coefficient cutoff controls uncomputed terms. Sampled value comparisons independently check implementation paths but are not substituted for those certificates.

No Lean compilation or historical-priority assessment was performed. No universal claim about repeated roots at arbitrary first omitted depth is made. A zero residue at finite precision is only a valuation lower bound. The repeated-root safety test deliberately keeps its unresolved branch unresolved.

The optimal uniform tail exponent remains 4M+3. The new results concern exact row dependence, root geometry, distributions and stopping certificates, not a replacement of that optimal universal bound.

## Files

- `history/v4/`: unmodified recovered v4 archive contents, including earlier proofs, original code, results and integrity records.
- `code/`: exact standard-library arithmetic, new certificates and audits, figure regeneration and document build scripts.
- `results/`: fresh v4 reruns, v5 scientific outputs, whole-ball atlases, resource/provenance manifests, logs, failure record and PDF quality checks.
- `figures/`: vector PDF and raster PNG figures. The numerical information is computed exactly before plotting.
- `sources/`: classical-source provenance and build environment notes.
- `CLAIM_STATUS.json`: a compact claim and evidence index.

The combined `IRREGULAR_49_V5.json` is a convenience merge of six disjoint successful runs, not an additional independent experiment. The bounded rerun of j=33 is the provenance-backed copy. Original and bounded v4 reruns agree in their mathematical results; timings naturally differ.

Two oversized size-49 runs were interrupted before producing their declared scientific result files. They are not counted as passes. The successful intervals are 1–20, 21–36, 37–40, 41–44, 45–48, and 49–52. See `results/DEVELOPMENT_FAILURES_V5.md`.

## Verify integrity

From this directory:

```text
python verify_release.py
```

This verifies packaged bytes, not mathematical truth. The nine new version-2 audit manifests were also validated with input and output hashes. To revalidate one:

```text
python code/support/validate_manifest.py results/MANIFEST_DISTRIBUTION.json --root .
```

The original v4 integrity ledger remains inside the historical directory. That original ledger covers 42 files and was verified before the continuation.

## Reproduce exact checks

From `code/`, choose new output names:

```text
python rerun_v4_v5.py --output ../results/v4_recheck.json
python check_distribution_v5.py --output ../results/distribution_recheck.json
python check_irregular_v5.py --j 33 --output ../results/j33_recheck.json
python check_irregular_v5.py --j 49 --delta-start 1 --delta-stop 20 --output ../results/j49_a_recheck.json
python check_irregular_v5.py --j 49 --delta-start 21 --delta-stop 36 --output ../results/j49_b_recheck.json
python check_irregular_v5.py --j 49 --delta-start 37 --delta-stop 40 --output ../results/j49_c1_recheck.json
python check_irregular_v5.py --j 49 --delta-start 41 --delta-stop 44 --output ../results/j49_c2_recheck.json
python check_irregular_v5.py --j 49 --delta-start 45 --delta-stop 48 --output ../results/j49_c3_recheck.json
python check_irregular_v5.py --j 49 --delta-start 49 --delta-stop 52 --output ../results/j49_c4_recheck.json
```

The optional `run_audit_v5.py` wrapper additionally uses POSIX resource limits. It refuses an existing declared result path. Its retained manifests contain the actual commands and effective limits. The core arithmetic does not require that wrapper or third-party numerical packages.

## Rebuild documents and figures

From the release root:

```text
python code/make_figures_v5.py
python code/build_running_document_v5.py
```

Figure generation requires Matplotlib. Document generation requires Pandoc, XeLaTeX and the standard LaTeX packages in the source preamble, plus Latin Modern and DejaVu Sans Mono fonts installed locally. No font files are redistributed.

The Markdown is the editable manuscript source. The build keeps recovered historical source files unchanged and makes only typesetting adaptations for URLs, long numeric residues and page layout. Regenerating scientific results or PDFs changes their hashes, so preserve this release and write new versions to new paths.

## Continue the record

Append a new numbered continuation, update the claim/correction register, retain previous proof notes and audit outputs, and create a new release ledger. An extension should identify the precise theorem or counterexample it adds and state any unresolved precision or multiplicity branch. There is no automatic or background update mechanism.
