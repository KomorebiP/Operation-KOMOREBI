# Independent exact-source proof audit: Claim 9.1, Block 25

**Normalized source claim.** For a finite family of pairwise nonisomorphic strictly compatible systems with absolutely irreducible members and common algebraic unramified traces in a number field E, choose exactly as many distinct permitted arithmetic places as there are systems so that the square matrix of common traces has nonzero determinant. Every coefficient embedding preserves that determinant. Identification with ordinary member traces is restricted to the selected places good for that member.

**Primary verdict: incomplete, with the smallest missing implication.** The new sources prove the system-to-member reflection and the general separator conditional on cofinite quotient coverage. They also prove an unconditional arithmetic coverage theorem and separator for representations of one fixed finite cyclotomic Galois group over Q. This is a real arithmetic restricted case, including actual prime ideals and arithmetic Frobenius residue action. It does not prove the full general-arithmetic source Claim 9.1. The missing implication is cofinite conjugacy coverage by actual permitted Frobenius samples in the relevant general absolute Galois group, including the finite exclusions needed for coefficient-place overlaps.

No defect was found in the eight final production sources under their actual hypotheses. This is an independent raw-source review, not an adoption of a ledger verdict. The reviewer read the frozen Block 24 Section 8 definitions and Claim 9.1 first, reconstructed the six initial proof modules, then reviewed the seventh and eighth at their announced frozen hashes. The older scope review and target contract were consulted only after that reconstruction. No production source was edited.

## Authoritative source and claim card

The authoritative statement is `source/Projector_Resolved_Seed_Calculus_X_Block24_Amended.tex`, SHA256 `fef55b77f3cb7b3b1c100226cec741b4bf82484ccdf2a3b15c7a4d09bedfa014`: Section 8, “Common arithmetic spine,” lines 760–806; Section 9, “Finite Frobenius separation,” theorem and proof, lines 1053–1083. Its following formalization paragraph is commentary on verification status, not an extra theorem hypothesis.

Section 8 specifies common characteristic polynomials at almost all places, coefficient-independent weight and determinant data, and prescribed ramified local labels. These labels do not define representation isomorphism. `ConditionalArithmeticSpine.Spine` makes the good-place cofiniteness and supplied label relations explicit; it does not assert that optional labels or records classify representations.

The relevant system equivalence is precisely

    MemberwiseEquiv rho i j := forall l, Nonempty ((rho l i).Equiv (rho l j)).

Each equivalence is an equivariant linear isomorphism over K(l), between W(l,i) and W(l,j). Different coefficient indices may have different fields and different vector spaces. No equivalence is asserted between vector spaces over different coefficient fields, no common basis is chosen, and no comparison of integral lattices or label records is substituted. A fixed embedding E → K(l), shared by all constituents at that coefficient index, is essential to reflecting equality of algebraic traces.

The source's absolute irreducibility implies the ordinary irreducibility used in the new proofs. The new characteristic-zero algebraic theorem in fact applies to arbitrary monoids; finiteness of the monoid and algebraic closedness of the coefficient field are unnecessary. The topological transfer uses groups and continuous actual characters into Hausdorff fields. General separation additionally uses a compact totally disconnected topological group and a topological-ring coefficient field. A selected coefficient index l₀ is an explicit argument, so nonemptiness of the coefficient-index type is never silently inferred.

The family index I is finite in the separator. Its cardinality may be zero. W(l,i) can vary with both indices; irreducibility rules out the zero vector space for an inhabited family. The good-place predicate may vary with l. Using one common predicate for the finite family I is legitimate after intersecting the finitely many constituent good sets. An intersection over all coefficient indices is neither assumed nor used.

## Dependency reconstruction

