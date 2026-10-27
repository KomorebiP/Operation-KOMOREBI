module

public import PaperX.CyclotomicNormDictionary

/-!
# Boundary limits for cyclotomic Artin series with modulus primes removed

The coefficients are the actual Frobenius ideal coefficients, with all prime
factors dividing the modulus removed. The cyclotomic/norm dictionary identifies
them with the actual norm-residue characters, whose cancellation and boundary
limits have already been proved. The remaining finite Euler factors are
restored in a separate module.
-/
@[expose] public section
noncomputable section
open NumberField Chebotarev Filter
open PaperX.ArtinLocalFactors PaperX.FrobeniusArtinDomination
open PaperX.NormResidueBoundary PaperX.CyclotomicNormDictionary
open scoped nonZeroDivisors Topology
namespace PaperX.CyclotomicGoodBoundary

/-- The residue of an actual nonzero ideal whose norm is coprime to the modulus. -/
def normResidue (K : Type*) [Field K] [NumberField K] (m : ℕ) [NeZero m]
    (I : NonzeroIdeal K) (hc : (Ideal.absNorm I.1).Coprime m) : realizedResidues K m :=
  ⟨ZMod.unitOfCoprime (Ideal.absNorm I.1) hc,
    ⟨⟨I.1, mem_nonZeroDivisors_of_ne_zero I.2⟩, by rw [ZMod.coe_unitOfCoprime]⟩⟩

theorem normResidue_val (K : Type*) [Field K] [NumberField K] (m : ℕ) [NeZero m]
    (I : NonzeroIdeal K) (hc : (Ideal.absNorm I.1).Coprime m) :
    ((normResidue K m I hc : (ZMod m)ˣ) : ZMod m) = (Ideal.absNorm I.1 : ZMod m) :=
  ZMod.coe_unitOfCoprime _ hc

theorem weight_coprime (K : Type*) [Field K] [NumberField K] (m : ℕ) [NeZero m]
    (ψ : realizedResidues K m →* ℂˣ) (I : NonzeroIdeal K)
    (hc : (Ideal.absNorm I.1).Coprime m) :
    weight (K := K) (m := m) ψ I = (ψ (normResidue K m I hc) : ℂ) := by
  rw [weight, ← normResidue_val K m I hc, value_apply]

theorem weight_noncoprime (K : Type*) [Field K] [NumberField K] (m : ℕ) [NeZero m]
    (ψ : realizedResidues K m →* ℂˣ) (I : NonzeroIdeal K)
    (hc : ¬ (Ideal.absNorm I.1).Coprime m) : weight (K := K) (m := m) ψ I = 0 := by
  classical
  apply Finset.sum_eq_zero
  intro u _
  apply ite_eq_right
  intro h
  exact hc ((ZMod.isUnit_iff_coprime _ m).mp (h ▸ (u : (ZMod m)ˣ).isUnit))

theorem normResidue_mul (K : Type*) [Field K] [NumberField K] (m : ℕ) [NeZero m]
    (I J : NonzeroIdeal K) (hI : (Ideal.absNorm I.1).Coprime m)
    (hJ : (Ideal.absNorm J.1).Coprime m)
    (hIJ : (Ideal.absNorm (I.1 * J.1)).Coprime m) :
    normResidue K m ⟨I.1 * J.1, mul_ne_zero I.2 J.2⟩ hIJ =
      normResidue K m I hI * normResidue K m J hJ := by
  apply Subtype.ext
  apply Units.ext
  simp only [Subgroup.coe_mul, Units.val_mul, normResidue_val, map_mul, Nat.cast_mul]

set_option backward.isDefEq.respectTransparency false in
theorem weight_mul_coprime (K : Type*) [Field K] [NumberField K] (m : ℕ) [NeZero m]
    (ψ : realizedResidues K m →* ℂˣ) (I J : NonzeroIdeal K)
    (hI : (Ideal.absNorm I.1).Coprime m) (hJ : (Ideal.absNorm J.1).Coprime m) :
    weight (K := K) (m := m) ψ ⟨I.1 * J.1, mul_ne_zero I.2 J.2⟩ = weight (K := K) (m := m) ψ I * weight (K := K) (m := m) ψ J := by
  have hnorm : Ideal.absNorm (I.1 * J.1) = Ideal.absNorm I.1 * Ideal.absNorm J.1 :=
    map_mul Ideal.absNorm I.1 J.1
  have hIJ : (Ideal.absNorm (I.1 * J.1)).Coprime m := hnorm.symm ▸ hI.mul_left hJ
  have hleft : weight (K := K) (m := m) ψ ⟨I.1 * J.1, mul_ne_zero I.2 J.2⟩ =
      (ψ (normResidue K m ⟨I.1 * J.1, mul_ne_zero I.2 J.2⟩ hIJ) : ℂ) :=
    weight_coprime K m ψ ⟨I.1 * J.1, mul_ne_zero I.2 J.2⟩ hIJ
  have he := congrArg (fun u : realizedResidues K m ↦ (ψ u : ℂ))
    (normResidue_mul K m I J hI hJ hIJ)
  have hm : (ψ (normResidue K m I hI * normResidue K m J hJ) : ℂ) =
      (ψ (normResidue K m I hI) : ℂ) * (ψ (normResidue K m J hJ) : ℂ) :=
    congrArg Units.val (map_mul ψ (normResidue K m I hI) (normResidue K m J hJ))
  exact hleft.trans (he.trans (hm.trans (congrArg₂ (fun a b : ℂ ↦ a * b)
    (weight_coprime K m ψ I hI).symm (weight_coprime K m ψ J hJ).symm)))


