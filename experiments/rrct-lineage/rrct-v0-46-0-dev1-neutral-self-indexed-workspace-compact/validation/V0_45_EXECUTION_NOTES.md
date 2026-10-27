# RRCT v0.45 Execution Notes

## Source provenance

The implementation was built from:

- RRCT `0.44.0.dev1` transformational self-continuity
- Komorebi Math `1.0.0b4` complete Block 21 handoff

The exact Komorebi wheel was copied unchanged into `src/rrct/_vendor/` with its license and a local vendor manifest. The RRCT bridge verifies the wheel digest and package version before using it.

## Development sequence

1. Located and extracted the complete Komorebi handoff rather than relying on paper descriptions.
2. Audited public finite APIs for packet systems, coordinate transport, Bayesian update, and low-rank recompression.
3. Implemented an RRCT adapter and an extended v0.44 controller.
4. Added synthetic source-attribution and memory-resolution comparisons.
5. Corrected exposed-development calibration: full cross-validated memory transport drives continuity quality; compressed-memory loss is reported separately, and negligible dynamics residuals are classified as no change.
6. Ran focused development tests and an exposed three-seed benchmark.
7. Selected four unused deterministic holdout seeds.
8. Sealed 82 source, dependency, protocol, test, and runner files.
9. Executed the frozen holdout without changing the sealed files.
10. Replayed the complete result exactly.

## Frozen execution

The holdout ran on:

```text
116221458
458425147
129992909
292534192
```

The operator cohort contained 256 unique worlds and 1,024 matched decisions. The bridge cohort contained 144 matched engine decisions. All 18 endpoints passed.

## Tests

```text
focused v0.45:             9 passed
v0.43-v0.45 line:         26 passed, 2 deselected
v0.36-v0.40 line:         64 passed, 1 deselected
v0.41-v0.45 line:         47 passed, 2 deselected
AST parse:                 168 files passed
```

The deselected checks are predecessor-specific immutable-freeze builders or predecessor source-seal checks that cannot certify a successor tree containing deliberate new source files.

A complete historical-suite pass is not claimed. The compact ancestor continues to omit older official-harness and protocol assets documented in earlier release notes.

## Built-package verification

The RRCT wheel built successfully without dependency download:

```text
rrct_prototype-0.45.0.dev1-py3-none-any.whl
```

It contains the exact nested Komorebi wheel, vendor manifest, and license. The embedded Komorebi wheel digest equals the frozen expected digest.

The installed RRCT wheel was imported from an isolated target directory. It reported RRCT `0.45.0.dev1`, loaded Komorebi `1.0.0b4`, instantiated `KomorebiOperatorBridge`, and passed a 32-row installed-wheel operator smoke test.

The first clean-install probe attempted to import two helper names that were not part of the sealed module. That probe failed before exercising the package. The corrected probe used the actual sealed bridge API and passed. No implementation or frozen result was changed.

## Claim boundary

The benchmark is a controlled linear existence and comparison test. It establishes direct integration and measured benefit over the specified controls. It does not establish general superiority of Komorebi Math, open-world self-boundary discovery, autonomous autobiographical repair, or consciousness.
