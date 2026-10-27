import PaperX.CyclotomicAbsoluteSamples
import Mathlib.RingTheory.IntegralClosure.Algebra.Basic
import Mathlib.Tactic

/-! Arithmetic Frobenius recognition in the actual integral closure of the
integers in the algebraic closure of the rationals. Reduction is injective on
roots of order prime to the residue characteristic. The ideal inertia subgroup
therefore acts trivially on the corresponding cyclotomic field. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CyclotomicIntegralFrobenius
open NumberField PaperX.CyclotomicAbsoluteSamples
open scoped Pointwise

section Roots
variable {R S : Type*} [CommRing R] [IsDomain R] [CommRing S] [IsDomain S]

/-- Any ring homomorphism is injective on roots whose order remains nonzero in
the target domain. The ambient homomorphism need not be injective. -/
theorem map_injective_on_roots (f : R →+* S) (n : ℕ) [NeZero n] (hn : (n : S) ≠ 0)
    {x y : R} (hx : x ^ n = 1) (hy : y ^ n = 1) (hres : f x = f y) : x = y := by
  let s : R := ∑ i ∈ Finset.range n, x ^ i * y ^ (n - 1 - i)
  have hp : s * (x - y) = 0 := by
    rw [show s = ∑ i ∈ Finset.range n, x ^ i * y ^ (n - 1 - i) from rfl,
      geom_sum₂_mul, hx, hy, sub_self]
  have hry : f y ≠ 0 := by
    intro hz
    have h := congrArg f hy
    simp [hz, NeZero.ne n] at h
  have hrs : f s = (n : S) * (f y) ^ (n - 1) := by
    simp only [s, map_sum, map_mul, map_pow, hres]
    rw [show (∑ i ∈ Finset.range n, f y ^ i * f y ^ (n - 1 - i)) =
      ∑ _i ∈ Finset.range n, f y ^ (n - 1) from ?_]
    simp
    apply Finset.sum_congr rfl
    intro i hi
    rw [← pow_add]
    congr 1
    have hi' := Finset.mem_range.mp hi
    omega
  have hs : s ≠ 0 := by
    intro hz
    have h := mul_ne_zero hn (pow_ne_zero (n - 1) hry)
    exact h (by simpa [hz] using hrs.symm)
  exact sub_eq_zero.mp ((mul_eq_zero.mp hp).resolve_left hs)
end Roots

abbrev AbsoluteGroup := Gal(AlgebraicClosure ℚ/ℚ)

abbrev AbsoluteIntegers := integralClosure ℤ (AlgebraicClosure ℚ)

section Absolute
variable (Q : Ideal AbsoluteIntegers) [Q.IsMaximal]
attribute [local instance] Ideal.Quotient.field

/-- A root of unity is an actual element of the integral closure. -/
theorem root_isIntegral (n : ℕ) [NeZero n] {x : AlgebraicClosure ℚ} (hx : x ^ n = 1) :
    IsIntegral ℤ x :=
  IsIntegral.of_pow (NeZero.pos n) (hx ▸ isIntegral_one)

/-- A p-power residue action determines the p-power action on roots whose order
is nonzero in the residue field. -/
theorem maps_roots_to_power (n : ℕ) [NeZero n] (hn : (n : AbsoluteIntegers ⧸ Q) ≠ 0)
    (p : ℕ) (γ : AbsoluteGroup)
    (hγ : ∀ z : AbsoluteIntegers, Ideal.Quotient.mk Q (γ • z) =
      (Ideal.Quotient.mk Q z) ^ p)
    {x : AlgebraicClosure ℚ} (hx : x ^ n = 1) : γ x = x ^ p := by
  let z : AbsoluteIntegers := ⟨x, root_isIntegral n hx⟩
  have hz : z ^ n = 1 := Subtype.ext hx
  have hleft : (γ • z) ^ n = 1 := by
    change (MulSemiringAction.toRingAut (AbsoluteGroup) AbsoluteIntegers γ z) ^ n = 1
    rw [← map_pow, hz, map_one]
  have hright : (z ^ p) ^ n = 1 := by rw [pow_right_comm, hz, one_pow]
  have hres : Ideal.Quotient.mk Q (γ • z) = Ideal.Quotient.mk Q (z ^ p) := by
    rw [map_pow]
    exact hγ z
  exact congrArg (fun a : AbsoluteIntegers => (a : AlgebraicClosure ℚ))
    (map_injective_on_roots (Ideal.Quotient.mk Q) n hn hleft hright hres)

/-- Coprimality makes the root order nonzero in the actual residue field over p. -/
theorem order_nonzero_in_quotient (n p : ℕ) [Fact p.Prime]
    [Q.LiesOver (Ideal.span {(p : ℤ)})] (hp : p.Coprime n) :
    (n : AbsoluteIntegers ⧸ Q) ≠ 0 := by
  let : CharP (ℤ ⧸ Ideal.span {(p : ℤ)}) p := ringChar.of_eq <| Int.ringChar_idealQuot p
  let : CharP (AbsoluteIntegers ⧸ Q) p :=
    charP_of_injective_algebraMap
      (algebraMap (ℤ ⧸ Ideal.span {(p : ℤ)}) (AbsoluteIntegers ⧸ Q)).injective p
  rw [ne_eq, CharP.cast_eq_zero_iff]
  exact (Nat.Prime.coprime_iff_not_dvd (Fact.out : p.Prime)).mp hp
