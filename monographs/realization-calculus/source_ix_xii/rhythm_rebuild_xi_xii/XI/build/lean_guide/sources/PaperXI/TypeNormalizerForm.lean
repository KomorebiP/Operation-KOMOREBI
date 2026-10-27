import PaperXI.TypeNormalizerPairing

/-! The source-facing field-valued form: the ambient quotient action is
transported to the declared vector-space coordinates, then preservation is
proved from the actual character commutator. Residue-field linearity is explicit. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TypeNormalizerForm
open TypeNormalizerAction TypeNormalizerPairing
open scoped IsMulCommutative

variable {J k X : Type*} [Group J] [Field k] [AddCommGroup X] [Module k X]

/-- The genuine quotient action in the supplied vector-space coordinates. -/
def coordinateAction (N : Subgroup J) [N.Normal] (H : Subgroup N)
    [H.Normal] [IsMulCommutative (N ⧸ H)] (hH : Stable N H)
    (e : (N ⧸ H) ≃* Multiplicative X) : (J ⧸ N) →* MulAut (Multiplicative X) where
  toFun j := (e.symm.trans (quotientAction N H hH j)).trans e
  map_one' := by
    ext x
    simp [MulEquiv.trans_apply]
  map_mul' a b := by
    ext x
    simp [MulEquiv.trans_apply]

@[simp] theorem coordinateAction_apply (N : Subgroup J) [N.Normal]
    (H : Subgroup N) [H.Normal] [IsMulCommutative (N ⧸ H)] (hH : Stable N H)
    (e : (N ⧸ H) ≃* Multiplicative X) (j : J ⧸ N) (x : Multiplicative X) :
    coordinateAction N H hH e j x = e (quotientAction N H hH j (e.symm x)) := rfl

/-- Scalar compatibility upgrades the actual additive automorphism to a linear
one; it does not assume form preservation. -/
def linearAut (a : MulAut (Multiplicative X))
    (hs : ∀ c : k, ∀ x : X, (a (Multiplicative.ofAdd (c • x))).toAdd =
      c • (a (Multiplicative.ofAdd x)).toAdd) : X ≃ₗ[k] X where
  toFun x := (a (Multiplicative.ofAdd x)).toAdd
  invFun x := (a.symm (Multiplicative.ofAdd x)).toAdd
  left_inv x := congrArg Multiplicative.toAdd (a.symm_apply_apply (Multiplicative.ofAdd x))
  right_inv x := congrArg Multiplicative.toAdd (a.apply_symm_apply (Multiplicative.ofAdd x))
  map_add' x y := congrArg Multiplicative.toAdd (a.map_mul (Multiplicative.ofAdd x) (Multiplicative.ofAdd y))
  map_smul' c x := hs c x

/-- The action on the actual source vector space. -/
def vectorAction (N : Subgroup J) [N.Normal] (H : Subgroup N)
    [H.Normal] [IsMulCommutative (N ⧸ H)] (hH : Stable N H)
    (e : (N ⧸ H) ≃* Multiplicative X)
    (hs : ∀ j : J ⧸ N, ∀ c : k, ∀ x : X,
      (coordinateAction N H hH e j (Multiplicative.ofAdd (c • x))).toAdd =
        c • (coordinateAction N H hH e j (Multiplicative.ofAdd x)).toAdd) :
    (J ⧸ N) →* (X ≃ₗ[k] X) where
  toFun j := linearAut (coordinateAction N H hH e j) (hs j)
  map_one' := by
    ext x
    change (coordinateAction N H hH e 1 (Multiplicative.ofAdd x)).toAdd = x
    rw [map_one]
    rfl
  map_mul' a b := by
    ext x
    change (coordinateAction N H hH e (a*b) (Multiplicative.ofAdd x)).toAdd =
      (coordinateAction N H hH e a (coordinateAction N H hH e b (Multiplicative.ofAdd x))).toAdd
    rw [map_mul]
    rfl

/-- Corrected source 10.3: an honest quotient action preserves the given
field-valued form. The nontrivial character may have a nontrivial kernel. -/
theorem source_form_preserved (N : Subgroup J) [N.Normal]
    (H : Subgroup N) [H.Normal] [IsMulCommutative (N ⧸ H)]
    (hH : Stable N H) (θ : H →* ℂˣ) (hθ : CharacterInvariant N H hH θ)
    (e : (N ⧸ H) ≃* Multiplicative X)
    (hs : ∀ j : J ⧸ N, ∀ c : k, ∀ x : X,
      (coordinateAction N H hH e j (Multiplicative.ofAdd (c • x))).toAdd =
        c • (coordinateAction N H hH e j (Multiplicative.ofAdd x)).toAdd)
    (B : X →ₗ[k] X →ₗ[k] k) (ψ : AddChar k ℂˣ) (hψ : ψ ≠ 1)
    (hsource : ∀ a b, ψ (B (e a).toAdd (e b).toAdd) = pairing N H hH θ hθ a b)
    (j : J ⧸ N) (x y : X) :
    B (vectorAction N H hH e hs j x) (vectorAction N H hH e hs j y) = B x y := by
  apply fieldForm_preserved B (vectorAction N H hH e hs j) ψ hψ
  intro u v
  let a := e.symm (Multiplicative.ofAdd u)
  let b := e.symm (Multiplicative.ofAdd v)
  have hp := (hsource (quotientAction N H hH j a) (quotientAction N H hH j b)).trans
    ((quotientAction_preserves_pairing N H hH θ hθ j a b).trans (hsource a b).symm)
  simpa [vectorAction, linearAut, coordinateAction, a, b] using hp

end PaperXI.TypeNormalizerForm
