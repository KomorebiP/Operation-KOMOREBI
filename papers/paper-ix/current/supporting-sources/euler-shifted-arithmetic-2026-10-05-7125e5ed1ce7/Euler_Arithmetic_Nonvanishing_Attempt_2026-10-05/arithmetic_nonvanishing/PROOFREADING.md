# Final mathematical proofreading

Mode: self-review of files written in this focused attempt.

* Root-authored target, current summary, state, no-recurrence proof and
  unit-filter report were re-read against the exact formulas and the
  independent review.
* The two different uses of the kernel variable are explicitly localized:
  the structural route uses g(z)=z coth z, while the unit route uses
  t=z^2 and writes g(t)=sqrt(t)coth(sqrt(t)). Thus their arguments 2z
  and4t denote the same doubling operation.
* The half-shift sign is -3, not the other square root of9. The reviewed
  commutator and resulting coefficient1/3 use this branch consistently.
* The Riccati quadratic term retains t^r because its tail is shifted.
* Every summary distinguishes the odd-valuation/unit15 counterexample to a
  candidate lemma from a counterexample to Euler simplicity. The constructed
  actual critical value is nonzero.
* The full-family noninterpolation theorem is distinguished from an unproved
  scalar critical-value interpolation.
* Routine edits: local wording and notation clarification only, including
  distinguishing a separate replay using inherited code from an independent
  Bernoulli implementation.
* Mathematical-token corrections from proofreading: none. Substantive
  mathematical derivations and checks are recorded in the separate proof
  audit, not treated as editorial corrections.
* Validation: exact arithmetic checks and independent proof review, with
  current manifest roots in MANIFEST_ROOTS.json. No LaTeX or Lean compilation
  was required or performed.

The remaining nonvanishing implication is a proof gap, not a proofreading
issue, and is preserved explicitly in the current state.
