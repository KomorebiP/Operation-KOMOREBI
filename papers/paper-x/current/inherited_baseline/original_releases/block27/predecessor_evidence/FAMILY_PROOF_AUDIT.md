# Block 19 independent proof audit

**Normalized claim.** Let R be a commutative integral domain, π an element such that R is complete for I=(π), Γ a finite group, and ρ an actual supplied representation on R^ι with finite coordinate set ι. Suppose |Γ| is nonzero in R and divides π^e. For k>0 and any finite label type J, every complete labeled orthogonal family of equivariant projectors on ρ modulo I^(e+k) has an actual complete labeled orthogonal family on ρ retaining all its matrices modulo I^k. The precision loss e is independent of |J| and |ι|. Every resulting family gives an equivariant linear decomposition into its actual images. If R is also local and π is a nonunit, any two such families with the same labeled reduction modulo I^k are conjugate by an equivariant matrix unit congruent to the identity modulo I^k.

**Primary verdict: proved as written.** This verdict concerns the nine new algebraic Lean modules under the hypotheses above. It does not upgrade the five full arithmetic claims.

The review was performed by a separate audit subagent against the raw source files, rather than relying on author verdicts. All nine final source revisions were independently compiled with warnings treated as errors; their hashes are recorded in `FAMILY_PROOF_AUDIT_SOURCES.json`. Imported predecessor proof objects were reused for this independent module replay. The cumulative rebuild and full declaration audit are separate release evidence.

## Dependency graph

1. `MatrixProjector.Projector` requires the actual equations P²=P and ρ(g)P=Pρ(g). `OrthogonalProjectors.Family` additionally requires ordered pairwise orthogonality and total sum 1. These are obligations, not labels standing for unconstructed objects.
2. `PrecisionAveraging.exists_intertwiner_lift` produces each exact equivariant A_i from the supplied quotient matrix at depth e+k, retaining depth k. Nonzero |Γ| and its divisibility into π^e justify integral cancellation. No exact lift or coherent comparison family is assumed.
3. `AdicIdempotent.correct_commuting` uses polynomial iteration, adic reconstruction, and separatedness to correct approximate idempotents while preserving every existing commutant.
4. `CornerProjectors.exists_in_corner` compresses A to B=CAC for the complementary projector C. Correction gives an idempotent Q commuting with C and the carrier action. The actual output C Q is an idempotent supported on both sides by C, with the required reduction.
5. `OrthogonalPartial` supplies exact finite-sum and complement identities. `OrthogonalLifting.exists_partial` inducts over a finite label subset, inserting each newly corrected projector in the complement of the previous ones. The two support equations prove both orders of orthogonality.
6. `exists_family_of_equivariant_lifts` lifts all labels and proves their sum is 1. The remaining complement is an idempotent reducing to zero at positive depth; its entries lie in every ideal power, so separatedness forces it to vanish. `exists_family_lift` invokes averaging once per label before this same-depth argument.
7. `FamilySummands` uses the actual projector ranges. Its forward map sums included components, and its inverse applies the projector retractions. Totality proves one composite is the identity; orthogonality proves the other. The actual restricted carrier actions are intertwined.
8. `FamilyRigidity` sets U=Σ_i F_i E_i. Orthogonality proves U E_j=F_j U. Each summand commutes with ρ, and equal labeled reductions imply U reduces to 1. A unit-reflecting coefficient map makes U a matrix unit. The local-ring positive-quotient lemma supplies that hypothesis in the stated π-adic application. `FamilyClassification` combines existence and this conjugacy theorem.

All these leaves are internal Lean proofs or imported Mathlib APIs. The audit does not rely on an unverified external literature theorem, a numerical experiment, or a new arithmetic attachment assumption.

## Obligation matrix

