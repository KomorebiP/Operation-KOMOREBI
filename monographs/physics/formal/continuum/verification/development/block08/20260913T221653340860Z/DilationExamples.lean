module

public import KomorebiPhysics.DilationDynamics
public import KomorebiPhysics.CycleGauge
public import KomorebiPhysics.EffectExamples

/-! Exact proper-isometry witnesses. These are not numerical approximations. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace DilationExamples
open scoped BigOperators
open ContinuousLinearMap

def weight : Fin 2 → ℝ := ![3 / 5, 4 / 5]

def scalarChannel (i : Fin 2) : ℂ →L[ℂ] ℂ := (weight i : ℂ) • 1

theorem scalarChannel_apply (i : Fin 2) (x : ℂ) :
    scalarChannel i x = (weight i : ℂ) * x := rfl

theorem scalarChannel_adjoint (i : Fin 2) :
    (scalarChannel i).adjoint = scalarChannel i := by
  symm
  apply (eq_adjoint_iff _ _).mpr
  intro x y
  simp [scalarChannel, inner_smul_left, inner_smul_right]

/-- A concrete family with two nonzero channels and a strictly larger dilation space. -/
def scalarFamily : ParsevalFamily ℂ (Fin 2) (fun _ => ℂ) where
  channel := scalarChannel
  resolution := by
    ext x
    simp only [Fin.sum_univ_two, add_apply, comp_apply, scalarChannel_adjoint,
      scalarChannel_apply, one_apply_eq_self]
    norm_num [weight]
    ring

theorem scalar_effect_apply (i : Fin 2) (x : ℂ) :
    scalarFamily.effectAtlas.effect i x = (weight i : ℂ)^2 * x := by
  change (scalarChannel i).adjoint (scalarChannel i x) = _
  rw [scalarChannel_adjoint, scalarChannel_apply, scalarChannel_apply]
  ring

theorem scalar_probabilities :
    scalarFamily.effectAtlas.probability 1 0 = 9 / 25 ∧
    scalarFamily.effectAtlas.probability 1 1 = 16 / 25 := by
  change (inner ℂ (1:ℂ) (scalarFamily.effectAtlas.effect 0 1)).re = _ ∧
    (inner ℂ (1:ℂ) (scalarFamily.effectAtlas.effect 1 1)).re = _
  norm_num [scalar_effect_apply, weight]

def kernelVector : PiLp 2 (fun _ : Fin 2 => ℂ) :=
  (4/5:ℂ) • PiLp.single 2 0 1 - (3/5:ℂ) • PiLp.single 2 1 1

theorem synthesis_kernel : scalarFamily.synthesis kernelVector = 0 := by
  rw [scalarFamily.synthesis_apply]
  simp only [Fin.sum_univ_two]
  change (scalarChannel 0).adjoint (kernelVector 0) +
    (scalarChannel 1).adjoint (kernelVector 1) = 0
  simp [scalarChannel_adjoint, scalarChannel_apply, kernelVector, PiLp.single_apply, weight]
  ring

theorem kernelVector_nonzero : kernelVector ≠ 0 := by
  intro h
  have h0 := congrArg (fun y : PiLp 2 (fun _ : Fin 2 => ℂ) => y 0) h
  norm_num [kernelVector, PiLp.single_apply] at h0

theorem rangeProjection_kernel : scalarFamily.rangeProjection kernelVector = 0 := by
  change scalarFamily.analysis (scalarFamily.synthesis kernelVector) = 0
  rw [synthesis_kernel, map_zero]

theorem rangeProjection_not_identity : scalarFamily.rangeProjection ≠ 1 := by
  intro h
  have he := rangeProjection_kernel
  rw [h, one_apply_eq_self] at he
  exact kernelVector_nonzero he

theorem analysis_not_surjective : ¬Function.Surjective scalarFamily.analysis := by
  intro h
  obtain ⟨x,hx⟩ := h kernelVector
  have he := scalarFamily.rangeProjection_fix_analysis x
  rw [hx, rangeProjection_kernel] at he
  exact kernelVector_nonzero he.symm

/-- Incorrectly retaining only diagonal channel blocks gives this actual operator. -/
def diagonalOnly : ℂ →L[ℂ] ℂ :=
  ∑ i, (scalarFamily.channel i).adjoint.comp
    ((scalarFamily.channelBlock 1 i i).comp (scalarFamily.channel i))

