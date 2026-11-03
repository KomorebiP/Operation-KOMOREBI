# SF-LEAN-B17 target contract

Mathematical base: published SF-LEAN-B16, Git
`200a2798532028f863f923028cb0ead95563975a`.
Publication starts from its editorial descendant
`0eae1fe6a4bf55db27af69ef40b405643aa2e5a9`.
Authority: Appendix J, coupled_lab_full.tex, lines 62-87, and
research/coupled_lab.py:disk_majorant, lines 56-89.

Prove the mathematical bounded-algorithm contract over exact rationals:
the first-small-radius ladder, its budget/trace equivalence, adequate fuel,
reverse-fold equality to rationalDiskMajorant, per-update size failure and
explicit step failure. Successful returns must bound the actual canonical
complex functions and give the existing exact real endpoint enclosure.
Analytic consequences retain strict positive contractions and nonnegative
target radius, with S>x>=0 for endpoints. The ladder/trace identities themselves
do not require contraction; success supplies the terminal condition.

Model validation using exact rational scales/radii and optional natural
resource inputs. Invalid scale tags precede negative-radius errors; radius
zero returns before resource validation; nonzero steps validate before bits.
Some 0 is valid for the step budget and invalid for the bit bound. None is an
abstract invalid-input tag, not a certified Python runtime type classifier.
Define the mathematical rational size by numerator absolute value and positive
denominator binary widths (zero has width zero). Checks follow fold updates;
the terminal seed is unchecked. A bit error is not a weaker successful bound.

Primary route: inductive first-small trace and budget recursion -> terminal
power identity and foldr/fuel identity -> success and failure characterization
of a guarded reverse fold -> inherited actual-function certificate. First
discriminators: radius exactly one, max_steps=0, Q=1/2,R=2 (ladder [2,1]),
and 0<R<1 with a seed exceeding the bit limit. For [2,1] and seed 2/3, the
correct reverse fold is 500/81; forward folding would give 757/81.

Alternative route: a direct while-loop state invariant carrying the accumulated
prefix and remaining step count. Deferred if the trace route closes this
contract; resume when proving source-language execution refinement. Attempt
to falsify wrong fold orientation, mandatory seed checking and omitted success
hypotheses through exact rejection controls. These variants are not substitutes
for the source contract. Bounded output sampling cannot prove all-input soundness.

This certifies Lean's exact algorithm specification and abstract input tags.
Actual Python interpreter, Fraction, comb/factorial, bit_length implementation,
type/exception-object classification, list mutation and returned dictionary
correspondence remain separate. Do not label this full Python refinement.
No Python or manuscript edits are needed. Preserve all previous blocks, original
parent guidance bytes and dated evidence. Maintain live guidance only under
current/. Review is self-review. Update I/O, GitHub and .io after verification.
