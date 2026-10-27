# Route 029: continuous local conditions up to kernel conjugacy

Base: exact v0.28 Continuous Local Gluing archive
SHA-256: 35043bbef695875f2f1316a2313dadab77d7b23ab5a28660c3bd735ae673d5f0

## Target contract
For a continuous representation with discrete coefficients across a square-zero
ring extension and an arbitrary indexed family of continuous local group maps,
construct the actual obstruction to one continuous lift matching specified local
lifts up to independent conjugators reducing to one. Include local degree-zero
cochains in the boundary, unlike the strict v0.28 problem. Do not assume order
invertibility, finite source, openness of local maps, a simultaneous section,
a global representation lift, or vanishing of a cohomology group.

## Outcome to verify
(1) A constructed class vanishes iff that ORIGINAL lifting problem has a solution.
(2) After an absolute primitive, the secondary obstruction lies in the cokernel
of restriction on continuous H1, not strict Z1; it is independent of primitive.
(3) The H1 cokernel injects into the degree-two gauge obstruction quotient,
with image exactly the kernel of forgetting local data to absolute H2.
(4) Replacing prescriptions by kernel-conjugate ones preserves the class.
(5) Test a strict-nonzero/gauge-zero example and an absolute-zero/gauge-nonzero example.

## Convention
d0(x)(g) = g.x - x; d1(b)(g,h) = g.b(h) - b(gh) + b(g).
Defect pair: (c,a) with d a_i = res_i c.
Boundary: (b,(x_i)) |-> (d b, (res_i b + d x_i)).
Corrected representation: (1-b(g)) r(g).
Local comparison: t_i(h) = (1+x_i) lift(alpha_i(h)) (1+x_i)^(-1).
Cohomology is the explicit continuous inhomogeneous quotient, not an unproved
identification with Mathlib's separate homogeneous API or a Selmer complex.

## Scope and expected failure
The universal vanishing claim is false. The Z/4 character triple from v0.28 must
remain nonzero even after allowing gauge. The Z/9 matrix example must become
zero gauge obstruction despite its nonzero strict obstruction.

## Accepted checkpoint
All eight additive modules and twenty unchanged source dependencies passed a clean
source replay; the separate axiom audit passed all seventy named constants.
The exact finite corroboration also passed. This closes the stated internal route,
not the arithmetic local-condition vanishing goal.
