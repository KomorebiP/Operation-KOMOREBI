# Special Function Discovery 1.1

**Komorebi P. · SF-DISCOVERY-110 · 9 October 2026**

Read [main.pdf](main.pdf) for the integrated research monograph and [visual_guide.pdf](visual_guide.pdf) for the mainly visual companion, *What Finite Observations Can Miss*. The edition contains five worked function families, 32 computed figures, ten technical appendices, and exact sequence, polyphase, and tap laboratories. Fourteen figures and the standalone guide are new in 1.1.

This file is the current entry point. [CLOSEOUT.md](CLOSEOUT.md) records the precise mathematical outcome and open questions. The current scope is [research_v11/TARGET_CONTRACT.json](research_v11/TARGET_CONTRACT.json). The root `TARGET_CONTRACT.json` remains the dated 1.0 contract because its original computation pins are preserved.

## What 1.1 adds

For four positive real strict contractions, the coupled system

\[
U'=1+U(qz)V(rz),\qquad V'=1+U(az)V(bz),\qquad U(0)=V(0)=0
\]

has a unique normalized entire pair. Both orders and lower orders equal the positive root of

\[
(1-q^\rho)(1-b^\rho)=(ar)^\rho.
\]

Both lower and upper type vectors are positive multiples of the corresponding Perron right eigenvector. The components are amplitude/argument rescalings of each other exactly on `q=b` or `qb=ar`. Outside those surfaces, their ordinary coefficients through degree seven identify all four ordered scales. The independent mathematical audit found these statements proved as written under the stated domains. This is not a claim of historical priority or machine-checked formalization.

The resolution atlas gives quantitative examples of three different mechanisms: a weak positive tap that changes order while remaining close on a disk, a large excluded prime hidden within a prescribed compact error, and a negative sieve atom missed by every polynomial through degree four but detected by an explicit degree-seven polynomial. Degrees five and six remain undecided. The radius bound is sufficient, not a minimum.

## Source map

| Path | Purpose |
|---|---|
| `main.tex`, `sections/`, `sections_v11/` | Integrated monograph and curated visual pages |
| `visual_guide.tex` | Standalone visual companion |
| `research_v11/` | Current exact proofs, independent growth derivation, and bounded literature comparison |
| `coupled_lab.py`, `coupled_inverse.py` | Exact coupled coefficients, evaluation certificates, and parameter inverse |
| `family_lab.py`, `new_results/sequence_polyphase.md` | Inherited sequence, root-filter, polyphase and tap machinery |
| `examples/` | Original 18-row catalog and new seven-row coupled catalog |
| `figures/`, `figures_v11/` | 18 inherited and 14 new vector figures with PNG previews |
| `evidence/v11/independent_math_audit.md` | Mathematical review with exact source revisions |
| `evidence/v11/release_run_review.json` | Current finite-run review and manifest locator |
| `evidence/v11/final_text_review.json`, `final_visual_review.json` | Final text and page review records, both under `evidence/v11/` |
| `checks/run_v11.py`, `checks/release_contract_v11.json` | Fresh-snapshot reproduction and declared finite scope |
| `historical/release_1.0/` | Dated 1.0 entry points, publication wrapper, and complete original source archive |
| `package_manifest.json`, `SHA256SUMS` | Current packaged file inventory and hashes |

All mathematical working Markdown notes created for this extension are included. Temporary renders and downloaded helper tools are excluded. The archive bundles neither external Python dependencies nor third-party papers.

## Reproduce the new finite computations

Use Python with assertions enabled. The three exact/numeric check scripts use the standard library. Figure reproduction also requires NumPy, Matplotlib, mpmath, and Pillow; the versions used are recorded in `checks/release_contract_v11.json`. The inherited `requirements.txt` records the 1.0 environment. No network access is needed once dependencies are installed.

From this directory, choose an output path that does not yet exist:

```bash
python3 checks/run_v11.py --output-dir evidence/v11/local-run-001
```

The wrapper preserves inputs in a fresh snapshot, runs the three new suites, regenerates all fourteen figure pairs, and records their hashes. The preserved bounded runs additionally use the computation-audit runner's process and output limits. Their complete invocations and environment are recorded in their manifests.

The current new suite passes **5,272 exact assertion statements**, **26 numerical assertion statements**, and **13 separately counted operational guards**. All fourteen regenerated PNGs match the publication figures. These counts exclude the unchanged 1.0 suite, whose preserved run passed **19,871 exact** and **5,576 numerical** assertion statements. The original suite was not rerun for this extension.

Exact rational certificates are distinguished from ordinary floating approximations. Finite checks validate their recorded ranges and implementations. Universal mathematical statements rely on the audited proofs.

## Use the exact APIs

```python
from fractions import Fraction as F
from coupled_lab import coupled_odd_derivatives, certified_evaluation

scales = (F(1,5), F(2,5), F(3,5), F(7,10))
u, v = coupled_odd_derivatives(*scales, last=12)
certificate = certified_evaluation(*scales, x=F(1), last=30,
                                   outer_radius=F(2))
```

`coupled_inverse.py` accepts six ordinary Taylor coefficients, not derivatives. Its generic inverse rejects the reduction locus. `recover_squared_scales` returns exact rational squared scales when available; `recover_rational_scales` additionally requires rational positive square roots. The mathematical uniqueness theorem covers all positive real strict contractions outside the reduction locus.

Catalog rows carry their normalization, denominator clearing, and analytic/formal scope. Signed or integer scales outside the strict contraction domain are not automatically entire functions. The catalogs supply reproducible integer sequences for comparison; they make no OEIS accession or priority claim.

## Rebuild the reading editions

Install Pandoc and a LaTeX distribution with `pdflatex`, the standard AMS packages, Palatino/PSNFSS, Latin Modern, `microtype`, `hyperref`, and `xurl`. Then run:

```bash
python3 build_v11.py
```

This converts the five new canonical proof/laboratory chapters and compiles both editions with three LaTeX passes. The inherited generated appendices A–E are included. Edit curated visual pages or canonical Markdown proofs; `*_full.tex` files are generated outputs. The alternative coupled growth derivation remains available in source in addition to the printed proof. Manuscript hashes and warning status are recorded separately from mathematical evidence.

`python3 build_package.py` packages a final reviewed build and verifies every ZIP member. Rebuilding a PDF changes its hash, so its final review record must match before packaging. PDF bytes can vary with timestamps, fonts, and tools even when the mathematics is unchanged.

## History and limitations

The original 1.0 archive is preserved byte-for-byte, including its dated target, evidence, publication edition, and earlier failures. Earlier route files can contain questions subsequently resolved; consult this entry point and the current closeout for status. The new audit corrected an overly broad initial-segment hypothesis in the general detector theorem. Its worked degree-seven certificate was already valid. A figure-label build error and an inactive dependency fallback were repaired and retained in the evidence history.

Ordinary coupled type limits, angular growth and zero geometry, stable inversion near the reduction surfaces, optimal detector degree, and historical priority remain open. The literature note records a bounded comparison with six primary sources and distinguishes known mechanisms from the exact results proved here.
