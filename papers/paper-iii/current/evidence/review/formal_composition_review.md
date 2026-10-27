# Paper III: independent formal composition audit

## Normalized claim and primary verdict

**Primary verdict: proved as written**, for the three mathematical statements in the exact `PacketJetComposition.lean` revision below. The source has the manuscript's actual range-jet meaning and preserves the complete derivative-order, input-slot, and intermediate-label scope. No mathematical repair is needed.

For finite complete, pairwise annihilating idempotent systems on normed spaces over one nontrivially normed field, assume the intermediate and output projectors are continuous. Let `f : X -> Y` be `C^n` at `x`, and `g : Y -> Z` be `C^n` at `f(x)`. For every actual input-range tuple, the output range jet of the actual `n`th iterated derivative of `g o f` equals the finite sum over canonical ordered set partitions and all intermediate packet labels of the corresponding outer range jet evaluated on the corresponding inner range jets. This holds for every natural number `n`, including zero.

If every decorated partition has a zero outer jet or at least one zero inner jet, the composite jet is zero. Consequently, a nonzero composite jet admits a decorated partition for which the outer jet and all inner jets are nonzero. No converse, noncancellation, or nonzero-composite-term assertion is made.

These are the exact finite-order composition and structural-pruning statements required by the corrected manuscript, expressed using mathlib's canonical ordered representation of partitions. The manuscript's real/complex Banach hypotheses specialize to the formal normed-space hypotheses. Its global or open-neighborhood `C^n` assumptions imply the formal `ContDiffAt` assumptions.

## Exact revision, provenance, and acceptance boundary

- **Date:** 20 October 2026.
- **Reviewer:** the `analytic_audit` agent, separately delegated after the first analytic review. The reviewer did not write or edit the formal module.
- **Reviewed source:** `/workspace/scratch/9014da510e4f/paper3_release/formal/KomorebiPaperIII/PacketJetComposition.lean`.
- **Source SHA-256:** `06e1d95456304561dd967bb924d23ff45b1c2fe8b710fc472a9d002fde7f0b3e`.
- **Underlying continuous-jet source:** `formal/KomorebiPaperIII/ContinuousPacketJets.lean`, SHA-256 `63f96e83190b694b27b00a9649fc87cac9a3b0a6d65830c2a2b5249e76cad924`, unchanged from the prior actual-range correspondence review.
- **Pinned mathlib revision:** `aeb72f1e9981b6d35b426b16dca7759be3e7ba06`.
- **Compiler provenance:** the runtime auditor reported that all three statements at this exact composition-module hash compiled before freezing the candidate. This reviewer did not invoke the compiler. At assignment time the module was outside the accepted import closure; its inclusion in the final cold closure, declaration census, and kernel replay is a separate release-integration step.

This is a new, separate audit record. It leaves `analytic_review.md` and all earlier reviewed hashes intact. The earlier report's statement that `ContinuousPacketJets.lean` does not itself establish composition remains true. The present additional module supplies that previously missing packet-composition and pruning bridge. No Taylor module was added: the release editor and runtime auditor explicitly froze the formal scope after this composition module.

The proof-audit skill's raw-object, typing, hypothesis, nullary, ordering, dependency, and support obligations were applied. The exact primary dependencies were available locally and were read directly. Clean-file comparison against the pinned mathlib commit succeeded. No prior claim of compilation or correctness was used as a substitute for reading the definitions and reconstructing the mathematical implication.

## Manuscript-to-formal dictionary

The formal file uses `f` for the inner map and `g` for the outer map. This reverses the letters used in the manuscript but not the composition order.

| Manuscript object | Formal object | Exact meaning |
|---|---|---|
| Inner map `G : X -> Y` | `f : X -> Y` | The map differentiated within each partition block |
| Outer map `F : Y -> Z` | `g : Y -> Z` | The map differentiated once per partition block |
| Input family `P` | `P : System K X I` | Actual input projectors |
| Intermediate family `Q` | `M : System K Y J` | Actual projectors resolving the identity on `Y` |
| Output family `R` | `Q : System K Z L` | Actual projectors on `Z` |
| Output label `delta` | `gamma : L` | The selected actual output range |
| Ordered input labels | `alpha : Fin n -> I` | One retained label for every original direction slot |
| Set partition `pi` | `c : OrderedFinpartition n` | Nonempty disjoint covering blocks, each increasingly parameterized and canonically ordered by greatest element |
| Block count | `c.length` | The order of the outer derivative |
| Block size | `c.partSize a` | The order of the inner derivative for block `a` |
| Inclusion of a block into the original slots | `c.emb a` | Increasing embedding of that block's local indices into `Fin n` |
| Intermediate decoration | `beta : Fin c.length -> J` | All independent choices of one intermediate label per block |

