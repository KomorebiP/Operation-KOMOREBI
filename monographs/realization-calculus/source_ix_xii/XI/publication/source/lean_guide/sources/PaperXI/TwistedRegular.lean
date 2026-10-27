import PaperXI.CocycleCommutator
import Mathlib.Analysis.Complex.Basic
import Mathlib.LinearAlgebra.StdBasis
import Mathlib.LinearAlgebra.Basis.Basic
import Mathlib.Algebra.Algebra.Subalgebra.Basic
import Mathlib.LinearAlgebra.Dimension.Finite

/-! The faithful twisted left regular operators for an arbitrary normalized
complex unit-valued cocycle. No finite-image hypothesis is used. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TwistedRegular

open CocycleCommutator
variable {A : Type*} [CommGroup A]

/-- Twisted left translation on the space of complex functions. -/
def regular (c : Cocycle A ℂˣ) (a : A) : Module.End ℂ (A → ℂ) where
  toFun f t := (c.coeff a (a⁻¹ * t) : ℂ) * f (a⁻¹ * t)
  map_add' f g := by ext t; simp [mul_add]
  map_smul' z f := by ext t; simp [mul_left_comm]

@[simp] theorem regular_apply (c : Cocycle A ℂˣ) (a : A) (f : A → ℂ) (t : A) :
    regular c a f t = (c.coeff a (a⁻¹ * t) : ℂ) * f (a⁻¹ * t) := rfl

@[simp] theorem regular_one (c : Cocycle A ℂˣ) (hc : Normalized c) :
    regular c 1 = 1 := by
  ext f t
  simp [hc.1]

theorem regular_mul (c : Cocycle A ℂˣ) (a b : A) :
    regular c a * regular c b = (c.coeff a b : ℂ) • regular c (a * b) := by
  ext f t
  have h := congrArg (fun z : ℂˣ => (z : ℂ)) (c.assoc a b ((a * b)⁻¹ * t))
  simp only [Units.val_mul] at h
  have hab : b * ((a * b)⁻¹ * t) = a⁻¹ * t := by simp [mul_assoc]
  have harg : b⁻¹ * (a⁻¹ * t) = (a * b)⁻¹ * t := by simp [mul_assoc]
  simp only [Module.End.mul_apply, regular_apply, LinearMap.smul_apply, Pi.smul_apply,
    smul_eq_mul]
  rw [hab] at h
  rw [harg]
  simpa [mul_assoc, mul_left_comm] using
    congrArg (fun z : ℂ => z * f ((a * b)⁻¹ * t)) h.symm

/-- The identity point mass. -/
def deltaOne : A → ℂ := by
  classical
  exact fun t => if t = 1 then 1 else 0

@[simp] theorem regular_deltaOne [DecidableEq A] (c : Cocycle A ℂˣ) (hc : Normalized c) (a : A) :
    regular c a deltaOne = Pi.single a 1 := by
  classical
  ext t
  by_cases ht : t = a
  · subst t
    simp [deltaOne, hc.2]
  · have hne : a⁻¹ * t ≠ 1 := by
      intro h
      apply ht
      calc
        t = a * (a⁻¹ * t) := by simp
        _ = a := by rw [h, mul_one]
    simp [deltaOne, hne, ht]

/-- Evaluation on the identity point mass recovers all regular basis vectors. -/
def evaluateOne : Module.End ℂ (A → ℂ) →ₗ[ℂ] (A → ℂ) where
  toFun T := T deltaOne
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

theorem regular_linearIndependent [Fintype A] (c : Cocycle A ℂˣ)
    (hc : Normalized c) : LinearIndependent ℂ (regular c) := by
  classical
  apply LinearIndependent.of_comp (evaluateOne (A := A))
  have heq : evaluateOne (A := A) ∘ regular c = ⇑(Pi.basisFun ℂ A) := by
    funext a
    exact (regular_deltaOne c hc a).trans (Pi.basisFun_apply ℂ A a).symm
  rw [heq]
  exact (Pi.basisFun ℂ A).linearIndependent

end PaperXI.TwistedRegular
