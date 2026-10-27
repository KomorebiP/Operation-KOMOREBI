import Mathlib.NumberTheory.Padics.PadicVal.Basic
import KomorebiPadic.QuotientBarrier

/-!
# Prime-base radix descent for the quotient barrier

For `1 ≤ q ≤ Q`, write `q - 1 = p*a + b` with `b < p`.  Kummer's
digit-sum formula shows that removing the common low base-`p` digit from
`p*Q - 1`, `q - 1`, and `p*Q - q` preserves the binomial `p`-adic valuation:

`v_p ((p*Q - 1).choose (q - 1)) = v_p ((Q - 1).choose a)`.

The final theorem specializes `a` and `b` to quotient and remainder.
-/

namespace KomorebiPadic

/-- Appending one low base-`p` digit adds that digit to the digit sum. -/
theorem digitSum_add_mul
    {p a b : ℕ} (hp : 1 < p) (hb : b < p) :
    (p.digits (b + p * a)).sum = b + (p.digits a).sum := by
  by_cases hb0 : b = 0
  · subst b
    by_cases ha0 : a = 0
    · subst a
      simp
    · rw [Nat.digits_add p hp 0 a (by omega) (Or.inr ha0)]
      simp
  · rw [Nat.digits_add p hp b a hb (Or.inl hb0)]
    simp

/-- The top barrier index `p*Q-1` has low digit `p-1`. -/
theorem digitSum_mul_sub_one
    {p Q : ℕ} (hp : 1 < p) (hQ : 0 < Q) :
    (p.digits (p * Q - 1)).sum =
      (p - 1) + (p.digits (Q - 1)).sum := by
  have hQeq : Q = (Q - 1) + 1 := by omega
  have hmul : p * Q = p * (Q - 1) + p := by
    calc
      p * Q = p * ((Q - 1) + 1) :=
        congrArg (fun x : ℕ => p * x) hQeq
      _ = p * (Q - 1) + p := by ring
  have hrepr : p * Q - 1 = (p - 1) + p * (Q - 1) := by
    rw [hmul]
    omega
  rw [hrepr]
  exact digitSum_add_mul hp (by omega)

/-- Arithmetic decomposition of the complementary barrier index. -/
theorem barrier_complement_decomp
    {p Q q a b : ℕ}
    (hp : 1 < p) (hq1 : 1 ≤ q) (hqQ : q ≤ Q)
    (hdecomp : q - 1 = p * a + b) (hb : b < p) :
    p * Q - q = (p - 1 - b) + p * (Q - 1 - a) := by
  have hp1 : 1 ≤ p := Nat.le_of_lt hp
  have ha_pa : a ≤ p * a := by
    simpa using Nat.mul_le_mul_right a hp1
  have hpa : p * a ≤ q - 1 := by omega
  have hqsub : q - 1 ≤ Q - 1 := Nat.sub_le_sub_right hqQ 1
  have haQ : a ≤ Q - 1 := ha_pa.trans (hpa.trans hqsub)
  have hQdecomp : Q = (Q - 1 - a) + a + 1 := by omega
  have hqeq : q = p * a + b + 1 := by omega
  have hPQ : p * Q = p * (Q - 1 - a) + p * a + p := by
    calc
      p * Q = p * ((Q - 1 - a) + a + 1) :=
        congrArg (fun x : ℕ => p * x) hQdecomp
      _ = p * (Q - 1 - a) + p * a + p := by ring
  rw [hPQ, hqeq]
  omega

/-- Explicit-radix form of Kummer descent at a quotient barrier. -/
theorem binomial_padic_radix_descent_of_decomp
    {p Q q a b : ℕ}
    (hp : p.Prime) (hq1 : 1 ≤ q) (hqQ : q ≤ Q)
    (hdecomp : q - 1 = p * a + b) (hb : b < p) :
    padicValNat p ((p * Q - 1).choose (q - 1)) =
      padicValNat p ((Q - 1).choose a) := by
  let _ : Fact p.Prime := ⟨hp⟩
  have hpgt : 1 < p := hp.one_lt
  have hQ : 0 < Q := lt_of_lt_of_le (by omega) hqQ
  have hp1 : 1 ≤ p := Nat.le_of_lt hpgt
  have hq_pQ : q ≤ p * Q := by
    calc
      q ≤ Q := hqQ
      _ = 1 * Q := by simp
      _ ≤ p * Q := Nat.mul_le_mul_right Q hp1
  have hleft : q - 1 ≤ p * Q - 1 := Nat.sub_le_sub_right hq_pQ 1
  have ha_pa : a ≤ p * a := by
    simpa using Nat.mul_le_mul_right a hp1
  have hpa : p * a ≤ q - 1 := by omega
  have hqsub : q - 1 ≤ Q - 1 := Nat.sub_le_sub_right hqQ 1
  have hright : a ≤ Q - 1 := ha_pa.trans (hpa.trans hqsub)

  have hdigit_q :
      (p.digits (q - 1)).sum = b + (p.digits a).sum := by
    rw [hdecomp]
    simpa [Nat.add_comm] using (digitSum_add_mul (p := p) (a := a) (b := b) hpgt hb)

  have hcomp := barrier_complement_decomp hpgt hq1 hqQ hdecomp hb
  have hbcomp : p - 1 - b < p := by omega
  have hdigit_comp :
      (p.digits (p * Q - q)).sum =
        (p - 1 - b) + (p.digits (Q - 1 - a)).sum := by
    rw [hcomp]
    exact digitSum_add_mul hpgt hbcomp

  have hdigit_top := digitSum_mul_sub_one hpgt hQ
  have hkum_left :=
    sub_one_mul_padicValNat_choose_eq_sub_sum_digits (p := p) hleft
  have hkum_right :=
    sub_one_mul_padicValNat_choose_eq_sub_sum_digits (p := p) hright
  have hsub : p * Q - 1 - (q - 1) = p * Q - q := by omega
  rw [hdigit_q, hsub, hdigit_comp, hdigit_top] at hkum_left

  have hmul :
      (p - 1) * padicValNat p ((p * Q - 1).choose (q - 1)) =
        (p - 1) * padicValNat p ((Q - 1).choose a) := by
    rw [hkum_left, hkum_right]
    omega
  exact Nat.eq_of_mul_eq_mul_left (by omega) hmul

/-- Canonical quotient/remainder form of the prime-base radix identity. -/
theorem binomial_padic_radix_descent
    {p Q q : ℕ} (hp : p.Prime) (hq1 : 1 ≤ q) (hqQ : q ≤ Q) :
    padicValNat p ((p * Q - 1).choose (q - 1)) =
      padicValNat p ((Q - 1).choose ((q - 1) / p)) := by
  refine binomial_padic_radix_descent_of_decomp
    (a := (q - 1) / p) (b := (q - 1) % p) hp hq1 hqQ ?_ ?_
  · simpa [Nat.add_comm] using (Nat.mod_add_div (q - 1) p).symm
  · exact Nat.mod_lt _ hp.pos

end KomorebiPadic