The input tuple has the dependent type

`xs : (k : Fin n) -> LinearMap.range (P.projector (alpha k))`.

For block `a`, its label tuple is `alpha o c.emb a` and its direction tuple is `xs o c.emb a`. The inner jet has output type `LinearMap.range (M.projector (beta a))`. This is exactly the corresponding input type of the outer jet with label tuple `beta`. The outer output belongs to `LinearMap.range (Q.projector gamma)`, and its coercion to `Z` is the displayed summand. No ambient surrogate, quotient range, arbitrary equivalence, diagonal-only restriction, or substituted derivative is used.

## Dependency graph and obligation matrix

The three formal implications form an acyclic chain:

1. The existing actual-range `iteratedPacketJet` definition and its coercion identity expose the selected output projection of the actual iterated derivative.
2. Pinned mathlib's `iteratedFDeriv_comp` gives the complete derivative partition formula under the exact local `C^n` assumptions.
3. Pinned `FormalMultilinearSeries.taylorComp` unfolds to the sum over all `OrderedFinpartition n` objects. Its composition evaluation uses all slots via `c.emb`.
4. The previously checked `multilinear_input_expansion M` inserts the finite intermediate identity into each outer derivative slot. This yields every `beta` assignment, and output linearity distributes the selected projector through the sum.
5. Continuous-multilinear-map extensionality and the zero-coordinate property prove the sufficient vanishing condition.
6. Classical negation of that condition proves existence of an admissible witness for every nonzero composite jet.

| Obligation | Finding | Status |
|---|---|---|
| Correct derivative | Direct `iteratedFDeriv` specialization; no placeholder multilinear map is assumed to be a derivative | Passed |
| Correct range objects and norms | Same actual submodule ranges and inherited norms audited in `ContinuousPacketJets.lean` | Passed |
| Smoothness order | `hf : ContDiffAt K n f x`, `hg : ContDiffAt K n g (f x)`; `le_rfl` applies the order-`n` source theorem without an extra derivative | Passed |
| Scalar and space hypotheses | One nontrivially normed field; all spaces normed over it. Real/complex Banach spaces are included; finite dimension and Hilbert orthogonality are absent | Passed |
| Input continuity hypothesis | `hP` is not required because actual subspace inclusions are continuous. Intermediate/output continuity is supplied exactly where their continuous jets are formed | Passed |
| Partition coverage | Blocks are nonempty, disjoint and covering, with strictly increasing embeddings and canonical block order | Passed |
| Mixed and repeated labels | `alpha` is unrestricted and every `beta` is summed; mixed slots and repeated intermediate labels are retained | Passed |
| Coefficients | One term per canonical set partition and decoration; no extra permutation factorial or normalized Taylor coefficient is inserted | Passed |
| Nullary boundary | Unique empty partition, unique empty label function, no inner arguments; yields the actual output packet of `g(f(x))` | Passed |
| Empty intermediate label type | For positive order there are no decorations and the intermediate space is forced to zero; at order zero the empty label function still exists | Passed |
| Vanishing criterion | Equality to zero is equality of restricted multilinear maps, not vanishing at one sampled tuple | Passed |
| Support consequence | Nonzero composite implies existence of nonzero constituent jets; no converse or noncancellation conclusion | Passed |
| Manuscript block-order convention | Canonical greatest-element order is a legitimate enumeration of the manuscript set partitions; in the real/complex case symmetry allows its least-element convention | Passed for mathematical correspondence |
| Stirling/Touchard count | The module has no theorem identifying the cardinality with `sum S(n,k) M^k` | Not addressed by this module |
| Packet Taylor remainder | No packet integral/remainder bridge is defined here | Out of scope |

## Reconstruction of the critical proof

Let `v_k` be the ambient coercion of `xs k`. Unfolding the left side of `iteratedPacketJet_comp` gives

`Q_gamma [D^n(g o f)(x)(v_0,...,v_(n-1))]`.

The pinned derivative-composition theorem rewrites the full derivative as a sum of terms

