import Mathlib.LinearAlgebra.Dual.Lemmas
import Mathlib.Tactic.Ring

/-! The Heisenberg group in position, frequency, and central coordinates.
The alternating bilinear cocycle defines a group in every characteristic.
Identifying its commutator with the symplectic pairing additionally needs 2 ≠ 0. -/
set_option autoImplicit false

namespace PaperXI.Heisenberg

@[ext]
structure Element (K X : Type*) [Field K] [AddCommGroup X] [Module K X] where
  position : X
  frequency : Module.Dual K X
  central : K

variable {K X : Type*} [Field K] [AddCommGroup X] [Module K X]

instance instMul : Mul (Element K X) where
  mul a b := ⟨a.position + b.position, a.frequency + b.frequency,
    a.central + b.central + (2 : K)⁻¹ * (b.frequency a.position - a.frequency b.position)⟩

instance instOne : One (Element K X) where
  one := ⟨0, 0, 0⟩

instance instInv : Inv (Element K X) where
  inv a := ⟨-a.position, -a.frequency, -a.central⟩

@[simp] theorem mul_position (a b : Element K X) :
    (a * b).position = a.position + b.position := rfl

@[simp] theorem mul_frequency (a b : Element K X) :
    (a * b).frequency = a.frequency + b.frequency := rfl

@[simp] theorem mul_central (a b : Element K X) :
    (a * b).central = a.central + b.central +
      (2 : K)⁻¹ * (b.frequency a.position - a.frequency b.position) := rfl

@[simp] theorem one_position : (1 : Element K X).position = 0 := rfl
@[simp] theorem one_frequency : (1 : Element K X).frequency = 0 := rfl
@[simp] theorem one_central : (1 : Element K X).central = 0 := rfl
@[simp] theorem inv_position (a : Element K X) : a⁻¹.position = -a.position := rfl
@[simp] theorem inv_frequency (a : Element K X) : a⁻¹.frequency = -a.frequency := rfl
@[simp] theorem inv_central (a : Element K X) : a⁻¹.central = -a.central := rfl

/-- The alternating cocycle gives the actual Heisenberg group operation. -/
instance instGroup : Group (Element K X) where
  mul_assoc a b c := by
    ext <;> simp [add_assoc, map_add]
    ring
  one_mul a := by
    ext <;> simp
  mul_one a := by
    ext <;> simp
  inv_mul_cancel a := by
    ext <;> simp

/-- Pure central elements. -/
def centralElement (z : K) : Element K X := ⟨0, 0, z⟩

/-- Pure position elements act by translation in the Schrödinger model. -/
def translationElement (x : X) : Element K X := ⟨x, 0, 0⟩

/-- Pure frequency elements act by modulation in the Schrödinger model. -/
def modulationElement (ξ : Module.Dual K X) : Element K X := ⟨0, ξ, 0⟩

@[simp] theorem centralElement_position (z : K) :
    (centralElement (X := X) z).position = 0 := rfl
@[simp] theorem centralElement_frequency (z : K) :
    (centralElement (X := X) z).frequency = 0 := rfl
@[simp] theorem centralElement_central (z : K) :
    (centralElement (X := X) z).central = z := rfl
@[simp] theorem translationElement_position (x : X) :
    (translationElement (K := K) x).position = x := rfl
@[simp] theorem translationElement_frequency (x : X) :
    (translationElement (K := K) x).frequency = 0 := rfl
@[simp] theorem translationElement_central (x : X) :
    (translationElement (K := K) x).central = 0 := rfl
@[simp] theorem modulationElement_position (ξ : Module.Dual K X) :
    (modulationElement ξ).position = 0 := rfl
@[simp] theorem modulationElement_frequency (ξ : Module.Dual K X) :
    (modulationElement ξ).frequency = ξ := rfl
@[simp] theorem modulationElement_central (ξ : Module.Dual K X) :
    (modulationElement ξ).central = 0 := rfl

@[simp] theorem centralElement_zero : centralElement (X := X) (0 : K) = 1 := rfl
@[simp] theorem translationElement_zero : translationElement (K := K) (0 : X) = 1 := rfl
@[simp] theorem modulationElement_zero :
    modulationElement (0 : Module.Dual K X) = 1 := rfl

@[simp] theorem centralElement_mul (z t : K) :
    centralElement (X := X) z * centralElement t = centralElement (z + t) := by
  ext <;> simp

@[simp] theorem translationElement_mul (x y : X) :
    translationElement (K := K) x * translationElement y = translationElement (x + y) := by
  ext <;> simp

@[simp] theorem modulationElement_mul (ξ η : Module.Dual K X) :
    modulationElement ξ * modulationElement η = modulationElement (ξ + η) := by
  ext <;> simp

/-- The central coordinate commutes with every group element. -/
theorem centralElement_commute (z : K) (a : Element K X) :
    Commute (centralElement z) a := by
  show centralElement z * a = a * centralElement z
  ext <;> simp [add_comm]

end PaperXI.Heisenberg
