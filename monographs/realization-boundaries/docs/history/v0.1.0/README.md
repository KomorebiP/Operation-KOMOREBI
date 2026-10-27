# Realization Boundaries — Lean companion

**Komorebi P. · Realization Calculus**

This is the first compiler-checked algebraic tranche for *Realization Boundaries: Finite Grammar, Infinite Groups, and the Limits of Reconstruction*. It constructs the actual infinite prime product and finite-support quotient. It does not replace them with finite arrays or assume the quotient is already a rational vector space.

## What is formalized

The production modules prove the torsion/finite-support equivalence, unique integer division in the actual quotient, its rational module structure, pure-preimage root criteria, canonical integer-quotient isomorphisms and finite-target kernel containment. They also construct the explicit reduced-rational section, prove the finite denominator support bound for its cocycle, construct a separate twisted normal-form group, and give its actual additive equivalence with the ambient preimage. Nonsplitting and the impossibility of removing the cocycle by a D-valued correction are proved. The paired-prime family and its selected/unselected marked root tests are instantiated without a caller-supplied infinite-support assumption.

The source uses the finite-support subgroup of the product as its model of D. The rational module on P/D is transported from a proved equivalence with its divisible hull, after injectivity and surjectivity of every positive integer multiplication have been established.

**This is not a complete Lean formalization of the book.** Full profinite topology and completion, the reverse pure-preimage correspondence, countability and root-fiber cardinality, unmarked classification, all-homomorphism and endomorphism theorems, the oracle-degree semantics, and repeated grammar diagonalization remain outside this tranche. The exact theorem-by-theorem boundary is in `docs/MONOGRAPH_COVERAGE.md` and its JSON companion.

## Reproduce the checks

Use the existing Linux x86-64 portable kit `Komorebi_Portable_Lean_4.34.0-rc2`. It also runs in a compatible x86-64 Linux distribution under WSL2. It is not a native Windows, ARM, or macOS executable. The compiler and multi-gigabyte dependency caches are not duplicated in this source archive.

From this directory:

```bash
export KOMOREBI_LEAN_KIT=/absolute/path/to/Komorebi_Portable_Lean_4.34.0-rc2
python3 scripts/verify.py --output ../realization-boundaries-verification
```

Choose a new output directory on every run. The verifier refuses an existing one. Python 3.10 or later, Git, and the kit's Linux runtime prerequisites are required. No network requests, dependency upgrades, or remote publications are performed.

The verifier checks all pinned dependency revisions, compiles production sources serially with automatic implicit parameters disabled and warnings treated as errors, exports declaration types and transitive axiom dependencies, checks the positive contracts and intended rejections, and replays each production module through Lean's kernel. It also compares source and dependency-cache/compiler hashes at the recorded endpoints. On a first-time source checkout, the cache baseline is obtained after the initial build; the report identifies this distinction explicitly.

A normal `lake build` is a separate elaboration check. Use the verifier above for the complete audit and low-memory sequential execution. `scripts/check.py` is a development helper and accepts `--kit` for individual files.

## Pinned environment

- Lean: **4.34.0-rc2**, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`.
- Mathlib: `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- The lockfile records all additional package revisions.
- The accepted audit permits only `propext`, `Classical.choice`, and `Quot.sound`.

The restored runtime came from the five existing `Lean_Compact_01.zip` through `Lean_Compact_05.zip` Library parts. `provenance/runtime_restoration.json` records this session's extraction/CRC and hash evidence. The observed archive hash is a provenance record, not independent authentication of every upstream byte.

## Reading the source

| Module | Main role |
|---|---|
| `Ambient` | Actual product, finite support, torsion, coordinate annihilators |
| `Quotient` | Concrete quotient, unique division, derived rational module |
| `Preimages` | Admissible preimages, root equivalence, purity, torsion, separation |
| `FiniteQuotients` | Actual quotient groups, coordinate transitions, finite-target kernels |
| `Extensions` | Rational quotient, reducedness, nonsplitting |
| `Sections` | Explicit rational section, denominator defects, unique normal forms |
| `Cocycle` | Infinite-coordinate support bound, cocycle laws, nonremovability |
| `PairedPrimes` | Prime-pair construction and exact marked root tests |
| `NormalForms` | A distinct cocycle group and its additive realization equivalence |

The separate `NormalForm` type is deliberate. Its addition contains the cocycle; it is not the standard split-group instance on the product type `ℚ × D`.

## Evidence and boundaries

`LEAN_VERIFICATION_REPORT.md` summarizes the accepted run. `verification/accepted` contains compiler logs, declaration/type/axiom exports, negative-control logs, kernel replays, dependency inventories, and source identities. `verification/development` retains failed intermediate compilations rather than relabelling them as passes.

The ten files under `tests/negative` are intentionally invalid and are excluded from production imports. Some deliberately declare a forbidden axiom, an admitted proof, or an unsafe definition to test that the audit rejects them. Their presence is not a proof admission in the production library.

Lean's kernel, compiler/runtime, standard axioms, and the imported pinned compiled dependencies are part of the trust boundary. Kernel replay here uses Lean's own kernel, not an independently implemented checker. Mathlib and the compiler were not rebuilt from source. Endpoint hashes do not authenticate the original provenance of caches or detect a transient alteration restored before the final snapshot.

The constructions are noncomputable where classical membership and choices are used. This release does not claim verified extraction of the Python arithmetic engine or a formal oracle-computability theorem. The book's earlier Python counts are inherited evidence, not fresh Lean test counts.

The publication PDF and its original final source archive are preserved unchanged under `publication` and `provenance`. This companion is the authoritative record of the new formalization scope; it does not silently rewrite the printed book's historical verification statements.

## License

The new Lean sources and verification scripts are MIT licensed under the name Komorebi P. Lean, Mathlib, and other dependencies retain their upstream licenses and are not included in this small source package. No historical-priority or independent external peer-review claim is made.
