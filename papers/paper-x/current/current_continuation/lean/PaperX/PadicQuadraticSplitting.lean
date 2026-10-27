import Mathlib.NumberTheory.Padics.Hensel
import Mathlib.NumberTheory.Padics.RingHoms
import Mathlib.NumberTheory.LegendreSymbol.Basic
import Mathlib.Tactic

/-!
# Splitting of the quadratic polynomial X² + 1 over p-adic fields

A square root of −1 in Q_p has norm one and hence lies in Z_p. This permits
finite residue obstructions at p = 3 and p = 2. At odd primes a simple residue
root lifts by the pinned Mathlib Hensel theorem. Together with the finite-field
criterion this proves the exact congruence criterion for every prime.

The p-adic fields and reduction maps below are actual Mathlib constructions.
No local-type label, square-root-existence oracle, or new axiom is assumed.
-/

noncomputable section
open Polynomial
namespace PaperX.PadicQuadraticSplitting
local instance : Fact (Nat.Prime 5) := ⟨by decide⟩

/-- Every p-adic square root of −1 is integral. -/
theorem root_integral {p : ℕ} [Fact p.Prime] {x : ℚ_[p]} (hx : x ^ 2 = -1) :
    ∃ y : ℤ_[p], (y : ℚ_[p]) = x ∧ y ^ 2 = -1 := by
  have hn : ‖x‖ ^ 2 = 1 := by simpa only [norm_pow, norm_neg, norm_one] using congrArg norm hx
  have hl : ‖x‖ ≤ 1 := by nlinarith [norm_nonneg x]
  refine ⟨⟨x, hl⟩, rfl, ?_⟩
  apply Subtype.ext
  exact hx

/-- Reduction modulo three obstructs a square root of −1 in Q_3. -/
theorem no_root_three : ¬ ∃ x : ℚ_[3], x ^ 2 = -1 := by
  rintro ⟨x, hx⟩
  obtain ⟨y, _, hy⟩ := root_integral hx
  have hz := congrArg (PadicInt.toZMod : ℤ_[3] →+* ZMod 3) hy
  have bad : ∀ z : ZMod 3, z ^ 2 ≠ -1 := by decide +kernel
  exact bad _ (by simpa using hz)

/-- Reduction modulo four obstructs a square root of −1 in Q_2. -/
theorem no_root_two : ¬ ∃ x : ℚ_[2], x ^ 2 = -1 := by
  rintro ⟨x, hx⟩
  obtain ⟨y, _, hy⟩ := root_integral hx
  have hz := congrArg (PadicInt.toZModPow 2 : ℤ_[2] →+* ZMod 4) hy
  have bad : ∀ z : ZMod 4, z ^ 2 ≠ -1 := by decide +kernel
  exact bad _ (by simpa using hz)

/-- Hensel lifting at the residue root 2 produces a root in Z_5. -/
theorem root_five_integral : ∃ x : ℤ_[5], x ^ 2 = -1 := by
  have hf : ∀ x : ℤ_[5], (X ^ 2 + 1 : Polynomial ℤ).aeval x = x ^ 2 + 1 := by intro x; simp
  have hd : (X ^ 2 + 1 : Polynomial ℤ).derivative.aeval (2 : ℤ_[5]) = 4 := by norm_num [Polynomial.aeval_def]
  have hv : (X ^ 2 + 1 : Polynomial ℤ).aeval (2 : ℤ_[5]) = 5 := by norm_num
  have hn : ‖(X ^ 2 + 1 : Polynomial ℤ).aeval (2 : ℤ_[5])‖ <
      ‖(X ^ 2 + 1 : Polynomial ℤ).derivative.aeval (2 : ℤ_[5])‖ ^ 2 := by
    rw [hd, hv]
    have h4 : ‖(4 : ℤ_[5])‖ = 1 := (PadicInt.norm_natCast_eq_one_iff).2 (by decide)
    have h5 : ‖(5 : ℤ_[5])‖ < 1 := (PadicInt.norm_natCast_lt_one_iff).2 (dvd_refl _)
    simpa only [h4, one_pow] using h5
  obtain ⟨x, hx, _⟩ := hensels_lemma hn
  exact ⟨x, by have h := hf x; rw [h] at hx; exact eq_neg_of_add_eq_zero_left hx⟩

