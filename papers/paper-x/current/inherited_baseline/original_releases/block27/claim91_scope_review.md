# Independent source audit: Claim 9.1 after Block 24

**Normalized claim.** A finite family of pairwise nonisomorphic strictly compatible systems, with absolutely irreducible members and common algebraic unramified traces in a number field E, admits exactly r distinct permitted places whose r by r trace matrix has nonzero determinant in E. The matrix stays invertible under every coefficient-field embedding. Identification of its entries with ordinary representation traces is asserted only at places permitted for that coefficient prime.

**Primary verdict: incomplete, with the smallest missing implication.** The algebraic separation and scalar descent are already present. The system-to-member implication can be proved from common traces, irreducibility, and conjugacy-saturated density on the appropriate overlap of permitted places. That implication is absent from the inspected production files. Actual arithmetic Frobenius coverage, including persistence after the finite exclusions used by those overlaps, remains an unproved formal leaf. Supplying coverage as a new hypothesis gives a valid restricted theorem but does not complete the arithmetic source claim.

This is a read-only independent source audit dated 2026-09-08. The authoritative raw statement and Section 8 definitions were read before status material. No Lean compilation, computation, production edit, or manuscript edit was performed. The examples below are exact elementary arguments, not claimed compiler results.

## Exact source and claim card

Base directory: `/root/.codex/tmp/paperx_block24`.

Manuscript: `source/Projector_Resolved_Seed_Calculus_X_Block24_Amended.tex`, SHA256 `fef55b77f3cb7b3b1c100226cec741b4bf82484ccdf2a3b15c7a4d09bedfa014`.

Authoritative locators:

- Section 8, “Prime-independent system seeds,” especially “Common arithmetic spine,” lines 760–806.
- Section 9, “Finite Frobenius separation,” theorem and proof, lines 1053–1083.
- The subsequent formalization-boundary paragraph, lines 1085–1100, was consulted after the raw statement.
- Section 1 fixes a complete DVR, its fraction field, and the Galois deformation example G_{F,S}. Characteristic zero is explicitly required for characteristic-zero conclusions. Claim 9.1 itself does not restate a formal type of strictly compatible systems or system isomorphism.

The claim quantifies over r systems, one common number field E, and ordinary members W_{i,lambda} over the corresponding characteristic-zero coefficient fields. Each member is absolutely irreducible, hence nonzero and irreducible. Dimensions may vary with i. The finite family need not have a common matrix dimension. There is no finite-group hypothesis, no effective norm bound on the selected places, and no assertion that all selected places are permitted at all coefficient primes simultaneously.

A formal system-isomorphism convention is not defined in the manuscript. The standard representation-family interpretation needed here is

    SystemIso(i,j) := forall lambda, Nonempty (W_{i,lambda}.Equiv W_{j,lambda}).

This compares members over the same field K_lambda. It is not equality of chosen matrix bases, integral lattices, packet labels, record fields, or characteristic-polynomial records. If different coefficient fields are used for the two systems, a common comparison field and scalar-extension convention must first be fixed. The source's common E and fixed coefficient-field embeddings provide the natural uniform setting.

## Exact missing system-to-member contract

Fix a coefficient prime lambda0. For a pair of systems i,j, suppose:

1. E is a characteristic-zero field and sigma_lambda : E -> K_lambda is one fixed field embedding for each lambda, shared by both systems.
2. W_{i,lambda} and W_{j,lambda} are finite-dimensional irreducible continuous representations of one common topological group G over a Hausdorff topological coefficient field K_lambda. It suffices to assume their actual characters are continuous.
3. There are common E-valued functions t_i,t_j on a place set V and permitted-place predicates good_{i,lambda}, good_{j,lambda}. At a permitted place the embedded common value equals the ordinary representation trace at the chosen Frobenius lift.
4. For each target lambda, the conjugacy saturation of the sample set on

       U = good_{i,lambda0} intersect good_{j,lambda0}
           intersect good_{i,lambda} intersect good_{j,lambda}

   is dense in G. When the same good predicate serves all systems, the redundant intersections disappear.

Then

    Nonempty (W_{i,lambda0}.Equiv W_{j,lambda0})
      -> forall lambda, Nonempty (W_{i,lambda}.Equiv W_{j,lambda}).

The converse follows immediately by evaluating a family of isomorphisms at lambda0. Thus a componentwise system isomorphism is reflected by any selected member. Pairwise nonisomorphic systems consequently give pairwise nonisomorphic members at lambda0.

The source's absolute irreducibility is stronger than the irreducibility actually needed for this bridge in characteristic zero. No additional absolute-irreducibility theorem, cross-coefficient linear equivalence, or equality of Hodge–Tate labels is needed to establish this representation-family implication.

## Dependency graph and proof outline

