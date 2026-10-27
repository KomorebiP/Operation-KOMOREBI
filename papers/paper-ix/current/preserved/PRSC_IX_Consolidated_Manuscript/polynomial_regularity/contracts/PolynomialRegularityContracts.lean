module
public import PolynomialRegularityIntegral
public import PolynomialAnalyticEvaluation
public import PolynomialAnalyticImplicit
public import PolynomialAnalyticSelection

@[expose] public section
noncomputable section
set_option autoImplicit false

namespace Komorebi.PolynomialRegularityContracts

open MvPolynomial
open Filter
open scoped Topology
open Komorebi.PolynomialAnalyticEvaluation

variable {𝕜 : Type*} [NontriviallyNormedField 𝕜] [CompleteSpace 𝕜]
variable {n m e k : ℕ}

/-- The analytic input and strict derivative are proved for actual polynomial
evaluation and the actual evaluated partial derivatives. -/
theorem actual_polynomial_evaluation (F : Fin m → MvPolynomial (Fin n) 𝕜)
    (a : Fin n → 𝕜) :
    AnalyticOnNhd 𝕜 (fun x i => eval x (F i)) Set.univ ∧
      HasStrictFDerivAt (fun x i => eval x (F i))
        (matrixCLM (fun i j => eval a (pderiv j (F i)))) a := by
  exact ⟨analyticOnNhd_evalSystem F, hasStrictFDerivAt_evalSystem F a⟩

/-- Only the original polynomial root and actual solved-matrix invertibility
are hypotheses. The conclusion constructs the analytic local root graph and
identifies its strict derivative by the original evaluated partial derivatives. -/
theorem actual_padic_analytic_root_graph (p : ℕ) [Fact p.Prime]
    (F : Fin e → MvPolynomial (Fin (e + k)) ℚ_[p])
    (a : Fin (e + k) → ℚ_[p]) (hF : ∀ i, eval a (F i) = 0)
    (hJ : IsUnit (Matrix.of fun i j => eval a (pderiv (Fin.castAdd k j) (F i)))) :
    ∃ (ψ : (Fin k → ℚ_[p]) → (Fin e → ℚ_[p])) (U : Set (Fin k → ℚ_[p]))
      (V : Set (Fin e → ℚ_[p])),
      IsOpen U ∧ IsOpen V ∧ (fun j => a (Fin.natAdd e j)) ∈ U ∧
      (fun i => a (Fin.castAdd k i)) ∈ V ∧
      ψ (fun j => a (Fin.natAdd e j)) = (fun i => a (Fin.castAdd k i)) ∧
      AnalyticOnNhd ℚ_[p] ψ U ∧ DifferentiableOn ℚ_[p] ψ U ∧
      (∀ t ∈ U, ψ t ∈ V) ∧
      (∀ t ∈ U, ∀ y ∈ V, (∀ i, eval (Fin.append y t) (F i) = 0) ↔ y = ψ t) ∧
      HasStrictFDerivAt ψ
        (matrixCLM (-((Matrix.of fun i j => eval a (pderiv (Fin.castAdd k j) (F i)))⁻¹ *
          (Matrix.of fun i j => eval a (pderiv (Fin.natAdd e j) (F i))))))
        (fun j => a (Fin.natAdd e j)) := by
  obtain ⟨ψ, U, V, hU, hV, ht, hy, hbase, han, hinto, hgraph, hder⟩ :=
    PolynomialAnalyticImplicit.exists_analytic_implicit F a (funext hF) hJ
  refine ⟨ψ, U, V, hU, hV, ht, hy, hbase, han, han.differentiableOn, hinto, ?_, hder⟩
  intro t ht y hy
  exact (show (∀ i, eval (Fin.append y t) (F i) = 0) ↔ evalSystem F (Fin.append y t) = 0
    from ⟨fun h => funext h, fun h i => congrFun h i⟩).trans (hgraph t ht y hy)

/-- A supplied continuous root selection has the same analytic germ and the
same actual implicit derivative. No regularity conclusion is assumed. -/
theorem actual_selection_germ (p : ℕ) [Fact p.Prime]
    (F : Fin e → MvPolynomial (Fin (e + k)) ℚ_[p])
    (a : Fin (e + k) → ℚ_[p])
    (hJ : IsUnit (Matrix.of fun i j => eval a (pderiv (Fin.castAdd k j) (F i))))
    (g : (Fin k → ℚ_[p]) → (Fin e → ℚ_[p]))
    (hg : ContinuousAt g (fun j => a (Fin.natAdd e j)))
    (hg₀ : g (fun j => a (Fin.natAdd e j)) = (fun i => a (Fin.castAdd k i)))
    (hroot : ∀ᶠ t in 𝓝 (fun j => a (Fin.natAdd e j)),
      ∀ i, eval (Fin.append (g t) t) (F i) = 0) :
    AnalyticAt ℚ_[p] g (fun j => a (Fin.natAdd e j)) ∧
      HasStrictFDerivAt g
        (matrixCLM (-((Matrix.of fun i j => eval a (pderiv (Fin.castAdd k j) (F i)))⁻¹ *
          (Matrix.of fun i j => eval a (pderiv (Fin.natAdd e j) (F i))))))
        (fun j => a (Fin.natAdd e j)) := by
  exact PolynomialAnalyticSelection.continuous_selection_regularity F a hJ g hg hg₀
    (hroot.mono fun _ ht => funext ht)

