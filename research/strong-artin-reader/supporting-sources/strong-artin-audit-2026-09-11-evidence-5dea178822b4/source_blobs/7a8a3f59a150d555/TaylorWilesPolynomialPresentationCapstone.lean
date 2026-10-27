import SelectedAuxiliaryColumnLift
import MinimalAuxiliaryColumnCount

/-!
# Taylor--Wiles auxiliary columns as an explicit nonlinear polynomial presentation

An abstract one-prime interface on the dual obstruction space selects the
cardinality-minimal family of auxiliary columns.  Those residual columns lift
entrywise to honest polynomial variables.  Their coordinate Jacobian is the
Taylor--Wiles augmented map, hence is surjective, and the v0.20 polynomial
Hensel theorem produces an exact nonlinear solution over the finite nilpotent
thickening.
-/

namespace Komorebi.StrongArtin.TaylorWilesPolynomialPresentationCapstone

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.VariableJacobianHensel
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel
open Komorebi.StrongArtin.SurjectiveResidueHomPolynomialHensel
open Komorebi.StrongArtin.PolynomialAuxiliaryAugmentation
open Komorebi.StrongArtin.SelectedAuxiliaryColumnLift
open Komorebi.StrongArtin.AuxiliaryColumnCompletion
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet
open Komorebi.StrongArtin.MinimalAuxiliaryColumnCount

noncomputable section

variable {R k ι κ Aux : Type*}
  [CommRing R] [Field k]
  [Fintype ι] [DecidableEq ι]
  [Fintype κ] [DecidableEq κ]
  [DecidableEq Aux]

/-- The residual coordinate Jacobian of one polynomial presentation. -/
def residualJacobian
    (q : R →+* k) (system : System ι κ R) (x₀ : ι → R) :
    (ι → k) →ₗ[k] (κ → k) :=
  matrixLinear ((jacobianMatrix system x₀).map q)

/--
**Minimal auxiliary polynomial-presentation lifting theorem.**

Starting from an abstract one-prime selection interface on the dual obstruction
of the residual polynomial Jacobian, Lean constructs:

* residual equation-space columns representing every local functional;
* exactly the Jacobian-codimension many admissible auxiliary labels;
* entrywise lifts of the selected columns to the coefficient ring;
* an explicit auxiliary-augmented polynomial system;
* an exact nonlinear solution reducing to the original residual point.
-/
theorem exists_exact_solution_after_minimal_auxiliary_augmentation
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span ({pi} : Set R))
    (system : System ι κ R) (x₀ : ι → R)
    (I : OnePrimeSelectionInterface k
      (obstructionDual (residualJacobian q system x₀)) Aux)
    (hpi : IsNilpotent pi)
    (hx₀ : PowDivisible pi 1 (evalSystem system x₀)) :
    ∃ column : Aux → (κ → k), ∃ Q : Finset Aux,
      ∃ columnR : Q → (κ → R), ∃ x : Sum ι Q → R,
        (∀ a : Aux,
          columnFunctional (residualJacobian q system x₀) column a =
            I.localFunctional a) ∧
        (∀ a ∈ Q, I.admissible a) ∧
        Q.card = Module.finrank k
          ((κ → k) ⧸ LinearMap.range (residualJacobian q system x₀)) ∧
        (∀ a : Q, ∀ j : κ, q (columnR a j) = column a.1 j) ∧
        SameResidual pi (zeroAuxPoint x₀) x ∧
        evalSystem (augmentedSystem system columnR) x = 0 := by
  obtain ⟨column, Q, hcolumn, hgood, hcard, hsurj⟩ :=
    exists_exact_codimension_auxiliary_columns
      (residualJacobian q system x₀) I
  obtain ⟨columnR, hcolumnR⟩ :=
    exists_selected_column_lift q hq column Q
  have hJaug : Function.Surjective
      (matrixLinear
        ((jacobianMatrix (augmentedSystem system columnR)
          (zeroAuxPoint x₀)).map q)) := by
    exact residualJacobian_augmentedSystem_surjective_of_selected_lift
      q system x₀ column Q columnR hcolumnR hsurj
  have hx₀aug : PowDivisible pi 1
      (evalSystem (augmentedSystem system columnR) (zeroAuxPoint x₀)) := by
    rw [eval_augmentedSystem_zeroAuxPoint]
    exact hx₀
  obtain ⟨x, hxres, hxsol⟩ :=
    exists_exact_solution_of_surjective_residue_jacobian
      pi q hq hker (augmentedSystem system columnR) (zeroAuxPoint x₀)
      hJaug hpi hx₀aug
  exact ⟨column, Q, columnR, x, hcolumn, hgood, hcard,
    hcolumnR, hxres, hxsol⟩

end

end Komorebi.StrongArtin.TaylorWilesPolynomialPresentationCapstone

#print axioms Komorebi.StrongArtin.TaylorWilesPolynomialPresentationCapstone.exists_exact_solution_after_minimal_auxiliary_augmentation
