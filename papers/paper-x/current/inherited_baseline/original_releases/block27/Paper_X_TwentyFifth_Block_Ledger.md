# Paper X — Twenty-fifth block ledger

**Source accounting: 17 checked / 3 partial.** No source claim is promoted in this block. The remaining partial claims are 9.1, 9.2 and 11.1. Claims 8.2 and 11.2 retain their checked conditional scopes and their unproved arithmetic application premises.

| Obligation advanced | Formal result | Scope |
|---|---|---|
| Character equality determines an irreducible member | `IrreducibleCharacterRigidity.equiv_iff_character_eq` | Actual finite-dimensional representations; characteristic zero; arbitrary monoid. |
| System nonisomorphism gives member nonisomorphism | `CompatibleSystemRigidity.nonisomorphic_members` | Shared common-field embeddings, trace compatibility and conjugacy density on good-place overlaps. |
| Common algebraic separation | `CompatibleSystemSeparation.finite_system_separator` | Cofinite quotient coverage; distinct samples; any fixed finite exclusion; all-embedding determinant transport. |
| Coverage after finite exclusion | `CyclotomicPrimeCoverage.exists_prime_with_automorphism` and `CyclotomicSystemSeparation.primeSample_cofiniteQuotientCoverage` | Actual rational primes for one fixed cyclotomic number field; Dirichlet supplies prime existence. |
| Arithmetic Frobenius attachment | `CyclotomicPrimeCoverage.primePowerAutomorphism_unramified_arithmeticFrobenius` | Actual stabilizer, ramification index one and $p$-power residue action. |
| Existence of witnessing prime ideals | `CyclotomicFrobeniusPrimes.exists_arithmetic_frobenius_prime` | Produces both the rational prime and a maximal ideal above it. |
| Restricted arithmetic separator | `CyclotomicSystemSeparation.finite_prime_system_separator_avoiding` | Actual finite cyclotomic Galois group; no supplied coverage or character-continuity premise. |
| Boundary of ordinary coverage | `FiniteAvoidanceBoundary.remaining_quotient_coverage_fails` | A surjective $C_2$ sample family loses coverage after deleting one natural-number index. |

The general arithmetic coverage leaf remains open in this development. The restricted cyclotomic proof does not establish coverage in every finite quotient of an absolute Galois group. Ordinary representation trace comparisons continue to require the corresponding good-place condition.

**Verification status: passed.** All 161 production modules passed the clean build. The 1,904 named declarations passed the transitive axiom audit using only Classical.choice, Quot.sound and propext. The block adds 48 theorem/lemma declarations and 12 other named declarations; the cumulative theorem/lemma count is 1,333. Nine positive controls passed, and 23 false claims plus the placeholder were rejected as intended. All 153 predecessor source and rebuilt proof-object hashes match Block 24. Fresh archive replay reproduced all eight new proof objects and the retained Block 22 exact regression. Independent review examined all eight final production sources and their actual mathematical dependencies. Separate reviews confirmed the arithmetic residue action, actual prime-ideal witnesses and manuscript scope.

Development failures are retained and summarized in `DEVELOPMENT_BLOCK25.md`. The source-scope decision is recorded in `CLAIM91_SCOPE_RESOLUTION.md`; the underlying independent planning review is `claim91_scope_review.md`.
