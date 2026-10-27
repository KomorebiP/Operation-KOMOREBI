import RealizationBoundaries.Quotient
import Mathlib.Algebra.Module.Submodule.Basic
import Mathlib.Algebra.Module.Submodule.Map

/-! # Rational preimages and exact integer-root certificates -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- The actual subgroup q⁻¹(W) of the unrestricted prime product. -/
def preimage (W : Submodule ℚ TailSpace) : AddSubgroup Ambient :=
  W.toAddSubgroup.comap quotientMap

@[simp] theorem mem_preimage (W : Submodule ℚ TailSpace) (x : Ambient) :
    x ∈ preimage W ↔ quotientMap x ∈ W := Iff.rfl

theorem finiteSupport_le_preimage (W : Submodule ℚ TailSpace) :
    finiteSupport ≤ preimage W := by
  intro x hx
  change quotientMap x ∈ W
  rw [(quotientMap_eq_zero_iff x).mpr hx]
  exact W.zero_mem

/-- Every ambient integer root of a member of H_W is already in H_W. -/
theorem nsmul_mem_preimage_iff (W : Submodule ℚ TailSpace) {m : ℕ}
    (hm : 0 < m) (x : Ambient) : m • x ∈ preimage W ↔ x ∈ preimage W := by
  change quotientMap (m • x) ∈ W ↔ quotientMap x ∈ W
  rw [map_nsmul, ← Nat.cast_smul_eq_nsmul ℚ]
  exact W.smul_mem_iff (by exact_mod_cast Nat.ne_of_gt hm)

/-- Complete root condition in the actual infinite ambient product. -/
theorem ambient_root_iff (m : ℕ) (x : Ambient) :
    (∃ y : Ambient, m • y = x) ↔ ∀ p : Prime, p.val ∣ m → x p = 0 := by
  constructor
  · rintro ⟨y, rfl⟩ p hp
    simp [(coordinate_cast_eq_zero m p).mpr hp]
  · intro hx
    refine ⟨coordinateDivide m x, ?_⟩
    funext p
    rw [coordinate_nsmul]
    change (m : Coordinate p) * ((m : Coordinate p)⁻¹ * x p) = x p
    by_cases hp : p.val ∣ m
    · simp [(coordinate_cast_eq_zero m p).mpr hp, hx p hp]
    · exact mul_inv_cancel_left₀ ((coordinate_cast_eq_zero m p).not.mpr hp) (x p)

/-- Monograph Theorem 4.2: root solvability in every rational preimage. -/
theorem preimage_root_iff (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m)
    (x : preimage W) :
    (∃ y : preimage W, m • y = x) ↔ ∀ p : Prime, p.val ∣ m → x.val p = 0 := by
  constructor
  · rintro ⟨y, hy⟩
    apply (ambient_root_iff m x.val).mp
    exact ⟨y.val, congrArg Subtype.val hy⟩
  · intro hx
    obtain ⟨y, hy⟩ := (ambient_root_iff m x.val).mpr hx
    have hymem : y ∈ preimage W := (nsmul_mem_preimage_iff W hm y).mp (hy ▸ x.property)
    exact ⟨⟨y, hymem⟩, Subtype.ext hy⟩

/-- Purity is a proved property of the constructed subgroup, not a supplied hypothesis. -/
theorem preimage_pure (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m)
    (x : preimage W) (h : ∃ y : Ambient, m • y = x.val) :
    ∃ y : preimage W, m • y = x :=
  (preimage_root_iff W hm x).mpr ((ambient_root_iff m x.val).mp h)

/-- A single exceptional nonzero coordinate rules out every root. -/
theorem prime_obstruction (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m)
    (x : preimage W) (p : Prime) (hp : p.val ∣ m) (hx : x.val p ≠ 0) :
    ¬ ∃ y : preimage W, m • y = x := by
  intro hy
  exact hx ((preimage_root_iff W hm x).mp hy p hp)

/-- Torsion remains precisely the original finite-support subgroup. -/
theorem preimage_torsion_iff (W : Submodule ℚ TailSpace) (x : preimage W) :
    (∃ m : ℕ, 0 < m ∧ m • x = 0) ↔ x.val ∈ finiteSupport := by
  constructor
  · rintro ⟨m, hm, hx⟩
    exact (torsion_iff_finiteSupport x.val).mp ⟨m, hm, congrArg Subtype.val hx⟩
  · intro hx
    obtain ⟨m, hm, hmx⟩ := exists_annihilator_of_finiteSupport x.val hx
    exact ⟨m, hm, Subtype.ext hmx⟩

/-- Every nonzero element is detected by a finite prime coordinate. -/
theorem nonzero_coordinate (W : Submodule ℚ TailSpace) (x : preimage W) (hx : x ≠ 0) :
    ∃ p : Prime, x.val p ≠ 0 := by
  by_contra h
  push Not at h
  apply hx
  apply Subtype.ext
  funext p
  exact h p

end RealizationBoundaries