open Classical in
def goodCoefficient (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (m : ℕ) (χ : Character K L) (I : Ideal (𝓞 K)) : ℂ :=
  if (Ideal.absNorm I).Coprime m then idealCoefficient K L χ I else 0

def goodSeries (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (m : ℕ) (χ : Character K L) (s : ℂ) : ℂ :=
  ∑' I : NonzeroIdeal K, goodCoefficient K L m χ I.1 * (Ideal.absNorm I.1 : ℂ) ^ (-s)

section Identification
variable (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
  [Algebra K L] [IsGalois K L] [IsMulCommutative Gal(L/K)]
  (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} K L] {ζ : L} (hζ : IsPrimitiveRoot ζ m)
  (χ : Character K L)

def residueCharacter : realizedResidues K m →* ℂˣ :=
  χ.comp (galResidueEquiv K L m hζ).symm.toMonoidHom

theorem residueCharacter_nontrivial (hχ : χ ≠ 1) : residueCharacter K L m hζ χ ≠ 1 := by
  intro h
  apply hχ
  apply MonoidHom.ext
  intro g
  have he := congrArg (fun ψ : realizedResidues K m →* ℂˣ ↦
    ψ (galResidueEquiv K L m hζ g)) h
  simpa only [residueCharacter, MonoidHom.comp_apply, MulEquiv.coe_toMonoidHom,
    MulEquiv.symm_apply_apply, MonoidHom.one_apply] using he

/-- Prime-level identity with actual arithmetic Frobenius. -/
theorem prime_weight_eq (p : Ideal (𝓞 K)) [p.IsPrime] (hp : p ≠ ⊥)
    (hc : (Ideal.absNorm p).Coprime m) :
    weight (residueCharacter K L m hζ χ) ⟨p, hp⟩ = idealCoefficient K L χ p := by
  have hu := unramified_of_coprime K L m p hp hc
  have he : galResidueEquiv K L m hζ (frobeniusClass K L p).out =
      normResidue K m ⟨p, hp⟩ hc := by
    apply Subtype.ext
    rw [galResidueEquiv_val, autToPow_frobeniusClass_out K L m hζ p hu hc]
    rfl
  rw [coefficient_prime K L χ p hp, ite_eq_left hu,
    weight_coprime K m _ ⟨p, hp⟩ hc, ← he]
  simp only [residueCharacter, MonoidHom.comp_apply, MulEquiv.coe_toMonoidHom,
    MulEquiv.symm_apply_apply]

/-- The prime dictionary extends through exact ideal factorization. -/
theorem coefficient_eq_weight_of_coprime (I : Ideal (𝓞 K)) (hI : I ≠ ⊥)
    (hc : (Ideal.absNorm I).Coprime m) :
    idealCoefficient K L χ I = weight (residueCharacter K L m hζ χ) ⟨I, hI⟩ := by
  classical
  revert hI hc
  induction I using UniqueFactorizationMonoid.induction_on_prime with
  | h₁ => exact fun hI _ ↦ absurd rfl hI
  | h₂ I hunit =>
      intro hI _
      obtain rfl : I = ⊤ := Ideal.isUnit_iff.mp hunit
      rw [coefficient_one, weight, Ideal.absNorm_top, Nat.cast_one]
      simpa only [OneMemClass.coe_one, Units.val_one, map_one, Units.val_one] using
        (value_apply (residueCharacter K L m hζ χ) 1).symm
  | h₃ I p hI hp ih =>
      intro hpI hc
      have : p.IsPrime := Ideal.isPrime_of_prime hp
      have hs : Ideal.absNorm (p * I) = Ideal.absNorm p * Ideal.absNorm I := map_mul _ _ _
      have hcp : (Ideal.absNorm p).Coprime m :=
        Nat.Coprime.coprime_dvd_left (Dvd.intro _ rfl) (hs ▸ hc)
      have hcI : (Ideal.absNorm I).Coprime m :=
        Nat.Coprime.coprime_dvd_left (Dvd.intro_left _ rfl) (hs ▸ hc)
      rw [coefficient_mul K L χ hp.ne_zero hI, ih hI hcI,
        ← prime_weight_eq K L m hζ χ p hp.ne_zero hcp]
      exact (weight_mul_coprime K m _ ⟨p, hp.ne_zero⟩ ⟨I, hI⟩ hcp hcI).symm

/-- Full coefficient identity, including zero at noncoprime norm. -/
theorem goodCoefficient_eq_weight (I : NonzeroIdeal K) :
    goodCoefficient K L m χ I.1 = weight (residueCharacter K L m hζ χ) I := by
  classical
  by_cases hc : (Ideal.absNorm I.1).Coprime m
  · rw [goodCoefficient, ite_eq_left hc]
    exact coefficient_eq_weight_of_coprime K L m hζ χ I.1 I.2 hc
  · rw [goodCoefficient, ite_eq_right hc, weight_noncoprime K m _ I hc]

/-- An actual boundary limit; no analytic continuation or cancellation hypothesis
is supplied. This series currently omits every modulus prime. -/
theorem goodSeries_boundary_limit (hχ : χ ≠ 1) :
    ∃ v : ℂ, Tendsto (fun s : ℝ ↦ goodSeries K L m χ (s : ℂ)) (𝓝[>] 1) (𝓝 v) := by
  obtain ⟨ζ, hζ⟩ := IsCyclotomicExtension.exists_isPrimitiveRoot K L
    (Set.mem_singleton m) (NeZero.ne m)
  obtain ⟨v, hv⟩ := actual_boundary_limit K m (residueCharacter K L m hζ χ)
    (residueCharacter_nontrivial K L m hζ χ hχ)
  refine ⟨v, hv.congr fun s ↦ ?_⟩
  apply tsum_congr
  intro I
  rw [← goodCoefficient_eq_weight K L m hζ χ I]

end Identification
end PaperX.CyclotomicGoodBoundary
