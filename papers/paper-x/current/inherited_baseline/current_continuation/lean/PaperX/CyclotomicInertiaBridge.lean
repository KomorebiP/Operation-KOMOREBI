import PaperX.CyclotomicAbsoluteSamples
import Mathlib.RingTheory.Valuation.RamificationGroup
import Mathlib.NumberTheory.Padics.RingHoms
import Mathlib.Tactic

/-! Actual valuation inertia fixes all roots of unity whose order is a unit in
its valuation ring. Consequently restriction to a cyclotomic field kills this
actual inertia subgroup. No quotient preimage is named an inertia subgroup. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.CyclotomicInertiaBridge

section Local
variable {R : Type*} [CommRing R] [IsDomain R] [IsLocalRing R]

/-- Reduction is injective on the n-th roots of unity when n is a unit. -/
theorem residue_injective_on_roots (n : ℕ) [NeZero n] (hn : IsUnit (n : R))
    {x y : R} (hx : x ^ n = 1) (hy : y ^ n = 1)
    (hres : IsLocalRing.residue R x = IsLocalRing.residue R y) : x = y := by
  let s : R := ∑ i ∈ Finset.range n, x ^ i * y ^ (n - 1 - i)
  have hp : s * (x - y) = 0 := by
    rw [show s = ∑ i ∈ Finset.range n, x ^ i * y ^ (n - 1 - i) from rfl,
      geom_sum₂_mul, hx, hy, sub_self]
  have hry : IsLocalRing.residue R y ≠ 0 := by
    intro hz
    have h := congrArg (IsLocalRing.residue R) hy
    simp [hz, NeZero.ne n] at h
  have hrs : IsLocalRing.residue R s =
      (n : IsLocalRing.ResidueField R) * (IsLocalRing.residue R y) ^ (n - 1) := by
    simp only [s, map_sum, map_mul, map_pow, hres]
    rw [show (∑ i ∈ Finset.range n,
      IsLocalRing.residue R y ^ i * IsLocalRing.residue R y ^ (n - 1 - i)) =
      ∑ _i ∈ Finset.range n, IsLocalRing.residue R y ^ (n - 1) from ?_]
    simp
    apply Finset.sum_congr rfl
    intro i hi
    rw [← pow_add]
    congr 1
    have hi' := Finset.mem_range.mp hi
    omega
  have hn0 : (n : IsLocalRing.ResidueField R) ≠ 0 := by
    simpa only [map_natCast] using (IsLocalRing.residue_ne_zero_iff_isUnit (n : R)).mpr hn
  have hs : s ≠ 0 := by
    intro hz
    have := mul_ne_zero hn0 (pow_ne_zero (n - 1) hry)
    exact this (by simpa [hz] using hrs.symm)
  exact sub_eq_zero.mp ((mul_eq_zero.mp hp).resolve_left hs)
end Local

section Valuation
variable {L : Type*} [Field L]

/-- Every root of unity belongs to any valuation subring of its field. -/
theorem root_mem_valuation (A : ValuationSubring L) (n : ℕ) [NeZero n]
    {x : L} (hx : x ^ n = 1) : x ∈ A := by
  have hx0 : x ≠ 0 := by
    intro hz
    simp [hz, NeZero.ne n] at hx
  rcases A.mem_or_inv_mem x with h | h
  · exact h
  · have hinv : x⁻¹ ^ (n - 1) = x := by
      rw [inv_pow_sub₀ hx0 (Nat.one_le_iff_ne_zero.mpr (NeZero.ne n)), hx]
      simp
    simpa [hinv] using A.toSubring.pow_mem h (n - 1)

