# Block 28 proof boundary

PROVED: full-transition basis-column relation; finite support propagation from the
actual initial coefficient support; inflationarity and monotonicity; stabilization
within the number of profile positions; leastness among closed coordinate sets;
exact equivalence with invariance of the entire coordinate-supported module;
zero-extension injectivity; exact restricted transition, initial and ordered-word
simulation; retained-entry matrix formula; integration inside Block 27's actual
variable-width profile; canonical all-coefficient output and positive-precision
output compatibility; exact ambient cardinality, nonincrease and strict slot
reduction when a position is omitted; a certificate retaining Block 27.

The actual mask assumptions are unchanged: prime p, positive r, integer masks A,B,
p not dividing B(0), and equal mask constants in ZMod(p^r). The canonical series is
constructed by inherited theorems. There is no supplied-series oracle. Generic
coordinate invariance only uses a commutative ring and finite position type. In
that generic theorem the alphabet can be any type; the actual digit alphabet is
Fin p. All position indexing is inside the already certified degree profile.

A column is computed from the complete routed/summed transition. Intra-column
branch cancellation is included. Correlation between different input coefficients
is NOT an excuse to remove a column needed by an arbitrary vector on the retained
positions. Ring zero divisors are allowed. The correlated ZMod5 and nilpotent ZMod4
witnesses demonstrate that least coordinate support can strictly exceed the support
of the particular initial orbit.

NOT PROVED: least invariant submodule under arbitrary linear relations; smallest
reachable automaton; minimum state space after changes of basis; a verified
optimized executable Lean polynomial engine; a Python/Lean executable refinement;
time, bit, memory, or analytic convergence bounds. The formal restricted map is
specified through the predecessor embedding, with a separately proved retained-
entry sum formula. Neither that formula nor a smaller mathematical state space is
a wall-time/memory improvement theorem. Precision compatibility concerns outputs,
not a common coordinate space across precisions. Historical checkpoint and quota
executables remain unchanged.

Verification uses the exact inherited Lean4.34.0-rc2/mathlib cache. leanchecker uses
Lean's own kernel, not a second implementation. The stable4.34.0 compatibility lane
and independent human/kernel review remain unperformed. No novelty claim is made.
