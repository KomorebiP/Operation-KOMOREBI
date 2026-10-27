module
public import StepAmplification
public import DyadicFourCongruences
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPaperIX.DyadicStepAmplification
open Mahler DyadicFourCongruences

/-- Every power of two in the natural step increases the per-difference precision,
up to the previously proved dyadic row cap. Zero step is included. -/
theorem normalized_bound (j u k n : ℕ) (hj : j<4) :
    (2:ℤ_[2])^(min (k*(padicValNat 2 u+1)) n) ∣
      difference u k (normalizedLift j hj) n := by
  have H := StepAmplification.repeated_precision 2 (normalizedLift j hj) 1 n u n
    (fun a => base_step_bound j a n hj) k
  simpa only [Nat.cast_ofNat,mul_one] using H

/-- The displacement strengthening for the original rational normalized Euler coefficients. -/
theorem normalized_precision (j u k n : ℕ) (hj : j<4) :
    GlobalEulerBoundary.precision 2 ((min (k*(padicValNat 2 u+1)) n:ℕ):ℤ)
      (difference u k (Congruential.coeff 4 j) n) :=
  StandardWindowPrecision.rational_precision_of_divisibility 2
    (difference u k (normalizedLift j hj) n) _ (normalized_difference_coe j u k n hj)
    _ (normalized_bound j u k n hj)

/-- Specializing to step u 2^s supplies at least s+1 digits per difference. -/
theorem prime_power_step_bound (j u s k n : ℕ) (hj : j<4) :
    (2:ℤ_[2])^(min (k*(s+1)) n) ∣
      difference (2^s*u) k (normalizedLift j hj) n := by
  have H := StepAmplification.repeated_precision 2 (normalizedLift j hj) u n (2^s) n
    (fun a => DyadicFourCongruences.normalized_bound j u a n hj) k
  simpa only [Nat.cast_ofNat,padicValNat.prime_pow] using H

/-- The higher-address factorial gain remains visible after step amplification. -/
theorem unnormalized_factorial_bound (j u k n : ℕ) (hj : j<4) :
    (2:ℤ_[2])^(min (k*(padicValNat 2 u+1)) n+padicValNat 2 j.factorial) ∣
      difference u k (unnormalizedLift j hj) n := by
  have hf : (2:ℤ_[2])^(padicValNat 2 j.factorial) ∣ (j.factorial:ℤ_[2]) := by
    obtain ⟨c,hc⟩ := pow_padicValNat_dvd (p:=2) (n:=j.factorial)
    refine ⟨(c:ℤ_[2]), ?_⟩
    simpa only [Nat.cast_mul,Nat.cast_pow,Nat.cast_ofNat] using congrArg (fun a:ℕ => (a:ℤ_[2])) hc
  have he : difference u k (unnormalizedLift j hj) n =
      (j.factorial:ℤ_[2])*difference u k (normalizedLift j hj) n := by
    exact congrFun (difference_mul_const u k (j.factorial:ℤ_[2]) (normalizedLift j hj)) n
  rw [he,pow_add]
  simpa only [mul_comm] using mul_dvd_mul hf (normalized_bound j u k n hj)

/-- Strengthened precision stated directly on j! C_(4,j), including its factorial digit. -/
theorem unnormalized_factorial_precision (j u k n : ℕ) (hj : j<4) :
    GlobalEulerBoundary.precision 2
      ((min (k*(padicValNat 2 u+1)) n+padicValNat 2 j.factorial:ℕ):ℤ)
      (difference u k (Congruential.unnormalized 4 j) n) :=
  StandardWindowPrecision.rational_precision_of_divisibility 2
    (difference u k (unnormalizedLift j hj) n) _ (unnormalized_difference_coe j u k n hj)
    _ (unnormalized_factorial_bound j u k n hj)

end KomorebiPaperIX.DyadicStepAmplification