/-- The actual residue-action kernel fixes every n-th root when n is a unit. -/
theorem inertia_fixes_roots (K : Type*) [Field K] [Algebra K L]
    (A : ValuationSubring L) (n : ℕ) [NeZero n] (hn : IsUnit (n : A))
    {x : L} (hx : x ^ n = 1)
    (σ : A.decompositionSubgroup K) (hσ : σ ∈ A.inertiaSubgroup K) :
    (σ.val : L ≃ₐ[K] L) x = x := by
  let z : A := ⟨x, root_mem_valuation A n hx⟩
  have hz : z ^ n = 1 := Subtype.ext hx
  have hres : IsLocalRing.residue A (σ • z) = IsLocalRing.residue A z := by
    change MulSemiringAction.toRingAut (A.decompositionSubgroup K)
      (IsLocalRing.ResidueField A) σ = 1 at hσ
    exact congrArg (fun f : RingAut (IsLocalRing.ResidueField A) =>
      f (IsLocalRing.residue A z)) hσ
  have hp : (σ • z) ^ n = 1 := by
    change (MulSemiringAction.toRingAut (A.decompositionSubgroup K) A σ z) ^ n = 1
    rw [← map_pow, hz, map_one]
  exact congrArg (fun a : A => (a : L)) (residue_injective_on_roots n hn hp hz hres)
/-- A decomposition element with arithmetic p-power residue action has that
same p-power action on all roots of order invertible in the valuation ring. -/
theorem decomposition_maps_roots_to_power (K : Type*) [Field K] [Algebra K L]
    (A : ValuationSubring L) (n : ℕ) [NeZero n] (hn : IsUnit (n : A))
    (p : ℕ) (σ : A.decompositionSubgroup K)
    (hσ : ∀ z : A, IsLocalRing.residue A (σ • z) = (IsLocalRing.residue A z) ^ p)
    {x : L} (hx : x ^ n = 1) : (σ.val : L ≃ₐ[K] L) x = x ^ p := by
  let z : A := ⟨x, root_mem_valuation A n hx⟩
  have hz : z ^ n = 1 := Subtype.ext hx
  have hleft : (σ • z) ^ n = 1 := by
    change (MulSemiringAction.toRingAut (A.decompositionSubgroup K) A σ z) ^ n = 1
    rw [← map_pow, hz, map_one]
  have hright : (z ^ p) ^ n = 1 := by rw [pow_right_comm, hz, one_pow]
  have hres : IsLocalRing.residue A (σ • z) = IsLocalRing.residue A (z ^ p) := by
    rw [map_pow]
    exact hσ z
  exact congrArg (fun a : A => (a : L))
    (residue_injective_on_roots n hn hleft hright hres)
end Valuation

section Cyclotomic
open NumberField PaperX.CyclotomicAbsoluteSamples
variable (n : ℕ) [NeZero n] (L : Type*) [Field L] [NumberField L]
  [IsCyclotomicExtension {n} ℚ L]

/-- Restriction of actual valuation inertia to the cyclotomic extension is
trivial when the root order is invertible in the valuation ring. -/
theorem restriction_eq_one_of_inertia
    (A : ValuationSubring (AlgebraicClosure ℚ)) (hn : IsUnit (n : A))
    (σ : A.decompositionSubgroup ℚ) (hσ : σ ∈ A.inertiaSubgroup ℚ) :
    restrictionMap n L (show Field.absoluteGaloisGroup ℚ from σ.val) = 1 := by
  have hζ := IsCyclotomicExtension.zeta_spec n ℚ L
  have hfix : restrictionMap n L (show Field.absoluteGaloisGroup ℚ from σ.val) (IsCyclotomicExtension.zeta n ℚ L) =
      IsCyclotomicExtension.zeta n ℚ L := by
    apply (fieldEmbedding n L).injective
    change fieldEmbedding n L ((restrictionMap n L (show Field.absoluteGaloisGroup ℚ from σ.val)) _) = _
    rw [restrictionMap_commutes n L (show Field.absoluteGaloisGroup ℚ from σ.val)]
    exact inertia_fixes_roots ℚ A n hn
      (by rw [← map_pow, hζ.pow_eq_one, map_one]) σ hσ
  apply AlgEquiv.coe_toAlgHom_injective
  apply AlgHom.ext_of_adjoin_eq_top
    (IsCyclotomicExtension.adjoin_primitive_root_eq_top hζ)
  intro x hx
  have hx' : x = IsCyclotomicExtension.zeta n ℚ L := Set.mem_singleton_iff.mp hx
  subst x
  exact hfix