end Absolute

section Cyclotomic
variable (n : ℕ) [NeZero n] (L : Type*) [Field L] [NumberField L]
  [IsCyclotomicExtension {n} ℚ L]
variable (Q : Ideal AbsoluteIntegers) [Q.IsMaximal] (p : ℕ) [Fact p.Prime]
  [Q.LiesOver (Ideal.span {(p : ℤ)})] (hp : p.Coprime n)

/-- An actual absolute-Galois p-power residue action restricts to the arithmetic
cyclotomic Frobenius. Existence of the element is a separate theorem. -/
theorem restriction_eq_primePower_of_residue (γ : AbsoluteGroup)
    (hγ : ∀ z : AbsoluteIntegers, Ideal.Quotient.mk Q (γ • z) =
      (Ideal.Quotient.mk Q z) ^ p) :
    restrictionMap n L γ = PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism n L p hp := by
  have hζ := IsCyclotomicExtension.zeta_spec n ℚ L
  have hfix : restrictionMap n L γ (IsCyclotomicExtension.zeta n ℚ L) =
      PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism n L p hp
        (IsCyclotomicExtension.zeta n ℚ L) := by
    apply (fieldEmbedding n L).injective
    change fieldEmbedding n L ((restrictionMap n L γ) _) = _
    rw [restrictionMap_commutes n L γ,
      PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism_apply n L p hp hζ.pow_eq_one,
      map_pow]
    exact maps_roots_to_power Q n (order_nonzero_in_quotient Q n p hp) p γ hγ
      (by rw [← map_pow, hζ.pow_eq_one, map_one])
  apply AlgEquiv.coe_toAlgHom_injective
  apply AlgHom.ext_of_adjoin_eq_top
    (IsCyclotomicExtension.adjoin_primitive_root_eq_top hζ)
  intro x hx
  have hx' : x = IsCyclotomicExtension.zeta n ℚ L := Set.mem_singleton_iff.mp hx
  subst x
  exact hfix

include hp in
/-- The actual ideal inertia subgroup, defined by trivial residue action, is
killed by restriction to the cyclotomic field away from its root order. -/
theorem restriction_eq_one_of_inertia (γ : AbsoluteGroup)
    (hγ : γ ∈ Q.inertia (AbsoluteGroup)) : restrictionMap n L γ = 1 := by
  have hζ := IsCyclotomicExtension.zeta_spec n ℚ L
  have hfix : restrictionMap n L γ (IsCyclotomicExtension.zeta n ℚ L) =
      IsCyclotomicExtension.zeta n ℚ L := by
    apply (fieldEmbedding n L).injective
    change fieldEmbedding n L ((restrictionMap n L γ) _) = _
    rw [restrictionMap_commutes n L γ]
    simpa using maps_roots_to_power Q n (order_nonzero_in_quotient Q n p hp) 1 γ
      (fun z => by simpa using (Ideal.Quotient.eq.mpr (hγ z)))
      (by rw [← map_pow, hζ.pow_eq_one, map_one])
  apply AlgEquiv.coe_toAlgHom_injective
  apply AlgHom.ext_of_adjoin_eq_top
    (IsCyclotomicExtension.adjoin_primitive_root_eq_top hζ)
  intro x hx
  have hx' : x = IsCyclotomicExtension.zeta n ℚ L := Set.mem_singleton_iff.mp hx
  subst x
  exact hfix
section Representations
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable (ρ : Representation K Gal(L/ℚ) V)

include hp in
/-- Every representation pulled back from the cyclotomic field kills the actual
ideal inertia at primes not dividing the root order. -/
theorem pullback_trivial_on_inertia (γ : AbsoluteGroup)
    (hγ : γ ∈ Q.inertia AbsoluteGroup) :
    (ρ.comp (restrictionMap n L)) γ = 1 := by
  change ρ (restrictionMap n L γ) = 1
  rw [restriction_eq_one_of_inertia n L Q p hp γ hγ, map_one]

/-- The full linear action at an actual p-power residue element is the finite
cyclotomic Frobenius action. -/
theorem pullback_on_arithmeticFrobenius (γ : AbsoluteGroup)
    (hγ : ∀ z : AbsoluteIntegers, Ideal.Quotient.mk Q (γ • z) =
      (Ideal.Quotient.mk Q z) ^ p) :
    (ρ.comp (restrictionMap n L)) γ =
      ρ (PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism n L p hp) := by
  change ρ (restrictionMap n L γ) = _
  rw [restriction_eq_primePower_of_residue n L Q p hp γ hγ]

/-- The character comparison follows from equality of the complete actions. -/
theorem pullback_character_on_arithmeticFrobenius (γ : AbsoluteGroup)
    (hγ : ∀ z : AbsoluteIntegers, Ideal.Quotient.mk Q (γ • z) =
      (Ideal.Quotient.mk Q z) ^ p) :
    Representation.character (ρ.comp (restrictionMap n L)) γ =
      ρ.character (PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism n L p hp) := by
  exact congrArg (LinearMap.trace K V)
    (pullback_on_arithmeticFrobenius n L Q p hp ρ γ hγ)
end Representations
end Cyclotomic
end PaperX.CyclotomicIntegralFrobenius
