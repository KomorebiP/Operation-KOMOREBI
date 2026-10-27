module

public import PaperX.NormResidueBoundary
public import PaperX.ArtinLocalFactors
public import CebotarevDensity.CyclotomicNormResidue
public import Mathlib.NumberTheory.NumberField.Cyclotomic.Basic
public import Mathlib.NumberTheory.Cyclotomic.Gal
public import Mathlib.RingTheory.DedekindDomain.Different

/-!
# Constructing the cyclotomic Frobenius/norm dictionary

The image of the cyclotomic character is identified with the subgroup of
actual ideal-norm residues. The good-prime Artin coefficients are then actual
norm-residue character coefficients. No prescribed Frobenius-class occurrence
or class field theory interface is supplied.
-/
@[expose] public section
noncomputable section
open NumberField Chebotarev
open PaperX.ArtinLocalFactors PaperX.FrobeniusArtinDomination PaperX.NormResidueBoundary
open scoped nonZeroDivisors Topology
namespace PaperX.CyclotomicNormDictionary

/-- A prime with norm coprime to the cyclotomic modulus is actually unramified.
This conductor/different argument adapts the corresponding upstream proof. -/
theorem unramified_of_coprime
    (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
    [Algebra K L] [IsGalois K L] (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} K L]
    (p : Ideal (𝓞 K)) [p.IsPrime] (hp : p ≠ ⊥) (hc : (Ideal.absNorm p).Coprime m) :
    UnramifiedIn K L p := by
  classical
  refine ⟨hp, fun P hPm hPl ↦ ?_⟩
  have := hPl
  have : P.IsPrime := hPm.isPrime
  rw [← not_dvd_differentIdeal_iff (A := 𝓞 K) (B := 𝓞 L)]
  intro hdiv
  obtain ⟨ζ, hζ⟩ := IsCyclotomicExtension.exists_isPrimitiveRoot K L
    (Set.mem_singleton m) (NeZero.ne m)
  let z : 𝓞 L := hζ.toInteger
  have hz : z ^ m = 1 := hζ.toInteger_isPrimitiveRoot.pow_eq_one
  have hd : minpoly (𝓞 K) z ∣ Polynomial.X ^ m - 1 := by
    refine minpoly.isIntegrallyClosed_dvd (Algebra.IsIntegral.isIntegral z) ?_
    simp [hz]
  obtain ⟨g, hg⟩ := hd
  have hkey : (m : 𝓞 L) * z ^ (m - 1) =
      Polynomial.aeval z (Polynomial.derivative (minpoly (𝓞 K) z)) * Polynomial.aeval z g := by
    have h := congrArg (Polynomial.aeval z ∘ Polynomial.derivative) hg
    simp only [Function.comp_apply, Polynomial.derivative_one, Polynomial.derivative_X_pow,
      Polynomial.derivative_mul, map_sub, map_mul, map_add, map_pow, Polynomial.aeval_X,
      minpoly.aeval, zero_mul, add_zero, sub_zero, Polynomial.aeval_C] at h
    simpa using h
  have hadj : Algebra.adjoin K {algebraMap (𝓞 L) L z} = ⊤ := by
    rw [show algebraMap (𝓞 L) L z = ζ from hζ.coe_toInteger]
    exact IsCyclotomicExtension.adjoin_primitive_root_eq_top hζ
  have hdiff : differentIdeal (𝓞 K) (𝓞 L) ∣
      Ideal.span {Polynomial.aeval z (Polynomial.derivative (minpoly (𝓞 K) z))} :=
    ⟨conductor (𝓞 K) z, by rw [← conductor_mul_differentIdeal (𝓞 K) K L z hadj]; ring⟩
  have hmem : (m : 𝓞 L) * z ^ (m - 1) ∈ P := by
    rw [hkey]
    exact Ideal.mul_mem_right _ _
      ((Ideal.dvd_iff_le.mp (dvd_trans hdiv hdiff)) (Ideal.mem_span_singleton_self _))
  have hmP : (m : 𝓞 L) ∈ P := by
    rcases ‹P.IsPrime›.mem_or_mem hmem with h | h
    · exact h
    · exact absurd (Ideal.eq_top_of_isUnit_mem _ h
        ((IsUnit.of_pow_eq_one hz (NeZero.ne m)).pow _)) ‹P.IsPrime›.ne_top
  have hmp : (m : 𝓞 K) ∈ p := by
    have hmap : algebraMap (𝓞 K) (𝓞 L) (m : 𝓞 K) ∈ P := by rwa [map_natCast]
    rw [hPl.over]
    exact Ideal.mem_comap.mpr hmap
  have hn : Ideal.absNorm p ∣ m ^ Module.finrank ℤ (𝓞 K) := by
    have hle : Ideal.span {(m : 𝓞 K)} ≤ p := (Ideal.span_singleton_le_iff_mem _).mpr hmp
    have h := Ideal.absNorm_dvd_absNorm_of_le hle
    rwa [Ideal.absNorm_span_singleton,
      show (m : 𝓞 K) = algebraMap ℤ (𝓞 K) (m : ℤ) by push_cast; rfl,
      Algebra.norm_algebraMap, Int.natAbs_pow, Int.natAbs_natCast] at h
  exact absurd (Ideal.absNorm_eq_one_iff.mp
    (Nat.eq_one_of_dvd_coprimes (hc.pow_right _) dvd_rfl hn)) ‹p.IsPrime›.ne_top

