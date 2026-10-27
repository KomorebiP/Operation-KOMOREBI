import Mathlib.LinearAlgebra.Eigenspace.Triangularizable
import Mathlib.Algebra.DirectSum.Decomposition
import Mathlib.Analysis.Calculus.IteratedDeriv.Defs
import Mathlib.Analysis.Complex.Polynomial.Basic

/-! Author: Komorebi P. Canonical finite-dimensional matrix functions from Taylor jets. -/
namespace KomorebiPaperVI.CanonicalJets
open Module
set_option backward.isDefEq.respectTransparency false
variable {V W : Type*} [AddCommGroup V] [Module ℂ V] [FiniteDimensional ℂ V]
  [AddCommGroup W] [Module ℂ W] [FiniteDimensional ℂ W]

noncomputable instance decomposition (A : End ℂ V) :
    DirectSum.Decomposition A.maxGenEigenspace := by
  classical
  exact (DirectSum.isInternal_submodule_of_iSupIndep_of_iSup_eq_top
    A.independent_maxGenEigenspace A.iSup_maxGenEigenspace_eq_top).chooseDecomposition

noncomputable def jet (A : End ℂ V) (a : ℂ → ℕ → ℂ) (μ : ℂ) (n : ℕ) : End ℂ V :=
  ∑ k ∈ Finset.range n, a μ k • (A-μ • 1)^k

noncomputable def calculus (A : End ℂ V) (a : ℂ → ℕ → ℂ) : End ℂ V := by
  classical
  exact (DirectSum.toModule ℂ ℂ V (fun μ =>
    (jet A a μ (finrank ℂ V)).comp (A.maxGenEigenspace μ).subtype)).comp
    (DirectSum.decomposeLinearEquiv A.maxGenEigenspace).toLinearMap

theorem calculus_on_component (A : End ℂ V) (a : ℂ → ℕ → ℂ) (μ : ℂ)
    (x : V) (hx : x ∈ A.maxGenEigenspace μ) :
    calculus A a x=jet A a μ (finrank ℂ V) x := by
  classical
  unfold calculus
  dsimp only [LinearMap.comp_apply,LinearEquiv.coe_toLinearMap]
  rw [DirectSum.decomposeLinearEquiv_apply_coe A.maxGenEigenspace μ ⟨x,hx⟩,
    DirectSum.toModule_lof]
  rfl

theorem power_kills (A : End ℂ V) (μ : ℂ) (x : V)
    (hx : x ∈ A.maxGenEigenspace μ) (k : ℕ) (hk : finrank ℂ V ≤ k) :
    ((A-μ • 1)^k) x=0 := by
  have h := A.genEigenspace_le_genEigenspace_finrank μ ⊤ hx
  have h' : x ∈ A.genEigenspace μ k :=
    (A.genEigenspace μ).monotone (by exact_mod_cast hk) h
  exact LinearMap.mem_ker.mp (Module.End.mem_genEigenspace_nat.mp h')

theorem jet_stable (A : End ℂ V) (a : ℂ → ℕ → ℂ) (μ : ℂ) (x : V)
    (hx : x ∈ A.maxGenEigenspace μ) (n : ℕ) (hn : finrank ℂ V ≤ n) :
    jet A a μ n x=jet A a μ (finrank ℂ V) x := by
  classical
  unfold jet
  simp only [LinearMap.sum_apply,LinearMap.smul_apply]
  symm
  apply Finset.sum_subset (Finset.range_mono hn)
  intro k _ hk
  rw [power_kills A μ x hx k (by simpa using hk),smul_zero]

omit [FiniteDimensional ℂ V] [FiniteDimensional ℂ W] in
theorem shift_intertwines (A : End ℂ V) (B : End ℂ W) (C : V →ₗ[ℂ] W)
    (h : B.comp C=C.comp A) (μ : ℂ) (x : V) :
    C ((A-μ • 1) x)=(B-μ • 1) (C x) := by
  have hh := LinearMap.congr_fun h x
  simpa using hh.symm

omit [FiniteDimensional ℂ V] [FiniteDimensional ℂ W] in
theorem power_intertwines (A : End ℂ V) (B : End ℂ W) (C : V →ₗ[ℂ] W)
    (h : B.comp C=C.comp A) (μ : ℂ) (k : ℕ) (x : V) :
    C (((A-μ • 1)^k) x)=((B-μ • 1)^k) (C x) := by
  induction k generalizing x with
  | zero => simp
  | succ k ih =>
    rw [pow_succ',pow_succ',Module.End.mul_apply,Module.End.mul_apply,
      shift_intertwines A B C h μ,ih]

omit [FiniteDimensional ℂ V] [FiniteDimensional ℂ W] in
theorem jet_intertwines (A : End ℂ V) (B : End ℂ W) (C : V →ₗ[ℂ] W)
    (h : B.comp C=C.comp A) (a : ℂ → ℕ → ℂ) (μ : ℂ) (n : ℕ) (x : V) :
    C (jet A a μ n x)=jet B a μ n (C x) := by
  simp only [jet,LinearMap.sum_apply,LinearMap.smul_apply,map_sum,map_smul,
    power_intertwines A B C h μ]

theorem canonical_naturality (A : End ℂ V) (B : End ℂ W) (C : V →ₗ[ℂ] W)
    (h : B.comp C=C.comp A) (a : ℂ → ℕ → ℂ) :
    C.comp (calculus A a)=(calculus B a).comp C := by
  apply DirectSum.decompose_lhom_ext A.maxGenEigenspace
  intro μ
  ext x
  have hx := Module.End.mapsTo_genEigenspace_of_comp C h μ ⊤ x.property
  change C (calculus A a x)=calculus B a (C x)
  rw [calculus_on_component A a μ x x.property,
    calculus_on_component B a μ (C x) hx,
    ← jet_stable A a μ x x.property (max (finrank ℂ V) (finrank ℂ W)) (le_max_left _ _),
    ← jet_stable B a μ (C x) hx (max (finrank ℂ V) (finrank ℂ W)) (le_max_right _ _)]
  exact jet_intertwines A B C h a μ _ x

noncomputable def holomorphic (A : End ℂ V) (f : ℂ → ℂ) : End ℂ V :=
  calculus A (fun μ k => iteratedDeriv k f μ / k.factorial)

theorem holomorphic_naturality (A : End ℂ V) (B : End ℂ W) (C : V →ₗ[ℂ] W)
    (h : B.comp C=C.comp A) (f : ℂ → ℂ) :
    C.comp (holomorphic A f)=(holomorphic B f).comp C :=
  canonical_naturality A B C h _

end KomorebiPaperVI.CanonicalJets
