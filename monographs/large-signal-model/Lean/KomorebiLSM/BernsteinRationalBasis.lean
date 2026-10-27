import Mathlib.RingTheory.Polynomial.Bernstein
import Mathlib.RingTheory.Polynomial.DegreeLT
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.Tactic

set_option autoImplicit false
namespace Komorebi.LSM.BernsteinRationalBasis
open Polynomial Module
noncomputable section

theorem bernstein_natDegree_le (n : ℕ) (k : Fin (n+1)) :
    (bernsteinPolynomial ℚ n k).natDegree ≤ n := by
  have hsub : (1-(X : ℚ[X])).natDegree ≤ 1 := by
    exact (Polynomial.natDegree_sub_le _ _).trans (by simp)
  have hp : ((1-(X : ℚ[X]))^(n-k.val)).natDegree ≤ n-k.val := by
    calc
      _ ≤ (n-k.val) * (1-(X : ℚ[X])).natDegree := Polynomial.natDegree_pow_le
      _ ≤ (n-k.val)*1 := Nat.mul_le_mul_left _ hsub
      _ = _ := by omega
  calc
    _ ≤ ((n.choose k.val : ℚ[X]) * X^k.val).natDegree +
        ((1-(X : ℚ[X]))^(n-k.val)).natDegree := Polynomial.natDegree_mul_le
    _ ≤ k.val + (n-k.val) := by
      apply Nat.add_le_add _ hp
      have hm : ((n.choose k.val : ℚ[X]) * X^k.val).natDegree ≤
          (n.choose k.val : ℚ[X]).natDegree + (X^k.val : ℚ[X]).natDegree :=
        Polynomial.natDegree_mul_le
      simpa using hm
    _ = n := Nat.add_sub_of_le (by omega)

/-- The literal rational Bernstein polynomial, in its finite degree space. -/
def vector (n : ℕ) (k : Fin (n+1)) : Polynomial.degreeLT ℚ (n+1) :=
  ⟨bernsteinPolynomial ℚ n k, Polynomial.mem_degreeLT.mpr
    (Polynomial.degree_le_natDegree.trans_lt
      (WithBot.coe_lt_coe.mpr (Nat.lt_succ_of_le (bernstein_natDegree_le n k))))⟩

theorem independent (n : ℕ) : LinearIndependent ℚ (vector n) := by
  apply LinearIndependent.of_comp (Polynomial.degreeLT ℚ (n+1)).subtype
  exact bernsteinPolynomial.linearIndependent n

/-- Actual rational basis inversion, obtained from the independent finite family. -/
def basis (n : ℕ) : Basis (Fin (n+1)) ℚ (Polynomial.degreeLT ℚ (n+1)) :=
  basisOfLinearIndependentOfCardEqFinrank (independent n) (by
    rw [Module.finrank_eq_card_basis (Polynomial.degreeLT.basis ℚ (n+1))])

@[simp] theorem basis_val (n : ℕ) (i : Fin (n+1)) :
    ((basis n i : Polynomial.degreeLT ℚ (n+1)) : ℚ[X]) = bernsteinPolynomial ℚ n i := by
  simp only [basis, coe_basisOfLinearIndependentOfCardEqFinrank]
  rfl

/-- Rational Bernstein coordinates of a degree-bounded polynomial. -/
def coordinates (n : ℕ) (p : Polynomial.degreeLT ℚ (n+1)) : Fin (n+1) → ℚ :=
  fun i => (basis n).repr p i

theorem reconstruct (n : ℕ) (p : Polynomial.degreeLT ℚ (n+1)) :
    ∑ i : Fin (n+1), C (coordinates n p i) * bernsteinPolynomial ℚ n i = (p : ℚ[X]) := by
  have h := (basis n).sum_repr p
  have hc := congrArg (fun z : Polynomial.degreeLT ℚ (n+1) => (z : ℚ[X])) h
  simpa only [Submodule.coe_sum, Submodule.coe_smul, coordinates,
    Polynomial.smul_eq_C_mul, basis_val] using hc

/-- Fixed-degree rational monomial coordinates; the constant uses partition of unity directly. -/
def monomialCoordinates (n k : ℕ) : Fin (n+1) → ℚ :=
  if k=0 then fun _ => 1 else if h : k≤n then
    coordinates n ⟨X^k, Polynomial.mem_degreeLT.mpr
      ((Polynomial.degree_X_pow_le k).trans_lt (WithBot.coe_lt_coe.mpr (Nat.lt_succ_of_le h)))⟩
  else fun _ => 0

