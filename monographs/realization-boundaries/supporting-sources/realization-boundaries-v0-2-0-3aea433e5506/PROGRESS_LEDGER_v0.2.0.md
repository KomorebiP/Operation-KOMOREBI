# Progress ledger v0.2.0

## Continuity

Input: `Komorebi_Realization_Boundaries.zip`.
Its SHA-256 is recorded in `verification/input_provenance.json`.
The input files are preserved unchanged under `inherited/`.
This package is a mathematical continuation, not a claim of external release certification.

## Completed in this continuation

| Item | Location | Evidence |
|---|---|---|
| Fixed ambient product and uniquely divisible quotient | Section 1 | Complete ordinary proof |
| Explicit dense subgroup and unique rational/torsion normal form | Section 2 | Complete ordinary proof |
| Finite cocycle group law | Section 3 | Ordinary proof and exact finite checks |
| Reducedness, residual finiteness, fixed torsion, nonsplitting | Section 4 | Complete ordinary proof |
| Integer-root criterion, explicit witness, and obstruction | Section 5 | Ordinary proof and exact finite checks |
| Identical full finite-quotient systems and profinite completion | Section 5 | Complete ordinary proof |
| Isomorphism exactly modulo finite selector changes | Section 6 | Ordinary proof and finite coordinate-transport checks |
| No embeddings or epimorphisms between distinct tail classes | Section 6 | Complete ordinary proof |
| Exact least presentation degree | Section 7 | Complete ordinary computability proof |
| No reconstruction from unmarked finite quotients | Section 8 | Complete ordinary proof |
| Countably infinite endomorphism-seed rank | Section 9 | Complete ordinary proof |
| Repeated diagonal escape within the same completion | Section 10 | Complete set-theoretic proof |
| Exact arithmetic implementation and reproducible report | src/ and verification/ | Fresh execution, PASS |
| Known antecedent for the inherited spectrum coding | Reference R1 | Primary source inspected, including page image |

## Critical distinctions retained

1. The common-completion construction is residually finite. It does not hide a nonzero element from every finite quotient, and it does not append a divisible direct summand.
2. All finite quotient objects and transition maps agree. Named points, source-element evaluations, and root-solvability predicates are additional information.
3. The unmarked isomorphism criterion is finite symmetric difference. Literal equality classifies the marked pairs (G_A,u_A).
4. Decoding from an arbitrary unmarked copy uses a nontorsion element and finite advice. A uniform decoder of the original literal A is neither asserted nor possible across finite alterations.
5. The degree claim is an X-computable-copy equivalence and least-degree assertion. No unproved identification with an exact-degree spectrum is used.
6. The diagonal selection of representatives is semantic and set-theoretic, not a proposed effective evaluation of every grammar description.
7. No term “non-Komorebi” is used without a declared realization contract.

## Verification performed

- Fresh Python run of the new exact checks: 114,738 assertions passed.
- Six negative controls reject: naive direct-product addition, false two-divisibility, omission of finite-change coordinate transport, omission of a torsion root correction, the wrong prime-power quotient order, and a zero root multiplier.
- Inherited exact checks replayed successfully. The original historical report is kept separate from the fresh replay.
- Source code hashes are in the current JSON report.
- Lean executable: not found. Lean compilation was not attempted and is not claimed.
- External referee review: not performed.
- Noncomputable-oracle execution: not attempted. Such cases are treated by proofs.

## Remaining obligations and restart point

The stated ordinary results have proofs in this package. The following are separate follow-on tasks, not premises silently assumed by those proofs.

1. Perform a focused novelty comparison with classical rank-one mixed abelian groups, extension classifications, and profinite genera. The broad topic is classical, and the original direct-sum computability example is already documented in R1.
2. Formalize the normal-form cocycle and integer-root theorem in Lean, then the common finite quotient system. This is the best first formalization block because Sections 3–5 isolate the algebraic core from computability.
3. Formalize the tail-divisibility invariant and the isomorphism/homomorphism theorems before attempting the computability formalization.
4. Connect the observation contract to the exact admissibility and completion interfaces of the existing Komorebi Space library. Do not claim that connection is already formally implemented.
5. Study restricted input classes or enriched observation systems that restore reconstruction. The present no-go theorem applies to the unmarked finite-quotient contract, not every observation language.

**Restart:** `FINITE_QUOTIENT_BLINDNESS.md`, Theorem 5.1, together with `DenseLiftGroup.root` in `src/dense_lift_groups.py`. The exact root construction supplies both the quotient calculation and the intrinsic divisibility invariant.