`D^k g(f(x))[D^(|B_0|) f(x)[v_i : i in B_0], ..., D^(|B_(k-1)|) f(x)[v_i : i in B_(k-1)]]`.

For each fixed partition, apply `multilinear_input_expansion M` to this outer continuous multilinear map after forgetting continuity. Because `sum_j M_j = id_Y`, its `a`th argument becomes the sum over all `M_(beta a)` projections. Multilinearity creates the full finite sum over `beta : Fin k -> J`. Applying the linear output projector distributes over that sum. By the literal coercion formulas, each projected inner argument is exactly the corresponding inner range jet, and the projected outer derivative restricted to those range arguments is exactly the outer range jet. This is the module's stated formula.

The source use of `FormalMultilinearSeries.taylorComp` is correct: this particular operation is designed to compose **unnormalized iterated derivatives**. It is not the differently normalized analytic power-series composition operation. Consequently no factorial is missing from the partition formula. The summation itself supplies the usual multiplicities when directions or labels repeat.

The equality is displayed after coercion to `Z`, for every actual range tuple. This is exactly the evaluation form of the manuscript theorem. The following vanishing theorem uses extensionality and injectivity of the subtype coercion to turn those evaluation equalities into equality of the actual range-valued continuous multilinear maps.

## Adversarial boundary checks

### Order zero

The pinned source provides `Unique (OrderedFinpartition 0)`. Its unique element is the empty partition and has length zero. Even if `J` is empty, there is exactly one function `Fin 0 -> J`. Thus the right-hand side has exactly one term: the nullary output range jet of `g` at `f(x)`. By the actual definition of `iteratedFDeriv`, its zero-order evaluation is `g(f(x))`. The left side is the same output projection of the zero-order composite value.

In the vanishing theorem, an existential inner zero-jet witness would require an element of `Fin 0`, so that branch cannot arise at order zero. The condition reduces to the outer nullary jet being zero. The support theorem reduces to the same outer nullary jet being nonzero, with the inner nonzero condition vacuous. These are correct. The `C^0` hypotheses are stronger than needed for this value identity, but do not exclude any of the positive-order manuscript claims or invalidate the stated zero-order extension.

### Orders one and two

There is one order-one partition. The formula is the first-order chain rule with a single intermediate resolution:

`Q_gamma Dg(f(x))[sum_j M_j Df(x)[v]]`.

At order two, the two partitions give exactly the outer second derivative applied to two projected first derivatives, and the outer first derivative applied to a projected second derivative. All pairs of intermediate labels appear in the first shape and every individual label appears in the second. The output projector is on `Z` throughout.

### Block order and general scalar field

The source structure explicitly sorts blocks by increasing greatest element, and each block's embedding is increasing. The file never silently permutes derivative slots over a general nontrivially normed field. This is necessary because arbitrary-field iterated derivatives need not satisfy the real/complex symmetry theorem.

For the manuscript's real/complex Banach setting, higher Fréchet derivatives are symmetric, as checked in the previous analytic review. Therefore the canonical greatest-element ordering and the manuscript's increasing least-element ordering give the same value when the labels and corresponding inner arguments are permuted together. The module does not add a separate named theorem expressing invariance under every arbitrary ordering, nor a separate bijection/cardinality theorem for Stirling numbers. These are representation distinctions, not omitted terms in its composition identity.

### Zero spaces, empty families, and zero packets

For positive `n`, every `OrderedFinpartition n` has positive length. If `J` is empty, there is no `beta` at all and the decorated sum is zero. Completeness forces `Y` to be the zero space, so `g o f` is constant and its positive-order derivative is zero, in agreement with the theorem. If an actual input range is zero, positive-order multilinearity gives a zero jet. If the output range is zero, every result lies in the zero subspace. The support hypothesis is then impossible, as it should be. No nonzero-projector assumption was inserted.

## Vanishing and support: exact strength

The hypothesis of `iteratedPacketJet_comp_eq_zero_of` is quantified over **every** partition and **every** intermediate label function. For each decorated term it requires either a zero outer restricted jet or a selected inner restricted jet equal to zero as a map. A zero outer map gives a zero term directly. A zero inner map gives a zero argument in an actual outer slot; the proof calls `map_coord_zero` with the witness `a` for that slot. It does not misuse this property for a nullary map.