@[simp] theorem monomialCoordinates_zero (n : ℕ) (i : Fin (n+1)) :
    monomialCoordinates n 0 i = 1 := by simp [monomialCoordinates]

theorem monomial_reconstruct (n k : ℕ) (hk : k≤n) :
    ∑ i : Fin (n+1), C (monomialCoordinates n k i)*bernsteinPolynomial ℚ n i = X^k := by
  by_cases h0 : k=0
  · subst k
    simpa only [monomialCoordinates_zero, map_one, one_mul, pow_zero,
      Fin.sum_univ_eq_sum_range] using bernsteinPolynomial.sum ℚ n
  · simp only [monomialCoordinates, h0, hk, ↓reduceIte]
    exact reconstruct n _

/-- The exact fixed-degree Bernstein coordinates of an affine power. -/
def affineCoordinates (n d : ℕ) (a w : ℚ) (i : Fin (n+1)) : ℚ :=
  ∑ k : Fin (d+1), (d.choose k : ℚ)*a^(d-k.val)*w^k.val*monomialCoordinates n k i

theorem affine_reconstruct (n d : ℕ) (hd : d≤n) (a w : ℚ) :
    ∑ i : Fin (n+1), C (affineCoordinates n d a w i)*bernsteinPolynomial ℚ n i =
      (C a+C w*X)^d := by
  calc
    _ = ∑ k : Fin (d+1), C ((d.choose k : ℚ)*a^(d-k.val)*w^k.val) *
        (∑ i : Fin (n+1), C (monomialCoordinates n k i)*bernsteinPolynomial ℚ n i) := by
      simp only [affineCoordinates, map_sum, map_mul, Finset.sum_mul, Finset.mul_sum]
      rw [Finset.sum_comm]
      apply Finset.sum_congr rfl
      intro k _
      apply Finset.sum_congr rfl
      intro i _
      ring
    _ = ∑ k : Fin (d+1), C ((d.choose k : ℚ)*a^(d-k.val)*w^k.val)*X^k.val := by
      apply Finset.sum_congr rfl
      intro k _
      rw [monomial_reconstruct n k (by omega)]
    _ = (C a+C w*X)^d := by
      rw [add_comm (C a), add_pow, ← Fin.sum_univ_eq_sum_range]
      apply Finset.sum_congr rfl
      intro k _
      simp only [map_mul, map_pow, mul_pow, map_natCast]
      ring

@[simp] theorem affineCoordinates_zero_width (n d : ℕ) (a : ℚ) (i : Fin (n+1)) :
    affineCoordinates n d a 0 i = a^d := by
  unfold affineCoordinates
  rw [Finset.sum_eq_single (0 : Fin (d+1))]
  · simp
  · intro k _ hk
    have hne : k.val≠0 := by
      intro h
      apply hk
      exact Fin.ext h
    simp [zero_pow hne]
  · simp

/-- The same finite rational coordinate expression over the real parameters. -/
def affineReal (n d : ℕ) (a w : ℝ) (i : Fin (n+1)) : ℝ :=
  ∑ k : Fin (d+1), (d.choose k : ℝ)*a^(d-k.val)*w^k.val*(monomialCoordinates n k i : ℝ)

@[simp] theorem cast_affineCoordinates (n d : ℕ) (a w : ℚ) (i : Fin (n+1)) :
    (affineCoordinates n d a w i : ℝ) = affineReal n d a w i := by
  simp [affineCoordinates, affineReal]

@[simp] theorem affineReal_zero_width (n d : ℕ) (a : ℝ) (i : Fin (n+1)) :
    affineReal n d a 0 i = a^d := by
  unfold affineReal
  rw [Finset.sum_eq_single (0 : Fin (d+1))]
  · simp
  · intro k _ hk
    have hne : k.val≠0 := by
      intro h
      apply hk
      exact Fin.ext h
    simp [zero_pow hne]
  · simp

theorem continuous_affineReal (n d : ℕ) (i : Fin (n+1)) :
    Continuous (fun aw : ℝ×ℝ => affineReal n d aw.1 aw.2 i) := by
  unfold affineReal
  fun_prop

end
end Komorebi.LSM.BernsteinRationalBasis
