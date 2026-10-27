import KomorebiVerification.PaperII.ReleaseRectifiableLength
import KomorebiVerification.PaperII.ReleaseRectifiableRSError
import KomorebiVerification.PaperII.ReleaseAnalyticContourSup

/-! Defect identity and original geometric-length bound for classical tagged
Riemann–Stieltjes integrals on finite continuous rectifiable cycles.  The remaining
canonical holomorphic-calculus identification is a separate theorem. -/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.ReleaseRectifiableDefect
open MeasureTheory Set
open scoped Topology BigOperators
open Komorebi.PaperII.ReleaseAnalyticContour
open Komorebi.PaperII.ReleaseRectifiableCycle
open Komorebi.PaperII.ReleaseRectifiableLength
open Komorebi.PaperII.ReleaseRectifiableRSError
open Komorebi.PaperII.ReleaseArcLength
open TypedLinearDefects
universe u v

/-- Chosen-cycle Dunford integral using the original contours' tagged RS
integrals, not defined through a velocity integral. -/
def rectifiableDunford (n : ℕ) (f : Fin n → ℝ → ℂ) (h : ℂ → ℂ)
    {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    (T : E →L[ℂ] E) : E →L[ℂ] E :=
  (2 * (Real.pi : ℂ) * Complex.I)⁻¹ •
    ∑ i : Fin n, taggedContourIntegral (f i) (fun z ↦ h z • resolvent T z) 0 1

section Operators
variable {Ef : Type u} {Ec : Type v}
variable [NormedAddCommGroup Ef] [NormedAddCommGroup Ec]
variable [NormedSpace ℂ Ef] [NormedSpace ℂ Ec]
variable [NormedSpace ℝ Ef] [NormedSpace ℝ Ec]
variable [IsScalarTower ℝ ℂ Ef] [IsScalarTower ℝ ℂ Ec]
variable [CompleteSpace Ef] [CompleteSpace Ec]

/-- Every original component trace lies in the actual reconstructed cycle. -/
theorem component_subset_trace (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0) (i : Fin n) :
    f i '' Icc (0:ℝ) 1 ⊆ (cycleOfRectifiable n f hv hc hclosed).trace := by
  intro z hz
  rw [trace_cycleOfRectifiable n f hv hc hclosed]
  exact ⟨i,hz⟩

/-- Proven RS/velocity representation for each original Dunford integral. -/
theorem rectifiableDunford_eq_dunfordIntegral (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0)
    (h : ℂ → ℂ) (hh : ContinuousOn h (cycleOfRectifiable n f hv hc hclosed).trace)
    {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    [NormedSpace ℝ E] [IsScalarTower ℝ ℂ E] [CompleteSpace E]
    (T : E →L[ℂ] E)
    (hT : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ resolventSet ℂ T) :
    rectifiableDunford n f h T = dunfordIntegral (cycleOfRectifiable n f hv hc hclosed) h T := by
  unfold rectifiableDunford dunfordIntegral
  apply congrArg (fun A ↦ (2 * (Real.pi : ℂ) * Complex.I)⁻¹ • A)
  exact sum_taggedContourIntegral_eq_lineIntegral n f hv hc hclosed
    (fun i ↦ (hh.smul (continuousOn_resolvent_trace _ T hT)).mono
      (component_subset_trace n f hv hc hclosed i))

/-- The actual classical finite-rectifiable-cycle defect identity. -/
theorem rectifiableDunford_defect (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0)
    (h : ℂ → ℂ) (hh : ContinuousOn h (cycleOfRectifiable n f hv hc hclosed).trace)
    (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (hf : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ resolventSet ℂ Tf)
    (hcc : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ resolventSet ℂ Tc) :
    C.comp (rectifiableDunford n f h Tf) - (rectifiableDunford n f h Tc).comp C =
      (2 * (Real.pi : ℂ) * Complex.I)⁻¹ •
        ∑ i : Fin n, taggedContourIntegral (f i) (fun z ↦ h z •
          ((resolvent Tc z).comp ((continuousDefect C Tf Tc).comp (resolvent Tf z)))) 0 1 := by
  have hfc := continuousOn_resolvent_trace (cycleOfRectifiable n f hv hc hclosed) Tf hf
  have hccc := continuousOn_resolvent_trace (cycleOfRectifiable n f hv hc hclosed) Tc hcc
  have hcont := hh.smul (hccc.clm_comp
    ((continuousOn_const (c := continuousDefect C Tf Tc)).clm_comp hfc))
  rw [rectifiableDunford_eq_dunfordIntegral n f hv hc hclosed h hh Tf hf,
    rectifiableDunford_eq_dunfordIntegral n f hv hc hclosed h hh Tc hcc,
    dunfordIntegral_defect _ h hh C Tf Tc hf hcc]
  apply congrArg (fun A ↦ (2 * (Real.pi : ℂ) * Complex.I)⁻¹ • A)
  exact (sum_taggedContourIntegral_eq_lineIntegral n f hv hc hclosed
    (fun i ↦ hcont.mono (component_subset_trace n f hv hc hclosed i))).symm

/-- The paper's separate supremum factors with the original geometric length,
proved using the sufficient velocity-length upper bound. -/
theorem rectifiableDunford_norm_defect_le_geometric_sup (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0)
    (h : ℂ → ℂ) (hh : ContinuousOn h (cycleOfRectifiable n f hv hc hclosed).trace)
    (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (hf : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ resolventSet ℂ Tf)
    (hcc : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ resolventSet ℂ Tc) :
    ‖C.comp (rectifiableDunford n f h Tf) - (rectifiableDunford n f h Tc).comp C‖ ≤
      (∑ i : Fin n, geometricLength (f i)) / (2 * Real.pi) *
        (cycleOfRectifiable n f hv hc hclosed).supNorm h * ‖continuousDefect C Tf Tc‖ *
        (cycleOfRectifiable n f hv hc hclosed).supNorm (resolvent Tc) *
        (cycleOfRectifiable n f hv hc hclosed).supNorm (resolvent Tf) := by
  let Γ := cycleOfRectifiable n f hv hc hclosed
  have hfc := continuousOn_resolvent_trace Γ Tf hf
  have hccc := continuousOn_resolvent_trace Γ Tc hcc
  have hh0 := Γ.supNorm_nonneg hh
  have hfc0 := Γ.supNorm_nonneg hfc
  have hcc0 := Γ.supNorm_nonneg hccc
  rw [rectifiableDunford_eq_dunfordIntegral n f hv hc hclosed h hh Tf hf,
    rectifiableDunford_eq_dunfordIntegral n f hv hc hclosed h hh Tc hcc]
  apply (dunfordIntegral_norm_defect_le_sup Γ h hh C Tf Tc hf hcc).trans
  gcongr
  exact length_cycleOfRectifiable_le n f hv hc hclosed

end Operators
end Komorebi.PaperII.ReleaseRectifiableDefect
