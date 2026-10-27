module

public import Mathlib.NumberTheory.Padics.PadicIntegers
public import Mathlib.Topology.MetricSpace.Contracting
public import Mathlib.Algebra.MvPolynomial.Basic
public import Mathlib.Tactic

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialPadicContraction

open MvPolynomial

variable {d e : ℕ}

/-- Evaluation of an actual polynomial system with arbitrary integral p-adic coefficients. -/
def evalSystem (p : ℕ) [Fact p.Prime]
    (H : Fin e → MvPolynomial (Fin d) ℤ_[p]) (u : Fin d → ℤ_[p]) : Fin e → ℤ_[p] :=
  fun i => MvPolynomial.eval u (H i)

/-- Polynomial evaluation over a commutative ring preserves every principal congruence. -/
theorem eval_dvd_of_dvd {R : Type*} [CommRing R]
    (P : MvPolynomial (Fin d) R) (x y : Fin d → R) (a : R)
    (h : ∀ i, a ∣ x i - y i) : a ∣ eval x P - eval y P := by
  induction P using MvPolynomial.induction_on with
  | C c => simp
  | add P Q hP hQ =>
    simp only [map_add]
    convert dvd_add hP hQ using 2
    ring
  | mul_X P j hP =>
    obtain ⟨r, hr⟩ := hP
    obtain ⟨s, hs⟩ := h j
    refine ⟨r * x j + eval y P * s, ?_⟩
    simp only [map_mul, eval_X]
    linear_combination x j * hr + eval y P * hs

/-- A p-adic integral polynomial is nonexpanding for the supremum metric. -/
theorem eval_dist_le (p : ℕ) [Fact p.Prime]
    (P : MvPolynomial (Fin d) ℤ_[p]) (x y : Fin d → ℤ_[p]) :
    dist (eval x P) (eval y P) ≤ dist x y := by
  rw [dist_eq_norm]
  induction P using MvPolynomial.induction_on with
  | C c => simp
  | add P Q hP hQ =>
    have heq : eval x (P + Q) - eval y (P + Q) =
        (eval x P - eval y P) + (eval x Q - eval y Q) := by simp; ring
    rw [heq]
    exact (PadicInt.nonarchimedean _ _).trans (max_le hP hQ)
  | mul_X P j hP =>
    have heq : eval x (P * X j) - eval y (P * X j) =
        (eval x P - eval y P) * x j + eval y P * (x j - y j) := by simp; ring
    rw [heq]
    apply (PadicInt.nonarchimedean _ _).trans
    apply max_le
    · rw [norm_mul]
      exact (mul_le_mul_of_nonneg_left (PadicInt.norm_le_one _) (norm_nonneg _)).trans
        (by simpa using hP)
    · rw [norm_mul]
      apply (mul_le_mul_of_nonneg_right (PadicInt.norm_le_one _) (norm_nonneg _)).trans
      simpa only [one_mul, ← dist_eq_norm] using dist_le_pi_dist x y j

/-- Actual polynomial systems with p-adic integral coefficients are 1-Lipschitz. -/
theorem lipschitz_evalSystem (p : ℕ) [Fact p.Prime]
    (H : Fin e → MvPolynomial (Fin d) ℤ_[p]) : LipschitzWith 1 (evalSystem p H) := by
  apply LipschitzWith.of_dist_le_mul
  intro x y
  simp only [NNReal.coe_one, one_mul]
  exact (dist_pi_le_iff dist_nonneg).2 fun i => eval_dist_le p (H i) x y

/-- The normalized integral fixed-point map. -/
def contractionMap (p : ℕ) [Fact p.Prime]
    (H : Fin d → MvPolynomial (Fin d) ℤ_[p]) (c : Fin d → ℤ_[p])
    (u : Fin d → ℤ_[p]) : Fin d → ℤ_[p] :=
  fun i => c i + (p : ℤ_[p]) * evalSystem p H u i

