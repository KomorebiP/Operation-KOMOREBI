# Block 25 failed approaches and repairs

## Incorrect phase group

The earlier candidate used `ℂˣ`, the group of all nonzero complex scalars, while describing it as the unit circle. This was mathematically wrong for Hilbert unitarity. Multiplication by `2` is invertible but multiplies squared norm by `4`.

**Repair:** replace the phase type by Mathlib's genuine `Circle` and prove phase preservation from the unit-modulus group law.

## Boolean channel assignment

The first position-space candidate assigned each spin component permanently to a positive or negative channel. That cannot represent the three noncommuting directional Clifford projectors.

**Repair:** implement each spatial direction with its own projectors `(I ± α_i)/2`.

## Recursive tower elaboration failures

Initial recursive definitions of dyadic `Fintype` instances failed because the recursive instance was not available to typeclass inference and because the class-valued helper was semireducible.

**Repair:** construct the recursive `Fintype` value explicitly, mark the helper `instance_reducible`, and install a separate level-indexed instance.

## Raw counting-measure isometry is false

A two-child replication does not preserve the unweighted finite sum. It doubles it.

**Repair:** prove the doubling theorem and define the fine-level inner product with half cell measure. A negative control verifies that the false raw-isometry claim is rejected.

## Monolithic axiom audit timeout

A single audit importing the full 124-module top-level library exceeded the external command window before returning a result. It was not counted as evidence.

**Repair:** preserve the checked parent audit by byte identity and split the 179 new declaration checks into three direct-import batches. Every batch completed, and only `propext`, `Classical.choice`, and `Quot.sound` were observed.

## Cumulative build command windows

Several first-pass cumulative builds exceeded the external command window while populating missing parent object files. No timeout was counted as a successful verification.

**Repair:** build the missing checked-parent modules in explicit dependency groups, then rerun the cumulative target. The final cumulative build completed successfully.
