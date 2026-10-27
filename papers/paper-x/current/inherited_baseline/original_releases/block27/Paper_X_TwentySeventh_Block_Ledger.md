# Paper X — Twenty-seventh block ledger

**Source accounting: 17 checked / 3 partial.** No source claim is promoted. Claims 9.1, 9.2 and 11.1 remain partial; 8.2 and 11.2 retain their checked conditional scopes.

| Obligation | Checked result | Scope |
|---|---|---|
| Actual prime restriction | `NumberFieldPrimeRestriction` | Every finite normal number field; literal contraction, maximality and residue injection. |
| Actual Frobenius restriction | `NumberFieldFrobeniusRestriction` | Same absolute prime and element give the contracted finite prime and p-power residue action. |
| Unramified finite Frobenius | `UnramifiedFrobeniusUniqueness` | Ramification index one or exclusion from the actual field discriminant; inertia and uniqueness derived. |
| Choice independence | `FrobeniusChoiceIndependence` | Absolute witnesses conjugate modulo actual inertia; traces agree when that inertia is killed. |
| Finite-field application | `NumberFieldWitnessIndependence` | Outside the discriminant, restriction kills actual inertia and gives a unique conjugacy class. |
| Embedding comparison | `RestrictionEmbeddingConjugacy` | Fixed conjugacy relates chosen and canonical restriction to a normal subfield. |
| Arithmetic coverage interface | `GeneralArithmeticCoverage` | Equivalence with cofinite quotient coverage, assuming the actual prime-existence statement. |

The arithmetic convention is p-th powering on residues. Trace independence from Frobenius witness choices does not require a supplied finite-dimensionality hypothesis because Mathlib defines trace in general; finite-dimensional separator applications retain their existing hypotheses. All actual witness and discriminant data use the same number field and rational prime.

**Release verification passed.** All 178 production modules passed the clean build. The 2,064 named declarations passed the transitive axiom audit using only Classical.choice, Quot.sound and propext. The block adds 59 theorem/lemma declarations and 16 other named declarations; the cumulative theorem/lemma count is 1,455. All 12 positive controls passed, and 25 false claims plus the placeholder were rejected as intended. All 170 predecessor source and rebuilt proof-object hashes match Block 26. Fresh archive replay reproduced all 8 new proof objects and the retained Block 22 exact regression. Independent exact-source review of all new modules and manuscript review passed.

The exact remaining rational-base arithmetic coverage obligation is `GeneralArithmeticCoverage.ExistentialArithmeticCoverage`. It has not been proved. General-base instances of source Claim 9.1 additionally need actual-prime/norm-power Frobenius attachment and coverage over F, or a proved transfer from the rational-base result. The original Claim 9.1 is not weakened by adding that condition to its statement.
