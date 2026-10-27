# Route 028 — simultaneous continuous local prescriptions

Base: v0.27 Continuous Obstruction and Finite-Quotient Vanishing, exact archive hash in README.
Target: construct the actual continuous obstruction to one global lift satisfying an indexed
family of local representation prescriptions, and separate it from the absolute obstruction.

Success criterion: a proved equivalence between actual continuous lift existence with all local
restrictions and zero of a constructed cochain class; no assumed simultaneous provisional section.
A second target is to identify the additional gluing obstruction after absolute cancellation.

Decisive checks: a C2 x C2 example where every pair extends but the triple does not; a tame matrix
example where local conjugacies exist but literal gluing does not. Both are Lean checked.

Outcome: proved as written. A positive order-invertible finite quotient/local-family theorem is
also proved up to independent kernel conjugators, then pulled back continuously.

Unresolved: actual arithmetic local deformation condition and vanishing, general local gauge
complex comparison, coefficient-tower iteration, and automorphic carrier existence.

Self-review: checked signs against corrected lift (1-b)r, verified that strict mismatch uses Z1,
that the positive family theorem uses independent conjugators, and that finite examples fall
inside/outside order hypotheses as stated. No independent specialist reviewer was used.
