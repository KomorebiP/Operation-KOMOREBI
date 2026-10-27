import RealizationBoundaries.DiagonalHomomorphisms
import Mathlib.Algebra.Ring.Subring.Basic
import Mathlib.Algebra.Ring.Equiv

/-!
# Exact realization of the diagonal families

A family is admitted precisely when its actual ambient multiplier takes the
source preimage into the target. This condition is equivalent to rational-line
membership and to a finite section defect in the selector setting.
-/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- The condition is on actual points in the two original subgroups. -/
def DiagonalAdmissible (U V : Submodule ℚ TailSpace) (c : Ambient) : Prop :=
  ∀ x : Ambient, x ∈ preimage U → diagonal c x ∈ preimage V

/-- Every recovered family is admissible, as a consequence of the coordinate formula. -/
theorem homDiagonal_admissible (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) : DiagonalAdmissible U V (homDiagonal U V f) := by
  intro x hx
  rw [← hom_eq_diagonal U V f ⟨x, hx⟩]
  exact (f ⟨x, hx⟩).property

/-- Restricting a family is legitimate only after its preservation condition is proved. -/
def diagonalRestriction (U V : Submodule ℚ TailSpace) (c : Ambient)
    (h : DiagonalAdmissible U V c) : preimage U →+ preimage V where
  toFun x := ⟨diagonal c x.val, h x.val x.property⟩
  map_zero' := Subtype.ext (map_zero (diagonal c))
  map_add' x y := Subtype.ext (map_add (diagonal c) x.val y.val)

@[simp] theorem diagonalRestriction_val (U V : Submodule ℚ TailSpace) (c : Ambient)
    (h : DiagonalAdmissible U V c) (x : preimage U) :
    (diagonalRestriction U V c h x).val = diagonal c x.val := rfl

@[simp] theorem homDiagonal_restriction (U V : Submodule ℚ TailSpace) (c : Ambient)
    (h : DiagonalAdmissible U V c) : homDiagonal U V (diagonalRestriction U V c h) = c := by
  funext p
  simp [homDiagonal, diagonalRestriction]

@[simp] theorem diagonalRestriction_recovery (U V : Submodule ℚ TailSpace)
    (f : preimage U →+ preimage V) :
    diagonalRestriction U V (homDiagonal U V f) (homDiagonal_admissible U V f) = f := by
  apply AddMonoidHom.ext
  intro x
  exact Subtype.ext (hom_eq_diagonal U V f x).symm

