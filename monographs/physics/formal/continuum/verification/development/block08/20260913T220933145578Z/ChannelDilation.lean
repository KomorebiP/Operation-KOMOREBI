module

public import KomorebiPhysics.ParsevalChannels

/-! Chapter 5.4 (5.28)--(5.31): actual finite Hilbert-sum coordinate projections,
compression, and the isometric range. Neither compression nor projector laws are inputs. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
open scoped BigOperators
open ContinuousLinearMap

namespace ChannelDilation
variable {I : Type*} (K : I → Type*) [Fintype I] [DecidableEq I]
  [∀ i, NormedAddCommGroup (K i)] [∀ i, InnerProductSpace ℂ (K i)]

/-- Insert one channel into the genuine L2 direct sum. -/
def inclusion (i : I) : K i →L[ℂ] PiLp 2 K :=
  (PiLp.continuousLinearEquiv 2 ℂ K).symm.toContinuousLinearMap.comp
    (ContinuousLinearMap.single ℂ K i)

omit [Fintype I] in
theorem inclusion_apply (i : I) (y : K i) : inclusion K i y = PiLp.single 2 i y := rfl

/-- The coordinate projector, defined using actual insertion and evaluation maps. -/
def coordinate (i : I) : PiLp 2 K →L[ℂ] PiLp 2 K :=
  (inclusion K i).comp (PiLp.proj 2 K i)

omit [Fintype I] in
theorem coordinate_apply (i : I) (y : PiLp 2 K) :
    coordinate K i y = PiLp.single 2 i (y i) := rfl

theorem inclusion_inner (i : I) (x : K i) (y : PiLp 2 K) :
    inner ℂ (inclusion K i x) y = inner ℂ x (y i) := by
  simp only [inclusion_apply, PiLp.inner_apply]
  rw [Fintype.sum_eq_single i]
  · simp only [PiLp.single_eq_same]
  · intro j hj
    simp [PiLp.single_eq_of_ne 2 hj]

theorem inner_inclusion (i : I) (x : PiLp 2 K) (y : K i) :
    inner ℂ x (inclusion K i y) = inner ℂ (x i) y := by
  simp only [inclusion_apply, PiLp.inner_apply]
  rw [Fintype.sum_eq_single i]
  · simp only [PiLp.single_eq_same]
  · intro j hj
    simp [PiLp.single_eq_of_ne 2 hj]

theorem coordinate_selfAdjoint (i : I) (x y : PiLp 2 K) :
    inner ℂ (coordinate K i x) y = inner ℂ x (coordinate K i y) := by
  change inner ℂ (inclusion K i (x i)) y = inner ℂ x (inclusion K i (y i))
  rw [inclusion_inner, inner_inclusion]

omit [Fintype I] in
theorem coordinate_idempotent (i : I) : coordinate K i * coordinate K i = coordinate K i := by
  ext x j
  simp only [mul_apply_eq_comp, coordinate_apply, PiLp.single_eq_same]

omit [Fintype I] in
theorem coordinate_orthogonal (i j : I) (hij : i ≠ j) :
    coordinate K i * coordinate K j = 0 := by
  apply ContinuousLinearMap.ext
  intro x
  change coordinate K i (coordinate K j x) = 0
  rw [coordinate_apply, coordinate_apply, PiLp.single_eq_of_ne 2 hij]
  change inclusion K i 0 = 0
  exact map_zero _

theorem coordinate_sum : (∑ i, coordinate K i) = 1 := by
  ext x j
  simp only [sum_apply, one_apply_eq_self]
  change (PiLp.proj 2 K j) (∑ i, coordinate K i x) = x j
  rw [map_sum]
  simp only [PiLp.proj_apply, coordinate_apply]
  rw [Fintype.sum_eq_single j]
  · exact PiLp.single_eq_same _ _ _
  · intro i hi
    exact PiLp.single_eq_of_ne' 2 hi _

/-- A constructed orthogonal atlas on the enlarged space. -/
def coordinateAtlas : Atlas (PiLp 2 K) I where
  proj := coordinate K
  mul_proj i j := by
    by_cases h : i = j
    · subst j
      simpa using coordinate_idempotent K i
    · simpa [h] using coordinate_orthogonal K i j h
  sum_proj := coordinate_sum K
  selfAdjoint := coordinate_selfAdjoint K

/-- Channel insertion has adjoint equal to actual coordinate evaluation. -/
theorem adjoint_inclusion [∀ i, CompleteSpace (K i)] (i : I) :
    (inclusion K i).adjoint = PiLp.proj 2 K i := by
  symm
  apply (eq_adjoint_iff _ _).mpr
  intro x y
  exact (inner_inclusion K i x y).symm

end ChannelDilation

namespace ParsevalFamily
variable {H I : Type*} {K : I → Type*}
  [NormedAddCommGroup H] [InnerProductSpace ℂ H] [CompleteSpace H]
  [Fintype I] [DecidableEq I]
  [∀ i, NormedAddCommGroup (K i)] [∀ i, InnerProductSpace ℂ (K i)]
  [∀ i, CompleteSpace (K i)]
variable (V : ParsevalFamily H I K)

theorem synthesis_single (i : I) (y : K i) :
    V.synthesis (PiLp.single 2 i y) = (V.channel i).adjoint y := by
  rw [V.synthesis_apply]
  rw [Fintype.sum_eq_single i]
  · simp only [PiLp.single_eq_same]
  · intro j hj
    simp [PiLp.single_eq_of_ne 2 hj]

