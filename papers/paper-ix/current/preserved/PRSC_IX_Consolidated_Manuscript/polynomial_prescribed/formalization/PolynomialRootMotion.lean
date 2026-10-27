module
public import PolynomialWeightedLift
public import PolynomialMotionNormalization
public import PolynomialMotionEstimate
public import PolynomialMotionRational

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialRootMotion
open MvPolynomial PolynomialWeightedInverse PolynomialPadicContraction
open PolynomialWeightedLift PolynomialMotionNormalization
variable {d : ℕ}

/-- Polynomial normalization yields a root, its retained precision, and uniqueness
throughout the full ball. The injective preconditioner may come from a different
original system, which is essential when the coefficients have been perturbed. -/
theorem exists_root_from_original_preconditioner (p s r : ℕ) [Fact p.Prime]
    (hr : 2 * s < r) (F : Fin d → MvPolynomial (Fin d) ℤ_[p])
    (a : Fin d → ℤ_[p]) (A J : Matrix (Fin d) (Fin d) ℤ_[p])
    (hJA : J * A = (p : ℤ_[p]) ^ s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
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
    have hpre := precondition_root_iff p s A J hJA F (shiftedPoint p s a w)
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

/-- The original Jacobian inverse certificate constructs the nearby root of the
actual perturbed polynomial system, without an assumption on its new Jacobian. -/
theorem exists_perturbed_root_certificate (p s M : ℕ) [Fact p.Prime]
    (hM : 2 * s < M) (F H : Fin d → MvPolynomial (Fin d) ℤ_[p])
    (a : Fin d → ℤ_[p]) (A : Matrix (Fin d) (Fin d) ℤ_[p])
    (hAJ : A * jacobian F a = (p : ℤ_[p]) ^ s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
    (hJA : jacobian F a * A = (p : ℤ_[p]) ^ s • (1 : Matrix (Fin d) (Fin d) ℤ_[p]))
    (hFa : ∀ i, eval a (F i) = 0) :
    ∃ b : Fin d → ℤ_[p],
      (∀ i, eval b (perturbSystem p M F H i) = 0) ∧
      (∀ i, (p : ℤ_[p]) ^ (M - s) ∣ b i - a i) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i) ∧
      (∀ z : Fin d → ℤ_[p], (∀ i, eval z (perturbSystem p M F H i) = 0) →
        (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ z i - a i) → z = b) := by
  obtain ⟨C, Q, hC, hQ, hnorm⟩ :=
    exists_motion_normalization p s M hM F H a A hAJ hFa
  exact exists_root_from_original_preconditioner p s M hM (perturbSystem p M F H)
    a A (jacobian F a) hJA C Q hC hQ hnorm

/-- Weighted first-order root motion, including construction and full-ball uniqueness
of the perturbed root, under the original actual Jacobian's inverse bound. -/
theorem exists_root_motion (p s M : ℕ) [Fact p.Prime]
    (hM : 2 * s < M) (F H : Fin d → MvPolynomial (Fin d) ℤ_[p])
    (a : Fin d → ℤ_[p]) (hFa : ∀ i, eval a (F i) = 0)
    (hJ : IsUnit (rationalMatrix p (jacobian F a)))
    (hbound : ∃ A : Matrix (Fin d) (Fin d) ℤ_[p],
      rationalMatrix p A = (p : ℚ_[p]) ^ s • (rationalMatrix p (jacobian F a))⁻¹) :
    ∃ b : Fin d → ℤ_[p],
      (∀ i, eval b (perturbSystem p M F H i) = 0) ∧
      (∀ i, (p : ℤ_[p]) ^ (M - s) ∣ b i - a i) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i) ∧
      (∀ z : Fin d → ℤ_[p], (∀ i, eval z (perturbSystem p M F H i) = 0) →
        (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ z i - a i) → z = b) ∧
      (∃ ε : Fin d → ℤ_[p], (∀ i, (p : ℤ_[p]) ^ (2 * M - 3 * s) ∣ ε i) ∧
        ∀ i, (b i : ℚ_[p]) - (a i : ℚ_[p]) =
          -(p : ℚ_[p]) ^ M * ((rationalMatrix p (jacobian F a))⁻¹).mulVec
            (fun j => (eval a (H j) : ℚ_[p])) i + (ε i : ℚ_[p])) := by
  obtain ⟨A, hA⟩ := hbound
  obtain ⟨hAJ, hJA⟩ := certificate_of_integral_inverse p s (jacobian F a) A hJ hA
  obtain ⟨b, hb, hdepth, hball, huniq⟩ :=
    exists_perturbed_root_certificate p s M hM F H a A hAJ hJA hFa
  have hroot : ∀ i, eval b (F i) + (p : ℤ_[p]) ^ M * eval b (H i) = 0 := by
    intro i
    simpa only [eval_perturbSystem] using hb i
  have herror := PolynomialMotionEstimate.first_order_error_dvd p s M F H a b A
    hM hAJ hFa hroot hdepth
  obtain ⟨ε, hε, hformula⟩ := PolynomialMotionRational.exists_rational_error
    p s M (2 * M - 3 * s) (by omega) (jacobian F a) A hA a b
    (fun j => eval a (H j)) herror
  exact ⟨b, hb, hdepth, hball, huniq, ε, hε, hformula⟩

/-- The unique-existence form keeps the full uniqueness ball separate from the
additional displacement and first-order precision conclusions. -/
theorem exists_unique_root_motion (p s M : ℕ) [Fact p.Prime]
    (hM : 2 * s < M) (F H : Fin d → MvPolynomial (Fin d) ℤ_[p])
    (a : Fin d → ℤ_[p]) (hFa : ∀ i, eval a (F i) = 0)
    (hJ : IsUnit (rationalMatrix p (jacobian F a)))
    (hbound : ∃ A : Matrix (Fin d) (Fin d) ℤ_[p],
      rationalMatrix p A = (p : ℚ_[p]) ^ s • (rationalMatrix p (jacobian F a))⁻¹) :
    (∃! b : Fin d → ℤ_[p], (∀ i, eval b (perturbSystem p M F H i) = 0) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i)) ∧
    (∀ b : Fin d → ℤ_[p], (∀ i, eval b (perturbSystem p M F H i) = 0) →
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i) →
      (∀ i, (p : ℤ_[p]) ^ (M - s) ∣ b i - a i) ∧
      (∃ ε : Fin d → ℤ_[p], (∀ i, (p : ℤ_[p]) ^ (2 * M - 3 * s) ∣ ε i) ∧
        ∀ i, (b i : ℚ_[p]) - (a i : ℚ_[p]) =
          -(p : ℚ_[p]) ^ M * ((rationalMatrix p (jacobian F a))⁻¹).mulVec
            (fun j => (eval a (H j) : ℚ_[p])) i + (ε i : ℚ_[p]))) := by
  obtain ⟨b, hb, hdepth, hball, huniq, herror⟩ := exists_root_motion p s M hM F H a hFa hJ hbound
  constructor
  · exact ⟨b, ⟨hb, hball⟩, fun z hz => huniq z hz.1 hz.2⟩
  · intro z hz hzb
    rw [huniq z hz hzb]
    exact ⟨hdepth, herror⟩

end Komorebi.PolynomialRootMotion
