# Block 32 development failures and repairs

The authoritative result is the final frozen-input plan, not these development attempts.
All 934 inherited theorem statements and their containing mathematical modules remain
unchanged. The root only imports the five new modules through PresentationExamples.

1. The first finite-presentation proof drafts failed on cast normalization, a guessed
   library lemma name, and eliminating an existential proposition directly into
   data. The final proof establishes Nonempty and uses explicit classical choice.
   This is a noncomputable mathematical presentation, not an executable Smith solver.

2. A prototype natural-representative generator-expansion lemma lacked a positive-
   base hypothesis. That unrestricted version is not valid at base zero, where
   ZMod(0)=Z and a natural representative cannot encode arbitrary negative elements.
   The final statement explicitly requires p>0. The intended prime-base theorem
   and every inherited statement are unchanged. Precision r=0 remains covered at
   prime base and correctly has no nontrivial factor.

3. Torsion-cardinality, cyclic-column and concrete permutation proofs needed explicit
   dependent-type and bundled-homomorphism normalization. In particular, simplifying
   a presentation's carrier and its algebraic instances simultaneously caused type
   mismatches in the same-signature/different-matrix witness. Pointwise equivalence
   identities resolve it without weakening the witness. Representative failed drafts
   and the full development compiler logs are retained.

4. During self-review the Python reference's iterate dimension check was found to
   check only after zip truncation, which could silently accept an extra coordinate.
   It now validates the input length before reduction. The audit rejects an extra
   coordinate in each of 168 generic executions. This was a development code defect,
   not a released theorem or a formal Python-to-Lean refinement result.

5. The first matrix-choice negative control failed for missing Decidable inference
   rather than the intended contradiction. It was not counted as a passing negative
   control. Explicitly normalizing the coefficient type to ZMod5 exposes 1=0. The
   final five negative controls all fail for their required contradiction or sorry
   diagnostic, while the positive arithmetic control succeeds.

The final 18-phase plan completed successfully with unchanged execution-input hashes.
No failed development build, incomplete log, or opaque reduction error is included
among the successful final results. The exact integer audit and source/axiom audit
both passed. All counts are in RESULTS.json and per-command receipts.
