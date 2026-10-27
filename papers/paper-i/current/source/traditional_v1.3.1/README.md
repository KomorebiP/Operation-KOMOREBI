# Projector-Resolved Seed Calculus I
## Complete distribution v1.3.1 — visual-refresh edition

Typed Seeds, Operator Grammars, and Exact Reconstruction  
Author: Komorebi P.

This is a consolidated source-and-artifact release for Paper I. The delivered PDF,
manuscript text, ten figure pairs, computational algorithms, Lean sources, and theorem
map are preserved from the visual-refresh edition. This packaging pass repairs the
stale manifest and release records, adds a continuation guide, and separates new checks
from historical verification.

## Contents

| Directory or file | Contents |
| --- | --- |
| `paper/` | 39-page article, editable LaTeX, ten vector PDFs, ten PNGs, contact sheet |
| `formalization/lean/` | 20 local Lean source files, Lake configuration, toolchain and dependency pins, theorem map |
| `code/python/` | Computational package, figure generator, example runner, six test modules (33 tests), dependency records |
| `scripts/` | Integrity check, read-only Python test wrapper, full Python regeneration, PDF build, Lean verifier |
| `results/` | Finite numerical results and current delivered-output inventory |
| `verification/` | Prior Lean and computation records plus the isolated fresh bundle recheck |
| `review/` | Mathematical review, claim mapping, corrections and diffs |
| `provenance/` | Original v1.2.1 snapshot and superseded pre-packaging metadata |
| `CONTINUE_HERE.md` | Restore instructions, exact state and proof boundaries |
| `RELEASE.json` | Current distribution versions, hashes, included and external components |
| `SHA256SUMS.txt` | SHA-256 checksums for every delivered file except the manifest itself |

All earlier logs retain their original timestamps and run paths. An absolute path
inside a historical log is provenance, not a portable path that must exist locally.

## Integrity and read-only Python checks

Before modifying anything:

```sh
python scripts/verify_manifest.py
python scripts/check_bundle.py --tests
```

The test wrapper uses the local package, disables pytest caching and bytecode output,
and places the Matplotlib cache outside the archive. It does not alter the manuscript,
figures or stored results. It does not install packages or run Lean.

`code/python/requirements.lock.txt` records the tested CPython 3.13.5 environment.
`requirements.in` and `pyproject.toml` describe the source package dependencies. To
provision a new Python environment, from the bundle root:

```sh
python -m venv .venv
# Activate .venv using the command appropriate to your shell, then:
python -m pip install -r code/python/requirements.lock.txt
```

Installing these dependencies requires an existing package cache or network access.
The bundle does not contain the interpreter or wheels. A wheel build has not been
performed; the source package can be run through PYTHONPATH without wheel installation.

## Regenerate the examples and figures

Run this on a working copy, not on the pristine release:

```sh
python scripts/verify_python.py
```

The script runs the tests, then `code/python/run_all.py`, updating `results/` and
`paper/figures/`. It writes a fresh verification record. Regeneration can change
PDF metadata, so the release checksums need not match after this operation. Retain
the pristine release rather than relabeling regenerated files as the original output.

The root `results/run_record.json` inventories the files actually delivered in this
bundle. The original generation record is preserved under
`provenance/pre_packaging_records/results/`. The latest isolated regeneration record
is under `verification/bundle_check/regenerated_results/`; its output hashes refer to
that run, not automatically to the byte-preserved publication PDF assets.

## Lean sources and checks

The local development contains 20 `.lean` files. The imported toolchain and dependency
pins are:

- Lean: `leanprover/lean4:v4.34.0-rc2`
- Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`
- Full dependency set: `formalization/lean/lake-manifest.json`

With an already provisioned matching Lake environment, from `formalization/lean/`:

```sh
lake --wfail build
lake env lean -DwarningAsError=true KomorebiVerification/KernelAudit.lean
```

These commands require Lean and the pinned dependencies to be present. They do not
perform the extra negative controls or all recordkeeping of `scripts/verify_lean.py`.
Do not run `lake update` casually: it changes the dependency state under review.

For the previously used portable Linux x86-64 kit, from this bundle root:

```sh
KIT="/path/to/Komorebi_Portable_Lean_4.34.0-rc2"
bash "$KIT/run.sh" lake -d "$KIT/workspace" env python3 \
  "$PWD/scripts/verify_lean.py" \
  --project "$PWD/formalization/lean" --kit "$KIT" \
  --out "$PWD/verification/lean_recheck"
```

The portable kit is **not** in this archive. The verifier requires a fresh local object
output directory and checks the dependency revisions before compiling. It rebuilds
local modules while reusing the matching dependency cache. It does not rebuild the
compiler or all of Mathlib.

The preserved audit records a successful build of 20 modules, 35 contract rows,
84 mapped targets, and 1,126 namespace entries, plus two rejected negative controls.
Targets and namespace entries include definitions and generated helpers; these are
not independent theorem counts. In this packaging pass, the source hashes were checked
against that record. The Lean compiler was not run again.

Files named `FalseEquality.lean` and `Placeholder.lean` under verification directories
are deliberate failing controls. They are not part of the main Lean library and must
not be treated as unfinished proofs in that library.

## Rebuild the article

With PDFLaTeX and the TeX packages used by the manuscript installed:

```sh
python scripts/build_pdf.py
```

The script runs three passes and fails on unresolved references or box overflow.
It does not visually inspect the PDF or certify accessibility, press compliance,
novelty, or mathematical correctness. The fresh isolated rebuild in this packaging
pass matched all 39 delivered pages in text and rendered pixels at 144 DPI. This is
a reproducibility comparison, not a new assessment of figure design quality.

## Formal scope

The 35-row formal contract retains its specified certificate inputs. Split algebra
and module equivalences, primary generators, projector polynomials, scalar quotient
maps, eigenbases and spectral coverage are supplied where required. The package does
not claim to construct arbitrary Jordan or Wedderburn decompositions, a spectral
certificate, or a formally verified exact eigensolver. The algebraic curve computation
does not formally establish projective smoothness or genus.

Mathematical review, claim-to-source correspondence, kernel acceptance, numerical
regression, and production review remain distinct. This is not an assertion of
independent peer review or a comprehensive novelty assessment.

No license has been selected; see `LICENSE_STATUS.md`.
