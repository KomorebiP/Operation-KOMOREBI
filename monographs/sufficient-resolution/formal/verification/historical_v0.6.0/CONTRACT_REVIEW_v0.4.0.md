# Mathematical contract review — Block 04

The target is an all-word perturbation bound for known linear models. It is not a
numerical experiment promoted to a universal statement. Every norm in the Lean
conclusions is the norm of an actual continuous linear map or its evaluated vector.

## Load-bearing checks

1. `ApproximateBounds.word_toLinearMap` identifies chronological operator words
   with the predecessor's algebraic definition. Concatenation reverses product
   order as required for chronological lists. Tests distinguish a noncommuting
   two-letter word from its reversal.
2. The exact residual is q T_w - U_w q. It is not a freely supplied error variable.
   The recurrence is proved by expanding this difference, and the finite sum has
   exactly length(w) actual transported defect terms.
3. The norm majorant includes both true and reduced growth rates. The readout
   defect O-Vq and readout amplification ||V|| are retained separately.
4. The scalar response includes empty words, equal rates, and zero rates. Its
   unequal-rate formula requires a != b. The stable denominator requires b<1.
5. Uniform contraction is a common operator-norm hypothesis, not a spectral-radius
   hypothesis and not a finite sample pass. No claim is made about automatic
   discovery of a common norm for a switched family.
6. Arbitrary reduced initial states have an extra term. The prepared state z=qx
   is a specialization, not silently imposed in the general initial-state theorem.
7. Two-stage models include both sources of discrepancy. Split coordinate
   re-encoding only requires J S=id; outputs are compared on embedded states,
   and no surjectivity onto the larger coordinate space is invented.
8. Sharp scalar realizations show the majorant can be attained. The unbounded
   example violates the true-growth assumption, not the contraction theorem.
9. The new analytic contracts do not automatically equip every earlier abstract
   algebraic quotient with a canonical norm. A bounded realization of q,T,U,O,V
   must be supplied when applying the quantitative theorems.
10. Standard Mathlib definitions and tactics are used. There are no custom
    syntax/notation extensions, custom axioms, placeholders, unsafe declarations,
    or native_decide invocations in the production sources.

## Verification scope

Source compilation, dependency HEAD revision checks, transitive axiom audits and
same-kernel replay are performed. Imported standard-library artifacts are reused;
no independent proof kernel or comparator challenge was used. Explicit theorem
signatures are saved separately for inspection. The standalone branch count
includes supporting lemmas and must not be interpreted as a novelty census.
