# Paper X — Block 27

**Block 27 extends the actual Frobenius comparison to every finite normal number field over the rationals.** It proves restriction of prime ideals, inertia and residue actions, derives unramifiedness outside the discriminant, and proves independence from the absolute Frobenius choices. General prescribed-conjugacy prime coverage remains an explicit, unproved arithmetic obligation. The source ledger stays **17 checked / 3 partial**.

For a finite normal number field $L/\mathbb Q$, let $q_L:G_{\mathbb Q}\to\operatorname{Gal}(L/\mathbb Q)$ be actual restriction through a chosen embedding. A prime $Q$ of the algebraic integers in $\overline{\mathbb Q}$ contracts to an actual prime $P$ of $\mathcal O_L$. An absolute arithmetic Frobenius at $Q$ restricts to arithmetic Frobenius at $P$.

For $p$ outside the finite set of prime divisors of $\operatorname{disc}(L)$, actual finite inertia is trivial. For any two absolute Frobenius witnesses $u,v$ at $p$,

$$q_L(u)\sim q_L(v).$$

Every representation factoring through $L$ kills the relevant actual absolute inertia and gives the same trace on both witnesses. The chosen embedding and canonical subfield embedding produce conjugate restriction maps.

| New module | Result |
|---|---|
| `AbsoluteFrobeniusWitnesses` | Packages actual prime, decomposition membership and residue action; proves residue conjugation and comparison modulo inertia. |
| `NumberFieldPrimeRestriction` | Actual integral embedding, equivariance, contracted prime, maximality, lying-over and injective residue comparison. |
| `NumberFieldFrobeniusRestriction` | Restricts decomposition, inertia and arithmetic residue action; simultaneous absolute and finite Frobenius existence. |
| `UnramifiedFrobeniusUniqueness` | Actual inertia cardinality, ramification index, uniqueness and finite discriminant exclusions. |
| `FrobeniusChoiceIndependence` | Conjugacy modulo actual inertia and trace independence when inertia is killed. |
| `NumberFieldWitnessIndependence` | Derives inertia triviality and witness-independent traces outside the discriminant for factored representations. |
| `RestrictionEmbeddingConjugacy` | Fixed conjugacy between chosen and canonical restriction maps. |
| `GeneralArithmeticCoverage` | Exact conditional equivalence between arithmetic prime coverage and the separator's cofinite quotient coverage; independence from global witness choices. |

The new arithmetic interface uses the rational base. Source Claim 9.1 also permits general arithmetic bases F; those applications need the analogous prime and norm-power Frobenius attachment and coverage, or a proved transfer.

The new coverage interface requires: for every finite Galois subfield, every finite excluded prime set, and every finite automorphism, produce an unramified prime whose actual arithmetic Frobenius restriction is conjugate to that automorphism. This prime-existence assertion is not proved by the equivalence. Existence of a Frobenius element above each prime does not establish coverage of all conjugacy classes.

**Release verification passed.** All 178 production modules passed the clean build. The 2,064 named declarations passed the transitive axiom audit using only Classical.choice, Quot.sound and propext. The block adds 59 theorem/lemma declarations and 16 other named declarations; the cumulative theorem/lemma count is 1,455. All 12 positive controls passed, and 25 false claims plus the placeholder were rejected as intended. All 170 predecessor source and rebuilt proof-object hashes match Block 26. Fresh archive replay reproduced all 8 new proof objects and the retained Block 22 exact regression. Independent exact-source review of all new modules and manuscript review passed.

The bundle contains cumulative Lean sources and proof objects, raw audit evidence, compiler controls, amended LaTeX, the updated ledger, a source patch, and the complete Block 26 baseline. No PDF was typeset. See `FIVE_PARTIALS_STATUS.md`, `BLOCK27_SCOPE_RESOLUTION.md`, and `NEXT_TARGET.md`.
