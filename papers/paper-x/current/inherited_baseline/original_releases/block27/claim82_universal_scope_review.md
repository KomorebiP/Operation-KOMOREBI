# Provisional adversarial scope review of universal conditional Claim 8.2

Date: 2026-09-08. Reviewer inspected the frozen Block 22 source statement, its preceding definitions, the existing representation/class completion interfaces, and the proposed Block 23 target contract. This is a **scope opinion before review of the final new Lean definitions and theorem**. It is not approval of uninspected code or a new arithmetic construction.

Base archive SHA256: `36073e737aac860ef1db06f9cc8e7b9ec915534387f200a1f48f9c4249666c75`.

## Conditional verdict

**Yes, the inference asserted by Section 8 can be completed as a universal conditional theorem without constructing Hodge–Tate or Weil–Deligne invariants or proving their closure unconditionally.** The source explicitly assumes inverse-limit closure of the selected local conditions. A theorem universally quantified over precisely specified local label relations and their finite versions can prove the inference for every interpretation satisfying that assumption. Such a theorem is not weakened merely because its proof is independent of the internal construction of those relations.

This does **not** justify saying that the intended arithmetic instances, attachments, or closure facts have been verified. Earlier ledgers used “full arithmetic scope” to include those instances. Changing Claim 8.2 to checked at its actual universal conditional statement must therefore be announced as a correction of that earlier, stronger verification target. It must not be described as newly constructing the missing arithmetic invariants.

The verdict is subject to the premise correspondence and effectivity restrictions below. Merely adding fields named `HodgeTate` and `WeilDeligne` to an arbitrary predicate would not meet them.

## What the source actually fixes and assumes

Section 8 defines a common arithmetic spine by three kinds of prescribed data:

1. Polynomials `P_v(X)` over a number field at almost all places.
2. Coefficient-prime-independent weight and determinant data.
3. Prescribed local Weil–Deligne or inertial packet labels at ramified places.

It then defines `X_{lambda,m}(Compat)` to be the finite set of admissible objects modulo the coefficient uniformizer power **realizing the reduction of this spine**. Its theorem assumes the spine is fixed, these levels are finite and nonempty at every positive precision, the reduction forests are finitely branching, and selected local conditions are closed under inverse limits.

The conclusion first asserts a compatible branch at every coefficient prime and then that the family realizes the prescribed spine. The proof invokes compactness, assumed local closure, and equality at every precision in a complete separated coefficient ring. It does not invoke or prove an unconditional Hodge–Tate closure result, Weil–Deligne comparison theorem, Chebotarev theorem, or arithmetic occupancy theorem.

The ambient context supplies complete DVRs with finite residue fields. It discusses an arbitrary moduli functor initially, but identifies Galois representations with determinant and local deformation conditions as the principal example. Section 3 proves effectivity for represented complete deformation problems under an explicit representability premise.

## Necessary input map

