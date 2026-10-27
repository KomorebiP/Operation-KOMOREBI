# Independent Mathlib source review for Claim 9.1

Checked 2026-09-08 UTC. Reviewer: cyclotomic_sources, a bounded independent source pass under the Claim 9.1 proof audit. Scope: CyclotomicPrimeCoverage.lean, the subsequently frozen CyclotomicFrobeniusPrimes.lean endpoint covered in the addendum, and the pinned Mathlib statements and proof portions identified below. No source-author audit verdicts were read. No production source was changed. This pass did not rerun Lean, inspect compiled proof axioms, or recursively audit the entire Mathlib dependency graph; those are separate kernel/build checks.

## Result

The checked Mathlib contracts support the file's stated finite cyclotomic prime coverage, decomposition-group membership, p-power action on every integral residue class at every maximal prime P above p, and ramification index e(P/p)=1. No mathematical source-application defect was found in these arrows. The inputs allow n=1 and exclude n=0. The source result is a formal corollary of Dirichlet's theorem and the arithmetic of a fixed cyclotomic extension of Q. It does not establish general arithmetic Chebotarev for arbitrary number fields, nonabelian finite Galois groups, or arbitrary profinite arithmetic representations.

Source authentication is local revision/content authentication: every file in the hash table was checked byte-for-byte against its git HEAD blob. The worktree was clean. The configured remote is the official Mathlib repository, but an independent web fetch of the exact commit failed with DisabledError. Consequently this report does not claim external remote or signature authentication of the portable kit.

## Revision and metadata

