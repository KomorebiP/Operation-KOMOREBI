import KomorebiPaperVI.CanonicalJets
import Mathlib.Analysis.Complex.CauchyIntegral
import Mathlib.LinearAlgebra.Matrix.ToLin

/-! Author: Komorebi P. Canonical holomorphic functions of finite complex matrices.
The definition uses the unique finite Taylor-jet action on generalized eigenspaces.
Cauchy's formula identifies each local coefficient with an actual circle integral. -/
namespace KomorebiPaperVI.HolomorphicFinite
open Module Complex Set
open scoped Topology
open KomorebiPaperVI.CanonicalJets
set_option backward.isDefEq.respectTransparency false

section Linear
variable {V : Type*} [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]

theorem canonical_unique (A : End ℂ V) (a : ℂ → ℕ → ℂ) (B : End ℂ V)
    (hB : ∀ μ x,x∈A.maxGenEigenspace μ → B x=jet A a μ (finrank ℂ V) x) :
    B=calculus A a := by
  apply DirectSum.decompose_lhom_ext A.maxGenEigenspace
  intro μ
  ext x
  exact (hB μ x x.property).trans (calculus_on_component A a μ x x.property).symm

theorem holomorphic_on_component (A : End ℂ V) (f : ℂ → ℂ) (μ : ℂ)
    (x : V) (hx : x∈A.maxGenEigenspace μ) :
    holomorphic A f x=∑ k ∈ Finset.range (finrank ℂ V),
      (iteratedDeriv k f μ/(k.factorial:ℂ)) • (((A-μ • 1)^k) x) := by
  rw [holomorphic,calculus_on_component A _ μ x hx]
  simp [jet]

omit [FiniteDimensional ℂ V] in
theorem component_mem_spectrum (A : End ℂ V) (μ : ℂ) (x : V)
    (hx : x∈A.maxGenEigenspace μ) (hne : x≠0) : μ∈spectrum ℂ A := by
  have hv : A.HasUnifEigenvector μ ⊤ x := ⟨hx,hne⟩
  exact (hv.hasUnifEigenvalue.lt zero_lt_one).mem_spectrum

theorem calculus_spectrum_congr (A : End ℂ V) (a b : ℂ → ℕ → ℂ)
    (h : ∀ μ∈spectrum ℂ A,∀ k∈Finset.range (finrank ℂ V),a μ k=b μ k) :
    calculus A a=calculus A b := by
  apply DirectSum.decompose_lhom_ext A.maxGenEigenspace
  intro μ
  ext x
  change calculus A a x=calculus A b x
  by_cases hx : (x:V)=0
  · simp [hx]
  rw [calculus_on_component A a μ x x.property,calculus_on_component A b μ x x.property]
  simp only [jet,LinearMap.sum_apply,LinearMap.smul_apply]
  apply Finset.sum_congr rfl
  intro k hk
  rw [h μ (component_mem_spectrum A μ x x.property hx) k hk]

end Linear

noncomputable def cauchyCoefficient (f : ℂ → ℂ) (μ : ℂ) (r : ℝ) (k : ℕ) : ℂ :=
  (2*Real.pi*I)⁻¹ * ∮ z in C(μ,r),f z/(z-μ)^(k+1)

theorem cauchyCoefficient_eq (f : ℂ → ℂ) (μ : ℂ) (r : ℝ) (hr : 0 < r)
    (hf : DifferentiableOn ℂ f (Metric.closedBall μ r)) (k : ℕ) :
    cauchyCoefficient f μ r k=iteratedDeriv k f μ/(k.factorial:ℂ) := by
  have hh := hf.circleIntegral_one_div_sub_center_pow_smul hr k
  simp only [smul_eq_mul,one_div] at hh
  unfold cauchyCoefficient
  have he : (fun z => f z/(z-μ)^(k+1))=(fun z => ((z-μ)^(k+1))⁻¹*f z) := by
    ext z
    simp [div_eq_mul_inv,mul_comm]
  rw [he,hh]
  field_simp

theorem cauchyCoefficient_independent (f : ℂ → ℂ) (μ : ℂ) (r s : ℝ)
    (hr : 0 < r) (hs : 0 < s)
    (hf : DifferentiableOn ℂ f (Metric.closedBall μ r))
    (hg : DifferentiableOn ℂ f (Metric.closedBall μ s)) (k : ℕ) :
    cauchyCoefficient f μ r k=cauchyCoefficient f μ s k := by
  rw [cauchyCoefficient_eq f μ r hr hf,cauchyCoefficient_eq f μ s hs hg]

