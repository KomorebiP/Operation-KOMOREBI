import KomorebiVerification.PaperII.ReleaseCanonicalHFC
import KomorebiVerification.PaperII.ReleaseRectifiableDefect
import KomorebiVerification.PaperII.ReleaseDefectTower

/-! Canonical holomorphic-calculus defect and arbitrary-depth compatibility,
with the original finite rectifiable tagged RS contours and geometric length. -/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.ReleaseCanonicalDefect
open Set
open scoped Topology BigOperators
open Komorebi.PaperII.ReleaseAnalyticContour
open Komorebi.PaperII.ReleaseRectifiableCycle
open Komorebi.PaperII.ReleaseRectifiableDefect
open Komorebi.PaperII.ReleaseRectifiableRSError
open Komorebi.PaperII.ReleaseArcLength
open Komorebi.PaperII.ReleaseCycleWinding
open Komorebi.PaperII.ReleaseCanonicalHFC
open Komorebi.PaperII.ReleaseDefectTower
open TypedLinearDefects
universe u v

/-- Original rectifiable winding, defined from the genuine tagged RS
contour integrals on the original parameterized paths. -/
def rectifiableWinding (n : ℕ) (f : Fin n → ℝ → ℂ) (w : ℂ) : ℂ :=
  (2 * (Real.pi : ℂ) * Complex.I)⁻¹ *
    ∑ i : Fin n, taggedContourIntegral (f i) (fun z ↦ (z-w)⁻¹) 0 1

/-- The original classical winding equals the actual represented cycle's
winding, as a theorem of the tagged RS/velocity comparison. -/
theorem rectifiableWinding_eq_winding (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0) {w : ℂ}
    (hw : w ∉ (cycleOfRectifiable n f hv hc hclosed).trace) :
    rectifiableWinding n f w = winding (cycleOfRectifiable n f hv hc hclosed) w := by
  have hcont : ContinuousOn (fun z : ℂ ↦ (z-w)⁻¹) (cycleOfRectifiable n f hv hc hclosed).trace :=
    (continuousOn_id.sub continuousOn_const).inv₀
      (fun z hz ↦ sub_ne_zero.mpr (ne_of_mem_of_not_mem hz hw))
  unfold rectifiableWinding winding
  apply congrArg (fun a : ℂ ↦ (2 * (Real.pi : ℂ) * Complex.I)⁻¹ * a)
  exact sum_taggedContourIntegral_eq_lineIntegral n f hv hc hclosed
    (fun i ↦ hcont.mono (component_subset_trace n f hv hc hclosed i))

/-- The manuscript's actual rectifiable Cauchy hypotheses construct an
admissible canonical-calculus cycle. No representation equation is a field. -/
def admissibleRectifiable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0)
    (h : ℂ → ℂ) (U : Set ℂ) (hU : IsOpen U) (hh : DifferentiableOn ℂ h U)
    (T : E →L[ℂ] E) (hσ : spectrum ℂ T ⊆ U)
    (htrace : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ U)
    (hR : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ resolventSet ℂ T)
    (hwindσ : ∀ z ∈ spectrum ℂ T, winding (cycleOfRectifiable n f hv hc hclosed) z = 1)
    (hwindU : ∀ z ∉ U, winding (cycleOfRectifiable n f hv hc hclosed) z = 0) :
    AdmissibleCycle h T where
  domain := U
  isOpen_domain := hU
  holomorphic := hh
  spectrum_subset := hσ
  cycle := cycleOfRectifiable n f hv hc hclosed
  trace_domain := htrace
  trace_resolvent := hR
  winding_spectrum := hwindσ
  winding_complement := hwindU

/-- Admission from the original contours' own classical winding numbers.
The off-trace hypotheses needed for winding comparison follow from the actual
resolvent and open-domain assumptions. -/
def admissibleRectifiable_original {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0)
    (h : ℂ → ℂ) (U : Set ℂ) (hU : IsOpen U) (hh : DifferentiableOn ℂ h U)
    (T : E →L[ℂ] E) (hσ : spectrum ℂ T ⊆ U)
    (htrace : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ U)
    (hR : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ resolventSet ℂ T)
    (hwindσ : ∀ z ∈ spectrum ℂ T, rectifiableWinding n f z = 1)
    (hwindU : ∀ z ∉ U, rectifiableWinding n f z = 0) : AdmissibleCycle h T := by
  refine admissibleRectifiable n f hv hc hclosed h U hU hh T hσ htrace hR ?_ ?_
  · intro z hz
    have hzR : z ∉ resolventSet ℂ T := by simpa only [spectrum,mem_compl_iff] using hz
    rw [← rectifiableWinding_eq_winding n f hv hc hclosed (fun ht ↦ hzR (hR ht))]
    exact hwindσ z hz
  · intro z hz
    rw [← rectifiableWinding_eq_winding n f hv hc hclosed (fun ht ↦ hz (htrace ht))]
    exact hwindU z hz

