import PaperX.ProfiniteSeparation
import Mathlib.NumberTheory.NumberField.Cyclotomic.Galois
import Mathlib.NumberTheory.LSeries.PrimesInAP

/-! Actual prime coverage of the cyclotomic Galois group, with any fixed finite
set of rational primes removed. The arithmetic prime-existence input is Mathlib's
proved Dirichlet theorem, not a supplied coverage predicate. The sample is an
actual automorphism of the cyclotomic number field. Its membership in the
decomposition group and its p-power action on the residue field are proved
below, giving the arithmetic Frobenius convention explicitly. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CyclotomicPrimeCoverage
open NumberField

variable (n : ℕ) [NeZero n]

/-- A rational prime coprime to the conductor, outside the prescribed finite set. -/
def PermittedPrime (forbidden : Finset ℕ) :=
  {p : ℕ // p.Prime ∧ p.Coprime n ∧ p ∉ forbidden}

/-- The actual residue of a permitted prime in the group of units. -/
def primeResidue (forbidden : Finset ℕ) (p : PermittedPrime n forbidden) : (ZMod n)ˣ :=
  ZMod.unitOfCoprime p.val p.property.2.1

/-- Dirichlet's theorem allows every unit residue while avoiding any finite set
and retaining an arbitrary strict lower bound. -/
theorem exists_prime_with_residue (forbidden : Finset ℕ) (u : (ZMod n)ˣ) (B : ℕ) :
    ∃ p : PermittedPrime n forbidden, B < p.val ∧ primeResidue n forbidden p = u := by
  classical
  obtain ⟨p, hpgt, hp, hres⟩ := Nat.forall_exists_prime_gt_and_eq_mod u.isUnit
    (max B (forbidden.sup id))
  have hc : p.Coprime n := (ZMod.isUnit_iff_coprime p n).mp (hres ▸ u.isUnit)
  have hn : p ∉ forbidden := by
    intro hm
    have hle : p ≤ forbidden.sup id := Finset.le_sup (f := id) hm
    exact (not_lt_of_ge (hle.trans (le_max_right _ _))) hpgt
  refine ⟨⟨p, hp, hc, hn⟩, (le_max_left _ _).trans_lt hpgt, ?_⟩
  apply Units.ext
  exact hres

theorem primeResidue_surjective (forbidden : Finset ℕ) :
    Function.Surjective (primeResidue n forbidden) := by
  intro u
  obtain ⟨p, _, hp⟩ := exists_prime_with_residue n forbidden u 0
  exact ⟨p, hp⟩

variable (K : Type*) [Field K] [NumberField K] [IsCyclotomicExtension {n} ℚ K]

/-- The actual cyclotomic automorphism whose root-of-unity exponent is p. -/
def primePowerAutomorphism (p : ℕ) (hp : p.Coprime n) : Gal(K/ℚ) :=
  (IsCyclotomicExtension.Rat.galEquivZMod n K).symm (ZMod.unitOfCoprime p hp)

/-- Prime-indexed automorphisms of the actual cyclotomic number field. -/
def primeSample (forbidden : Finset ℕ) (p : PermittedPrime n forbidden) : Gal(K/ℚ) :=
  primePowerAutomorphism n K p.val p.property.2.1

@[simp] theorem galEquiv_primePowerAutomorphism (p : ℕ) (hp : p.Coprime n) :
    IsCyclotomicExtension.Rat.galEquivZMod n K (primePowerAutomorphism n K p hp) =
      ZMod.unitOfCoprime p hp := by
  exact (IsCyclotomicExtension.Rat.galEquivZMod n K).apply_symm_apply _

/-- This is a theorem about actual field elements, not a name assigned to the sample. -/
theorem primePowerAutomorphism_apply (p : ℕ) (hp : p.Coprime n)
    {x : K} (hx : x ^ n = 1) : primePowerAutomorphism n K p hp x = x ^ p := by
  rw [IsCyclotomicExtension.Rat.galEquivZMod_apply_of_pow_eq n K _ hx,
    galEquiv_primePowerAutomorphism, ZMod.coe_unitOfCoprime]
  apply pow_eq_pow_of_modEq _ hx
  apply (ZMod.natCast_eq_natCast_iff _ _ n).mp
  simp

/-- Every actual cyclotomic automorphism is represented by a permitted prime,
even after imposing an arbitrary lower bound. -/
theorem exists_prime_with_automorphism (forbidden : Finset ℕ) (σ : Gal(K/ℚ)) (B : ℕ) :
    ∃ p : PermittedPrime n forbidden, B < p.val ∧ primeSample n K forbidden p = σ := by
  obtain ⟨p, hB, hp⟩ := exists_prime_with_residue n forbidden
    (IsCyclotomicExtension.Rat.galEquivZMod n K σ) B
  refine ⟨p, hB, ?_⟩
  apply (IsCyclotomicExtension.Rat.galEquivZMod n K).injective
  rw [primeSample, galEquiv_primePowerAutomorphism]
  exact hp

theorem primeSample_surjective (forbidden : Finset ℕ) :
    Function.Surjective (primeSample n K forbidden) := by
  intro σ
  obtain ⟨p, _, hp⟩ := exists_prime_with_automorphism n K forbidden σ 0
  exact ⟨p, hp⟩

/-- All open normal quotient classes are covered. This is derived from actual
prime surjectivity for this fixed cyclotomic extension. -/
theorem primeSample_quotientCoverage (forbidden : Finset ℕ) :
    PaperX.ProfiniteSeparation.QuotientCoverage (primeSample n K forbidden) := by
  intro H σ
  obtain ⟨p, hp⟩ := primeSample_surjective n K forbidden σ
  refine ⟨p, 1, ?_⟩
  simp [hp]

section Residue
open scoped Pointwise
variable (p : ℕ) [Fact (Nat.Prime p)] (P : Ideal (𝓞 K)) [P.IsMaximal]
  [P.LiesOver (Ideal.span {(p : ℤ)})] (hp : p.Coprime n)
attribute [local instance] Ideal.Quotient.field

/-- The sampled automorphism belongs to the actual decomposition group at every
prime of the cyclotomic field above p. -/
theorem primePowerAutomorphism_mem_stabilizer :
    primePowerAutomorphism n K p hp ∈ MulAction.stabilizer Gal(K/ℚ) P := by
  have hmem : ZMod.unitOfCoprime p hp ∈
      (IsCyclotomicExtension.Rat.galEquivZMod n K).mapSubgroup
        (MulAction.stabilizer Gal(K/ℚ) P) := by
    rw [IsCyclotomicExtension.Rat.galEquivZMod_stabilizer n K p P hp]
    exact Subgroup.mem_zpowers _
  exact Subgroup.mem_map_equiv.mp hmem

/-- The arithmetic Frobenius condition is proved on every integral element:
reduction of the sampled action equals the p-power residue-field action. -/
theorem primePowerAutomorphism_residue (x : 𝓞 K) :
    Ideal.Quotient.mk P (primePowerAutomorphism n K p hp • x) =
      (Ideal.Quotient.mk P x) ^ p := by
  have : CharP (ℤ ⧸ Ideal.span {(p : ℤ)}) p := ringChar.of_eq <| Int.ringChar_idealQuot p
  have : CharP (𝓞 K ⧸ P) p :=
    charP_of_injective_algebraMap
      (algebraMap (ℤ ⧸ Ideal.span {(p : ℤ)}) (𝓞 K ⧸ P)).injective p
  let σ := primePowerAutomorphism n K p hp
  let f := ((Ideal.Quotient.mk P).comp
    (MulSemiringAction.toRingHom Gal(K/ℚ) (𝓞 K) σ)).toIntAlgHom
  let g := ((frobenius (𝓞 K ⧸ P) p).comp (Ideal.Quotient.mk P)).toIntAlgHom
  have hζ := IsCyclotomicExtension.zeta_spec n ℚ K
  have hfg : f = g := by
    apply AlgHom.ext_of_adjoin_eq_top
      (IsCyclotomicExtension.Rat.adjoin_singleton_eq_top hζ)
    intro z hz
    have hz' : z = hζ.toInteger := Set.mem_singleton_iff.mp hz
    subst z
    change Ideal.Quotient.mk P (σ • hζ.toInteger) =
      (Ideal.Quotient.mk P hζ.toInteger) ^ p
    rw [IsCyclotomicExtension.Rat.galEquivZMod_smul_of_pow_eq n K σ
      hζ.toInteger_isPrimitiveRoot.pow_eq_one]
    simp only [σ, galEquiv_primePowerAutomorphism, ZMod.coe_unitOfCoprime,
      ZMod.val_natCast, map_pow]
    exact (pow_eq_pow_mod p
      (by simp [← map_pow, hζ.toInteger_isPrimitiveRoot.pow_eq_one])).symm
  exact DFunLike.congr_fun hfg x

/-- Both defining properties of arithmetic Frobenius are obtained for the
actual prime and its actual residue field. -/
theorem primePowerAutomorphism_arithmeticFrobenius :
    primePowerAutomorphism n K p hp ∈ MulAction.stabilizer Gal(K/ℚ) P ∧
      ∀ x : 𝓞 K, Ideal.Quotient.mk P (primePowerAutomorphism n K p hp • x) =
        (Ideal.Quotient.mk P x) ^ p :=
  ⟨primePowerAutomorphism_mem_stabilizer n K p P hp,
    primePowerAutomorphism_residue n K p P hp⟩
/-- The actual arithmetic prime is unramified in the cyclotomic extension. -/
theorem permitted_prime_ramificationIdx (hcop : p.Coprime n) :
    Ideal.ramificationIdx P ℤ = 1 :=
  IsCyclotomicExtension.Rat.ramificationIdx_eq_of_not_dvd p K P
    ((Nat.Prime.coprime_iff_not_dvd (Fact.out : p.Prime)).mp hcop)

/-- Unramifiedness and the arithmetic Frobenius action are proved together. -/
theorem primePowerAutomorphism_unramified_arithmeticFrobenius :
    Ideal.ramificationIdx P ℤ = 1 ∧
      primePowerAutomorphism n K p hp ∈ MulAction.stabilizer Gal(K/ℚ) P ∧
      ∀ x : 𝓞 K, Ideal.Quotient.mk P (primePowerAutomorphism n K p hp • x) =
        (Ideal.Quotient.mk P x) ^ p :=
  ⟨permitted_prime_ramificationIdx n K p P hp,
    primePowerAutomorphism_arithmeticFrobenius n K p P hp⟩
end Residue

end PaperX.CyclotomicPrimeCoverage
