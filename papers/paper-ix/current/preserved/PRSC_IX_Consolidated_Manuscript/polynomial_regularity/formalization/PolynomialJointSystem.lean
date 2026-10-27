module
public import PolynomialParameterSystem
public import PolynomialMotionNormalization
public import PolynomialBlockInverse

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialJointSystem
open MvPolynomial Matrix
open Komorebi.PolynomialParameterSystem
open Komorebi.PolynomialWeightedInverse
open Komorebi.PolynomialMotionNormalization

variable {e k : ℕ}

/-- The actual partial Jacobian in the solved coordinates, over the coefficient ring. -/
def solvedJacobian {R : Type*} [CommRing R]
    (F : Fin e → MvPolynomial (Fin (e + k)) R) (a : Fin (e + k) → R) :
    Matrix (Fin e) (Fin e) R :=
  fun i j => eval a (pderiv (Fin.castAdd k j) (F i))

/-- The actual partial Jacobian in the prescribed parameter coordinates. -/
def parameterJacobian {R : Type*} [CommRing R]
    (F : Fin e → MvPolynomial (Fin (e + k)) R) (a : Fin (e + k) → R) :
    Matrix (Fin e) (Fin k) R :=
  fun i j => eval a (pderiv (Fin.natAdd e j) (F i))

/-- Append equations fixing the parameters to the given base value. -/
def augmented {R : Type*} [CommRing R]
    (F : Fin e → MvPolynomial (Fin (e + k)) R) (t₀ : Fin k → R) :
    Fin (e + k) → MvPolynomial (Fin (e + k)) R :=
  join F (fun j => X (Fin.natAdd e j) - C (t₀ j))

/-- Append the negative parameter displacement to the coefficient perturbation. -/
def augmentedPerturbation {R : Type*} [CommRing R]
    (H : Fin e → MvPolynomial (Fin (e + k)) R) (v : Fin k → R) :
    Fin (e + k) → MvPolynomial (Fin (e + k)) R :=
  join H (fun j => -C (v j))

@[simp] theorem augmented_solved {R : Type*} [CommRing R]
    (F : Fin e → MvPolynomial (Fin (e + k)) R) (t₀ : Fin k → R) (i : Fin e) :
    augmented F t₀ (Fin.castAdd k i) = F i := by simp [augmented]

@[simp] theorem augmented_free {R : Type*} [CommRing R]
    (F : Fin e → MvPolynomial (Fin (e + k)) R) (t₀ : Fin k → R) (j : Fin k) :
    augmented F t₀ (Fin.natAdd e j) = X (Fin.natAdd e j) - C (t₀ j) := by
  simp [augmented]

@[simp] theorem augmentedPerturbation_solved {R : Type*} [CommRing R]
    (H : Fin e → MvPolynomial (Fin (e + k)) R) (v : Fin k → R) (i : Fin e) :
    augmentedPerturbation H v (Fin.castAdd k i) = H i := by
  simp [augmentedPerturbation]

@[simp] theorem augmentedPerturbation_free {R : Type*} [CommRing R]
    (H : Fin e → MvPolynomial (Fin (e + k)) R) (v : Fin k → R) (j : Fin k) :
    augmentedPerturbation H v (Fin.natAdd e j) = -C (v j) := by
  simp [augmentedPerturbation]

/-- Evaluation of the augmented system retains the original equations and exact parameters. -/
theorem eval_augmented {R : Type*} [CommRing R]
    (F : Fin e → MvPolynomial (Fin (e + k)) R) (t₀ : Fin k → R)
    (z : Fin (e + k) → R) :
    (fun i => eval z (augmented F t₀ i)) =
      join (fun i => eval z (F i)) (freePart z - t₀) := by
  ext i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i <;>
    simp [freePart]

/-- Evaluation of the augmented perturbation has the sign needed for the prescribed shift. -/
theorem eval_augmentedPerturbation {R : Type*} [CommRing R]
    (H : Fin e → MvPolynomial (Fin (e + k)) R) (v : Fin k → R)
    (z : Fin (e + k) → R) :
    (fun i => eval z (augmentedPerturbation H v i)) =
      join (fun i => eval z (H i)) (-v) := by
  ext i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i <;> simp

/-- An original exact root is an exact root of the system fixing its original parameters. -/
theorem augmented_root {R : Type*} [CommRing R]
    (F : Fin e → MvPolynomial (Fin (e + k)) R) (a : Fin (e + k) → R)
    (hF : ∀ i, eval a (F i) = 0) :
    ∀ i, eval a (augmented F (freePart a) i) = 0 := by
  intro i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i <;> simp [hF, freePart]

