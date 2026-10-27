# Outward-rounded posterior certificates — v0.1.0

**CLOSED / LEAN CHECKED for the stated dyadic enclosure contract.**

The mathematical input is the exact factor-coded rational Gaussian model inherited
from v8. The new evaluator rounds scalar centers and absolute-error radii to p
fractional binary bits, encloses the exact model expressions throughout rectangular
matrix products, and derives local packet-energy and innovation-energy bounds.
Successful acceptance implies a Wasserstein-2 bound on the actual Bayesian
posterior versus the represented gain's Joseph Gaussian approximation.

This is not a hardware floating-point implementation: integer parts are unbounded,
terminal energy accumulation and tolerance comparisons are exact rationals, and
IEEE-754 exceptions/overflow are not modeled. Measurement uncertainty is not
silently equated with arithmetic rounding. See PROOF_NOTE.md for the full contract.

## Main results

- `Komorebi.RoundedPosterior.residualBall_encloses` proves the full residual enclosure.
- `Komorebi.RoundedPosterior.roundedCandidate_valid` proves all computed upper bounds.
- `Komorebi.RoundedPosterior.rounded_tolerance_bounds_posterior` connects the evaluator
  to the actual-law tolerance.
- `Komorebi.RoundedPosterior.rounded_return_bounds_posterior` proves successful-return
  soundness without assuming input validity before the checks.
- `Komorebi.RoundedPosterior.precision_search_bounds_posterior` handles a finite
  precision schedule. It is soundness, not a general precision-success theorem.

The existing exact Richardson solver and earlier probability theorems are not
replaced. A rounded update does not inherit ideal exact-arithmetic termination.

## Run a rounded certificate and emit its Lean instance

From the focused release directory, using Python 3.11 or newer:

```bash
python checks/rounded_certificate.py examples/rounded_scalar.json --output results/my_scalar.json --emit-lean Komorebi/MyRoundedScalar.lean --namespace MyRoundedScalar
```

The JSON root fields are exactly `model`, `gain`, `precisions`, `epsilon`. The model
schema is shown in both examples. Values are exact integers, fraction strings, or
exact decimal strings. Raw JSON floats are rejected. The producer supports positive
dimensions and packet counts at most 8, 1..16 precision attempts, and p=0..512.
These are input checks, not a proved OS-memory or arithmetic bit-size bound.

`PASS_ROUNDED_PROVISIONAL` is not itself a proof. Compile the generated module to
check its actual rounded-evaluator outputs and apply the generic Lean theorem.
`NOT_CERTIFIED` (exit 2) is a failed certificate attempt, not proof that the true
posterior error exceeds epsilon. Invalid input is rejected explicitly.

The parser and exporter are not formally verified. The exact data in the emitted
Lean source is the mathematical input being certified. A machine-produced finite
binary gain can be represented by exact rational literals, but its conversion and
correspondence to an intended external array must be checked separately.

## Reproduce the formal checks in small blocks

Use the preserved portable runtime, Lean 4.34.0-rc2 with mathlib
`aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. Set RUNTIME to its extracted directory.
`MODULE_ORDER.json` is dependency-ordered, not an alphabetical compile order.

```bash
python verify_blocks.py --runtime "$RUNTIME" --clean --modules
# Compile entries from MODULE_ORDER.json sequentially in bounded groups.
python verify_blocks.py --runtime "$RUNTIME" --modules RationalBall DyadicBall --timeout 40
# After all dependencies and proofs are checked:
python verify_blocks.py --runtime "$RUNTIME" --modules RoundedAxiomAudit --timeout 40
python checks/test_rounded.py
python checks/negative_controls.py --runtime "$RUNTIME"
python audit_integrity.py --runtime "$RUNTIME" --seal
```

Each source receives a separate Lean process and a receipt with exact source,
compiled-output and direct-dependency hashes. The negative controls are deliberate
invalid claims, kept outside active sources. The integrity seal checks successful
receipts; it is not a substitute for running Lean. The 42 inherited dependency
sources are unchanged; other historical program blocks are retained in the full
v9 continuation, not duplicated or freshly checked in this focused slice.

The producer needs only Python's standard library. Independent diagnostics also
use SymPy 1.14.0. No network, native proof evaluation or hardware floating-point
arithmetic is required by the certificate producer.

## Evidence

`FINAL_VERIFICATION_RECEIPT.json` and `AXIOM_AUDIT.json` record 53 active modules,
253 audited theorem/lemma declarations, including 68 new declarations. All audited
axioms are contained in propext, Classical.choice, Quot.sound. Declaration counts
include support identities and regressions, not independent discoveries.

The scalar test explicitly has zero rounded residual center and a nonzero exact
residual; its nonzero radius prevents a false zero certificate. Both the scalar
and rotated two-state examples reject p=4 and pass p=12 for their stated tolerance.
The actual scalar precision-search return is kernel-checked.

## Next boundary

Prove quantitative precision sufficiency with strict certificate slack, and then
control additive roundoff forcing in a rounded gain solver. IEEE-754 refinement,
uncertain model data, general interval covariance-floor certification, parser
verification, sequential filtering and complexity/performance claims remain open.
