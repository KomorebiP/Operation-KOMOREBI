import KomorebiPadic.CartierSection
import Mathlib.Algebra.Polynomial.OfFn
import Mathlib.Tactic.Positivity

/-! # Polynomial Cartier extraction and lossless bounded coordinates
The zero polynomial uses `natDegree 0 = 0`. Compatibility requires positive radix;
no primality, integral-domain, or characteristic assumption is used here.
-/
namespace KomorebiPadic
open Polynomial
variable {R : Type*} [CommRing R]

/-- Finite extraction. At zero radix this is deliberately only a finite truncation. -/
noncomputable def polynomialCartier (p d : ℕ) (P : R[X]) : R[X] :=
  open scoped Classical in
  Polynomial.ofFn (P.natDegree + 1) (fun i => P.coeff (p * i.val + d))

@[simp] theorem coeff_polynomialCartier {p : ℕ} (hp : 0 < p)
    (d n : ℕ) (P : R[X]) :
    (polynomialCartier p d P).coeff n = P.coeff (p*n+d) := by
  classical
  unfold polynomialCartier
  by_cases hn : n < P.natDegree + 1
  · simp [Polynomial.ofFn_coeff_eq_val_of_lt, hn]
  · rw [Polynomial.ofFn_coeff_eq_zero_of_ge _ (by omega)]
    symm
    apply Polynomial.coeff_eq_zero_of_natDegree_lt
    have hm : n ≤ p*n := by simpa using Nat.mul_le_mul_right n hp
    omega

/-- Exact agreement with the complete-series section, not truncated agreement. -/
@[simp] theorem polynomialCartier_coe {p : ℕ} (hp : 0 < p)
    (d : ℕ) (P : R[X]) :
    (polynomialCartier p d P : PowerSeries R) = cartierSection p d (P : PowerSeries R) := by
  ext n
  simp [coeff_polynomialCartier hp]

/-- This bound includes a zero result and digits larger than the input degree. -/
theorem polynomialCartier_natDegree_le {p : ℕ} (hp : 0 < p)
    (d : ℕ) (P : R[X]) :
    (polynomialCartier p d P).natDegree ≤ P.natDegree / p := by
  rw [Polynomial.natDegree_le_iff_coeff_eq_zero]
  intro n hn
  rw [coeff_polynomialCartier hp]
  apply Polynomial.coeff_eq_zero_of_natDegree_lt
  have hx := (Nat.div_lt_iff_lt_mul hp).mp hn
  rw [Nat.mul_comm] at hx
  omega

/-- The sharper offset-sensitive natural-degree bound also handles zero output. -/
theorem polynomialCartier_natDegree_le_offset {p : ℕ} (hp : 0 < p)
    (d : ℕ) (P : R[X]) :
    (polynomialCartier p d P).natDegree ≤ (P.natDegree-d) / p := by
  rw [Polynomial.natDegree_le_iff_coeff_eq_zero]
  intro n hn
  rw [coeff_polynomialCartier hp]
  apply Polynomial.coeff_eq_zero_of_natDegree_lt
  have hx := (Nat.div_lt_iff_lt_mul hp).mp hn
  rw [Nat.mul_comm] at hx
  omega

/-- Support is exactly the selected residue progression. -/
theorem polynomialCartier_support_iff {p : ℕ} (hp : 0 < p)
    (d n : ℕ) (P : R[X]) :
    n ∈ (polynomialCartier p d P).support ↔ p*n+d ∈ P.support := by
  simp only [Polynomial.mem_support_iff, coeff_polynomialCartier hp]

noncomputable def polynomialCartierLinear (p d : ℕ) (hp : 0 < p) : R[X] →ₗ[R] R[X] where
  toFun := polynomialCartier p d
  map_add' P Q := by ext n; simp [coeff_polynomialCartier hp]
  map_smul' a P := by ext n; simp [coeff_polynomialCartier hp]

/-- Coefficient reduction commutes with extraction, including composite moduli. -/
theorem polynomialCartier_map {S : Type*} [CommRing S] {p : ℕ} (hp : 0 < p)
    (f : R →+* S) (d : ℕ) (P : R[X]) :
    (polynomialCartier p d P).map f = polynomialCartier p d (P.map f) := by
  ext n
  simp [coeff_polynomialCartier hp]

/-- Uniform multiplicative degree closure, valid even over rings with zero divisors. -/
theorem polynomialCartier_mul_degree_le {p D : ℕ} (hp : 0 < p) (d : ℕ)
    (P H : R[X]) (hP : P.natDegree ≤ D) (hH : H.natDegree ≤ (p-1)*D) :
    (polynomialCartier p d (P*H)).natDegree ≤ D := by
  have hdeg : (P*H).natDegree ≤ p*D := by
    calc
      (P*H).natDegree ≤ P.natDegree + H.natDegree := Polynomial.natDegree_mul_le
      _ ≤ D + (p-1)*D := Nat.add_le_add hP hH
      _ = (1+(p-1))*D := by ring
      _ = p*D := by congr 1; omega
  exact (polynomialCartier_natDegree_le hp d _).trans
    (by simpa [Nat.mul_div_right, hp.ne'] using Nat.div_le_div_right (c := p) hdeg)

/-- Coefficient coordinates encode all polynomials of degree at most D. -/
noncomputable def numeratorPolynomial (D : ℕ) (v : Fin (D+1) → R) : R[X] :=
  open scoped Classical in Polynomial.ofFn (D+1) v

noncomputable def numeratorCoordinates (D : ℕ) (P : R[X]) : Fin (D+1) → R :=
  Polynomial.toFn (D+1) P

@[simp] theorem numeratorPolynomial_degree (D : ℕ) (v : Fin (D+1) → R) :
    (numeratorPolynomial D v).natDegree ≤ D := by
  classical
  exact Nat.le_of_lt_succ (Polynomial.ofFn_natDegree_lt (by omega) v)

@[simp] theorem numeratorCoordinates_polynomial (D : ℕ) (v : Fin (D+1) → R) :
    numeratorCoordinates D (numeratorPolynomial D v) = v := by
  classical
  exact Polynomial.toFn_comp_ofFn_eq_id (D+1) v

/-- No coefficients are discarded when the degree certificate holds. -/
theorem numeratorPolynomial_coordinates {D : ℕ} (P : R[X]) (hP : P.natDegree ≤ D) :
    numeratorPolynomial D (numeratorCoordinates D P) = P := by
  classical
  exact Polynomial.ofFn_comp_toFn_eq_id_of_natDegree_lt (by omega)

/-- At radix zero a finite polynomial cannot represent the repeated constant sequence. -/
theorem polynomialCartier_zero_radix_counterexample :
    PowerSeries.coeff 1 (polynomialCartier 0 0 (1 : ℤ[X]) : PowerSeries ℤ) = 0 ∧
      PowerSeries.coeff 1 (cartierSection 0 0 (1 : PowerSeries ℤ)) = 1 := by
  constructor
  · norm_num [polynomialCartier]
  · simp

/-- A nonzero input can have a zero digit section; degree equality is not universal. -/
theorem polynomialCartier_can_annihilate :
    polynomialCartier 2 1 (X^2 : ℤ[X]) = 0 := by
  ext n
  rw [coeff_polynomialCartier (by decide : 0 < 2)]
  have hn : 2*n+1 ≠ 2 := by omega
  simp [Polynomial.coeff_X_pow, hn]

end KomorebiPadic
