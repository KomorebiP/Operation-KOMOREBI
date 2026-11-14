# Replay, input format and verification

**Komorebi P. · Reviewed reading edition · 13 November 2026**

The validated replay bundle contains the source dependency closure,
the exact input view, saved results, fresh bounded-run manifests and a
standard-library verification script. The original 71 KB replay archive
is retained separately as a historical export. Neither archive contains
the full earlier research history.

## Prepare a Python environment

The qualification environment used Python 3.12.14, NumPy 2.5.4 and
SymPy 1.14.0 on Windows. The bundle's `requirements.txt` pins the two
Python packages. Other platforms are not qualified merely by this record.

Create a virtual environment and install the requirements from the
unpacked bundle root:

```text
python -m venv .venv
```

On Windows, run the environment's interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On Linux or macOS, the corresponding interpreter is `.venv/bin/python`:

```sh
.venv/bin/python -m pip install -r requirements.txt
```

The commands below use `python` as shorthand for that chosen interpreter.
They do not require activation or a change to Windows execution policy.
Set conventional numerical-library thread caps before launching the
programs:

```powershell
$env:OPENBLAS_NUM_THREADS='1'
$env:OMP_NUM_THREADS='1'
$env:MKL_NUM_THREADS='1'
```

On a POSIX shell, use `export OPENBLAS_NUM_THREADS=1`, and likewise for
`OMP_NUM_THREADS` and `MKL_NUM_THREADS`.

## Run the saved cache example

Run from the unpacked bundle root, using a fresh output filename:

```text
python chemistry_stage14/recover_sector_cache.py --input chemistry_stage14/example_cache.json --output replay/certificate.json
```

The exact response center is $-107/1157-(1146/1157)i$. The output includes
`full_linear_consistent: true`, `positive_integral_estimate: true`,
`all_compatible_positive_integral: true` and
`operator_bound_is_sharp: false`. Its conditional response radius is
below 0.001336. The toy example's error caps are supplied assumptions;
the molecular replay measures its action cap separately.

## Input fields and conventions

| JSON field | Required meaning |
|---|---|
| `action_matrix` | Nine rows and three columns of real observed products, using exactly the fixed probe and determinant order. |
| `b_hat` | Nine real observed source components in the same determinant basis. |
| `raw_error_radius` | Nonnegative aggregate Frobenius cap for the three raw action errors. |
| `source_radius` | Nonnegative Euclidean source-error cap; defaults to zero. |
| `energy` | Real evaluation coordinate; defaults to zero. |
| `eta` | Strictly positive broadening; defaults to one. |

Integer and rational/decimal strings denote exact numbers. A JSON floating
number is interpreted as its exact stored binary64 value. For example,
`"0.1"` is exactly one tenth, whereas the JSON number `0.1` is its
binary64 approximation. Booleans and nonfinite floats are rejected.
The decoder does not infer a valid error cap, validate molecular model
assumptions or detect every possible probe-order mistake from the values
alone.

If the full linear family is inconsistent, the result has no response
center or response disk. For consistent data, the positivity feasibility
field is `true`, `false` or `null` according to the
[case distinctions](three-queries.md#positivity-existence-and-an-all-compatible-guarantee).
The all-compatible positivity flag is a separate sufficient guarantee.
Compatible integral representatives are not recovered original integrals.
The representative ERI matrix uses the explicit `eri_pair_order` in its
output. That order must not be inferred from a different packed-storage
convention.

## Repeat the exact audits

Use fresh output directories:

```text
python chemistry_stage14/audit_sector.py --output replay/exact
python chemistry_stage14/qualify_frozen_core.py --output replay/molecular
python chemistry_stage14/audit_reading_extensions.py --output replay/extensions
```

The first run repeats the 82 named original checks. The second checks the
declared projection, positivity, measured action errors and response
inclusion. The third checks the added coefficient dictionaries, positivity
boundary cases, parser/root boundaries and finite examples of the
conditional full-model bound. Finite examples support implementation
checking; the general arguments are in the written proofs.

The molecular run creates `molecular_cache.json`,
`molecular_certificate.json`, `molecular_reference.json` and
`qualification.json`. The source container is the declared selected-array
view. Its hash is intentionally different from that of the original full
fixture. Different numerical-library builds can also change floating
products; each run must measure and validate its own cap. Copying a saved
cap onto different products is not a certificate.

Existing output certificates are not overwritten. Choose another fresh
folder, such as `replay-02`, when repeating a command.

## Check the included provenance

```text
python verify_public_replay.py
```

This standard-library command checks the complete bundle checksum index,
the three included v2 manifests, their before/after input hashes and output
hashes, saved input-to-certificate links, and the rational numerical
inequalities used by the notes. It does not run the calculations again or
substitute for mathematical review.

The manifest commands use a relative `python` executable and project-relative
paths. The records expose versions, timestamps, runtime, platform, bounds,
status and hashes without retaining a personal machine path. The Windows
runs enforce wall-clock/log caps and conventional thread limits; no POSIX
memory or CPU limit is claimed.

`VALIDATION_SHA256SUMS` covers the complete validated bundle. The separate
historical archive has its own `PUBLIC_SHA256SUMS` index. Original
historical results and fresh validation results have distinct paths and
container hashes; neither is relabeled as the other.

An installed Mathbox `validate_manifest.py --root <unpacked-root>` can
also validate each new manifest. A replay user does not need Mathbox for
the three scientific commands or the included standard-library verifier.

## Failures and interpretation

| Observation | Next check |
|---|---|
| Missing NumPy or SymPy | Use the selected virtual-environment interpreter and install its requirements. |
| Wrong matrix/source shape | Check the nine determinant rows, three fixed probe columns and nine source entries. |
| Negative radius or nonpositive broadening | Correct the input assumptions; zero broadening is outside the theorem. |
| Inconsistent cache | Inspect probe ordering, actual action errors, the cap and model membership. Do not enlarge a cap without justification. |
| A hash mismatch | Keep the differing file, identify the edition or transfer error, and obtain a verified copy. Do not refresh the expected digest to hide it. |
| A different floating radius on replay | Compare versions and products, then inspect the fresh exact reference inclusion. |

The replay verifies a finite arithmetic contract. It supplies no full-H10
truncation/source/ground-energy certificate, no runtime advantage and no
world-priority result. The [review](review.md) lists the remaining scope.
