# Certified Bayesian Inference

**Packet Updates, Posterior Guarantees, and Arithmetic Certificates**  
Author: **Komorebi P.**  
Publication edition 1.0, based on Certified Inference Core 1.0.0.

This set presents the completed single-observation Gaussian inference contract through a traditional paper, an extended visual guide, and a source-based Lean companion. The canonical program is `Komorebi.CachedPosterior.runCached`.

## Read the set

| File or directory | Contents |
|---|---|
| `output/Certified_Bayesian_Traditional_Final.pdf` | Model semantics, posterior error certificate, exact selective solver, arithmetic, examples, and release boundaries |
| `output/Certified_Bayesian_Visual_Guide_Final.pdf` | A visual route through both complete examples, packet updates, singular geometry, convergence, interval arithmetic, and counterexamples |
| `output/Certified_Bayesian_Lean_Companion_Final.pdf` | Formal interfaces, theorem dependencies, 94 source-matched excerpts, and reproduction guidance |
| `manuscripts/` | Editable LaTeX sources for all three documents |
| `figures/` | Twenty Python-generated figures, each supplied as PDF and PNG |
| `scripts/` | Exact example verification, source inventory, figure generation, PDF build, and layout validation |
| `reviews/` | Fresh bounded checks, source maps, independent review, build records, and PDF inspection records |
| `inputs/FD_Certified_Inference_Core_v1.0.0_Checked.zip` | The original checked source archive, preserved intact |

The Lean companion's 94 excerpts comprise 47 definitions and 47 complete proofs. The source inventory contains 117 active modules and 543 named theorem/lemma declarations. These counts include supporting results and explicit instance certificates.

## Closed mathematical scope

Inputs are finite-dimensional exact rational factor-coded data with

- a prior `P = L Lᵀ`, allowing singular priors;
- observation noise `R = N Nᵀ + sigma I` with `sigma > 0`;
- a rectangular observation operator when required;
- fixed complete, self-adjoint, mutually orthogonal rational packet families;
- an output-label seed and a finite scan covering every output label;
- positive rational posterior tolerance `epsilon` and output-radius tolerance `delta`.

The exact selective solver preserves cached packet residuals and energies, produces the same gains as the recomputed greedy trajectory, and has computable finite iteration fuel. After exact-score search reaches its verification margin, independent outward-rounded dyadic certification supplies the posterior Wasserstein guarantee. Computed output precision supplies mean and covariance intervals for the same Joseph Gaussian at the returned gain.

The posterior is the explicit Gaussian kernel version established by the Bayesian semantics. Its conditional interpretation follows from disintegration and almost-everywhere agreement with canonical versions. The result does not assert uniqueness of arbitrary pointwise conditional versions on null observations.

The parameter intervals enclose the certified approximation's parameters. Their centers do not define a separately certified Gaussian, and `delta` is not an exact-posterior coordinate error bound. A separate completed branch performs genuinely rounded full-gain updates with a perturbation bound. Rounded selective caching requires an additional error invariant.

## Verification status

| Evidence | Status and scope |
|---|---|
| Archived Lean compilation | The preserved Core receipt records successful builds for all 117 active modules and axiom reports for all 543 named theorem/lemma declarations |
| Fresh source and receipt inventory | Source hashes, archived attempt snapshots and logs, recorded dependency-output relationships, declaration locations, axiom coverage, and all publication excerpts were checked |
| Fresh exact publication examples | 236 exact `Fraction` assertions passed, including both complete cached runs and the rounded-cache/covariance-center counterexamples |
| Fresh cache diagnostics | 1,068 bounded assertions passed |
| Fresh output diagnostics | 398 bounded assertions passed |
| Fresh Lean compilation | **Not run: the pinned Lean runtime was unavailable in this publication session** |
| Archived compiled payloads | No `.olean` files are included in the source archive; receipt hashes can be compared, but absent compiled payloads could not be rehashed here |

The fresh example run checked that all 940 baseline files remained unchanged. The baseline manifest covers 939 files. Fresh finite Python checks supplement the formal record; they are not universal proofs, a fresh Lean kernel run, or a universal Python/parser-to-Lean refinement theorem. The axiom union is `Classical.choice`, `Quot.sound`, and `propext`.

See `reviews/lean_inventory.json`, `reviews/exact_example_results.json`, the two diagnostic JSON files, and the independent publication audit for the detailed evidence. Build and PDF validation reports record document checks separately from mathematical verification.

## Rebuild the publication

Run commands from the directory containing this README. Python 3.12 was used for publication production. The packages and versions are listed in `requirements-publication.txt`. Install those packages in your chosen Python environment before rebuilding. The formal reference tools themselves use Python's standard library.

The original source ZIP has SHA-256:

```text
844ae280ea4be7e7c25906e00733f0130996b32aa110c53951df00f8c18fa488
```

