module

public import KomorebiPhysics.PositiveEffects
public import Mathlib.Analysis.InnerProductSpace.PiL2

/-!
Chapter 5.4 (5.22)--(5.29): actual bounded channels into a finite family
of complex Hilbert spaces, their effects, and analysis/synthesis maps.
The only resolution hypothesis is sum_i V_i† V_i = I.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
open scoped BigOperators
open ContinuousLinearMap

/-- A given finite Parseval family, with no compression or reconstruction conclusion as a field. -/
structure ParsevalFamily (H I : Type*) (K : I → Type*)
    [NormedAddCommGroup H] [InnerProductSpace ℂ H] [CompleteSpace H] [Fintype I]
    [∀ i, NormedAddCommGroup (K i)] [∀ i, InnerProductSpace ℂ (K i)]
    [∀ i, CompleteSpace (K i)] where
  channel : ∀ i, H →L[ℂ] K i
  resolution : ∑ i, (channel i).adjoint.comp (channel i) = 1

namespace ParsevalFamily
variable {H I : Type*} {K : I → Type*}
  [NormedAddCommGroup H] [InnerProductSpace ℂ H] [CompleteSpace H] [Fintype I]
  [∀ i, NormedAddCommGroup (K i)] [∀ i, InnerProductSpace ℂ (K i)]
  [∀ i, CompleteSpace (K i)]
variable (V : ParsevalFamily H I K)

/-- The positive effects are constructed, with all atlas laws discharged. -/
def effectAtlas : EffectAtlas H I where
  effect i := (V.channel i).adjoint.comp (V.channel i)
  selfAdjoint i x y := by
    simp only [comp_apply, adjoint_inner_left, adjoint_inner_right]
  nonnegative i x := by
    simp only [comp_apply, adjoint_inner_right]
    rw [inner_self_eq_norm_sq (𝕜 := ℂ)]
    positivity
  sum_effect := V.resolution

/-- Literal channel-norm probability (5.23). -/
theorem probability_eq_norm_sq (x : H) (i : I) :
    V.effectAtlas.probability x i = ‖V.channel i x‖ ^ 2 := by
  change (inner ℂ x ((V.channel i).adjoint (V.channel i x))).re = _
  rw [adjoint_inner_right]
  exact inner_self_eq_norm_sq (𝕜 := ℂ) _

/-- Literal state reconstruction (5.24). -/
theorem reconstruct_state (x : H) :
    (∑ i, (V.channel i).adjoint (V.channel i x)) = x :=
  V.effectAtlas.reconstruct x

theorem reconstruct_inner (x y : H) :
    (∑ i, inner ℂ (V.channel i x) (V.channel i y)) = inner ℂ x y := by
  simp only [← adjoint_inner_right, ← inner_sum, V.reconstruct_state]

theorem norm_sq_sum (x : H) : (∑ i, ‖V.channel i x‖ ^ 2) = ‖x‖ ^ 2 := by
  simpa only [V.probability_eq_norm_sq] using V.effectAtlas.probability_sum x

theorem channel_norm_le (x : H) (i : I) : ‖V.channel i x‖ ≤ ‖x‖ := by
  have h := V.effectAtlas.probability_le_norm_sq x i
  rw [V.probability_eq_norm_sq] at h
  nlinarith [norm_nonneg (V.channel i x), norm_nonneg x]

/-- The actual cross-channel block H_j -> H_i, with the source adjoint on the right. -/
def channelBlock (X : H →L[ℂ] H) (i j : I) : K j →L[ℂ] K i :=
  (V.channel i).comp (X.comp (V.channel j).adjoint)

theorem channelBlock_apply (X : H →L[ℂ] H) (i j : I) (y : K j) :
    V.channelBlock X i j y = V.channel i (X ((V.channel j).adjoint y)) := rfl

/-- Literal full double-sum reconstruction (5.25), for every bounded X. -/
theorem reconstruct_operator (X : H →L[ℂ] H) :
    (∑ i, ∑ j, (V.channel i).adjoint.comp
      ((V.channelBlock X i j).comp (V.channel j))) = X := by
  ext x
  simp only [sum_apply, comp_apply, channelBlock, ← map_sum, V.reconstruct_state]

