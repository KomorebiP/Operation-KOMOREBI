module
public import PolynomialMotionControls
public import PolynomialParameterSystem
public import PolynomialJointSystem
public import Mathlib.Tactic

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialJointMotionControls
open MvPolynomial PolynomialParameterSystem

@[simp] theorem join_one_zero {R : Type*} (y t : Fin 1 → R) :
    join y t (0 : Fin (1 + 1)) = y 0 := rfl

@[simp] theorem join_one_one {R : Type*} (y t : Fin 1 → R) :
    join y t (1 : Fin (1 + 1)) = t 0 := rfl

/-- Both the solved coordinate and the prescribed parameter enter this equation. -/
def linearSystem : Fin 1 → MvPolynomial (Fin (1 + 1)) ℤ_[2] :=
  fun _ => X (Fin.castAdd 1 0) + X (Fin.natAdd 1 0)

/-- A nonzero coefficient perturbation, independent of the parameter shift. -/
def linearPerturbation : Fin 1 → MvPolynomial (Fin (1 + 1)) ℤ_[2] :=
  fun _ => C 1

/-- The exact base root and both derivative contributions are nontrivial as intended. -/
theorem linear_base_data :
    eval (0 : Fin (1 + 1) → ℤ_[2]) (linearSystem 0) = 0 ∧
    eval (0 : Fin (1 + 1) → ℤ_[2])
      (pderiv (Fin.castAdd 1 0) (linearSystem 0)) = 1 ∧
    eval (0 : Fin (1 + 1) → ℤ_[2])
      (pderiv (Fin.natAdd 1 0) (linearSystem 0)) = 1 ∧
    eval (0 : Fin (1 + 1) → ℤ_[2]) (linearPerturbation 0) = 1 := by
  norm_num [linearSystem, linearPerturbation, pderiv_X, Pi.single_apply, Fin.ext_iff]

/-- For p=2, M=1, v=1, the prescribed parameter is 2 and the solved root is -4. -/
theorem linear_joint_root :
    eval (join (fun _ : Fin 1 => (-4 : ℤ_[2])) (fun _ : Fin 1 => (2 : ℤ_[2])))
      (linearSystem 0 + C ((2 : ℤ_[2]) ^ 1) * linearPerturbation 0) = 0 ∧
    freePart (join (fun _ : Fin 1 => (-4 : ℤ_[2])) (fun _ : Fin 1 => (2 : ℤ_[2]))) =
      (fun _ : Fin 1 => (2 : ℤ_[2])) := by
  constructor
  · norm_num [linearSystem, linearPerturbation]
  · exact freePart_join _ _

/-- Every root with the prescribed parameter equals the displayed root. -/
theorem linear_joint_unique (y : Fin 1 → ℤ_[2])
    (hy : ∀ i, eval (join y (fun _ : Fin 1 => (2 : ℤ_[2])))
      (linearSystem i + C ((2 : ℤ_[2]) ^ 1) * linearPerturbation i) = 0) :
    y = (fun _ : Fin 1 => (-4 : ℤ_[2])) := by
  ext i
  fin_cases i
  have h := hy 0
  simp [linearSystem, linearPerturbation] at h
  change y 0 = -4
  linear_combination h

/-- The response contains both H(a)=1 and K v=1, with the same negative sign. -/
theorem linear_joint_forcing_and_error :
    eval (0 : Fin (1 + 1) → ℤ_[2]) (linearPerturbation 0) +
      eval (0 : Fin (1 + 1) → ℤ_[2])
        (pderiv (Fin.natAdd 1 0) (linearSystem 0)) * 1 = 2 ∧
    (-4 : ℤ_[2]) = -(2 : ℤ_[2]) ^ 1 * (1 + 1) + 0 ∧
    (2 : ℤ_[2]) ^ 2 ∣ (0 : ℤ_[2]) := by
  norm_num [linearSystem, linearPerturbation, pderiv_X, Pi.single_apply, Fin.ext_iff]

/-- The actual solved and parameter Jacobian matrices both equal the identity. -/
theorem linear_actual_jacobians :
    PolynomialJointSystem.solvedJacobian linearSystem (0 : Fin (1 + 1) → ℤ_[2]) =
      (1 : Matrix (Fin 1) (Fin 1) ℤ_[2]) ∧
    PolynomialJointSystem.parameterJacobian linearSystem (0 : Fin (1 + 1) → ℤ_[2]) =
      (1 : Matrix (Fin 1) (Fin 1) ℤ_[2]) := by
  constructor <;> ext i j <;> fin_cases i <;> fin_cases j <;>
    norm_num [PolynomialJointSystem.solvedJacobian, PolynomialJointSystem.parameterJacobian,
      linearSystem, pderiv_X, Pi.single_apply, Matrix.one_apply, Fin.ext_iff]