theorem diagonalOnly_value : diagonalOnly 1 = (337/625:ℂ) := by
  simp only [diagonalOnly, sum_apply, Fin.sum_univ_two, comp_apply,
    ParsevalFamily.channelBlock_apply]
  change (scalarChannel 0).adjoint (scalarChannel 0 ((1:ℂ→L[ℂ]ℂ)
    ((scalarChannel 0).adjoint (scalarChannel 0 1)))) +
    (scalarChannel 1).adjoint (scalarChannel 1 ((1:ℂ→L[ℂ]ℂ)
    ((scalarChannel 1).adjoint (scalarChannel 1 1)))) = _
  norm_num [scalarChannel_adjoint, scalarChannel_apply, weight]

theorem diagonalOnly_not_identity : diagonalOnly ≠ 1 := by
  intro h
  have he := diagonalOnly_value
  rw [h, one_apply_eq_self] at he
  norm_num at he

theorem full_reconstruction :
    (∑ i, ∑ j, (scalarFamily.channel i).adjoint.comp
      ((scalarFamily.channelBlock 1 i j).comp (scalarFamily.channel j))) = 1 :=
  scalarFamily.reconstruct_operator 1

theorem compressed_effect_not_idempotent :
    scalarFamily.effectAtlas.effect 0 * scalarFamily.effectAtlas.effect 0 ≠
      scalarFamily.effectAtlas.effect 0 := by
  intro h
  have he := congrArg (fun T : ℂ →L[ℂ] ℂ => T 1) h
  norm_num [mul_apply_eq_comp, scalar_effect_apply, weight] at he

theorem compression_not_multiplicative :
    scalarFamily.compressOperator
      (ChannelDilation.coordinate (fun _ : Fin 2 => ℂ) 0 *
       ChannelDilation.coordinate (fun _ : Fin 2 => ℂ) 0) ≠
    scalarFamily.compressOperator (ChannelDilation.coordinate (fun _ : Fin 2 => ℂ) 0) *
    scalarFamily.compressOperator (ChannelDilation.coordinate (fun _ : Fin 2 => ℂ) 0) := by
  rw [ChannelDilation.coordinate_idempotent, scalarFamily.compress_coordinate]
  exact Ne.symm compressed_effect_not_idempotent

theorem scalar_unsharpness :
    effectExpectation (scalarFamily.effectAtlas.effect 0 -
      scalarFamily.effectAtlas.effect 0 * scalarFamily.effectAtlas.effect 0) 1 = 144/625 := by
  norm_num [effectExpectation, sub_apply, mul_apply_eq_comp, scalar_effect_apply, weight]

theorem escaped_norm_exact :
    ‖ChannelDilation.coordinate (fun _ : Fin 2 => ℂ) 0 (scalarFamily.analysis 1) -
      scalarFamily.rangeProjection
        (ChannelDilation.coordinate (fun _ : Fin 2 => ℂ) 0 (scalarFamily.analysis 1))‖^2 = 144/625 := by
  rw [← scalarFamily.effect_defect_norm]
  exact scalar_unsharpness

theorem lifted_identity_not_ambient_identity : scalarFamily.liftOperator 1 ≠ 1 := by
  rw [scalarFamily.liftOperator_one]
  exact rangeProjection_not_identity

theorem missing_normalization :
    (∑ _i : Fin 2, (1:ℂ→L[ℂ]ℂ).adjoint.comp 1) ≠ 1 := by
  intro h
  have he := congrArg (fun T : ℂ →L[ℂ] ℂ => T 1) h
  norm_num [Fin.sum_univ_two, adjoint_one, comp_apply] at he

/-- The universal square-root construction reproduces a previously checked genuinely soft effect. -/
theorem soft_dilation_probability :
    (EffectExamples.softAtlas.sqrtFamily).effectAtlas.probability EffectExamples.softState 0 = 43/100 := by
  have he : EffectExamples.softAtlas.sqrtFamily.effectAtlas = EffectExamples.softAtlas := by
    apply EffectAtlas.ext
    exact EffectExamples.softAtlas.sqrtFamily_effect
  rw [he]
  exact EffectExamples.soft_probabilities.1

end DilationExamples
end KomorebiPhysics
