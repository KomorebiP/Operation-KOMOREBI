import PaperXI.TwistedAction
import PaperXI.CocycleBasis

/-! Actual algebra equivalences under normalized scalar changes of basis.
The equivalence is constructed from the canonical bases of the two concrete
twisted algebras; its multiplicativity follows from their proved tables. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TwistedRescaling

open CocycleCommutator Module
variable {A : Type*} [CommGroup A] [Fintype A]

/-- Equality of cocycles transports the actual algebras and their bases. -/
def congrEquiv (c d : Cocycle A ℂˣ) (hc : Normalized c) (hd : Normalized d)
    (h : c = d) : TwistedAlgebra.Algebra c hc ≃ₐ[ℂ] TwistedAlgebra.Algebra d hd := by
  cases h
  exact AlgEquiv.refl

@[simp] theorem congrEquiv_basis (c d : Cocycle A ℂˣ)
    (hc : Normalized c) (hd : Normalized d) (h : c = d) (a : A) :
    congrEquiv c d hc hd h (TwistedAlgebra.basis c hc a) =
      TwistedAlgebra.basis d hd a := by
  cases h
  rfl

/-- The constructed linear equivalence sends each rescaled algebra basis
element to the corresponding scalar multiple in the original algebra. -/
def linearEquiv (c : Cocycle A ℂˣ) (hc : Normalized c)
    (s : A → ℂˣ) (hs : s 1 = 1) :
    TwistedAlgebra.Algebra (rescale c s) (normalized_rescale c hc s hs) ≃ₗ[ℂ]
      TwistedAlgebra.Algebra c hc :=
  (TwistedAlgebra.basis (rescale c s) (normalized_rescale c hc s hs)).equiv
    ((TwistedAlgebra.basis c hc).unitsSMul s) (Equiv.refl A)

@[simp] theorem linearEquiv_basis (c : Cocycle A ℂˣ) (hc : Normalized c)
    (s : A → ℂˣ) (hs : s 1 = 1) (a : A) :
    linearEquiv c hc s hs
      (TwistedAlgebra.basis (rescale c s) (normalized_rescale c hc s hs) a) =
        (s a : ℂ) • TwistedAlgebra.basis c hc a := by
  simp only [linearEquiv, Basis.equiv_apply, Equiv.refl_apply,
    Basis.unitsSMul_apply, Units.smul_def]

set_option backward.isDefEq.respectTransparency false in
/-- The rescaled basis obeys the rescaled cocycle's multiplication table. -/
theorem scaled_basis_mul (c : Cocycle A ℂˣ) (hc : Normalized c)
    (s : A → ℂˣ) (a b : A) :
    ((s a : ℂ) • TwistedAlgebra.basis c hc a) *
      ((s b : ℂ) • TwistedAlgebra.basis c hc b) =
        ((rescale c s).coeff a b : ℂ) •
          ((s (a * b) : ℂ) • TwistedAlgebra.basis c hc (a * b)) := by
  have h := rescaled_basis_mul (B := TwistedAlgebra.Algebra c hc) c
    (TwistedAlgebra.basis c hc) (TwistedAlgebra.basis_mul c hc) s a b
  simpa only [Basis.unitsSMul_apply, Units.smul_def] using h

theorem linearEquiv_one (c : Cocycle A ℂˣ) (hc : Normalized c)
    (s : A → ℂˣ) (hs : s 1 = 1) : linearEquiv c hc s hs 1 = 1 := by
  rw [← TwistedAlgebra.basis_one (rescale c s) (normalized_rescale c hc s hs),
    linearEquiv_basis, hs, Units.val_one, one_smul, TwistedAlgebra.basis_one]

theorem linearEquiv_mul (c : Cocycle A ℂˣ) (hc : Normalized c)
    (s : A → ℂˣ) (hs : s 1 = 1)
    (x y : TwistedAlgebra.Algebra (rescale c s) (normalized_rescale c hc s hs)) :
    linearEquiv c hc s hs (x * y) =
      linearEquiv c hc s hs x * linearEquiv c hc s hs y := by
  classical
  have hBasis (a b : A) :
      linearEquiv c hc s hs
        (TwistedAlgebra.basis (rescale c s) (normalized_rescale c hc s hs) a *
          TwistedAlgebra.basis (rescale c s) (normalized_rescale c hc s hs) b) =
        linearEquiv c hc s hs
          (TwistedAlgebra.basis (rescale c s) (normalized_rescale c hc s hs) a) *
        linearEquiv c hc s hs
          (TwistedAlgebra.basis (rescale c s) (normalized_rescale c hc s hs) b) := by
    rw [TwistedAlgebra.basis_mul, map_smul, linearEquiv_basis,
      linearEquiv_basis, linearEquiv_basis, scaled_basis_mul]
  conv_lhs => rw [← (TwistedAlgebra.basis (rescale c s)
      (normalized_rescale c hc s hs)).sum_repr x,
    ← (TwistedAlgebra.basis (rescale c s) (normalized_rescale c hc s hs)).sum_repr y]
  conv_rhs => rw [← (TwistedAlgebra.basis (rescale c s)
      (normalized_rescale c hc s hs)).sum_repr x,
    ← (TwistedAlgebra.basis (rescale c s) (normalized_rescale c hc s hs)).sum_repr y]
  simp only [Finset.sum_mul, Finset.mul_sum, map_sum, map_smul,
    smul_mul_assoc, mul_smul_comm, hBasis]