omit [NeZero n] in
/-- A valuation with residue characteristic p makes each integer coprime to p
a unit. This turns a prime-coprimality hypothesis into the local unit condition. -/
theorem order_isUnit_of_coprime
    (A : ValuationSubring (AlgebraicClosure ℚ)) (p : ℕ) [Fact p.Prime]
    [CharP (IsLocalRing.ResidueField A) p] (hp : p.Coprime n) : IsUnit (n : A) := by
  apply (IsLocalRing.residue_ne_zero_iff_isUnit (n : A)).mp
  rw [map_natCast, ne_eq, CharP.cast_eq_zero_iff]
  exact (Nat.Prime.coprime_iff_not_dvd (Fact.out : p.Prime)).mp hp

/-- Actual valuation inertia over a residue prime not dividing n acts trivially
on the chosen cyclotomic subfield of the algebraic closure. -/
theorem restriction_eq_one_of_coprime_inertia
    (A : ValuationSubring (AlgebraicClosure ℚ)) (p : ℕ) [Fact p.Prime]
    [CharP (IsLocalRing.ResidueField A) p] (hp : p.Coprime n)
    (σ : A.decompositionSubgroup ℚ) (hσ : σ ∈ A.inertiaSubgroup ℚ) :
    restrictionMap n L (show Field.absoluteGaloisGroup ℚ from σ.val) = 1 :=
  restriction_eq_one_of_inertia n L A (order_isUnit_of_coprime n A p hp) σ hσ
/-- Recognition of a genuine arithmetic Frobenius element: its restriction
is exactly the finite cyclotomic sample proved in Block 25. This theorem assumes
the decomposition element and its residue action, but proves the comparison. -/
theorem restriction_eq_primePower_of_residue
    (A : ValuationSubring (AlgebraicClosure ℚ)) (p : ℕ) (hp : p.Coprime n)
    (hn : IsUnit (n : A)) (σ : A.decompositionSubgroup ℚ)
    (hσ : ∀ z : A, IsLocalRing.residue A (σ • z) = (IsLocalRing.residue A z) ^ p) :
    restrictionMap n L (show Field.absoluteGaloisGroup ℚ from σ.val) = PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism n L p hp := by
  have hζ := IsCyclotomicExtension.zeta_spec n ℚ L
  have hfix : restrictionMap n L (show Field.absoluteGaloisGroup ℚ from σ.val) (IsCyclotomicExtension.zeta n ℚ L) =
      PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism n L p hp
        (IsCyclotomicExtension.zeta n ℚ L) := by
    apply (fieldEmbedding n L).injective
    change fieldEmbedding n L ((restrictionMap n L (show Field.absoluteGaloisGroup ℚ from σ.val)) _) = _
    rw [restrictionMap_commutes n L (show Field.absoluteGaloisGroup ℚ from σ.val),
      PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism_apply n L p hp hζ.pow_eq_one,
      map_pow]
    exact decomposition_maps_roots_to_power ℚ A n hn p σ hσ
      (by rw [← map_pow, hζ.pow_eq_one, map_one])
  apply AlgEquiv.coe_toAlgHom_injective
  apply AlgHom.ext_of_adjoin_eq_top
    (IsCyclotomicExtension.adjoin_primitive_root_eq_top hζ)
  intro x hx
  have hx' : x = IsCyclotomicExtension.zeta n ℚ L := Set.mem_singleton_iff.mp hx
  subst x
  exact hfix

/-- The cyclotomic Frobenius comparison at a prime whose residue characteristic
is p. Coprimality supplies the unit condition rather than assuming it separately. -/
theorem restriction_eq_primePower_of_coprime_residue
    (A : ValuationSubring (AlgebraicClosure ℚ)) (p : ℕ) [Fact p.Prime]
    [CharP (IsLocalRing.ResidueField A) p] (hp : p.Coprime n)
    (σ : A.decompositionSubgroup ℚ)
    (hσ : ∀ z : A, IsLocalRing.residue A (σ • z) = (IsLocalRing.residue A z) ^ p) :
    restrictionMap n L (show Field.absoluteGaloisGroup ℚ from σ.val) = PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism n L p hp :=
  restriction_eq_primePower_of_residue n L A p hp (order_isUnit_of_coprime n A p hp) σ hσ