If the extracted source directory is absent, restore it from the unchanged archive:

```bash
python3 -m zipfile -e inputs/FD_Certified_Inference_Core_v1.0.0_Checked.zip source
```

This creates `source/FD_Certified_Inference_Core_v1.0.0_Checked`. That path is the default used by the publication scripts. Regenerate checks and figures before building the documents:

```bash
python3 scripts/verify_publication_examples.py --output reviews/exact_example_results.json
python3 scripts/lean_inventory.py
python3 scripts/bayes_figures.py
python3 scripts/build_publication.py
python3 scripts/validate_publication.py
```

The example script runs the two bounded source diagnostic programs and writes their results beside the requested report. It does not compile Lean. The inventory is read-only with respect to original source and archived evidence. Figure generation consumes the exact example report and the preserved archived benchmark report. Gaussian contours and ellipse rendering are numerical illustrations of exact rational inputs, rather than interval-certified plotting geometry. Benchmark panels show archived measurements, not newly measured timing results.

PDF building requires a system TeX installation exposing `pdflatex`, with the packages used in `manuscripts/common.tex`, including Latin Modern fonts, `microtype`, `amsmath`, `amsthm`, `mathtools`, `graphicx`, `booktabs`, `longtable`, `tabularx`, `enumitem`, `fancyhdr`, `lastpage`, `listings`, `float`, `xurl`, and `hyperref`. TeX is a separate system dependency and is not installed by the Python requirements file.

The builder runs three passes for each PDF and preserves logs. To rebuild one document, use `--documents main`, `--documents visual`, or `--documents lean`. The validator checks text bounds, internal link targets, and replacement characters, then renders page previews and contact sheets in `tmp/pdf_review`. Its structural checks complement human page inspection.

`scripts/author_lean_companion.py` records the original source-based companion authoring route. Normal PDF reproduction uses the included finalized `manuscripts/lean.tex`; regenerating the authored manuscript is not required for the commands above.

`scripts/package_publication.py` assembles the complete ZIP in the parent directory. It checks that final PDF and manuscript hashes agree with their review records, verifies the original archive and figure hashes, and validates every ZIP payload against `PACKAGE_MANIFEST.json`. The manifest covers the payload files; it excludes its own self-hash. A changed manuscript or regenerated figure/PDF requires an updated review before packaging. Historical absolute paths in audit manifests describe the recorded session, while rebuild scripts locate their inputs relative to this directory.

## Rebuild the formal source separately

The large portable runtime is external to this publication set. Restoration metadata is retained inside the original source archive under `RUNTIME_METADATA/`. The pinned environment is:

| Component | Pin |
|---|---|
| Lean | `4.34.0-rc2` |
| Lean commit | `6a10ac8c22beadecabdbb0919c2b50214762f91d` |
| Mathlib commit | `aeb72f1e9981b6d35b426b16dca7759be3e7ba06` |
| Runtime platform | Linux x86_64, also intended for a compatible x86_64 WSL environment |

The runtime includes its pinned dependency repositories and mathlib caches. Follow its restoration metadata to obtain and assemble that external runtime. The metadata alone does not supply the missing binaries. The formal rebuild script does not download dependencies.

From `source/FD_Certified_Inference_Core_v1.0.0_Checked`, once the runtime is available:

```bash
python3 checks/rebuild_release.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

This is an intentional formal rebuild operation: it removes active project compiled caches, recompiles the recorded module order, runs negative controls and exact diagnostics, and checks receipts, dependencies, and axiom lists. Pinned external mathlib caches are reused. Preserve the original archive and perform this rebuild in a separate working extraction when you want to retain the archived source/evidence untouched.

The source README also documents proof-producing instance export. `PASS_CACHED_PROVISIONAL` denotes a Python result whose emitted explicit Lean instance must compile before it is treated as a checked execution. A `RESOURCE_LIMIT` result means a bounded producer failed to finish within its caps; it is not a successful certificate and does not refute mathematical finite termination.

## Retained failures and extensions

The archived `FAILURE_LOG.md`, `SELF_REVIEW.md`, negative-control sources/logs, and release scope preserve unsuccessful routes and their corrections. A checked scalar counterexample shows that independently rounding gain and residual centers can yield stored score zero while the true score is two. The final verifier rejects that false convergence signal. A separate covariance-center example shows why interval enclosures cannot be replaced by a covariance matrix made from centers alone.

The seven-case reference benchmark supports cheaper cached selective iteration relative to recomputing selective packets. It does not establish an overall speed advantage over the efficient full-update baseline, optimized numerical libraries, or large-scale Gaussian-process systems. Export and Lean-checking costs are reported separately.

Sequential filtering, changing packet hierarchies, uncertain input data, rounded selective caches, approximate selection, hardware floating-point refinement, parser refinement, sampling, and large-scale performance remain named extensions. They do not alter the completed first-release contract.
