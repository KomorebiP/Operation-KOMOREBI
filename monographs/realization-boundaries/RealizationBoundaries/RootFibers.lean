import RealizationBoundaries.FiniteQuotients
import Mathlib.SetTheory.Cardinal.Finite

/-! # Actual integer-root fibers and their translation parameters

Roots are elements of the original infinite preimage group. Translation by a
supplied root identifies the entire fiber with its integer-torsion kernel.
The kernel is then identified with the actual divisor-coordinate product.
-/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- The full fiber of multiplication on the original group. -/
def RootFiber (W : Submodule ℚ TailSpace) (m : ℕ) (x : preimage W) :=
  {y : preimage W // m • y = x}

/-- The actual integer-torsion kernel inside the original group. -/
def rootKernel (W : Submodule ℚ TailSpace) (m : ℕ) : AddSubgroup (preimage W) :=
  (integerMultiplication W m).ker

@[simp] theorem mem_rootKernel (W : Submodule ℚ TailSpace) (m : ℕ) (y : preimage W) :
    y ∈ rootKernel W m ↔ m • y = 0 := Iff.rfl

/-- A kernel element cannot have a nonzero coordinate away from the multiplier. -/
theorem rootKernel_coordinate_zero (W : Submodule ℚ TailSpace) (m : ℕ)
    (y : rootKernel W m) (p : Prime) (hp : ¬ p.val ∣ m) : y.val.val p = 0 := by
  apply coordinate_eq_zero_of_nsmul_eq_zero p hp
  exact congrArg (fun z : preimage W => z.val p) y.property

/-- Zero extension is killed by m, before any finiteness assumption is used. -/
theorem coordinateExtension_annihilated (m : ℕ) (z : DivisorCoordinates m) :
    m • coordinateExtension m z = 0 := by
  funext p
  rw [coordinate_nsmul]
  by_cases hp : p.val ∣ m
  · simp [(coordinate_cast_eq_zero m p).mpr hp]
  · simp [coordinateExtension, hp]

/-- All m-torsion is given by arbitrary values in precisely the prime-divisor coordinates. -/
def rootKernelEquiv (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m) :
    rootKernel W m ≃+ DivisorCoordinates m where
  toFun y := coordinateMap W m y.val
  invFun z := ⟨⟨coordinateExtension m z,
    finiteSupport_le_preimage W (coordinateExtension_finite hm z)⟩,
    Subtype.ext (coordinateExtension_annihilated m z)⟩
  left_inv y := by
    apply Subtype.ext
    apply Subtype.ext
    funext p
    by_cases hp : p.val ∣ m
    · simp [coordinateExtension, coordinateMap, hp]
    · simp [coordinateExtension, hp, rootKernel_coordinate_zero W m y p hp]
  right_inv z := by
    funext p
    simp [coordinateMap, coordinateExtension, p.property]
  map_add' _ _ := rfl

@[simp] theorem rootKernelEquiv_apply (W : Submodule ℚ TailSpace) {m : ℕ}
    (hm : 0 < m) (y : rootKernel W m) (p : DivisorPrime m) :
    rootKernelEquiv W hm y p = y.val.val p.val := rfl

@[simp] theorem rootKernelEquiv_symm_apply (W : Submodule ℚ TailSpace) {m : ℕ}
    (hm : 0 < m) (z : DivisorCoordinates m) :
    ((rootKernelEquiv W hm).symm z).val.val = coordinateExtension m z := rfl

/-- Translation is an equivalence of sets, not an additive equivalence to a nonzero fiber. -/
def rootFiberTranslation (W : Submodule ℚ TailSpace) (m : ℕ) (x : preimage W)
    (y : RootFiber W m x) : rootKernel W m ≃ RootFiber W m x where
  toFun k := ⟨y.val + k.val, by
    rw [nsmul_add, y.property, (mem_rootKernel W m k.val).mp k.property, add_zero]⟩
  invFun z := ⟨z.val - y.val, by
    change m • (z.val - y.val) = 0
    rw [nsmul_sub, z.property, y.property, sub_self]⟩
  left_inv k := by
    apply Subtype.ext
    simp
  right_inv z := by
    apply Subtype.ext
    simp

@[simp] theorem rootFiberTranslation_apply (W : Submodule ℚ TailSpace) (m : ℕ)
    (x : preimage W) (y : RootFiber W m x) (k : rootKernel W m) :
    (rootFiberTranslation W m x y k).val = y.val + k.val := rfl

/-- One actual root and arbitrary divisor-coordinate values parameterize every root exactly once. -/
def rootFiberEquiv (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m)
    (x : preimage W) (y : RootFiber W m x) : RootFiber W m x ≃ DivisorCoordinates m :=
  (rootFiberTranslation W m x y).symm.trans (rootKernelEquiv W hm).toEquiv

/-- Literal affine solution formula in the original ambient product. -/
@[simp] theorem rootFiberEquiv_symm_apply (W : Submodule ℚ TailSpace) {m : ℕ}
    (hm : 0 < m) (x : preimage W) (y : RootFiber W m x) (z : DivisorCoordinates m) :
    ((rootFiberEquiv W hm x y).symm z).val.val =
      y.val.val + coordinateExtension m z := rfl

/-- The coset criterion retains the supplied root and actual kernel membership. -/
theorem rootFiber_coset_iff (W : Submodule ℚ TailSpace) (m : ℕ) (x : preimage W)
    (y : RootFiber W m x) (z : preimage W) :
    m • z = x ↔ z - y.val ∈ rootKernel W m := by
  rw [mem_rootKernel, nsmul_sub, y.property, sub_eq_zero]

/-- Unsolvability gives a genuinely empty type of roots. -/
theorem rootFiber_isEmpty (W : Submodule ℚ TailSpace) (m : ℕ) (x : preimage W)
    (h : ¬ ∃ y : preimage W, m • y = x) : IsEmpty (RootFiber W m x) :=
  ⟨fun y => h ⟨y.val, y.property⟩⟩

/-- Nonempty root fibers are finite for every positive multiplier. -/
theorem rootFiber_finite (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m)
    (x : preimage W) : Finite (RootFiber W m x) := by
  classical
  by_cases h : Nonempty (RootFiber W m x)
  · let y := Classical.choice h
    let : Finite (DivisorCoordinates m) := divisorCoordinates_finite hm
    exact Finite.of_injective (rootFiberEquiv W hm x y) (rootFiberEquiv W hm x y).injective
  · let : IsEmpty (RootFiber W m x) := not_nonempty_iff.mp h
    infer_instance

/-- Kernel finiteness is proved using its explicit coordinate equivalence. -/
theorem rootKernel_finite (W : Submodule ℚ TailSpace) {m : ℕ} (hm : 0 < m) :
    Finite (rootKernel W m) := by
  let : Finite (DivisorCoordinates m) := divisorCoordinates_finite hm
  exact Finite.of_injective (rootKernelEquiv W hm) (rootKernelEquiv W hm).injective

end RealizationBoundaries
