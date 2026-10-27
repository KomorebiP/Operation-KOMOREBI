import KomorebiVerification.PaperII.ReleaseCanonicalHFC

set_option autoImplicit false
set_option backward.isDefEq.respectTransparency false
set_option maxHeartbeats 1000000
noncomputable section
namespace Komorebi.PaperII.ReleaseCanonicalNaturality
open Set Filter
open scoped Topology Classical
open Komorebi.PaperII.TypedLinearDefects
open Komorebi.PaperII.ReleaseAnalyticContour
open Komorebi.PaperII.ReleaseCycleWinding
open Komorebi.PaperII.ReleaseCycleCauchy
open Komorebi.PaperII.ReleaseCanonicalHFC

variable {Ef Ec : Type*}
variable [NormedAddCommGroup Ef] [NormedAddCommGroup Ec]
variable [NormedSpace ℂ Ef] [NormedSpace ℂ Ec]
variable [NormedSpace ℝ Ef] [NormedSpace ℝ Ec]
variable [IsScalarTower ℝ ℂ Ef] [IsScalarTower ℝ ℂ Ec]
variable [CompleteSpace Ef] [CompleteSpace Ec]

omit [NormedSpace ℝ Ef] [NormedSpace ℝ Ec]
  [IsScalarTower ℝ ℂ Ef] [IsScalarTower ℝ ℂ Ec]
  [CompleteSpace Ef] [CompleteSpace Ec] in
