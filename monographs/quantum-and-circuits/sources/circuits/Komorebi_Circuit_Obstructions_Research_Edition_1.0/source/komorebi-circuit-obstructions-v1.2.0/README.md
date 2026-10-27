# Komorebi Circuit Obstructions

### Restoration, discrepancy covers, and the limits of exact projection

**Version 1.2.0 · closed research scope · Lean Block 02**

This repository contains written mathematics, formal Lean proofs, exact finite checks, and counterexamples concerning classical reversible computation with restored workspace. It is **not a proof of P = NP or P ≠ NP**. No independent review, novelty claim, or hosted publication is asserted.

## New formal result

For every legal classical NOT/CNOT/Toffoli circuit implementing

\[
(x,0^a,b)\longmapsto(x,0^a,b\oplus f(x))
\]

on every input and both initial target bits, Lean now proves

\[
\deg(f)\le T+1,\qquad 2\beta^*(f)\le T+3.
\]

The first inequality is formalized as an explicit polynomial-representation certificate `DegreeLE (T+1) f`. Here T counts Toffolis, beta is the least degree needed for complete safe coverage, and betaStar is its affine-output optimization. NOT and CNOT cost zero only in this particular resource count. All registers may be dirty between boundary states, and the target may be used as a control.

The key invariant is **degree <= t+r for any product of r current registers after t Toffolis**. It preserves sharing instead of unfolding the circuit into a formula. The cut-cover theorem, balanced-cut construction, existence of beta and betaStar, and zero-Toffoli affine-output circuit are all proved.

**Formal scope:** C01, the maintained NCT specialization of F3, and the lower-bound component of C02. The C02 evaluation-span dual and C03-C08 retain their written/finite status. There are **115 checked theorem declarations, 75 added in Block 02**, not 115 independent discoveries. The formal proof also establishes betaStar<=n, so this result does not force superpolynomial growth.

- [Cumulative Lean theorem reference](reference/lean-block02/Lean_Verified_Bounds_Block_02.pdf)
- [Exact Block 02 proof and scope](docs/formalization/LEAN_BLOCK_02.md)
- [All declaration names and source lines](formalization/lean/theorem_inventory.json)
- [Build, axiom, and module-replay evidence](evidence/lean-block02/verified/verification.json)
- [Original Block 01 reference](reference/lean-block01/Lean_Verified_Core_Block_01.pdf)

## Reproduce the formal result

With the pinned Lean 4.34.0-rc2 toolchain already installed:

```sh
python scripts/verify_lean.py
```

Or select a portable toolchain:

```sh
python scripts/verify_lean.py --toolchain /path/to/toolchain
```

Only bundled Std is imported; there is no Mathlib dependency. The verifier builds from fresh source, audits every declaration's axioms, replays eight modules, and requires eight invalid controls to be rejected. Tool errors are not reported as verification success. See [formal instructions](formalization/lean/README.md).

## Closed mathematical scope

| Component | Verified status | Boundary |
|---|---|---|
| C01: complete cut cover | Lean, written, finite | Requires the stated restored classical oracle |
| F3: degree with sharing | Lean for the maintained NCT model | Separate generic XOR-AND syntax is not formalized |
| C02: affine-optimized bound | Lean, written, finite | C02 dual certificates remain unformalized; betaStar<=n |
| C03-C04: calibration families | Written and exact finite evidence | AND2 is the additional explicitly formalized example |
| C05: projection limitations | Written and exact finite evidence | Nonlinear cost is not total gate count |
| C06: faithful flat gluing | Written and exact finite evidence | Restricted summary model, not arbitrary algorithms |
| C07-C08: witness trace | Written and exact finite evidence | Efficient evaluator is not supplied |

The [claim register](docs/CLAIMS.md) and [proof boundary](PROOF_BOUNDARY.md) control the interpretation. Original v1.0.0 and v1.1.0 snapshots and their references are preserved rather than relabeled.

## Run it

No Python packages, network connection, bank of test instances, or external solver are needed for the local checks.

```sh
python scripts/verify.py --quick
```

The full active suite additionally needs a C++17 compiler, selected by `CXX` (default `g++`):

```sh
python scripts/verify.py --full
```

To run the active suite and reproduce the frozen source checkpoint:

```sh
python scripts/verify.py --all
```

Python 3.10+ is the supported source target. The recorded local release run used Python 3.13.5 and g++ 14.2.0 on Linux. Other platforms are not claimed locally tested. Do not run with `-O` or `PYTHONOPTIMIZE`: the checks deliberately use assertions, and the launcher rejects optimized Python.

On Windows PowerShell, `py -3 scripts/verify.py --quick` uses an installed Python. The full historical replay is documented for Linux/WSL, not MSVC.

Runs write only to a new directory under `build/verification/`. Sealed source archives and baseline evidence are never overwritten. A nonzero exit code means failure or inconclusive execution, not mathematical falsity by default.

See [reproduction details](docs/REPRODUCIBILITY.md) and the [current release audit](evidence/lean-block02/RELEASE_AUDIT.md).

## Repository map

```text
checks/                  Flat, maintained scientific checkers
scripts/                 Verification, integrity, and manifest tools
tests/                   Fast independent controls and packaging tests
docs/                    Proofs, conventions, claim register, and sources
evidence/baseline/       Frozen expected scientific results
evidence/closure/        Evidence from preparing this release
archive/checkpoints/     Ten original research checkpoints, unchanged
.github/workflows/       Quick CI and manually requested full verification
```

## What “closed” means

The accepted scope is fixed in [SCOPE.md](SCOPE.md). Correctness fixes and reproduction repairs belong here. Solving P versus NP, formalizing every proof, and completing every exploratory idea are **not** requirements for this release. Earlier open-ended continuation prompts survive only inside the historical archives.

The version has no active research-completion blockers. Open directions are archived in [OUT_OF_SCOPE.md](docs/OUT_OF_SCOPE.md), not presented as promised features.

## Identity and publication

Publication name: **Komorebi P.** This was developed with AI assistance. No legal name, affiliation, DOI, or live repository address is asserted. See [CITATION.cff](CITATION.cff), [RIGHTS.md](RIGHTS.md), and [publication notes](docs/PUBLICATION.md).

This snapshot was assembled locally. It does not by itself create, publish, privatize, or archive a hosted GitHub repository. The GitHub workflow is supplied but has not run on a hosted repository in this release session.
