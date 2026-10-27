import RealizationBoundaries.Countability
import RealizationBoundaries.TailSignature
import RealizationBoundaries.ProductTopology

/-!
# Diagonality of arbitrary homomorphisms

The coefficient at a prime is defined by the image of the actual prime seed.
The coordinate formula is derived from prime-root solvability, without assuming
continuity, linearity over the product ring, or a prescribed diagonal action.
-/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- The original prime seed regarded as a member of an arbitrary rational preimage. -/
def preimageSeed (W : Submodule ℚ TailSpace) (p : Prime) : preimage W :=
  ⟨(primeSeed p).val, finiteSupport_le_preimage W (primeSeed p).property⟩

@[simp] theorem preimageSeed_apply (W : Submodule ℚ TailSpace) (p : Prime) :
    (preimageSeed W p).val p = 1 := by
  classical
  simp [preimageSeed, primeSeed, cut]

/-- A homomorphism preserves a zero prime coordinate because it preserves roots. -/
theorem hom_preserves_zero_coordinate (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) (x : preimage U) (p : Prime)
    (hx : x.val p = 0) : (f x).val p = 0 :=
  (preimage_prime_root_iff V (f x) p).mp
    (hasPrimeRoot_map f x p ((preimage_prime_root_iff U x p).mpr hx))

/-- Coefficients are recovered from the given homomorphism, not chosen as hypotheses. -/
def homDiagonal (U V : Submodule ℚ TailSpace) (f : preimage U →+ preimage V) : Ambient :=
  fun p => (f (preimageSeed U p)).val p

/-- Subtract a multiple of one prime seed and use the root criterion on the remainder. -/
theorem hom_coordinate_formula (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) (x : preimage U) (p : Prime) :
    (f x).val p = homDiagonal U V f p * x.val p := by
  let n := (x.val p).val
  let e := preimageSeed U p
  have hz : (x - n • e).val p = 0 := by
    change x.val p - n • e.val p = 0
    simp [n, e, nsmul_eq_mul]
  have h := hom_preserves_zero_coordinate U V f (x - n • e) p hz
  rw [map_sub, map_nsmul] at h
  change (f x).val p - n • (f e).val p = 0 at h
  simpa [n, e, homDiagonal, nsmul_eq_mul, mul_comm] using sub_eq_zero.mp h

/-- The coefficient family is unique, since each prime seed is an actual source element. -/
theorem homDiagonal_unique (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) (c : Ambient)
    (h : ∀ x : preimage U, ∀ p : Prime, (f x).val p = c p * x.val p) :
    c = homDiagonal U V f := by
  funext p
  simpa [homDiagonal] using (h (preimageSeed U p) p).symm

/-- Scalar families determine homomorphisms on the entire infinite group. -/
theorem homDiagonal_injective (U V : Submodule ℚ TailSpace) :
    Function.Injective (homDiagonal U V) := by
  intro f g h
  apply AddMonoidHom.ext
  intro x
  apply Subtype.ext
  funext p
  rw [hom_coordinate_formula U V f, hom_coordinate_formula U V g, h]

/-- Coordinate multiplication on the unrestricted product. -/
def diagonal (c : Ambient) : Ambient →+ Ambient where
  toFun x p := c p * x p
  map_zero' := by funext p; simp
  map_add' x y := by funext p; exact mul_add (c p) (x p) (y p)

@[simp] theorem diagonal_apply (c x : Ambient) (p : Prime) :
    diagonal c x p = c p * x p := rfl

@[simp] theorem diagonal_one (x : Ambient) : diagonal 1 x = x := by
  funext p
  simp

@[simp] theorem diagonal_add (c d x : Ambient) :
    diagonal (c + d) x = diagonal c x + diagonal d x := by
  funext p
  exact add_mul (c p) (d p) (x p)

@[simp] theorem diagonal_mul (c d x : Ambient) :
    diagonal (c * d) x = diagonal c (diagonal d x) := by
  funext p
  exact mul_assoc (c p) (d p) (x p)

/-- Arbitrary diagonal families preserve finite support. -/
theorem diagonal_finiteSupport (c : Ambient) (x : Ambient) (hx : x ∈ finiteSupport) :
    diagonal c x ∈ finiteSupport := by
  apply (show (support x).Finite from hx).subset
  intro p hp hxp
  exact hp (by simp [hxp])

/-- The original map is exactly the restriction of its recovered ambient diagonal. -/
theorem hom_eq_diagonal (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) (x : preimage U) :
    (f x).val = diagonal (homDiagonal U V f) x.val := by
  funext p
  exact hom_coordinate_formula U V f x p

/-- Every coordinate multiplier is continuous for the actual product topology. -/
theorem diagonal_continuous (c : Ambient) : Continuous (diagonal c) := by
  apply continuous_pi
  intro p
  exact (continuous_of_discreteTopology : Continuous (fun z : Coordinate p => c p * z)).comp
    (continuous_apply p)

/-- Automatic continuity: the abstract homomorphism needs no topological hypothesis. -/
theorem preimage_hom_continuous (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) : Continuous f := by
  apply continuous_induced_rng.mpr
  have he : (fun x : preimage U => (f x).val) =
      (diagonal (homDiagonal U V f)) ∘ (fun x : preimage U => x.val) := by
    funext x
    exact hom_eq_diagonal U V f x
  rw [show (Subtype.val ∘ f) = (fun x : preimage U => (f x).val) from rfl, he]
  exact (diagonal_continuous _).comp continuous_subtype_val

/-- The induced quotient map exists because preservation of D was proved. -/
def diagonalTailAdd (c : Ambient) : TailSpace →+ TailSpace :=
  QuotientAddGroup.map finiteSupport finiteSupport (diagonal c)
    (fun x hx => diagonal_finiteSupport c x hx)

@[simp] theorem diagonalTailAdd_quotient (c x : Ambient) :
    diagonalTailAdd c (quotientMap x) = quotientMap (diagonal c x) := rfl

/-- Rational linearity follows from unique division, not an assumed scalar action. -/
def diagonalTail (c : Ambient) : TailSpace →ₗ[ℚ] TailSpace where
  toAddHom := diagonalTailAdd c
  map_smul' r x := map_rat_smul (diagonalTailAdd c) r x

@[simp] theorem diagonalTail_quotient (c x : Ambient) :
    diagonalTail c (quotientMap x) = quotientMap (diagonal c x) := rfl

@[simp] theorem diagonalTail_one (v : TailSpace) : diagonalTail 1 v = v := by
  obtain ⟨x, rfl⟩ := quotientMap_surjective v
  simp

@[simp] theorem diagonalTail_add (c d : Ambient) (v : TailSpace) :
    diagonalTail (c + d) v = diagonalTail c v + diagonalTail d v := by
  obtain ⟨x, rfl⟩ := quotientMap_surjective v
  simp

@[simp] theorem diagonalTail_mul (c d : Ambient) (v : TailSpace) :
    diagonalTail (c * d) v = diagonalTail c (diagonalTail d v) := by
  obtain ⟨x, rfl⟩ := quotientMap_surjective v
  simp

end RealizationBoundaries
