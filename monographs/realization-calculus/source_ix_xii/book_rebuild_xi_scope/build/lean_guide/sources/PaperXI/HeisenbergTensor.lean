import PaperXI.FiniteTensor
import PaperXI.CentralProduct
import Mathlib.Analysis.Complex.Basic

/-! The actual tensor action descends from the direct product, with one retained
central factor, to the balanced central product. Its central character occurs once. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.HeisenbergTensor
open TensorProduct

variable {S Z : Type*} [Fintype S] [CommGroup Z]
variable {H A V : S → Type*} [∀ s, Group (H s)] [∀ s, CommGroup (A s)]
variable [∀ s, AddCommGroup (V s)] [∀ s, Module ℂ (V s)]

/-- The central coordinate acts once, in addition to the external tensor action. -/
def ambient (ζ : Z →* ℂˣ) (σ : ∀ s, Representation ℂ (H s) (V s)) :
    Representation ℂ (Z × (∀ s, H s)) (PiTensorProduct ℂ V) where
  toFun x := (ζ x.1 : ℂ) • FiniteTensor.representation σ x.2
  map_one' := by simp
  map_mul' x y := by
    simp only [Prod.fst_mul, Prod.snd_mul, map_mul, Units.val_mul,
      smul_mul_assoc, mul_smul_comm, smul_smul]
    rw [mul_comm (ζ x.1 : ℂ) (ζ y.1 : ℂ)]

omit [Fintype S] in
@[simp] theorem ambient_apply (ζ : Z →* ℂˣ)
    (σ : ∀ s, Representation ℂ (H s) (V s)) (z : Z) (h : ∀ s, H s)
    (x : PiTensorProduct ℂ V) :
    ambient ζ σ (z, h) x = (ζ z : ℂ) • FiniteTensor.representation σ h x := rfl

omit [Fintype S] in
@[simp] theorem ambient_tprod (ζ : Z →* ℂˣ)
    (σ : ∀ s, Representation ℂ (H s) (V s)) (z : Z) (h : ∀ s, H s)
    (v : ∀ s, V s) :
    ambient ζ σ (z, h) (PiTensorProduct.tprod ℂ v) =
      (ζ z : ℂ) • PiTensorProduct.tprod ℂ (fun s => σ s (h s) (v s)) := by
  simp

/-- The balancing relations act trivially, permitting actual quotient descent. -/
theorem ambient_balanced (D : ∀ s, CentralExtension.Datum Z (H s) (A s))
    (ζ : Z →* ℂˣ) (σ : ∀ s, Representation ℂ (H s) (V s))
    (hσ : ∀ s z, σ s ((D s).i z) = (ζ z : ℂ) • LinearMap.id)
    (z : S → Z) : ambient ζ σ (CentralProduct.balanced D z) = 1 := by
  change (ζ ((∏ s, z s)⁻¹) : ℂ) •
      PiTensorProduct.map (fun s => σ s ((D s).i (z s))) = 1
  simp only [hσ, FiniteTensor.scalar_map, smul_smul]
  have hp : (∏ s, (ζ (z s) : ℂ)) = (ζ (∏ s, z s) : ℂ) := by
    simp
  rw [hp]
  rw [map_inv, ← Units.val_mul, inv_mul_cancel, Units.val_one, one_smul]
  rfl

/-- Representation of the genuine central quotient, on the actual finite tensor space. -/
def descend (D : ∀ s, CentralExtension.Datum Z (H s) (A s))
    (ζ : Z →* ℂˣ) (σ : ∀ s, Representation ℂ (H s) (V s))
    (hσ : ∀ s z, σ s ((D s).i z) = (ζ z : ℂ) • LinearMap.id) :
    Representation ℂ (CentralProduct.Group D) (PiTensorProduct ℂ V) :=
  CentralProduct.descend D (ambient ζ σ) (ambient_balanced D ζ σ hσ)

@[simp] theorem descend_mk (D : ∀ s, CentralExtension.Datum Z (H s) (A s))
    (ζ : Z →* ℂˣ) (σ : ∀ s, Representation ℂ (H s) (V s))
    (hσ : ∀ s z, σ s ((D s).i z) = (ζ z : ℂ) • LinearMap.id)
    (x : Z × (∀ s, H s)) :
    descend D ζ σ hσ (CentralProduct.mk D x) = ambient ζ σ x := rfl

/-- Formula on pure tensors for representatives of every element of the quotient. -/
theorem descend_tprod (D : ∀ s, CentralExtension.Datum Z (H s) (A s))
    (ζ : Z →* ℂˣ) (σ : ∀ s, Representation ℂ (H s) (V s))
    (hσ : ∀ s z, σ s ((D s).i z) = (ζ z : ℂ) • LinearMap.id)
    (z : Z) (h : ∀ s, H s) (v : ∀ s, V s) :
    descend D ζ σ hσ (CentralProduct.mk D (z, h)) (PiTensorProduct.tprod ℂ v) =
      (ζ z : ℂ) • PiTensorProduct.tprod ℂ (fun s => σ s (h s) (v s)) := by
  simp

/-- The total distinguished center has the prescribed character, to the first power. -/
theorem central (D : ∀ s, CentralExtension.Datum Z (H s) (A s))
    (ζ : Z →* ℂˣ) (σ : ∀ s, Representation ℂ (H s) (V s))
    (hσ : ∀ s z, σ s ((D s).i z) = (ζ z : ℂ) • LinearMap.id) (z : Z) :
    descend D ζ σ hσ ((CentralProduct.datum D).i z) =
      (ζ z : ℂ) • LinearMap.id := by
  change ambient ζ σ (z, 1) = _
  change (ζ z : ℂ) • FiniteTensor.representation σ 1 = _
  rw [map_one]
  rfl

/-- In an empty family, the tensor unit still carries the central character. -/
theorem empty_central [IsEmpty S]
    (D : ∀ s, CentralExtension.Datum Z (H s) (A s))
    (ζ : Z →* ℂˣ) (σ : ∀ s, Representation ℂ (H s) (V s))
    (hσ : ∀ s z, σ s ((D s).i z) = (ζ z : ℂ) • LinearMap.id)
    (z : Z) (x : PiTensorProduct ℂ V) :
    PiTensorProduct.isEmptyEquiv S
        (descend D ζ σ hσ ((CentralProduct.datum D).i z) x) =
      (ζ z : ℂ) * PiTensorProduct.isEmptyEquiv S x := by
  rw [central]
  simp

end PaperXI.HeisenbergTensor
