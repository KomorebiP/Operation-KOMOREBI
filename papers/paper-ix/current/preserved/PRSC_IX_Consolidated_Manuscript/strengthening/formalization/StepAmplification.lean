module
public import PeriodFromDifferences
public import DifferenceStepMultiples
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.StepAmplification
open Mahler
variable (p : ℕ) [Fact p.Prime]

/-- Positive Newton coefficients supply the valuation of the displacement multiplier. -/
theorem binomial_step_precision (u a : ℕ) (ha : 0<a) (hau : a≤u) :
    p^(padicValNat p u+1) ∣ u.choose a * p^a := by
  have hp : p.Prime := Fact.out
  have hu : 0<u := lt_of_lt_of_le ha hau
  have hc : u.choose a ≠ 0 := Nat.choose_ne_zero hau
  have he := Nat.add_one_mul_choose_eq (u-1) (a-1)
  rw [Nat.sub_add_cancel (by omega : 1≤u), Nat.sub_add_cancel (by omega : 1≤a)] at he
  have hd : p^(padicValNat p u) ∣ u.choose a * a := by
    rw [←he]
    exact dvd_mul_of_dvd_left (pow_padicValNat_dvd) _
  have hv := (padicValNat_dvd_iff_le (Nat.mul_ne_zero hc ha.ne')).mp hd
  rw [padicValNat.mul hc ha.ne'] at hv
  have hva := PeriodFromDifferences.valuation_lt p a ha
  apply (padicValNat_dvd_iff_le (Nat.mul_ne_zero hc (pow_ne_zero _ hp.ne_zero))).mpr
  rw [padicValNat.mul hc (pow_ne_zero _ hp.ne_zero), padicValNat.prime_pow]
  omega

variable {R : Type*} [CommRing R]

/-- A displacement consumes base differences and adds its valuation to their first-order gain.
The cap M is fixed at the inspected row. No period hypothesis is used. -/
theorem offset_displacement (f : ℕ→R) (h n u A M : ℕ)
    (H : ∀ a, (p:R)^(min (A+a) M) ∣ difference h a f n) :
    (p:R)^(min (A+padicValNat p u+1) M) ∣ f (n+u*h)-f n := by
  rw [PeriodFromDifferences.displacement_expansion]
  apply Finset.dvd_sum
  intro a ha
  have hau : a+1≤u := by have := Finset.mem_range.mp ha; omega
  by_cases hs : A+(a+1)<M
  · have hd := H (a+1)
    rw [min_eq_left (Nat.le_of_lt hs)] at hd
    obtain ⟨b,hb⟩ := hd
    rw [hb]
    have hn := binomial_step_precision p u (a+1) (by omega) hau
    have hc : (p:R)^(padicValNat p u+1) ∣ (u.choose (a+1):R)*(p:R)^(a+1) := by
      obtain ⟨c,hc⟩ := hn
      refine ⟨(c:R), ?_⟩
      simpa only [Nat.cast_mul,Nat.cast_pow] using congrArg (fun x:ℕ => (x:R)) hc
    have hpA : (p:R)^(A+(padicValNat p u+1)) ∣
        (u.choose (a+1):R)*((p:R)^(A+(a+1))*b) := by
      obtain ⟨c,hc⟩ := hc
      refine ⟨c*b, ?_⟩
      calc
        _ = (p:R)^A * ((u.choose (a+1):R)*(p:R)^(a+1))*b := by rw [pow_add]; ring
        _ = (p:R)^A * ((p:R)^(padicValNat p u+1)*c)*b := by rw [hc]
        _ = _ := by rw [pow_add]; ring
    apply dvd_trans (pow_dvd_pow (p:R) (min_le_left _ _))
    simpa only [Nat.add_assoc] using hpA
  · have hd := H (a+1)
    rw [min_eq_right (by omega : M≤A+(a+1))] at hd
    exact dvd_trans (pow_dvd_pow (p:R) (min_le_right _ _)) (dvd_mul_of_dvd_right hd _)

/-- Difference composition is iteration of the same operator. -/
theorem difference_compose (h a b : ℕ) (f : ℕ→R) :
    difference h a (difference h b f)=difference h (a+b) f := by
  simp only [difference,Function.iterate_add_apply]

/-- Repeated displacement, while retaining every base-difference offset. -/
theorem repeated_offset (f : ℕ→R) (h n u M : ℕ)
    (H : ∀ a, (p:R)^(min a M) ∣ difference h a f n) (k a : ℕ) :
    (p:R)^(min (k*(padicValNat p u+1)+a) M) ∣
      difference h a (difference (u*h) k f) n := by
  induction k generalizing a with
  | zero => simpa using H a
  | succ k ih =>
    have he : difference (u*h) (k+1) f = difference (u*h) 1 (difference (u*h) k f) := by
      rw [difference_compose]; congr 1; omega
    rw [he,StepMultiples.difference_commute_one,difference_one]
    have hd := offset_displacement p (difference h a (difference (u*h) k f)) h n u
      (k*(padicValNat p u+1)+a) M (by
        intro b
        rw [difference_compose]
        simpa only [Nat.add_assoc,Nat.add_comm a b] using ih (a+b))
    simpa only [Nat.succ_mul,Nat.add_assoc,Nat.add_left_comm,Nat.add_comm] using hd

/-- Any natural multiplier: zero step is included because its positive differences vanish. -/
theorem repeated_precision (f : ℕ→R) (h n u M : ℕ)
    (H : ∀ a, (p:R)^(min a M) ∣ difference h a f n) (k : ℕ) :
    (p:R)^(min (k*(padicValNat p u+1)) M) ∣ difference (u*h) k f n := by
  simpa only [Nat.add_zero,difference_zero] using repeated_offset p f h n u M H k 0

end KomorebiPaperIX.StepAmplification
