import PaperIRelease.TopologyTransport
import Mathlib.Topology.Algebra.GroupCompletion
import Mathlib.Topology.Algebra.Module.LocallyConvex

/-!
# Dense presentations with the transported locally convex topology

The uniformity is explicitly pulled back along the presentation map.
The comparison map is constructed by the universal property of completion.
Its inverse, linearity, uniqueness, and intertwining are proved here.
-/

noncomputable section
open Set Function UniformSpace Topology

namespace PaperIRelease.TopologyDenseCompletion

section Transport

variable {𝕜 E X : Type*} [Ring 𝕜]
variable [AddCommGroup E] [Module 𝕜 E]
variable [AddCommGroup X] [Module 𝕜 X] [UniformSpace X]

/-- The uniformity transported from the image of the linear presentation. -/
@[instance_reducible]
def transportedUniformity (j : E →ₗ[𝕜] X) : UniformSpace E :=
  UniformSpace.comap j inferInstance

/-- Its topology is exactly the subspace topology pulled back along `j`. -/
theorem transported_isUniformInducing (j : E →ₗ[𝕜] X) :
    let : UniformSpace E := transportedUniformity j
    IsUniformInducing j := by
  let : UniformSpace E := transportedUniformity j
  exact ⟨rfl⟩

/-- Pulling back the linear topology preserves local convexity. -/
theorem transported_locallyConvex [PartialOrder 𝕜] [IsOrderedRing 𝕜]
    [LocallyConvexSpace 𝕜 X] (j : E →ₗ[𝕜] X) :
    let : UniformSpace E := transportedUniformity j
    LocallyConvexSpace 𝕜 E := by
  let : UniformSpace E := transportedUniformity j
  exact (transported_isUniformInducing j).isInducing.locallyConvexSpace

/-- The transported additive uniformity is compatible with the group law. -/
theorem transported_uniformAddGroup [IsUniformAddGroup X] (j : E →ₗ[𝕜] X) :
    let : UniformSpace E := transportedUniformity j
    IsUniformAddGroup E := by
  let : UniformSpace E := transportedUniformity j
  exact (transported_isUniformInducing j).isUniformAddGroup j

/-- Scalar multiplication is uniformly continuous in the transported topology. -/
theorem transported_uniformConstSMul [UniformContinuousConstSMul 𝕜 X]
    (j : E →ₗ[𝕜] X) :
    let : UniformSpace E := transportedUniformity j
    UniformContinuousConstSMul 𝕜 E := by
  let : UniformSpace E := transportedUniformity j
  exact (transported_isUniformInducing j).uniformContinuousConstSMul (map_smul j)

end Transport

section Completion

variable {𝕜 E X : Type*} [Ring 𝕜]
variable [AddCommGroup E] [Module 𝕜 E] [UniformSpace E]
variable [IsUniformAddGroup E] [UniformContinuousConstSMul 𝕜 E]
variable [AddCommGroup X] [Module 𝕜 X] [UniformSpace X]
variable [IsUniformAddGroup X] [UniformContinuousConstSMul 𝕜 X]
variable [CompleteSpace X] [T0Space X]

/-- The complete target with its dense presentation map is an abstract
completion, because the domain carries the transported uniformity. -/
def presentationCompletion (j : E →ₗ[𝕜] X)
    (hj : IsUniformInducing j) (hd : DenseRange j) : AbstractCompletion E where
  space := X
  coe := j
  uniformStruct := inferInstance
  complete := inferInstance
  separation := inferInstance
  isUniformInducing := hj
  dense := hd

/-- The canonical uniform isomorphism extending the dense presentation. -/
def completionUniformEquiv (j : E →ₗ[𝕜] X)
    (hj : IsUniformInducing j) (hd : DenseRange j) : Completion E ≃ᵤ X :=
  Completion.cPkg.compareEquiv (presentationCompletion j hj hd)

omit [IsUniformAddGroup E] [UniformContinuousConstSMul 𝕜 E]
  [IsUniformAddGroup X] [UniformContinuousConstSMul 𝕜 X] in
@[simp]
theorem completionUniformEquiv_apply_coe (j : E →ₗ[𝕜] X)
    (hj : IsUniformInducing j) (hd : DenseRange j) (x : E) :
    completionUniformEquiv j hj hd (x : Completion E) = j x :=
  Completion.cPkg.compare_coe (presentationCompletion j hj hd) x