/-- The factor p makes every such actual polynomial map strictly contracting. -/
theorem contracting_contractionMap (p : ℕ) [Fact p.Prime]
    (H : Fin d → MvPolynomial (Fin d) ℤ_[p]) (c : Fin d → ℤ_[p]) :
    ContractingWith ‖(p : ℤ_[p])‖₊ (contractionMap p H c) := by
  constructor
  · exact_mod_cast (PadicInt.norm_lt_one_iff_dvd (p : ℤ_[p])).2 (dvd_refl _)
  · apply LipschitzWith.of_dist_le_mul
    intro x y
    apply (dist_pi_le_iff (mul_nonneg (norm_nonneg _) dist_nonneg)).2
    intro i
    change dist (c i + (p : ℤ_[p]) * evalSystem p H x i)
      (c i + (p : ℤ_[p]) * evalSystem p H y i) ≤ ‖(p : ℤ_[p])‖ * dist x y
    rw [dist_eq_norm]
    have heq : c i + (p : ℤ_[p]) * evalSystem p H x i -
        (c i + (p : ℤ_[p]) * evalSystem p H y i) =
        (p : ℤ_[p]) * (evalSystem p H x i - evalSystem p H y i) := by ring
    rw [heq, norm_mul]
    exact mul_le_mul_of_nonneg_left (eval_dist_le p (H i) x y)
      (norm_nonneg (p : ℤ_[p]))

/-- Existence and uniqueness of the normalized vector fixed point, without an assumed
Lipschitz or contraction hypothesis on the polynomial system. -/
theorem exists_unique_fixedPoint (p : ℕ) [Fact p.Prime]
    (H : Fin d → MvPolynomial (Fin d) ℤ_[p]) (c : Fin d → ℤ_[p]) :
    ∃! u : Fin d → ℤ_[p], contractionMap p H c u = u := by
  let hf := contracting_contractionMap p H c
  exact ⟨hf.fixedPoint _, hf.fixedPoint_isFixedPt, fun u hu => hf.fixedPoint_unique hu⟩

/-- If the polynomial correction vanishes at zero, every precision of the constant
term is inherited by the fixed point. -/
theorem fixedPoint_divisible (p N : ℕ) [Fact p.Prime]
    (H : Fin d → MvPolynomial (Fin d) ℤ_[p]) (c u : Fin d → ℤ_[p])
    (hH : evalSystem p H 0 = 0) (hu : contractionMap p H c u = u)
    (hc : ∀ i, (p : ℤ_[p]) ^ N ∣ c i) : ∀ i, (p : ℤ_[p]) ^ N ∣ u i := by
  suffices h : ∀ n : ℕ, (∀ i, (p : ℤ_[p]) ^ n ∣ c i) →
      ∀ i, (p : ℤ_[p]) ^ n ∣ u i from h N hc
  intro n
  induction n with
  | zero => simp
  | succ n ih =>
    intro hcn
    have hun : ∀ i, (p : ℤ_[p]) ^ n ∣ u i :=
      ih (fun i => dvd_trans (pow_dvd_pow _ (Nat.le_succ n)) (hcn i))
    intro i
    have hHi : eval (0 : Fin d → ℤ_[p]) (H i) = 0 := congrFun hH i
    have hHn : (p : ℤ_[p]) ^ n ∣ evalSystem p H u i := by
      simpa only [evalSystem, hHi, sub_zero, Pi.zero_apply] using
        eval_dvd_of_dvd (H i) u 0 ((p : ℤ_[p]) ^ n) (by simpa using hun)
    have hm : (p : ℤ_[p]) ^ (n + 1) ∣ (p : ℤ_[p]) * evalSystem p H u i := by
      rw [pow_succ']
      exact mul_dvd_mul_left _ hHn
    have hui : c i + (p : ℤ_[p]) * evalSystem p H u i = u i := congrFun hu i
    rw [← hui]
    exact dvd_add (hcn i) hm

/-- The unique fixed point satisfies every given constant-term divisibility bound. -/
theorem exists_unique_fixedPoint_divisible (p N : ℕ) [Fact p.Prime]
    (H : Fin d → MvPolynomial (Fin d) ℤ_[p]) (c : Fin d → ℤ_[p])
    (hH : evalSystem p H 0 = 0) (hc : ∀ i, (p : ℤ_[p]) ^ N ∣ c i) :
    ∃! u : Fin d → ℤ_[p], contractionMap p H c u = u ∧
      ∀ i, (p : ℤ_[p]) ^ N ∣ u i := by
  obtain ⟨u, hu, huniq⟩ := exists_unique_fixedPoint p H c
  exact ⟨u, ⟨hu, fixedPoint_divisible p N H c u hH hu hc⟩,
    fun v hv => huniq v hv.1⟩

end Komorebi.PolynomialPadicContraction
