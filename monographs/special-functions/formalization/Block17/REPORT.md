# SF-LEAN-B17: guarded exact majorant specification

The bounded first-small ladder and guarded reverse-fold contract is proved
over exact rationals. A successful return B supplies a trace of length k no
larger than the step budget, terminal Q^k*R<1, and
B=rationalDiskMajorant Q k R. Under strict positive contractions and R>=0,
B bounds the actual canonical complex functions on |z|<=R. For S>x>=0,
the exact endpoints built from the Block16 array polynomial and
B*(x/S)^(2N+3) enclose the actual real component whenever the guarded
majorant at S succeeds. Last index N still retains N+1 coefficients.

The trace stops at the first radius strictly below one. A radius equal to
one requires a step, and a zero step budget then fails. Trace success is
equivalent to the trace relation plus length<=budget. Adequate mathematical
fuel gives a successful ladder; it does not guarantee a fixed step or bit
budget succeeds. Step errors and bit errors are explicit distinct results.

The reverse fold checks the size predicate after every computed update.
Its successful value is the ordinary foldr; success is characterized by
that value and the conjunction of all post-update checks. Bit failure is
equivalent to a failed check. The terminal seed is not checked. For Q=1/2,
R=2 the ladder is [2,1], terminal 1/2, seed 2/3 and bound 500/81. Forward
folding would give 757/81 and is rejected by an exact control. A small-radius
seed can exceed the bit limit and still be returned, as in the source.

The concrete rational size uses max of numerator-absolute-value and positive
denominator binary widths, with width(0)=0 and width(n)=log2(n)+1 otherwise.
An abstract checked-input wrapper preserves scale rejection before radius
rejection, zero-radius return before resource validation, step-input validation
before bit-input validation, and positive bit bounds. Some 0 is a valid step
budget. None represents an invalid nonnegative-integer resource input; it
does not implement a Python runtime type checker. Fraction conversion failures
and mappings of bool/int/negative/exception objects remain outside the model.

Authority: Appendix J, monograph/sections_v11/coupled_lab_full.tex lines
62-87, and research/coupled_lab.py:disk_majorant. Mathematical base `200a2798532028f863f923028cb0ead95563975a`;
editorial publication parent `0eae1fe6a4bf55db27af69ef40b405643aa2e5a9`. Python and manuscript sources are
assessed at pinned hashes, not used as trusted proof leaves and not edited.

There are **30 new theorem declarations**, for **465 registered names**.
All **66 fresh replay steps** pass: seventeen compilations, audits and
same-kernel replays, 426 fresh coupled theorem axiom audits, four expected
rejections and one positive fixture. The finite core's 39 names retain
inherited evidence; Mathlib imports are cached, not freshly rebuilt or replayed.
Allowed axioms are propext, Classical.choice and Quot.sound. Review is self-review.
Formal I/O records 59 inputs, 67 packaged outputs, seventeen generated objects
and 39 staging copies; assessment I/O has 37 inputs and two outputs. Development
source/log pairs and preflight diagnostics are separate from accepted evidence.

This completes the registered **Lean guarded-algorithm specification**.
Actual Python interpreter, Fraction, comb/factorial/bit_length implementation,
type/exception classification, list mutation and certified_evaluation dictionary
correspondence remain open. Next: compose the proved array and guarded-majorant
interfaces into a typed evaluation-result specification, then assess the source
call path and exact metadata/endpoints with explicit runtime assumptions.
Other J degree/denominator/symmetry, ancillary F/H, I and A-E remain.
