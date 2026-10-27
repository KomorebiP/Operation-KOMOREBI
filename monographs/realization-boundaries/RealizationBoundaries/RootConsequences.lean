import RealizationBoundaries.CyclicFiniteTargets
import RealizationBoundaries.Countability

/-! # Normalized roots and boundary cases

A solvable equation has a unique root with zero divisor coordinates, but in
general has many roots. The multiplier-zero fiber is infinite, not an empty
finite product. These are proved distinctions rather than comments in an API.
-/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- Coordinate division solves the equation exactly when the obstruction coordinates vanish. -/
theorem coordinateDivide_root (m : ℕ) (x : Ambient)
    (h : ∀ p : Prime, p.val ∣ m → x p = 0) : m • coordinateDivide m x = x := by
  funext p
  rw [coordinate_nsmul]
  change (m : Coordinate p) * ((m : Coordinate p)⁻¹ * x p) = x p
  by_cases hp : p.val ∣ m
  · simp [(coordinate_cast_eq_zero m p).mpr hp, h p hp]
  · exact mul_inv_cancel_left₀ ((coordinate_cast_eq_zero m p).not.mpr hp) (x p)

/-- No root is chosen by classical existence here: every coordinate is specified. -/
def normalizedRoot (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m)
    (x : preimage W) (h : ∀ p : Prime, p.val ∣ m → x.val p = 0) : RootFiber W m x :=
  ⟨⟨coordinateDivide m x.val,
    (nsmul_mem_preimage_iff W hm _).mp ((coordinateDivide_root m x.val h).symm ▸ x.property)⟩,
    Subtype.ext (coordinateDivide_root m x.val h)⟩

@[simp] theorem normalizedRoot_coordinate (W : Submodule ℚ TailSpace) {m : ℕ}
    (hm : 0 < m) (x : preimage W) (h : ∀ p : Prime, p.val ∣ m → x.val p = 0)
    (p : Prime) : (normalizedRoot W hm x h).val.val p = (m : Coordinate p)⁻¹ * x.val p := rfl

theorem normalizedRoot_exceptional_zero (W : Submodule ℚ TailSpace) {m : ℕ}
    (hm : 0 < m) (x : preimage W) (h : ∀ p : Prime, p.val ∣ m → x.val p = 0)
    (p : Prime) (hp : p.val ∣ m) : (normalizedRoot W hm x h).val.val p = 0 := by
  simp [normalizedRoot_coordinate, (coordinate_cast_eq_zero m p).mpr hp]

/-- Zero values at all free divisor coordinates select exactly one root. -/
theorem normalizedRoot_unique (W : Submodule ℚ TailSpace) {m : ℕ}
    (hm : 0 < m) (x : preimage W) (h : ∀ p : Prime, p.val ∣ m → x.val p = 0)
    (y : RootFiber W m x) (hy : ∀ p : Prime, p.val ∣ m → y.val.val p = 0) :
    y = normalizedRoot W hm x h := by
  apply Subtype.ext
  apply Subtype.ext
  funext p
  by_cases hp : p.val ∣ m
  · rw [hy p hp, normalizedRoot_exceptional_zero W hm x h p hp]
  · have hk : y.val - (normalizedRoot W hm x h).val ∈ rootKernel W m :=
      (rootFiber_coset_iff W m x (normalizedRoot W hm x h) y.val).mp y.property
    exact sub_eq_zero.mp (rootKernel_coordinate_zero W m ⟨_, hk⟩ p hp)

/-- The positive multiplier with radical one is exactly one. -/
theorem primeRadical_eq_one_iff {m : ℕ} (hm : 0 < m) : primeRadical m = 1 ↔ m = 1 := by
  constructor
  · intro h
    by_contra hm1
    obtain ⟨p, hp, hpm⟩ := Nat.exists_prime_and_dvd hm1
    have hd : p ∣ primeRadical m := (prime_dvd_radical_iff hm ⟨p,hp⟩).mpr hpm
    rw [h] at hd
    exact hp.ne_one (Nat.eq_one_of_dvd_one hd)
  · rintro rfl
    exact primeRadical_one

/-- Uniqueness of the entire fiber is different from uniqueness of the normalized root. -/
theorem unique_root_iff_one (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m)
    (x : preimage W) (h : ∃ y : preimage W, m • y = x) :
    (∃! y : preimage W, m • y = x) ↔ m = 1 := by
  have hc := rootFiber_card_of_solvable W hm x h
  constructor
  · rintro ⟨y, hy, hu⟩
    have hs : Subsingleton (RootFiber W m x) := ⟨by
      intro z w
      apply Subtype.ext
      exact (hu z.val z.property).trans (hu w.val w.property).symm⟩
    have hn : Nonempty (RootFiber W m x) := ⟨⟨y,hy⟩⟩
    have hcard : Nat.card (RootFiber W m x) = 1 := Nat.card_eq_one_iff_unique.mpr ⟨hs, hn⟩
    exact (primeRadical_eq_one_iff hm).mp (hc.symm.trans hcard)
  · rintro rfl
    exact ⟨x, one_nsmul x, fun y hy => by simpa using hy⟩

/-- A solvable positive prime-power equation has p roots, not p^k roots. -/
theorem prime_power_root_count (W : Submodule ℚ TailSpace) {p k : ℕ}
    (hp : p.Prime) (hk : k ≠ 0) (x : preimage W)
    (h : ∃ y : preimage W, (p ^ k) • y = x) :
    Nat.card (RootFiber W (p ^ k) x) = p := by
  rw [rootFiber_card_of_solvable W (pow_pos hp.pos k) x h, primeRadical_prime_pow hp hk]

/-- Zero multiplication at zero has the whole original group as its root fiber. -/
def zeroRootFiberEquiv (W : Submodule ℚ TailSpace) : RootFiber W 0 0 ≃ preimage W where
  toFun x := x.val
  invFun x := ⟨x, zero_nsmul x⟩
  left_inv _ := rfl
  right_inv _ := rfl

theorem zeroRootFiber_infinite (W : Submodule ℚ TailSpace) : Infinite (RootFiber W 0 0) :=
  Infinite.of_injective (zeroRootFiberEquiv W).symm (zeroRootFiberEquiv W).symm.injective

/-- Nat.card = 0 at multiplier zero must not be read as a proof of emptiness. -/
theorem zeroRootFiber_card (W : Submodule ℚ TailSpace) : Nat.card (RootFiber W 0 0) = 0 := by
  let := zeroRootFiber_infinite W
  exact Nat.card_eq_zero_of_infinite

theorem zeroRootFiber_nonempty (W : Submodule ℚ TailSpace) : Nonempty (RootFiber W 0 0) :=
  ⟨⟨0, zero_nsmul 0⟩⟩

/-- Zero multiplication at a nonzero target has no root. -/
theorem zeroRootFiber_isEmpty_of_ne_zero (W : Submodule ℚ TailSpace) (x : preimage W)
    (hx : x ≠ 0) : IsEmpty (RootFiber W 0 x) := by
  apply rootFiber_isEmpty
  rintro ⟨y, hy⟩
  exact hx (by simpa using hy.symm)

end RealizationBoundaries
