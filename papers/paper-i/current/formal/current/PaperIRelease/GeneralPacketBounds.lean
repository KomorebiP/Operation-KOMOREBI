import PaperIRelease.GeneralNormedPackets

set_option autoImplicit false
noncomputable section
open scoped BigOperators

namespace Komorebi.PaperIRelease.GeneralNormedPackets
namespace ContinuousProjectorFamily

variable {𝕜 X Y I : Type*} [NormedField 𝕜]
variable [NormedAddCommGroup X] [NormedSpace 𝕜 X]
variable [NormedAddCommGroup Y] [NormedSpace 𝕜 Y] [Fintype I]

theorem analysis_bound (P : ContinuousProjectorFamily 𝕜 X I)
    (C : ℝ) (hC : 0 ≤ C) (hb : ∀ i x, ‖P.proj i x‖ ≤ C * ‖x‖) (x : X) :
    ‖P.analysis x‖ ≤ C * ‖x‖ := by
  apply (pi_norm_le_iff_of_nonneg (mul_nonneg hC (norm_nonneg x))).mpr
  intro i
  exact hb i x

theorem synthesis_bound (P : ContinuousProjectorFamily 𝕜 X I)
    (z : ∀ i, P.packet i) : ‖P.synthesis z‖ ≤ (Fintype.card I : ℝ) * ‖z‖ := by
  rw [P.synthesis_apply]
  calc
    ‖∑ i, (z i : X)‖ ≤ ∑ i, ‖(z i : X)‖ := norm_sum_le _ _
    _ ≤ ∑ _i : I, ‖z‖ := Finset.sum_le_sum (fun i _ => norm_le_pi_norm z i)
    _ = (Fintype.card I : ℝ) * ‖z‖ := by simp

/-- Finite individual boundedness supplies a single bound for analysis. -/
theorem exists_uniform_bound (P : ContinuousProjectorFamily 𝕜 X I)
    (hb : ∀ i, IsBoundedLinearMap 𝕜 (P.proj i)) :
    ∃ C : ℝ, 0 ≤ C ∧ ∀ i x, ‖P.proj i x‖ ≤ C * ‖x‖ := by
  classical
  choose C hC hbound using fun i => (hb i).bound
  refine ⟨∑ i, C i, Finset.sum_nonneg (fun i _ => (hC i).le), ?_⟩
  intro i x
  exact (hbound i x).trans (mul_le_mul_of_nonneg_right
    (Finset.single_le_sum (fun j _ => (hC j).le) (Finset.mem_univ i)) (norm_nonneg x))

theorem analysis_isBounded (P : ContinuousProjectorFamily 𝕜 X I)
    (hb : ∀ i, IsBoundedLinearMap 𝕜 (P.proj i)) :
    IsBoundedLinearMap 𝕜 P.analysis := by
  obtain ⟨C, hC, h⟩ := P.exists_uniform_bound hb
  exact P.analysis.toLinearMap.isLinear.with_bound C (P.analysis_bound C hC h)

theorem synthesis_isBounded (P : ContinuousProjectorFamily 𝕜 X I) :
    IsBoundedLinearMap 𝕜 P.synthesis :=
  P.synthesis.toLinearMap.isLinear.with_bound (Fintype.card I : ℝ) P.synthesis_bound

/-- Literal bounded packet maps in every norm equivalent to the canonical
finite-product norm, including over trivially valued normed fields. -/
theorem equivalent_norm_packet_bounds (P : ContinuousProjectorFamily 𝕜 X I)
    (hb : ∀ i, IsBoundedLinearMap 𝕜 (P.proj i))
    (e : (∀ i, P.packet i) ≃ₗ[𝕜] Y)
    (C D : ℝ) (hC : ∀ z, ‖e z‖ ≤ C * ‖z‖)
    (hD : ∀ y, ‖e.symm y‖ ≤ D * ‖y‖) :
    (∀ i, IsClosed (P.packet i : Set X)) ∧
      IsBoundedLinearMap 𝕜 (fun x => e (P.analysis x)) ∧
      IsBoundedLinearMap 𝕜 (fun y => P.synthesis (e.symm y)) ∧
      Function.LeftInverse (fun y => P.synthesis (e.symm y)) (fun x => e (P.analysis x)) ∧
      Function.RightInverse (fun y => P.synthesis (e.symm y)) (fun x => e (P.analysis x)) := by
  refine ⟨P.isClosed_packet, ?_, ?_, ?_, ?_⟩
  · exact (e.toLinearMap.isLinear.with_bound C hC).comp (P.analysis_isBounded hb)
  · exact P.synthesis_isBounded.comp (e.symm.toLinearMap.isLinear.with_bound D hD)
  · intro x
    simp only [e.symm_apply_apply, P.synthesis_analysis]
  · intro y
    simp only [P.analysis_synthesis, e.apply_symm_apply]

end ContinuousProjectorFamily
end Komorebi.PaperIRelease.GeneralNormedPackets
