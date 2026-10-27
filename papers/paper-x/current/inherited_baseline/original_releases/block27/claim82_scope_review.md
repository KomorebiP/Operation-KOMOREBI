# Independent scope review of Claim 8.2

Baseline: Block 22 ZIP SHA256 `36073e737aac860ef1db06f9cc8e7b9ec915534387f200a1f48f9c4249666c75`.

This is a read-only mathematical scope audit. The primary manuscript and Lean declarations were read before the five-partials ledger. No source theorem or release status was changed, and no new Lean build was run for this review.

## Decision

**A universal completion theorem over arbitrary selected local predicates can faithfully prove the conditional mathematical implication of Claim 8.2. The fact that the predicates are parameters is not itself a gap.** Its explicit inverse-limit-closure hypothesis is allowed to supply preservation of the intended local property. Separately proving that Hodge–Tate or Weil–Deligne conditions have that closure, or constructing every particular arithmetic packet, would impose obligations that this conditional theorem does not undertake.

There remains a precise distinction between this universal implication and an arithmetic application. To identify the original claim with the universal theorem, the manuscript must fix the meaning of its finite-level objects, of closure, and of “realizes the prescribed strictly compatible spine.” Those meanings may be given by a general interface, but they cannot conceal an extra implication. An interface is faithful when realization means the prescribed common polynomial equalities together with the selected full local relations, and closure means that the actual reconstruction of any compatible admissible finite family satisfies those relations. It is unfaithful if it merely attaches arbitrary labels and then calls them actual arithmetic invariants.

The present mathematical and Lean evidence supports completing **the universal conditional implication**, after documenting this exact semantic contract. It does not support claiming that every intended arithmetic deformation condition or packet has been constructed or that its closure hypothesis holds. This report makes no ledger promotion on its own.

## Exact source and logical content

The source is `source/Projector_Resolved_Seed_Calculus_X_Block22_Amended.tex` under `/root/.codex/tmp/paperx_block22`.

- Lines 150–175 introduce a complete DVR with finite residue field and a general moduli functor. The Galois example uses a fixed residual representation and determinant/local deformation conditions.
- Lines 246–275 introduce total adjacent reduction maps and separately state represented-functor inverse-limit reconstruction.
- Lines 759–772 define the common spine by common algebraic characteristic polynomials, weight and determinant data, and local WD **or inertial** labels. They do not define a particular Hodge–Tate or WD attachment functor.
- Lines 787–803 state Claim 8.2: fixed spine; finite nonempty positive levels at every coefficient place; finite branching; inverse-limit-closed selected local conditions. The conclusion is one branch at every coefficient place realizing the common spine.
- Lines 852–874 explicitly distinguish the existing reconstruction theorem from arithmetic applications and acknowledge that source closure is already a hypothesis.

The proof decomposes as follows.

1. Nonempty finite levels and total adjacent reduction maps give a branch at each coefficient place. The branches can be selected simultaneously by choice.
2. For actual fixed-rank matrix representations over a complete coefficient ring, a branch has an actual integral realization, continuous when finite admissible representations are continuous. For isomorphism classes, finite residue quotients allow coherent frames.
3. Prescribed integral polynomial coefficients at every precision give the exact polynomial. Mapping the local integral coefficients and common field coefficients into the local field gives the common polynomial equality.
4. The stated closure hypothesis supplies the selected local properties of the reconstructed member. If weight, determinant, ramification and full local packet matching are among those properties, they hold. No separate arithmetic closure theorem is needed for this implication.
5. If “realizes the spine” is precisely the conjunction of the preceding requirements for the fixed common data, the constructed collection realizes it by definition.

All five steps are a valid general argument. The algebraic word “common” does not create an additional existence theorem, and no Chebotarev or Galois-to-WD construction is used by this implication.

## Exact existing Lean coverage

| Mathematical component | Existing declaration and source location |
|---|---|
| Simultaneous branch selection for any index type | `Compactness.indexed_finite_completion`, `Compactness.lean:159–166` |
| Total reductions preserve admissibility | `RepresentationForests.Conditions.downward` and `tower`, `RepresentationForests.lean:16–25` |
| Actual integral reconstruction | `RepresentationForests.exists_realization` |
| Continuity and actual reconstruction | `RepresentationForests.exists_continuous_realization` |
| Exact polynomial coefficients | `CommonSpine.charpoly_detected`, `CommonSpine.lean:15–28` |
| Prescribed sampled polynomial | `CommonSpine.realization_has_spine`, `CommonSpine.lean:30–42` |
| Comparison in the local field | `CommonSpine.polynomial_base_change`, `CommonSpine.lean:44–52` |
| Framed conditional common-spine theorem | `CompletionAssembly.conditional_common_spine_completion`, `CompletionAssembly.lean:56–89` |
| Unframed conditional common-spine theorem | `ClassCommonSpine.unframed_common_spine_completion`, `ClassCommonSpine.lean:44–86` |

The exact local hypothesis in `CompletionAssembly.conditional_common_spine_completion` is

```lean
(stable : ∀ l ρ, Realizes (I l) (C l) ρ →
  Local l (changeCoefficients (inc l) ρ))
```

The conclusion contains that same `Local` predicate on the actual field-valued continuous representation. This does not infer an unprovided arithmetic property. It proves every instance for which that property is substituted and the source closure hypothesis has the displayed meaning.

`ClassCommonSpine` has the same implication with allowed conjugacy classes at all depths. Its extra finiteness requirements concern the coefficient rings and hold in the source's finite-residue DVR setting. Reduction maps need not be surjective. No Frobenius density premise is required for equality at the specified Frobenius samples: density would be needed for a different recovery/separation conclusion, not for this one.

## Is a generic local relation legitimate here?

