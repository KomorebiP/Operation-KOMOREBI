# Continuation — Sufficient Resolution v0.1.0

Read `README.md`, `THEOREM_GUIDE.md`, and the release verification report first.
This is a new, independent formalization block. It does not replace or recompute
the theorem census of Papers I–XII or earlier inference releases.

Production source order:
1. ExactResolution
2. Compression
3. Globalization
4. ObstructionTransport
5. Behavioral
6. Examples

All are in `Komorebi/SufficientResolution/`. The exact toolchain and dependency
pins are retained. Use `scripts/verify.py` with the preserved portable runtime.
Do not mistake compiler logs for proof statements or negative controls for library
sources. Do not add a custom axiom to make a missing theorem compile.

## Recommended next block

Formalize exact discrete-time elimination with visible/hidden blocks, derive the
memory-kernel recurrence, and connect its zero-feedback criterion to the existing
compression defect. First prove the all-depth recurrence. Then add a genuinely
finite Cayley–Hamilton certificate under an explicitly finite-dimensional hidden
space. Keep prepared hidden initial state separate from arbitrary hidden initial
state. Do not silently promote this discrete result to a continuous-time Volterra
or matrix-exponential theorem.

A second useful direction is proving that the behavioral quotient comparison is
surjective and deriving the finite-dimensional minimality inequality and closure
iteration termination bound. The current kernel-inclusion theorem is already
proved; the finite dimension claim is not yet in the contract.

A third direction is the Hilbert-space obstruction decomposition, keeping the
compatible-but-unrealizable component separate from local inconsistency and
keeping the smallest-positive-singular-value assumption explicit.

## One-line continuation instruction

Open this ZIP, read CONTINUE_HERE.md and the theorem guide, rerun the pinned verifier,
then extend the exact discrete-memory bridge while preserving all stated boundaries.
