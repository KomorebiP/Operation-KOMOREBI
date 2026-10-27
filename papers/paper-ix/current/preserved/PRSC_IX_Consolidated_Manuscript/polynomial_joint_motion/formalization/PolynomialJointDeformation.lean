module
public import PolynomialJointMotion

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialJointDeformation
open MvPolynomial Matrix
open Komorebi.PolynomialParameterSystem (join solvedPart freePart)
open Komorebi.PolynomialWeightedInverse
open Komorebi.PolynomialJointSystem (solvedJacobian parameterJacobian)

variable {e k : ℕ}

/-- A solved-coordinate point in the weighted uniqueness ball, combined with
its prescribed parameter displacement, lies in the full augmented ball. -/
theorem join_deformed_ball (p s M : ℕ) [Fact (Nat.Prime p)] (hM : 2 * s < M)
    (a : Fin (e+k) → ℤ_[p]) (v : Fin k → ℤ_[p]) (y : Fin e → ℤ_[p])
    (hy : ∀ i, (p : ℤ_[p])^(s+1) ∣ y i - solvedPart a i) :
    ∀ i, (p : ℤ_[p])^(s+1) ∣
      join y (freePart a + (p : ℤ_[p])^M • v) i - a i := by
  intro i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i
  · simpa only [PolynomialParameterSystem.join_solved, solvedPart] using hy j
  · simp only [PolynomialParameterSystem.join_free, Pi.add_apply, Pi.smul_apply,
      smul_eq_mul, freePart, add_sub_cancel_left]
    exact dvd_mul_of_dvd_left (pow_dvd_pow (p : ℤ_[p]) (by omega)) (v j)

/-- The joint deformation theorem in the original solved-coordinate variables.
The only inverse assumption concerns the original actual solved Jacobian. -/
theorem exists_joint_deformation (p s M : ℕ) [Fact (Nat.Prime p)]
    (hM : 2 * s < M) (F H : Fin e → MvPolynomial (Fin (e+k)) ℤ_[p])
    (a : Fin (e+k) → ℤ_[p]) (hFa : ∀ i, eval a (F i) = 0)
    (hJ : IsUnit (rationalMatrix p (solvedJacobian F a)))
    (hbound : ∃ A : Matrix (Fin e) (Fin e) ℤ_[p],
      rationalMatrix p A = (p : ℚ_[p])^s • (rationalMatrix p (solvedJacobian F a))⁻¹)
    (v : Fin k → ℤ_[p]) :
    ∃ y : Fin e → ℤ_[p],
      (∀ i, eval (join y (freePart a + (p : ℤ_[p])^M • v)) (F i) +
        (p : ℤ_[p])^M * eval (join y (freePart a + (p : ℤ_[p])^M • v)) (H i) = 0) ∧
      (∀ i, (p : ℤ_[p])^(M-s) ∣ y i - solvedPart a i) ∧
      (∀ i, (p : ℤ_[p])^(s+1) ∣ y i - solvedPart a i) ∧
      (∀ z : Fin e → ℤ_[p],
        (∀ i, eval (join z (freePart a + (p : ℤ_[p])^M • v)) (F i) +
          (p : ℤ_[p])^M * eval (join z (freePart a + (p : ℤ_[p])^M • v)) (H i) = 0) →
        (∀ i, (p : ℤ_[p])^(s+1) ∣ z i - solvedPart a i) → z = y) ∧
      (∃ ε : Fin e → ℤ_[p], (∀ i, (p : ℤ_[p])^(2*M-3*s) ∣ ε i) ∧
        ∀ i, (y i : ℚ_[p]) - (a (Fin.castAdd k i) : ℚ_[p]) =
          -(p : ℚ_[p])^M * ((rationalMatrix p (solvedJacobian F a))⁻¹).mulVec
            (fun j => ((eval a (H j) + (parameterJacobian F a).mulVec v j : ℤ_[p]) : ℚ_[p])) i +
          (ε i : ℚ_[p])) := by
  obtain ⟨b, hb, hbparams, hdepth, hball, huniq, herror⟩ :=
    PolynomialJointMotion.exists_joint_root_motion p s M hM F H a v hFa hJ hbound
  have hjoin : join (solvedPart b) (freePart a + (p : ℤ_[p])^M • v) = b := by
    rw [← hbparams, PolynomialParameterSystem.join_parts]
  refine ⟨solvedPart b, ?_, ?_, ?_, ?_, herror⟩
  · simpa only [hjoin] using hb
  · exact fun i => hdepth (Fin.castAdd k i)
  · exact fun i => hball (Fin.castAdd k i)
  · intro z hz hzb
    have hfull := huniq (join z (freePart a + (p : ℤ_[p])^M • v)) hz
      (PolynomialParameterSystem.freePart_join _ _)
      (join_deformed_ball p s M hM a v z hzb)
    simpa only [PolynomialParameterSystem.solvedPart_join] using
      congrArg (fun w : Fin (e+k) → ℤ_[p] => solvedPart w) hfull

/-- Unique existence holds throughout the original solved-coordinate ball. -/
theorem exists_unique_joint_deformation (p s M : ℕ) [Fact (Nat.Prime p)]
    (hM : 2 * s < M) (F H : Fin e → MvPolynomial (Fin (e+k)) ℤ_[p])
    (a : Fin (e+k) → ℤ_[p]) (hFa : ∀ i, eval a (F i) = 0)
    (hJ : IsUnit (rationalMatrix p (solvedJacobian F a)))
    (hbound : ∃ A : Matrix (Fin e) (Fin e) ℤ_[p],
      rationalMatrix p A = (p : ℚ_[p])^s • (rationalMatrix p (solvedJacobian F a))⁻¹)
    (v : Fin k → ℤ_[p]) :
    ∃! y : Fin e → ℤ_[p],
      (∀ i, eval (join y (freePart a + (p : ℤ_[p])^M • v)) (F i) +
        (p : ℤ_[p])^M * eval (join y (freePart a + (p : ℤ_[p])^M • v)) (H i) = 0) ∧
      (∀ i, (p : ℤ_[p])^(s+1) ∣ y i - solvedPart a i) := by
  obtain ⟨y, hy, _, hball, huniq, _⟩ :=
    exists_joint_deformation p s M hM F H a hFa hJ hbound v
  exact ⟨y, ⟨hy, hball⟩, fun z hz => huniq z hz.1 hz.2⟩

end Komorebi.PolynomialJointDeformation
