# Claim 11.2: exact scope and status correction

Base: Block 23, archive SHA-256 `93d1d13a4dbf8bf71a8d742613c78d7fceff30bb8beb3e0225d438645fd57c70`.

## What the source claims

The corollary “Exact location of the remaining existence problem” retains three requirements: residual companion nonemptiness at every coefficient prime, liftability through every higher finite depth, and positive trace for every required global packet. Its accompanying paragraph retains finite branching and inverse-limit closure. Section 10 fixes the packet carriers, commuting operators and selected eigenvalues before constructing their projectors.

Block 24 proves a precise equivalence in that conditional setting. There is a continuous system realizing the full chosen common spine and an actual nonzero joint eigenvector in each required supplied carrier if and only if all residual levels, all higher levels and all positive packet traces are present. The original corollary is retained. No positive-occupancy theorem is substituted for this criterion.

## What the new statement assembles

`SpineExistenceCriterion.SystemRealization` retains actual integral representations, their admissible conjugacy-class reductions at every depth, continuity after coefficient change, and every item of `ConditionalArithmeticSpine.RealizesSpine`. Those items include common Frobenius-polynomial equations, actual coefficient-specific determinant equations and the selected weight/packet relations. Completion uses their explicit inverse-limit closure assumption.

`SpineExistenceCriterion.full_existence_boundary` quantifies over an arbitrary required-packet index. It returns a dependent family of vectors, one in each carrier. The carriers may differ. No single vector, common ambient carrier or attachment of those carriers to the completed representation is inferred.

| Source ingredient | Formal content |
|---|---|
| Common-spine system and branches | `SystemRealization`, built using checked Claim 8.2; its reductions are admissible at every depth. |
| Residual companion existence | For every coefficient index, an allowed conjugacy class at depth one. |
| Higher-depth liftability | For every coefficient index and every depth at least two, an allowed class. No single finite bound replaces this quantifier. |
| Required global packets | An arbitrary supplied index, with a finite list of split commuting operators and target scalars for each actual finite-dimensional carrier. |
| Exact projector | `JointOccupancy.joint`, computed from actual spectral-polynomial selectors; it is proved to project onto the actual intersection of eigenspaces. |
| Positive trace | `PositiveTrace`: a positive natural number whose cast equals the actual field-valued projector trace. The number is uniquely the joint-space dimension in characteristic zero. |
| Occupancy | A nonzero vector satisfying every selected eigenvalue equation in that carrier. |
| Every required packet | A universal quantifier over the entire index, equivalently one chosen eigenvector in each carrier. The index need not be finite. |

Positivity introduces no order on an arbitrary field. Under the split, commuting and characteristic-zero hypotheses, positive natural trace, positive joint-space dimension and nonzero field trace are equivalent. Absent eigenvalues, zero carriers and empty condition lists retain their actual meanings.

## Correction to prior accounting

The previous partial status included identification and verification of particular arithmetic application data among the obligations of proving this conditional corollary. That was a stronger target. The literal statement fixes the packet setting and identifies the remaining existence requirements; it does not prove them.

Accordingly, the explicit compiled assembly supports checking Claim 11.2 at its universal conditional source scope, consistently with the correction to Claim 8.2 in Block 23. The source ledger becomes **17 checked / 3 partial**. This combines a scope-accounting correction with a completed formal interface. It does not establish new Hodge–Tate or Weil–Deligne attachment, universal companion existence or universal positive occupancy.

A particular arithmetic application must still identify the actual required packets, their carriers and operators, and the common-spine local relations and reductions. It must supply the stipulated closure and all-depth nonemptiness and establish positive occupancy wherever the desired conclusion requires it. Those obligations are not concealed by renaming abstract predicates or arbitrary carriers “arithmetic.”

## Quantifier boundary

For any natural number N, `RequiredPacketBoundary` constructs a family of one-dimensional rational carriers with identity operator. Every packet except the N-th requests eigenvalue one; the N-th requests the absent eigenvalue zero. The actual spectral-projector trace is therefore one except at N, where it is zero.

For every predetermined finite sample, a choice of omitted index N gives a family that passes the sample and fails at N. This disproves a universal inference from arbitrary finite sampling to every-packet occupancy. The family depends on N. It does not say that one fixed family can pass every finite prefix but fail at a natural-number index.

## Remaining source claims and verification status

Claims 9.1 and 9.2 retain actual arithmetic Frobenius separation and local-attachment obligations. Claim 11.1 retains its horizontal-transport interpretation and its recovery clause inherited from those results. The system-plus-occupancy conjunction proved here does not establish any of those recovery assertions.

Independent source-scope review is preserved in `claim112_scope_review.md`. Independent final proof review of all three exact sources and seven edge applications passed; see `CLAIM112_PROOF_AUDIT.md`. All 153 production modules passed the clean build. The 1,844 named declarations passed the transitive axiom audit using only propext, Classical.choice and Quot.sound. The block adds 33 theorem/lemma declarations; the cumulative theorem/lemma count is 1,285. Eight positive controls passed, and 22 false claims plus the placeholder were rejected as intended. All 150 predecessor source and rebuilt proof-object hashes match Block 23. Fresh archive replay reproduced the three new proof objects and the retained Block 22 exact regression.