- Local source root: /workspace/scratch/66a0b821dfa4/runtime_inputs/Komorebi_Portable_Lean_4.34.0-rc2/workspace/.lake/packages/mathlib
- Git HEAD: aeb72f1e9981b6d35b426b16dca7759be3e7ba06
- Git tree: 86d40f11a5373d9deb8558ac5a88907913068f2e
- Parent commit: 5fcc6656691ed31965746c369f41fa75e567ac9d
- Author and committer recorded in commit: mathlib-update-dependencies[bot], 2026-09-02 19:47:54 UTC.
- Commit subject: chore: update Mathlib dependencies 2026-09-02 (#43361).
- Configured origin: https://github.com/leanprover-community/mathlib4.git
- Lean toolchain file: leanprover/lean4:v4.34.0-rc2.
- Primary-source stable commit locator: https://github.com/leanprover-community/mathlib4/commit/aeb72f1e9981b6d35b426b16dca7759be3e7ba06
- Source files are Apache 2.0; individual authors appear in the hash table.
- Target under review: /root/.codex/tmp/paperx_block25/lean/PaperX/CyclotomicPrimeCoverage.lean
- Target SHA-256: 497cb15ebc4b9c48206bcf1782758ef3f66c0c46c30a2168d6c169a9dcab6273

The HEAD commit object contains no embedded signature field. A configured origin and matching git objects authenticate the local snapshot's consistency, not its independent upstream delivery chain. No current-source lookup was substituted for this pinned revision.

## Exact contracts and application

### 1. Dirichlet, conductor 1, and finite exclusions

Mathlib/NumberTheory/LSeries/PrimesInAP.lean, lines 423–446: namespace Nat has variables `{q : Nat} [NeZero q] {a : ZMod q}`. `Nat.infinite_setOfPred_prime_and_eq_mod` (line 429) proves infinitude of primes with `(p : ZMod q)=a` from `IsUnit a`. `Nat.forall_exists_prime_gt_and_eq_mod` (line 442) proves `exists p > B, p.Prime and (p : ZMod q)=a`, for every natural bound B. Its proof extracts an element above B from that infinite set; the preceding infinitude proof uses the proved nonsummability result, rather than an assumed prime coverage predicate.

Translation: q=n, a=the underlying ZMod element of the supplied unit u, B=max(user bound, forbidden.sup id). The class `[NeZero n]` supplies exactly the required nonzero modulus. There is no n>1, prime modulus, or nontrivial ZMod hypothesis. In particular n=1 is valid: ZMod 1 is the zero ring with its singleton unit group, so the asserted prime coverage becomes ordinary infinitude of primes. n=0 is intentionally outside the theorem.

In the target, lines 28–40, any member p of the finite forbidden set satisfies p<=forbidden.sup id, which contradicts the strict Dirichlet bound. The proof also retains the requested strict lower bound. It then recovers coprimality and unit equality using the next source contract. Lines 42–46 specialize B=0 to obtain surjectivity.

### 2. Unit residues are actual congruence classes

Mathlib/Data/ZMod/Basic.lean, lines 794–817: `ZMod.unitOfCoprime p hp` is a unit whose underlying ZMod value is literally the natural cast of p (`coe_unitOfCoprime`, line 798). `ZMod.isUnit_iff_coprime` (line 813) is `IsUnit (p : ZMod n) iff p.Coprime n`, without an extra n>1 restriction.

The target correctly transports the unit property through the equality returned by Dirichlet, then uses `Units.ext` to recover equality of units from equality of underlying residues. No assumed surjection occurs here.

### 3. The field automorphism and exponent convention

Mathlib/NumberTheory/NumberField/Cyclotomic/Galois.lean, lines 53–73, assumes n:Nat, `[NeZero n]`, K a field and number field, and `[IsCyclotomicExtension {n} Q K]`. `IsCyclotomicExtension.Rat.galEquivZMod` (line 60) is the actual multiplicative equivalence `Gal(K/Q) equiv* (ZMod n)^units`. It specializes `IsCyclotomicExtension.autEquivPow` using irreducibility of the nth cyclotomic polynomial over Q.

`galEquivZMod_apply_of_pow_eq` (line 63) asserts that for any x:K with x^n=1, sigma(x)=x^a, with a the natural value of the underlying unit residue. `galEquivZMod_smul_of_pow_eq` (line 70) proves the same action formula on the ring of integers; its proof compares the action after the injective inclusion into K.

The supporting `autEquivPow` is defined in Mathlib/NumberTheory/Cyclotomic/Gal.lean, lines 44 and 68–109. Its inverse constructs algebra automorphisms from power bases and equality of minimal polynomials. It is not merely a named function with an assumed inverse or assumed exponent property.

In target lines 51–70, sigma is the inverse image of the unit class of p. Therefore sigma sends every nth root of unity to its pth power. The reduction from the natural residue representative to the exponent p uses equality of exponents modulo n, which is valid because x^n=1. No inverse of p appears: this is the arithmetic Frobenius exponent convention. Target lines 74–87 transport Dirichlet residue coverage through this equivalence to cover every automorphism, with any finite exclusion and any strict bound.

### 4. Integral generation and extension to every residue class

Mathlib/NumberTheory/NumberField/Cyclotomic/Basic.lean, line 660 supplies `[NeZero n]`, and lines 766–799 contain `IsCyclotomicExtension.Rat.adjoin_singleton_eq_top` (line 770): for a primitive nth root zeta in a cyclotomic extension K/Q, the Z-subalgebra of the actual ring of integers generated by `hZeta.toInteger` is the whole ring. This is the integral generation theorem O_K=Z[zeta], not only generation of K as a Q-algebra. The proof uses induction by prime powers and coprime products; the prime-power case uses an integral power basis and the product case uses the integral-compositum result. The zero case is excluded by NeZero. The prime-power induction also accommodates n=1.

Mathlib/NumberTheory/NumberField/Basic.lean, lines 92–132, defines O_K as the integral closure of Z in K and gives the inherited automorphism action. Mathlib/Algebra/Algebra/Subalgebra/Lattice.lean, lines 876–883, proves `AlgHom.ext_of_adjoin_eq_top`: two R-algebra homomorphisms out of A are equal if they agree on a set whose R-adjoin is top.

The target's residue proof, lines 117–143, constructs the Z-algebra maps

- f: O_K -> O_K/P, x |-> reduction(sigma(x));
- g: O_K -> O_K/P, x |-> reduction(x)^p.

Both maps are actual ring/algebra maps. Since P is maximal, O_K/P is a nontrivial field. Lying-over yields the quotient algebra map Z/(p) -> O_K/P. `Int.ringChar_idealQuot` in Mathlib/RingTheory/Ideal/Int.lean (line 44) gives characteristic p to Z/(p), and `charP_of_injective_algebraMap` in Mathlib/Algebra/CharP/Algebra.lean (line 62) transfers it to O_K/P. The injectivity also follows directly from the quotient field algebra map; Mathlib/RingTheory/Ideal/Over.lean, lines 295–304, supplies the compatible quotient structure and its faithfulness under lying-over.

`frobenius` in Mathlib/Algebra/CharP/Lemmas.lean, lines 314–324, is the ring map x|->x^p under ExpChar; primality and CharP furnish the required instance here. Every ring map is a Z-algebra map, so the conversions to `toIntAlgHom` introduce no extra fixed-point assumption.

The target proves f(zeta)=g(zeta) using `galEquivZMod_smul_of_pow_eq` and the fact that the reduction of zeta still satisfies zeta^n=1. `pow_eq_pow_mod` in Mathlib/Algebra/Group/Basic.lean (line 169) proves x^p=x^(p mod n) whenever x^n=1. Integral generation then gives f=g on all O_K. Surjectivity of quotient reduction means the identity describes the action on every residue-field element. Only nth-root torsion, not primitivity after reduction, is required for this extension step.

### 5. Actual decomposition stabilizer at every P above p

Mathlib/NumberTheory/NumberField/Cyclotomic/Galois.lean, lines 109–151: for prime p, any maximal P of O_K lying over the ideal (p) of Z, and `p.Coprime n`, `galEquivZMod_stabilizer` (line 135) identifies the image of `MulAction.stabilizer Gal(K/Q) P` with the subgroup generated by the actual unit class of p.

The proof first maps a stabilizing field automorphism to its induced residue-field automorphism, uses the finite-field theorem that such automorphisms are powers of arithmetic Frobenius, and then compares subgroup cardinalities using e=1 and the multiplicative order of p mod n. The finite-field theorem is `FiniteField.exists_forall_apply_eq_pow`, Mathlib/FieldTheory/Finite/Extension.lean, lines 142–151; with k=Z/(p), its exponent base `Nat.card k` equals p by `Int.card_ideal_quot` (line 36 of Ideal/Int.lean). The cardinality identity is `Ideal.card_stabilizer_eq`, Mathlib/NumberTheory/RamificationInertia/Galois.lean, lines 328–335.

This stabilizer is the standard decomposition group: Mathlib/RingTheory/Ideal/Pointwise.lean, lines 39–69, defines the action on ideals by ideal map under the given ring action; Mathlib/GroupTheory/GroupAction/Defs.lean, lines 515–526, defines stabilizer membership as sigma(P)=P. Mathlib/RingTheory/Ideal/Over.lean, lines 340–356, provides the induced stabilizer action on the residue-field extension and identifies its kernel with inertia.

Target lines 106–113 correctly recover membership of sigma as the inverse image of the generator [p]. No particular P is selected or assumed to have a favorable splitting type: P is arbitrary with the stated maximality and lying-over hypotheses. The same sigma works at every such P because this is an abelian cyclotomic extension. Combined with the all-elements residue formula, it is precisely a lift of arithmetic Frobenius on the actual residue field.

### 6. Ramification index 1 and the word unramified

Mathlib/NumberTheory/NumberField/Cyclotomic/Ideal.lean, lines 47–48 and 284–328: `IsCyclotomicExtension.Rat.ramificationIdx_eq_of_not_dvd` (line 311) assumes p prime, K a number field, P prime and lying over (p), nonzero conductor m, and the cyclotomic hypothesis for m. From `not p divides m` it proves `Ideal.ramificationIdx P Z=1`. The target's maximality implies the required primality; its coprimality hypothesis implies nondivisibility by `Nat.Prime.coprime_iff_not_dvd`. Thus target lines 154–157 instantiate the source correctly with m=n, including n=1.

The source proof invokes Kummer–Dedekind with the integral generator's exponent equal to 1 and shows the relevant factor has multiplicity 1 because the reduced minimum polynomial is separable when p is coprime to m. The invoked multiplicity formula is `NumberField.Ideal.ramificationIdx_primesOverSpanEquivMonicFactorsMod_symm_apply'`, Mathlib/NumberTheory/NumberField/Ideal/KummerDedekind.lean, lines 257–264 (with its underlying proof at lines 239–255).

The exact exported target proposition is e=1, decomposition membership, and the universal residue equation. It does not export a separate `Algebra.IsUnramifiedAt` instance or an equality with a named Frobenius object. That is a formal-interface limitation, not a failure of the arithmetic claim in this number-field setting. Mathlib/RingTheory/RamificationInertia/Ramification.lean, lines 45–55, defines the current ramification index by local module length. Its `ramificationIdx_eq_one_iff` at lines 106–120 identifies e=1 with `Algebra.IsUnramifiedAt` when the algebra is integral, essentially of finite type, and the base residue field is perfect. Those hypotheses hold for O_K/Z at p: O_K is finite integral over Z and F_p is finite/perfect. Lines 144–169 also compare this definition with the ordinary Dedekind ideal-factorization ramification index.

The target does not separately choose a prime P, but its universal formulation is not arithmetically vacuous: integral lying-over supplies primes over (p), as formalized by `Ideal.nonempty_primesOver`, Mathlib/RingTheory/Ideal/GoingUp.lean, lines 334–338; such primes are maximal here. This source pass did not add an existential wrapper to the target.

## Scope and residual limitations

1. Verified mathematical application: for each fixed nonzero n and K/Q satisfying the stated cyclotomic hypotheses, every sigma in Gal(K/Q) occurs at arbitrarily large permitted rational primes; every maximal P above such a p has e=1, is stabilized by that same sigma, and has the p-power residue action. This is stronger than merely assigning a Frobenius-sounding name to a residue class.
2. The `primeSample_quotientCoverage` result in target lines 91–96 follows from surjectivity of this finite cyclotomic sample. This pass did not audit the imported project definition of QuotientCoverage; the parent audit handles that interface.
3. No assertion of density, effective prime bounds, general base number fields, nonabelian Chebotarev, or simultaneous compatibility over all conductors follows from the reviewed file alone. In particular, one cannot replace its fixed finite cyclotomic Galois group with an arbitrary profinite group and retain the same Dirichlet argument.
4. This report checks source statements, selected proofs, hypotheses, and the target's mathematical translations. It does not replace kernel checking of the exact compiled target or a complete audit of all imported theorem axioms. A direct scan of the five main cyclotomic/Dirichlet files found no `sorry`, `admit`, `axiom`, or `unsafe` token; this is only a local source scan, not an axiom-closure certificate.
5. The remote revision delivery chain remains independently unverified because the exact GitHub commit lookup was disabled. Local content hashes and git-tree equality are fully recorded below.

## SHA-256 source manifest

Every relative path below is under the pinned local source root. Every row was compared byte-for-byte with `git show HEAD:<path>`. Stable online locators are `https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/<relative path>#L<line>`; the cited line numbers above refer to those exact bytes.

| Relative source file | SHA-256 | File authors |
|---|---|---|
| `Mathlib/NumberTheory/LSeries/PrimesInAP.lean` | `a2491d48850056b27fe6ad31cf7b210a7f6455e8e0fa4fbb714671bbffb61ca4` | Michael Stoll |
| `Mathlib/NumberTheory/NumberField/Cyclotomic/Galois.lean` | `1681a3493873d5a04d9cc5c6254de0ee48403291ecf410d768b43c445ced4216` | Xavier Roblot |
| `Mathlib/NumberTheory/NumberField/Cyclotomic/Basic.lean` | `3e454ef15141368c7fabb3db375f371a010f721aa131e4c73b87ddd2f4ff876d` | Riccardo Brasca |
| `Mathlib/NumberTheory/NumberField/Cyclotomic/Ideal.lean` | `46ac69c6ea3635f12ff5b8fc8e1ff393e2b270cd0726acf8b02d53ff2ff568c6` | Xavier Roblot |
| `Mathlib/NumberTheory/Cyclotomic/Gal.lean` | `ab987d23de31f27b61903ba55111f98d52e202a2df40de1533f783f4b8037838` | Eric Rodriguez |
| `Mathlib/Data/ZMod/Basic.lean` | `fbe19ea6fc95105cf596e1ef3c730e32dffdf9f53b74a17eaab5c668e03d1b0f` | Chris Hughes |
| `Mathlib/Algebra/Algebra/Subalgebra/Lattice.lean` | `c8b4d7beab07c04ecd1c5cfca6e5b188db569cb5e35552fd3b35d11cea85b737` | Kenny Lau, Yury Kudryashov |
| `Mathlib/Algebra/Group/Basic.lean` | `4e164322527dc8133513618327feb10708238cd40848c273ca2d8317bda81e88` | Jeremy Avigad, Leonardo de Moura, Simon Hudon, Mario Carneiro |
| `Mathlib/Algebra/CharP/Algebra.lean` | `1c64cf153c3bdbc156dc687170ab5e226a838dc80486703140d3e868e41fe7f2` | Jon Eugster, Eric Wieser |
| `Mathlib/Algebra/CharP/Lemmas.lean` | `7aab29f90e99ded1f03a3edf9870d459cfa076fdd700def6a0b3831dda3f6b01` | Kenny Lau, Joey van Langen, Casper Putz |
| `Mathlib/RingTheory/Ideal/Int.lean` | `6a34f6d45487752d5e8ff75755eca667c0720c906b72916b8adbfaf5f5762e85` | Xavier Roblot |
| `Mathlib/RingTheory/Ideal/Over.lean` | `62c8e8522acccb33936868bdcb6ace99c2ead9ac729d5a14577a0178856f1bd9` | Anne Baanen, Yongle Hu |
| `Mathlib/RingTheory/Ideal/Pointwise.lean` | `a1ed8f3147ef0f3e56fa041e3496955b55eae99618356a1023b0c40b557cbb2c` | Eric Wieser |
| `Mathlib/GroupTheory/GroupAction/Defs.lean` | `cf70af56ad01e2be99c2c6335db1c5a062076ae2eaa3167b7eaefa8262b693e9` | Chris Hughes |
| `Mathlib/RingTheory/RamificationInertia/Ramification.lean` | `b64904cc5e0ab062c5c6e4b5b6abfefc35163969ff7dbb122cf9cd57978bd3f5` | Thomas Browning |
| `Mathlib/NumberTheory/NumberField/Basic.lean` | `4e9e600e2aeee2c69f498c2d5d8af2622b03d35a13e4f61dbb5730a88a7eb58b` | Ashvni Narayanan, Anne Baanen |
| `Mathlib/FieldTheory/Finite/Extension.lean` | `3c8e114073e50386ef314293184b7426f1fd2431c8b2369a0d9c5418fe764cf2` | Kenny Lau, Kevin Buzzard |
| `Mathlib/NumberTheory/NumberField/Ideal/KummerDedekind.lean` | `5680f7cbc524710aa72aae08e56bf0369925e6df2b8f36a718714ea642e37669` | Xavier Roblot |
| `Mathlib/NumberTheory/RamificationInertia/Galois.lean` | `8b982a93096532a4fb980947e5c803ead6ae78cadd4c9421aac359b37f00a499` | Yongle Hu, Jiedong Jiang |
| `Mathlib/RingTheory/Ideal/GoingUp.lean` | `6363ce60994dd160c97aa0919d401ab9e1ccac4711d7cb9c4036c84bf622e065` | Anne Baanen, Yongle Hu |

Checked-file revision history: PrimesInAP.lean last touched at 9b366004fb27a648b32abd1a2923cd94ec82077d (2026-08-14); Cyclotomic/Galois.lean at 7c72847433f7784f32989be58d4f040df96de34a (2026-08-31); Cyclotomic/Basic.lean at 1de9bcbfd003f6e92cf5d510f369d02b1bed9bcc (2026-08-13); Cyclotomic/Ideal.lean at d4519b399018129db0a28eda3488eddfed9f73c4 (2026-07-17). These are locally recorded commit facts.

## Addendum: frozen actual-prime endpoint

The audit parent expanded this bounded source pass to include the eighth production module after the initial review. Its raw source was independently read; no compiler or audit verdict from its author was used as evidence for the mathematical conclusions below.

- File: /root/.codex/tmp/paperx_block25/lean/PaperX/CyclotomicFrobeniusPrimes.lean
- Independently recomputed SHA-256: 315bdb71a834a6024fa47e7dc41ebb64954b0279d1df0fea451b662d7c8231fe.
- Relevant source: Mathlib/RingTheory/Ideal/GoingUp.lean at the same pinned Mathlib HEAD.
- Source SHA-256: 6363ce60994dd160c97aa0919d401ab9e1ccac4711d7cb9c4036c84bf622e065 (already included and HEAD-byte-verified in the manifest).
- Source metadata: Authors Anne Baanen and Yongle Hu; copyright 2020; Apache 2.0.
- Exact stable locator: https://github.com/leanprover-community/mathlib4/blob/aeb72f1e9981b6d35b426b16dca7759be3e7ba06/Mathlib/RingTheory/Ideal/GoingUp.lean#L348

`Ideal.exists_maximal_ideal_liesOver_of_isIntegral`, lines 348–353, has commutative rings R and S with an R-algebra structure on S, `[Algebra.IsIntegral R S]`, `[FaithfulSMul R S]`, and a maximal ideal P of R. It proves existence of a maximal ideal Q of S satisfying Q.LiesOver P. No Galois, finite-degree, noetherian, residue-characteristic, or conductor hypothesis is needed by this source theorem itself. Its proof uses the maximal lying-over result immediately above (lines 342–346) and discharges its kernel containment from injectivity of the algebra map. That result obtains a prime over P using integral lying-over and then upgrades it to maximality because its contraction is maximal.

For the target application, R=Z and S=O_K. Integrality is the `Algebra.IsIntegral Z (O_K)` instance in Mathlib/NumberTheory/NumberField/Basic.lean, lines 281–285, arising from the integral-closure definition. Faithfulness is the injectivity of the characteristic-zero integer embedding. The base ideal (p) is maximal by `Int.ideal_span_isMaximal_of_prime`, Mathlib/RingTheory/Ideal/Int.lean, lines 39–42; its hypothesis is exactly the target's `[Fact (Nat.Prime p)]`.

The new module's `exists_prime_above_with_frobenius`, lines 17–29, obtains Q, maximality, and lying-over from that theorem, registers those two proofs as local instances, and applies the already reviewed universal e=1/stabilizer/residue theorem at this Q. Thus it exports a concrete existential maximal-prime witness. `permitted_prime_has_frobenius_witness`, lines 34–42, extracts primality and coprimality from the permitted-prime subtype. Finally `exists_arithmetic_frobenius_prime`, lines 46–58, first selects a rational prime with the requested automorphism, finite exclusions, and strict lower bound, then selects its maximal prime witness and rewrites the automorphism equality into the stabilizer and residue conclusions.

Verdict on the expanded source application: valid. The arithmetic endpoint now explicitly provides both actual p and actual P; the initial observation that CyclotomicPrimeCoverage.lean alone lacked an existential P wrapper is resolved by this added module. The finite cyclotomic scope is unchanged. The statement still exports ramification index 1 and the defining arithmetic Frobenius properties rather than an `Algebra.IsUnramifiedAt` instance or a named Frobenius equality; the previously stated mathematical interpretation and source bridge apply. Compilation and axiom-closure checking remain outside this independent source pass.
