# Proof and continuation protocol

Use current root CONTINUE_HERE.md for authority. Historical root files remain
unchanged snapshots and cannot override later checked evidence.

A theorem is checked only after its exact final source compiles under the pinned
Lean/mathlib environment, without placeholders, custom axioms or native proof
shortcuts. Audit every active theorem's axioms, source and compiled-output hashes,
and direct dependency hashes. No numerical case or Python success establishes a
universal claim. Keep failed and interrupted attempts distinct from final checks.

Use bounded, sequential modules with warnings as errors and one Lean thread.
Don't share a cache between competing builds. Do not change a checked source
without rebuilding and auditing its affected dependency closure. The archive
manifest verifies bytes; it is not a substitute for kernel verification.

Preserve singular-prior scope, positive observation-noise floor, exact rational
input semantics, explicit-versus-canonical posterior quantifiers, self-adjoint
versus algebraic projector distinctions, and coupling-cost versus optimal-distance
distinctions. Positive-tolerance exact solver success is not floating-point
stability, a complexity guarantee, monotonic true error or global optimality.

Return a durable successor checkpoint after new verified work, preserving all
inherited checked-release files and archiving superseded root controls. Record
actual successful and failed executions and all remaining assumptions. Do not
promote numerical enclosures, uncertain-input semantics, sequential filtering or
literature novelty before those exact obligations are proved.
