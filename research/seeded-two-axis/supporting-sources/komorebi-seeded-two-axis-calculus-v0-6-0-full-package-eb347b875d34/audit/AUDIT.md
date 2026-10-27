# v0.6.0 audit and continuation

## Scope and verdict

The complete v0.5.0 LaTeX source was read and checked for local mathematical consistency, hypothesis sufficiency, type/variance issues, and manuscript structure. This was a self-review in the authoring session, not an independent referee report or a Lean check.

Verdict on the previous package: **correct only after stated restrictions and corrections**. Existing results were not all rejected. The stable path-relative filtration and thick quotient construction survive. The general ordered-filtration-independence ambition is refuted. The quotient alone does not imply constructor descent or noncollapse.

## Main proof/correction records

1. **Resolution metric.** The old separation depth could use an empty set and lacked a common state set. The corrected result assumes nested equivalence relations on one set and a universal zeroth level. Without separation the result is an ultrapseudometric.
2. **Refinements.** One fine isomorphism class does not mean a contractible framed lift groupoid. The corrected text records the chosen identification and automorphisms when needed. Branching information excludes log(0).
3. **Termination.** The normal-form statement requires a rule for every well-typed inversion. Principal-path termination does not prove termination of recursive residual branches.
4. **Split shift.** For the split projection A = B plus E -> B, cofiber is E[1]. The source-side remainder is Delta[-1], not Delta. The new finite expansion proof avoids the unsupported recursive branch argument.
5. **Path independence.** In Perf(k), 0 -> k -> k plus k^2 and 0 -> k^2 -> k plus k^2 have identical comparison maps and totals but different filtered middle stages. The manuscript additionally realizes this inside the stated exact two-axis grammar. Coherence alone cannot identify these ordered filtrations.
6. **Replacement.** A finite-height semantic diamond argument fixes the comparison map up to homotopy. Pure exchange histories form the ideal lattice of a finite event poset. A supplied coherent semantic functor on that lattice gives the complete residual-history diagram. This preserves the meaningful order dependence.
7. **Quotient invariance.** In the C^3 example the ordinary thick kernel is C x C x 0. U sends a killable second-coordinate object to a persistent third-coordinate object. Thus U does not descend. The least invariant thick kernel contains all three coordinates, and its quotient is zero.
8. **Directed repair.** With W = P after U = Q after T and UX = 0, one has Q(TX) = P(UX) = 0. Thus directed common postcomposition gives invariance in addition to the already proved thick closure.
9. **Orbit test.** Pointwise cofiber of a natural transformation between exact functors is exact. Its kernel, and the kernel after exact quotient, is thick. Vanishing on all operation-orbit generators therefore extends to their thick zoo. The orbit may be infinite.
10. **Stable envelope.** Ordinary and infinity-categorical regimes are now separated. The source universal property is an equivalence of functor infinity-categories. This supports extension of noninvertible exchange morphisms and supplied coherence; the mapping-space adjunction alone would not justify that step.
11. **Descent.** Effective descent includes morphisms, all overlap degrees, and an equivalence of descent categories. Obstruction transport must reflect zero as well as preserve it to infer an iff. The functor on obstruction quotients is barred to keep its domain correct. No arithmetic realization is supplied by these abstract facts.
12. **Set-level examples.** A commuting polynomial congruence square is not silently called a stable cofiber calculation. The torsor repair relation is not identified with the exact-constructor monoid.
13. **Foundations and derived quantities.** A one-object resolution base presents any category, so bare two-axis existence has no new foundational strength. Zoo growth depends on generators. Search displays do not prove existence of a minimizer or decidability.

## Dependency check

- Saunier and Winges, *On exact categories and their stable envelopes*, arXiv:2502.03408v2 (28 November 2025). Definition 3.1 and its following functor-category universal property. The source explicitly uses infinity-categories. Checked for free stable envelope and the enriched extension of exchange morphisms.
- Drew, *Verdier quotients of stable quasi-categories are localizations*, arXiv:1511.08287v1 (26 November 2015), Definition 1.1 and Theorem 1.3. Checked for stable localization by cofiber conditions.
- Stacks Project, Section 13.6, Tag 05RA, especially Lemmas 13.6.2, 13.6.8, 13.6.9. Checked for thick kernels and the exact quotient universal property in homotopy categories.
- Stacks Project, Section 13.3, Tag 05QK. Octahedral axiom. This alone gives triangulated existence, not functorial canonical cofibers.
- Stacks Project, Section 21.4, Tag 03AG. Classical torsor/global-section interpretation.
- Fairbanks–Shulman is retained as background. Its HTML retrieval was unavailable in this session, and no exact numbered theorem from it is used to discharge a proof. The manuscript's strict free syntax result has a direct terms-and-relations proof.

This is an exact-dependency check, not a comprehensive novelty search. No global novelty assertion is made.

## Executed checks

`python checks/check_models.py --max-length 10` (the default bound was used in the actual run) passed. See results.json for the exact scope, software version, script hash and runtime. This is finite exact regression evidence, separate from the universal proofs.

`latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=build Komorebi_Seeded_Two_Axis_Calculus_v0.6.0.tex` succeeded with 45 pages. The final TeX log has no warnings, overfull/underfull boxes, undefined references, or undefined citations. Source-label checks found no duplicate labels or unresolved references.

All pages were rendered and visually scanned using contact sheets. Pages affected by final edits were re-rendered and rechecked. Automated text-bound checks found no text outside the generous safety margins. These are layout checks, not mathematical certification.

## Execution failures and resolutions

- An initial editing script contained a stray malformed Python expression. It failed at parsing and produced no revised manuscript. The line was removed.
- The next run hit its protective exact-match assertion because Python adjacent string literals had swallowed LaTeX's closing quote marks in a replacement key. The replacement strings were changed to safely quoted strings. The guard then passed and all edits were applied.
- No mathematical conclusion was inferred from those failed editing runs. The final LaTeX build succeeded.
- The proposed general ordered-filtration-independence claim failed mathematically for the explicit counterexample above. It was replaced rather than hidden or silently retained.
- Constructor descent and noncollapse failed in the explicit C^3 model. The invariant quotient and its possible collapse are now part of the theorem statement.

## Remaining obligations

The actual coherent semantic diagram must be constructed for any richer domain. The invariant quotient can be zero. The operation orbit need not be finite. Arithmetic globalization and unrestricted reciprocity are not established. No Lean compiler was run for this release.
