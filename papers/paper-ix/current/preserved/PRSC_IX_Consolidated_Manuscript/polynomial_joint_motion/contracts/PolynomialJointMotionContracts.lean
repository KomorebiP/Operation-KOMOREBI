module
public import PolynomialJointDeformation

@[expose] public section
noncomputable section
set_option autoImplicit false
open scoped BigOperators

namespace Komorebi.PolynomialJointMotionContracts
open MvPolynomial
variable {e k : ℕ}

/-- The actual solved derivative certificate constructs a root of the original
perturbed equations with exactly the prescribed parameters. The parameter derivative
is explicit in the integral first-order error, and uniqueness is on the full ball. -/
theorem actual_joint_certificate (p s M : ℕ) [Fact p.Prime]
    (hM : 2 * s < M) (F H : Fin e → MvPolynomial (Fin (e + k)) ℤ_[p])
    (a : Fin (e + k) → ℤ_[p]) (v : Fin k → ℤ_[p])
    (A : Matrix (Fin e) (Fin e) ℤ_[p])
    (hAJ : A * (Matrix.of fun i j => eval a (pderiv (Fin.castAdd k j) (F i))) =
      (p : ℤ_[p]) ^ s • (1 : Matrix (Fin e) (Fin e) ℤ_[p]))
    (hJA : (Matrix.of fun i j => eval a (pderiv (Fin.castAdd k j) (F i))) * A =
      (p : ℤ_[p]) ^ s • (1 : Matrix (Fin e) (Fin e) ℤ_[p]))
    (hFa : ∀ i, eval a (F i) = 0) :
    ∃ b : Fin (e + k) → ℤ_[p],
      (∀ i, eval b (F i) + (p : ℤ_[p]) ^ M * eval b (H i) = 0) ∧
      (∀ j, b (Fin.natAdd e j) = a (Fin.natAdd e j) + (p : ℤ_[p]) ^ M * v j) ∧
      (∀ i, (p : ℤ_[p]) ^ (M - s) ∣ b i - a i) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ b i - a i) ∧
      (∀ z : Fin (e + k) → ℤ_[p],
        (∀ i, eval z (F i) + (p : ℤ_[p]) ^ M * eval z (H i) = 0) →
        (∀ j, z (Fin.natAdd e j) = a (Fin.natAdd e j) + (p : ℤ_[p]) ^ M * v j) →
        (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ z i - a i) → z = b) ∧
      (∀ i, (p : ℤ_[p]) ^ (2 * M - 3 * s) ∣
        b (Fin.castAdd k i) - a (Fin.castAdd k i) + (p : ℤ_[p]) ^ (M - s) *
          A.mulVec ((fun j => eval a (H j)) +
            (Matrix.of fun r j => eval a (pderiv (Fin.natAdd e j) (F r))).mulVec v) i) := by
  obtain ⟨b, hb, ht, hdepth, hball, huniq, herror⟩ :=
    PolynomialJointMotion.exists_joint_root_certificate p s M hM F H a v A hAJ hJA hFa
  refine ⟨b, hb, fun j => congrFun ht j, hdepth, hball, ?_, herror⟩
  intro z hz hzt hzb
  exact huniq z hz (funext hzt) hzb

/-- The final statement names only the original polynomial derivatives and the
original solved inverse bound. Parameters are substituted explicitly, and the
first-order formula contains both the coefficient and parameter forcing. -/
theorem actual_joint_rational_motion (p s M : ℕ) [Fact p.Prime]
    (hM : 2 * s < M) (F H : Fin e → MvPolynomial (Fin (e + k)) ℤ_[p])
    (a : Fin (e + k) → ℤ_[p]) (hFa : ∀ i, eval a (F i) = 0)
    (hJ : IsUnit ((algebraMap ℤ_[p] ℚ_[p]).mapMatrix
      (fun i j => eval a (pderiv (Fin.castAdd k j) (F i)))))
    (hbound : ∃ A : Matrix (Fin e) (Fin e) ℤ_[p],
      (algebraMap ℤ_[p] ℚ_[p]).mapMatrix A = (p : ℚ_[p]) ^ s •
        ((algebraMap ℤ_[p] ℚ_[p]).mapMatrix
          (fun i j => eval a (pderiv (Fin.castAdd k j) (F i))))⁻¹)
    (v : Fin k → ℤ_[p]) :
    ∃ y : Fin e → ℤ_[p],
      (∀ i, eval (Fin.append y (fun j => a (Fin.natAdd e j) + (p : ℤ_[p]) ^ M * v j))
          (F i) + (p : ℤ_[p]) ^ M *
        eval (Fin.append y (fun j => a (Fin.natAdd e j) + (p : ℤ_[p]) ^ M * v j)) (H i) = 0) ∧
      (∀ i, (p : ℤ_[p]) ^ (M - s) ∣ y i - a (Fin.castAdd k i)) ∧
      (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ y i - a (Fin.castAdd k i)) ∧
      (∀ z : Fin e → ℤ_[p],
        (∀ i, eval (Fin.append z (fun j => a (Fin.natAdd e j) + (p : ℤ_[p]) ^ M * v j))
            (F i) + (p : ℤ_[p]) ^ M *
          eval (Fin.append z (fun j => a (Fin.natAdd e j) + (p : ℤ_[p]) ^ M * v j)) (H i) = 0) →
        (∀ i, (p : ℤ_[p]) ^ (s + 1) ∣ z i - a (Fin.castAdd k i)) → z = y) ∧
      (∃ ε : Fin e → ℤ_[p], (∀ i, (p : ℤ_[p]) ^ (2 * M - 3 * s) ∣ ε i) ∧
        ∀ i, (y i : ℚ_[p]) - (a (Fin.castAdd k i) : ℚ_[p]) =
          -(p : ℚ_[p]) ^ M *
            (((algebraMap ℤ_[p] ℚ_[p]).mapMatrix
              (fun r j => eval a (pderiv (Fin.castAdd k j) (F r))))⁻¹).mulVec
              (fun j => ((eval a (H j) +
                (Matrix.of fun r t => eval a (pderiv (Fin.natAdd e t) (F r))).mulVec v j : ℤ_[p]) : ℚ_[p])) i +
            (ε i : ℚ_[p])) := by
  have result := PolynomialJointDeformation.exists_joint_deformation
    p s M hM F H a hFa hJ hbound v
  unfold PolynomialWeightedInverse.rationalMatrix
    PolynomialJointSystem.solvedJacobian PolynomialJointSystem.parameterJacobian
    PolynomialParameterSystem.join PolynomialParameterSystem.solvedPart
    PolynomialParameterSystem.freePart at result
  exact result

end Komorebi.PolynomialJointMotionContracts
