import PaperXI.CyclicPolynomial
import Mathlib.LinearAlgebra.Basis.SMul
import Mathlib.GroupTheory.Perm.Fin

/-! Transfer formulas in an actual basis, including independent rescalings. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CycleCoordinates
open Polynomial
open PaperXI.CyclicPolynomial
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

theorem basis_eq_powers (F : Module.End K V) {n : ℕ} (hn : 0 < n)
    (b : Module.Basis (Fin n) K V)
    (hstep : ∀ (i : Fin n) (hi : (i : ℕ) + 1 < n), F (b i) = b ⟨i + 1, hi⟩) :
    ∀ i : Fin n, b i = (F ^ (i : ℕ)) (b ⟨0, hn⟩) := by
  have aux : ∀ k (hk : k < n), b ⟨k, hk⟩ = (F ^ k) (b ⟨0, hn⟩) := by
    intro k
    induction k with
    | zero => intro hk; simp
    | succ k ih =>
      intro hk
      rw [← hstep ⟨k, by omega⟩ hk, ih (by omega), pow_succ']
      rfl
  intro i
  exact aux i i.isLt

theorem closing_of_last_step (F : Module.End K V) {n : ℕ} (hn : 0 < n)
    (b : Module.Basis (Fin n) K V)
    (hstep : ∀ (i : Fin n) (hi : (i : ℕ) + 1 < n), F (b i) = b ⟨i + 1, hi⟩)
    (c : K) (hlast : F (b ⟨n - 1, by omega⟩) = c • b ⟨0, hn⟩) :
    (F ^ n) (b ⟨0, hn⟩) = c • b ⟨0, hn⟩ := by
  have hb := basis_eq_powers F hn b hstep ⟨n - 1, by omega⟩
  have he : n = (n - 1) + 1 := by omega
  calc
    (F ^ n) (b ⟨0, hn⟩) = F ((F ^ (n - 1)) (b ⟨0, hn⟩)) := by
      have hp : F ^ n = F * F ^ (n - 1) := by
        conv_lhs => rw [he, pow_succ']
      rw [hp]
      rfl
    _ = F (b ⟨n - 1, by omega⟩) := congrArg F hb.symm
    _ = c • b ⟨0, hn⟩ := hlast

/-- Proposition 4.4 in its stated cyclic-coordinate form. -/
theorem cycle_formula [FiniteDimensional K V] (F : Module.End K V) {n : ℕ}
    (hn : 0 < n) (b : Module.Basis (Fin n) K V)
    (hstep : ∀ (i : Fin n) (hi : (i : ℕ) + 1 < n), F (b i) = b ⟨i + 1, hi⟩)
    (c : K) (hlast : F (b ⟨n - 1, by omega⟩) = c • b ⟨0, hn⟩) :
    F.charpoly = X ^ n - C c ∧ F.det = (-1) ^ (n - 1) * c := by
  have hb := basis_eq_powers F hn b hstep
  have hc := closing_of_last_step F hn b hstep c hlast
  exact ⟨charpoly_of_orbit_basis F hn b _ hb c hc,
    det_of_orbit_basis F hn b _ hb c hc⟩

theorem rescaled_entry {ι : Type*} [Fintype ι] [DecidableEq ι]
    (F : Module.End K V) (b : Module.Basis ι K V) (w : ι → Kˣ) (i j : ι) :
    LinearMap.toMatrix (b.unitsSMul w) (b.unitsSMul w) F i j =
      (w i : K)⁻¹ * LinearMap.toMatrix b b F i j * (w j : K) := by
  simp [LinearMap.toMatrix_apply, Module.Basis.unitsSMul_apply,
    Module.Basis.repr_unitsSMul, Units.smul_def, mul_comm]

theorem rescaled_charpoly [FiniteDimensional K V]
    {ι : Type*} [Fintype ι] [DecidableEq ι]
    (F : Module.End K V) (b : Module.Basis ι K V) (w : ι → Kˣ) :
    (LinearMap.toMatrix (b.unitsSMul w) (b.unitsSMul w) F).charpoly =
      (LinearMap.toMatrix b b F).charpoly := by simp

theorem rescaled_det {ι : Type*} [Fintype ι] [DecidableEq ι]
    (F : Module.End K V) (b : Module.Basis ι K V) (w : ι → Kˣ) :
    (LinearMap.toMatrix (b.unitsSMul w) (b.unitsSMul w) F).det =
      (LinearMap.toMatrix b b F).det := by
  rw [LinearMap.det_toMatrix, LinearMap.det_toMatrix]

theorem cycle_orientation (n : ℕ) : Equiv.Perm.sign (finRotate n) = (-1) ^ (n - 1) :=
  sign_finRotate n

theorem cycle_local_polynomial [FiniteDimensional K V] (F : Module.End K V) {n : ℕ}
    (hn : 0 < n) (b : Module.Basis (Fin n) K V)
    (hstep : ∀ (i : Fin n) (hi : (i : ℕ) + 1 < n), F (b i) = b ⟨i + 1, hi⟩)
    (c : K) (hlast : F (b ⟨n - 1, by omega⟩) = c • b ⟨0, hn⟩) :
    Matrix.det (1 - (X : K[X]) • (LinearMap.toMatrix b b F).map C) =
      1 - C c * X ^ n := by
  change (LinearMap.toMatrix b b F).charpolyRev = _
  exact local_polynomial_of_orbit_basis F hn b _ (basis_eq_powers F hn b hstep) c
    (closing_of_last_step F hn b hstep c hlast)

theorem rescaled_cycle_formula [FiniteDimensional K V] (F : Module.End K V) {n : ℕ}
    (hn : 0 < n) (b : Module.Basis (Fin n) K V)
    (hstep : ∀ (i : Fin n) (hi : (i : ℕ) + 1 < n), F (b i) = b ⟨i + 1, hi⟩)
    (c : K) (hlast : F (b ⟨n - 1, by omega⟩) = c • b ⟨0, hn⟩)
    (w : Fin n → Kˣ) :
    (LinearMap.toMatrix (b.unitsSMul w) (b.unitsSMul w) F).charpoly = X ^ n - C c ∧
    (LinearMap.toMatrix (b.unitsSMul w) (b.unitsSMul w) F).det = (-1) ^ (n - 1) * c := by
  rw [LinearMap.charpoly_toMatrix, LinearMap.det_toMatrix]
  exact cycle_formula F hn b hstep c hlast

end PaperXI.CycleCoordinates