1. An isomorphism at lambda0 implies equality of the two actual characters there (`Representation.char_iso`).
2. On the overlap U, compatibility and injectivity of sigma_lambda0 give equality t_i(v)=t_j(v) in E.
3. Mapping that equality under sigma_lambda gives equality of the two target characters at every sample from U.
4. Characters are conjugacy invariant (`Representation.char_conj`), so they agree on the conjugacy saturation of U.
5. Density and continuity into a Hausdorff field imply equality of the full target characters.
6. If the two irreducible target representations were nonisomorphic, `GeneralCharacters.independent_irreducible_characters`, applied to a two-element family, would make their characters linearly independent. Equality contradicts that independence. Therefore an actual representation equivalence exists.
7. With pairwise nonisomorphism now established at lambda0, the existing irreducible character-independence theorem gives r independent character functions there.
8. Arithmetic density of the selected permitted Frobenius samples preserves independence after restriction; `FiniteSeparation.exists_nonsingular_samples` selects r distinct places.
9. `TraceRecovery.common_trace_separator` descends the actual sampled trace matrix to E; `TraceRecovery.determinant_transport` preserves its nonzero determinant under every field embedding.

The transfer and final sampling may use different permitted domains. The domain for transferring to lambda excludes both coefficient residue characteristics, while final selection can use the permitted domain for lambda0. No step requires an ordinary Frobenius trace comparison at every coefficient prime on one globally fixed unramified domain.

## Obligation matrix

| Obligation | Result of this audit | Evidence or missing leaf |
|---|---|---|
| Isomorphic representations have equal characters | Passed by source inspection | Mathlib `Representation.char_iso` |
| Actual representation characters are conjugacy invariant | Passed by source inspection | Mathlib `Representation.char_conj` |
| Irreducible character independence, arbitrary groups/monoids and varying dimensions | Passed by source inspection | `GeneralCharacters.independent_irreducible_characters`; actual monoid algebra and `SimpleModuleSeparation.independent_module_traces` |
| Character continuity for jointly continuous coordinate actions | Passed by source inspection | `GeneralCharacters.continuous_character_of_action` |
| Equality on dense conjugacy-saturated samples implies equality of characters | Available proof ingredients | `DenseRange.equalizer`, conjugacy invariance; existing analogous proofs in `DenseTraceSeparation` |
| Equality of two irreducible characters implies actual representation equivalence | Missing derived wrapper | Two-member specialization of checked independence suffices |
| Nonisomorphic systems give nonisomorphic selected members | Missing formal assembly and explicit isomorphism convention | Contract above; depends on correct overlap density |
| Coverage of every open normal quotient gives conjugacy-saturated density | Passed by source inspection | `ProfiniteSeparation.dense_of_quotient_coverage` |
| Initial coverage survives deleting finitely many sample indices | Failed as a generic implication | Counterexample below; needs an additional robust-coverage hypothesis or arithmetic proof |
| Actual permitted arithmetic Frobenius classes satisfy required coverage | Conditional / not formalized | Arithmetic density leaf; no identified theorem in the bounded source search |
| r independent functions admit r distinct nonsingular evaluations | Passed by source inspection | `FiniteSeparation.exists_nonsingular_samples` |
| Common-field descent and all-embedding invertibility | Passed by source inspection | `TraceRecovery.common_trace_separator`, `determinant_transport` |
| Arithmetic trace identification at excluded residue-characteristic places | Not asserted; must remain excluded | Explicit qualification in source theorem |
| Integral lattice isomorphism from rational trace agreement | Out of scope | Source uses coefficient-field representations, not lattice equivalence |
| Hodge–Tate / Weil–Deligne attachment and carrier summand compatibility | Out of scope for this bridge | They remain other claim dependencies |

“Passed by source inspection” records the exact existing theorem and proof inspected. This reviewer did not replay the compiler or independently certify their transitive imported proof objects.

## Decisive boundary cases

### Removing the irreducibility or semisimplicity condition loses information

For the discrete group Z and a characteristic-zero field K, let

    rho(n) = [[1,n],[0,1]],       tau(n) = identity_2.

Both are representations, have character 2 at every n, and have characteristic polynomial (X-1)^2 at every n. They are not isomorphic: an isomorphism would conjugate rho(1) to the identity and hence force rho(1)=identity. The nontrivial representation is not semisimple. A two-index family that uses tau at the first index and rho at the second is trace-compatible with the family using tau at both indices, yet the families agree at one member and differ at another. This is a valid warning about a weakened trace-compatible definition, not a counterexample to the source's absolutely irreducible arithmetic hypothesis.

### Coverage need not survive a finite exclusion

Let G=C2 with its discrete topology, V=N, s(0) the nonidentity element, and s(n+1)=1. The conjugacy-saturated range equals G, so it is dense and covers all open normal quotients. Deleting the single sample 0 leaves only the identity and destroys density. Therefore generic `QuotientCoverage s` cannot justify density on cofinite overlaps. The arithmetic input should supply coverage after every finite exclusion, or directly on each required overlap.

### Record labels do not define representation isomorphism

`ConditionalArithmeticSpine.Spine` supplies arbitrary `hasWeights` and `hasPacket` relations. These are intentionally not definitions of the arithmetic attachment. The relations are not required by that interface to determine labels uniquely. Two different selected labels can therefore describe the same family of representations at this abstraction level. A proof that “distinct spine records imply nonisomorphic members” would be false without new extensionality/attachment hypotheses. Use componentwise representation equivalence as the source-system isomorphism convention.

