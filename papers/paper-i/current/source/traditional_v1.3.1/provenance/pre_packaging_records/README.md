# Projector-Resolved Seed Calculus I
## Journal edition v1.3.0

**Typed Seeds, Operator Grammars, and Exact Reconstruction**  
**Author:** Komorebi P.  
**Series:** Journal of Komorebi Mathematics · Core Series I  
**Edition date:** 12 September 2026 (UTC verification record)

Start with `paper/Projector_Resolved_Seed_Calculus_I.pdf`.
Read `review/REVIEW.md` for the corrections, scope, and checks performed.
This is a self-published journal manuscript and a verification release, not
an assertion of independent peer review or a comprehensive novelty review.

## What has been checked in this edition

- Twenty local Lean modules rebuilt in a fresh object directory, using the
  pinned imported dependency cache; all 35 registered contract rows resolve
  to 84 distinct mapped targets. The target count includes definitions.
- The fail-closed namespace gate audited 1,126 project declarations,
  including definitions and generated helpers. The permitted transitive
  axioms are `propext`, `Classical.choice`, and `Quot.sound`.
- Both negative controls behaved as intended: a false equality was rejected,
  and a proof placeholder was rejected with warnings treated as errors.
- Thirty-three Python regression tests passed, including new large-integer
  and complex-symmetric-matrix cases. The original finite numerical results
  are unchanged; only release/interpreter metadata differs.
- All ten programmatic figures were regenerated. The schematic dependency
  figure now separates the generator and projector branches; captions
  distinguish illustrations, finite computations, and all-size proofs.
- The main text keeps all 69 numbered environments and their original
  result labels. These include definitions, examples, remarks, and boundaries;
  69 is not a theorem count.

Recorded outcomes belong to the bundled source hashes. A changed source
needs a new run. No script infers a verification pass from a previous run.

## Layout

```
paper/                  manuscript, PDF, ten figure pairs
formalization/lean/     pinned sources and 35-row map
code/python/            companion v1.1.2 and 33 tests
results/                finite experiments and generated-output hashes
verification/lean/      fresh compiler logs, types, audit, negative controls
verification/python_release/  final tests and experiment process records
verification/pdf_final/     final typesetting logs
review/                 substantive review, patches, and comparison records
provenance/             original v1.2.1 Paper I snapshot, explicitly historical
scripts/                repeatable check and build commands
```

The portable Lean runtime and Mathlib cache are not included in this ZIP.
No standalone font files are distributed. Local compiled Lean objects are regenerated
by the verifier and are not included; the compiler logs and object hashes are retained.

## Repeat the Python checks

Use an environment with the packages in `code/python/requirements.lock.txt`.
That file records the observed CPython 3.13.5 test environment. It is not a
claim that every supported interpreter or operating system has been tested.
The source can be used without installing a wheel:

```sh
python scripts/verify_python.py
```

This writes a new `verification/python_recheck` record, runs the tests, then
regenerates the finite examples and figures. It does not check Lean, novelty,
visual layout, or the formal correctness of Python algorithms. Wheel
packaging was not run in this edition. The optional build dependency `wheel`
is not installed in the recorded verification environment.

## Repeat the Lean checks with the existing portable kit

The recorded platform is Linux x86-64. Set `KIT` to the existing
`Komorebi_Portable_Lean_4.34.0-rc2` directory. From this package root:

```sh
KIT="/path/to/Komorebi_Portable_Lean_4.34.0-rc2"
bash "$KIT/run.sh" lake -d "$KIT/workspace" env python3 \
  "$PWD/scripts/verify_lean.py" \
  --project "$PWD/formalization/lean" --kit "$KIT" \
  --out "$PWD/verification/lean_recheck"
```

The verifier requires an initially empty local object output directory. Use
a new `--out` directory for another run. It checks the toolchain and all nine
package revisions before compiling. URL suffixes `.git` are normalized when
comparing equivalent repository addresses; revisions are not relaxed.

The Lean pin is `leanprover/lean4:v4.34.0-rc2`. Mathlib is pinned to
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The original theorem statements and
proof bodies are unchanged. Eight blanket imports were replaced with one
focused import module to fit the available memory. The smaller import closure
is the only change to the nineteen existing Lean files.

An ordinary, already provisioned Lake environment can instead run these
commands from `formalization/lean`:

```sh
lake --wfail build
lake env lean -DwarningAsError=true KomorebiVerification/KernelAudit.lean
```

Those commands do not reproduce all the extra recordkeeping and negative
controls of the packaged verifier. The dependency cache in the recorded run
was reused, not independently rebuilt. A full clean Mathlib rebuild is a
separate, more demanding operation.

## Build the article

With a TeX Live installation that supplies the packages used by the source:

```sh
python scripts/build_pdf.py
```

The script runs three PDFLaTeX passes, fails on unresolved references or
box overflow, and copies the resulting PDF into `paper/`. It does not claim
that a PDF was visually inspected. The delivered edition has a separate
visual-review record. This is a reading/publication manuscript, not an
assertion of PDF/UA, PDF/A, or printer-specific press compliance.

## Claim boundary

The 35-row contract excludes classical existence/classification inputs.
Split algebra/module equivalences, primary generators, projector
polynomials, scalar quotient maps, eigenbases, and spectral coverage are
supplied where required. The release does not construct a general Jordan or
Wedderburn decomposition, a spectral-theorem certificate, or a verified
exact eigensolver. The quotient-algebra computation does not constitute a
formal proof of the associated curve's projective smoothness or genus.

Mathematical review, source-to-statement correspondence, kernel acceptance,
finite computational checks, and production review are distinct records.
This package does not convert one into another.

## Package integrity

Before editing, run `python scripts/verify_manifest.py` to check the
bundled SHA-256 manifest. This checks file integrity, not correctness.
The source-only production rebuild and repeated 33-test run are recorded
under `verification/source_rebuild`; all 39 rebuilt pages match the
delivered article in extracted text and at 144 DPI.
