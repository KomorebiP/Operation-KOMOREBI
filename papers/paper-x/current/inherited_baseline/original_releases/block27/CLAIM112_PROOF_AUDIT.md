# Independent proof audit of Claim 11.2 and Block 24

**Normalized claim and primary verdict: proved as written, at the conditional scope below.**

Fix the complete common spine, its downward-closed admissible finite representation classes, the complete coefficient rings and continuous coefficient maps, and a family of required supplied spectral packets. Each packet has its own finite-dimensional carrier over a characteristic-zero field, a finite list of commuting split operators, and selected eigenvalues. Then an actual continuous system realizing the full chosen spine, together with a nonzero joint eigenvector in every required carrier, exists if and only if every residual companion exists, every higher finite level is nonempty, and every required actual spectral projector has positive integer trace.

This verdict concerns the universal conditional implication of source Claim 11.2. It does not identify an unspecified arithmetic packet with a carrier, prove the closure or nonemptiness premises for all intended arithmetic data, embed the reconstructed system into any supplied carrier, or establish universal occupancy.

## Authoritative source and review method

The statement was read directly in the frozen Block 23 manuscript, `source/Projector_Resolved_Seed_Calculus_X_Block23_Amended.tex`, before any current ledger: common spine and Claim 8.2 at lines 763–805, finite spectral occupancy at lines 1383–1441, universal occupancy at lines 1484–1488, and Claim 11.2 at lines 1510–1524. The older status discussion at lines 1553–1562 is historical status evidence, not the authoritative mathematical statement.

The raw final versions of `RequiredPacketOccupancy.lean`, `RequiredPacketBoundary.lean`, and `SpineExistenceCriterion.lean` were reviewed in an isolated subagent. No production source was edited. The exact definitions and proofs in all 19 internal dependency modules were read. The attached source manifest pins the reviewed bytes, including the raw predecessor manuscript. This is independent exact-source review of all three new modules, not a review of a builder's summary.

The three modules add 33 theorem declarations and five definitions. Their proof objects were rebuilt in an isolated directory containing only the 150 hash-verified frozen Block 23 predecessor proof objects and the newly copied sources. The initial isolated directory contained no proof objects for the three new modules. The frozen predecessor archive was independently hashed as `93d1d13a4dbf8bf71a8d742613c78d7fceff30bb8beb3e0225d438645fd57c70`.

## Claim card

- Coefficients: each complete integral coefficient ring `O l` has a finitely generated ideal `I l` and finite residue ring. `K l` is a field with specified topology, and `inc l : O l →+* K l` is continuous for the ideal-adic topology. The common polynomial coefficient field `E` maps to each `K l`; no map `E → O l` is assumed.
- Representation objects: actual monoid homomorphisms `G →* Matrix ι ι (O l)`, with finite matrix index. Since `G` is a group, their values are invertible. Finite objects are actual matrix-conjugacy classes over `O l / I l^k`.
- Finite conditions: the `ClassConditions.downward` field gives total reduction maps preserving admissibility. Finite nonempty class levels give finite nonempty sets of all frames; surjectivity of successive reduction maps and prechosen compatible frames are not assumptions.
- Closure: `InverseLimitClosed` is an explicit premise on the selected full local realization predicate. It quantifies over genuine compatible quotient-representation families and applies the existing reconstruction. It is not an existence assumption or a definition of Hodge–Tate or Weil–Deligne attachment.
- Full-spine target: `SystemRealization` contains allowed reductions at every precision, continuity of every field-valued member, every good-place common characteristic polynomial, the whole specified determinant family, the selected weight relation, and every selected local packet relation. The source's cofinite good-place data remain in `Spine`.
- Global occupancy target: for every index `p`, there is a nonzero vector in its own carrier `A p`, satisfying every selected eigenvalue equation. The packet index is arbitrary, possibly infinite or empty. It is not the same as the finite list of operators within one packet.
- Trace positivity: `PositiveTrace` means a positive natural-number preimage of the actual field-valued trace. Under characteristic zero and the spectral hypotheses that preimage is uniquely the joint-space dimension. No ordering of a coefficient field is used.

## Dependency graph

1. `ClassConditions` and finite residue coefficients give finite sets of actual frames above finite allowed classes (`ClassCompletion`). Continuity is independent of matrix frame (`ClassInvariants`, `ClassCommonSpine`).
2. Positive precision nonemptiness gives the zero precision through downward reduction, then finite branch compactness constructs compatible matrices. `RepresentationLimits` reconstructs the actual integral representation and proves exact reduction, group laws, and invertibility.
3. `RepresentationTopology` proves actual continuity from continuous finite reductions. `CommonSpine` recovers complete characteristic polynomials by separatedness. `DeterminantSpine` independently recovers determinants by separatedness.
4. `ConditionalArithmeticSpine.adelic_finite_depth_completion` applies the explicit closure premise to all chosen weight and packet conditions, yielding the full `SystemRealization` target.
5. `SpineExistenceCriterion.system_iff_positive_levels` adds the converse by reducing an existing realization. `system_iff_residual_and_higher` separates depth one from all depths at least two.
6. `SpectralProjectors` constructs the actual Lagrange polynomial projector from the actual eigenvalue set, with zero for absent targets. `JointOccupancy` proves the actual product projects onto the actual joint eigenspace and that its trace is the dimension cast into the field.
7. `RequiredPacketOccupancy` uses injectivity of the natural cast in characteristic zero to equate positive integer trace, positive dimension, and actual nonzero eigenvector existence. Choice selects a separate witness in every indexed carrier.
8. The final theorem combines the full system criterion and all indexed occupancy equivalences. Neither component is used to prove the other's nonemptiness.

