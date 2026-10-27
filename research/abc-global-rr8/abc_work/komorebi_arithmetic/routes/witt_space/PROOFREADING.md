# Local mathematical prose and notation self-review

Scope: this route's new PROOF_NOTE.md and CLAIMS.md, with their source
definitions and coefficient rings. No predecessor file was edited.

The construction uses k=F_p, R_N=Z/p^N and K_N=R_(N-1). Division by p
is through the specified injective map K_N->R_N. The p=2 and N=1 cases
are retained. The zero-tail symbol t_0 was defined explicitly during proof
construction. The positive multiplication diagram is Set-valued; only the
separate additive diagram receives the additive quotient construction.

Routine prose edits in the final conservative pass: none.
Mathematical-token clarification: the residual product in Section 4 is now
explicitly product_(f:v->w) F_N(v). These are the targets of the
contravariant restrictions, not F_N(w). The displayed differential already
forced this codomain. The independent reviewer identified the ambiguous
phrase and checked the clarified formulation; no new hypothesis or proof
argument was introduced by this wording change.
The correctness review also made the already assumed equality D_Nh=j_N(C)
explicit in the forward proof of (10). Its zero residue-arrow component,
together with protection, forces the vertex correction to be p-divisible.
Protection alone does not force that statement at unprotected vertices.
This is recorded as a proof clarification under correctness review, not
as an unsupported general assertion about every protected correction.
Proof construction and its correctness review remain separate from this
prose pass. The review records both exact revisions.

Validation: direct rereading of local notation, quantifier and reference
consistency. No LaTeX build, numerical experiment or Lean compilation was
needed or performed for these Markdown proof files. The source-level
framework identity is recorded in INPUTS.json. The global height estimate
remains an explicit open obligation, not a proofreading issue.