section Representations
variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]
variable (ρ : Representation K Gal(L/ℚ) V)

/-- Every representation inflated from the cyclotomic field is unramified on
the actual valuation inertia away from primes dividing the root order. -/
theorem pullback_trivial_on_inertia
    (A : ValuationSubring (AlgebraicClosure ℚ)) (p : ℕ) [Fact p.Prime]
    [CharP (IsLocalRing.ResidueField A) p] (hp : p.Coprime n)
    (σ : A.decompositionSubgroup ℚ) (hσ : σ ∈ A.inertiaSubgroup ℚ) :
    (ρ.comp (restrictionMap n L)) (show Field.absoluteGaloisGroup ℚ from σ.val) = 1 := by
  change ρ (restrictionMap n L (show Field.absoluteGaloisGroup ℚ from σ.val)) = 1
  rw [restriction_eq_one_of_coprime_inertia n L A p hp σ hσ, map_one]

/-- The entire inflated linear action at a genuine decomposition Frobenius is
the finite cyclotomic action. The Frobenius element remains supplied. -/
theorem pullback_on_arithmeticFrobenius
    (A : ValuationSubring (AlgebraicClosure ℚ)) (p : ℕ) [Fact p.Prime]
    [CharP (IsLocalRing.ResidueField A) p] (hp : p.Coprime n)
    (σ : A.decompositionSubgroup ℚ)
    (hσ : ∀ z : A, IsLocalRing.residue A (σ • z) = (IsLocalRing.residue A z) ^ p) :
    (ρ.comp (restrictionMap n L)) (show Field.absoluteGaloisGroup ℚ from σ.val) =
      ρ (PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism n L p hp) := by
  change ρ (restrictionMap n L (show Field.absoluteGaloisGroup ℚ from σ.val)) = _
  rw [restriction_eq_primePower_of_coprime_residue n L A p hp σ hσ]

/-- The trace comparison follows from equality of the full linear operators. -/
theorem pullback_character_on_arithmeticFrobenius
    (A : ValuationSubring (AlgebraicClosure ℚ)) (p : ℕ) [Fact p.Prime]
    [CharP (IsLocalRing.ResidueField A) p] (hp : p.Coprime n)
    (σ : A.decompositionSubgroup ℚ)
    (hσ : ∀ z : A, IsLocalRing.residue A (σ • z) = (IsLocalRing.residue A z) ^ p) :
    Representation.character (ρ.comp (restrictionMap n L)) (show Field.absoluteGaloisGroup ℚ from σ.val) =
      ρ.character (PaperX.CyclotomicPrimeCoverage.primePowerAutomorphism n L p hp) := by
  exact congrArg (LinearMap.trace K V)
    (pullback_on_arithmeticFrobenius n L ρ A p hp σ hσ)
end Representations
end Cyclotomic

/-- The unit condition is essential even in a genuine characteristic-zero DVR:
1 and -1 in Z₂ are distinct square roots with identical residues. -/
theorem twoAdic_distinct_roots_same_residue :
    ∃ x y : PadicInt 2, x ^ 2 = 1 ∧ y ^ 2 = 1 ∧ x ≠ y ∧
      IsLocalRing.residue (PadicInt 2) x = IsLocalRing.residue (PadicInt 2) y := by
  refine ⟨1, -1, by norm_num, by norm_num, by norm_num, ?_⟩
  apply (PadicInt.residueField (p := 2)).injective
  simp only [map_one, map_neg]
  change (1 : ZMod 2) = -1
  decide

/-- The root order 2 in that boundary example is not a unit of Z₂. -/
theorem twoAdic_order_not_unit : ¬ IsUnit (2 : PadicInt 2) := by
  exact PadicInt.p_nonunit (p := 2)


end PaperX.CyclotomicInertiaBridge
