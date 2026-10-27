import PaperX.PrimeDegreeSummability

/-!
# Degree-one primes in number-field towers

The contraction map, residue degrees and exclusions are actual arithmetic objects.
Nonsummability of the supplied prime set remains an explicit hypothesis.
-/

noncomputable section
set_option autoImplicit false
set_option maxHeartbeats 1000000

namespace PaperX.PrimeDegreeSummabilityTower

open NumberField IsDedekindDomain PrimeDegreeSummability

variable (K L : Type*) [Field K] [Field L] [NumberField K] [NumberField L] [Algebra K L]

/-- Absolute degree one implies relative degree one in an actual number-field tower. -/
theorem relative_degree_one (q : HeightOneSpectrum (𝓞 L))
    (hq : q.asIdeal.inertiaDeg ℤ = 1) : q.asIdeal.inertiaDeg (𝓞 K) = 1 := by
  have ht := Ideal.inertiaDeg_tower (R := ℤ) (q := q.asIdeal.under (𝓞 K)) q.asIdeal
  rw [hq] at ht
  have hpos := (q.asIdeal.under (𝓞 K)).inertiaDeg_pos ℤ
  have hle := Nat.le_mul_of_pos_left (q.asIdeal.inertiaDeg (𝓞 K)) hpos
  have hrel := q.asIdeal.inertiaDeg_pos (𝓞 K)
  omega

/-- Only finitely many actual upper primes contract to a fixed lower prime. -/
theorem finite_under_fibre (p : HeightOneSpectrum (𝓞 K)) :
    {q : HeightOneSpectrum (𝓞 L) | q.under (𝓞 K) = p}.Finite := by
  have hf : {q : HeightOneSpectrum (𝓞 L) | q.asIdeal ∈ p.asIdeal.primesOver (𝓞 L)}.Finite :=
    (Algebra.QuasiFinite.finite_primesOver (S := 𝓞 L) p.asIdeal).preimage
      (fun _ _ _ _ h => HeightOneSpectrum.ext h)
  apply hf.subset
  intro q hq
  have he := congrArg HeightOneSpectrum.asIdeal hq
  exact ⟨q.isPrime, ⟨he.symm⟩⟩

/-- A finite set of lower primes excludes only finitely many upper primes. -/
theorem finite_under_preimage (bad : Set (HeightOneSpectrum (𝓞 K))) (hbad : bad.Finite) :
    ((fun q : HeightOneSpectrum (𝓞 L) => q.under (𝓞 K)) ⁻¹' bad).Finite := by
  apply hbad.preimage'
  intro p _
  exact finite_under_fibre K L p

/-- Divergence supplies a relative degree-one prime outside prescribed lower exclusions. -/
theorem exists_relative_degree_one_outside_finite
    (S : Set (HeightOneSpectrum (𝓞 L)))
    (hS : ¬ Summable (fun q : S => (q.1.asIdeal.absNorm : ℝ)⁻¹))
    (bad : Set (HeightOneSpectrum (𝓞 K))) (hbad : bad.Finite) :
    ∃ q : HeightOneSpectrum (𝓞 L), q ∈ S ∧ q.under (𝓞 K) ∉ bad ∧
      q.asIdeal.inertiaDeg (𝓞 K) = 1 := by
  obtain ⟨q, hq, hb, hd⟩ := exists_degree_one_outside_finite L S hS _
    (finite_under_preimage K L bad hbad)
  exact ⟨q, hq, hb, relative_degree_one K L q hd⟩

/-- Infinitely many such relative degree-one primes survive the lower-field exclusions. -/
theorem infinite_relative_degree_one_outside_finite
    (S : Set (HeightOneSpectrum (𝓞 L)))
    (hS : ¬ Summable (fun q : S => (q.1.asIdeal.absNorm : ℝ)⁻¹))
    (bad : Set (HeightOneSpectrum (𝓞 K))) (hbad : bad.Finite) :
    {q : HeightOneSpectrum (𝓞 L) | q ∈ S ∧ q.under (𝓞 K) ∉ bad ∧
      q.asIdeal.inertiaDeg (𝓞 K) = 1}.Infinite := by
  apply (infinite_degree_one_outside_finite L S hS _
    (finite_under_preimage K L bad hbad)).mono
  intro q hq
  exact ⟨hq.1, hq.2.1, relative_degree_one K L q hq.2.2⟩

end PaperX.PrimeDegreeSummabilityTower
