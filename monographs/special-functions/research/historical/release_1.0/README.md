# Special Function Discovery v1.0

Author attribution: **Komorebi P.**  
Research checkpoint: **SF-DISCOVERY-100**, 2026-10-08 UTC.

This release combines a 75-page research monograph, an atlas of 18 mathematical figures, five proof appendices, an exact sequence and polyphase API, and reproducible computational evidence. Read [main.pdf](main.pdf) for the exposition and [CLOSEOUT.md](CLOSEOUT.md) for the precise completed and open claims.

## Current mathematical status

The files in `routes/` intentionally preserve the SF-DISCOVERY-001 / v0.1 baseline, including its then-open questions. The five chapters in `new_results/` give the current extensions and close selected gaps. For example, the old orbit route's global-continuation disclaimer records the earlier state; [spectral_continuation.md](new_results/spectral_continuation.md) now proves continuation for that family and its nonnegative real shifts. Use the release status in [CLOSEOUT.md](CLOSEOUT.md), rather than an old route paragraph in isolation.

The new proofs establish positive lower dilation type and quantitative tap continuity; exact arithmetic parameter recovery and its finite-data limitations; the finite-prime positivity domain and explicit negative-atom detectors; orbit-zeta continuation, trace values and shifted regularized products; and integer coefficient, root-filter and polyphase identities. [The independent audit](evidence/v1_independent_audit.md) found these claims proved as written under their stated domains.

Historical priority remains unresolved for the candidate extensions. The one-dilation equation is an authenticated known baseline from Méndez (2024). Laplace uniqueness, orthogonal-polynomial methods, Mittag-Leffler seeds and spectral Mellin continuation have established antecedents. The proofs establish mathematical statements; the bounded literature comparisons do not establish global novelty.

## Package map

| Path | Purpose |
|---|---|
| `main.pdf`, `main.tex`, `sections/` | Monograph and LaTeX source |
| `figures/`, `build_*figures.py` and other figure builders | Vector figures, PNG previews and generators |
| `routes/`, `historical/` | Preserved v0.1 proofs, audits and history |
| `new_results/` | Five current proof chapters |
| `family_lab.py`, `examples/` | Exact API and 18-row JSON/CSV catalog |
| `checks/` | Ten finite check scripts and aggregate driver |
| `evidence/v1_independent_audit.md` | Mathematical and API audit with final pins |
| `evidence/release-run-001/` | Preserved bounded run, full reports, snapshots and manifest |
| `evidence/release_summary.json`, `evidence/release_summary.md` | Final counts and validator status |
| `requirements.txt`, `TARGET_CONTRACT.json` | Recorded dependencies and release scope |

## Exact sequence and filter API

The API uses Python's standard library and exact integer or `Fraction` arithmetic. It computes odd derivatives and ordinary Taylor coefficients, bivariate coefficient polynomials and finite feedback banks. Its filter operations include root-filter sections, decimated phase lanes, ordinary FIR taps, Hurwitz products, EGF derivative/antiderivative shifts, and carry-preserving polyphase matrices.

```bash
python family_lab.py coefficients --q 1/4 --r 3/4 --n 8
python family_lab.py catalog --n 12 --output-dir examples/local-catalog
```

The shipped catalog has 18 rows through index 12 and records the normalization, denominator clearing and analytic/formal scope of each row. Integer sequences above unit scale can have radius zero; the catalog does not label every formal sequence an analytic germ. It supplies candidates for sequence comparison, with no OEIS accession or priority claim. Definitions and examples are in [sequence_polyphase.md](new_results/sequence_polyphase.md).

## Run the finite suite without Mathbox

The aggregate suite requires Python with assertions enabled and `mpmath==1.3.0`. Other packages in `requirements.txt` support the figures, manuscript tooling or review. In an environment with mpmath installed, run the following from this directory. Choose a fresh output name:

```bash
python - <<'PY'
from pathlib import Path
import subprocess
import sys
import mpmath

root = Path.cwd()
output = Path("evidence/local-run-001")
(root / output).mkdir()  # deliberately fails if this run already exists
packages = Path(mpmath.__file__).resolve().parent.parent
subprocess.run([
    sys.executable, "checks/run_release.py",
    "--output-dir", str(output),
    "--dependencies", str(packages),
    "--script-timeout", "300",
], cwd=root, check=True)
PY
```

The parser requires `--output-dir` and `--dependencies`; the output directory must already exist and contain no earlier aggregate summary or snapshot. The dependency argument names the directory containing the mpmath package. Do not use Python `-O`. This standalone command preserves full reports and snapshots and applies the per-script wall timeout. The bounded manifest run additionally enforces resource caps and validates artifact hashes; its complete reproduction instructions are in [checks/RELEASE_CHECKS.md](checks/RELEASE_CHECKS.md).

The preserved release run passed **19,871 exact assertion statements** and **5,576 numerical assertion statements**. The exact total comprises 19,331 principal checks and 540 separately recorded inverse helpers. All ten scripts passed, all 25 pinned inputs remained unchanged, and the manifest validator passed. Numerical comparisons use ordinary high precision and are not interval certificates. Universal analytic conclusions rely on the proofs.

## Build the monograph

Install Pandoc and a LaTeX distribution with `pdflatex`, Latin Modern, `hyperref`,
`xurl`, and the standard AMS packages. From this directory run:

```bash
python build_manuscript.py
```

The builder converts the five canonical Markdown proofs to LaTeX, applies
typography-only line breaking and heading cleanup, and runs LaTeX three times
for the linked contents. Edit the curated `sections/*.tex` files or the canonical
Markdown proofs; regenerated `*_full.tex` files are build outputs. The separate
manuscript record is `evidence/manuscript_build.json`. All 18 vector figures and
their Python generators are included.

## Corrections and retained history

Independent review reproduced two invalid-input API defects: fractional residues and a zero phase base were accepted. Both now raise `ValueError`, with passing regression checks. Two draft sequence integers were corrected against the exact catalog. Earlier author history, including a failed absolute determinant-residual criterion and its scale-normalized correction, remains in the full evidence. The current release run has no failures. [CHANGELOG.md](CHANGELOG.md) records the changes; these histories are retained rather than erased.

The archive does not bundle external Python dependencies or third-party papers. Figure builders and LaTeX source are included; PDF bytes may vary with timestamps, fonts and build environments. Computational provenance covers the declared proof/check inputs, while manuscript and figure-build records are separate.