@[simp] theorem jacobian_augmented_solved_solved {R : Type*} [CommRing R]
    (F : Fin e → MvPolynomial (Fin (e + k)) R) (t₀ : Fin k → R)
    (a : Fin (e + k) → R) (i j : Fin e) :
    jacobian (augmented F t₀) a (Fin.castAdd k i) (Fin.castAdd k j) =
      solvedJacobian F a i j := by simp [jacobian, solvedJacobian]

@[simp] theorem jacobian_augmented_solved_free {R : Type*} [CommRing R]
    (F : Fin e → MvPolynomial (Fin (e + k)) R) (t₀ : Fin k → R)
    (a : Fin (e + k) → R) (i : Fin e) (j : Fin k) :
    jacobian (augmented F t₀) a (Fin.castAdd k i) (Fin.natAdd e j) =
      parameterJacobian F a i j := by simp [jacobian, parameterJacobian]

@[simp] theorem jacobian_augmented_free_solved {R : Type*} [CommRing R]
    (F : Fin e → MvPolynomial (Fin (e + k)) R) (t₀ : Fin k → R)
    (a : Fin (e + k) → R) (i : Fin k) (j : Fin e) :
    jacobian (augmented F t₀) a (Fin.natAdd e i) (Fin.castAdd k j) = 0 := by
  have hne : Fin.natAdd e i ≠ Fin.castAdd k j := by
    intro h
    have hv := congrArg Fin.val h
    simp only [Fin.val_natAdd, Fin.val_castAdd] at hv
    omega
  simp [jacobian, pderiv_X, hne]

@[simp] theorem jacobian_augmented_free_free {R : Type*} [CommRing R]
    (F : Fin e → MvPolynomial (Fin (e + k)) R) (t₀ : Fin k → R)
    (a : Fin (e + k) → R) (i j : Fin k) :
    jacobian (augmented F t₀) a (Fin.natAdd e i) (Fin.natAdd e j) =
      (1 : Matrix (Fin k) (Fin k) R) i j := by
  by_cases hij : i = j <;>
    simp [jacobian, pderiv_X, Matrix.one_apply, hij]

/-- The derivative of the actual augmented polynomial is the triangular block matrix. -/
theorem jacobian_augmented {R : Type*} [CommRing R]
    (F : Fin e → MvPolynomial (Fin (e + k)) R) (t₀ : Fin k → R)
    (a : Fin (e + k) → R) :
    jacobian (augmented F t₀) a =
      Komorebi.PolynomialBlockInverse.upperBlock
        (solvedJacobian F a) (parameterJacobian F a) 1 := by
  ext i j
  refine Fin.addCases (fun i => ?_) (fun i => ?_) i <;>
    refine Fin.addCases (fun j => ?_) (fun j => ?_) j <;> simp

/-- The augmented perturbed root equations are precisely the original perturbed equations
and the requested parameter equality. -/
theorem perturb_augmented_root_iff (p M : ℕ) [Fact (Nat.Prime p)]
    (F H : Fin e → MvPolynomial (Fin (e + k)) ℤ_[p])
    (t₀ v : Fin k → ℤ_[p]) (b : Fin (e + k) → ℤ_[p]) :
    (∀ i, eval b (perturbSystem p M (augmented F t₀) (augmentedPerturbation H v) i) = 0) ↔
      (∀ i, eval b (F i) + (p : ℤ_[p]) ^ M * eval b (H i) = 0) ∧
      freePart b = t₀ + (p : ℤ_[p]) ^ M • v := by
  constructor
  · intro h
    constructor
    · intro i
      simpa only [eval_perturbSystem, augmented_solved, augmentedPerturbation_solved]
        using h (Fin.castAdd k i)
    · ext j
      have hj := h (Fin.natAdd e j)
      simp only [eval_perturbSystem, augmented_free, augmentedPerturbation_free,
        map_sub, eval_X, eval_C, map_neg] at hj
      change b (Fin.natAdd e j) = t₀ j + (p : ℤ_[p]) ^ M * v j
      linear_combination hj
  · rintro ⟨hF, ht⟩ i
    refine Fin.addCases (fun j => ?_) (fun j => ?_) i
    · simpa only [eval_perturbSystem, augmented_solved, augmentedPerturbation_solved]
        using hF j
    · have hj := congrFun ht j
      change b (Fin.natAdd e j) = t₀ j + (p : ℤ_[p]) ^ M * v j at hj
      simp only [eval_perturbSystem, augmented_free, augmentedPerturbation_free,
        map_sub, eval_X, eval_C, map_neg, hj]
      ring

end Komorebi.PolynomialJointSystem
