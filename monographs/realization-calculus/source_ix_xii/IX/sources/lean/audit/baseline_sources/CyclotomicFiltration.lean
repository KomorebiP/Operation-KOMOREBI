module
public import Mathlib.RingTheory.Ideal.Operations
public import Mathlib.Data.Nat.Multiplicity
public import Mathlib.NumberTheory.Padics.PadicVal.Basic
public import Mathlib.Tactic
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.CyclotomicFiltration
variable {R : Type*} [CommRing R]
/-- The ideal of the prime and the augmentation of a prime-torsion element. -/
def torsionIdeal (p : ℕ) (z : R) : Ideal R := Ideal.span {(p:R), z-1}
theorem prime_mem (p : ℕ) (z : R) : (p:R) ∈ torsionIdeal p z :=
  Ideal.subset_span (by simp)
theorem augmentation_mem (p : ℕ) (z : R) : z-1 ∈ torsionIdeal p z :=
  Ideal.subset_span (by simp)
/-- A stronger relation than nilpotence modulo p. -/
theorem augmentation_pow_mem (p : ℕ) (hp : p.Prime) (z : R) (hz : z^p=1) :
    (z-1)^p ∈ Ideal.span {(p:R)} * torsionIdeal p z := by
  classical
  let y := z-1
  let I := torsionIdeal p z
  let P : Ideal R := Ideal.span {(p:R)}
  have hy : y∈I := augmentation_mem p z
  have hm : (∑ k ∈ Finset.range (p-1), (p.choose (k+1):R)*y^(k+1)) ∈ P*I := by
    apply Ideal.sum_mem
    intro k hk
    have hk' : k+1 < p := by have := Finset.mem_range.mp hk; omega
    have hd : p ∣ p.choose (k+1) := by
      simpa using hp.dvd_choose_pow (n := 1) (by omega : k+1 ≠ 0)
        (by simpa using (Nat.ne_of_lt hk'))
    have hc : (p.choose (k+1):R)∈P := by
      apply Ideal.mem_span_singleton.mpr
      obtain ⟨a, ha⟩ := hd
      exact ⟨(a:R), by rw [ha, Nat.cast_mul]⟩
    exact Ideal.mul_mem_mul hc
      (Ideal.pow_le_self (by omega : k+1 ≠ 0) (Ideal.pow_mem_pow hy (k+1)))
  have hsum : (y+1)^p = 1 +
      (∑ k ∈ Finset.range (p-1), (p.choose (k+1):R)*y^(k+1)) + y^p := by
    rw [add_pow, Finset.sum_range_succ]
    simp only [one_pow, mul_one, Nat.choose_self, Nat.cast_one]
    have hs : (∑ k ∈ Finset.range p, y^k*(p.choose k:R)) = 1 +
        ∑ k ∈ Finset.range (p-1), (p.choose (k+1):R)*y^(k+1) := by
      conv_lhs => rw [show p=(p-1)+1 by have := hp.pos; omega, Finset.sum_range_succ']
      simp only [pow_zero, Nat.choose_zero_right, Nat.cast_one, mul_one]
      rw [Nat.sub_add_cancel (show 1≤p from hp.one_le), add_comm]
      congr 1
      apply Finset.sum_congr rfl
      intro k _
      ring
    rw [hs]
  have hunit : (y+1)^p=1 := by simpa [y] using hz
  have he : y^p = -(∑ k ∈ Finset.range (p-1), (p.choose (k+1):R)*y^(k+1)) := by
    linear_combination hunit-hsum
  change y^p∈P*I
  rw [he]
  exact (P*I).neg_mem hm
/-- The whole two-generated ideal contracts after a p-th power. -/
theorem torsion_ideal_pow (p : ℕ) (hp : p.Prime) (z : R) (hz : z^p=1) :
    torsionIdeal p z ^ p ≤ Ideal.span {(p:R)} * torsionIdeal p z := by
  classical
  let I := torsionIdeal p z
  let P : Ideal R := Ideal.span {(p:R)}
  let Q : Ideal R := Ideal.span {z-1}
  have hI : I=P+Q := by
    simp only [I, P, Q, torsionIdeal, Ideal.span_insert, Ideal.add_eq_sup]
  have hPI : P≤I := by rw [hI, Ideal.add_eq_sup]; exact le_sup_left
  have hQI : Q≤I := by rw [hI, Ideal.add_eq_sup]; exact le_sup_right
  have hQp : Q^p≤P*I := by
    change (Ideal.span {z-1})^p ≤ P*I
    rw [Ideal.span_singleton_pow]
    exact Ideal.span_le.mpr (by
      intro x hx
      rw [Set.mem_singleton_iff] at hx
      subst x
      exact augmentation_pow_mem p hp z hz)
  change I^p≤P*I
  conv_lhs => rw [hI, add_pow, Ideal.sum_eq_sup]
  apply Finset.sup_le
  intro k hk
  by_cases hk0 : k=0
  · subst k
    simpa using hQp
  · have hPpow : P^k=P*P^(k-1) := by
      rw [← pow_succ']
      congr 1
      omega
    have htail : P^(k-1)*Q^(p-k)≤I := by
      by_cases hk1 : k=1
      · subst k
        simpa using (Ideal.pow_le_self (I:=Q) (by have := hp.two_le; omega : p-1 ≠ 0)).trans hQI
      · exact Ideal.mul_le_left.trans
          ((Ideal.pow_le_self (by omega : k-1 ≠ 0)).trans hPI)
    exact Ideal.mul_le_left.trans (by
      rw [hPpow, mul_assoc]
      exact Ideal.mul_mono_right htail)
/-- A factorial estimate in ideals, without domain hypotheses. -/
theorem factorial_power_bound (p : ℕ) (hp : p.Prime) (I P : Ideal R)
    (hIp : I^p≤P*I) (n : ℕ) :
    I^n ≤ P^(padicValNat p n.factorial) := by
  let : Fact p.Prime := ⟨hp⟩
  induction n using Nat.strong_induction_on with
  | h n ih =>
    by_cases hn : n=0
    · subst n
      simp
    · have hsmall : n/p<n := Nat.div_lt_self (Nat.pos_of_ne_zero hn) hp.one_lt
      have hdecomp : p*(n/p)+n%p=n := Nat.div_add_mod n p
      have hv : padicValNat p n.factorial = padicValNat p (n/p).factorial+n/p := by
        rw [← padicValNat_mul_div_factorial (p:=p) n, padicValNat_factorial_mul]
      calc
        I^n = (I^p)^(n/p)*I^(n%p) := by rw [←pow_mul, ←pow_add, hdecomp]
        _ ≤ (P*I)^(n/p)*I^(n%p) := Ideal.mul_mono_left (Ideal.pow_right_mono hIp _)
        _ = P^(n/p)*(I^(n/p)*I^(n%p)) := by rw [mul_pow, mul_assoc]
        _ ≤ P^(n/p)*I^(n/p) := Ideal.mul_mono_right Ideal.mul_le_left
        _ ≤ P^(n/p)*P^(padicValNat p (n/p).factorial) := Ideal.mul_mono_right (ih _ hsmall)
        _ = P^(padicValNat p n.factorial) := by rw [←pow_add, hv, Nat.add_comm]
theorem torsion_ideal_factorial_bound (p : ℕ) (hp : p.Prime) (z : R) (hz : z^p=1)
    (q : ℕ) :
    torsionIdeal p z ^ q ≤ Ideal.span {(p:R)^(padicValNat p q.factorial)} := by
  rw [←Ideal.span_singleton_pow]
  exact factorial_power_bound p hp _ _ (torsion_ideal_pow p hp z hz) q
end KomorebiPaperIX.CyclotomicFiltration
