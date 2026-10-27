# Precision closure for certified Bayesian inference

**Checked release v0.1.0**

This release proves quantitative precision sufficiency for the existing outward
rounded evaluator and total correctness of a hybrid exact Richardson solver plus
rounded verifier. It also proves total correctness of an early precision-search
variant with a guaranteed finite fallback.

## Main guarantees

For a fixed valid exact factor-coded Gaussian model and complete self-adjoint
rational packet families:

- The actual rounded certificate score is bounded by its exact counterpart plus
  a computable coefficient times 2^(-p).
- Strict exact-certificate slack yields a computed sufficient precision, valid
  for every larger precision.
- For every positive rational tolerance, the hybrid solver manufactures slack,
  chooses sufficient precision, and returns a Gaussian approximation with an
  actual-posterior Wasserstein-2 tolerance theorem.
- A finite list of cheaper precision probes may precede the sufficient fallback;
  the first passing result remains sound and the schedule is guaranteed to return.

See PROOF_NOTE.md for the exact hypotheses and limitations.

## Exact input and arithmetic contract

Input model data are H, prior factor L, noise factor N, positive noise floor σ,
mean m, observation y, and complete packet projectors. They represent
P=L Lᵀ, R=N Nᵀ+σI. Integers and decimal/fraction strings mean exact rationals.
JSON floating-point values are rejected. Singular priors and rectangular H are
allowed. The main Lean theorems cover arbitrary finite index types; the Python
producer has explicit dimension and resource caps.

Gain updates are exact rational operations. Certificate centers/radii use dyadic
outward rounding, unbounded integer parts, and exact terminal comparisons.
Neither unknown input uncertainty nor IEEE-754 behavior is certified.

## Run the proof-producing example

From this directory, using Python 3.10 or newer:

```bash
python checks/hybrid_solver.py examples/solver_scalar.json --output results/my_scalar.json --emit-lean Komorebi/MyHybrid.lean --namespace MyHybrid --try-precisions 4 12
```

The producer reports PASS_HYBRID_PROVISIONAL, not a completed formal proof. Compile
the exported module with the pinned portable runtime to obtain the instance proof:

```bash
python verify_blocks.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --modules MyHybrid --timeout 120
```

The required project dependencies must have been compiled first as below.
The exact mathematical input certified is the input embedded in the generated
Lean source. Parser/exporter fidelity and external data correspondence require
inspection; they are not asserted by this proof.

Without --try-precisions, the program uses the computed sufficient precision
directly. With a finite probe list, it tries those values then the computed
fallback. A resource limit produces RESOURCE_LIMIT and no success proof export.
A failed check is not evidence that the true posterior error exceeds tolerance.

## Reproduce the formal checks

Required pins:

- Lean/Lake 4.34.0-rc2, Lean commit 6a10ac8c22beadecabdbb0919c2b50214762f91d.
- Mathlib aeb72f1e9981b6d35b426b16dca7759be3e7ba06.
- One Lean thread and warnings treated as errors.

The portable runtime is preserved separately and is not duplicated in this ZIP.
The active source order is MODULE_ORDER.json. Rebuild all modules, each in a
separate bounded Lean process, using:

```bash
python verify_blocks.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2 --timeout 120 --clean
python checks/negative_controls.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
python checks/test_precision_closure.py
python checks/seal.py --runtime /path/to/Komorebi_Portable_Lean_4.34.0-rc2
```

The independent diagnostics additionally require SymPy; the run recorded here
used SymPy 1.14.0. The core producer uses only the Python standard library.
To avoid an outer execution cap, pass bounded dependency-ordered module groups
with --modules instead of launching a long tool invocation. Failed or interrupted
runs do not count as proof checks. The verifier preserves actual attempted source
snapshots and logs under audit/.

checks/seal.py audits successful receipts and source/output/dependency hashes;
it does not itself rerun Lean. The all-declaration audit source is
Komorebi/PrecisionClosureAxiomAudit.lean. No official Mathbox manifest-validator
execution is claimed; that executable was unavailable in this environment.

## Verification summary

83 active modules passed, including 64 unchanged inherited modules freshly checked.
386 theorem/lemma declarations were axiom-audited, of which 82 are new in this
release. All axiom lists are contained in propext, Classical.choice, Quot.sound.
No active placeholders, custom axioms, unsafe proof shortcuts, or native_decide.
The active dependency-slice counts are not cumulative discovery counts.

Three concrete program instances are kernel-checked: scalar hybrid, singular
rotated two-state hybrid, and scalar early-precision hybrid. Independent exact
matrix diagnostics passed 9,651 assertions and 14 input/export rejections.

## Main source files

- PrecisionBudget / PrecisionEnergy: quantified scalar radii and energy inflation.
- PrecisionMatrix / PrecisionModel: the actual rectangular arithmetic graph.
- PrecisionScore / PrecisionSelection / PrecisionCompleteness: score bound,
  computed bit count, and successful rounded certification.
- HybridPosteriorSolver / HybridPosteriorGuarantee: executable hybrid and its
  actual-posterior successful-termination theorem.
- TaggedPrecisionSearch / HybridPrecisionSchedule: early precision probes with
  a sufficient fallback.
- GeneratedHybridScalar / GeneratedHybridRotated / GeneratedHybridScheduled:
  executable return equations and actual-law guarantees.

## Next proof boundary

Control additive roundoff in actual gain updates and certify their precision
policy. The present completion intentionally retains exact gain iteration.
Model-changing adaptation, sequential filtering, verified external parsers,
hardware floating point, and performance or literature novelty remain separate.