| Formal datum or premise | Source role | Assessment |
|---|---|---|
| Coefficient index, complete coefficient rings/fields, inclusions, and common-field embeddings | Finite places of the number field and their coefficient completions | Ambient data. Allowing arbitrary such families generalizes the proof, provided the theorem does not claim to have constructed the arithmetic family. |
| Finitely generated coefficient ideal and finite residue ring | Uniformizer ideal in a complete DVR with finite residue field | Consequences of the stated ambient setting, not new arithmetic hypotheses. The universal theorem may use these weaker properties directly. |
| Actual finite representations or actual integral conjugacy classes | The representation interpretation of admissible finite objects | Necessary for the existing constructive effectivity proof. Do not silently claim effectivity of every arbitrary moduli functor. |
| Total downward reductions preserving allowed levels | Meaning of a reduction forest and inverse system | Structural/definitional. No surjectivity or extension of every individual node may be added. |
| Finiteness and nonemptiness at every positive precision | Numbered premise 2 | Explicit source hypotheses. No uniform lift of a selected node is supplied. |
| Finite branching | Numbered premise 3 | Already follows from finite full levels for a tower with total reduction; may be derived rather than repeated. |
| Continuity of finite Galois representation classes | Meaning of admissible finite Galois objects | Definitional for the intended continuous representation problem. For arbitrary abstract group maps it is an additional premise for the stronger continuity conclusion. |
| Sample maps and permitted-place predicates | Where the given Frobenius polynomials are prescribed | Supplied structural data. No density theorem is needed. The chosen domain must preserve the manuscript's exclusions, including coefficient-characteristic exclusions when appropriate. |
| Integral local polynomials with the specified common-field base changes | Meaning of “reduction of” the common polynomial spine | Required typing/integrality data, not an independent existence claim. Do not impose a map from the whole number field into its integer ring. |
| Finite-level polynomial and determinant equalities for every allowed object | Definition of `X_{lambda,m}(Compat)` | Definitional once the finite-level spine interpretation is fixed. |
| Types of weight and packet labels, prescribed common labels, and coefficient-specific realization relations | Meaning of the selected weight/local data | May remain universally quantified. The theorem must not assert these abstract relations are already a constructed arithmetic attachment. |
| Finite versions of those relations plus an implication from their validity at every reduction to the integral/local realization relation | Numbered premise 4 | The precise inverse-limit closure premise needed by the proof. It must be exposed, not concealed in a typeclass whose fields include system existence. |

In particular, the valid logical shape is:

`for every integral rho, (every finite reduction has the prescribed finite local relation) -> rho has the prescribed integral local relation`.

The theorem should derive the antecedent from actual membership in the allowed levels and derive an actual `rho` by the existing matrix/class reconstruction. It must not assume a realizing `rho`, an arbitrary realization bijection, finite-depth occupancy as a consequence of closure, or an isomorphism between unrelated packet labels and actual local data.

## Four hostile checks

### 1. The closure premise must be the right premise

There are different statements informally called “closed.” A subset of integral representations can be topologically closed without an arbitrary choice of finite-level predicates having anything to do with it. Therefore topological closedness alone, paired with unrelated finite predicates, cannot justify the limit assertion. Conversely, if finite admissibility and its closure are supplied in the exact all-reductions implication above, the source's proof uses precisely that assumption and no unconditional local comparison theorem is missing from the conditional inference.

The finite predicate must be connected to allowed-level membership. A bare implication `allowed at every precision -> desired local conclusion` is logically sufficient, but exposing the finite local predicates and their relation to the selected labels makes the source correspondence checkable and avoids a hidden assumption of the desired arithmetic conclusion.

### 2. Determinant data must not be strengthened

The source says common determinant **data**. It does not require one character `G -> E*` over the common number field whose scalar extensions are all determinant characters. Requiring that one global character would be a substantive restriction.

A safe representation interface uses coefficient-specific determinant characters/values, their integral reductions where defined, and their prescribed compatibility data. Common Frobenius determinant values then follow from the common characteristic polynomials. A generic label relation can encode further determinant compatibility if the source's chosen data require it. The final proof must not silently replace these with a stronger global number-field-valued character assumption.

### 3. Actual effectivity must be proved or appropriately scoped

The existing `ClassBranchLifting` and `ClassCommonSpine` results construct actual matrix representatives over complete coefficient rings from genuine finite conjugacy classes, using finite frame fibers. This discharges effectivity for that representation setting and does not assume a realization map.

The same is not automatically true for an arbitrary moduli functor from Section 1. For example, the functor assigning a singleton to an algebra when the uniformizer is nilpotent in that algebra and the empty set otherwise has singleton values at every uniformizer-power quotient and empty value at the DVR itself. It is functorial, and its finite tower is nonempty and compatible. This demonstrates why an unrestricted moduli-effectivity assertion needs more than compactness. It is not a counterexample to the intended actual-representation version, whose effectivity has been proved.