/-- The finite Hilbert direct sum, not the sup-norm product, receives the analysis map. -/
def analysis : H →L[ℂ] PiLp 2 K :=
  (PiLp.continuousLinearEquiv 2 ℂ K).symm.toContinuousLinearMap.comp
    (ContinuousLinearMap.pi V.channel)

/-- Actual synthesis, separately constructed from channel adjoints and coordinate evaluation. -/
def synthesis : PiLp 2 K →L[ℂ] H :=
  ∑ i, (V.channel i).adjoint.comp (PiLp.proj 2 K i)

theorem analysis_apply (x : H) (i : I) : V.analysis x i = V.channel i x := rfl

theorem synthesis_apply (y : PiLp 2 K) :
    V.synthesis y = ∑ i, (V.channel i).adjoint (y i) := by
  simp only [synthesis, sum_apply, comp_apply, PiLp.proj_apply]

/-- The adjoint identification is proved by the Hilbert pairing, not postulated. -/
theorem synthesis_eq_adjoint : V.synthesis = V.analysis.adjoint := by
  apply (eq_adjoint_iff _ _).mpr
  intro y x
  simp only [V.synthesis_apply, sum_inner, adjoint_inner_left,
    PiLp.inner_apply, V.analysis_apply]

theorem adjoint_analysis : V.analysis.adjoint = V.synthesis := V.synthesis_eq_adjoint.symm

theorem adjoint_synthesis : V.synthesis.adjoint = V.analysis := by
  rw [V.synthesis_eq_adjoint, adjoint_adjoint]

theorem synthesis_analysis : V.synthesis.comp V.analysis = 1 := by
  ext x
  simp only [comp_apply, V.synthesis_apply, V.analysis_apply,
    V.reconstruct_state, one_apply_eq_self]

/-- Literal isometric identity (5.31). -/
theorem adjoint_analysis_comp_analysis : V.analysis.adjoint.comp V.analysis = 1 := by
  rw [V.adjoint_analysis, V.synthesis_analysis]

theorem analysis_inner (x y : H) : inner ℂ (V.analysis x) (V.analysis y) = inner ℂ x y := by
  simpa only [PiLp.inner_apply, V.analysis_apply] using V.reconstruct_inner x y

theorem analysis_norm (x : H) : ‖V.analysis x‖ = ‖x‖ := by
  have h := congrArg Complex.re (V.analysis_inner x x)
  change (inner ℂ (V.analysis x) (V.analysis x)).re = (inner ℂ x x).re at h
  rw [inner_self_eq_norm_sq (𝕜 := ℂ), inner_self_eq_norm_sq (𝕜 := ℂ)] at h
  nlinarith [norm_nonneg (V.analysis x), norm_nonneg x]

/-- Norm preservation is attached to the already constructed analysis operator. -/
def analysisIsometry : H →ₗᵢ[ℂ] PiLp 2 K where
  toLinearMap := V.analysis.toLinearMap
  norm_map' := V.analysis_norm

theorem analysis_injective : Function.Injective V.analysis := by
  intro x y h
  have h' := congrArg V.synthesis h
  have he (z : H) : V.synthesis (V.analysis z) = z :=
    congrArg (fun T : H →L[ℂ] H => T z) V.synthesis_analysis
  simpa only [he] using h'

/-- A channel-norm continuity theorem from the original vector flow. -/
theorem hasDerivAt_channel_norm (A : H →L[ℂ] H) (hA : IsSkew A)
    {ψ : ℝ → H} {t : ℝ} (hψ : HasDerivAt ψ (A (ψ t)) t) (i : I) :
    HasDerivAt (fun s => ‖V.channel i (ψ s)‖ ^ 2)
      (∑ j, V.effectAtlas.current A (ψ t) i j) t := by
  simpa only [V.probability_eq_norm_sq] using V.effectAtlas.hasDerivAt_probability A hA hψ i

/-- The actual derivative of the analysis trajectory. -/
theorem hasDerivAt_analysis {ψ : ℝ → H} {v : H} {t : ℝ}
    (hψ : HasDerivAt ψ v t) :
    HasDerivAt (fun s => V.analysis (ψ s)) (V.analysis v) t :=
  (V.analysis.restrictScalars ℝ).hasFDerivAt.comp_hasDerivAt t hψ

end ParsevalFamily
end KomorebiPhysics