/-- Classification of all abstract homomorphisms by their unique admissible families. -/
def diagonalHomEquiv (U V : Submodule ℚ TailSpace) :
    (preimage U →+ preimage V) ≃ {c : Ambient // DiagonalAdmissible U V c} where
  toFun f := ⟨homDiagonal U V f, homDiagonal_admissible U V f⟩
  invFun c := diagonalRestriction U V c.val c.property
  left_inv := diagonalRestriction_recovery U V
  right_inv c := Subtype.ext (homDiagonal_restriction U V c.val c.property)

/-- A diagonal map preserves the original preimages exactly when its derived rational
map takes the source subspace into the target subspace. -/
theorem diagonalAdmissible_iff_tail (U V : Submodule ℚ TailSpace) (c : Ambient) :
    DiagonalAdmissible U V c ↔ ∀ v ∈ U, diagonalTail c v ∈ V := by
  constructor
  · intro h v hv
    obtain ⟨x, rfl⟩ := quotientMap_surjective v
    exact h x hv
  · intro h x hx
    exact h (quotientMap x) hx

/-- For lines, the entire preservation contract reduces to the actual generating tail. -/
theorem diagonalAdmissible_selector_iff (S T : Set Prime) (c : Ambient) :
    DiagonalAdmissible (selectorLine S) (selectorLine T) c ↔
      diagonal c (indicator S) ∈ selectorGroup T := by
  constructor
  · intro h
    exact h (indicator S) (markedElement S).property
  · intro h x hx
    obtain ⟨r, hr⟩ := (mem_selectorGroup_iff S x).mp hx
    change quotientMap (diagonal c x) ∈ selectorLine T
    rw [← diagonalTail_quotient, ← hr, map_smul]
    exact (selectorLine T).smul_mem r h

/-- The section defect is finite precisely when the diagonal can be realized. -/
theorem diagonalAdmissible_iff_finite_defect (S T : Set Prime) (c : Ambient) :
    DiagonalAdmissible (selectorLine S) (selectorLine T) c ↔
      ∃ r : ℚ, diagonal c (indicator S) - rationalSection T r ∈ finiteSupport := by
  rw [diagonalAdmissible_selector_iff, mem_selectorGroup_iff]
  constructor
  · rintro ⟨r, hr⟩
    refine ⟨r, (quotientMap_eq_iff _ _).mp ?_⟩
    rw [quotientMap_rationalSection, hr]
  · rintro ⟨r, hr⟩
    refine ⟨r, ?_⟩
    have hq := (quotientMap_eq_iff _ _).mpr hr
    rw [quotientMap_rationalSection] at hq
    exact hq.symm

/-- Monograph Theorem 7.5: exact full-family realization and uniqueness. -/
def selectorHomEquiv (S T : Set Prime) :
    (selectorGroup S →+ selectorGroup T) ≃
      {c : Ambient // ∃ r : ℚ,
        diagonal c (indicator S) - rationalSection T r ∈ finiteSupport} where
  toFun f := ⟨homDiagonal (selectorLine S) (selectorLine T) f,
    (diagonalAdmissible_iff_finite_defect S T _).mp
      (homDiagonal_admissible (selectorLine S) (selectorLine T) f)⟩
  invFun c := diagonalRestriction (selectorLine S) (selectorLine T) c.val
    ((diagonalAdmissible_iff_finite_defect S T c.val).mpr c.property)
  left_inv f := diagonalRestriction_recovery (selectorLine S) (selectorLine T) f
  right_inv c := Subtype.ext (homDiagonal_restriction (selectorLine S) (selectorLine T) c.val
    ((diagonalAdmissible_iff_finite_defect S T c.val).mpr c.property))

/-- The actual admissible families form a subring of the coordinate product. -/
def diagonalEndRing (W : Submodule ℚ TailSpace) : Subring Ambient where
  carrier := {c | DiagonalAdmissible W W c}
  zero_mem' := by
    intro x _
    have hz : diagonal 0 x = 0 := by funext p; simp
    rw [hz]
    exact (preimage W).zero_mem
  one_mem' := by intro x hx; simpa using hx
  add_mem' := by
    intro c d hc hd x hx
    rw [diagonal_add]
    exact (preimage W).add_mem (hc x hx) (hd x hx)
  neg_mem' := by
    intro c hc x hx
    have hn : diagonal (-c) x = -(diagonal c x) := by funext p; simp
    rw [hn]
    exact (preimage W).neg_mem (hc x hx)
  mul_mem' := by
    intro c d hc hd x hx
    rw [diagonal_mul]
    exact hc _ (hd x hx)

/-- Addition and composition of actual endomorphisms become coordinate ring operations. -/
def homDiagonalRing (W : Submodule ℚ TailSpace) :
    AddMonoid.End (preimage W) →+* diagonalEndRing W where
  toFun f := ⟨homDiagonal W W f, homDiagonal_admissible W W f⟩
  map_zero' := rfl
  map_one' := by
    apply Subtype.ext
    funext p
    exact preimageSeed_apply W p
  map_add' _ _ := rfl
  map_mul' f g := by
    apply Subtype.ext
    funext p
    exact hom_coordinate_formula W W f (g (preimageSeed W p)) p

/-- Ring equivalence, not merely a bijection between underlying sets. -/
def endomorphismRingEquiv (W : Submodule ℚ TailSpace) :
    AddMonoid.End (preimage W) ≃+* diagonalEndRing W :=
  RingEquiv.ofBijective (homDiagonalRing W) (by
    constructor
    · intro f g h
      exact homDiagonal_injective W W (congrArg Subtype.val h)
    · intro c
      exact ⟨diagonalRestriction W W c.val c.property,
        Subtype.ext (homDiagonal_restriction W W c.val c.property)⟩)

/-- Commutativity is a proved property of this endomorphism ring. -/
theorem preimage_endomorphisms_commute (W : Submodule ℚ TailSpace)
    (f g : AddMonoid.End (preimage W)) : f * g = g * f := by
  apply (endomorphismRingEquiv W).injective
  simp only [map_mul, mul_comm]

end RealizationBoundaries
