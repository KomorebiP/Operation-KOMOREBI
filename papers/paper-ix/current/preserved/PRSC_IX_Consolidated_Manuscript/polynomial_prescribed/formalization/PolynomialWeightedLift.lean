module
public import PolynomialTaylorRing
public import PolynomialPadicContraction
public import PolynomialWeightedInverse
public import PolynomialWeightedNormalization

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialWeightedLift
open MvPolynomial PolynomialWeightedInverse PolynomialPadicContraction
variable {d : ℕ}

/-- The integral coordinates on the full weighted uniqueness ball. -/
def shiftedPoint (p s : ℕ) [Fact p.Prime] (a u : Fin d → ℤ_[p]) : Fin d → ℤ_[p] :=
  fun i => a i + (p : ℤ_[p]) ^ (s + 1) * u i

/-- Polynomial normalization yields a root, its retained precision, and uniqueness
throughout the full ball. The actual Taylor normalization is supplied below. -/
theorem exists_root_of_normalization (p s r : ℕ) [Fact p.Prime]
    (hr : 2 * s < r) (F : Fin d → MvPolynomial (Fin d) ℤ_[p])
    (a : Fin d → ℤ_[p]) (A : Matrix (Fin d) (Fin d) ℤ_[p])
    (hJA : jacobian F a * A = (p : ℤ_[p]) ^ s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
    (C : Fin d → ℤ_[p]) (Q : Fin d → MvPolynomial (Fin d) ℤ_[p])
    (hC : ∀ i, (p : ℤ_[p]) ^ (r - (2 * s + 1)) ∣ C i)
    (hQ : ∀ i, eval (0 : Fin d → ℤ_[p]) (Q i) = 0)
    (hnorm : ∀ u i, eval (shiftedPoint p s a u) (precondition A F i) =
      (p : ℤ_[p]) ^ (2 * s + 1) * (C i + u i + (p : ℤ_[p]) * eval u (Q i))) :
    ∃ b : Fin d → ℤ_[p],
      (∀ i, eval b (F i) = 0) ∧
      (∀ i, (p : ℤ_[p]) ^ (r - s) ∣ b i - a i) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i) ∧
      (∀ z : Fin d → ℤ_[p], (∀ i, eval z (F i) = 0) →
        (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ z i - a i) → z = b) := by
  let H : Fin d → MvPolynomial (Fin d) ℤ_[p] := fun i => -Q i
  let c : Fin d → ℤ_[p] := fun i => -C i
  have hH : evalSystem p H 0 = 0 := by
    funext i
    change eval (0 : Fin d → ℤ_[p]) (-Q i) = 0
    rw [map_neg, hQ i, neg_zero]
  have hc : ∀ i, (p : ℤ_[p]) ^ (r - (2 * s + 1)) ∣ c i :=
    fun i => dvd_neg.mpr (hC i)
  obtain ⟨u, hu, huniq⟩ := exists_unique_fixedPoint p H c
  have hprec := fixedPoint_divisible p (r - (2 * s + 1)) H c u hH hu hc
  have hp : (p : ℤ_[p]) ≠ 0 := Nat.cast_ne_zero.mpr (Fact.out : p.Prime).ne_zero
  have hroot_iff (w : Fin d → ℤ_[p]) :
      (∀ i, eval (shiftedPoint p s a w) (F i) = 0) ↔ contractionMap p H c w = w := by
    have hpre := precondition_root_iff p s A (jacobian F a) hJA F (shiftedPoint p s a w)
    constructor
    · intro hw
      have hg : (fun i => eval (shiftedPoint p s a w) (precondition A F i)) = 0 :=
        hpre.mpr (funext hw)
      funext i
      have hi := congrFun hg i
      rw [hnorm] at hi
      have hz : C i + w i + (p : ℤ_[p]) * eval w (Q i) = 0 :=
        (mul_eq_zero.mp hi).resolve_left (pow_ne_zero _ hp)
      change -C i + (p : ℤ_[p]) * eval w (-Q i) = w i
      rw [map_neg]
      linear_combination -hz
    · intro hw
      apply funext_iff.mp (hpre.mp ?_)
      funext i
      rw [hnorm]
      have hi := congrFun hw i
      change -C i + (p : ℤ_[p]) * eval w (-Q i) = w i at hi
      rw [map_neg] at hi
      have hz : C i + w i + (p : ℤ_[p]) * eval w (Q i) = 0 := by
        linear_combination -hi
      simp only [hz, mul_zero, Pi.zero_apply]
  refine ⟨shiftedPoint p s a u, (hroot_iff u).mpr hu, ?_, ?_, ?_⟩
  · intro i
    obtain ⟨v, hv⟩ := hprec i
    refine ⟨v, ?_⟩
    have he : s + 1 + (r - (2 * s + 1)) = r - s := by omega
    simp only [shiftedPoint, add_sub_cancel_left]
    rw [hv, ← mul_assoc, ← pow_add, he]
  · intro i
    exact ⟨u i, by simp [shiftedPoint]⟩
  · intro z hz hball
    choose w hw using hball
    have hzw : z = shiftedPoint p s a w := by
      funext i
      have hi := hw i
      change z i = a i + (p : ℤ_[p]) ^ (s + 1) * w i
      linear_combination hi
    rw [hzw] at hz ⊢
    exact congrArg (shiftedPoint p s a) (huniq w ((hroot_iff w).mp hz))

