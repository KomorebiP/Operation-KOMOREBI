module
public import PolynomialAnalyticImplicit

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialRegularityIntegral

open MvPolynomial Matrix
open Komorebi.PolynomialJointSystem
open Komorebi.PolynomialWeightedInverse
open Komorebi.PolynomialParameterSystem
open Komorebi.PolynomialAnalyticEvaluation

variable {e k : ℕ}

/-- Include the actual integral coefficients in the p-adic field. -/
def rationalSystem (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (e + k)) ℤ_[p]) :
    Fin e → MvPolynomial (Fin (e + k)) ℚ_[p] :=
  fun i => (F i).map (algebraMap ℤ_[p] ℚ_[p])

/-- Include every coordinate of an integral point in the p-adic field. -/
def rationalPoint (p : ℕ) [Fact (Nat.Prime p)] {d : ℕ}
    (a : Fin d → ℤ_[p]) : Fin d → ℚ_[p] := fun i => (a i : ℚ_[p])

/-- Evaluation commutes with the actual coefficient and coordinate inclusions. -/
@[simp] theorem eval_rationalSystem (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (e + k)) ℤ_[p])
    (a : Fin (e + k) → ℤ_[p]) (i : Fin e) :
    eval (rationalPoint p a) (rationalSystem p F i) = (eval a (F i) : ℚ_[p]) := by
  exact (MvPolynomial.map_eval (algebraMap ℤ_[p] ℚ_[p]) a (F i)).symm

/-- Partial differentiation followed by evaluation commutes with coefficient inclusion. -/
@[simp] theorem eval_pderiv_rationalSystem (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (e + k)) ℤ_[p])
    (a : Fin (e + k) → ℤ_[p]) (i : Fin e) (j : Fin (e + k)) :
    eval (rationalPoint p a) (pderiv j (rationalSystem p F i)) =
      (eval a (pderiv j (F i)) : ℚ_[p]) := by
  rw [rationalSystem, pderiv_map]
  exact (MvPolynomial.map_eval (algebraMap ℤ_[p] ℚ_[p]) a (pderiv j (F i))).symm

/-- The rational solved Jacobian is the inclusion of the actual integral solved Jacobian. -/
@[simp] theorem solvedJacobian_rationalSystem (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (e + k)) ℤ_[p])
    (a : Fin (e + k) → ℤ_[p]) :
    Komorebi.PolynomialJointSystem.solvedJacobian (rationalSystem p F) (rationalPoint p a) =
      rationalMatrix p (Komorebi.PolynomialJointSystem.solvedJacobian F a) := by
  ext i j
  exact eval_pderiv_rationalSystem p F a i (Fin.castAdd k j)

/-- The rectangular parameter Jacobian is also the entrywise inclusion of the actual one. -/
@[simp] theorem parameterJacobian_rationalSystem (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (e + k)) ℤ_[p])
    (a : Fin (e + k) → ℤ_[p]) :
    parameterJacobian (rationalSystem p F) (rationalPoint p a) =
      fun i j => algebraMap ℤ_[p] ℚ_[p] (parameterJacobian F a i j) := by
  ext i j
  exact eval_pderiv_rationalSystem p F a i (Fin.natAdd e j)

/-- Every integral exact root remains an exact root after inclusion in the field. -/
theorem rationalSystem_root (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (e + k)) ℤ_[p])
    (a : Fin (e + k) → ℤ_[p]) (hF : ∀ i, eval a (F i) = 0) :
    ∀ i, eval (rationalPoint p a) (rationalSystem p F i) = 0 := by
  intro i
  simp [hF]

@[simp] theorem rationalPoint_join (p : ℕ) [Fact (Nat.Prime p)]
    (y : Fin e → ℤ_[p]) (t : Fin k → ℤ_[p]) :
    rationalPoint p (join y t) = join (rationalPoint p y) (rationalPoint p t) := by
  ext i
  refine Fin.addCases (fun j => ?_) (fun j => ?_) i <;> simp [rationalPoint]