/-- The actual twisted algebras of cohomologous normalized cocycles are
isomorphic, with the source-to-target direction matching basis rescaling. -/
def rescaleEquiv (c : Cocycle A ℂˣ) (hc : Normalized c)
    (s : A → ℂˣ) (hs : s 1 = 1) :
    TwistedAlgebra.Algebra (rescale c s) (normalized_rescale c hc s hs) ≃ₐ[ℂ]
      TwistedAlgebra.Algebra c hc :=
  AlgEquiv.ofLinearEquiv (linearEquiv c hc s hs)
    (linearEquiv_one c hc s hs) (linearEquiv_mul c hc s hs)

@[simp] theorem rescaleEquiv_basis (c : Cocycle A ℂˣ) (hc : Normalized c)
    (s : A → ℂˣ) (hs : s 1 = 1) (a : A) :
    rescaleEquiv c hc s hs
      (TwistedAlgebra.basis (rescale c s) (normalized_rescale c hc s hs) a) =
        (s a : ℂ) • TwistedAlgebra.basis c hc a :=
  linearEquiv_basis c hc s hs a

/-- The inverse sends an original basis vector to its inverse scalar multiple. -/
@[simp] theorem rescaleEquiv_symm_basis (c : Cocycle A ℂˣ) (hc : Normalized c)
    (s : A → ℂˣ) (hs : s 1 = 1) (a : A) :
    (rescaleEquiv c hc s hs).symm (TwistedAlgebra.basis c hc a) =
      ((s a)⁻¹ : ℂˣ) •
        TwistedAlgebra.basis (rescale c s) (normalized_rescale c hc s hs) a := by
  apply (rescaleEquiv c hc s hs).injective
  simp only [AlgEquiv.apply_symm_apply, Units.smul_def, map_smul,
    rescaleEquiv_basis, smul_smul]
  simp

variable {B : Type*} [Semiring B] [Algebra ℂ B]

/-- Transport any algebra action through the constructed rescaling map. -/
def transport (c : Cocycle A ℂˣ) (hc : Normalized c)
    (s : A → ℂˣ) (hs : s 1 = 1)
    (F : TwistedAlgebra.Algebra c hc →ₐ[ℂ] B) :
    TwistedAlgebra.Algebra (rescale c s) (normalized_rescale c hc s hs) →ₐ[ℂ] B :=
  F.comp (rescaleEquiv c hc s hs).toAlgHom

@[simp] theorem transport_basis (c : Cocycle A ℂˣ) (hc : Normalized c)
    (s : A → ℂˣ) (hs : s 1 = 1)
    (F : TwistedAlgebra.Algebra c hc →ₐ[ℂ] B) (a : A) :
    transport c hc s hs F
      (TwistedAlgebra.basis (rescale c s) (normalized_rescale c hc s hs) a) =
        (s a : ℂ) • F (TwistedAlgebra.basis c hc a) := by
  simp only [transport, AlgHom.comp_apply, AlgEquiv.coe_toAlgHom, rescaleEquiv_basis, map_smul]

/-- A transported action is determined by the rescaled basis operators. -/
theorem transport_unique (c : Cocycle A ℂˣ) (hc : Normalized c)
    (s : A → ℂˣ) (hs : s 1 = 1)
    (F : TwistedAlgebra.Algebra c hc →ₐ[ℂ] B)
    (G : TwistedAlgebra.Algebra (rescale c s) (normalized_rescale c hc s hs) →ₐ[ℂ] B)
    (hG : ∀ a, G (TwistedAlgebra.basis (rescale c s)
      (normalized_rescale c hc s hs) a) =
        (s a : ℂ) • F (TwistedAlgebra.basis c hc a)) :
    G = transport c hc s hs F := by
  apply AlgHom.toLinearMap_injective
  apply (TwistedAlgebra.basis (rescale c s) (normalized_rescale c hc s hs)).ext
  intro a
  exact (hG a).trans (transport_basis c hc s hs F a).symm

/-- Rescaling induces an equivalence on actual algebra actions. -/
def actionEquiv (c : Cocycle A ℂˣ) (hc : Normalized c)
    (s : A → ℂˣ) (hs : s 1 = 1) :
    (TwistedAlgebra.Algebra c hc →ₐ[ℂ] B) ≃
      (TwistedAlgebra.Algebra (rescale c s) (normalized_rescale c hc s hs) →ₐ[ℂ] B) where
  toFun := transport c hc s hs
  invFun F := F.comp (rescaleEquiv c hc s hs).symm.toAlgHom
  left_inv F := by
    ext x
    exact congrArg F ((rescaleEquiv c hc s hs).apply_symm_apply x)
  right_inv F := by
    ext x
    exact congrArg F ((rescaleEquiv c hc s hs).symm_apply_apply x)

end PaperXI.TwistedRescaling
