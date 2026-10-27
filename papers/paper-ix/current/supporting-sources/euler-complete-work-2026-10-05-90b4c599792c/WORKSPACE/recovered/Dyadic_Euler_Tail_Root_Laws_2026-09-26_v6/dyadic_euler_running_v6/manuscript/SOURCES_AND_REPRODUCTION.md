# Sources, files and reproduction

## Classical inputs

[S1] NIST, *Digital Library of Mathematical Functions*, Section 24.10(i), equation 24.10.1. The von Staudt–Clausen denominator theorem supplies the dyadic Bernoulli valuation. <https://dlmf.nist.gov/24.10>

[S2] NIST, *Digital Library of Mathematical Functions*, Section 24.4. Finite Bernoulli expansions, multiplication identities and power sums supply the coefficient identities used in the precision-local Bernoulli evaluator. <https://dlmf.nist.gov/24.4>

[S3] Keith Conrad, *Hensel's Lemma*, Theorem 8.2 and Remark 8.3, printed pages 16–17. These cover restricted-series Hensel lifting and its relation to Weierstrass preparation. <https://kconrad.math.uconn.edu/blurbs/gradnumthy/hensel.pdf>

These references support the classical ingredients, not a priority claim for the specialized Euler-tail deductions. The v5 source review checked the Bernoulli identities and read the relevant Hensel/Weierstrass pages. The specialized proofs and computational certificates are provided in the manuscript and source bundle.

## Bundle layout

| Directory | Contents |
|---|---|
| `manuscript/` | Running Markdown, generated LaTeX, cumulative PDF, and the separate v5 appendix |
| `history/v4/` | Unmodified recovered v4 directory, including all earlier proof notes, code and results |
| `code/` | Reused exact modular engine and new certificate/distribution checkers |
| `results/` | Fresh v4 rerun, new v5 results, whole-ball certificates, logs and manifests |
| `figures/` | Seven plots in PDF and PNG formats with a regeneration script |
| `sources/` | Source-provenance metadata and document-build information |

The top-level release README identifies current proof files and separates mathematical, computational and unresolved claims. No font files are included.

## Scientific reproduction

The core scientific checks use Python's standard library. The plot builder additionally uses Matplotlib. Pandoc and XeLaTeX build the manuscript. All exact scientific assertions use integers, rational numbers or modular residues. Floating point is confined to plotting coordinates and runtime metadata.

From the `code` directory, run the individual checkers with new output filenames. The bounded runner refuses to reuse an existing declared scientific result file, preventing a stale result from masquerading as a completed run.

```text
python rerun_v4_v5.py --output ../results/v4_recheck.json
python check_distribution_v5.py --output ../results/distribution_recheck.json
python check_irregular_v5.py --j 33 --output ../results/j33_recheck.json
```

For size 49, use the retained disjoint intervals so the reproduction does not repeat the recorded oversized runs:

```text
python check_irregular_v5.py --j 49 --delta-start 1 --delta-stop 20 --output ../results/j49_a_recheck.json
python check_irregular_v5.py --j 49 --delta-start 21 --delta-stop 36 --output ../results/j49_b_recheck.json
python check_irregular_v5.py --j 49 --delta-start 37 --delta-stop 40 --output ../results/j49_c1_recheck.json
python check_irregular_v5.py --j 49 --delta-start 41 --delta-stop 44 --output ../results/j49_c2_recheck.json
python check_irregular_v5.py --j 49 --delta-start 45 --delta-stop 48 --output ../results/j49_c3_recheck.json
python check_irregular_v5.py --j 49 --delta-start 49 --delta-stop 52 --output ../results/j49_c4_recheck.json
```

The v2 audit manifests record actual argv, pinned input hashes before and after, hashed scientific outputs, logs, runtime, exit status and resource limits. The document-build report records page counts and rendering checks separately. Scientific output integrity is not proof of a theorem, and a PDF build is not a scientific audit.

## The present stopping point

The mathematical development is cumulative but not closed by declaration. Every first omitted depth has an exact prepared polynomial. Completed atlases give exact root-distance and distribution laws. The regular-wall theorem and finite certificates cover shifted-wall labels through 64. A nonzero resultant gives a finite stopping guarantee.

What remains is an explicit arithmetic classification outside these wall families and a universal answer about possible exact repeated roots of the prepared Euler-tail polynomials. Neither the finite audits nor the new average-precision identities are substitutes for that missing argument.
