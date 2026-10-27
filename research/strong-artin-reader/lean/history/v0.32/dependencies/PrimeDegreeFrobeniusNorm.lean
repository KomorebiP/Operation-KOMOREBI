import FrobeniusSpectralNorm

/-! In characteristic p, the prime-degree norm vanishes exactly at eigenvalue 1.
The interpretation for a diagonalized kernel action does NOT assert that every
kernel action is diagonalizable. -/
namespace Komorebi.StrongArtin.SquareZeroH2
variable {G A B k I : Type} [Group G] [Ring A] [Ring B] [Field k]
variable (p : ℕ) [Fact (Nat.Prime p)] [CharP k p]

theorem normWeight_prime_eq (a : k) :
    normWeight a p = (a-1)^(p-1) := by
  have hp := (Fact.out : Nat.Prime p)
  by_cases ha : a = 1
  · subst a
    rw [normWeight_one, CharP.cast_eq_zero k p, sub_self]
    simp [Nat.sub_ne_zero_of_lt hp.one_lt]
  · apply mul_right_cancel₀ (sub_ne_zero.mpr ha)
    change (∑ j ∈ Finset.range p, a^j) * (a-1) = (a-1)^(p-1) * (a-1)
    rw [geom_sum_mul, ← pow_succ, Nat.sub_add_cancel hp.one_le]
    rw [sub_pow_char]
    simp

theorem normWeight_prime_zero_iff (a : k) :
    normWeight a p = 0 ↔ a = 1 := by
  rw [normWeight_prime_eq p]
  have hp := (Fact.out : Nat.Prime p)
  rw [pow_eq_zero_iff (Nat.sub_ne_zero_of_lt hp.one_lt), sub_eq_zero]

namespace FrobeniusSpectralCoordinates
variable {D : Datum G A B} {F : Aˣ}
variable (S : FrobeniusSpectralCoordinates D F k I)

/-- At the quotient prime, the only blocked coordinates are the invariant ones. -/
theorem prime_norm_image_iff (e : D.Kernel) :
    (∃ x, D.frobeniusNorm F p x = e) ↔
    ∀ i, S.eigenvalue i = 1 → S.coordinates e i = 0 := by
  rw [S.norm_image_iff]
  simp only [normWeight_prime_zero_iff p]

/-- Exact criterion for the original prescribed p-th power problem. -/
theorem prescribed_prime_power_iff (V : Aˣ)
    (hV : D.q V = D.q (F^p)) :
    (∃ F' : Aˣ, D.q F' = D.q F ∧ F'^p = V) ↔
    ∀ i, S.eigenvalue i = 1 →
      S.coordinates (D.unitMismatch V (F^p) hV) i = 0 := by
  rw [D.power_lifting_iff_norm_image, S.prime_norm_image_iff p]

/-- The same condition controls matching up to one independent local conjugator. -/
theorem prescribed_prime_gauge_iff (V : Aˣ)
    (hV : D.q V = D.q (F^p)) :
    (∃ F' u : Aˣ, D.q F' = D.q F ∧ D.q u = 1 ∧ u * F'^p * u⁻¹ = V) ↔
    ∀ i, S.eigenvalue i = 1 →
      S.coordinates (D.unitMismatch V (F^p) hV) i = 0 := by
  rw [D.one_power_gauge_iff_strict, S.prescribed_prime_power_iff p]

end FrobeniusSpectralCoordinates
end Komorebi.StrongArtin.SquareZeroH2
