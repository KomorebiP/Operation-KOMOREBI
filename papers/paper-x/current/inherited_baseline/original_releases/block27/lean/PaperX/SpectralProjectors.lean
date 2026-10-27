import Mathlib.LinearAlgebra.Eigenspace.Minpoly
import Mathlib.LinearAlgebra.Eigenspace.Semisimple
import Mathlib.LinearAlgebra.Trace
import Mathlib.Tactic

/-! Actual Lagrange spectral projectors. Diagonalizability is the spanning of
actual eigenspaces. No eigenbasis or desired projector is assumed supplied. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.SpectralProjectors

open scoped BigOperators Polynomial
open Polynomial LinearMap Module.End
attribute [local instance] Classical.propDecidable
universe u v
variable {K : Type u} [Field K] {V : Type v} [AddCommGroup V] [Module K V]

/-- Exact finite-spectrum Lagrange selector; absent targets select zero. -/
def selector (s : Finset K) (a : K) : K[X] := by
  classical
  exact if a ∈ s then ∏ b ∈ s.erase a, C ((a-b)⁻¹) * (X-C b) else 0

theorem selector_eval_self (s : Finset K) {a : K} (ha : a ∈ s) :
    (selector s a).eval a = 1 := by
  classical
  simp only [selector, ite_eq_left ha, eval_prod, eval_mul, eval_C, eval_sub, eval_X]
  apply Finset.prod_eq_one
  intro b hb
  exact inv_mul_cancel₀ (sub_ne_zero.mpr (Finset.ne_of_mem_erase hb).symm)

theorem selector_eval_other (s : Finset K) {a b : K} (hb : b ∈ s) (hne : b ≠ a) :
    (selector s a).eval b = 0 := by
  classical
  by_cases ha : a ∈ s
  · simp only [selector, ite_eq_left ha, eval_prod, eval_mul, eval_C, eval_sub, eval_X]
    exact Finset.prod_eq_zero (Finset.mem_erase.mpr ⟨hne, hb⟩) (by simp)
  · simp [selector, ha]

theorem selector_eval (s : Finset K) {a b : K} (hb : b ∈ s) :
    (selector s a).eval b = if b = a then 1 else 0 := by
  classical
  by_cases h : b = a
  · subst b
    simp [selector_eval_self s hb]
  · simp [h, selector_eval_other s hb h]

variable [FiniteDimensional K V]

/-- The actual finite eigenvalue set of T. -/
def eigenvalues (T : Module.End K V) : Finset K := T.finite_hasEigenvalue.toFinset

theorem mem_eigenvalues (T : Module.End K V) (a : K) :
    a ∈ eigenvalues T ↔ T.HasEigenvalue a := by
  classical
  simp [eigenvalues]

/-- Evaluate the Lagrange selector on the actual operator. -/
def spectral (T : Module.End K V) (a : K) : Module.End K V :=
  aeval T (selector (eigenvalues T) a)

theorem spectral_absent (T : Module.End K V) (a : K) (ha : ¬ T.HasEigenvalue a) :
    spectral T a = 0 := by
  classical
  simp [spectral, selector, mem_eigenvalues, ha]

theorem spectral_on_eigenvector (T : Module.End K V) (a b : K) (x : V)
    (hx : T x = b • x) : spectral T a x = if b = a then x else 0 := by
  classical
  by_cases hz : x = 0
  · subst x; simp
  have hb : b ∈ eigenvalues T := (mem_eigenvalues T b).2
    (T.hasEigenvalue_of_hasEigenvector ⟨mem_eigenspace_iff.mpr hx, hz⟩)
  rw [spectral, aeval_apply_of_mem_apply_eq_smul hx, selector_eval _ hb]
  split_ifs <;> simp

/-- Diagonalizability in the coefficient field: actual eigenspaces span V. -/
def Split (T : Module.End K V) : Prop := (⨆ a : K, T.eigenspace a) = ⊤

theorem spectral_maps_into (T : Module.End K V) (hT : Split T) (a : K) (x : V) :
    spectral T a x ∈ T.eigenspace a := by
  have hle : (⨆ b : K, T.eigenspace b) ≤ (T.eigenspace a).comap (spectral T a) := by
    refine iSup_le fun b => ?_
    intro y hy
    change spectral T a y ∈ T.eigenspace a
    rw [spectral_on_eigenvector T a b y (mem_eigenspace_iff.mp hy)]
    split_ifs with h
    · simpa [h] using hy
    · exact Submodule.zero_mem _
  rw [hT] at hle
  exact hle (Submodule.mem_top)

theorem spectral_isProj (T : Module.End K V) (hT : Split T) (a : K) :
    LinearMap.IsProj (T.eigenspace a) (spectral T a) := by
  refine ⟨spectral_maps_into T hT a, ?_⟩
  intro x hx
  simpa using spectral_on_eigenvector T a a x (mem_eigenspace_iff.mp hx)

theorem spectral_idempotent (T : Module.End K V) (hT : Split T) (a : K) :
    IsIdempotentElem (spectral T a) := (spectral_isProj T hT a).isIdempotentElem

theorem spectral_range (T : Module.End K V) (hT : Split T) (a : K) :
    LinearMap.range (spectral T a) = T.eigenspace a := (spectral_isProj T hT a).range

/-- The standard semisimple algebraically closed setting supplies Split. -/
theorem split_of_semisimple [IsAlgClosed K] (T : Module.End K V) (hT : T.IsSemisimple) :
    Split T := hT.iSup_eigenspace_eq_top

omit [FiniteDimensional K V] in
/-- Commutation survives evaluation of a polynomial in one operator. -/
theorem polynomial_commute_right (T U : Module.End K V) (h : Commute T U) (p : K[X]) :
    Commute T (aeval U p) := by
  induction p using Polynomial.induction_on' with
  | add p q hp hq => simpa only [map_add] using hp.add_right hq
  | monomial n c =>
      rw [aeval_monomial]
      exact (Algebra.commute_algebraMap_right c T).mul_right (h.pow_right n)

theorem spectral_commute (T U : Module.End K V) (h : Commute T U) (a b : K) :
    Commute (spectral T a) (spectral U b) := by
  exact (polynomial_commute_right _ _
    (polynomial_commute_right T U h (selector (eigenvalues U) b)).symm
    (selector (eigenvalues T) a)).symm

end PaperX.SpectralProjectors
