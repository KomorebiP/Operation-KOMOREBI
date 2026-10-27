import FormalPowerSeriesJacobianAtOrigin

/-!
# Completed local presentation Hensel capstone

For a finite system of multivariate formal power series centered at the residual
point, the only Jacobian datum required is the matrix of linear coefficients of
the original series.  Surjectivity of that matrix after reduction, together
with nilpotence of the principal maximal-ideal generator, gives an exact solution
of the canonical untruncated formal equations.
-/

namespace Komorebi.StrongArtin.CompletedPresentationHenselCapstone

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel
open Komorebi.StrongArtin.FormalPowerSeriesSystemHensel
open Komorebi.StrongArtin.FormalPowerSeriesJacobianAtOrigin
open Komorebi.StrongArtin.MvPowerSeriesNilpotentSubstitution

noncomputable section

variable {R k ι κ : Type*} [CommRing R] [Field k]
  [Fintype ι] [DecidableEq ι]
  [Fintype κ] [DecidableEq κ]

/-- Vector of constant coefficients of a finite formal presentation. -/
def constantCoefficientVector
    (system : FormalSystem ι κ R) : κ → R :=
  fun j => MvPowerSeries.constantCoeff (system j)

omit [Fintype ι] [DecidableEq ι] [Fintype κ] [DecidableEq κ] in
/-- Canonical formal evaluation at the residual origin is exactly the vector of
constant coefficients. -/
theorem formalEvalSystem_zero
    (system : FormalSystem ι κ R) :
    formalEvalSystem system (0 : ι → R) =
      constantCoefficientVector system := by
  have hsubst : constSubst (0 : ι → R) =
      (0 : ι → MvPowerSeries Empty R) := by
    funext i
    simp [constSubst]
  funext j
  change MvPowerSeries.isEmptyEquiv Empty R
      (MvPowerSeries.subst (constSubst (0 : ι → R)) (system j)) =
    MvPowerSeries.constantCoeff (system j)
  rw [hsubst, MvPowerSeries.subst_zero_eq_C_constantCoeff]
  simp

/--
**Completed-presentation Hensel theorem.** Let a finite formal presentation over
`R` be centered at the residual point.  Assume the kernel of the residue map is
the principal nilpotent ideal `(pi)`, the constant coefficient vector lies in
that ideal, and the reduced matrix of linear coefficients is surjective.  Then
the original untruncated formal power-series equations have an exact solution
whose coordinates lie in `(pi)`.
-/
theorem exists_exact_solution_of_surjective_linearCoefficientMatrix
    (pi : R) (N : ℕ) (hN : 2 ≤ N) (hpiN : pi ^ N = 0)
    (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span ({pi} : Set R))
    (system : FormalSystem ι κ R)
    (hJ : Function.Surjective
      (matrixLinear ((linearCoefficientMatrix system).map q)))
    (hconst : PowDivisible pi 1 (constantCoefficientVector system)) :
    ∃ x : ι → R,
      (∀ i, PowDivisible pi 1 (x i)) ∧
      formalEvalSystem system x = 0 := by
  have hJtrunc : Function.Surjective
      (matrixLinear
        ((jacobianMatrix (compileSystemAt N system) (0 : ι → R)).map q)) := by
    rw [map_jacobianMatrix_compileSystemAt_zero q N hN system]
    exact hJ
  have hbase : PowDivisible pi 1
      (formalEvalSystem system (0 : ι → R)) := by
    rw [formalEvalSystem_zero]
    exact hconst
  exact exists_exact_formal_solution_at_zero
    pi N hpiN q hq hker system hJtrunc hbase

/-- Equivalent centered formulation using an explicit residual zero condition
for the formal equations. -/
theorem exists_exact_solution_of_residual_zero_and_surjective_linear_part
    (pi : R) (N : ℕ) (hN : 2 ≤ N) (hpiN : pi ^ N = 0)
    (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span ({pi} : Set R))
    (system : FormalSystem ι κ R)
    (hJ : Function.Surjective
      (matrixLinear ((linearCoefficientMatrix system).map q)))
    (hzero : q ∘ constantCoefficientVector system = 0) :
    ∃ x : ι → R,
      (∀ i, PowDivisible pi 1 (x i)) ∧
      formalEvalSystem system x = 0 := by
  have hconst : PowDivisible pi 1 (constantCoefficientVector system) := by
    have hcoord : ∀ j, PowDivisible pi 1 (constantCoefficientVector system j) := by
      intro j
      have hz : q (constantCoefficientVector system j) = 0 := by
        have := congrFun hzero j
        simpa using this
      have hmem : constantCoefficientVector system j ∈ RingHom.ker q :=
        RingHom.mem_ker.mpr hz
      rw [hker, Ideal.mem_span_singleton] at hmem
      obtain ⟨c, hc⟩ := hmem
      refine ⟨c, ?_⟩
      simpa [pow_one, smul_eq_mul] using hc.symm
    classical
    choose witness hwitness using hcoord
    refine ⟨fun j => witness j, ?_⟩
    funext j
    simpa using hwitness j
  exact exists_exact_solution_of_surjective_linearCoefficientMatrix
    pi N hN hpiN q hq hker system hJ hconst

end

end Komorebi.StrongArtin.CompletedPresentationHenselCapstone

#print axioms Komorebi.StrongArtin.CompletedPresentationHenselCapstone.exists_exact_solution_of_surjective_linearCoefficientMatrix
#print axioms Komorebi.StrongArtin.CompletedPresentationHenselCapstone.exists_exact_solution_of_residual_zero_and_surjective_linear_part
