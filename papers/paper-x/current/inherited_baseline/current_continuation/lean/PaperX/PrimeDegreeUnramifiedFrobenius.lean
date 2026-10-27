import PaperX.PrimeDegreeFieldFrobenius
import Mathlib.NumberTheory.NumberField.Discriminant.Different

/-!
# Unramified Frobenius after discriminant exclusions

The excluded set is constructed from the nonzero absolute discriminant of the
upper number field. Its finiteness and actual unramifiedness are proved.
Only nonsummability of the prescribed Frobenius prime set remains assumed.
-/

noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000

namespace PaperX.PrimeDegreeUnramifiedFrobenius

open NumberField IsDedekindDomain PrimeDegreeSummability PrimeDegreeFieldFrobenius

variable (K T : Type*) [Field K] [Field T] [NumberField K] [NumberField T]

/-- Lower primes containing the absolute discriminant of the upper field. -/
def discriminantPrimes : Set (HeightOneSpectrum (𝓞 K)) :=
  {p | (NumberField.discr T : 𝓞 K) ∈ p.asIdeal}

/-- The discriminant exclusion is finite because the discriminant is nonzero. -/
theorem discriminantPrimes_finite : (discriminantPrimes K T).Finite := by
  have hne : (NumberField.discr T : 𝓞 K) ≠ 0 := by
    exact_mod_cast NumberField.discr_ne_zero T
  exact (Ring.HasFiniteQuotients.finite_setOfPred_mem (NumberField.discr T : 𝓞 K) hne).preimage
    (fun _ _ _ _ h => HeightOneSpectrum.ext h)

/-- Avoiding the absolute discriminant gives actual unramifiedness over the integers. -/
theorem isUnramifiedAt_int_of_discriminant_notMem (Q : HeightOneSpectrum (𝓞 T))
    (hdisc : (NumberField.discr T : 𝓞 T) ∉ Q.asIdeal) :
    Algebra.IsUnramifiedAt ℤ Q.asIdeal := by
  let p := rationalPrimeBelow T Q
  have hp : Prime (p.1 : ℤ) := Nat.prime_iff_prime_int.mp p.2
  have hnd : ¬ (p.1 : ℤ) ∣ NumberField.discr T := by
    rintro ⟨a, ha⟩
    apply hdisc
    rw [ha, Int.cast_mul]
    apply Q.asIdeal.mul_mem_right
    simpa only [p, rationalPrimeBelow, Int.cast_natCast] using Int.absNorm_under_mem Q.asIdeal
  exact (NumberField.not_dvd_discr_iff_forall_liesOver T (𝓞 T) hp).mp hnd
    Q.asIdeal inferInstance (Int.liesOver_span_absNorm Q.asIdeal)

variable [Algebra K T]

omit [NumberField K] in
/-- The constructed lower exclusion ensures unramifiedness over the lower number field. -/
theorem isUnramifiedAt_of_notMem_discriminantPrimes (Q : HeightOneSpectrum (𝓞 T))
    (hQ : Q.under (𝓞 K) ∉ discriminantPrimes K T) :
    Algebra.IsUnramifiedAt (𝓞 K) Q.asIdeal := by
  have hdisc : (NumberField.discr T : 𝓞 T) ∉ Q.asIdeal := by
    simpa only [discriminantPrimes, Set.mem_ofPred_eq, HeightOneSpectrum.under_asIdeal,
      Ideal.under, Ideal.mem_comap, map_intCast] using hQ
  have := isUnramifiedAt_int_of_discriminant_notMem T Q hdisc
  exact Algebra.IsUnramifiedAt.of_restrictScalars ℤ Q.asIdeal

/-- Nonsummability alone supplies the prescribed actual unramified Frobenius after exclusions. -/
theorem exists_unramified_fixedField_frobenius
    (ρ : T ≃ₐ[K] T)
    (hdiv : ¬ Summable
      (fun q : prescribedPrimes (IntermediateField.fixedField (Subgroup.zpowers ρ)) T
        (overFixedField K T ρ) => (q.1.asIdeal.absNorm : ℝ)⁻¹))
    (bad : Set (HeightOneSpectrum (𝓞 K))) (hbad : bad.Finite) :
    ∃ Q : HeightOneSpectrum (𝓞 T), Q.under (𝓞 K) ∉ bad ∧
      Algebra.IsUnramifiedAt (𝓞 K) Q.asIdeal ∧
      (integralAut K T ρ).toAlgHom.IsArithFrobAt Q.asIdeal := by
  obtain ⟨Q, hb, _, hF⟩ := exists_fixedField_descended_frobenius K T ρ hdiv
    (bad ∪ discriminantPrimes K T) (hbad.union (discriminantPrimes_finite K T))
  have ht :
      (Q.under (𝓞 (IntermediateField.fixedField (Subgroup.zpowers ρ)))).under (𝓞 K) =
        Q.under (𝓞 K) := by
    apply HeightOneSpectrum.ext
    change (Q.asIdeal.under (𝓞 (IntermediateField.fixedField (Subgroup.zpowers ρ)))).under
      (𝓞 K) = Q.asIdeal.under (𝓞 K)
    rw [Ideal.under_under]
  rw [ht] at hb
  have hdisc : Q.under (𝓞 K) ∉ discriminantPrimes K T := fun h => hb (Or.inr h)
  exact ⟨Q, (fun h => hb (Or.inl h)),
    isUnramifiedAt_of_notMem_discriminantPrimes K T Q hdisc, hF⟩

end PaperX.PrimeDegreeUnramifiedFrobenius
