module
public import DyadicFourDwork
public import SeriesDifferenceBridge
public import PeriodFromDifferences
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.DyadicFourCongruences
open PowerSeries DyadicFourDwork HurwitzDworkClosure SeriesDifferenceBridge DworkCriterion Mahler

theorem packet_integral_series (j:ℕ) (hj:j<4) :
    rationalMap 2 (ExponentialSection.expandedPacket 4 (by decide) j) ∈ integralSeries 2 := by
  exact actual_packet_flat j hj 0

/-- The original normalized Euler sequence, as an actual integral lift. -/
def normalizedLift (j:ℕ) (hj:j<4) : ℕ→ℤ_[2] :=
  packetLift 2 4 (ExponentialSection.expandedPacket 4 (by decide) j) (packet_integral_series j hj)

theorem decode_packet (j n:ℕ) :
    EGF.decode (ExponentialSection.expandedPacket 4 (by decide) j) (4*n) =
      Congruential.coeff 4 j n := by
  rw [EGF.decode,ExponentialSection.packet_coefficient_at_address]
  have hn : ((4*n).factorial:ℚ)≠0 := Nat.cast_ne_zero.mpr (Nat.factorial_ne_zero _)
  field_simp

@[simp] theorem normalizedLift_coe (j n:ℕ) (hj:j<4) :
    (normalizedLift j hj n:ℚ_[2]) = ((Congruential.coeff 4 j n:ℚ):ℚ_[2]) := by
  rw [normalizedLift,packetLift_coe,decode_packet]

/-- Support on multiples of four is a coefficient theorem about the original series. -/
theorem packet_support (j d:ℕ) (hd:¬4∣d) :
    coeff d (ExponentialSection.expandedPacket 4 (by decide) j)=0 :=
  coeff_expand_of_not_dvd 4 (by decide) _ hd

theorem lifted_flat (j:ℕ) (hj:j<4) : CoeffFlat4 (packed 4 (normalizedLift j hj)) := by
  apply (flat4_encode_iff _).mp
  rw [normalizedLift,packet_encoding 2 4 _ _ (packet_support j)]
  exact actual_packet_flat j hj

/-- Extract the larger dyadic defect at degree 4n-4k, then saturate all difference orders. -/
theorem base_step_bound (j k n:ℕ) (hj:j<4) :
    (2:ℤ_[2])^(min k n) ∣ difference 1 k (normalizedLift j hj) n := by
  have H := DifferenceFiltration.saturated_bound_of_triangular (2:ℤ_[2]) 1 1
    (normalizedLift j hj) ?_ k n
  · simpa only [one_mul] using H
  · intro r s hs
    have hd := lifted_flat j hj s (4*r-4*s)
    have he := defect_packet_extraction 4 1 1 s r (by decide) hs (normalizedLift j hj)
    simpa only [one_mul,mul_one,he] using hd

/-- Full dyadic N=4 bound, derived from actual source flatness and reciprocal closure. -/
theorem normalized_bound (j u k n:ℕ) (hj:j<4) :
    (2:ℤ_[2])^(min k n) ∣ difference u k (normalizedLift j hj) n := by
  have H := StepMultiples.saturated_multiple_step (2:ℤ_[2]) 1 1 (normalizedLift j hj)
    (fun k n => by simpa only [one_mul] using base_step_bound j k n hj) u k n
  simpa only [one_mul,mul_one] using H

/-- Rational finite differences coincide with the differences of the integral lift. -/
theorem normalized_difference_coe (j u k n:ℕ) (hj:j<4) :
    ((difference u k (normalizedLift j hj) n:ℤ_[2]):ℚ_[2]) =
      ((difference u k (Congruential.coeff 4 j) n:ℚ):ℚ_[2]) := by
  change (algebraMap ℤ_[2] ℚ_[2]) (difference _ _ _ _) =
    (algebraMap ℚ ℚ_[2]) (difference _ _ _ _)
  rw [←DifferenceFiltration.difference_map,←DifferenceFiltration.difference_map]
  congr 1
  funext r
  exact normalizedLift_coe j r hj