| Obligation | Result | Evidence and exact scope |
|---|---|---|
| Actual ambient carrier and quotient family | Passed | `ρ` and `Q` are explicitly supplied; family fields contain the complete equations. |
| Uniform precision across all labels | Passed | Only the initial averaging uses e+k; every corner correction retains the same k. No cardinality-dependent precision occurs in the theorem or induction. |
| Two-sided corner support and orthogonality | Passed | Both C P=P and P C=P are proved and used in opposite multiplication orders. |
| Totality after lifting | Passed | Zero-idempotent detection uses separatedness; it does not assume totality of arbitrary independent lifts. |
| Empty and unary labels | Passed | The finite induction includes the empty subset. Independent Lean smoke examples instantiate an empty family on the zero carrier and a unary family on a rank-one carrier. A unary complete family is the identity. Empty complete families cannot be silently asserted on a nonzero carrier. |
| Positive-depth and domain hypotheses | Passed | k>0 is required for correction and zero-idempotent detection. Domain and nonzero group order are used in averaging. Locality and π nonunit belong to the π-adic conjugacy corollary, not to the general existence theorem. |
| Actual image decomposition | Passed | The components are range submodules, with explicitly inverse linear maps and equivariance. No basis, freeness, intrinsic quotient-module isomorphism, or packet identification is silently inferred. |
| Labeled conjugacy direction | Passed | U E_i U⁻¹=F_i. The inverse and restricted image isomorphisms use the same direction consistently. |
| Independence from chosen lifts | Passed at the stated level | All exact families with the same retained labeled reduction are equivariantly conjugate by a unit equal to 1 there. Equality of families, a canonical lift, or unlabeled permutation invariance is not asserted. |
| Concrete positive example and sharpness | Passed | The generic lifting theorem is invoked on a three-projector C2 example over Z_2, from modulo 4 to modulo 2. Each output projector is nonzero. Full modulo-4 retention is proved impossible. |
| Source hygiene and selected axioms | Passed | All nine sources were scanned. Eight principal declarations were independently checked transitively and use only propext, Classical.choice, Quot.sound. The release audit covers every recorded declaration. |
| Full arithmetic claims | Out of scope | Supplied carrier, intended arithmetic packet, Frobenius coverage, and period/Weil–Deligne/Hodge–Tate identifications are not constructed here. |

## Decisive boundary checks

For the trivial C2 carrier over Z_2, E=diag(1,0) and P=[[0,2],[0,1]] are exact equivariant idempotents. P reduces to diag(0,1) modulo 2, but E P=[[0,2],[0,0]] is nonzero and E+P is not 1. Thus independent idempotent lifting does not establish family lifting. `FamilyBoundary` proves these statements in Lean.

The two complete families `{diag(1,0),diag(0,1)}` and `{[[1,-2],[0,0]],[[0,2],[0,1]]}` have equal labeled reductions modulo 2 but are distinct. Their comparison is U=[[1,2],[0,1]], which is congruent to 1 and conjugates the labels correctly. The general rigidity theorem is also explicitly invoked on these families.

For ρ(generator)=diag(1,-1,1), the three integer projectors in `FamilyExamples` are complete and orthogonal and commute with ρ modulo 4. Their mixed-sign off-diagonal entries are ±2. Exact commutation forces that entry x to satisfy 2x=0 in Z_2, hence x=0. Therefore the prescribed modulo-4 family cannot be retained exactly. The generic theorem nevertheless constructs three nonzero exact projectors retaining modulo 2. This tests nonunit group order and more than two summands.

Both explicit matrix fixtures were also recomputed with exact integer arithmetic by this auditor. The record is `checks/family_audit/boundary_recompute.json`; its scope is precisely these fixtures, not exhaustive classification.

## Commands, provenance, and limits

The independent build used the pinned Lean 4.34.0-rc2 runtime and Mathlib revision aeb72f1e9981b6d35b426b16dca7759be3e7ba06, with `-DwarningAsError=true`. Compile records and logs are under `checks/family_audit/compile.json` and `checks/family_audit/`. `checks/family_audit/FamilyAuditSmoke.lean` contains the boundary API instances and eight `#print axioms` commands.

The replay command is `python3 checks/family_audit/run_audit.py /path/to/pinned/kit`; the exact fixture command is `python3 checks/family_audit/boundary_recompute.py`. Temporary proof objects are removed after replay.

An initial audit environment had an incomplete PaperX import directory. Linking the predecessor proof objects into that isolated namespace root resolved the lookup failure. No production proof was edited for this issue. The initial smoke probe also required a missing import and an unused-variable correction; its final version compiles. These were audit harness issues, not failures of the nine production modules.

There is no remaining mathematical gap in the normalized Block 19 claim identified by this review. The strongest safe result is simultaneous lifting and labeled rigidity inside a supplied finite-group carrier, with actual image decompositions. It supplies no finite-group carrier from arbitrary finite-level data, no natural or unique family representative, and no arithmetic compatibility beyond its stated equations. The next release gate is the independent cumulative build, complete axiom/control audit, and packaged archive replay against these exact source hashes.
