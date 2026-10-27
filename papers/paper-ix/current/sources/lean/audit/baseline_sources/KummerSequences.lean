module
public import FiniteMahler
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.KummerSequences
open Mahler
variable {R : Type*} [CommRing R]
/-- Unshifted higher-difference divisibility in a ring, not in its fraction field. -/
def Kummer (p:R) (f:ℕ→R) : Prop := ∀ k n, p^k ∣ difference 1 k f n

theorem difference_product (f g:ℕ→R) (s n:ℕ) :
    difference 1 s (fun r => f r*g r) n = ∑ i ∈ Finset.range (s+1),
      (s.choose i:R)*difference 1 i f n*difference 1 (s-i) g (n+i) := by
  induction s generalizing n with
  | zero => simp
  | succ s ih =>
    rw [difference_succ, ih, ih, ←Finset.sum_sub_distrib]
    have hs := Finset.sum_choose_succ_mul
      (fun i j => difference 1 i f n*difference 1 j g (n+i)) s
    simp only [←mul_assoc] at hs
    rw [hs, ←Finset.sum_add_distrib]
    apply Finset.sum_congr rfl
    intro i hi
    have his := Finset.mem_range_succ_iff.mp hi
    rw [show s+1-i=s-i+1 by omega, difference_succ, difference_succ]
    have h1 : n+(i+1)=n+1+i := by omega
    have h2 : n+i+1=n+1+i := by omega
    rw [h1,h2]
    ring

theorem difference_constant (a:R) (k n:ℕ) (hk:0<k) :
    difference 1 k (fun _ => a) n=0 := by
  induction k generalizing n with
  | zero => omega
  | succ k ih =>
    by_cases hz:k=0
    · subst k; simp
    · rw [difference_succ,ih (n+1) (by omega),ih n (by omega),sub_self]

theorem constant_kummer (p a:R) : Kummer p (fun _ => a) := by
  intro k n
  by_cases hz:k=0
  · subst k; simp
  · rw [difference_constant a k n (by omega)]; exact dvd_zero _

theorem kummer_mul (p:R) {f g:ℕ→R} (hf:Kummer p f) (hg:Kummer p g) :
    Kummer p (fun n => f n*g n) := by
  intro k n
  rw [difference_product]
  apply Finset.dvd_sum
  intro i hi
  have hik := Finset.mem_range_succ_iff.mp hi
  have H := mul_dvd_mul (hf i n) (hg (k-i) (n+i))
  rw [←pow_add,Nat.add_sub_of_le hik] at H
  simpa only [mul_assoc] using dvd_mul_of_dvd_right H (k.choose i:R)

theorem kummer_inverse (p:R) (f g:ℕ→R) (hfg:∀n,f n*g n=1)
    (hf:Kummer p f) : Kummer p g := by
  intro k
  induction k using Nat.strong_induction_on with
  | h k ih =>
    intro n
    by_cases hk:k=0
    · subst k; simp
    have hkpos:0<k := by omega
    have he := difference_product g f k n
    have hfun : (fun r => g r*f r) = fun _ => (1:R) := by
      funext r; simpa only [mul_comm] using hfg r
    rw [hfun,difference_constant 1 k n hkpos,Finset.sum_range_succ] at he
    simp only [Nat.choose_self,Nat.cast_one,one_mul,Nat.sub_self,difference_zero] at he
    have ht : p^k ∣ ∑ i ∈ Finset.range k,
        (k.choose i:R)*difference 1 i g n*difference 1 (k-i) f (n+i) := by
      apply Finset.dvd_sum
      intro i hi
      have hik: i<k := Finset.mem_range.mp hi
      have H := mul_dvd_mul (ih i hik n) (hf (k-i) (n+i))
      rw [←pow_add,Nat.add_sub_of_le (by omega : i≤k)] at H
      simpa only [mul_assoc] using dvd_mul_of_dvd_right H (k.choose i:R)
    have hp : p^k ∣ difference 1 k g n*f (n+k) := by
      have hh := dvd_neg.mpr ht
      convert hh using 1
      linear_combination -he
    have H := dvd_mul_of_dvd_left hp (g (n+k))
    simpa only [mul_assoc,hfg, mul_one] using H

/-- Affine functions with slope divisible by p are Kummer sequences. -/
theorem affine_kummer (p a b:R) (ha:p∣a) : Kummer p (fun n => a*(n:R)+b) := by
  intro k n
  cases k with
  | zero => simp
  | succ k =>
    have he : difference 1 1 (fun n:ℕ => a*(n:R)+b) = fun _ => a := by
      funext r; simp only [difference_one,Nat.cast_add,Nat.cast_one]; ring
    have hh : difference 1 (k+1) (fun n:ℕ => a*(n:R)+b) n =
        difference 1 k (fun _ => a) n := by
      change (fwdDiff 1)^[k+1] _ n = _
      rw [Function.iterate_succ_apply]
      change difference 1 k (difference 1 1 (fun n:ℕ => a*(n:R)+b)) n = _
      rw [he]
    rw [hh]
    by_cases hz:k=0
    · subst k; simpa using ha
    · rw [difference_constant a k n (by omega)]; exact dvd_zero _
end KomorebiPaperIX.KummerSequences
