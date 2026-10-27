module
public import Mathlib.LinearAlgebra.Vandermonde
public import Mathlib.Tactic.Ring
@[expose] public section
noncomputable section
namespace Komorebi.Euler
open scoped BigOperators
section Ring
variable {K : Type*} [CommRing K] {n : ℕ}

/-- Transpose orientation: packet rows, correction-order columns. -/
def spectralObservation (z : Fin n → K) : Matrix (Fin n) (Fin n) K :=
  fun i j => (z i-1)*z i^j.val

lemma spectralObservation_factor (z : Fin n → K) :
    spectralObservation z=Matrix.diagonal (fun i => z i-1)*Matrix.vandermonde z := by
  ext i j
  simp [spectralObservation, Matrix.diagonal_mul]

/-- Classical Vandermonde identity applied to successive spectral defects. -/
theorem spectralObservation_det (z : Fin n → K) :
    (spectralObservation z).det =
      (∏ i, (z i-1)) * (∏ i, ∏ j > i, (z j-z i)) := by
  rw [spectralObservation_factor, Matrix.det_mul, Matrix.det_diagonal,
      Matrix.det_vandermonde]

variable [IsDomain K]

theorem spectralObservation_nonsingular (z : Fin n → K)
    (hz : Function.Injective z) (hone : ∀ i, z i ≠ 1) :
    (spectralObservation z).det ≠ 0 := by
  rw [spectralObservation_factor, Matrix.det_mul, Matrix.det_diagonal]
  apply mul_ne_zero
  · exact Finset.prod_ne_zero_iff.mpr (fun i _ => sub_ne_zero.mpr (hone i))
  · exact Matrix.det_vandermonde_ne_zero_iff.mpr hz

/-- Separation at ONE FIXED argument. This says nothing about a moving critical point. -/
theorem spectral_fixed_point_separation (z a : Fin n → K)
    (hz : Function.Injective z) (hone : ∀ i, z i ≠ 1)
    (h : ∀ m : Fin n, ∑ i, (z i-1)*a i*z i^m.val=0) : a=0 := by
  have ht : (fun i => (z i-1)*a i)=0 :=
    Matrix.eq_zero_of_forall_pow_sum_mul_pow_eq_zero hz h
  funext i
  have hi := congrFun ht i
  exact (mul_eq_zero.mp hi).resolve_left (sub_ne_zero.mpr (hone i))

/-- Apply the separation theorem separately to value and slope coordinates. -/
theorem spectral_fixed_jet_separation (z a b : Fin n → K)
    (hz : Function.Injective z) (hone : ∀ i, z i ≠ 1)
    (ha : ∀ m : Fin n, ∑ i, (z i-1)*a i*z i^m.val=0)
    (hb : ∀ m : Fin n, ∑ i, (z i-1)*b i*z i^m.val=0) :
    a=0 ∧ b=0 :=
  ⟨spectral_fixed_point_separation z a hz hone ha,
    spectral_fixed_point_separation z b hz hone hb⟩

end Ring
end Komorebi.Euler