/-- Canonical calculus is represented by the original tagged rectifiable
contour integral under precisely the geometric Cauchy hypotheses. -/
theorem canonicalValue_eq_rectifiableDunford
    {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    [NormedSpace ℝ E] [IsScalarTower ℝ ℂ E] [CompleteSpace E]
    (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0)
    (h : ℂ → ℂ) (U : Set ℂ) (hU : IsOpen U) (hh : DifferentiableOn ℂ h U)
    (T : E →L[ℂ] E) (hσ : spectrum ℂ T ⊆ U)
    (htrace : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ U)
    (hR : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ resolventSet ℂ T)
    (hwindσ : ∀ z ∈ spectrum ℂ T, winding (cycleOfRectifiable n f hv hc hclosed) z = 1)
    (hwindU : ∀ z ∉ U, winding (cycleOfRectifiable n f hv hc hclosed) z = 0)
    (H : Nonempty (AdmissibleCycle h T)) :
    canonicalValue h T H = rectifiableDunford n f h T := by
  let A := admissibleRectifiable n f hv hc hclosed h U hU hh T hσ htrace hR hwindσ hwindU
  exact (canonicalValue_eq_dunfordIntegral h T H A).trans
    (rectifiableDunford_eq_dunfordIntegral n f hv hc hclosed h
      (hh.continuousOn.mono htrace) T hR).symm

/-- Original-winding form of the canonical RS representation theorem. -/
theorem canonicalValue_eq_rectifiableDunford_original
    {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
    [NormedSpace ℝ E] [IsScalarTower ℝ ℂ E] [CompleteSpace E]
    (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0)
    (h : ℂ → ℂ) (U : Set ℂ) (hU : IsOpen U) (hh : DifferentiableOn ℂ h U)
    (T : E →L[ℂ] E) (hσ : spectrum ℂ T ⊆ U)
    (htrace : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ U)
    (hR : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ resolventSet ℂ T)
    (hwindσ : ∀ z ∈ spectrum ℂ T, rectifiableWinding n f z = 1)
    (hwindU : ∀ z ∉ U, rectifiableWinding n f z = 0)
    (H : Nonempty (AdmissibleCycle h T)) :
    canonicalValue h T H = rectifiableDunford n f h T := by
  let A := admissibleRectifiable_original n f hv hc hclosed h U hU hh T hσ htrace hR hwindσ hwindU
  exact (canonicalValue_eq_dunfordIntegral h T H A).trans
    (rectifiableDunford_eq_dunfordIntegral n f hv hc hclosed h
      (hh.continuousOn.mono htrace) T hR).symm

section TwoSpaces
variable {Ef : Type u} {Ec : Type v}
variable [NormedAddCommGroup Ef] [NormedAddCommGroup Ec]
variable [NormedSpace ℂ Ef] [NormedSpace ℂ Ec]
variable [NormedSpace ℝ Ef] [NormedSpace ℝ Ec]
variable [IsScalarTower ℝ ℂ Ef] [IsScalarTower ℝ ℂ Ec]
variable [CompleteSpace Ef] [CompleteSpace Ec]

/-- Theorem 11.6: the canonical holomorphic-calculus defect, with the original
classical tagged rectifiable contour integrals on its right-hand side. -/
theorem canonical_holomorphic_defect (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0)
    (h : ℂ → ℂ) (U : Set ℂ) (hU : IsOpen U) (hh : DifferentiableOn ℂ h U)
    (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (hσf : spectrum ℂ Tf ⊆ U) (hσc : spectrum ℂ Tc ⊆ U)
    (htrace : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ U)
    (hRf : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ resolventSet ℂ Tf)
    (hRc : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ resolventSet ℂ Tc)
    (hwindσ : ∀ z ∈ spectrum ℂ Tf ∪ spectrum ℂ Tc,
      rectifiableWinding n f z = 1)
    (hwindU : ∀ z ∉ U, rectifiableWinding n f z = 0)
    (Hf : Nonempty (AdmissibleCycle h Tf)) (Hc : Nonempty (AdmissibleCycle h Tc)) :
    C.comp (canonicalValue h Tf Hf) - (canonicalValue h Tc Hc).comp C =
      (2 * (Real.pi : ℂ) * Complex.I)⁻¹ •
        ∑ i : Fin n, taggedContourIntegral (f i) (fun z ↦ h z •
          ((resolvent Tc z).comp ((continuousDefect C Tf Tc).comp (resolvent Tf z)))) 0 1 := by
  rw [canonicalValue_eq_rectifiableDunford_original n f hv hc hclosed h U hU hh Tf hσf htrace hRf
      (fun z hz ↦ hwindσ z (Or.inl hz)) hwindU Hf,
    canonicalValue_eq_rectifiableDunford_original n f hv hc hclosed h U hU hh Tc hσc htrace hRc
      (fun z hz ↦ hwindσ z (Or.inr hz)) hwindU Hc]
  exact rectifiableDunford_defect n f hv hc hclosed h (hh.continuousOn.mono htrace) C Tf Tc hRf hRc

/-- Theorem 11.6 norm bound: original geometric length, actual canonical
values, and the three separate trace suprema occurring in the manuscript. -/
theorem canonical_holomorphic_norm_defect_le (n : ℕ) (f : Fin n → ℝ → ℂ)
    (hv : ∀ i, BoundedVariationOn (f i) (Icc (0:ℝ) 1))
    (hc : ∀ i, ContinuousOn (f i) (Icc (0:ℝ) 1))
    (hclosed : ∀ i, f i 1 = f i 0)
    (h : ℂ → ℂ) (U : Set ℂ) (hU : IsOpen U) (hh : DifferentiableOn ℂ h U)
    (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (hσf : spectrum ℂ Tf ⊆ U) (hσc : spectrum ℂ Tc ⊆ U)
    (htrace : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ U)
    (hRf : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ resolventSet ℂ Tf)
    (hRc : (cycleOfRectifiable n f hv hc hclosed).trace ⊆ resolventSet ℂ Tc)
    (hwindσ : ∀ z ∈ spectrum ℂ Tf ∪ spectrum ℂ Tc,
      rectifiableWinding n f z = 1)
    (hwindU : ∀ z ∉ U, rectifiableWinding n f z = 0)
    (Hf : Nonempty (AdmissibleCycle h Tf)) (Hc : Nonempty (AdmissibleCycle h Tc)) :
    ‖C.comp (canonicalValue h Tf Hf) - (canonicalValue h Tc Hc).comp C‖ ≤
      (∑ i : Fin n, geometricLength (f i)) / (2 * Real.pi) *
        (cycleOfRectifiable n f hv hc hclosed).supNorm h * ‖continuousDefect C Tf Tc‖ *
        (cycleOfRectifiable n f hv hc hclosed).supNorm (resolvent Tc) *
        (cycleOfRectifiable n f hv hc hclosed).supNorm (resolvent Tf) := by
  rw [canonicalValue_eq_rectifiableDunford_original n f hv hc hclosed h U hU hh Tf hσf htrace hRf
      (fun z hz ↦ hwindσ z (Or.inl hz)) hwindU Hf,
    canonicalValue_eq_rectifiableDunford_original n f hv hc hclosed h U hU hh Tc hσc htrace hRc
      (fun z hz ↦ hwindσ z (Or.inr hz)) hwindU Hc]
  exact rectifiableDunford_norm_defect_le_geometric_sup n f hv hc hclosed h
    (hh.continuousOn.mono htrace) C Tf Tc hRf hRc

/-- The zero-defect consequence concerns genuine canonical holomorphic
values, independently of the witnesses used to define them. -/
theorem canonicalValue_compatible_of_defect_eq_zero (h : ℂ → ℂ)
    (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (Hf : Nonempty (AdmissibleCycle h Tf)) (Hc : Nonempty (AdmissibleCycle h Tc))
    (Af : AdmissibleCycle h Tf) (Ac : AdmissibleCycle h Tc)
    (hcycle : Ac.cycle = Af.cycle) (hdef : continuousDefect C Tf Tc = 0) :
    C.comp (canonicalValue h Tf Hf) = (canonicalValue h Tc Hc).comp C := by
  have hh : ContinuousOn h Af.cycle.trace := Af.holomorphic.continuousOn.mono Af.trace_domain
  have hRc : Af.cycle.trace ⊆ resolventSet ℂ Tc := by rw [← hcycle]; exact Ac.trace_resolvent
  rw [canonicalValue_eq_dunfordIntegral h Tf Hf Af, canonicalValue_eq_dunfordIntegral h Tc Hc Ac,
    hcycle]
  exact dunfordIntegral_compatible_of_defect_eq_zero Af.cycle h hh C Tf Tc Af.trace_resolvent hRc hdef
end TwoSpaces

/-- Corollary 11.10, holomorphic branch, at every actual tower depth including
zero: vanishing local defects imply canonical holomorphic compatibility. -/
theorem multilevel_canonical_holomorphic_compatible
    {X : ℕ → Type v}
    [∀ n, NormedAddCommGroup (X n)] [∀ n, NormedSpace ℂ (X n)]
    [∀ n, NormedSpace ℝ (X n)] [∀ n, IsScalarTower ℝ ℂ (X n)]
    [∀ n, CompleteSpace (X n)]
    (C : ∀ n, X (n+1) →L[ℂ] X n) (T : ∀ n, X n →L[ℂ] X n) (L : ℕ)
    (hd : ∀ k : Fin L, continuousDefect (C k.val) (T (k.val+1)) (T k.val) = 0)
    (h : ℂ → ℂ)
    (Hf : Nonempty (AdmissibleCycle h (T L))) (Hc : Nonempty (AdmissibleCycle h (T 0)))
    (Af : AdmissibleCycle h (T L)) (Ac : AdmissibleCycle h (T 0))
    (hcycle : Ac.cycle = Af.cycle) :
    (continuousSegment C (Nat.zero_le L)).comp (canonicalValue h (T L) Hf) =
      (canonicalValue h (T 0) Hc).comp (continuousSegment C (Nat.zero_le L)) := by
  apply canonicalValue_compatible_of_defect_eq_zero h _ _ _ Hf Hc Af Ac hcycle
  exact sub_eq_zero.mpr (continuous_multilevel_compatible C T L hd)

end Komorebi.PaperII.ReleaseCanonicalDefect
