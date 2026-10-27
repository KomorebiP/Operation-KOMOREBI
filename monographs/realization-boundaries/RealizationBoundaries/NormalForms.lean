import RealizationBoundaries.Cocycle

/-! # A distinct normal-form group, not the split direct-product group -/
set_option autoImplicit false
noncomputable section
namespace RealizationBoundaries

/-- A separate type prevents accidental use of the split addition on ℚ × D. -/
structure NormalForm (S : Set Prime) where
  rational : ℚ
  finite : finiteSupport

namespace NormalForm

def toPair {S : Set Prime} (x : NormalForm S) : ℚ × finiteSupport :=
  (x.rational, x.finite)

def pairEquiv (S : Set Prime) : NormalForm S ≃ (ℚ × finiteSupport) where
  toFun := toPair
  invFun x := ⟨x.1, x.2⟩
  left_inv _ := rfl
  right_inv _ := rfl

instance (S : Set Prime) : Zero (NormalForm S) := ⟨⟨0,0⟩⟩
instance (S : Set Prime) : Add (NormalForm S) :=
  ⟨fun x y => ⟨x.rational+y.rational, x.finite+y.finite+cocycle S x.rational y.rational⟩⟩
instance (S : Set Prime) : Neg (NormalForm S) := ⟨fun x => ⟨-x.rational,-x.finite⟩⟩

instance (S : Set Prime) : AddCommGroup (NormalForm S) where
  nsmul := nsmulRec
  zsmul := zsmulRec
  add_assoc x y z := (pairEquiv S).injective (normalAdd_assoc S x.toPair y.toPair z.toPair)
  add_zero x := (pairEquiv S).injective (normalAdd_zero S x.toPair)
  zero_add x := (pairEquiv S).injective
    ((normalAdd_comm S (0,0) x.toPair).trans (normalAdd_zero S x.toPair))
  neg_add_cancel x := (pairEquiv S).injective
    ((normalAdd_comm S (-x.rational,-x.finite) x.toPair).trans (normalAdd_inverse S x.toPair))
  add_comm x y := (pairEquiv S).injective (normalAdd_comm S x.toPair y.toPair)

@[simp] theorem toPair_add {S : Set Prime} (x y : NormalForm S) :
    (x+y).toPair = normalAdd S x.toPair y.toPair := rfl

@[simp] theorem rational_add {S : Set Prime} (x y : NormalForm S) :
    (x+y).rational = x.rational+y.rational := rfl

@[simp] theorem finite_add {S : Set Prime} (x y : NormalForm S) :
    (x+y).finite = x.finite+y.finite+cocycle S x.rational y.rational := rfl

/-- The exact group isomorphism from cocycle coordinates to the actual ambient preimage. -/
def realizationEquiv {S : Set Prime} (hS : S.Infinite) : NormalForm S ≃+ selectorGroup S where
  toEquiv := (pairEquiv S).trans (normalFormEquiv hS)
  map_add' x y := normalEvaluate_add S x.toPair y.toPair

@[simp] theorem realizationEquiv_coe {S : Set Prime} (hS : S.Infinite) (x : NormalForm S) :
    (realizationEquiv hS x).val = rationalSection S x.rational+x.finite.val := rfl

end NormalForm
end RealizationBoundaries
