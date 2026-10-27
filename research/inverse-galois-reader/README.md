# Inverse Galois: the realization still required

Operation Komorebi · Conjecture Series 09 · Komorebi P.  
Reader edition 1.0 · 9 October 2026

The publication set contains a substantial mathematical reader, a separate mainly visual guide, editable LaTeX, 22 code-native figures, four recovered historical inputs, exact worked examples and separate source, proof, computation and page-review evidence.

It does not prove inverse Galois realization over Q for every finite group. The edition proves specified elementary field and regular-projector statements, records conditional realization routes, and isolates the arithmetic existence input. No Lean or other proof-assistant certification is claimed.

## Read

The final PDFs are under `output/pdf/`. They are self-contained, with internal contents links and primary-source bibliographic URLs. There are no external-file or Library download actions inside either PDF.

The monograph includes five complete scalar field examples, the generic invariant-field construction, the regular subgroup-projector calculus, specialization, proper embedding problems and a concrete field realization certificate. The visual guide shows the same distinctions through exact diagrams and finite examples. The plotted complex roots are illustrations, not Galois group certificates.

## Reproduce the exact examples

Python 3 and SymPy are required. From this directory:

```sh
python3 computations/exact_examples.py --output computations/exact_examples.json
```

This deterministic script checks five polynomials, all 36 ordered pairs of the six S3 subgroups, one faithful S4 representation boundary, two finite embedding toys and three specialization values. It uses exact rational and finite-field arithmetic. It does not enumerate arbitrary finite groups or construct all inverse Galois realizations.

The following optional wrapper enforces POSIX memory/CPU limits and records version 2 provenance. It is intended for Linux or WSL rather than native Windows:

```sh
python3 computations/run_examples.py
```

The delivered manifest is `evidence/computation/manifest.json`. It records actual input/output hashes, command, runtime, software and limits. Its validator passed with the project root supplied. The JSON under `computations/` is byte-identical to the scientific result under `evidence/computation/`.

## Rebuild the readers

Python 3, matplotlib, numpy, SymPy, PyMuPDF, Pillow, Poppler and TeX Live with the packages in the shared preambles were used. Exact installed versions are recorded in `evidence/BUILD_ENVIRONMENT.json`.

```sh
python3 build.py --figures
python3 validate_historical.py
python3 validate_fonts.py
```

`quality_check.py` renders immutable snapshots with system Poppler at 150 dpi and checks page bounds, text extraction and TeX diagnostics. `merge_layout_reviews.py` requires actual individual page-review records for the same PDF and PNG hashes. `validate_release.py` checks exports, portable links and current evidence. An automated check alone is not visual inspection.

Existing layout records certify only the shipped PDFs. Rebuilding may change metadata, pagination or figures and therefore requires renewed page review before a changed PDF can receive full layout validation.

## Source and claim scope

The four originals in `historical/` are preserved byte for byte. Their extracted contents remain historical material. This edition independently reviews the selected proof chain rather than certifying every result in the larger Galois manuscript. The historical Frobenius multiplication laboratory is not newly executed here and is not an inverse Galois proof dependency.

Primary-source contracts under `literature/` record exact versions, locators, notation translation, source qualifications and acquisition failures. Third-party source PDFs are excluded from the distributed archive. The 2026 M23 result is attributed to a versioned external preprint. Its numerical/Magma certificates were not reproduced in this project. The general problem remains open in the checked source scope.

`audits/` separates universal written arguments from external inputs and bounded computations. The failure of subgroup detection in a merely group-faithful S4 representation is explicitly documented. Regular group-algebra faithfulness remains a required hypothesis for the converse projector statements.

`MANIFEST.json` pins every packaged member's byte count and SHA-256. The package builder verifies archive integrity and every member hash. Hashes record provenance, not mathematical truth.