theorem resolvent_natural_of_defect_zero
    (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (hdef : continuousDefect C Tf Tc = 0) {z : ℂ}
    (hf : z ∈ resolventSet ℂ Tf) (hc : z ∈ resolventSet ℂ Tc) :
    C.comp (resolvent Tf z) = (resolvent Tc z).comp C := by
  apply sub_eq_zero.mp
  rw [resolvent_defect_actual C Tf Tc z hf hc,hdef]
  simp

omit [NormedSpace ℝ Ef] [NormedSpace ℝ Ec]
  [IsScalarTower ℝ ℂ Ef] [IsScalarTower ℝ ℂ Ec]
  [CompleteSpace Ef] [CompleteSpace Ec] in
/-- The intertwining resolvents agree on their overlap, so they define one
holomorphic map on the union of the two resolvent sets. -/
def gluedResolvent (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (z : ℂ) : Ef →L[ℂ] Ec :=
  if z ∈ resolventSet ℂ Tf then C.comp (resolvent Tf z) else (resolvent Tc z).comp C

omit [NormedSpace ℝ Ef] [NormedSpace ℝ Ec]
  [IsScalarTower ℝ ℂ Ef] [IsScalarTower ℝ ℂ Ec]
  [CompleteSpace Ef] [CompleteSpace Ec] in
theorem gluedResolvent_eq_left
    (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec) {z : ℂ}
    (hz : z ∈ resolventSet ℂ Tf) :
    gluedResolvent C Tf Tc z = C.comp (resolvent Tf z) := by
  simp [gluedResolvent,hz]

omit [NormedSpace ℝ Ef] [NormedSpace ℝ Ec]
  [IsScalarTower ℝ ℂ Ef] [IsScalarTower ℝ ℂ Ec]
  [CompleteSpace Ef] [CompleteSpace Ec] in
theorem gluedResolvent_eq_right
    (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (hdef : continuousDefect C Tf Tc = 0) {z : ℂ}
    (hz : z ∈ resolventSet ℂ Tc) :
    gluedResolvent C Tf Tc z = (resolvent Tc z).comp C := by
  unfold gluedResolvent
  split_ifs with hf
  · exact resolvent_natural_of_defect_zero C Tf Tc hdef hf hz
  · rfl

omit [NormedSpace ℝ Ef] [NormedSpace ℝ Ec]
  [IsScalarTower ℝ ℂ Ef] [IsScalarTower ℝ ℂ Ec] in
theorem differentiableOn_gluedResolvent
    (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (hdef : continuousDefect C Tf Tc = 0) :
    DifferentiableOn ℂ (gluedResolvent C Tf Tc)
      (resolventSet ℂ Tf ∪ resolventSet ℂ Tc) := by
  let post : (Ef →L[ℂ] Ef) →L[ℂ] (Ef →L[ℂ] Ec) :=
    ContinuousLinearMap.compL ℂ Ef Ef Ec C
  let pre : (Ec →L[ℂ] Ec) →L[ℂ] (Ef →L[ℂ] Ec) :=
    (ContinuousLinearMap.compL ℂ Ef Ec Ec).flip C
  intro z hz
  rcases hz with hf | hc
  · have hd := post.hasFDerivAt.comp_hasDerivAt z
      (spectrum.hasDerivAt_resolvent_const_left hf)
    apply DifferentiableAt.differentiableWithinAt
    apply hd.differentiableAt.congr_of_eventuallyEq
    filter_upwards [(spectrum.isOpen_resolventSet Tf).mem_nhds hf] with w hw
    exact gluedResolvent_eq_left C Tf Tc hw
  · have hd := pre.hasFDerivAt.comp_hasDerivAt z
      (spectrum.hasDerivAt_resolvent_const_left hc)
    apply DifferentiableAt.differentiableWithinAt
    apply hd.differentiableAt.congr_of_eventuallyEq
    filter_upwards [(spectrum.isOpen_resolventSet Tc).mem_nhds hc] with w hw
    exact gluedResolvent_eq_right C Tf Tc hdef hw

/-- Canonical intertwining uses independently admissible cycles and domains.
No contour common to the two operator spaces is required. -/
theorem dunfordIntegral_natural_of_admissible
    (h : ℂ → ℂ) (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (Af : AdmissibleCycle h Tf) (Ac : AdmissibleCycle h Tc)
    (hdef : continuousDefect C Tf Tc = 0) :
    C.comp (dunfordIntegral Af.cycle h Tf) =
      (dunfordIntegral Ac.cycle h Tc).comp C := by
  let V : Set ℂ := (Af.domain ∪ Ac.domain) ∩
    (resolventSet ℂ Tf ∪ resolventSet ℂ Tc)
  have hV : IsOpen V := (Af.isOpen_domain.union Ac.isOpen_domain).inter
    ((spectrum.isOpen_resolventSet Tf).union (spectrum.isOpen_resolventSet Tc))
  have hh : DifferentiableOn ℂ h (Af.domain ∪ Ac.domain) := by
    intro z hz
    rcases hz with hf | hc
    · exact ((Af.holomorphic z hf).differentiableAt
        (Af.isOpen_domain.mem_nhds hf)).differentiableWithinAt
    · exact ((Ac.holomorphic z hc).differentiableAt
        (Ac.isOpen_domain.mem_nhds hc)).differentiableWithinAt
  have hdensity : DifferentiableOn ℂ (fun z => h z • gluedResolvent C Tf Tc z) V := by
    intro z hz
    have hhz := (hh z hz.1).differentiableAt
      ((Af.isOpen_domain.union Ac.isOpen_domain).mem_nhds hz.1)
    have hrz := (differentiableOn_gluedResolvent C Tf Tc hdef z hz.2).differentiableAt
      (((spectrum.isOpen_resolventSet Tf).union
        (spectrum.isOpen_resolventSet Tc)).mem_nhds hz.2)
    exact (hhz.smul hrz).differentiableWithinAt
  have htracef : Af.cycle.trace ⊆ V :=
    fun z hz => ⟨Or.inl (Af.trace_domain hz),Or.inl (Af.trace_resolvent hz)⟩
  have htracec : Ac.cycle.trace ⊆ V :=
    fun z hz => ⟨Or.inr (Ac.trace_domain hz),Or.inr (Ac.trace_resolvent hz)⟩
  have hwind : ∀ w ∉ V, winding Af.cycle w = winding Ac.cycle w := by
    intro w hw
    by_cases hr : w ∈ resolventSet ℂ Tf ∪ resolventSet ℂ Tc
    · have ho : w ∉ Af.domain ∪ Ac.domain := fun hu => hw ⟨hu,hr⟩
      rw [Af.winding_complement w (fun ha => ho (Or.inl ha)),
        Ac.winding_complement w (fun ha => ho (Or.inr ha))]
    · have hsf : w ∈ spectrum ℂ Tf := by
        simpa only [spectrum,mem_compl_iff] using (fun hf => hr (Or.inl hf))
      have hsc : w ∈ spectrum ℂ Tc := by
        simpa only [spectrum,mem_compl_iff] using (fun hc => hr (Or.inr hc))
      rw [Af.winding_spectrum w hsf,Ac.winding_spectrum w hsc]
  have hcompare := lineIntegral_eq_of_winding Af.cycle Ac.cycle hV hdensity htracef htracec hwind
  let post : (Ef →L[ℂ] Ef) →L[ℂ] (Ef →L[ℂ] Ec) :=
    ContinuousLinearMap.compL ℂ Ef Ef Ec C
  let pre : (Ec →L[ℂ] Ec) →L[ℂ] (Ef →L[ℂ] Ec) :=
    (ContinuousLinearMap.compL ℂ Ef Ec Ec).flip C
  have hff : ContinuousOn (fun z => h z • resolvent Tf z) Af.cycle.trace :=
    (Af.holomorphic.continuousOn.mono Af.trace_domain).smul
      (continuousOn_resolvent_trace Af.cycle Tf Af.trace_resolvent)
  have hcc : ContinuousOn (fun z => h z • resolvent Tc z) Ac.cycle.trace :=
    (Ac.holomorphic.continuousOn.mono Ac.trace_domain).smul
      (continuousOn_resolvent_trace Ac.cycle Tc Ac.trace_resolvent)
  have hleft : Af.cycle.lineIntegral (fun z => h z • gluedResolvent C Tf Tc z) =
      post (Af.cycle.lineIntegral (fun z => h z • resolvent Tf z)) := by
    rw [← Af.cycle.lineIntegral_map post hff]
    apply lineIntegral_congr_on_trace Af.cycle
    intro z hz
    change h z • gluedResolvent C Tf Tc z = post (h z • resolvent Tf z)
    rw [gluedResolvent_eq_left C Tf Tc (Af.trace_resolvent hz)]
    simp only [map_smul]
    rfl
  have hright : Ac.cycle.lineIntegral (fun z => h z • gluedResolvent C Tf Tc z) =
      pre (Ac.cycle.lineIntegral (fun z => h z • resolvent Tc z)) := by
    rw [← Ac.cycle.lineIntegral_map pre hcc]
    apply lineIntegral_congr_on_trace Ac.cycle
    intro z hz
    change h z • gluedResolvent C Tf Tc z = pre (h z • resolvent Tc z)
    rw [gluedResolvent_eq_right C Tf Tc hdef (Ac.trace_resolvent hz)]
    simp only [map_smul]
    rfl
  rw [hleft,hright] at hcompare
  change post ((2 * (Real.pi : ℂ) * Complex.I)⁻¹ •
      Af.cycle.lineIntegral (fun z => h z • resolvent Tf z)) =
    pre ((2 * (Real.pi : ℂ) * Complex.I)⁻¹ •
      Ac.cycle.lineIntegral (fun z => h z • resolvent Tc z))
  rw [map_smul,map_smul,hcompare]

/-- Naturality of the canonical holomorphic functional calculus for zero
defect, with separate admissibility witnesses for the two operators. -/
theorem canonicalValue_natural_of_defect_zero
    (h : ℂ → ℂ) (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (Hf : Nonempty (AdmissibleCycle h Tf)) (Hc : Nonempty (AdmissibleCycle h Tc))
    (hdef : continuousDefect C Tf Tc = 0) :
    C.comp (canonicalValue h Tf Hf) = (canonicalValue h Tc Hc).comp C := by
  exact dunfordIntegral_natural_of_admissible h C Tf Tc
    (Classical.choice Hf) (Classical.choice Hc) hdef

theorem canonicalValue_compatible_of_defect_eq_zero
    (h : ℂ → ℂ) (C : Ef →L[ℂ] Ec) (Tf : Ef →L[ℂ] Ef) (Tc : Ec →L[ℂ] Ec)
    (Hf : Nonempty (AdmissibleCycle h Tf)) (Hc : Nonempty (AdmissibleCycle h Tc))
    (hdef : continuousDefect C Tf Tc = 0) :
    C.comp (canonicalValue h Tf Hf) = (canonicalValue h Tc Hc).comp C :=
  canonicalValue_natural_of_defect_zero h C Tf Tc Hf Hc hdef

end Komorebi.PaperII.ReleaseCanonicalNaturality
