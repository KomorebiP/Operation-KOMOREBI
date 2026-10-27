# Continue after Block 28

Authoritative checkpoint: Block28 Support Closure. Read REPORT.md,
PROOF_BOUNDARY.md, RESULTS.json, COMPUTATION_CONTRACT.md, DEVELOPMENT_FAILURES.md,
and the four added modules CoordinateSupport, ProfileSupport,
SupportMaskAutomaton, SupportExamples. Use the exact pinned RC2 runtime and mathlib.
Run read-only verify_release.py before edits; rebuild on a separate working copy.

Closed: least invariant coordinate set for the fully summed transition columns
inside the least degree profile; finite stabilization, exact embedding, all-word
and canonical coefficient output, cardinality and precision-output comparison.
Do not reinterpret this as orbit support, a minimum invariant submodule, or minimum
automaton size. Preserve the correlated and zero-divisor counterexamples.

Next mathematical target: coefficient-ideal / valuation-aware coordinate closure
over ZMod(p^r). A retained coordinate may still be restricted to p^a R rather than
all R. Treat a=r as the zero ideal. Transport valuations using actual summed matrix
entries; prove leastness within coordinate-ideal products, not arbitrary correlated
submodules. The nilpotentSystem witness should be a decisive test: coefficient 2
in ZMod4 times matrix entry 2 is zero. Do not silently assume a field or perform
illegal division. Preserve the current support machine as the verified predecessor.

Alternatively, an explicitly requested engineering block can verify worklist or
early-stop support iteration against the current fixed-round specification. No
shared dependency cache may be deleted. Stable4.34.0 remains a separate lane.
