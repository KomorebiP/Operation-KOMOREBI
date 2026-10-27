module
public import Mathlib.Analysis.SpecialFunctions.Complex.Log
public import Mathlib.Topology.Separation.Lemmas
public import Mathlib.Topology.Order.LeftRightNhds
public import Mathlib.Topology.Order.IntermediateValue
public import Mathlib.Tactic.Linarith
public import Mathlib.Tactic.Ring

/-! Continuous logarithmic lifts have finite boundary values when their
exponentials tend to a nonzero value. No differentiability is assumed. -/
@[expose] public section
noncomputable section
open Filter Set Complex
open scoped Topology
namespace PaperX.ExponentialBoundary

theorem exists_limit_of_exp_limit (G : ℝ → ℂ)
    (hG : ContinuousOn G (Ioi 1)) {v : ℂ} (hv : v ≠ 0)
    (hexp : Tendsto (fun s ↦ Complex.exp (G s)) (𝓝[>] 1) (𝓝 v)) :
    ∃ g : ℂ, Complex.exp g = v ∧ Tendsto G (𝓝[>] 1) (𝓝 g) := by
  let F : ℝ → ℂ := fun s ↦ Complex.exp (G s) / v
  have hF : Tendsto F (𝓝[>] 1) (𝓝 (1 : ℂ)) := by
    simpa [F, div_self hv] using hexp.div_const v
  have hFn : ∀ s, F s ≠ 0 := fun s ↦ div_ne_zero (Complex.exp_ne_zero _) hv
  have hs : ∀ᶠ s in 𝓝[>] (1 : ℝ), F s ∈ Complex.slitPlane :=
    hF.eventually (Complex.isOpen_slitPlane.mem_nhds (by simp))
  obtain ⟨b, hb, hslit⟩ := mem_nhdsGT_iff_exists_Ioo_subset.mp hs
  have hsub : Ioo (1 : ℝ) b ⊆ Ioi 1 := fun _ h ↦ h.1
  let H : ℝ → ℂ := fun s ↦ G s - Complex.log v - Complex.log (F s)
  have hFc : ContinuousOn F (Ioo 1 b) :=
    ((Complex.continuous_exp.comp_continuousOn hG).mono hsub).div_const v
  have hH : ContinuousOn H (Ioo 1 b) :=
    ((hG.mono hsub).sub continuousOn_const).sub (hFc.clog hslit)
  have hHexp : ∀ s, Complex.exp (H s) = 1 := by
    intro s
    simp only [H, Complex.exp_sub, Complex.exp_log hv, Complex.exp_log (hFn s)]
    exact div_self (hFn s)
  have hk : IsTotallyDisconnected (Complex.exp ⁻¹' {1}) :=
    (Set.countable_singleton (1 : ℂ)).preimage_cexp.isTotallyDisconnected
  have himage : (H '' Ioo (1 : ℝ) b).Subsingleton :=
    hk _ (by rintro _ ⟨s, _, rfl⟩; exact hHexp s)
      (isPreconnected_Ioo.image H hH)
  obtain ⟨a, ha⟩ := nonempty_Ioo.mpr (show (1 : ℝ) < b from hb)
  have hconstant : ∀ s ∈ Ioo (1 : ℝ) b, H s = H a := fun s hs ↦
    himage (mem_image_of_mem H hs) (mem_image_of_mem H ha)
  have hlog : Tendsto (fun s ↦ Complex.log (F s)) (𝓝[>] 1) (𝓝 (0 : ℂ)) := by
    simpa using hF.clog (by simp)
  have hlimit : Tendsto G (𝓝[>] 1) (𝓝 (H a + Complex.log v)) := by
    have h := (tendsto_const_nhds (x := H a + Complex.log v)).add hlog
    simp only [add_zero] at h
    apply h.congr'
    filter_upwards [Ioo_mem_nhdsGT hb] with s hs
    have hc := hconstant s hs
    dsimp [H] at hc
    linear_combination -hc
  refine ⟨H a + Complex.log v, ?_, hlimit⟩
  exact tendsto_nhds_unique ((Complex.continuous_exp.tendsto _).comp hlimit) hexp

end PaperX.ExponentialBoundary
