# Visual appendix source and claim map

The original manuscript and formal proof corpus are preserved. The appendix supplies worked examples and explanatory distinctions, not additions to the Lean theorem ledger. The original Feshbach wording must be read with its recorded invertibility amendment.

| Appendix page | Worked subject | Manuscript or supplement source |
|---:|---|---|
| V-1 | Three objects, three questions | Reading source: main text, Sections 1, 7, and 9; finite-completion supplement, pp. 5--6. |
| V-2 | The objects on the page | Main text: Definitions 1.1 and Sections 2--10; supplement, exact formal scope. |
| V-3 | One seed, eight addresses | Main text: Theorem 2.4 and Definition 1.1, pp. 4 and 6. |
| V-4 | Entanglement changes the local span | Main text: Theorem 2.1 and Corollary 2.3, p. 5. |
| V-5 | Why one seed is not always enough | Main text: Theorem 2.2, p. 5. |
| V-6 | Four phases resolve a cyclic shift | Main text: Theorem 3.1, p. 6. |
| V-7 | A coarse packet can still contain coherence | Main text: Theorem 3.2 and Numerical Certificate 3.3, p. 7. |
| V-8 | Track the Bell state through the circuit | Main text: Theorem 4.1 and Example 4.3, p. 8. |
| V-9 | Why path probabilities do not add | Main text: Theorems 4.1--4.2, p. 8. |
| V-10 | A symmetry reveals blocks, not approximations | Main text: Theorem 5.1 and the two-qubit example, pp. 8--10. |
| V-11 | Quantify the amplitude that escapes | Main text: Theorem 5.2, p. 9. |
| V-12 | A moving frame creates a connection term | Main text: Theorem 6.1, p. 11. |
| V-13 | Differentiate the subspace itself | Main text: Theorem 6.3, p. 12. |
| V-14 | A chart failure is not a singular fiber | Reading source: finite-completion supplement, pp. 2--4; main text, Classical Input 6.4. |
| V-15 | Curvature measures a local area response | Main text: Section 6.3, pp. 12--13; completion supplement, curvature theorem. |
| V-16 | Which coherence can a measurement see? | Main text: Theorem 7.1, p. 14. |
| V-17 | A channel acts on four matrix entries | Main text: Classical Input 7.2 and packet superoperators, p. 14. |
| V-18 | An ancilla tests more than positivity | Main text: Classical Input 7.2, the arbitrary-auxiliary-dimension clause, p. 14. |
| V-19 | Find the error without reading the logical state | Main text: Classical Input 8.1 and the bit-flip example, pp. 15--16. |
| V-20 | A harmless-looking syndrome can hide a logical error | Main text: Classical Input 8.1, pp. 15--16; normalized recovery supplements. |
| V-21 | Hidden states return as spectral dependence | Main text: Theorem 9.1, pp. 16--17; first-block amendments and v0.6.0 ledger. |
| V-22 | The smaller system remembers the discarded one | Main text: Section 9.2, pp. 17--18. |
| V-23 | Positive transfer is not a stochastic matrix | Main text: Theorem 10.1, p. 18. |
| V-24 | A dimension curve is a scale diagnostic | Main text: Section 11, pp. 21--22. |
| V-25 | Refine the grid while holding the mode fixed | Main text: Theorem 11.1, p. 21; nonzero-spacing clarification in the formal ledger. |
| V-26 | A zero compressed anomaly can be automatic | Main text: Section 12, p. 23; ConstraintAudit in the finite formal release. |
| V-27 | One complete calculation: opposite-site transfer | Main text: Sections 2--5 and 7, especially Theorems 3.1 and 4.1. |
| V-28 | What these pictures establish | Source release: v0.6.0 finite-completion supplement, pp. 5--7; original manuscript, Section 12. |

## Evidence classes

- Exact finite and symbolic identities: `visual_appendix/checks/verify_examples.py`. Its 180 checks include 171 positive assertions and nine rejected false controls.
- Drawings: `visual_appendix/source/generate_graphics.py` generates 26 TikZ plates. Coordinate sampling illustrates explicit formulas; the exact checks, not pixel positions, support the mathematical statements.
- Original numerical companion: its 22 tests and 19 figure pairs were replayed separately. These remain numerical/software observations.
- Saved Lean evidence: 19 registered finite items, 25 current modules, and 323 recorded theorem audits in `original_snapshot`. No Lean compilation was run for this editorial package.
- Continuum claims: all five original research targets remain outside the completed finite formal contract.

## Selection and provenance

The selected formal authority is v0.6.0. Its unchanged 25-page manuscript and seven-page final completion supplement are both included in the combined PDF. A 31-page v0.5.1 proofread sibling is retained separately as editorial reference, not substituted for the v0.6.0 formal ledger. The separately recovered original numerical package has the identical original manuscript PDF.
