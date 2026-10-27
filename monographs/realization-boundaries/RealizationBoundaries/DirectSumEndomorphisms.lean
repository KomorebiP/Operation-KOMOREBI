import RealizationBoundaries.DiagonalRealization
import RealizationBoundaries.CompletionConsequences

/-! # The endomorphism ring of the original finite-support subgroup -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- Every coordinate family restricts to the actual finite-support subgroup. -/
def finiteSupportDiagonal (c : Ambient) : AddMonoid.End finiteSupport where
  toFun x := ⟨diagonal c x.val, diagonal_finiteSupport c x.val x.property⟩
  map_zero' := Subtype.ext (map_zero (diagonal c))
  map_add' x y := Subtype.ext (map_add (diagonal c) x.val y.val)

@[simp] theorem finiteSupportDiagonal_apply (c : Ambient) (x : finiteSupport) (p : Prime) :
    (finiteSupportDiagonal c x).val p = c p * x.val p := rfl

/-- Multiplication in the source is coordinatewise; multiplication in the target is composition. -/
def finiteSupportDiagonalRing : Ambient →+* AddMonoid.End finiteSupport where
  toFun := finiteSupportDiagonal
  map_zero' := by
    apply AddMonoidHom.ext
    intro x
    apply Subtype.ext
    funext p
    exact zero_mul (x.val p)
  map_one' := by
    apply AddMonoidHom.ext
    intro x
    apply Subtype.ext
    funext p
    exact one_mul (x.val p)
  map_add' c d := by
    apply AddMonoidHom.ext
    intro x
    apply Subtype.ext
    exact diagonal_add c d x.val
  map_mul' c d := by
    apply AddMonoidHom.ext
    intro x
    apply Subtype.ext
    exact diagonal_mul c d x.val

theorem finiteSupportDiagonalRing_bijective : Function.Bijective finiteSupportDiagonalRing := by
  constructor
  · intro c d h
    funext p
    have he := congrArg (fun f : AddMonoid.End finiteSupport => (f (primeSeed p)).val p) h
    classical
    change c p * (primeSeed p).val p = d p * (primeSeed p).val p at he
    simpa [primeSeed, cut] using he
  · intro f
    let e := bottomFiniteSupportEquiv
    let g : preimage (⊥ : Submodule ℚ TailSpace) →+
        preimage (⊥ : Submodule ℚ TailSpace) :=
      e.symm.toAddMonoidHom.comp (f.comp e.toAddMonoidHom)
    refine ⟨homDiagonal ⊥ ⊥ g, ?_⟩
    apply AddMonoidHom.ext
    intro x
    apply Subtype.ext
    exact (hom_eq_diagonal ⊥ ⊥ g (e.symm x)).symm

/-- Monograph Proposition 2.2: the original direct-sum endomorphism ring, not a proxy. -/
def finiteSupportEndomorphismRingEquiv : AddMonoid.End finiteSupport ≃+* Ambient :=
  (RingEquiv.ofBijective finiteSupportDiagonalRing finiteSupportDiagonalRing_bijective).symm

/-- No arbitrary endomorphism of D can introduce a missing prime coordinate. -/
theorem finiteSupport_endomorphism_coordinate (f : AddMonoid.End finiteSupport)
    (x : finiteSupport) (p : Prime) :
    (f x).val p = finiteSupportEndomorphismRingEquiv f p * x.val p := by
  have he : finiteSupportDiagonalRing (finiteSupportEndomorphismRingEquiv f) = f :=
    (RingEquiv.ofBijective finiteSupportDiagonalRing
      finiteSupportDiagonalRing_bijective).apply_symm_apply f
  exact (congrArg (fun g : AddMonoid.End finiteSupport => (g x).val p) he).symm

theorem finiteSupport_endomorphism_preserves_zero (f : AddMonoid.End finiteSupport)
    (x : finiteSupport) (p : Prime) (hx : x.val p = 0) : (f x).val p = 0 := by
  rw [finiteSupport_endomorphism_coordinate, hx, mul_zero]

end RealizationBoundaries