After summing, the composite evaluates to zero for every actual range tuple. Extensionality proves the composite jet is the zero map. The support theorem takes the contrapositive: if there were no partition/decorating function with every constituent nonzero, each decoration would satisfy the sufficient vanishing alternative. This would contradict the nonzero-composite hypothesis.

This conclusion is exactly the typed support inclusion in the revised manuscript. It does not say that all admissible profiles occur. It does not say that every set of nonzero constituents composes to a nonzero term. It does not exclude cancellation between different terms. The cancellation and zero-composite examples in the earlier report remain valid and do not contradict the new formal theorem.

## Exact primary-source checks

The source theorem and the definitions it unfolds were read at the pinned mathlib commit. No web discovery result was substituted for the exact local source text.

| Dependency | Exact revision and extracted implication |
|---|---|
| `Mathlib/Analysis/Calculus/ContDiff/Comp.lean` | SHA-256 `26495369d99d4815f99e8319623231a5fe25f0fdd1756c31162216323e27ed0f`; `iteratedFDeriv_comp` at line 271 has `ContDiffAt` hypotheses for inner and outer maps, and an order bound `i <= n`. Setting `i=n` gives the exact required derivative identity. Its reduction to the within-set version was read. |
| `Mathlib/Analysis/Calculus/ContDiff/FaaDiBruno.lean` | SHA-256 `79b3216e965f032554197e51cb6d4dbcfb35e8a801b3dde1228f0eacbbb64aaf`; the `OrderedFinpartition` structure, covering/disjointness/increasing-order fields, `Fintype` and unique-zero instances, block evaluation, `taylorComp`, and the principal composition construction were read. |
| `Mathlib/Analysis/Calculus/ContDiff/Defs.lean` | SHA-256 `b1bbfe431bab224de42a989f3f31d7480868b415dd80abf43bf318310c05ed02`; `ContDiffAt` is the local smoothness predicate used by the module. The prior audit also read the `ContDiff.ftaylorSeries` bridge. |
| `KomorebiPaperIII/MultilinearPacketJets.lean` | `multilinear_input_expansion` was rechecked against the actual complete system and raw multilinear map. Its finite input-label sum is the precise extra packet step beyond the standard derivative formula. |
| `KomorebiPaperIII/ContinuousPacketJets.lean` | The previously reviewed source hash is unchanged. Its actual range input/output types and definitional coercion formula are the objects instantiated here. |

The pinned library sources prove a stronger canonical-order formula than needed for the real/complex manuscript case. Application is **verified**. No new external analytic theorem is assumed by the support consequences: they are finite multilinear and logical consequences of the displayed composition formula.

## Checks performed and remaining release implications

Representative checks were:

```sh
sha256sum formal/KomorebiPaperIII/PacketJetComposition.lean
sha256sum formal/KomorebiPaperIII/ContinuousPacketJets.lean
sed -n '240,292p' formal/.lake/packages/mathlib/Mathlib/Analysis/Calculus/ContDiff/Comp.lean
sed -n '93,232p' formal/.lake/packages/mathlib/Mathlib/Analysis/Calculus/ContDiff/FaaDiBruno.lean
sed -n '868,909p' formal/.lake/packages/mathlib/Mathlib/Analysis/Calculus/ContDiff/FaaDiBruno.lean
git -C formal/.lake/packages/mathlib diff --exit-code HEAD -- Mathlib/Analysis/Calculus/ContDiff/Comp.lean Mathlib/Analysis/Calculus/ContDiff/FaaDiBruno.lean Mathlib/Analysis/Calculus/ContDiff/Defs.lean
```

A direct source search found no `sorry`, `admit`, introduced `axiom`, `unsafe`, `partial`, or foreign implementation declaration in the new module. This is a source check; the full transitive axiom census remains the runtime auditor's separate task. No finite example or computation is being used to infer the universal formula.

**Remaining mathematical gap in the three exact reviewed statements: none found.** The exact source hash and the pass were sent to both the release editor and runtime auditor before this report was written. A Taylor module was not reviewed or accepted because none was added under the final scope freeze.

Once the new module is admitted to the successfully replayed import closure, release records may describe the actual finite-order packet composition identity and structural support consequence as formally checked under their explicit hypotheses. They should retain separate status for the packet Taylor integral/remainder theorem and the Stirling/Touchard term count. The earlier report is historical evidence for its own exact revisions and should not be silently rewritten to imply it covered this later module.
