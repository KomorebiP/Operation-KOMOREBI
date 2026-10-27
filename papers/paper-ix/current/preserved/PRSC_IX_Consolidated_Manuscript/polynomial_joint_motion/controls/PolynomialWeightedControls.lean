module
public import PolynomialPadicUnique
public import Mathlib.Tactic

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialWeightedControls
open MvPolynomial Komorebi.PolynomialPadicUnique

/-- The excluded binary boundary is an actual polynomial over the p-adic integers. -/
def squarePlusThree : MvPolynomial (Fin 1) ℤ_[2] := X 0 ^ 2 + C 3

/-- At a = 1 the residual has depth exactly two, while the derivative has depth one. -/
theorem boundary_residual_derivative :
    eval (fun _ : Fin 1 => (1 : ℤ_[2])) squarePlusThree = 4 ∧
    eval (fun _ : Fin 1 => (1 : ℤ_[2])) (pderiv 0 squarePlusThree) = 2 := by
  norm_num [squarePlusThree]

/-- The scalar effective inverse A = 1 clears the derivative denominator with s = 1. -/
theorem boundary_scaled_inverse :
    (1 : ℤ_[2]) * eval (fun _ : Fin 1 => (1 : ℤ_[2]))
      (pderiv 0 squarePlusThree) = (2 : ℤ_[2]) ^ 1 ∧
    eval (fun _ : Fin 1 => (1 : ℤ_[2])) (pderiv 0 squarePlusThree) *
      (1 : ℤ_[2]) = (2 : ℤ_[2]) ^ 1 := by
  simp [boundary_residual_derivative.2]

/-- No residue class modulo eight solves X^2 + 3 = 0. -/
theorem boundary_no_mod_eight (t : ZMod 8) : t ^ 2 + 3 ≠ 0 := by
  have h : ∀ x : ZMod 8, x ^ 2 + 3 ≠ 0 := by decide
  exact h t

/-- Consequently the excluded boundary does not even admit a p-adic root. -/
theorem boundary_no_padic_root (a : Fin 1 → ℤ_[2]) :
    eval a squarePlusThree ≠ 0 := by
  intro h
  have h8 := congrArg (PadicInt.toZModPow 3) h
  have heq : (PadicInt.toZModPow 3 (a 0)) ^ 2 + 3 = 0 := by
    simpa only [squarePlusThree, map_add, map_pow, eval_X, eval_C,
      map_ofNat, map_zero] using h8
  exact boundary_no_mod_eight (PadicInt.toZModPow 3 (a 0)) heq

/-- Existence-form refutation for the strict-threshold negative control. -/
theorem boundary_no_root :
    ¬ ∃ a : Fin 1 → ℤ_[2], eval a squarePlusThree = 0 := by
  rintro ⟨a, ha⟩
  exact boundary_no_padic_root a ha

/-- Powers of p have their stated exact depth in the actual p-adic integers. -/
theorem prime_power_exact_depth (p k : ℕ) [Fact (Nat.Prime p)] :
    ¬ (p : ℤ_[p]) ^ (k + 1) ∣ (p : ℤ_[p]) ^ k := by
  intro h
  have hz : (p : ℤ) ^ (k + 1) ∣ (p : ℤ) ^ k := by
    apply (int_pow_dvd_iff p (k + 1) ((p : ℤ) ^ k)).mpr
    simpa using h
  have hn : p ^ (k + 1) ∣ p ^ k := by exact_mod_cast hz
  have hle := (Nat.pow_dvd_pow_iff_le_right (Fact.out : Nat.Prime p).one_lt).mp hn
  omega

/-- The boundary residual is divisible by p^r at r = 2s, and not at r + 1. -/
theorem boundary_exact_residual_depth :
    (2 : ℤ_[2]) ^ 2 ∣ eval (fun _ : Fin 1 => (1 : ℤ_[2])) squarePlusThree ∧
    ¬ (2 : ℤ_[2]) ^ 3 ∣ eval (fun _ : Fin 1 => (1 : ℤ_[2])) squarePlusThree := by
  rw [boundary_residual_derivative.1]
  constructor
  · norm_num
  · convert prime_power_exact_depth 2 2 using 1
    norm_num

/-- A scalar linear polynomial realizes the full loss of s digits. -/
def weightedLinear (p s : ℕ) [Fact (Nat.Prime p)] :
    MvPolynomial (Fin 1) ℤ_[p] := C ((p : ℤ_[p]) ^ s) * X 0

/-- The root after adding p^M is exactly -p^(M-s). -/
theorem linear_perturbation_root (p s M : ℕ) [Fact (Nat.Prime p)] (hM : s ≤ M) :
    eval (fun _ : Fin 1 => -(p : ℤ_[p]) ^ (M - s))
      (weightedLinear p s + C ((p : ℤ_[p]) ^ M)) = 0 := by
  simp only [weightedLinear, map_add, map_mul, eval_C, eval_X, mul_neg]
  rw [← pow_add, Nat.add_sub_of_le hM]
  ring

/-- No uniformly stronger displacement depth is possible, even in dimension one. -/
theorem linear_displacement_sharp (p s M : ℕ) [Fact (Nat.Prime p)] :
    (p : ℤ_[p]) ^ (M - s) ∣ -(p : ℤ_[p]) ^ (M - s) ∧
    ¬ (p : ℤ_[p]) ^ (M - s + 1) ∣ -(p : ℤ_[p]) ^ (M - s) := by
  constructor
  · exact dvd_neg.mpr dvd_rfl
  · intro h
    exact prime_power_exact_depth p (M - s) (dvd_neg.mp h)

end Komorebi.PolynomialWeightedControls