/-- Weighted nonlinear lifting for the actual Jacobian, with an effective integral
inverse certificate. Uniqueness holds on the entire ball of depth s+1. -/
theorem exists_weighted_root_certificate (p s r : ℕ) [Fact p.Prime]
    (hr : 2 * s < r) (F : Fin d → MvPolynomial (Fin d) ℤ_[p])
    (a : Fin d → ℤ_[p]) (A : Matrix (Fin d) (Fin d) ℤ_[p])
    (hAJ : A * jacobian F a = (p : ℤ_[p]) ^ s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
    (hJA : jacobian F a * A = (p : ℤ_[p]) ^ s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
    (hF : ∀ i, (p : ℤ_[p]) ^ r ∣ eval a (F i)) :
    ∃ b : Fin d → ℤ_[p],
      (∀ i, eval b (F i) = 0) ∧
      (∀ i, (p : ℤ_[p]) ^ (r - s) ∣ b i - a i) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i) ∧
      (∀ z : Fin d → ℤ_[p], (∀ i, eval z (F i) = 0) →
        (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ z i - a i) → z = b) := by
  obtain ⟨C, Q, hC, hQ, hnorm⟩ :=
    PolynomialWeightedNormalization.exists_normalization p s r hr F a A hAJ hF
  exact exists_root_of_normalization p s r hr F a A hJA C Q hC hQ hnorm

/-- The full weighted lifting theorem under the stated fraction-field inverse bound.
Coefficients and the center are arbitrary p-adic integers, and the same exponent s
is retained without replacing it by a determinant valuation. -/
theorem exists_weighted_root (p s r : ℕ) [Fact p.Prime]
    (hr : 2 * s < r) (F : Fin d → MvPolynomial (Fin d) ℤ_[p])
    (a : Fin d → ℤ_[p]) (hJ : IsUnit (rationalMatrix p (jacobian F a)))
    (hbound : ∃ A : Matrix (Fin d) (Fin d) ℤ_[p],
      rationalMatrix p A = (p : ℚ_[p]) ^ s • (rationalMatrix p (jacobian F a))⁻¹)
    (hF : ∀ i, (p : ℤ_[p]) ^ r ∣ eval a (F i)) :
    ∃ b : Fin d → ℤ_[p],
      (∀ i, eval b (F i) = 0) ∧
      (∀ i, (p : ℤ_[p]) ^ (r - s) ∣ b i - a i) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i) ∧
      (∀ z : Fin d → ℤ_[p], (∀ i, eval z (F i) = 0) →
        (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ z i - a i) → z = b) := by
  obtain ⟨A, hAJ, hJA⟩ := (bounded_inverse_iff_certificate p s (jacobian F a)).mp ⟨hJ, hbound⟩
  exact exists_weighted_root_certificate p s r hr F a A hAJ hJA hF

/-- Unique-existence presentation, with uniqueness in the full ball as predicate. -/
theorem exists_unique_weighted_root (p s r : ℕ) [Fact p.Prime]
    (hr : 2 * s < r) (F : Fin d → MvPolynomial (Fin d) ℤ_[p])
    (a : Fin d → ℤ_[p]) (hJ : IsUnit (rationalMatrix p (jacobian F a)))
    (hbound : ∃ A : Matrix (Fin d) (Fin d) ℤ_[p],
      rationalMatrix p A = (p : ℚ_[p]) ^ s • (rationalMatrix p (jacobian F a))⁻¹)
    (hF : ∀ i, (p : ℤ_[p]) ^ r ∣ eval a (F i)) :
    (∃! b : Fin d → ℤ_[p], (∀ i, eval b (F i) = 0) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i)) ∧
    (∀ b : Fin d → ℤ_[p], (∀ i, eval b (F i) = 0) →
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i) →
      ∀ i, (p : ℤ_[p]) ^ (r - s) ∣ b i - a i) := by
  obtain ⟨b, hb, hprec, hball, huniq⟩ := exists_weighted_root p s r hr F a hJ hbound hF
  constructor
  · exact ⟨b, ⟨hb, hball⟩, fun z hz => huniq z hz.1 hz.2⟩
  · intro z hz hzb
    rw [huniq z hz hzb]
    exact hprec

end Komorebi.PolynomialWeightedLift
