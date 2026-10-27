import PaperX.PrimeDegreeSummabilityTower
import Mathlib.RingTheory.Frobenius

/-!
# Frobenius descent at relative degree-one primes

The input is an actual supplied Frobenius endomorphism, not an assertion that a
prime with a prescribed Frobenius exists. The residue congruence descends because
relative degree one makes the two base residue cardinalities equal.
-/

noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000

namespace PaperX.PrimeDegreeSummabilityFrobenius

open NumberField IsDedekindDomain

variable (K E T : Type*) [Field K] [Field E] [Field T]
  [NumberField K] [NumberField E] [NumberField T]
  [Algebra K E] [Algebra E T] [Algebra K T] [IsScalarTower K E T]

omit [NumberField T] in
/-- Residue cardinalities agree below a relative degree-one prime. -/
theorem residue_card_eq_of_degree_one (Q : HeightOneSpectrum (𝓞 T))
    (hdegree : (Q.asIdeal.under (𝓞 E)).inertiaDeg (𝓞 K) = 1) :
    Nat.card (𝓞 E ⧸ Q.asIdeal.under (𝓞 E)) =
      Nat.card (𝓞 K ⧸ Q.asIdeal.under (𝓞 K)) := by
  have hnorm := Ideal.absNorm_pow_inertiaDeg
    (Q.asIdeal.under (𝓞 K)) (Q.asIdeal.under (𝓞 E))
  rw [hdegree, pow_one] at hnorm
  exact hnorm.symm

omit [NumberField T] in
/-- The same actual endomorphism is Frobenius over the lower field at degree one. -/
theorem restrictScalars_isArithFrobAt_of_degree_one
    (φ : (𝓞 T) →ₐ[𝓞 E] (𝓞 T)) (Q : HeightOneSpectrum (𝓞 T))
    (hφ : φ.IsArithFrobAt Q.asIdeal)
    (hdegree : (Q.asIdeal.under (𝓞 E)).inertiaDeg (𝓞 K) = 1) :
    (φ.restrictScalars (𝓞 K)).IsArithFrobAt Q.asIdeal := by
  intro x
  change φ x - x ^ Nat.card (𝓞 K ⧸ Q.asIdeal.under (𝓞 K)) ∈ Q.asIdeal
  rw [← residue_card_eq_of_degree_one K E T Q hdegree]
  exact hφ x

/-- Actual intermediate primes admitting the supplied Frobenius endomorphism upstairs. -/
def prescribedPrimes (φ : (𝓞 T) →ₐ[𝓞 E] (𝓞 T)) : Set (HeightOneSpectrum (𝓞 E)) :=
  {q | ∃ Q : HeightOneSpectrum (𝓞 T), Q.under (𝓞 E) = q ∧ φ.IsArithFrobAt Q.asIdeal}

omit [NumberField T] in
/-- Divergence of the prescribed Frobenius set produces an actual descended Frobenius. -/
theorem exists_descended_frobenius
    (φ : (𝓞 T) →ₐ[𝓞 E] (𝓞 T))
    (hdiv : ¬ Summable (fun q : prescribedPrimes E T φ => (q.1.asIdeal.absNorm : ℝ)⁻¹))
    (bad : Set (HeightOneSpectrum (𝓞 K))) (hbad : bad.Finite) :
    ∃ Q : HeightOneSpectrum (𝓞 T), (Q.under (𝓞 E)).under (𝓞 K) ∉ bad ∧
      (Q.asIdeal.under (𝓞 E)).inertiaDeg (𝓞 K) = 1 ∧
      (φ.restrictScalars (𝓞 K)).IsArithFrobAt Q.asIdeal := by
  obtain ⟨q, hq, hb, hd⟩ :=
    PrimeDegreeSummabilityTower.exists_relative_degree_one_outside_finite K E
      (prescribedPrimes E T φ) hdiv bad hbad
  obtain ⟨Q, hQ, hφ⟩ := hq
  subst q
  exact ⟨Q, hb, hd, restrictScalars_isArithFrobAt_of_degree_one K E T φ Q hφ hd⟩

end PaperX.PrimeDegreeSummabilityFrobenius
