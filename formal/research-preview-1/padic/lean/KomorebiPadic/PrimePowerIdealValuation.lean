import KomorebiPadic.PrimePowerIdeals
import Mathlib.NumberTheory.Padics.PadicVal.Basic

namespace KomorebiPadic
namespace PrimePowerIdeal

@[simp] theorem order_zero (p r : ℕ) : order p r (0 : ZMod (p^r)) = r := by
  apply Nat.le_antisymm (order_le p r _)
  exact (order_spec (le_refl r) _).mpr (by simp)

theorem order_natCast {p r n : ℕ} (hp : p ≠ 1) (hn : n ≠ 0) :
    order p r (n : ZMod (p^r)) = min r (padicValNat p n) := by
  have hspec (a : ℕ) (ha : a ≤ r) : a ≤ order p r (n : ZMod (p^r)) ↔ a ≤ padicValNat p n := by
    rw [order_spec ha, ZMod.val_natCast, Nat.dvd_mod_iff (pow_dvd_pow p ha),
      Nat.pow_dvd_iff_le_padicValNat hp hn]
  apply Nat.le_antisymm
  · exact le_min (order_le p r _) ((hspec _ (order_le p r _)).mp le_rfl)
  · exact (hspec _ (min_le_left _ _)).mpr (min_le_right _ _)

theorem order_eq_truncated {p r : ℕ} (hp : 0 < p) (hp1 : p ≠ 1)
    (x : ZMod (p^r)) (hx : x ≠ 0) : order p r x = min r (padicValNat p x.val) := by
  let : NeZero (p^r) := ⟨ne_of_gt (pow_pos hp _)⟩
  have hval : x.val ≠ 0 := fun h => hx ((ZMod.val_eq_zero x).mp h)
  conv_lhs => rw [← ZMod.natCast_zmod_val x]
  exact order_natCast hp1 hval

theorem order_mul_power {p r : ℕ} (hp : p.Prime) (a : ℕ) (x : ZMod (p^r)) :
    order p r ((p : ZMod (p^r))^a*x) = min r (a+order p r x) := by
  let : NeZero (p^r) := ⟨pow_ne_zero _ hp.ne_zero⟩
  let : Fact p.Prime := ⟨hp⟩
  by_cases hx : x = 0
  · simp [hx]
  · have hval : x.val ≠ 0 := fun h => hx ((ZMod.val_eq_zero x).mp h)
    have he : (p : ZMod (p^r))^a*x = ((p^a*x.val : ℕ) : ZMod (p^r)) := by simp
    rw [he, order_natCast hp.ne_one (mul_ne_zero (pow_ne_zero _ hp.ne_zero) hval),
      padicValNat.mul (pow_ne_zero _ hp.ne_zero) hval, padicValNat.prime_pow,
      order_eq_truncated hp.pos hp.ne_one x hx]
    omega

theorem transfer_eq_sub {p r n : ℕ} (hp : p.Prime) (hn : n ≤ r) (t : ZMod (p^r)) :
    transfer p r t n = n - order p r t := by
  unfold transfer capacity
  rw [order_mul_power hp]
  omega

end PrimePowerIdeal
end KomorebiPadic