### Coefficient embeddings must be shared

Injectivity reflects equality only after both common values have been mapped by the same embedding. If one permits separate embeddings for the two systems at the same coefficient prime, equality of their realized traces does not force equality of their E-valued traces. For example, the two conjugate embeddings of Q(sqrt(2)) into R send sqrt(2) and -sqrt(2), respectively, to the same real number. This does not violate the source's intended fixed embedding convention, but the interface must not omit it.

### Empty family and forbidden primes

For r=0 the selected family is empty and the 0 by 0 determinant is 1. The existing finite-separation theorem supports empty index and sample types. For r>0, density plus character independence supplies enough distinct samples; distinctness should not be imposed as an independent unsupported existence input. A selected place above the residue characteristic of a later coefficient prime still contributes a valid E-valued matrix entry and its field image, but the theorem does not identify that entry with an ordinary unramified representation trace at that prime.

## Source and computation checks

Commands used: bounded `rg` searches for the raw theorem/definitions, direct reads of the source files listed below, and SHA256 calculation of the compact Block 24 archive and inspected primary files. Applicable ancestor `AGENTS.md` locations were checked; none was present. The project has no `.mathbox` directory.

The compact baseline archive was found and its hash independently recomputed:

- `PRSC_X_v0.24.0_Checked_Proof_Bundle.zip`
- size: 17,869,337 bytes
- SHA256: `8bff25880aa4bc30d85a8674a33e99c11dde98e60053e19135515d4eabf68ad5`

A case-insensitive search for `Chebotarev`, `Čebotarev`, and `Chebotar[eë]v` in production Lean, checks, and the pinned Mathlib tree found only a comment explicitly disclaiming Chebotarev in `CommonSpine.lean`. Filename searches for Chebotarev and Brauer variants found no source. The historical scope report was read only after the current raw proof and independent derivation. It does not supply an authenticated primary theorem proving the arithmetic leaf.

The literature-check workflow was consulted for this leaf. No exact external primary source was authenticated or fetched in this bounded read-only audit, so external theorem provenance remains unverified here. This is not a claim that the mathematical arithmetic-density theorem is open, or that no other formal library contains it. No novelty claim is made.

## Strongest safe next block

Prove the irreducible character-equality/isomorphism equivalence and the selected-member reflection theorem with explicit permitted-place overlap density, or with cofinite-robust quotient coverage plus cofinite good-place sets. Connect that result directly to the existing common-field separator. Add the finite-exclusion counterexample to guard against accidentally weakening robust coverage to ordinary coverage. This removes a precise missing representation-theoretic bridge.

Completing those lemmas still does not justify promoting the full arithmetic Claim 9.1: the actual Frobenius construction and arithmetic quotient-coverage theorem must be supplied by checked proofs, or the release must explicitly retain that unproved arithmetic leaf. Unlike Claims 8.2 and 11.2, Claim 9.1 does not state arithmetic density as an assumed closure premise. Adding it is a genuine restriction of the result under formal verification.

## Inspected source hashes

Paths are relative to the Block 24 directory unless indicated.

| File | SHA256 |
|---|---|
| `source/Projector_Resolved_Seed_Calculus_X_Block24_Amended.tex` | `fef55b77f3cb7b3b1c100226cec741b4bf82484ccdf2a3b15c7a4d09bedfa014` |
| `lean/PaperX/GeneralCharacters.lean` | `ed31851177b1a85ea5d836ccf9b2a06a8968cb7c31d77dbea897fb39a28fd7ea` |
| `lean/PaperX/ProfiniteSeparation.lean` | `c23660150cd7a55a7da46770967d33dd9e3c068ced194f78e928be0f00b7ee1b` |
| `lean/PaperX/DenseTraceSeparation.lean` | `2b96061df0f8e7f46d08e168dcf53712011aef1050a40b0ee73a2c8b7c67dd88` |
| `lean/PaperX/FiniteSeparation.lean` | `1975b5fb629823eb7f80c17c995ecc55bc9f19cd1bcf221acfd627f64f20c9cb` |
| `lean/PaperX/CommonSpine.lean` | `d34a9f2b7a2e5011a29ad51c3122531d6b7b369b73f11da75cfc6e8c58d4e6e5` |
| `lean/PaperX/ConditionalArithmeticSpine.lean` | `cb8054a1da634b7753be9ea07c4d29e8aebf849edfc369294f1615c364a87438` |
| `lean/PaperX/SimpleModuleSeparation.lean` | `e76bfbea5d9d71ada508d76381a86770915c44648bcfb7049b428d8cab2db6d2` |
| `lean/PaperX/TraceRecovery.lean` | `d62a7b0966d53bb7331ead3ca41e8b6ba74d5882cc39997a85ebd6ef2e7f73ff` |
| Mathlib `RepresentationTheory/Character.lean` | `89d93daf4d053bad5f98f053fe61d864fb8d7fa5ea6b0da3cd0a728a8190ae3c` |