theorem normalized_precision (j u k n:ℕ) (hj:j<4) :
    GlobalEulerBoundary.precision 2 ((min k n:ℕ):ℤ)
      (difference u k (Congruential.coeff 4 j) n) :=
  StandardWindowPrecision.rational_precision_of_divisibility 2
    (difference u k (normalizedLift j hj) n) _ (normalized_difference_coe j u k n hj)
    _ (normalized_bound j u k n hj)

/-- Multiplication by j! matches the author's original unnormalized coefficients. -/
def unnormalizedLift (j:ℕ) (hj:j<4) (n:ℕ) : ℤ_[2] :=
  (j.factorial:ℤ_[2])*normalizedLift j hj n

@[simp] theorem unnormalizedLift_coe (j n:ℕ) (hj:j<4) :
    (unnormalizedLift j hj n:ℚ_[2]) = ((Congruential.unnormalized 4 j n:ℚ):ℚ_[2]) := by
  simp [unnormalizedLift,Congruential.unnormalized]

theorem unnormalized_integral (j n:ℕ) (hj:j<4) :
    ((Congruential.unnormalized 4 j n:ℚ):ℚ_[2]) ∈ PadicInt.subring 2 := by
  rw [←unnormalizedLift_coe j n hj]
  exact (unnormalizedLift j hj n).property

theorem unnormalized_difference_coe (j u k n:ℕ) (hj:j<4) :
    ((difference u k (unnormalizedLift j hj) n:ℤ_[2]):ℚ_[2]) =
      ((difference u k (Congruential.unnormalized 4 j) n:ℚ):ℚ_[2]) := by
  change (algebraMap ℤ_[2] ℚ_[2]) (difference _ _ _ _) =
    (algebraMap ℚ ℚ_[2]) (difference _ _ _ _)
  rw [←DifferenceFiltration.difference_map,←DifferenceFiltration.difference_map]
  congr 1
  funext r
  exact unnormalizedLift_coe j r hj

theorem unnormalized_bound (j u k n:ℕ) (hj:j<4) :
    (2:ℤ_[2])^(min k n) ∣ difference u k (unnormalizedLift j hj) n := by
  have he : difference u k (unnormalizedLift j hj) n =
      (j.factorial:ℤ_[2])*difference u k (normalizedLift j hj) n := by
    induction k generalizing n with
    | zero => rfl
    | succ k ih => rw [difference_succ,ih,ih,difference_succ,mul_sub]
  rw [he]
  exact dvd_mul_of_dvd_right (normalized_bound j u k n hj) _

theorem unnormalized_precision (j u k n:ℕ) (hj:j<4) :
    GlobalEulerBoundary.precision 2 ((min k n:ℕ):ℤ)
      (difference u k (Congruential.unnormalized 4 j) n) :=
  StandardWindowPrecision.rational_precision_of_divisibility 2
    (difference u k (unnormalizedLift j hj) n) _ (unnormalized_difference_coe j u k n hj)
    _ (unnormalized_bound j u k n hj)

/-- The dyadic period required by Conjecture 3.9, as genuine ideal divisibility. -/
theorem dyadic_period (j r n:ℕ) (hj:j<4) (hr:0<r) (hn:r≤n) :
    (2:ℤ_[2])^r ∣ unnormalizedLift j hj (n+2^(r-1))-unnormalizedLift j hj n := by
  have H := PeriodFromDifferences.prime_power_period 2 (unnormalizedLift j hj) 1 n r hr ?_
  · simpa only [Nat.cast_ofNat,mul_one] using H
  · intro k
    exact dvd_trans (pow_dvd_pow _ (min_le_min_left k hn)) (unnormalized_bound j 1 k n hj)

/-- The period stated literally for the original rational numbers, with zero safe. -/
theorem dyadic_period_precision (j r n:ℕ) (hj:j<4) (hr:0<r) (hn:r≤n) :
    GlobalEulerBoundary.precision 2 (r:ℤ)
      (Congruential.unnormalized 4 j (n+2^(r-1))-Congruential.unnormalized 4 j n) := by
  apply StandardWindowPrecision.rational_precision_of_divisibility 2
    (unnormalizedLift j hj (n+2^(r-1))-unnormalizedLift j hj n)
  · simp only [PadicInt.coe_sub,unnormalizedLift_coe,Rat.cast_sub]
  · exact dyadic_period j r n hj hr hn

end KomorebiPaperIX.DyadicFourCongruences