/-- The completed presentation is a topological linear isomorphism. -/
def completionLinearEquiv (j : E →ₗ[𝕜] X)
    (hj : IsUniformInducing j) (hd : DenseRange j) : Completion E ≃L[𝕜] X where
  toEquiv := (completionUniformEquiv j hj hd).toEquiv
  map_add' x y := by
    induction x, y using Completion.induction_on₂ with
    | hp =>
      exact isClosed_eq
        ((completionUniformEquiv j hj hd).continuous.comp (continuous_fst.add continuous_snd))
        (((completionUniformEquiv j hj hd).continuous.comp continuous_fst).add
          ((completionUniformEquiv j hj hd).continuous.comp continuous_snd))
    | ih x y => simp only [← Completion.coe_add, Equiv.toFun_as_coe,
        UniformEquiv.coe_toEquiv, completionUniformEquiv_apply_coe, map_add]
  map_smul' c x := by
    induction x using Completion.induction_on with
    | hp =>
      exact isClosed_eq
        ((completionUniformEquiv j hj hd).continuous.comp (continuous_const_smul c))
        ((completionUniformEquiv j hj hd).continuous.const_smul c)
    | ih x => simp only [← Completion.coe_smul, Equiv.toFun_as_coe,
        UniformEquiv.coe_toEquiv, completionUniformEquiv_apply_coe, map_smul,
        RingHom.id_apply]
  continuous_toFun := (completionUniformEquiv j hj hd).continuous
  continuous_invFun := (completionUniformEquiv j hj hd).symm.continuous

@[simp]
theorem completionLinearEquiv_apply_coe (j : E →ₗ[𝕜] X)
    (hj : IsUniformInducing j) (hd : DenseRange j) (x : E) :
    completionLinearEquiv j hj hd (x : Completion E) = j x :=
  completionUniformEquiv_apply_coe j hj hd x

/-- The canonical extension is the unique continuous extension. -/
theorem completionLinearEquiv_unique (j : E →ₗ[𝕜] X)
    (hj : IsUniformInducing j) (hd : DenseRange j)
    (g : Completion E → X) (hg : Continuous g)
    (hext : ∀ x : E, g (x : Completion E) = j x) :
    g = completionLinearEquiv j hj hd := by
  apply Completion.denseRange_coe.equalizer hg
    (completionLinearEquiv j hj hd).continuous
  funext x
  exact (hext x).trans (completionLinearEquiv_apply_coe j hj hd x).symm

omit [IsUniformAddGroup E] [UniformContinuousConstSMul 𝕜 E]
  [UniformContinuousConstSMul 𝕜 X] [CompleteSpace X] [T0Space X] in
/-- Intertwining with a continuous target operator makes the algebraic
operator on the presentation uniformly continuous in the induced topology. -/
theorem presentation_action_uniformContinuous (j : E →ₗ[𝕜] X)
    (hj : IsUniformInducing j) (T : E →ₗ[𝕜] E) (B : X →L[𝕜] X)
    (hintertwine : ∀ x, j (T x) = B (j x)) : UniformContinuous T := by
  apply hj.uniformContinuous_iff.mpr
  have h : (j : E → X) ∘ T = B ∘ j := funext hintertwine
  rw [h]
  exact B.uniformContinuous.comp hj.uniformContinuous

/-- The uniquely extended action operator, constructed by conjugation
through the canonical completion isomorphism. -/
def completedAction (j : E →ₗ[𝕜] X)
    (hj : IsUniformInducing j) (hd : DenseRange j) (B : X →L[𝕜] X) :
    Completion E →L[𝕜] Completion E :=
  (completionLinearEquiv j hj hd).symm.toContinuousLinearMap.comp
    (B.comp (completionLinearEquiv j hj hd).toContinuousLinearMap)

@[simp]
theorem completedAction_apply_coe (j : E →ₗ[𝕜] X)
    (hj : IsUniformInducing j) (hd : DenseRange j)
    (T : E →ₗ[𝕜] E) (B : X →L[𝕜] X)
    (hintertwine : ∀ x, j (T x) = B (j x)) (x : E) :
    completedAction j hj hd B (x : Completion E) = (T x : Completion E) := by
  apply (completionLinearEquiv j hj hd).injective
  simp [completedAction, ← hintertwine]

/-- The completion isomorphism intertwines the entire extended action. -/
theorem completion_intertwines (j : E →ₗ[𝕜] X)
    (hj : IsUniformInducing j) (hd : DenseRange j) (B : X →L[𝕜] X) :
    (completionLinearEquiv j hj hd).toContinuousLinearMap.comp
        (completedAction j hj hd B) =
      B.comp (completionLinearEquiv j hj hd).toContinuousLinearMap := by
  ext x
  simp [completedAction]

end Completion

section QuotientPresentation