Accordingly, a checked declaration for actual representations may be presented as Claim 8.2's Galois-representation completion inference. A claim that it proves the same result for every arbitrary moduli functor would require a separate represented/effective-functor input or a source clarification.

### 4. Independent local labels do not constitute an attached invariant theorem

Universal quantification over label realization relations is legitimate. Calling one such relation “the Hodge–Tate condition” does not construct the actual invariant. The final result should say it realizes the **supplied** weight and packet relations under their stated finite-level interpretation and inverse-limit closure, and separately state whether any arithmetic interpretation has been instantiated. A reader must be able to see both facts simultaneously.

## What a justified promotion would mean

If the final Lean theorem reconstructs actual representations and actual branches, recovers all common polynomials and specified determinant data, and proves every selected weight/packet relation under precisely the source's matching closure hypotheses, the conditional theorem's proof can be marked checked. Further arithmetic instantiations are then applications whose premises have to be supplied, not missing steps in that universally quantified implication.

The release should also correct the earlier accounting explicitly: previous status demanded verification of intended arithmetic applications in addition to the conditional source inference. Those applications remain unfinished. This is not the same as proving their premises, and it does not settle the Hodge–Tate/Weil–Deligne attachment needed by other claims, especially 9.2.

This provisional opinion is more permissive than my first report's assessment at the prior ledger's **full arithmetic application** target. The difference is the target being assessed: a genuinely universal conditional theorem is a valid theorem, while an uninstantiated generic theorem is not evidence that a particular arithmetic interpretation has been verified. Final source-to-Lean review must establish which one the release actually claims.

## Evidence and pending review

Frozen source: `/root/.codex/tmp/paperx_block22/source/Projector_Resolved_Seed_Calculus_X_Block22_Amended.tex`, SHA256 `c963d3926a10af5f574097084e760595d7c25f21767ed814970d614b8485181c`.

Inspected existing interfaces: `ClassCommonSpine.lean`, `ClassCompletion.lean`, `ClassBranchLifting.lean`, `RepresentationForests.lean`, and `CommonSpine.lean` in the frozen Block 22 tree. Proposed contract: `/root/.codex/tmp/paperx_block23/CLAIM82_TARGET_CONTRACT.md`.

Pending: the new raw definitions, exact theorem signature, proof, compiler evidence, and final ledger wording. No final promotion is certified by this pre-code review.

## Addendum: review of the compiled core source

The following new raw source files were subsequently read in full:

* `lean/PaperX/ConditionalArithmeticSpine.lean`
* `lean/PaperX/DeterminantSpine.lean`
* `lean/PaperX/InverseLimitLocalConditions.lean`

The author reports all three compiled; their proof-object files are present. This review does not substitute that report or file presence for the release's independent compiler/audit evidence. It assesses the full definitions, signatures, and proof expressions directly.

**Source-to-core verdict: pass for Claim 8.2's universal conditional inference in the actual representation setting**, subject to the explicit scope accounting below. No new mathematical hypothesis was found that strengthens the intended local-closure premise or assumes the sought representation exists.

`ConditionalArithmeticSpine.Spine` exposes common polynomial values, permitted samples, coefficient-specific determinant prescriptions, common weight labels, and indexed common packet labels. Its `hasWeights` and `hasPacket` fields are supplied realization relations, and the module expressly disclaims construction of an attached arithmetic invariant. `RealizesSpine` spells out each corresponding conclusion instead of merely renaming an opaque representation predicate.

`InverseLimitLocalConditions.InverseLimitClosed` has precisely this shape: every actual compatible matrix family whose reduction classes lie in the allowed levels reconstructs to a representation satisfying the supplied condition. Its equivalence with the corresponding all-reductions property is proved using the two actual reconstruction/reduction identities. It contains no existence field, no carrier, no realization bijection, and no positive-occupancy assumption. The core theorem applies it only after constructing a realizing representation by unframed completion. Thus its use is the source's premise 4, not a proof of that premise for particular arithmetic conditions.

