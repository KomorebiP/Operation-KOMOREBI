# Beal research — Block 73
## Nontriangular deformation and a delayed tame lifting obstruction

Release7.3.0. Sole predecessor: exact Block72 archive in predecessor/.

This block retains the actual lower-left7*beta at depth one and formulates the
same global mod49 representation as an adjoint cocycle. The fixed-seven period
valuation is a nonhomogeneous local condition on that GLOBAL cocycle, not a
fictional global upper Kummer lift.

An upper correction7*xi*E12 preserves every mod49 trace and both residual endpoints.
But a local representation with F=I+7A and T=I+7M can lift to mod343 only if
[A,M]=((Q-1)/7)M mod7. At actual beta support M21 is nonzero. A nonzero unramified
upper correction leaves inertia unchanged and violates that identity.

Every frozen pattern supports883, where phi,3,sqrt5 are seventh powers and7 is
not. Therefore a [7] correction cannot freely adjust the fixed-seven valuation
while keeping the actual inertia and next-level lift. In a precisely stipulated
fixed-trace/fixed-inertia fibre the valuation is rigid. Its value is NOT proved
zero, and the complete global fibre has NOT been solved.

NONE of the eight patterns is eliminated. The old local positive Frey families
remain valid. New local matrix controls show that the remaining local algebra
is nonempty, without constructing a global Frey representation.

Run from this directory, with the report outside it:

    python -B verify.py --report ../Block73_Replay.json

Add --replay-predecessor to run the immediate Block72 DEFAULT verifier as well.
This is not the entire historical chain. No point counts, Lean compilation, or
independent mathematical review are claimed. See work73/REPORT.md and proof notes.
