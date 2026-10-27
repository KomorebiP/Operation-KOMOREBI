import RealizationBoundaries.Preimages
import Mathlib.GroupTheory.OrderOfElement

/-! # Canonical integer quotients and cofinal finite-target kernels -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

abbrev DivisorPrime (m : ℕ) := {p : Prime // p.val ∣ m}
abbrev DivisorCoordinates (m : ℕ) := (p : DivisorPrime m) → Coordinate p.val

theorem divisorPrime_finite {m : ℕ} (hm : 0 < m) : Finite (DivisorPrime m) :=
  (exceptional_finite hm).to_subtype

theorem divisorCoordinates_finite {m : ℕ} (hm : 0 < m) : Finite (DivisorCoordinates m) := by
  let : Finite (DivisorPrime m) := divisorPrime_finite hm
  infer_instance

/-- Restriction to the finitely many prime coordinates dividing the multiplier. -/
def coordinateMap (W : Submodule ℚ TailSpace) (m : ℕ) :
    preimage W →+ DivisorCoordinates m where
  toFun x p := x.val p.val
  map_zero' := rfl
  map_add' _ _ := rfl

/-- Extend a finite divisor-coordinate assignment by zero. -/
def coordinateExtension (m : ℕ) (z : DivisorCoordinates m) : Ambient :=
  fun p => if hp : p.val ∣ m then z ⟨p, hp⟩ else 0

theorem coordinateExtension_finite {m : ℕ} (hm : 0 < m) (z : DivisorCoordinates m) :
    coordinateExtension m z ∈ finiteSupport := by
  apply (exceptional_finite hm).subset
  intro p hp
  by_contra hn
  apply hp
  have hn' : ¬ p.val ∣ m := hn
  simp [coordinateExtension, hn']

theorem coordinateMap_surjective (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m) :
    Function.Surjective (coordinateMap W m) := by
  intro z
  refine ⟨⟨coordinateExtension m z,
    finiteSupport_le_preimage W (coordinateExtension_finite hm z)⟩, ?_⟩
  funext p
  change coordinateExtension m z p.val = z p
  simp [coordinateExtension, p.property]

/-- Integer multiplication as a homomorphism on the original group. -/
def integerMultiplication (W : Submodule ℚ TailSpace) (m : ℕ) :
    preimage W →+ preimage W where
  toFun x := m • x
  map_zero' := nsmul_zero m
  map_add' x y := nsmul_add x y m

/-- The actual subgroup m H_W, not just an abstract kernel with the same cardinality. -/
def multiples (W : Submodule ℚ TailSpace) (m : ℕ) : AddSubgroup (preimage W) :=
  (integerMultiplication W m).range

@[simp] theorem mem_multiples (W : Submodule ℚ TailSpace) (m : ℕ) (x : preimage W) :
    x ∈ multiples W m ↔ ∃ y : preimage W, m • y = x := Iff.rfl

/-- Both inclusions are proved using the concrete infinite-coordinate root theorem. -/
theorem coordinateMap_ker (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m) :
    (coordinateMap W m).ker = multiples W m := by
  ext x
  change coordinateMap W m x = 0 ↔ ∃ y : preimage W, m • y = x
  rw [preimage_root_iff W hm x]
  constructor
  · intro h p hp
    exact congrFun h ⟨p, hp⟩
  · intro h
    funext p
    exact h p.val p.property

/-- Monograph Theorem 4.4, algebraic quotient clause, with its canonical coordinate map. -/
def integerQuotientEquiv (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m) :
    (preimage W ⧸ multiples W m) ≃+ DivisorCoordinates m :=
  (QuotientAddGroup.quotientAddEquivOfEq (coordinateMap_ker W hm).symm).trans
    (QuotientAddGroup.quotientKerEquivOfSurjective (coordinateMap W m)
      (coordinateMap_surjective W hm))

@[simp] theorem integerQuotientEquiv_mk (W : Submodule ℚ TailSpace) {m : ℕ}
    (hm : 0 < m) (x : preimage W) :
    integerQuotientEquiv W hm (QuotientAddGroup.mk x) = coordinateMap W m x := by
  rfl

/-- The quotient kernels depend on the prime divisors, not their multiplicities. -/
theorem multiples_eq_of_same_prime_divisors (W : Submodule ℚ TailSpace)
    {m n : ℕ} (hm : 0 < m) (hn : 0 < n)
    (h : ∀ p : Prime, p.val ∣ m ↔ p.val ∣ n) : multiples W m = multiples W n := by
  ext x
  simp only [mem_multiples, preimage_root_iff W hm, preimage_root_iff W hn]
  constructor
  · intro hx p hp
    exact hx p ((h p).mpr hp)
  · intro hx p hp
    exact hx p ((h p).mp hp)

/-- The canonical finite-coordinate transition for divisibility of multipliers. -/
def coordinateRestriction {m n : ℕ} (hmn : m ∣ n) :
    DivisorCoordinates n →+ DivisorCoordinates m where
  toFun z p := z ⟨p.val, dvd_trans p.property hmn⟩
  map_zero' := rfl
  map_add' _ _ := rfl

@[simp] theorem coordinateRestriction_map (W : Submodule ℚ TailSpace)
    {m n : ℕ} (hmn : m ∣ n) (x : preimage W) :
    coordinateRestriction hmn (coordinateMap W n x) = coordinateMap W m x := rfl

/-- Every finite additive target kills a canonical integer-multiple subgroup.
This is the cofinal-kernel input, not a substitute definition of profinite completion. -/
theorem finite_target_kills_multiples (W : Submodule ℚ TailSpace)
    (F : Type*) [AddGroup F] [Fintype F] (f : preimage W →+ F) :
    multiples W (Fintype.card F) ≤ f.ker := by
  rintro x ⟨y, rfl⟩
  change f (Fintype.card F • y) = 0
  rw [map_nsmul]
  exact card_nsmul_eq_zero

/-- A finite-coordinate quotient kernel is contained in the kernel of every finite-target map. -/
theorem finite_target_coordinate_kernel (W : Submodule ℚ TailSpace)
    (F : Type*) [AddGroup F] [Fintype F] (f : preimage W →+ F) :
    (coordinateMap W (Fintype.card F)).ker ≤ f.ker := by
  rw [coordinateMap_ker W Fintype.card_pos]
  exact finite_target_kills_multiples W F f

end RealizationBoundaries