section Dictionary
variable (K L : Type*) [Field K] [NumberField K] [Field L] [NumberField L]
  [Algebra K L] [IsGalois K L] [IsMulCommutative Gal(L/K)]
  (m : ℕ) [NeZero m] [IsCyclotomicExtension {m} K L] {ζ : L} (hζ : IsPrimitiveRoot ζ m)

/-- Every Galois-character image is realized by an actual ideal norm. -/
theorem range_le_realized : (hζ.autToPow K).range ≤ realizedResidues K m := by
  let H := Subgroup.comap (hζ.autToPow K) (realizedResidues K m)
  have ht : H = ⊤ := by
    refine subgroup_eq_top_of_forall_frobenius_mem_of_coprime K L m H
      (fun p hpp hp hu hc ↦ ?_)
    have := hpp
    change hζ.autToPow K (frobeniusClass K L p).out ∈ realizedResidues K m
    rw [autToPow_frobeniusClass_out K L m hζ p hu hc]
    exact ⟨⟨p, mem_nonZeroDivisors_of_ne_zero hp⟩, by rw [ZMod.coe_unitOfCoprime]⟩
  rintro a ⟨g, rfl⟩
  have h : g ∈ H := ht ▸ Subgroup.mem_top g
  exact h

omit [IsMulCommutative Gal(L/K)] in
/-- The converse image inclusion follows by prime factorization and actual
cyclotomic Frobenius action; it is not a surjectivity assumption. -/
theorem coprime_norm_mem_range (I : Ideal (𝓞 K)) (hI : I ≠ ⊥)
    (hc : (Ideal.absNorm I).Coprime m) :
    ZMod.unitOfCoprime (Ideal.absNorm I) hc ∈ (hζ.autToPow K).range := by
  classical
  revert hI hc
  induction I using UniqueFactorizationMonoid.induction_on_prime with
  | h₁ => exact fun hI _ ↦ absurd rfl hI
  | h₂ I hunit =>
      intro _ hc
      obtain rfl : I = ⊤ := Ideal.isUnit_iff.mp hunit
      have h1 : ZMod.unitOfCoprime (Ideal.absNorm (⊤ : Ideal (𝓞 K))) hc = 1 := by
        apply Units.ext
        simp [ZMod.coe_unitOfCoprime]
      rw [h1]
      exact (hζ.autToPow K).range.one_mem
  | h₃ I p hI hp ih =>
      intro _ hc
      have hpp : p.IsPrime := Ideal.isPrime_of_prime hp
      have := hpp
      have hs : Ideal.absNorm (p * I) = Ideal.absNorm p * Ideal.absNorm I := map_mul _ _ _
      have hcp : (Ideal.absNorm p).Coprime m :=
        Nat.Coprime.coprime_dvd_left (Dvd.intro _ rfl) (hs ▸ hc)
      have hcI : (Ideal.absNorm I).Coprime m :=
        Nat.Coprime.coprime_dvd_left (Dvd.intro_left _ rfl) (hs ▸ hc)
      have hu := unramified_of_coprime K L m p hp.ne_zero hcp
      have hmemp : ZMod.unitOfCoprime (Ideal.absNorm p) hcp ∈ (hζ.autToPow K).range :=
        ⟨(frobeniusClass K L p).out, autToPow_frobeniusClass_out K L m hζ p hu hcp⟩
      have heq : ZMod.unitOfCoprime (Ideal.absNorm (p * I)) hc =
          ZMod.unitOfCoprime (Ideal.absNorm p) hcp * ZMod.unitOfCoprime (Ideal.absNorm I) hcI := by
        apply Units.ext
        simp [ZMod.coe_unitOfCoprime, hs]
      rw [heq]
      exact (hζ.autToPow K).range.mul_mem hmemp (ih hI hcI)

omit [IsMulCommutative Gal(L/K)] in
theorem realized_le_range : realizedResidues K m ≤ (hζ.autToPow K).range := by
  rintro a ⟨I, hI⟩
  have hc : (Ideal.absNorm (I : Ideal (𝓞 K))).Coprime m :=
    (ZMod.isUnit_iff_coprime _ m).mp (hI ▸ a.isUnit)
  have h := coprime_norm_mem_range K L m hζ I (by simpa using nonZeroDivisors.coe_ne_zero I) hc
  have heq : ZMod.unitOfCoprime (Ideal.absNorm (I : Ideal (𝓞 K))) hc = a :=
    Units.ext (by rw [ZMod.coe_unitOfCoprime]; exact hI)
  rwa [heq] at h

/-- The Galois group is identified with the actual norm-residue image. -/
def galResidueEquiv : Gal(L/K) ≃* realizedResidues K m :=
  let f : Gal(L/K) →* realizedResidues K m :=
    { toFun := fun g ↦ ⟨hζ.autToPow K g, range_le_realized K L m hζ ⟨g, rfl⟩⟩
      map_one' := Subtype.ext (map_one _)
      map_mul' := fun a b ↦ Subtype.ext (map_mul _ a b) }
  MulEquiv.ofBijective f
    ⟨fun a b h ↦ IsPrimitiveRoot.autToPow_injective K hζ (congrArg (fun u : realizedResidues K m ↦ u.1) h),
      fun u ↦ by
        obtain ⟨g, hg⟩ := realized_le_range K L m hζ u.2
        exact ⟨g, Subtype.ext hg⟩⟩

theorem galResidueEquiv_val (g : Gal(L/K)) :
    (galResidueEquiv K L m hζ g : (ZMod m)ˣ) = hζ.autToPow K g := rfl

end Dictionary
end PaperX.CyclotomicNormDictionary
