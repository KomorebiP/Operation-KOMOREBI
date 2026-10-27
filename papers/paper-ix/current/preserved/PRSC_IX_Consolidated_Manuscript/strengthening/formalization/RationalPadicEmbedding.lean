module
public import Mathlib.NumberTheory.Padics.PadicIntegers

/-!
# Rational samples as p-adic integer samples

Author: Komorebi P.
The natural input metric is the metric inherited from the p-adic integers.
No claim identifies it with the usual metric on the natural numbers.
-/

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace KomorebiPaperIX.RationalPadicEmbedding

variable (p : ℕ) [Fact p.Prime]

theorem norm_le_one (f : ℕ → ℚ) (h0 : f 0 = 0)
    (h : ∀ m n, padicNorm p (f m - f n) = padicNorm p ((m : ℚ) - n)) (n : ℕ) :
    ‖(f n : ℚ_[p])‖ ≤ 1 := by
  have hn : padicNorm p (f n) = padicNorm p (n : ℚ) := by
    simpa only [h0, Nat.cast_zero, sub_zero] using h n 0
  rw [Padic.eq_padicNorm, hn]
  have hi : ‖((n : ℚ) : ℚ_[p])‖ ≤ 1 := by
    simpa only [Rat.cast_natCast, Int.cast_natCast] using
      Padic.norm_int_le_one (p := p) (n : ℤ)
  simpa only [Padic.eq_padicNorm] using hi

/-- The exact rational values, included in the integral unit ball. -/
def samples (f : ℕ → ℚ) (h0 : f 0 = 0)
    (h : ∀ m n, padicNorm p (f m - f n) = padicNorm p ((m : ℚ) - n)) :
    ℕ → ℤ_[p] :=
  fun n => ⟨(f n : ℚ_[p]), norm_le_one p f h0 h n⟩

@[simp]
theorem samples_coe (f : ℕ → ℚ) (h0 : f 0 = 0)
    (h : ∀ m n, padicNorm p (f m - f n) = padicNorm p ((m : ℚ) - n)) (n : ℕ) :
    (samples p f h0 h n : ℚ_[p]) = (f n : ℚ_[p]) := rfl

/-- Distances agree with natural numbers embedded in the p-adic integers. -/
theorem samples_dist (f : ℕ → ℚ) (h0 : f 0 = 0)
    (h : ∀ m n, padicNorm p (f m - f n) = padicNorm p ((m : ℚ) - n)) (m n : ℕ) :
    dist (samples p f h0 h m) (samples p f h0 h n) =
      dist (m : ℤ_[p]) (n : ℤ_[p]) := by
  simp only [dist_eq_norm, PadicInt.norm_def, PadicInt.coe_sub, samples_coe,
    PadicInt.coe_natCast]
  have hm : (m : ℚ_[p]) = ((m : ℚ) : ℚ_[p]) := by simp
  have hn : (n : ℚ_[p]) = ((n : ℚ) : ℚ_[p]) := by simp
  rw [hm, hn, ← Rat.cast_sub, ← Rat.cast_sub, Padic.eq_padicNorm, Padic.eq_padicNorm, h]

end KomorebiPaperIX.RationalPadicEmbedding

#print axioms KomorebiPaperIX.RationalPadicEmbedding.norm_le_one
#print axioms KomorebiPaperIX.RationalPadicEmbedding.samples
#print axioms KomorebiPaperIX.RationalPadicEmbedding.samples_coe
#print axioms KomorebiPaperIX.RationalPadicEmbedding.samples_dist
