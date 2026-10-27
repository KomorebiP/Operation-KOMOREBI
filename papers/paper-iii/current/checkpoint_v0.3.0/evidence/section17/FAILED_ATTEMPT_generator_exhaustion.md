# Preserved test harness failure and repair

During addition of finite families of complete but non-idempotent operators,
the `nonidempotent_complete_resolution_expansion` control **initially failed**.
It was a test implementation fault, not a mathematical counterexample:
`vsum(vectors, dim)` iterated the same generator separately for each output
coordinate. The first component exhausted that generator, so later output
coordinates incorrectly summed an empty collection.

The implementation was corrected by materializing the terms once at the start
of `vsum` (`vectors = list(vectors)`). The modified suite then passed all 2622
assertions, including 45 complete/non-idempotent reconstruction controls.
The deliberately invalid mathematical controls still fail as intended.

This repair is independently auditable in
`tests/section17/exact_section17.py`. It does not affect any Lean theorem,
prior accepted Section 16 source, or mathematical identity.
