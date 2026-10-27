module
public import Mathlib.NumberTheory.Padics.RingHoms
public import Mathlib.RingTheory.PowerSeries.Basic
public import Mathlib.Tactic.NormNum
public import Mathlib.Tactic.Ring
public import Mathlib.Tactic.FinCases
@[expose] public section
noncomputable section
namespace Komorebi.Euler
abbrev D := ℤ_[2]
abbrev F₂ := ZMod 2
abbrev red : D →+* F₂ := PadicInt.toZMod
abbrev red4 : D →+* ZMod 4 := PadicInt.toZModPow 2
abbrev red8 : D →+* ZMod 8 := PadicInt.toZModPow 3

def LastOdd (f : PowerSeries D) (d : ℕ) : Prop :=
  red (PowerSeries.coeff d f) = 1 ∧ ∀ n, d < n → red (PowerSeries.coeff n f) = 0

lemma two_ne_zero : (2 : D) ≠ 0 := by norm_num
lemma four_ne_zero : (4 : D) ≠ 0 := by norm_num

@[simp] lemma red_two : red (2 : D) = 0 := by
  change (PadicInt.toZMod : D →+* F₂) (Nat.cast _) = 0
  rw [map_natCast]
  rfl
@[simp] lemma red_four : red (4 : D) = 0 := by
  change (PadicInt.toZMod : D →+* F₂) (Nat.cast _) = 0
  rw [map_natCast]
  rfl

lemma red_two_mul (a : D) : red (2*a) = 0 := by simp
lemma red_four_pow_mul (n : ℕ) (hn : 0 < n) (a : D) : red (4^n*a) = 0 := by
  simp [ne_of_gt hn]

lemma cancel_two {a b : D} (h : 2*a = 2*b) : a = b :=
  mul_left_cancel₀ two_ne_zero h

lemma red_eq_zero_iff (a : D) : red a = 0 ↔ ∃ b : D, a = 2*b := by
  change PadicInt.toZMod a = 0 ↔ (2 : D) ∣ a
  rw [← RingHom.mem_ker, PadicInt.ker_toZMod, PadicInt.maximalIdeal_eq_span_p]
  rw [Ideal.mem_span_singleton]
  norm_num

lemma binary_value (a : F₂) : a = 0 ∨ a = 1 := by
  fin_cases a
  · exact Or.inl rfl
  · exact Or.inr rfl

lemma red_not_zero_eq_one (a : D) (h : red a ≠ 0) : red a = 1 :=
  (binary_value (red a)).resolve_left h

lemma lastOdd_unique {f : PowerSeries D} {d e : ℕ}
    (hd : LastOdd f d) (he : LastOdd f e) : d = e := by
  rcases lt_trichotomy d e with h | h | h
  · have hz := hd.2 e h
    rw [he.1] at hz
    norm_num at hz
  · exact h
  · have hz := he.2 d h
    rw [hd.1] at hz
    norm_num at hz

end Komorebi.Euler