1. `IrreducibleCharacterRigidity.character_eq_of_equiv` uses the actual representation character and Mathlib's equivariant-isomorphism invariance of trace. Its converse reduces two possibly different representation spaces to a Bool-indexed family. A reverse isomorphism is inverted in the off-diagonal case. Existing arbitrary-monoid character independence makes equality of the two characters impossible unless the representations are equivalent.
2. Character equality on samples extends to their conjugacy saturation by actual character conjugacy invariance, then to the whole group by continuity and the Hausdorff equalizer theorem.
3. `CofiniteQuotientCoverage s` quantifies over **every** finite subset of sample indices and **every** open normal subgroup/coset. Its cofinite-domain lemma converts the finite complement to a finset, and its overlap lemma deletes the union of the two exceptional sets and any additional finite exclusions. Coverage-to-density is the frozen `ProfiniteSeparation` theorem.
4. An equivalence at l₀ gives equality of embedded algebraic traces on good(l₀). Injectivity of the shared embedding reflects equality in E. On good(l₀) ∩ good(l), compatibility maps it into equality of target traces. Dense conjugacy saturation and irreducible character rigidity give equivalence at l. This proves `MemberwiseEquiv`, and hence pairwise nonisomorphism at every chosen coefficient member.
5. The existing independence theorem produces independent selected-member characters. Cofinite coverage supplies the permitted sampling domain after arbitrary finite deletion. `TraceRecovery.common_trace_separator` selects an injective I-indexed family of samples and reflects nonzero determinant into E. `determinant_transport` preserves it under every coefficient embedding. Matrix rows are places and columns are constituent systems.
6. For n ≠ 0 and an actual cyclotomic number field L/Q of conductor n, Mathlib's proved Dirichlet theorem supplies primes in any unit residue class modulo n above any bound. A bound above the maximum of a finite forbidden set enforces avoidance. The actual cyclotomic Galois equivalence turns these primes into a surjective family of automorphisms, and the same bound argument proves coverage after every finite deletion of the permitted-prime index set.
7. The prime-power automorphism acts by x ↦ x^p on n-th roots of unity. The decomposition-group theorem places it in the actual prime-ideal stabilizer. The integral generation identity O_L = Z[ζ], together with characteristic-p Frobenius, extends the residue identity to every integral element. The explicit ramification-index result is e(P/p)=1 for p coprime to n. Thus the convention is arithmetic Frobenius, not its inverse.
8. `CyclotomicFrobeniusPrimes` applies integral maximal lying-over to obtain an actual maximal P above (p). Combining it with Dirichlet and the preceding residue theorem gives, for every σ in Gal(L/Q), every finite forbidden set, and every bound B, a permitted prime p>B and an actual P with e=1, sample(p)=σ, stabilizer membership, and the p-power residue action.
9. `CyclotomicSystemSeparation` uses the existing discrete Krull topology of this finite number-field Galois group. Character continuity is therefore automatic. The general conditional separator becomes an arithmetic-prime separator for that fixed group, and a finset preimage converts exclusions of permitted-prime indices into exclusions of underlying natural primes.

The PaperX import closure contains 19 predecessor modules. Every source in that closure is hash-pinned in the manifest. The raw predecessor definition sources actually examined are separately identified there. External-source authentication is local pinned-revision and git-blob consistency; an independent upstream fetch was unavailable. The main arithmetic source checks and exact Mathlib hypotheses are recorded in `checks/claim91_audit/MathlibSourceReview.md`.

## Obligation matrix

| Obligation | Result | Exact scope/evidence |
|---|---|---|
| Genuine character and representation-equivalence definitions | Passed | Mathlib trace of the action; actual equivariant linear equivalence |
| Different representation spaces and dimensions | Passed | Dependent W(l,i), two-space Bool construction, actual monoid-algebra module independence |
| Shared coefficient embedding and equality reflection | Passed | One `emb l` for all i; injectivity used before transfer |
| Equivalence reflected from any chosen member | Passed | `memberwiseEquiv_iff_member`, with explicit overlap density |
| Good-place overlap for different coefficient primes | Passed | Pairwise overlap, finite complements; no global all-prime ordinary-trace domain |
| Finite exclusion from initial coverage alone | Failed as a proposed generic implication | Actual C2 boundary example; this false implication is not used |
| Cofinite coverage implies all required overlap density | Passed | Finite-union argument followed by frozen profinite-density theorem |
| Exactly r distinct samples and nonsingular common matrix | Passed under stated coverage | General separator, injective sample function and determinant descent |
| All-embedding determinant versus ordinary trace comparison | Passed | Determinant for all l; equality of entries only when good(l,v) holds |
| Dirichlet supplies actual primes outside arbitrary finite sets | Passed | Exact pinned Mathlib theorem, not an assumed coverage predicate |
| Actual cyclotomic Galois automorphism, decomposition action, and residue convention | Passed | Field automorphism, actual maximal ideals, p-power residue action on every integral x |
| Existence of an actual prime ideal above each permitted p | Passed | New maximal lying-over endpoint; not only a conditional forall-P assertion |
| Unramifiedness | Passed in the precise number-field form | Explicit ramification index e(P/p)=1 at p coprime to n; residue fields are finite/perfect |
| Conductor n=1 and empty family | Passed | No n>1 assumption; audit edge applications compile |
| General absolute-Galois arithmetic coverage | Not addressed by the cyclotomic theorem | Finite fixed Gal(L/Q) is not the full absolute Galois group |
| Full strictly compatible system/label classification, carrier construction, or local attachment | Out of scope | No such construction follows from trace rigidity alone |
| Effective selected-prime norm bound | Not addressed | B is an arbitrary lower bound; the separator is existential |

## Decisive boundaries

The finite-avoidance obstruction is an actual infinite index family in the actual discrete group C2: s(0) is its nonidentity element and s(n+1)=1. The original family is surjective and covers every open normal quotient. Deleting {0} leaves only the identity, so even conjugacy saturation is not dense. The actual distinct sign and trivial unit-valued characters agree on every remaining sample. The audit also compiled the consequence that this family is not `CofiniteQuotientCoverage`. This guards precisely the overlap-density premise; it is not a counterexample to the arithmetic source claim.