/-- The integral root gives an actual square root of −1 in Q_5. -/
theorem root_five : ∃ x : ℚ_[5], x ^ 2 = -1 := by
  obtain ⟨x, hx⟩ := root_five_integral
  exact ⟨x, congrArg (fun y : ℤ_[5] => (y : ℚ_[5])) hx⟩


/-- A p-adic integer has norm less than one exactly when its residue vanishes. -/
theorem residual_norm_lt_one {p : ℕ} [Fact p.Prime] (a : ℤ_[p]) :
    ‖a‖ < 1 ↔ PadicInt.toZMod a = 0 := by
  rw [← PadicInt.mem_nonunits, ← IsLocalRing.mem_maximalIdeal,
    ← PadicInt.ker_toZMod, RingHom.mem_ker]

/-- Every residue root of X² + 1 at an odd prime supplies an integral root. -/
theorem lift_odd_root {p : ℕ} [Fact p.Prime] (hp : p ≠ 2)
    (x : ZMod p) (hx : x ^ 2 = -1) : ∃ y : ℤ_[p], y ^ 2 = -1 := by
  obtain ⟨a, ha⟩ := ZMod.ringHom_surjective (PadicInt.toZMod : ℤ_[p] →+* ZMod p) x
  have hx0 : x ≠ 0 := by intro h; simp [h] at hx
  have ht : (2 : ZMod p) ≠ 0 := by
    intro h
    have hdvd : p ∣ 2 := (ZMod.natCast_eq_zero_iff 2 p).mp h
    have hle : p ≤ 2 := Nat.le_of_dvd (by decide) hdvd
    have hge := (Fact.out : Nat.Prime p).two_le
    omega
  have hf : ∀ z : ℤ_[p], (X ^ 2 + 1 : Polynomial ℤ).aeval z = z ^ 2 + 1 := by intro z; simp
  have hd : (X ^ 2 + 1 : Polynomial ℤ).derivative.aeval a = 2 * a := by
    norm_num [Polynomial.aeval_def]
  have hn : ‖a ^ 2 + 1‖ < 1 := (residual_norm_lt_one _).2 (by simp [ha, hx])
  have hdn : ‖(2 : ℤ_[p]) * a‖ = 1 := by
    have hnot : ¬ ‖(2 : ℤ_[p]) * a‖ < 1 := by
      rw [residual_norm_lt_one]
      simpa only [map_mul, map_ofNat, ha] using mul_ne_zero ht hx0
    exact le_antisymm (PadicInt.norm_le_one _) (not_lt.mp hnot)
  obtain ⟨y, hy, _⟩ := hensels_lemma (F := (X ^ 2 + 1 : Polynomial ℤ)) (a := a)
    (by simpa only [hf, hd, hdn, one_pow] using hn)
  exact ⟨y, by rw [hf] at hy; exact eq_neg_of_add_eq_zero_left hy⟩

/-- For odd primes the p-adic criterion agrees with the finite-field criterion. -/
theorem root_iff_mod_four {p : ℕ} [Fact p.Prime] (hp : p ≠ 2) :
    (∃ x : ℚ_[p], x ^ 2 = -1) ↔ p % 4 ≠ 3 := by
  constructor
  · rintro ⟨x, hx⟩
    obtain ⟨y, _, hy⟩ := root_integral hx
    apply ZMod.mod_four_ne_three_of_sq_eq_neg_one
    simpa using congrArg (PadicInt.toZMod : ℤ_[p] →+* ZMod p) hy
  · intro h
    obtain ⟨x, hx⟩ := ZMod.exists_sq_eq_neg_one_iff.mpr h
    obtain ⟨y, hy⟩ := lift_odd_root hp x (by simpa only [pow_two] using hx.symm)
    exact ⟨y, congrArg (fun z : ℤ_[p] => (z : ℚ_[p])) hy⟩


/-- Complete criterion, including the nonsplit prime two. -/
theorem root_iff_mod_four_eq_one (p : ℕ) [Fact p.Prime] :
    (∃ x : ℚ_[p], x ^ 2 = -1) ↔ p % 4 = 1 := by
  by_cases hp : p = 2
  · subst p
    simp only [no_root_two, false_iff]
    norm_num
  · rw [root_iff_mod_four hp]
    have hodd := (Nat.Prime.mod_two_eq_one_iff_ne_two (Fact.out : p.Prime)).mpr hp
    omega

end PaperX.PadicQuadraticSplitting