theorem admissible_circle (f : ℂ → ℂ) (U : Set ℂ) (hU : IsOpen U)
    (hf : AnalyticOnNhd ℂ f U) (μ : ℂ) (hμ : μ∈U) :
    ∃ r : ℝ,0 < r ∧ Metric.closedBall μ r ⊆ U ∧
      ∀ k,cauchyCoefficient f μ r k=iteratedDeriv k f μ/(k.factorial:ℂ) := by
  obtain ⟨r,hr,hsub⟩ := Metric.nhds_basis_closedBall.mem_iff.mp (hU.mem_nhds hμ)
  exact ⟨r,hr,hsub,fun k => cauchyCoefficient_eq f μ r hr
    (fun z hz => (hf z (hsub hz)).differentiableAt.differentiableWithinAt) k⟩

section LocalRepresentation
variable {V : Type*} [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]

theorem canonical_cauchy_representation (A : End ℂ V) (f : ℂ → ℂ) (r : ℂ → ℝ)
    (hr : ∀ μ∈spectrum ℂ A,0 < r μ)
    (hf : ∀ μ∈spectrum ℂ A,DifferentiableOn ℂ f (Metric.closedBall μ (r μ))) :
    calculus A (fun μ k => cauchyCoefficient f μ (r μ) k)=holomorphic A f := by
  apply calculus_spectrum_congr
  intro μ hμ k _
  exact cauchyCoefficient_eq f μ (r μ) (hr μ hμ) (hf μ hμ) k

theorem canonical_contours_exist (A : End ℂ V) (f : ℂ → ℂ) (U : Set ℂ)
    (hU : IsOpen U) (hf : AnalyticOnNhd ℂ f U) (hA : spectrum ℂ A ⊆ U) :
    ∃ r : ℂ → ℝ,(∀ μ∈spectrum ℂ A,0 < r μ ∧ Metric.closedBall μ (r μ) ⊆ U) ∧
      calculus A (fun μ k => cauchyCoefficient f μ (r μ) k)=holomorphic A f := by
  classical
  have he (μ : ℂ) : ∃ r : ℝ,0 < r ∧
      (μ∈spectrum ℂ A → Metric.closedBall μ r ⊆ U) := by
    by_cases hm : μ∈spectrum ℂ A
    · obtain ⟨r,hr,hsub,_⟩ := admissible_circle f U hU hf μ (hA hm)
      exact ⟨r,hr,fun _ => hsub⟩
    · exact ⟨1,zero_lt_one,fun h => (hm h).elim⟩
  choose r hr hsub using he
  refine ⟨r,fun μ hμ => ⟨hr μ,hsub μ hμ⟩,?_⟩
  apply canonical_cauchy_representation A f r (fun μ _ => hr μ)
  intro μ hμ z hz
  exact (hf z (hsub μ hμ hz)).differentiableAt.differentiableWithinAt

theorem canonical_contours_independent (A : End ℂ V) (f : ℂ → ℂ) (r s : ℂ → ℝ)
    (hr : ∀ μ∈spectrum ℂ A,0 < r μ) (hs : ∀ μ∈spectrum ℂ A,0 < s μ)
    (hf : ∀ μ∈spectrum ℂ A,DifferentiableOn ℂ f (Metric.closedBall μ (r μ)))
    (hg : ∀ μ∈spectrum ℂ A,DifferentiableOn ℂ f (Metric.closedBall μ (s μ))) :
    calculus A (fun μ k => cauchyCoefficient f μ (r μ) k)=
      calculus A (fun μ k => cauchyCoefficient f μ (s μ) k) := by
  rw [canonical_cauchy_representation A f r hr hf,canonical_cauchy_representation A f s hs hg]

end LocalRepresentation

section Matrix
variable {I J : Type*} [Fintype I] [Fintype J] [DecidableEq I] [DecidableEq J]

noncomputable def matrixFunction (A : Matrix I I ℂ) (f : ℂ → ℂ) : Matrix I I ℂ :=
  LinearMap.toMatrix' (holomorphic A.toLin' f)

theorem matrix_holomorphic_naturality (A : Matrix I I ℂ) (B : Matrix J J ℂ)
    (C : Matrix J I ℂ) (h : C*A=B*C) (f : ℂ → ℂ) :
    C*matrixFunction A f=matrixFunction B f*C := by
  have hh : B.toLin'.comp C.toLin'=C.toLin'.comp A.toLin' := by
    rw [← Matrix.toLin'_mul,← Matrix.toLin'_mul,h]
  have hc := holomorphic_naturality A.toLin' B.toLin' C.toLin' hh f
  have hm := congrArg LinearMap.toMatrix' hc
  simpa only [LinearMap.toMatrix'_comp,LinearMap.toMatrix'_toLin',matrixFunction] using hm

end Matrix
end KomorebiPaperVI.HolomorphicFinite
