module
public import PolynomialJointSystem
public import PolynomialBlockInverse
public import PolynomialRootMotion

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialJointMotion
open MvPolynomial Matrix
open Komorebi.PolynomialParameterSystem (join solvedPart freePart join_solved)
open Komorebi.PolynomialWeightedInverse Komorebi.PolynomialMotionNormalization
open Komorebi.PolynomialJointSystem Komorebi.PolynomialBlockInverse

variable {e k : ℕ}

/-- The original solved inverse certificate constructs the joint perturbed root.
The exact parameter displacement is built into actual augmented polynomial equations.
The integral first-order estimate retains the original denominator exponent. -/
theorem exists_joint_root_certificate (p s M : ℕ) [Fact p.Prime]
    (hM : 2 * s < M) (F H : Fin e → MvPolynomial (Fin (e + k)) ℤ_[p])
    (a : Fin (e + k) → ℤ_[p]) (v : Fin k → ℤ_[p])
    (A : Matrix (Fin e) (Fin e) ℤ_[p])
    (hAJ : A * solvedJacobian F a =
      (p : ℤ_[p]) ^ s • (1 : Matrix (Fin e) (Fin e) ℤ_[p]))
    (hJA : solvedJacobian F a * A =
      (p : ℤ_[p]) ^ s • (1 : Matrix (Fin e) (Fin e) ℤ_[p]))
    (hFa : ∀ i, eval a (F i) = 0) :
    ∃ b : Fin (e + k) → ℤ_[p],
      (∀ i, eval b (F i) + (p : ℤ_[p]) ^ M * eval b (H i) = 0) ∧
      freePart b = freePart a + (p : ℤ_[p]) ^ M • v ∧
      (∀ i, (p : ℤ_[p]) ^ (M - s) ∣ b i - a i) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i) ∧
      (∀ z : Fin (e + k) → ℤ_[p],
        (∀ i, eval z (F i) + (p : ℤ_[p]) ^ M * eval z (H i) = 0) →
        freePart z = freePart a + (p : ℤ_[p]) ^ M • v →
        (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ z i - a i) → z = b) ∧
      (∀ i, (p : ℤ_[p]) ^ (2 * M - 3 * s) ∣
        solvedPart b i - solvedPart a i + (p : ℤ_[p]) ^ (M - s) *
          A.mulVec ((fun j => eval a (H j)) + (parameterJacobian F a).mulVec v) i) := by
  let B := blockCertificate A (parameterJacobian F a) ((p : ℤ_[p]) ^ s)
  have hJac : jacobian (augmented F (freePart a)) a =
      upperBlock (solvedJacobian F a) (parameterJacobian F a) 1 :=
    jacobian_augmented F (freePart a) a
  obtain ⟨hBA, hAB⟩ := blockCertificate_two_sided A (solvedJacobian F a)
    (parameterJacobian F a) ((p : ℤ_[p]) ^ s) hAJ hJA
  rw [← hJac] at hBA hAB
  have hBase := augmented_root F a hFa
  obtain ⟨b, hb, hdepth, hball, huniq⟩ :=
    PolynomialRootMotion.exists_perturbed_root_certificate p s M hM
      (augmented F (freePart a)) (augmentedPerturbation H v) a B hBA hAB hBase
  have hbParts := (perturb_augmented_root_iff p M F H (freePart a) v b).mp hb
  have hbSum : ∀ i, eval b (augmented F (freePart a) i) +
      (p : ℤ_[p]) ^ M * eval b (augmentedPerturbation H v i) = 0 := by
    intro i
    simpa only [eval_perturbSystem] using hb i
  have herror := PolynomialMotionEstimate.first_order_error_dvd p s M
    (augmented F (freePart a)) (augmentedPerturbation H v) a b B
    hM hBA hBase hbSum hdepth
  refine ⟨b, hbParts.1, hbParts.2, hdepth, hball, ?_, ?_⟩
  · intro z hz ht hzb
    exact huniq z ((perturb_augmented_root_iff p M F H (freePart a) v z).mpr
      ⟨hz, ht⟩) hzb
  · intro i
    have hi := herror (Fin.castAdd k i)
    change (p : ℤ_[p]) ^ (2 * M - 3 * s) ∣
      b (Fin.castAdd k i) - a (Fin.castAdd k i) + (p : ℤ_[p]) ^ (M - s) *
        (blockCertificate A (parameterJacobian F a) ((p : ℤ_[p]) ^ s)).mulVec
          (fun j => eval a (augmentedPerturbation H v j)) (Fin.castAdd k i) at hi
    rw [eval_augmentedPerturbation, blockCertificate_mulVec_join_neg, join_solved] at hi
    exact hi

/-- Simultaneous coefficient and prescribed parameter motion under the original
actual solved Jacobian's rational inverse bound. The perturbed Jacobian is not a hypothesis. -/
theorem exists_joint_root_motion (p s M : ℕ) [Fact p.Prime]
    (hM : 2 * s < M) (F H : Fin e → MvPolynomial (Fin (e + k)) ℤ_[p])
    (a : Fin (e + k) → ℤ_[p]) (v : Fin k → ℤ_[p])
    (hFa : ∀ i, eval a (F i) = 0)
    (hJ : IsUnit (rationalMatrix p (solvedJacobian F a)))
    (hbound : ∃ A : Matrix (Fin e) (Fin e) ℤ_[p],
      rationalMatrix p A = (p : ℚ_[p]) ^ s • (rationalMatrix p (solvedJacobian F a))⁻¹) :
    ∃ b : Fin (e + k) → ℤ_[p],
      (∀ i, eval b (F i) + (p : ℤ_[p]) ^ M * eval b (H i) = 0) ∧
      freePart b = freePart a + (p : ℤ_[p]) ^ M • v ∧
      (∀ i, (p : ℤ_[p]) ^ (M - s) ∣ b i - a i) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i) ∧
      (∀ z : Fin (e + k) → ℤ_[p],
        (∀ i, eval z (F i) + (p : ℤ_[p]) ^ M * eval z (H i) = 0) →
        freePart z = freePart a + (p : ℤ_[p]) ^ M • v →
        (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ z i - a i) → z = b) ∧
      (∃ ε : Fin e → ℤ_[p], (∀ i, (p : ℤ_[p]) ^ (2 * M - 3 * s) ∣ ε i) ∧
        ∀ i, ((solvedPart b i : ℤ_[p]) : ℚ_[p]) - ((solvedPart a i : ℤ_[p]) : ℚ_[p]) =
          -(p : ℚ_[p]) ^ M * ((rationalMatrix p (solvedJacobian F a))⁻¹).mulVec
            (fun j => ((eval a (H j) + (parameterJacobian F a).mulVec v j : ℤ_[p]) : ℚ_[p])) i +
          (ε i : ℚ_[p])) := by
  obtain ⟨A, hA⟩ := hbound
  obtain ⟨hAJ, hJA⟩ := certificate_of_integral_inverse p s (solvedJacobian F a) A hJ hA
  obtain ⟨b, hb, ht, hdepth, hball, huniq, herror⟩ :=
    exists_joint_root_certificate p s M hM F H a v A hAJ hJA hFa
  obtain ⟨ε, hε, hformula⟩ := PolynomialMotionRational.exists_rational_error
    p s M (2 * M - 3 * s) (by omega) (solvedJacobian F a) A hA
    (solvedPart a) (solvedPart b)
    ((fun j => eval a (H j)) + (parameterJacobian F a).mulVec v) herror
  exact ⟨b, hb, ht, hdepth, hball, huniq, ε, hε, hformula⟩

end Komorebi.PolynomialJointMotion
