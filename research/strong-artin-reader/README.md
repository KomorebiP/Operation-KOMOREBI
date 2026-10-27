# Strong Artin in the Operation Komorebi conjecture series

Reader edition 1.0, 8 October 2026. Publication author: Komorebi P.

This set brings the Strong Artin research into the same monograph and visual guide format as the Collatz and Riemann pieces. It explains the proved finite mechanisms and the precise global attachment problem. General Strong Artin is not claimed proved.

## Reader documents

- `pdf/Komorebi_Strong_Artin_Conjecture_Piece_v1.0.pdf`: the conjecture, cyclic Clifford alternatives, extension and descent torsors, local coefficient selectors, finite Satake alphabets, conditional residual and l-adic recovery, obstruction and lifting methods, worked examples, and the remaining realization input.
- `pdf/Komorebi_Strong_Artin_Visual_Guide_v1.0.pdf`: twenty four illustrated spreads, each with one reading task, exact hypotheses, and a carry forward statement. Finite examples, models, imported theorems, and conditional global gates are identified where they appear.

The monograph retains the load bearing arguments from the earlier residual realization paper and adds detailed explanations of later formal work. A separate formal appendix derives cyclic cohomology, square zero defects, target compatibility, ordered matrix derivatives, and the certified local matrix root criterion. These algebraic mechanisms do not themselves construct an automorphic carrier.

The assembled monograph has 58 pages. The visual guide has 25 pages, comprising its cover and twenty four illustrated spreads.

## Reading and evidence map

`paper/` contains the manuscript, formal appendix, bibliography, source register, and proofreading reports. `visual/` contains the guide, generator, vector and raster figures, data, pinned dependencies, computation record, and proofreading report.

`evidence/REVIEW.md` pins the source revisions reviewed as mathematics. `evidence/independent_controls.py` and its bounded run preserve independent exact checks and necessary hypothesis counterexamples. `evidence/SOURCE_VALIDATION.json` records current TeX references and reviewed revision agreement. `evidence/LAYOUT_VALIDATION.json` records the assembled PDFs and page inspection. `AUTHORING_REPORT.md` records corrections, failed steps, and their resolution.

`evidence/LITERATURE_CHECK.md` and `LITERATURE_SOURCE_MANIFEST.json` record precise primary source statements, versions, locators, and application limits. Full third party papers and extracted text are not redistributed. The September 2026 Wang preprint is cited as a newly posted external result with a stated sector, not an independently audited project proof.

`evidence/recovered/` preserves the original residual realization manuscript and package, the September 11 audit, and the latest recovered v0.38 archive and replay record. The original archive retains historical claims and disclosures unchanged. Current corrections are made in the new reader documents and authoring report. `RECOVERED_INPUTS.json` authenticates the seven selected inputs. `lean/` contains extracted source ancestry, authentication records, source coverage, and replay instructions. Historical checkpoint folders retain their own scopes and toolchain assumptions. They are not a flat combined build.

## Exact status

The finite representation and coefficient arguments, finite trace encoding, and certified local lifting statements have explicit hypotheses. Cyclic automorphic base change and induction remain imported external results. A valid induction chain is required. Arbitrary monomial and arbitrary solvable automorphy are not inferred from the existence of cyclic operations.

The realization arguments require an actual global representation or an appropriate lifting input. Pointwise Frobenius polynomials, finite alphabets, residual label collapse at the quotient prime, and abstract correction operators do not provide that existence input. Weak unramified attachment and attachment at every place are kept distinct.

The v0.38 archive contains seven new modules with 44 theorem declarations, 15 definitions, and one abbreviation. That local count is not a total for all historical branches. Its matrix root criterion requires a supplied two sided inverse derivative certificate over Q_p and depth m greater than its loss s. It allows a derivative singular modulo p. It does not cover derivatives singular over Q_p or all shallow prefixes.

A fresh Lean replay was attempted as a workflow but could not reach compilation. Downloading the matching portable runtime returned HTTP 403. The authenticated September 12 replay and its exact source hashes are retained. Archive and static source checks in this edition are not represented as a new Lean proof check. The isolated replay wrapper requires the pinned portable kit and reuses its pinned Mathlib dependencies.

## Rebuild

Provide Python 3 and the dependencies in `visual/requirements.txt`. The independent exact controls use the standard library. Provide pdflatex with mathpazo, Helvetica, Courier, amsmath, mathtools, microtype, titlesec, fancyhdr, graphicx, enumitem, booktabs and hyperref.

```bash
python visual/figures.py
python evidence/independent_controls.py
python evidence/independent_layer_controls.py
python evidence/independent_cochain_controls.py
python build.py
```

`python build.py --only paper` or `--only visual` builds one reader. `--figures` regenerates the guide figures first. For optional layout checks, provide PyMuPDF, Pillow and Poppler, then run `python quality_check.py`. Regenerated pages still require visual inspection.

After final reports exist, `python package.py` creates the source archive, checks its ZIP integrity, and verifies every payload SHA256 against `MANIFEST.json`. Computational passes establish only their declared finite assertions. The written proofs and cited inputs carry the universal statements.

`python validate_release.py --manual-reviewed` validates the source revision pins and final PDF checks after every rendered page has been visually inspected. The flag records that inspection step. It does not perform it automatically. The separate `quality_check.py` prepares all page images and contact sheets.
