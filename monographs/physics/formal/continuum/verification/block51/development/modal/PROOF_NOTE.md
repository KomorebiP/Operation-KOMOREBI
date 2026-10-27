# Modal perturbation proof

Base: checked generator source in the Block 49 project, with generator overlay
`ee721cc3ab78f500bab87c1edb358be8b30a0892e7047c9e9cb5aa31a6d51499`.

For self-adjoint bounded spinor endomorphisms A and B, let U_A(t) = exp(-itA).
Assume the actual pointwise estimate ||(A-B)v|| <= D ||v|| for every spinor v.

For fixed real t and spinor v, set F(s) = U_A(t-s) U_B(s) v.
The right-ordered derivative for U_A and the left-ordered derivative for U_B give

F'(s) = i U_A(t-s) (A-B) U_B(s) v.

This identity does not commute A with B. Each derivative theorem follows from
the ordinary Banach-algebra exponential derivative, with the scalar time
parameter acting on its own fixed generator.

Both evolution maps preserve norm, so ||F'(s)|| <= D ||v||. The real mean value
estimate on the convex set R gives

||U_A(t)v - U_B(t)v|| <= |t| D ||v||.

The endpoint argument is unchanged for negative t and includes t=0.
This is formal support for the manuscript's Duhamel bound. The argument uses
an interpolation derivative instead of a Bochner integral, with the same
constant and domain. It is a theorem for a single finite-dimensional spinor
mode; the infinite-mode summation belongs to the separate rates module.

Compilation status is determined only by the retained attempt receipts.