/-- Every continuous exact polynomial root selection with invertible actual
solved matrix on an open set is analytic and has the explicit derivative there. -/
theorem actual_selection_analytic_on_open (p : ℕ) [Fact p.Prime]
    (F : Fin e → MvPolynomial (Fin (e + k)) ℚ_[p])
    (g : (Fin k → ℚ_[p]) → (Fin e → ℚ_[p])) (U : Set (Fin k → ℚ_[p]))
    (hU : IsOpen U) (hg : ContinuousOn g U)
    (hroot : ∀ t ∈ U, ∀ i, eval (Fin.append (g t) t) (F i) = 0)
    (hJ : ∀ t ∈ U, IsUnit (Matrix.of fun i j =>
      eval (Fin.append (g t) t) (pderiv (Fin.castAdd k j) (F i)))) :
    AnalyticOnNhd ℚ_[p] g U ∧
      ∀ t ∈ U, HasStrictFDerivAt g
        (matrixCLM (-((Matrix.of fun i j =>
          eval (Fin.append (g t) t) (pderiv (Fin.castAdd k j) (F i)))⁻¹ *
          (Matrix.of fun i j =>
            eval (Fin.append (g t) t) (pderiv (Fin.natAdd e j) (F i)))))) t := by
  exact PolynomialAnalyticSelection.continuous_selection_analyticOnNhd F g U hU hg
    (fun t ht => funext (hroot t ht)) hJ

/-- Integral coefficients and centers are included in the ambient p-adic field.
The input is the original solved Jacobian and the root graph evaluates the
original integral polynomials directly via the coefficient inclusion. -/
theorem actual_integral_analytic_root_graph (p : ℕ) [Fact p.Prime]
    (F : Fin e → MvPolynomial (Fin (e + k)) ℤ_[p])
    (a : Fin (e + k) → ℤ_[p]) (hF : ∀ i, eval a (F i) = 0)
    (hJ : IsUnit ((algebraMap ℤ_[p] ℚ_[p]).mapMatrix
      (Matrix.of fun i j => eval a (pderiv (Fin.castAdd k j) (F i))))) :
    ∃ (ψ : (Fin k → ℚ_[p]) → (Fin e → ℚ_[p])) (U : Set (Fin k → ℚ_[p]))
      (V : Set (Fin e → ℚ_[p])),
      IsOpen U ∧ IsOpen V ∧ (fun j => (a (Fin.natAdd e j) : ℚ_[p])) ∈ U ∧
      (fun i => (a (Fin.castAdd k i) : ℚ_[p])) ∈ V ∧
      ψ (fun j => (a (Fin.natAdd e j) : ℚ_[p])) =
        (fun i => (a (Fin.castAdd k i) : ℚ_[p])) ∧
      AnalyticOnNhd ℚ_[p] ψ U ∧ DifferentiableOn ℚ_[p] ψ U ∧
      (∀ t ∈ U, ψ t ∈ V) ∧
      (∀ t ∈ U, ∀ y ∈ V,
        (∀ i, eval₂ (algebraMap ℤ_[p] ℚ_[p]) (Fin.append y t) (F i) = 0) ↔ y = ψ t) ∧
      HasStrictFDerivAt ψ
        (matrixCLM (-(((algebraMap ℤ_[p] ℚ_[p]).mapMatrix
          (Matrix.of fun i j => eval a (pderiv (Fin.castAdd k j) (F i))))⁻¹ *
          (Matrix.of fun i j => (eval a (pderiv (Fin.natAdd e j) (F i)) : ℚ_[p])))))
        (fun j => (a (Fin.natAdd e j) : ℚ_[p])) := by
  obtain ⟨ψ, U, V, hU, hV, ht, hy, hbase, han, hinto, hgraph, hder⟩ :=
    PolynomialRegularityIntegral.exists_analytic_integral_implicit p F a hF hJ
  exact ⟨ψ, U, V, hU, hV, ht, hy, hbase, han, han.differentiableOn, hinto, hgraph, hder⟩

end Komorebi.PolynomialRegularityContracts