/-- Literal compression (5.31), derived for the maps built above. -/
theorem effect_compression (i : I) :
    V.analysis.adjoint.comp ((ChannelDilation.coordinate K i).comp V.analysis) =
      V.effectAtlas.effect i := by
  rw [V.adjoint_analysis]
  ext x
  simp only [comp_apply, ChannelDilation.coordinate_apply,
    V.analysis_apply, V.synthesis_single]
  rfl

theorem compressed_probability (x : H) (i : I) :
    (ChannelDilation.coordinateAtlas K).energy (V.analysis x) i =
      V.effectAtlas.probability x i := by
  change ‖ChannelDilation.coordinate K i (V.analysis x)‖ ^ 2 = _
  rw [ChannelDilation.coordinate_apply, PiLp.norm_single, V.analysis_apply,
    V.probability_eq_norm_sq]

/-- Cross-channel blocks are the actual blocks of the lifted operator. -/
def liftOperator (X : H →L[ℂ] H) : PiLp 2 K →L[ℂ] PiLp 2 K :=
  V.analysis.comp (X.comp V.synthesis)

/-- The range projector need not be the identity of the larger space. -/
def rangeProjection : PiLp 2 K →L[ℂ] PiLp 2 K := V.analysis.comp V.synthesis

omit [DecidableEq I] in
theorem rangeProjection_idempotent : V.rangeProjection * V.rangeProjection = V.rangeProjection := by
  apply ContinuousLinearMap.ext
  intro y
  change V.analysis (V.synthesis (V.analysis (V.synthesis y))) = V.analysis (V.synthesis y)
  have h := congrArg (fun T : H →L[ℂ] H => T (V.synthesis y)) V.synthesis_analysis
  exact congrArg V.analysis h

omit [DecidableEq I] in
theorem rangeProjection_adjoint : V.rangeProjection.adjoint = V.rangeProjection := by
  simp only [rangeProjection, adjoint_comp, V.adjoint_synthesis, V.adjoint_analysis]

omit [DecidableEq I] in
theorem rangeProjection_fix_analysis (x : H) : V.rangeProjection (V.analysis x) = V.analysis x := by
  change V.analysis (V.synthesis (V.analysis x)) = _
  exact congrArg V.analysis (congrArg (fun T : H →L[ℂ] H => T x) V.synthesis_analysis)

omit [DecidableEq I] in
/-- Exact range characterization, avoiding an unjustified surjectivity claim. -/
theorem rangeProjection_fixed_iff (y : PiLp 2 K) :
    V.rangeProjection y = y ↔ ∃ x, V.analysis x = y := by
  constructor
  · intro h
    exact ⟨V.synthesis y, h⟩
  · rintro ⟨x, rfl⟩
    exact V.rangeProjection_fix_analysis x

omit [DecidableEq I] in
theorem synthesis_residual_zero (y : PiLp 2 K) :
    V.synthesis (y - V.rangeProjection y) = 0 := by
  rw [map_sub]
  have h := congrArg (fun T : H →L[ℂ] H => T (V.synthesis y)) V.synthesis_analysis
  change V.synthesis y - V.synthesis (V.analysis (V.synthesis y)) = 0
  change V.synthesis (V.analysis (V.synthesis y)) = V.synthesis y at h
  rw [h, sub_self]

omit [DecidableEq I] in
/-- The range error is orthogonal to every analyzed state. -/
theorem residual_orthogonal (x : H) (y : PiLp 2 K) :
    inner ℂ (V.analysis x) (y - V.rangeProjection y) = 0 := by
  rw [← adjoint_inner_right, V.adjoint_analysis, V.synthesis_residual_zero, inner_zero_right]

omit [DecidableEq I] in
theorem liftOperator_recover (X : H →L[ℂ] H) :
    V.synthesis.comp ((V.liftOperator X).comp V.analysis) = X := by
  ext x
  have he (z : H) : V.synthesis (V.analysis z) = z :=
    congrArg (fun T : H →L[ℂ] H => T z) V.synthesis_analysis
  simp only [comp_apply, liftOperator, he]

omit [DecidableEq I] in
theorem liftOperator_injective : Function.Injective V.liftOperator := by
  intro X Y h
  have h' := congrArg (fun T => V.synthesis.comp (T.comp V.analysis)) h
  simpa only [V.liftOperator_recover] using h'

omit [DecidableEq I] in
theorem liftOperator_mul (X Y : H →L[ℂ] H) :
    V.liftOperator (X * Y) = V.liftOperator X * V.liftOperator Y := by
  ext z
  have he (x : H) : V.synthesis (V.analysis x) = x :=
    congrArg (fun T : H →L[ℂ] H => T x) V.synthesis_analysis
  simp only [liftOperator, comp_apply, mul_apply_eq_comp, he]

omit [DecidableEq I] in
theorem liftOperator_one : V.liftOperator 1 = V.rangeProjection := by
  ext y
  rfl

omit [DecidableEq I] in
theorem liftOperator_adjoint (X : H →L[ℂ] H) :
    (V.liftOperator X).adjoint = V.liftOperator X.adjoint := by
  simp only [liftOperator, adjoint_comp, V.adjoint_analysis, V.adjoint_synthesis, comp_assoc]

theorem lifted_block (X : H →L[ℂ] H) (i j : I) :
    (PiLp.proj 2 K i).comp ((V.liftOperator X).comp (ChannelDilation.inclusion K j)) =
      V.channelBlock X i j := by
  ext y
  simp only [comp_apply, liftOperator, PiLp.proj_apply, V.analysis_apply,
    ChannelDilation.inclusion_apply, V.synthesis_single, channelBlock_apply]

end ParsevalFamily
end KomorebiPhysics
