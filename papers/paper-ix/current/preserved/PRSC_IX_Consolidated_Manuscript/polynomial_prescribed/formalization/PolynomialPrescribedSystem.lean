module

public import PolynomialParameterSystem
public import FiniteFiberCounts

@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialPrescribedSystem

open scoped BigOperators
open Komorebi.NativeAffine Komorebi.PolynomialDigitBridge
open Komorebi.FiniteFiberCounts

variable {m k e : ℕ}

/-- The actual Jacobian block for the coordinates that may be solved. -/
def solvedJacobian (q : ℕ) (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (x : Fin (m + k) → ℤ) : (Fin m → ZMod q) →ₗ[ZMod q] (Fin e → ZMod q) where
  toFun u i := ∑ j,
    (MvPolynomial.eval x (MvPolynomial.pderiv (Fin.castAdd k j) (F i)) : ZMod q) * u j
  map_add' u v := by ext i; simp [mul_add, Finset.sum_add_distrib]
  map_smul' a u := by
    ext i
    simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro j _
    ring

/-- The actual Jacobian block for the prescribed parameter coordinates. -/
def parameterJacobian (q : ℕ) (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (x : Fin (m + k) → ℤ) : (Fin k → ZMod q) →ₗ[ZMod q] (Fin e → ZMod q) where
  toFun v i := ∑ j,
    (MvPolynomial.eval x (MvPolynomial.pderiv (Fin.natAdd m j) (F i)) : ZMod q) * v j
  map_add' u v := by ext i; simp [mul_add, Finset.sum_add_distrib]
  map_smul' a u := by
    ext i
    simp only [Pi.smul_apply, smul_eq_mul, RingHom.id_apply]
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro j _
    ring

/-- The full Jacobian splits into the two actual coordinate blocks. -/
theorem digitJacobian_join (q : ℕ) (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (x : Fin (m + k) → ℤ) (u : Fin m → ZMod q) (v : Fin k → ZMod q) :
    digitJacobian q F x (PolynomialParameterSystem.join u v) =
      solvedJacobian q F x u + parameterJacobian q F x v := by
  ext i
  simp [digitJacobian, solvedJacobian, parameterJacobian, Fin.sum_univ_add]

/-- A prescribed parameter digit shifts the residual by its actual Jacobian image. -/
def parameterResidual (q : ℕ) (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (x : Fin (m + k) → ℤ) (r : Fin e → ℤ) (v : Fin k → ZMod q) : Fin e → ZMod q :=
  reduction q e r + parameterJacobian q F x v

/-- The obstruction lies in the cokernel of the solved block alone. -/
abbrev PrescribedObstruction (q : ℕ) (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (x : Fin (m + k) → ℤ) :=
  (Fin e → ZMod q) ⧸ (solvedJacobian q F x).range

/-- The actual residual class after imposing the parameter digit. -/
def obstruction (q : ℕ) (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (x : Fin (m + k) → ℤ) (r : Fin e → ℤ) (v : Fin k → ZMod q) :
    PrescribedObstruction q F x :=
  Submodule.Quotient.mk (parameterResidual q F x r v)

/-- The solved-coordinate digits compatible with the prescribed parameter digit. -/
abbrev PrescribedDigits (q : ℕ) (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (x : Fin (m + k) → ℤ) (r : Fin e → ℤ) (v : Fin k → ZMod q) :=
  Fiber (solvedJacobian q F x) (parameterResidual q F x r v)

/-- The prescribed correction equation is exactly the full digit equation. -/
theorem prescribed_equation_iff (q : ℕ) (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (x : Fin (m + k) → ℤ) (r : Fin e → ℤ) (v : Fin k → ZMod q) (u : Fin m → ZMod q) :
    parameterResidual q F x r v + solvedJacobian q F x u = 0 ↔
      reduction q e r + digitJacobian q F x (PolynomialParameterSystem.join u v) = 0 := by
  rw [digitJacobian_join]
  simp only [parameterResidual, add_assoc, add_comm (parameterJacobian q F x v)]

/-- Vanishing of the solved-block obstruction is precisely digit existence. -/
theorem prescribed_digits_nonempty_iff (q : ℕ)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (x : Fin (m + k) → ℤ) (r : Fin e → ℤ) (v : Fin k → ZMod q) :
    Nonempty (PrescribedDigits q F x r v) ↔ obstruction q F x r v = 0 := by
  exact fiber_nonempty_iff_class_zero (solvedJacobian q F x) (parameterResidual q F x r v)

/-- Positive moduli give a finite correction problem, including composite moduli. -/
theorem prescribed_digits_finite (q : ℕ) (hq : 0 < q)
    (F : Fin e → MvPolynomial (Fin (m + k)) ℤ)
    (x : Fin (m + k) → ℤ) (r : Fin e → ℤ) (v : Fin k → ZMod q) :
    Finite (PrescribedDigits q F x r v) := by
  let : NeZero q := ⟨Nat.ne_of_gt hq⟩
  unfold PrescribedDigits Fiber
  infer_instance

end Komorebi.PolynomialPrescribedSystem