variable {𝕜 F X : Type*} [Ring 𝕜]
variable [AddCommGroup F] [Module 𝕜 F]
variable [AddCommGroup X] [Module 𝕜 X] [UniformSpace X]
variable [IsUniformAddGroup X] [UniformContinuousConstSMul 𝕜 X]
variable [CompleteSpace X] [T0Space X]

/-- The actual injective map induced on the quotient of a presentation by
its relation module. No topology on the free module is presupposed. -/
def quotientEmbedding (f : F →ₗ[𝕜] X) : (F ⧸ f.ker) →ₗ[𝕜] X :=
  f.range.subtype.comp f.quotKerEquivRange.toLinearMap

omit [UniformSpace X] [IsUniformAddGroup X] [UniformContinuousConstSMul 𝕜 X]
  [CompleteSpace X] [T0Space X] in
@[simp]
theorem quotientEmbedding_apply_mk (f : F →ₗ[𝕜] X) (x : F) :
    quotientEmbedding f (f.ker.mkQ x) = f x :=
  f.quotKerEquivRange_apply_mk x

omit [UniformSpace X] [IsUniformAddGroup X] [UniformContinuousConstSMul 𝕜 X]
  [CompleteSpace X] [T0Space X] in
theorem quotientEmbedding_injective (f : F →ₗ[𝕜] X) :
    Injective (quotientEmbedding f) :=
  Subtype.val_injective.comp f.quotKerEquivRange.injective

omit [IsUniformAddGroup X] [UniformContinuousConstSMul 𝕜 X]
  [CompleteSpace X] [T0Space X] in
theorem quotientEmbedding_dense (f : F →ₗ[𝕜] X) (hd : DenseRange f) :
    DenseRange (quotientEmbedding f) := by
  apply hd.mono
  rintro x ⟨y, rfl⟩
  exact ⟨f.ker.mkQ y, quotientEmbedding_apply_mk f y⟩

/-- Completion of the quotient by the actual kernel of the presentation,
equipped with the topology transported from the target. This applies to
free seed evaluation and to the restriction of a quotient realization to
any subspace with dense image. -/
def completedQuotientEquiv (f : F →ₗ[𝕜] X) (hd : DenseRange f) :
    letI : UniformSpace (F ⧸ f.ker) := transportedUniformity (quotientEmbedding f)
    letI : IsUniformAddGroup (F ⧸ f.ker) :=
      transported_uniformAddGroup (quotientEmbedding f)
    letI : UniformContinuousConstSMul 𝕜 (F ⧸ f.ker) :=
      transported_uniformConstSMul (quotientEmbedding f)
    Completion (F ⧸ f.ker) ≃L[𝕜] X := by
  letI : UniformSpace (F ⧸ f.ker) := transportedUniformity (quotientEmbedding f)
  letI : IsUniformAddGroup (F ⧸ f.ker) :=
    transported_uniformAddGroup (quotientEmbedding f)
  letI : UniformContinuousConstSMul 𝕜 (F ⧸ f.ker) :=
    transported_uniformConstSMul (quotientEmbedding f)
  exact completionLinearEquiv (quotientEmbedding f)
    (transported_isUniformInducing (quotientEmbedding f)) (quotientEmbedding_dense f hd)

/-- The canonical completed quotient sends a represented class to its
original presentation value. -/
theorem completedQuotientEquiv_apply_mk (f : F →ₗ[𝕜] X) (hd : DenseRange f) (x : F) :
    letI : UniformSpace (F ⧸ f.ker) := transportedUniformity (quotientEmbedding f)
    letI : IsUniformAddGroup (F ⧸ f.ker) :=
      transported_uniformAddGroup (quotientEmbedding f)
    letI : UniformContinuousConstSMul 𝕜 (F ⧸ f.ker) :=
      transported_uniformConstSMul (quotientEmbedding f)
    completedQuotientEquiv f hd (f.ker.mkQ x : Completion (F ⧸ f.ker)) = f x := by
  let : UniformSpace (F ⧸ f.ker) := transportedUniformity (quotientEmbedding f)
  let : IsUniformAddGroup (F ⧸ f.ker) :=
    transported_uniformAddGroup (quotientEmbedding f)
  let : UniformContinuousConstSMul 𝕜 (F ⧸ f.ker) :=
    transported_uniformConstSMul (quotientEmbedding f)
  exact (completionLinearEquiv_apply_coe (quotientEmbedding f)
    (transported_isUniformInducing (quotientEmbedding f))
    (quotientEmbedding_dense f hd) (f.ker.mkQ x)).trans (quotientEmbedding_apply_mk f x)

end QuotientPresentation

end PaperIRelease.TopologyDenseCompletion
