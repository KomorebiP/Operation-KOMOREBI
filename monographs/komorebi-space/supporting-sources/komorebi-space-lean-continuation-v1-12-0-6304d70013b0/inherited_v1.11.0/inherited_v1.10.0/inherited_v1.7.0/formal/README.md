# Komorebi Space — integrated formal project

Version 1.2.0. Recorded platform: Linux x86-64.

## Source closure

`KomorebiSpace.lean` imports all 138 production modules. The 133 inherited modules combine the foundation v0.20.0, focused moving-space v0.32.0, and separate Hilbert holonomy source, deduplicating one byte-identical shared module. Their original source bytes are unchanged. Five new modules formalize KS54–KS58.

| Item | Module | Main interface |
|---|---|---|
| KS54 | `FinitePrefixBoundary` | Actual nonempty finite prefixes and empty original point/ambient types. |
| KS55 | `DyadicSupport` | Nondivisibility support, coordinate recovery, and the valuation threshold on the actual varying-fiber system. |
| KS56 | `ProtectedHilbertRepair` | Feasibility, nearest protected answer, Pythagorean identity, and the restricted closed-range/gain criterion. |
| KS57 | `ProtectedLinearCertificates` | Arbitrary-field exclusive alternative, literal normalized row witnesses, affine ambiguity, and matrix rank-nullity. |
| KS58 | `FiniteRealizationExistence` | Original resolution points compared to actual cofiltered sections; finite-fiber existence and evaluation image. |

## Recorded verification path

From the publication package root:

```bash
python3 formal/scripts/verify.py \
  --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 \
  --label independent1
```

The label must be new. The verifier refuses to overwrite an existing replay directory. It checks the Lean version, all nine dependency pins, local import closure, production source scan, clean per-module compilation, project declaration axiom dependencies, positive examples, six compiler rejection controls, and one custom-axiom policy rejection. It saves a terminal PASS or FAIL record. Source, verifier, pin, and test changes during a run are rejected. Timed-out subprocess groups are terminated.

Supply the pinned external runtime and compiled cache. `pinned-dependencies.json` fixes the revisions. The runtime is not included in the source package. The compiler version is Lean 4.34.0-rc2 at `6a10ac8c22beadecabdbb0919c2b50214762f91d`, with mathlib at `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.

The `.lake` output directories are disposable and omitted from the source distribution. Their recorded object hashes are retained as execution metadata, not prerequisites for a clean replay. The `lakefile.toml` and `lean-toolchain` describe the project for a conventional installation. This edition's recorded verification is the offline script, not a claim that every alternative installation method or native Windows build was tested.

## Evidence locations

`../audit/formal/release.json` lists accepted final replay records and source hashes. The final imported axiom report is linked there. `../data/canonical_declarations.json` distinguishes lexical named declarations from compiler-generated declarations. The regression file is under `tests/positive/`. Intentional failures are under `tests/negative/` and `tests/policy/`, outside the production import closure.

The first integrated end-to-end attempt compiled all sources and passed its axiom audit but failed positive regression fixtures. It remains FAIL. Its corrected fixtures were checked independently before the accepted clean replay. Development records are preserved, not relabeled as final evidence.

## Trust boundary

Only the standard axioms `propext`, `Classical.choice`, and `Quot.sound` are permitted. The official compiler/kernel and pinned external dependency caches remain trusted. Mathlib was not rebuilt from source, and no independent kernel was used. The axiom collector uses Lean's imported axiom machinery. Formal declarations are checked, not natural-language text or a universal refinement of the Python implementation.
