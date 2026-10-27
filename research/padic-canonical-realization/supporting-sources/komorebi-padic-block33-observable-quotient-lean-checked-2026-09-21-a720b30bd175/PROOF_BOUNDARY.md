# Block33 proof boundary

PROVED: linear full-word observations; greatest silent invariant submodule;
descending kernel/preimage construction with exactly word-length < n semantics;
finite stabilization within b rounds for an ambient module of cardinality p^b;
short distinguishing words; quotient digit maps and output; exact projection,
word, and output laws; quotient equality iff full future-output equality;
observability; preserved linear reachability; unique surjective comparison from
other silent-kernel quotients of the SAME system; exact cardinality identity;
actual-mask output linearity and all-coefficient correctness; finite observation
horizon for the actual reachable module; cyclic presentation existence and
signature uniqueness via Block32; positive-precision output compatibility;
proof-carrying actual-mask certificate and nonfield/restriction examples.

Actual masks retain p prime, r>0, integer A,B, p not dividing B(0), and
A(0)=B(0) in ZMod(p^r). The canonical F is inherited and constructed, not supplied.
Generic observation theory allows arbitrary commutative rings and arbitrary
alphabets. The cardinality bound adds finite V, prime p, and |V|=p^b. Actual digit
alphabets are finite. Counts are cardinality exponents, not field dimensions.

NOT PROVED: cross-realization universal comparison or uniqueness among ALL linear
realizations of a given word behavior; minimum DFA; canonical literal matrices;
new cross-precision state morphisms; executable refinement of the exact Python
HNF/Smith engine to Lean; efficient noncomputable Lean polynomial evaluation;
wall-time/bit/memory guarantees; analytic convergence; novelty or priority.
Linear reachability is span, not enumeration of the actual deterministic orbit.
The minimum-cardinality result is restricted to silent invariant quotients of the
fixed source module. Broader minimality must not be inferred without its theorem.

Toolchain is the exact recovered Lean4.34.0-rc2 and pinned cached mathlib.
Project sources are freshly compiled, dependency caches are not independently
rebuilt. leanchecker is the same Lean kernel, not an independent implementation.
Stable4.34.0 compatibility and independent human/kernel review remain unperformed.
