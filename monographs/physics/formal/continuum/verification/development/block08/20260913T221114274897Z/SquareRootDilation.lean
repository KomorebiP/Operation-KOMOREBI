module

public import KomorebiPhysics.ChannelDilation
public import Mathlib.Analysis.InnerProductSpace.StarOrder
public import Mathlib.Analysis.SpecialFunctions.ContinuousFunctionalCalculus.Rpow.Basic

/-! Added finite-outcome universal construction. Each bounded positive effect
is factored using the actual positive square root from Mathlib's continuous
functional calculus. Completeness of the complex Hilbert space is explicit.
This is not a countable-outcome or unbounded-operator dilation theorem. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
open scoped BigOperators
open ContinuousLinearMap
namespace EffectAtlas
variable {H I : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
  [CompleteSpace H] [Fintype I] (F : EffectAtlas H I)

omit [CompleteSpace H] in
/-- Reconcile the atlas quadratic-form positivity with the operator Loewner order. -/
theorem operator_nonneg (i : I) : 0 ≤ F.effect i := by
  apply ContinuousLinearMap.nonneg_iff_isPositive.mpr
  refine ⟨F.selfAdjoint i, ?_⟩
  intro x
  change 0 ≤ (inner ℂ (F.effect i x) x).re
  rw [F.selfAdjoint]
  exact F.nonnegative i x

/-- Actual positive square-root channel, not an existentially assumed factor. -/
def sqrtChannel (i : I) : H →L[ℂ] H := CFC.sqrt (F.effect i)

theorem sqrtChannel_nonneg (i : I) : 0 ≤ F.sqrtChannel i := CFC.sqrt_nonneg _

theorem sqrtChannel_adjoint (i : I) : (F.sqrtChannel i).adjoint = F.sqrtChannel i :=
  (IsSelfAdjoint.of_nonneg (F.sqrtChannel_nonneg i)).adjoint_eq

theorem sqrtChannel_square (i : I) : F.sqrtChannel i * F.sqrtChannel i = F.effect i :=
  CFC.sqrt_mul_sqrt_self _ (F.operator_nonneg i)

/-- Every original effect is exactly the adjoint-square of its constructed channel. -/
theorem sqrtChannel_factor (i : I) :
    (F.sqrtChannel i).adjoint.comp (F.sqrtChannel i) = F.effect i := by
  rw [F.sqrtChannel_adjoint]
  exact F.sqrtChannel_square i

/-- The Parseval resolution is discharged from the original effect partition. -/
def sqrtFamily : ParsevalFamily H I (fun _ => H) where
  channel := F.sqrtChannel
  resolution := by simpa only [F.sqrtChannel_factor] using F.sum_effect

theorem sqrtFamily_effect (i : I) : F.sqrtFamily.effectAtlas.effect i = F.effect i :=
  F.sqrtChannel_factor i

theorem sqrtFamily_probability (x : H) (i : I) :
    F.sqrtFamily.effectAtlas.probability x i = F.probability x i := by
  unfold probability effectExpectation
  rw [F.sqrtFamily_effect]

theorem sqrtChannel_probability (x : H) (i : I) :
    ‖F.sqrtChannel i x‖ ^ 2 = F.probability x i := by
  rw [← F.sqrtFamily_probability x i, F.sqrtFamily.probability_eq_norm_sq]
  rfl

/-- A specified dilation map on the finite Hilbert sum of copies of H. -/
def dilation : H →L[ℂ] PiLp 2 (fun _ : I => H) := F.sqrtFamily.analysis

theorem dilation_isometric : F.dilation.adjoint.comp F.dilation = 1 :=
  F.sqrtFamily.adjoint_analysis_comp_analysis

theorem dilation_norm (x : H) : ‖F.dilation x‖ = ‖x‖ := F.sqrtFamily.analysis_norm x

/-- A compression theorem with no dilation assumption in its hypotheses. -/
theorem dilation_compression [DecidableEq I] (i : I) :
    F.dilation.adjoint.comp ((ChannelDilation.coordinate (fun _ : I => H) i).comp F.dilation)
      = F.effect i := by
  exact (F.sqrtFamily.effect_compression i).trans (F.sqrtFamily_effect i)

theorem exists_finite_dilation [DecidableEq I] :
    ∃ V : H →L[ℂ] PiLp 2 (fun _ : I => H),
      V.adjoint.comp V = 1 ∧ ∀ i,
        V.adjoint.comp ((ChannelDilation.coordinate (fun _ : I => H) i).comp V) = F.effect i :=
  ⟨F.dilation, F.dilation_isometric, F.dilation_compression⟩

end EffectAtlas
end KomorebiPhysics