/-- At M=2 the actual augmented system has solved root -8 and prescribed parameter 4.
This precision distinguishes an incorrect response formula from its allowed error. -/
theorem linear_augmented_root_depth_two :
    ∀ i, eval (join (fun _ : Fin 1 => (-8 : ℤ_[2])) (fun _ : Fin 1 => (4 : ℤ_[2])))
      (PolynomialMotionNormalization.perturbSystem 2 2
        (PolynomialJointSystem.augmented linearSystem (0 : Fin 1 → ℤ_[2]))
        (PolynomialJointSystem.augmentedPerturbation linearPerturbation
          (fun _ : Fin 1 => (1 : ℤ_[2]))) i) = 0 := by
  apply (PolynomialJointSystem.perturb_augmented_root_iff 2 2 linearSystem linearPerturbation
    (0 : Fin 1 → ℤ_[2]) (fun _ : Fin 1 => (1 : ℤ_[2])) _).mpr
  constructor
  · intro i
    norm_num [linearSystem, linearPerturbation]
  · rw [freePart_join]
    ext i
    norm_num

/-- Omitting K v fails even modulo the permitted first-order error ideal. -/
theorem omitted_parameter_term_fails :
    ¬ (2 : ℤ_[2]) ^ 4 ∣ (-8 : ℤ_[2]) - (-(2 : ℤ_[2]) ^ 2 * 1) := by
  intro h
  have hz : (2 : ℤ) ^ 4 ∣ (-4 : ℤ) :=
    (PolynomialPadicUnique.int_pow_dvd_iff 2 4 (-4)).mpr (by convert h using 1 <;> norm_num)
  norm_num at hz

/-- Reversing the sign of K v also fails at the actual theorem's error precision. -/
theorem reversed_parameter_sign_fails :
    ¬ (2 : ℤ_[2]) ^ 4 ∣ (-8 : ℤ_[2]) - (-(2 : ℤ_[2]) ^ 2 * (1 - 1)) := by
  intro h
  have hz : (2 : ℤ) ^ 4 ∣ (-8 : ℤ) :=
    (PolynomialPadicUnique.int_pow_dvd_iff 2 4 (-8)).mpr (by convert h using 1 <;> norm_num)
  norm_num at hz

/-- The parameter-only nonlinear example is an actual two-variable polynomial. -/
def quadraticParameterSystem : Fin 1 → MvPolynomial (Fin (1 + 1)) ℤ_[2] :=
  fun _ => X (Fin.castAdd 1 0) + X (Fin.castAdd 1 0) ^ 2 + X (Fin.natAdd 1 0)

/-- Its unperturbed root has solved Jacobian 1 and parameter Jacobian 1. -/
theorem quadratic_parameter_base_data :
    eval (0 : Fin (1 + 1) → ℤ_[2]) (quadraticParameterSystem 0) = 0 ∧
    eval (0 : Fin (1 + 1) → ℤ_[2])
      (pderiv (Fin.castAdd 1 0) (quadraticParameterSystem 0)) = 1 ∧
    eval (0 : Fin (1 + 1) → ℤ_[2])
      (pderiv (Fin.natAdd 1 0) (quadraticParameterSystem 0)) = 1 := by
  norm_num [quadraticParameterSystem, pderiv_X, Pi.single_apply, Fin.ext_iff]

/-- With H=0 and parameter shift 2, the first-order error has exactly depth two.
The root exists by the previously checked scalar root-motion theorem. -/
theorem exists_sharp_parameter_only_root :
    ∃ y : Fin 1 → ℤ_[2],
      (∀ i, eval (join y (fun _ : Fin 1 => (2 : ℤ_[2])))
        (quadraticParameterSystem i) = 0) ∧
      (2 : ℤ_[2]) ∣ y 0 ∧
      (2 : ℤ_[2]) ^ 2 ∣ y 0 + 2 ∧
      ¬ (2 : ℤ_[2]) ^ 3 ∣ y 0 + 2 := by
  obtain ⟨b, hroot, heven, hdepth, hsharp⟩ := PolynomialMotionControls.exists_sharp_motion_root
  refine ⟨fun _ => b, ?_, heven, hdepth, hsharp⟩
  intro i
  simpa [quadraticParameterSystem] using hroot

/-- An extra error digit cannot hold uniformly even for parameter-only motion. -/
theorem no_uniform_extra_parameter_error_digit :
    ¬ ∀ y : Fin 1 → ℤ_[2],
      (∀ i, eval (join y (fun _ : Fin 1 => (2 : ℤ_[2])))
        (quadraticParameterSystem i) = 0) →
      (2 : ℤ_[2]) ∣ y 0 → (2 : ℤ_[2]) ^ 3 ∣ y 0 + 2 := by
  intro h
  obtain ⟨y, hy, heven, _, hsharp⟩ := exists_sharp_parameter_only_root
  exact hsharp (h y hy heven)

end Komorebi.PolynomialJointMotionControls