`DeterminantSpine` defines an actual determinant monoid homomorphism, proves conjugacy invariance, defines the determinant on genuine representation classes, and detects equality by all coefficient reductions. The top-level theorem uses coefficient-specific `S.determinant l g`, integral local determinant values, and their actual reductions. The optional helper about a common number-field-valued determinant is **not** a premise of the top-level theorem. The previously identified determinant-strengthening hazard is avoided.

The final proof uses `unframed_common_spine_completion` to construct integral representations realizing all admissible classes, proves continuity of their coefficient-field changes, recovers all prescribed Frobenius polynomials, and adds determinant and selected weight/packet conclusions. Although the result does not separately return a `Branch` structure, the actual finite reductions of the returned representation are compatible by the proved reduction identities and belong to every allowed class level. This supplies the source's branch conclusion without an additional existence hypothesis.

The finite local-label predicates are packaged in the allowed class family rather than exposed as additional standalone fields. Consequently the `closed` premise is expressly relative to that same allowed family. This is mathematically sufficient for the conditional inference. A concrete application still must prove that its actual finite admissible objects and its actual local relations satisfy that premise; this core does not conceal an application proof.

### Remaining source metadata and effectivity qualification

The theorem deliberately permits arbitrary coefficient indices, groups, permitted-sample predicates, and complete coefficient families. In particular it does not itself prove that the index is the finite places of a number field, that the sample map consists of arithmetic Frobenius elements, or that the good-place set is cofinite. Such metadata are part of the source's chosen arithmetic data and remain fixed on application. The proof works for arbitrary choices, so these generalizations do not invalidate the conditional implication. They must not be advertised as arithmetic constructions or new facts about the permitted places.

The theorem's actual object type is finite-rank group representations and their integral conjugacy classes. It proves effectivity there. It does not extend Section 3's represented-moduli effectivity theorem to every arbitrary moduli functor from Section 1. For the Galois-representation reading of Section 8 this is the intended concrete category; a broader moduli assertion would still need an explicit effectivity premise.

### Ledger decision supported by this review

Promoting **the conditional source statement of 8.2** to checked is supported by the inspected core, once the release compiler, axiom, and archive checks pass and its statement/source mapping is preserved. Reporting a 16 checked / 4 partial source-claim count is then defensible **only with the announced correction of the former arithmetic-application scope**. The author must state that actual Hodge–Tate/Weil–Deligne attachment, arithmetic local closure instances, and identification of the intended finite arithmetic packets remain unproved application obligations.

It would be misleading to say that all arithmetic obligations formerly grouped under 8.2 have been proved, or that this release constructs a general strictly compatible arithmetic system without supplying the theorem's arithmetic data and closure hypotheses. This review supports the universal conditional theorem and does not support those stronger descriptions.

Final ledger wording and release compiler/axiom evidence remain outside this raw-core scope check; changes to these source files require a renewed check of the changed material.

Reviewed Block 23 core hashes:

| Source | SHA256 |
|---|---|
| `lean/PaperX/DeterminantSpine.lean` | `043fdc73af2916db6dd6b55c0a59ea1e9887c2298955ac3d2dc849a6529ec817` |
| `lean/PaperX/InverseLimitLocalConditions.lean` | `3d4c7a36a60487d0051b3fca82efd8f1b5ae34b4ebbf16939cf6b2b324adbe2b` |
| `lean/PaperX/ConditionalArithmeticSpine.lean` | `fee17787d68c9932b04bc1f7714f28d383fd4f4a79f0b0ae7c573cc53e69ca46` |
| `CLAIM82_TARGET_CONTRACT.md` | `4c07f955a76b0088d3a2c858e417c8d16cb102cd67eeb20b775f8c1c7e709243` |