@[simp] theorem rationalPoint_solvedPart (p : ℕ) [Fact (Nat.Prime p)]
    (a : Fin (e + k) → ℤ_[p]) :
    solvedPart (rationalPoint p a) = rationalPoint p (solvedPart a) := rfl

@[simp] theorem rationalPoint_freePart (p : ℕ) [Fact (Nat.Prime p)]
    (a : Fin (e + k) → ℤ_[p]) :
    freePart (rationalPoint p a) = rationalPoint p (freePart a) := rfl

/-- Integral coefficients and centers have an analytic implicit solution in the ambient
p-adic field. The only nonsingularity hypothesis is on their actual solved Jacobian.
The root graph is stated by evaluating the original integral polynomials in the field. -/
theorem exists_analytic_integral_implicit (p : ℕ) [Fact (Nat.Prime p)]
    (F : Fin e → MvPolynomial (Fin (e + k)) ℤ_[p])
    (a : Fin (e + k) → ℤ_[p]) (hF : ∀ i, eval a (F i) = 0)
    (hJ : IsUnit (rationalMatrix p (Komorebi.PolynomialJointSystem.solvedJacobian F a))) :
    ∃ (ψ : (Fin k → ℚ_[p]) → (Fin e → ℚ_[p])) (U : Set (Fin k → ℚ_[p]))
      (V : Set (Fin e → ℚ_[p])),
      IsOpen U ∧ IsOpen V ∧ rationalPoint p (freePart a) ∈ U ∧
      rationalPoint p (solvedPart a) ∈ V ∧
      ψ (rationalPoint p (freePart a)) = rationalPoint p (solvedPart a) ∧
      AnalyticOnNhd ℚ_[p] ψ U ∧ (∀ t ∈ U, ψ t ∈ V) ∧
      (∀ t ∈ U, ∀ y ∈ V,
        (∀ i, eval₂ (algebraMap ℤ_[p] ℚ_[p]) (join y t) (F i) = 0) ↔ y = ψ t) ∧
      HasStrictFDerivAt ψ
        (matrixCLM (-((rationalMatrix p
          (Komorebi.PolynomialJointSystem.solvedJacobian F a))⁻¹ *
          Matrix.of (fun i j => algebraMap ℤ_[p] ℚ_[p] (parameterJacobian F a i j)))))
        (rationalPoint p (freePart a)) := by
  have hroot : evalSystem (rationalSystem p F) (rationalPoint p a) = 0 := by
    ext i
    exact rationalSystem_root p F a hF i
  have hunit : IsUnit (Komorebi.PolynomialJointSystem.solvedJacobian
      (rationalSystem p F) (rationalPoint p a)) := by
    simpa only [solvedJacobian_rationalSystem] using hJ
  obtain ⟨ψ, U, V, hU, hV, ht, hy, hψa, hψan, hψV, hgraph, hder⟩ :=
    Komorebi.PolynomialAnalyticImplicit.exists_analytic_implicit
      (rationalSystem p F) (rationalPoint p a) hroot hunit
  refine ⟨ψ, U, V, hU, hV, ht, hy, hψa, hψan, hψV, ?_, ?_⟩
  · intro t ht' y hy'
    have h := hgraph t ht' y hy'
    simpa only [evalSystem, rationalSystem, MvPolynomial.eval_map,
      funext_iff, Pi.zero_apply] using h
  · have hK : parameterJacobian (rationalSystem p F) (rationalPoint p a) =
        Matrix.of (fun i j => algebraMap ℤ_[p] ℚ_[p] (parameterJacobian F a i j)) := by
      ext i j
      exact eval_pderiv_rationalSystem p F a i (Fin.natAdd e j)
    rw [solvedJacobian_rationalSystem, hK, rationalPoint_freePart] at hder
    exact hder

end Komorebi.PolynomialRegularityIntegral
