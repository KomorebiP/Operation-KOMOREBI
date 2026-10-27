# Independent review: total finite-witness search for native oracle enumerability

**Verdict: proved as written. No semantic or computability defect found.**

Reviewed source: `RealizationBoundaries/OracleEnumerationNormalForm.lean`.
SHA-256: `1f271d55166e8766314516e4e8aede4b7b852d646a57d5c50b6b50cb94d90d09`.

The exact final claim is: if a set is the domain of a partial function in Mathlib's native recursion semantics relative to the actual binary membership oracle, then it has a total oracle-computable natural-number witness verifier, with membership equivalent to existence of a successful finite witness. The proof does not assume this relativized normal form as an external input.

## Critical derivation

`OracleGraphSearch` requires a **total** test with a genuine `OracleComputable` proof and an exact graph equivalence for every input/output. The induction follows every native `RecursiveIn` constructor.

* Total primitive functions and the actual total binary oracle have direct graph verifiers.
* Pairing stores both child certificates and checks both actual output components.
* Composition stores the intermediate value and both child certificates.
* Primitive recursion stores base and transition states/certificates. The base is checked even for zero recursion length; every transition below the requested length is checked; the final state must equal the requested output.
* Minimization checks the child graph certificate at **every** stage up to and including the proposed answer, requires every earlier output to be nonzero, and requires the final output to be zero.

The last point retains the actual partial semantics. Divergence before a later zero cannot pass: the diverging earlier child has no successful graph certificate. This is stronger than checking only that a later stage returns zero or that no earlier *observed* zero was found.

The partial-recursion and partial-minimization trace dependencies were inspected directly in `OraclePartialRecursionTraces.lean` and `OraclePartialMinimizationTraces.lean`. They identify the literal native recursor and `Nat.rfind` membership semantics. In particular, the `Nat.mem_rfind` premise provides defined earlier values, rather than allowing divergence before the least successful stage.

## Finite encoding and totality

Trace decoding is a primitive-recursive total finite-list decoder with default entries. Missing/invalid entries do not create a gap: soundness checks every required child certificate and every required state equation even when a default value was supplied. A short trace can pass only if those values/certificates are genuinely valid. Completeness constructs a long-enough actual finite encoding by `finiteTrace_exists`.

Classical selections of child certificates and auxiliary state functions occur only in the existential completeness proofs. The total verifier does not call those selected infinite functions; it reads a finite natural witness and runs native bounded arithmetic/child tests. Its `OracleComputable` proof is derived from the concrete native recursion/composition operations.

Natural sums of verifier outputs are zero exactly when every bounded child check is zero. No cancellation or signed-encoding assumption is used. The minimization witness at answer zero checks the final child at stage zero and has no earlier-stage requirement, retaining the smallest boundary case.

The final domain-to-search theorem encodes the partial function's output value and graph certificate into one natural witness. Conversely, it decodes that pair and invokes graph-verifier soundness to recover actual membership in the partial function's domain. It therefore closes the exact domain/listing API bridge without treating a partial oracle graph as a decidable oracle.

## Verification and scope

`verification/development/OracleEnumerationNormalForm_independent_review.log` checks the exact pair/composition/recursion/minimization interfaces, the graph normal form and the domain-to-total-search theorem. Main axiom dependencies are confined to `propext`, `Classical.choice`, `Quot.sound`.

Five runtime branch checks passed:

* immediate zero minimization certificate accepted (test output 0);
* a later answer rejected when an earlier defined zero exists;
* a constant nonzero child rejected as a zero witness;
* a correct paired-child witness accepted (test output 0);
* a paired witness with the wrong second output rejected.

These are boundary checks, not substitutes for the universal Lean derivation. The independent kernel replay passed in `verification/development/OracleEnumerationNormalForm_independent_replay.log`.

No polynomial-time bound, effective decision of divergence, or standalone compiler that extracts a verifier from erased Lean proof objects is asserted. The theorem is the genuine existence/computability normal form needed for oracle computable enumerability.

Review provenance: separate-agent reading of raw definitions and trace proofs, reconstruction of all critical constructor cases, exact interface/axiom checks and finite runtime branch checks. No source edits were made.
