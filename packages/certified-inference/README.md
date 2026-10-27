# Komorebi Certified Inference Core 1.0.0

Author: Komorebi P. A finished scoped research release for finite-dimensional,
one-observation Gaussian inference with explicit arithmetic and output contracts.
Read RELEASE_SCOPE.md before using stronger descriptions of its capabilities.

The canonical program is Komorebi.CachedPosterior.runCached. It maintains exact
packet residuals and energies, selects a largest residual packet, and changes only
that packet. Its cache invariants, equivalence to the recomputed greedy trajectory,
finite termination, final rounded certificate and interval output are Lean-checked.

For valid exact factor-coded model data, fixed complete self-adjoint packet families,
and positive rational epsilon/delta, it returns a gain whose Joseph Gaussian is
within epsilon of the actual Bayesian posterior in W2, plus mean/covariance intervals
of that approximation with each radius at most delta. The centers alone do not
define a separately certified Gaussian. There is no executable sampler contract.

## Run a proof-producing instance

Python 3.10+ with the standard library. From this directory:

```bash
python3 checks/cached_posterior.py examples/adaptive_coordinate.json --output results/local_cached.json --emit-lean Komorebi/LocalCached.lean --namespace LocalCached --try-precisions 4 12
```

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_cached.ps1
```

`PASS_CACHED_PROVISIONAL` is not a proof. The explicit emitted Lean source must
compile to certify that execution. Its model/gain data are the mathematical input;
a universal JSON parser or Python-to-Lean refinement theorem is not claimed.
The exporter checks the actual program return and reported interval arrays.

Inputs include model factors, initial_gain, epsilon, output_radius, seed, and scan.
The scan must cover every output packet. Duplicates and arbitrary order are allowed;
ties preserve the incumbent. Rational fractions and decimal strings are exact.
Raw JSON floating-point numbers are rejected.

Default producer caps: dimensions at most 8, 10,000 updates, 32,768 bits per gain
rational, 512 fractional certificate/output bits, 16 precision probes, 128 scan
entries and one million input bytes. Resource-limited executions report failure and
cannot emit a success theorem. The ideal finite-fuel theorem has no hardware cap.

## Arithmetic and solver branches

The cached selective branch uses exact rational gain updates and cached scores.
Final certificate/output evaluation uses the declared outward-rounded dyadic graph.
The v11 rounded full-gain solver remains preserved as a separate checked branch.
The cached solver defers full rounded verification until its exact score is at most
epsilon^2/4, which provides a guaranteed verification margin. This stopping rule
can take more updates than v13's earlier-attempt policy.

A naive independently rounded cache is formally refuted: stored score zero can
coexist with true residual score two. The final verifier rejects it. General rounded
selective updates require a new cache-error invariant and remain an extension.

## Reproduce verification

The portable runtime is Linux-based and can be used under WSL on Windows. Its
large binaries are separate from this source release; restoration metadata is
included. Pins: Lean 4.34.0-rc2, commit 6a10ac8c22beadecabdbb0919c2b50214762f91d;
mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06. All Lean processes use one thread
and warnings as errors.

```bash
python3 checks/rebuild_release.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

This removes active project compiled caches, recompiles MODULE_ORDER.json, runs
negative controls and exact cache diagnostics, checks source/log/output/dependency
receipts and all axiom lists, and joins benchmark outputs with compilation evidence.
Pinned mathlib caches are reused. It does not download dependencies.

For a new exported instance, first run `python3 checks/build_inventory.py`, then
rebuild. The seal requires successful receipts after the recorded clean-build start.
The axiom allowlist is propext, Classical.choice and Quot.sound. Declaration counts
include support lemmas and benchmark certificates, not independent discoveries.

## Evidence and practical limits

PROOF_NOTE.md describes the exact theorem chain. SELF_REVIEW.md records the
adversarial self-review. FAILURE_LOG.md preserves failures and corrections.
FINAL_VERIFICATION_RECEIPT.json records the clean build and complete axiom coverage.
BENCHMARK_REPORT.md gives total producer, export and Lean-checking costs.

The controlled seven-case benchmark uses dimensions at most eight, five measured
repetitions after warmup, the same exact backend/tolerances, and an efficient full
Richardson baseline. Cached and recomputed selective runs return identical gains.
The cache makes selective iteration cheaper, but it does not establish an overall
speed advantage over the full-update baseline. Final verification/output and proof
checking dominate much of this tested range. No practical scalability claim follows.

LITERATURE_COMPARISON.md identifies strong prior overlap in block greedy selection,
caching, pathwise Gaussian conditioning, Wasserstein approximation and formal
arithmetic certificates. The delivered contribution is the checked integrated
artifact. Literature priority or a breakthrough claim remains unestablished.

Sequential filtering, changing packet hierarchy/model, uncertain measurements,
hardware floating point, rounded selective updates, parser refinement and sampling
are separately named extensions, not silently included in version 1.0.0.