All internal leaves are Lean proofs or explicit data/premises. No unchecked external arithmetic theorem, assumed realization bijection, or computational experiment occurs in the implication.

## Obligation matrix

| Obligation | Result | Decisive evidence |
|---|---|---|
| Every required packet, rather than one or a finite sample | Passed | Every equivalence ends with `∀ p`; dependent witness function is `(p : P) → A p`. |
| Positive trace over arbitrary characteristic-zero fields | Passed | Unique natural preimage proved using `Nat.cast_injective`; no field order instance. |
| Actual projector and actual carrier | Passed | `joint` is a product of `spectral` polynomial evaluations; `Occupied` is a nonzero vector with actual operator equations. |
| Common polynomials retained | Passed | `SystemRealization` contains `RealizesSpine`; good-place polynomial equalities are in that predicate. |
| Determinants and all selected local conditions retained | Passed | Determinants are a separate full-family conjunct; weights and every selected local packet are retained through `LocalRealizes`. |
| No assumed global realization or level nonemptiness | Passed | Final theorem parameters contain finiteness, continuity, reduction specifications, and closure, but no occupancy/existence premise. Nonemptiness is on the right side of the equivalence. |
| No loss of residual or higher-depth requirements | Passed | Depth one and every depth `k ≥ 2` occur separately in the final statement. |
| Zero precision handled correctly | Passed | Existing positive-level completion derives its allowed zero-level representative by reducing a residual one. |
| Independent witnesses in varying carriers | Passed | The witness family has a dependent codomain; choice supplies each vector separately. No witness identity or common ambient carrier is imposed. |
| Empty lists and zero-dimensional carriers | Passed | Independent applications show empty conditions occupy a nonzero one-dimensional carrier and fail in the zero carrier. |
| Empty required index | Passed | Independent application constructs the empty witness family without requiring any nonzero vector. |
| Finite-sample counterexample quantifiers | Passed | A different family is constructed for each omitted index/sample. The statement does not assert that one family passes every finite prefix while failing globally. |
| Source-to-application arithmetic identification | Out of scope | No arbitrary supplied packet is declared to be an actual unspecified arithmetic packet. Applications must supply the intended data and satisfy the retained premises. |
| Universal occupancy | Out of scope | Source Section 10 states this separately as a conjecture. The new theorem does not prove any unknown packet's positive trace. |
| Axiom and placeholder contamination | Passed | All 38 new named declarations audited transitively; only `propext`, `Classical.choice`, `Quot.sound`. |

## Independent verification

Pinned compiler: Lean 4.34.0-rc2 from the existing portable kit. Commands and exact source/object hashes are in `checks/claim112_audit/compilation.json`. Each module was compiled with `-DwarningAsError=true`, using the isolated `lean_env.py` and copied frozen predecessor objects. All three compilations exited zero. The new source hashes were checked again after compilation and after this review.

`checks/claim112_audit/Axioms.lean` prints the transitive axioms for all 38 new named declarations; compilation exited zero and only the project-standard three axioms appeared. This independent audit does not claim a new cumulative rebuild of all 153 production modules; that is a separate release gate.

Seven additional compiled applications are in `checks/claim112_audit/EdgeApplications.lean`:

1. Zero-dimensional carrier with an empty condition list has no positive trace in characteristic zero.
2. A one-dimensional carrier with an empty list is occupied.
3. In characteristic two, even the zero projector has a positive natural-number preimage of its field trace, demonstrating why `CharZero` is essential for the intended positivity convention.
4. An empty required-packet index has an empty witness family.
5. An infinite packet family can use carriers of dimensions `p + 1`.
6. The omitted packet may be index zero, covering the empty-prefix boundary.
7. Every finite prefix of one fixed family does imply pointwise occupancy, confirming that the negative examples use the correct changing-family quantifiers.

The third edge application required four development attempts. `simp` and `norm_num` alone initially left the valid equality `0 = 2` in `ZMod 2`; a too-narrow simplification then left noncomputable `finrank` for `decide`. The final check simplifies the dimension and proves the residual finite-ring equality using kernel `decide`. All three failed sources and logs are retained. These were failures in the independent audit fixture, not production proof failures. The final complete edge application file exits zero.

## Exact scope and remaining gap

No missing implication was found in the final universal conditional criterion at the supplied-object scope stated above. Source Claim 11.2 is an existence boundary combining reconstruction and occupancy in fixed carriers. It does not assert that these independent requirements automatically hold or that a vector in an unrelated supplied carrier realizes the reconstructed Galois system.

The strongest safe release statement is: **the full common-spine conditional existence criterion, together with positive trace occupancy for every required supplied spectral packet, is proved in Lean.** Claiming automatic arithmetic attachment, an unknown carrier's existence, a system-to-carrier embedding, or universal positivity would exceed both the proof and this audit. For a concrete arithmetic application, the next check is the exact identification of its finite admissible classes, local realization relation, required carrier family, and the retained nonemptiness/closure premises.
