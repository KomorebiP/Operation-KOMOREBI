# Formal scope review — expanded publication 1.3.0

The canonical Lean sources and formal metadata are unchanged from the accepted 1.2.0 baseline. No new Lean compilation or declaration-axiom query was run for this edition. Source names and hashes are resolved against the retained accepted environment inventory. This is an editorial correspondence, not an automatic translation proof.

## New exposition using existing verified declarations

| Item | Editorial scope retained |
|---|---|
| KS59 | Additive view systems and nested prescribed domains. The forgetful quotient maps are surjective, not generally injective. Both quotient naturality and persistence refer to the actual extension class. |
| KS60 | The concrete three-view integer model retains its original restriction maps. The initial extension fiber is parametrized by integers, while a prescribed middle value extends precisely when even. |
| KS61 | Set-valued sequential resolutions, monotone schedules, and finite-stage eventual equality. The realized action respects the quotient and composition. This is not an identification with every general pro-category. |
| KS62 | Faithfulness assumes surjectivity of every source projection from the limit. Surjective bonding maps give a sufficient condition. Without it equality on global points can conceal a finite-stage difference. |
| KS63 | Every source limit projection is surjective. For each target coordinate one finite source stage must work uniformly for all source points. The theorem does not assert that arbitrary functions have finite observation. |
| KS64 | Increasing cofinal schedules give explicit isomorphisms in the eventual transport category and Hom equivalences. This does not assert equality of quantitative residual norms. |
| KS65 | Continuous linear right inverses of a fixed defect operator determine exact/residual coordinates. Projectors with this common kernel image commute exactly when equal, and equality reflects equality of the right inverses. |
| KS66 | The square of defect operators commutes exactly. The mismatch depends on chosen bounded right inverses. Its composition law uses the declared residual map in the second term. Norm convergence requires the supplied bounded maps and vanishing residuals. |
| KS67 | Actual operator-valued tower residuals with contractive bonding maps. A uniform bound on sampling gaps is required for the stated residual operator and repair norm estimates, but not for qualitative preservation of exactness. |
| KS68 | The two-copy equivalent-view model compares actual fully framed gauge groupoids. Failure concerns freezing every representative, not the invariant identified-boundary realization construction. |
| KS69 | A supplied residual bound for the reference operator. Measurement error and operator error have separate terms. Proximity is to the reference exact space, not automatically to the changed kernel. |
| KS70 | The changed operator annihilates the old kernel and the product of reference gain and perturbation radius is strictly less than one. Kernel equality and the new bound are derived, not assumed from norm closeness alone. |

## Worked cases and proof review

The finite-observation converse derives finite-stage naturality using surjectivity of source point projections; it does not assume the missing naturality as part of the input. Eventual equality is required on every point of the witnessing finite fiber, not only on globally extendable states. The empty-limit example keeps this distinction visible.

The repair chart assumes actual continuous linear right inverses. The section mismatch is exact-valued and obeys the typed composition law. Resampling requires bounded gaps for the quantitative operator estimate, while qualitative exactness preservation does not. The unbounded-gap counterexample concerns arbitrary bounded residual data and does not claim a bounded primitive exists.

The full-framing example is not conflated with the marked boundary fiber. Noncommutative multiplication order is retained in the explicit comparison formula and checked independently on S3.

The signal cycle changes inconsistent edge data before selecting a primitive. The anchor and the mean-zero convention select different members of the same affine solution family. The reflection cycle separately declares its Euclidean vertex and one-orientation residual norms; the optimal gain and squared errors are derived by actual matrices. No maximum-norm theorem is silently reassigned those constants.

The scalar endpoint gain plot is defined only before rank change. At the endpoint the exact space enlarges; the limiting divergence is not described as an infinite least gain for the zero operator. Reference-model and changed-model proximity are different conclusions.

## Inherited completed formalization

KS54–KS58 remain implemented in the five version-1.2.0 additions. Their detailed hypothesis review is preserved in `history/v1.2.0/FORMAL_SCOPE_REVIEW.md` and the Lean companion. The accepted principal type export covers the former 139 references; it was not silently relabeled as a fresh export of all 180 current references. Newly cited declarations were inspected in their actual source modules and resolved against the retained axiom inventory.

## No enlarged universal claim

All 70 principal exposition entries have source correspondences. This does not imply that every numerical worked instance, sentence, exercise, or algorithm implementation has a separately compiled Lean theorem. The finite suites are implementation evidence. General results retain their typed hypotheses and standard trust boundary. Universal-view, infinity-stack, arbitrary semantic-realization, nonlinear-repair, and unrestricted arithmetic/physical generalizations are not asserted.
