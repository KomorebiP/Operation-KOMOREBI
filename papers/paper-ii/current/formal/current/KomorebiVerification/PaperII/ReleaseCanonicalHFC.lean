import KomorebiVerification.PaperII.ReleaseCycleCauchy
import Mathlib.Analysis.Normed.Algebra.Spectrum

set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.ReleaseCanonicalHFC
open Set
open scoped Topology
open Komorebi.PaperII.ReleaseAnalyticContour
open Komorebi.PaperII.ReleaseCycleWinding
open Komorebi.PaperII.ReleaseCycleCauchy

variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℂ E]
variable [NormedSpace ℝ E] [IsScalarTower ℝ ℂ E] [CompleteSpace E]

/-- The paper's admissibility data consist only of holomorphy, genuine
cycle traces, actual resolvents and actual winding integrals. No calculus
value, contour-independence equation or Cauchy conclusion is a field. -/
structure AdmissibleCycle (h : ℂ → ℂ) (T : E →L[ℂ] E) where
  domain : Set ℂ
  isOpen_domain : IsOpen domain
  holomorphic : DifferentiableOn ℂ h domain
  spectrum_subset : spectrum ℂ T ⊆ domain
  cycle : IntegralCycle
  trace_domain : cycle.trace ⊆ domain
  trace_resolvent : cycle.trace ⊆ resolventSet ℂ T
  winding_spectrum : ∀ z ∈ spectrum ℂ T, winding cycle z = 1
  winding_complement : ∀ z ∉ domain, winding cycle z = 0

/-- Actual normalized Dunford integrals are independent of every admissible
cycle and its open holomorphy domain, including on the zero operator space. -/
theorem dunfordIntegral_eq_of_admissible (h : ℂ → ℂ) (T : E →L[ℂ] E)
    (A B : AdmissibleCycle h T) :
    dunfordIntegral A.cycle h T = dunfordIntegral B.cycle h T := by
  let V : Set ℂ := (A.domain ∪ B.domain) ∩ resolventSet ℂ T
  have hV : IsOpen V :=
    (A.isOpen_domain.union B.isOpen_domain).inter (spectrum.isOpen_resolventSet T)
  have hhol : DifferentiableOn ℂ h (A.domain ∪ B.domain) := by
    intro z hz
    rcases hz with ha | hb
    · exact ((A.holomorphic z ha).differentiableAt
        (A.isOpen_domain.mem_nhds ha)).differentiableWithinAt
    · exact ((B.holomorphic z hb).differentiableAt
        (B.isOpen_domain.mem_nhds hb)).differentiableWithinAt
  have hdensity : DifferentiableOn ℂ (fun z ↦ h z • resolvent T z) V := by
    intro z hz
    have hh := (hhol z hz.1).differentiableAt
      ((A.isOpen_domain.union B.isOpen_domain).mem_nhds hz.1)
    exact (hh.smul (spectrum.hasDerivAt_resolvent_const_left hz.2).differentiableAt).differentiableWithinAt
  have htraceA : A.cycle.trace ⊆ V := fun z hz ↦
    ⟨Or.inl (A.trace_domain hz),A.trace_resolvent hz⟩
  have htraceB : B.cycle.trace ⊆ V := fun z hz ↦
    ⟨Or.inr (B.trace_domain hz),B.trace_resolvent hz⟩
  have hwind : ∀ w ∉ V, winding A.cycle w = winding B.cycle w := by
    intro w hw
    by_cases hr : w ∈ resolventSet ℂ T
    · have ho : w ∉ A.domain ∪ B.domain := fun hu ↦ hw ⟨hu,hr⟩
      rw [A.winding_complement w (fun ha ↦ ho (Or.inl ha)),
        B.winding_complement w (fun hb ↦ ho (Or.inr hb))]
    · have hs : w ∈ spectrum ℂ T := by simpa only [spectrum, mem_compl_iff] using hr
      rw [A.winding_spectrum w hs,B.winding_spectrum w hs]
  unfold dunfordIntegral
  exact congrArg (fun q : E →L[ℂ] E ↦ (2 * (Real.pi : ℂ) * Complex.I)⁻¹ • q)
    (lineIntegral_eq_of_winding A.cycle B.cycle hV hdensity htraceA htraceB hwind)

/-- The canonical value is chosen only when admissible data exist. The
theorem below proves that the choice has no effect on the resulting value. -/
def canonicalValue (h : ℂ → ℂ) (T : E →L[ℂ] E)
    (H : Nonempty (AdmissibleCycle h T)) : E →L[ℂ] E :=
  dunfordIntegral (Classical.choice H).cycle h T

theorem canonicalValue_eq_dunfordIntegral (h : ℂ → ℂ) (T : E →L[ℂ] E)
    (H : Nonempty (AdmissibleCycle h T)) (A : AdmissibleCycle h T) :
    canonicalValue h T H = dunfordIntegral A.cycle h T :=
  dunfordIntegral_eq_of_admissible h T (Classical.choice H) A

theorem canonicalValue_eq_of_witness (h : ℂ → ℂ) (T : E →L[ℂ] E)
    (H K : Nonempty (AdmissibleCycle h T)) : canonicalValue h T H = canonicalValue h T K := by
  exact dunfordIntegral_eq_of_admissible h T (Classical.choice H) (Classical.choice K)

end Komorebi.PaperII.ReleaseCanonicalHFC
