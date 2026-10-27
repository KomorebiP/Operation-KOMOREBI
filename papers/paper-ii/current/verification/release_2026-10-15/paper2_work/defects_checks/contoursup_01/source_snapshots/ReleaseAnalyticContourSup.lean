import ReleaseAnalyticContour
import Mathlib.Topology.Order.Compact

set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.ReleaseAnalyticContour
open scoped BigOperators Topology
open MeasureTheory Set TypedLinearDefects
universe u v
namespace IntegralCycle

/-- A finite cycle has compact trace, including the empty cycle. -/
theorem isCompact_trace (Γ : IntegralCycle) : IsCompact Γ.trace := by
  have htrace : Γ.trace = ⋃ i : Fin Γ.count, Γ.curve i '' uIcc (0:ℝ) 1 := by
    ext z
    simp only [trace, mem_setOf_eq, mem_iUnion, mem_image]
  rw [htrace]
  exact isCompact_iUnion fun i => isCompact_uIcc.image_of_continuousOn (Γ.continuousOn_curve i)

/-- Supremum norm on the trace, with explicit zero for an empty cycle. -/
def supNorm {E : Type u} [NormedAddCommGroup E] (Γ : IntegralCycle) (f : ℂ → E) : ℝ :=
  sSup (insert 0 ((fun z => ‖f z‖) '' Γ.trace))

 theorem bddAbove_norms {E : Type u} [NormedAddCommGroup E]
    (Γ : IntegralCycle) {f : ℂ → E} (hf : ContinuousOn f Γ.trace) :
    BddAbove (insert 0 ((fun z => ‖f z‖) '' Γ.trace)) := by
  exact (Γ.isCompact_trace.bddAbove_image hf.norm).insert 0

 theorem supNorm_nonneg {E : Type u} [NormedAddCommGroup E]
    (Γ : IntegralCycle) {f : ℂ → E} (hf : ContinuousOn f Γ.trace) :
    0 ≤ Γ.supNorm f := by
  exact le_csSup (Γ.bddAbove_norms hf) (mem_insert _ _)

 theorem norm_le_supNorm {E : Type u} [NormedAddCommGroup E]
    (Γ : IntegralCycle) {f : ℂ → E} (hf : ContinuousOn f Γ.trace)
    {z : ℂ} (hz : z ∈ Γ.trace) : ‖f z‖ ≤ Γ.supNorm f := by
  exact le_csSup (Γ.bddAbove_norms hf) (mem_insert_of_mem _ (mem_image_of_mem _ hz))

/-- On a nonempty trace this is exactly the usual supremum of norms. -/
theorem supNorm_eq_sSup {E : Type u} [NormedAddCommGroup E]
    (Γ : IntegralCycle) {f : ℂ → E} (hf : ContinuousOn f Γ.trace)
    (hne : Γ.trace.Nonempty) :
    Γ.supNorm f = sSup ((fun z => ‖f z‖) '' Γ.trace) := by
  apply le_antisymm
  · apply csSup_le (by simp [supNorm])
    intro b hb
    rcases hb with rfl | hb
    · obtain ⟨z,hz⟩ := hne
      exact (norm_nonneg (f z)).trans
        (le_csSup (Γ.isCompact_trace.bddAbove_image hf.norm) (mem_image_of_mem _ hz))
    · exact le_csSup (Γ.isCompact_trace.bddAbove_image hf.norm) hb
  · exact csSup_le_csSup (Γ.bddAbove_norms hf) (hne.image _) (subset_insert _ _)
end IntegralCycle

/-- Exact supremum-norm version of the actual cycle integral defect estimate.
For an empty cycle, the explicitly defined suprema and integral are zero. -/
theorem dunfordIntegral_norm_defect_le_sup
    {Ef : Type u} {Ec : Type v}
    [NormedAddCommGroup Ef] [NormedAddCommGroup Ec]
    [NormedSpace ℂ Ef] [NormedSpace ℂ Ec]
    [NormedSpace ℝ Ef] [NormedSpace ℝ Ec]
    [IsScalarTower ℝ ℂ Ef] [IsScalarTower ℝ ℂ Ec]
    [CompleteSpace Ef] [CompleteSpace Ec]
    (Γ : IntegralCycle) (h : ℂ → ℂ) (hh : ContinuousOn h Γ.trace)
    (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (hf : Γ.trace ⊆ resolventSet ℂ Tf) (hc : Γ.trace ⊆ resolventSet ℂ Tc) :
    ‖C.comp (dunfordIntegral Γ h Tf) - (dunfordIntegral Γ h Tc).comp C‖ ≤
      Γ.length / (2 * Real.pi) * Γ.supNorm h * ‖continuousDefect C Tf Tc‖ *
        Γ.supNorm (resolvent Tc) * Γ.supNorm (resolvent Tf) := by
  have hfc := continuousOn_resolvent_trace Γ Tf hf
  have hcc := continuousOn_resolvent_trace Γ Tc hc
  exact dunfordIntegral_norm_defect_le Γ h hh C Tf Tc hf hc _ _ _
    (Γ.supNorm_nonneg hh) (Γ.supNorm_nonneg hcc) (Γ.supNorm_nonneg hfc)
    (fun _ hz => Γ.norm_le_supNorm hh hz)
    (fun _ hz => Γ.norm_le_supNorm hcc hz)
    (fun _ hz => Γ.norm_le_supNorm hfc hz)
end Komorebi.PaperII.ReleaseAnalyticContour
