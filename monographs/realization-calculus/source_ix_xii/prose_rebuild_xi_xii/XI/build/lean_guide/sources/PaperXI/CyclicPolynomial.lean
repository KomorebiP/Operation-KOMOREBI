import Mathlib.LinearAlgebra.Charpoly.ToMatrix
import Mathlib.Algebra.Polynomial.Degree.IsMonicOfDegree
import Mathlib.Tactic

/-! Characteristic polynomials from a proved cyclic basis. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CyclicPolynomial
open scoped BigOperators
open Polynomial
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

theorem aeval_apply_eq_sum (F : Module.End K V) (v : V) {p : K[X]} {n : ℕ}
    (hp : p.natDegree < n) :
    aeval F p v = ∑ i : Fin n, p.coeff i • (F ^ (i : ℕ)) v := by
  rw [aeval_eq_sum_range' hp]
  simp only [LinearMap.sum_apply]
  exact (Fin.sum_univ_eq_sum_range _ _).symm

theorem no_short_annihilator (F : Module.End K V) (v : V) {n : ℕ}
    (hli : LinearIndependent K (fun i : Fin n => (F ^ (i : ℕ)) v))
    {p : K[X]} (hp : p.natDegree < n) (hzero : aeval F p v = 0) : p = 0 := by
  classical
  rw [aeval_apply_eq_sum F v hp] at hzero
  have hc := Fintype.linearIndependent_iff.mp hli (fun i => p.coeff i) hzero
  ext k
  by_cases hk : k < n
  · exact hc ⟨k, hk⟩
  · simp [coeff_eq_zero_of_natDegree_lt (by omega : p.natDegree < k)]

theorem charpoly_of_orbit_basis [FiniteDimensional K V] (F : Module.End K V)
    {n : ℕ} (hn : 0 < n) (b : Module.Basis (Fin n) K V) (v : V)
    (hb : ∀ i : Fin n, b i = (F ^ (i : ℕ)) v) (c : K)
    (hclose : (F ^ n) v = c • v) : F.charpoly = X ^ n - C c := by
  have hdim : Module.finrank K V = n := by simpa using Module.finrank_eq_card_basis b
  have hli : LinearIndependent K (fun i : Fin n => (F ^ (i : ℕ)) v) := by
    simpa only [← hb] using b.linearIndependent
  have hm1 : IsMonicOfDegree F.charpoly n := ⟨by simpa [hdim] using F.charpoly_natDegree, F.charpoly_monic⟩
  have hm2 : IsMonicOfDegree (X ^ n - C c : K[X]) n :=
    ⟨natDegree_X_pow_sub_C, monic_X_pow_sub_C c (Nat.ne_of_gt hn)⟩
  apply sub_eq_zero.mp
  apply no_short_annihilator F v hli (hm1.natDegree_sub_lt (Nat.ne_of_gt hn) hm2)
  simp [map_sub, map_pow, aeval_X, aeval_C, F.aeval_self_charpoly, hclose]

theorem det_of_orbit_basis [FiniteDimensional K V] (F : Module.End K V)
    {n : ℕ} (hn : 0 < n) (b : Module.Basis (Fin n) K V) (v : V)
    (hb : ∀ i : Fin n, b i = (F ^ (i : ℕ)) v) (c : K)
    (hclose : (F ^ n) v = c • v) : F.det = (-1) ^ (n - 1) * c := by
  classical
  rw [← LinearMap.det_toMatrix b F, Matrix.det_eq_sign_charpoly_coeff,
    LinearMap.charpoly_toMatrix, charpoly_of_orbit_basis F hn b v hb c hclose]
  simp only [Fintype.card_fin, coeff_sub, coeff_X_pow, coeff_C]
  have he : n = (n - 1) + 1 := by omega
  have hs : (-1 : K) ^ n = -((-1 : K) ^ (n - 1)) := by
    conv_lhs => rw [he, pow_succ]
    simp
  simp [Ne.symm hn.ne', hs]

theorem eval_charpoly_of_orbit_basis [FiniteDimensional K V] (F : Module.End K V)
    {n : ℕ} (hn : 0 < n) (b : Module.Basis (Fin n) K V) (v : V)
    (hb : ∀ i : Fin n, b i = (F ^ (i : ℕ)) v) (c t : K)
    (hclose : (F ^ n) v = c • v) :
    (algebraMap K (Module.End K V) t - F).det = t ^ n - c := by
  rw [← F.eval_charpoly, charpoly_of_orbit_basis F hn b v hb c hclose]
  simp

theorem reverse_cycle_polynomial (n : ℕ) (c : K) :
    (X ^ n - C c : K[X]).reverse = 1 - C c * X ^ n := by
  rw [Polynomial.reverse, natDegree_X_pow_sub_C, reflect_sub, reflect_monomial, reflect_C]
  simp

theorem local_polynomial_of_orbit_basis [FiniteDimensional K V] (F : Module.End K V)
    {n : ℕ} (hn : 0 < n) (b : Module.Basis (Fin n) K V) (v : V)
    (hb : ∀ i : Fin n, b i = (F ^ (i : ℕ)) v) (c : K)
    (hclose : (F ^ n) v = c • v) :
    (LinearMap.toMatrix b b F).charpolyRev = 1 - C c * X ^ n := by
  classical
  rw [← Matrix.reverse_charpoly, LinearMap.charpoly_toMatrix,
    charpoly_of_orbit_basis F hn b v hb c hclose, reverse_cycle_polynomial]

end PaperXI.CyclicPolynomial