For cyclotomic coverage, an arbitrary natural conductor n is universally quantified subject to n≠0, but the acting group remains the one **finite** Gal(L/Q) attached to that conductor. Quantifying over all conductors does not cover arbitrary finite Galois quotients, nonabelian quotients, other base number fields, or the full absolute Galois group. No passage to that larger class is present. Nor do the files construct a strictly compatible system: the compatible family of irreducible representations and common traces are given inputs.

The ordinary trace restriction is maintained even after obtaining a common invertible E-matrix. A selected p can fail a later coefficient member's good predicate. The mapped algebraic matrix remains invertible there, but no ordinary unramified trace identity is asserted at that excluded place.

## Independent compilation and axiom evidence

The reviewer created a fresh isolated PaperX cache at `/root/.codex/tmp/paperx_block25_independent_claim91`. Initially it contained **only the 153 frozen Block 24 predecessor oleans**. Each predecessor source hash and olean hash matched the frozen Block 24 verification record; each olean also matched the compact archive bytes. The verification record itself matched the archive. The archive SHA256 is `8bff25880aa4bc30d85a8674a33e99c11dde98e60053e19135515d4eabf68ad5`.

The runtime is pinned Lean 4.34.0-rc2, commit `6a10ac8c22beadecabdbb0919c2b50214762f91d`; Lean executable SHA256 `e8baaa71855a616dc351028f3ad2200051b0671f423a1696a100e809302d5550`; shared library SHA256 `cddf08bd2b9239f8ce2e2aba8630c47e37b6b341b47705d9d0ba910ad6db13b5`; Mathlib revision `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`. The production Block 25 build directory was excluded from LEAN_PATH. Exact environment and all commands are saved under `checks/claim91_audit`.

All eight final source modules compiled independently with `-DwarningAsError=true`, in the order recorded by `run_isolated.py`. The final `AllNewAxioms.lean` requests `#print axioms` for **all 60 explicitly named new declarations: 48 theorems and 12 definitions/abbreviations**. The final audit permits only `Classical.choice`, `Quot.sound`, and `propext`; it rejects any additional axiom. No sorry/admit, new axiom, native_decide, or unsafe declaration occurs in the new production sources.

The edge applications check finite-avoidance failure, n=1 with several excluded primes, the exponent-two arithmetic action for conductor five, arbitrary finite prime exclusions and lower bounds in the conductor-four field, and the empty-family/empty-sample determinant. One initial edge fixture failed because its cyclotomic instance was introduced after it was needed in the theorem statement; its exact failing source, output, and result are retained as `EdgeApplications_Failure1.*`. Moving that instance before the statement repaired the audit fixture; no production change was required. The first declaration scanner omitted a one-line simp theorem through an over-greedy attribute pattern; the incomplete 59-declaration input/output is retained as `*_IncompleteScanner.*`. The corrected scan includes `sample_succ` and all 60 names and was rerun. These are audit-harness corrections, not suppressed production failures.

Replay commands, from the project root, with a fresh isolated work path:

    python checks/claim91_audit/run_isolated.py --work /root/.codex/tmp/paperx_block25_claim91_replay --init IrreducibleCharacterRigidity CofiniteConjugacyCoverage CompatibleSystemRigidity CompatibleSystemSeparation FiniteAvoidanceBoundary CyclotomicPrimeCoverage CyclotomicSystemSeparation CyclotomicFrobeniusPrimes --axioms --edge

The script intentionally refuses to overwrite already-built new proof objects or reuse an existing initial work directory. Predecessor proof bodies were not all recompiled in this pass: this is an independent new-source replay against the authenticated 153-object predecessor baseline and pinned Mathlib kit. The axiom check follows the imported theorem dependencies.

## Strongest safe statement and remaining work

The safe release statement is: “The nonisomorphic-system-to-member bridge and finite common-algebraic separation are Lean-checked under cofinite arithmetic coverage; cofinite coverage and actual arithmetic Frobenius prime witnesses are proved for each fixed finite cyclotomic Galois extension of Q, yielding a genuine restricted arithmetic separator.”

Full Claim 9.1 remains partial. Completing it requires construction and cofinite quotient coverage of the intended general arithmetic Frobenius samples, with the permitted-place convention and common ambient absolute Galois group explicit. The finite cyclotomic theorem does not supply that missing implication. Claims 9.2 or 11.1 are not promoted by this audit.

`CLAIM91_PROOF_AUDIT_SOURCES.json` pins all eight final production sources, the full internal source closure, reviewed predecessor definitions, exact raw source TeX, scope materials consulted, local external-source review, compiler/axiom/edge evidence, the baseline archive, and this report as the final evidence entry. It does not pin mutable Block 25 provenance, README, or amended manuscript, and does not include its own hash.
