import Mathlib.RingTheory.Valuation.RamificationGroup
import Mathlib.RingTheory.Ideal.Operations

/-! Lower congruence subgroups are defined by their action on an actual local ring.
For a discrete valuation ring in a finite Galois extension these are the usual
nonnegative lower ramification groups. The generic local-ring definition is NOT
asserted to be an absolute Weil ramification filtration. -/
set_option autoImplicit false
noncomputable section

namespace PaperXI.ValuationRamification
variable (R D : Type*) [CommRing R] [IsLocalRing R] [Group D] [MulSemiringAction D R]

/-- Automorphisms acting as identity modulo the (i+1)-st maximal-ideal power. -/
def lower (i : ℕ) : Subgroup D where
  carrier := {g | ∀ x : R, g • x - x ∈ (IsLocalRing.maximalIdeal R) ^ (i + 1)}
  one_mem' := by intro x; simp
  mul_mem' := by
    intro g h hg hh x
    have ha := hg (h • x)
    have hb := hh x
    have hab := Ideal.add_mem ((IsLocalRing.maximalIdeal R) ^ (i+1)) ha hb
    simpa only [sub_add_sub_cancel, mul_smul] using hab
  inv_mem' := by
    intro g hg x
    have hh := hg (g⁻¹ • x)
    have hh' := ((IsLocalRing.maximalIdeal R) ^ (i+1)).neg_mem hh
    simpa using hh'

@[simp] theorem mem_lower (i : ℕ) (g : D) :
    g ∈ lower R D i ↔ ∀ x : R, g • x - x ∈ (IsLocalRing.maximalIdeal R) ^ (i+1) := Iff.rfl

/-- Automorphisms preserve every power of the maximal ideal. -/
theorem smul_mem_power (g : D) (n : ℕ) {x : R}
    (hx : x ∈ (IsLocalRing.maximalIdeal R)^n) :
    g • x ∈ (IsLocalRing.maximalIdeal R)^n := by
  let e := MulSemiringAction.toRingAut D R g
  have hm : Ideal.map (e : R →+* R) ((IsLocalRing.maximalIdeal R)^n) =
      (IsLocalRing.maximalIdeal R)^n := by
    rw [Ideal.map_pow]
    exact congrArg (fun J : Ideal R => J^n)
      (IsLocalRing.map_maximalIdeal_of_surjective (e : R →+* R) e.surjective)
  have he := Ideal.mem_map_of_mem (e : R →+* R) hx
  rw [hm] at he
  exact he

/-- Normality is derived from conjugation on the actual ring. -/
instance lower_normal (i : ℕ) : (lower R D i).Normal where
  conj_mem g hg h := by
    intro x
    have hm := smul_mem_power R D h (i+1) (hg (h⁻¹ • x))
    simpa only [smul_sub, smul_inv_smul, mul_smul] using hm

/-- The filtration is decreasing without an assumed filtration certificate. -/
theorem antitone : Antitone (lower R D) := by
  intro i j hij g hg x
  exact (Ideal.pow_le_pow_right (Nat.add_le_add_right hij 1)) (hg x)

/-- Zeroth congruence group equals the kernel of the literal residue-field action. -/
theorem lower_zero_eq_residue_kernel : lower R D 0 =
    (MulSemiringAction.toRingAut D (IsLocalRing.ResidueField R)).ker := by
  ext g
  change (∀ x : R, g • x - x ∈ (IsLocalRing.maximalIdeal R) ^ (0+1)) ↔
    MulSemiringAction.toRingAut D (IsLocalRing.ResidueField R) g = 1
  simp only [zero_add, pow_one]
  constructor
  · intro hg
    apply RingEquiv.ext
    intro y
    obtain ⟨x, rfl⟩ := IsLocalRing.residue_surjective (R := R) y
    have h := (IsLocalRing.residue_eq_zero_iff (g • x - x)).mpr (hg x)
    change g • IsLocalRing.residue R x = IsLocalRing.residue R x
    simpa only [map_sub, IsLocalRing.ResidueField.residue_smul, sub_eq_zero] using h
  · intro hg x
    apply (IsLocalRing.residue_eq_zero_iff (g • x - x)).mp
    rw [map_sub, IsLocalRing.ResidueField.residue_smul]
    have hh := RingEquiv.congr_fun hg (IsLocalRing.residue R x)
    exact sub_eq_zero.mpr hh

theorem lower_le_inertia (i : ℕ) : lower R D i ≤
    (MulSemiringAction.toRingAut D (IsLocalRing.ResidueField R)).ker := by
  rw [← lower_zero_eq_residue_kernel]
  exact antitone R D (Nat.zero_le i)

theorem positive_le_one {i : ℕ} (hi : 1 ≤ i) : lower R D i ≤ lower R D 1 :=
  antitone R D hi

section Valuation
variable (K : Type*) {L : Type*} [Field K] [Field L] [Algebra K L]

theorem valuation_lower_zero (A : ValuationSubring L) :
    lower A (A.decompositionSubgroup K) 0 = A.inertiaSubgroup K :=
  lower_zero_eq_residue_kernel A (A.decompositionSubgroup K)

end Valuation
end PaperXI.ValuationRamification
