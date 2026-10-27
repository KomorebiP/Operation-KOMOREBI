# Komorebi Circuit Obstructions

### Restoration, discrepancy covers, and the limits of exact projection

**Version 1.0.0 · closed research scope · exact finite checks**

This repository collects a bounded piece of the Komorebi program: what a classical reversible computation must preserve when it borrows workspace, transports information, and restores its registers. It contains mathematical arguments, executable checks, and counterexamples to several tempting compression arguments.

**This is not a proof of P = NP or P ≠ NP.** The release is complete as a research artifact, not as a resolution of that conjecture. Its proofs are written and self-reviewed; the stated finite computations are reproducible. They have not been checked by Lean or an independent reviewer. No novelty or best-known-lower-bound claim is made.

## The central result

A restored computation has the form

\[
(x,0^a,y)\longmapsto(x,0^a,y\oplus f(x)).
\]

At any cut \(C=Q\circ P\), compare the forward and backward states:

\[
H_i(x)=P_i(x,0)\oplus Q_i^{-1}(x,0).
\]

Then every discrepancy is safe, and the discrepancies together decide the function:

\[
H_i\le f,\qquad \bigvee_iH_i=f.
\]

The construction allows intermediate workspace changes, output feedback, cancellation, and reuse. The rest of the release studies what can and cannot be inferred from these complete discrepancy covers.

## What is included

| Component | Result | Limit |
|---|---|---|
| Restored computation | Exact cut-comparison identity and complete safe coverage | Specified classical NOT/CNOT/Toffoli model |
| Packet degree | Affine-optimized complete-cover bound and exact finite dual certificates | The degree parameter is at most input length |
| Calibration | Optimal restored implementations for every function on at most three inputs | Matching bounds and constructions, not an exhaustive search over circuits |
| Projection | Exact family where a homogeneous grade has greater nonlinear cost than the whole | Not a total-gate or input-length exponential separation |
| Exact gluing | Faithful linear multiplicative witness summaries need exponential dimension | Restricted summary model, not arbitrary algorithms |
| Weighted witnesses | Exact fingerprint and coefficient-extraction identity | The supplied evaluator is exponential; overlap defeats the naive product rule |

Read the [claim register](docs/CLAIMS.md), the [foundations](docs/FOUNDATIONS.md), and the [research manuscript](docs/THEORY.md). The [proof boundary](PROOF_BOUNDARY.md) controls every claim in this release.

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

See [reproduction details](docs/REPRODUCIBILITY.md) and the [release audit](evidence/closure/RELEASE_AUDIT.md).

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