Yes, subject to an explicit translation.

Suppose the prescribed local data form a type `D`, the fixed common datum is `d : D`, and `Satisfies l d ρ` is the selected full local condition on a representation. A theorem universally quantified over `D` and `Satisfies`, whose hypothesis is inverse-limit closure of that same relation and whose conclusion is `Satisfies l d ρ`, also proves its arithmetic specializations. The proof need not inspect or construct every possible invariant defining `Satisfies`. This is ordinary universal generality.

The following would be a faithful completion record:

- actual finite-rank representations of the supplied group, or their actual conjugacy classes;
- complete separated local coefficient rings and maps into coefficient fields;
- common polynomial data with local integral lifts and the allowed-place predicate;
- fixed common local data and their selected realization relations on the actual representations;
- finite admissible levels realizing the reduced common data, with total reductions;
- closure of the full selected realization relation under reconstruction;
- realization of the spine defined by these polynomial and relation requirements.

This does **not** justify the assertion that a relation manufactured for an example equals the intended arithmetic relation. That equality is an application obligation. But absence of the equality for every possible example cannot invalidate the universal conditional theorem.

If “strictly compatible” additionally means requirements absent from these data—for example full WD isomorphism even when only inertial labels were selected, a semisimplicity condition not included in admissibility, or a specific common exceptional-place bound not carried by the allowed-place predicate—those extra conclusions do not follow. The source itself says WD **or inertial** labels, so the conclusion should explicitly mean realization of the selected spine, not silently upgrade inertial data to full WD data.

## Adversarial checks of the literal assumptions

### 1. Genuine reduction towers: no branch counterexample exists

For each coefficient place, finite nonempty levels with total adjacent maps have an inverse-limit point. One does not need surjectivity or an additional finite-branching assumption: each child set is a subset of the next finite level. The simultaneous choice is also valid. The existing `Compactness` proof establishes exactly this.

If “forest” meant an arbitrary graded directed graph with nodes of positive depth allowed to have no parent, singletons at every level with no edges would have no branch. That does not refute the intended statement: the earlier source definition explicitly supplies total reduction maps. It only shows that downward closure must remain part of the formal interface.

### 2. Ambient functor effectivity is distinct from preservation of extra local conditions

There is a literal arbitrary-moduli-functor boundary if one interprets assumption 4 as only closure of *extra* local conditions and leaves effectivity of the ambient functor unspecified.

Let `O = Z_p`, and on complete local `O`-algebras set

\[
\mathcal M(A)=\{x\in A:\ x\text{ is nilpotent and }x-p\in p^2 A\}.
\]

Ring homomorphisms preserve both conditions, so this is a functor. Every finite quotient `O/p^m` has a finite nonempty set of such points: the image of `p` is a point. Reductions are total. Extra local conditions can be vacuous. Yet `M(O)` is empty: the only nilpotent in the domain `Z_p` is zero, and `-p` is not in `p^2 Z_p`. The compatible finite points given by `p` have no `M(O)` realization.

This is **not** a counterexample to the branch conclusion. It is also **not** a counterexample to the intended fixed-rank Galois-representation version, whose ambient effectivity has been proved directly, or to a reading of source assumption 4 that already includes effectivity of the whole admissible-object condition. It locates the needed semantic distinction. For general moduli functors, one must use the earlier represented/effective-functor hypothesis or explicitly include it in the closure convention; merely declaring an empty integral locus topologically closed does not give effectivity.

### 3. Finite label equality alone does not imply exact label equality

An arbitrary label set need not be separated by its reductions. For example, two labels can have the same image in every finite label set. Requiring each finite object to carry the reduction of a target label then does not force the integral object's label to equal that target.

Thus source sentence “equality at every finite precision implies equality in the complete coefficient ring” proves equality for coefficient-valued invariants such as polynomial coefficients. It does not by itself prove equality of an arbitrary WD-orbit or inertial label. For non-coefficient labels, the full fixed-label realization relation must be covered by assumption 4, or a separate separatedness theorem for the label reductions must be supplied. The former is sufficient for the conditional theorem and imposes no unconditional arithmetic closure burden.

## Recommended next action

Do not spend another block proving an unrelated restricted local example merely because actual HT/WD definitions are not instantiated. First write a precise theorem contract stating that the selected full local relation—including the fixed local part of the spine—is the property covered by assumption 4. Package the already proved reconstruction and polynomial conclusions with this relation. Make explicit that the arithmetic theorem is conditional on the supplied finite admissible levels and their stated closure.

An independent review should then check the new contract clause by clause against the four manuscript assumptions and the earlier DVR/Galois-object setup. If they match, the universal conditional implication can be recorded as checked while arithmetic applications and verification of its premises remain open. If the project instead intends “Claim 8.2 complete” to certify a specific not-yet-defined arithmetic deformation functor and its exact local packet reductions, it must first name that functor; the present source does not determine one.

## Input hashes

- Manuscript: `c963d3926a10af5f574097084e760595d7c25f21767ed814970d614b8485181c`
- `CommonSpine.lean`: `d34a9f2b7a2e5011a29ad51c3122531d6b7b369b73f11da75cfc6e8c58d4e6e5`
- `CompletionAssembly.lean`: `1900d2142d60552da6d0e8816a83eac1b4240133ea2e311ffcfa6f0e650b293c`
- `ClassCommonSpine.lean`: `80b55f61d6d502c23379d43b40c42bf03a56ee83fc801a3be85ae20b57e43cfd`
- `RepresentationForests.lean`: `af41085503e926e54cc8ec1f2554983a2b99dc6f129055148c5b511284df8831`
- `Compactness.lean`: `0bd9169cb2b0efc4938e70d7f13d535fcdce0066f6d98d72602a5686e08663f2`
