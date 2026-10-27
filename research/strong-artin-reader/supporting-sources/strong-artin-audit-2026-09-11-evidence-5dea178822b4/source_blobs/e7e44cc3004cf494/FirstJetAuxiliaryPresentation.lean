import TaylorWilesPolynomialPresentationCapstone

/-!
# First-jet robustness of the auxiliary polynomial presentation

The canonical auxiliary augmentation uses variables linearly.  An arithmetic
presentation need not have exactly those higher-order equations: it is enough
that its residual Jacobian at the base point agree with the canonical
augmentation.  The v0.20 Hensel theorem then applies directly to the actual
presentation.
-/

namespace Komorebi.StrongArtin.FirstJetAuxiliaryPresentation

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
open Komorebi.StrongArtin.TaylorWilesPolynomialPresentationCapstone

noncomputable section

variable {R k ι κ Aux : Type*}
  [CommRing R] [Field k]
  [Fintype ι] [DecidableEq ι]
  [Fintype κ] [DecidableEq κ]
  [DecidableEq Aux]

/-- Equality of residual coordinate Jacobians at one base point. -/
def SameResidualFirstJet
    {β : Type*} [Fintype β] [DecidableEq β]
    (q : R →+* k) (system₁ system₂ : System β κ R) (x₀ : β → R) : Prop :=
  (jacobianMatrix system₁ x₀).map q =
    (jacobianMatrix system₂ x₀).map q

/-- Surjectivity of a residual coordinate Jacobian transfers across equality of
residual first jets. -/
theorem residualJacobian_surjective_of_same_firstJet
    {β : Type*} [Fintype β] [DecidableEq β]
    (q : R →+* k) (system₁ system₂ : System β κ R) (x₀ : β → R)
    (hjet : SameResidualFirstJet q system₁ system₂ x₀)
    (hsurj : Function.Surjective
      (matrixLinear ((jacobianMatrix system₁ x₀).map q))) :
    Function.Surjective
      (matrixLinear ((jacobianMatrix system₂ x₀).map q)) := by
  rw [SameResidualFirstJet] at hjet
  rw [← hjet]
  exact hsurj

/-- An actual polynomial system with the same residual first jet as a model
system inherits the model's nonlinear Hensel solvability. -/
theorem exists_exact_solution_of_same_residual_firstJet
    {β : Type*} [Fintype β] [DecidableEq β]
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span ({pi} : Set R))
    (model actual : System β κ R) (x₀ : β → R)
    (hmodel : Function.Surjective
      (matrixLinear ((jacobianMatrix model x₀).map q)))
    (hjet : SameResidualFirstJet q model actual x₀)
    (hpi : IsNilpotent pi)
    (hbase : PowDivisible pi 1 (evalSystem actual x₀)) :
    ∃ x : β → R, SameResidual pi x₀ x ∧ evalSystem actual x = 0 := by
  have hactual := residualJacobian_surjective_of_same_firstJet
    q model actual x₀ hjet hmodel
  exact exists_exact_solution_of_surjective_residue_jacobian
    pi q hq hker actual x₀ hactual hpi hbase

/--
**First-jet robust Taylor--Wiles polynomial presentation.**  The minimal
auxiliary family selected from the dual-obstruction one-prime interface has the
following universal property: every finite polynomial presentation with the
same residual first jet as the canonical auxiliary augmentation lifts exactly,
provided its base point is a residual solution.
-/
theorem exists_minimal_auxiliary_family_with_firstJet_lifting_property
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span ({pi} : Set R))
    (system : System ι κ R) (x₀ : ι → R)
    (I : OnePrimeSelectionInterface k
      (obstructionDual (residualJacobian q system x₀)) Aux)
    (hpi : IsNilpotent pi) :
    ∃ column : Aux → (κ → k), ∃ Q : Finset Aux,
      ∃ columnR : Q → (κ → R),
        (∀ a : Aux,
          columnFunctional (residualJacobian q system x₀) column a =
            I.localFunctional a) ∧
        (∀ a ∈ Q, I.admissible a) ∧
        Q.card = Module.finrank k
          ((κ → k) ⧸ LinearMap.range (residualJacobian q system x₀)) ∧
        (∀ a : Q, ∀ j : κ, q (columnR a j) = column a.1 j) ∧
        ∀ actual : System (Sum ι Q) κ R,
          SameResidualFirstJet q
            (augmentedSystem system columnR) actual (zeroAuxPoint x₀) →
          PowDivisible pi 1 (evalSystem actual (zeroAuxPoint x₀)) →
          ∃ x : Sum ι Q → R,
            SameResidual pi (zeroAuxPoint x₀) x ∧
            evalSystem actual x = 0 := by
  obtain ⟨column, Q, hcolumn, hgood, hcard, hsurj⟩ :=
    exists_exact_codimension_auxiliary_columns
      (residualJacobian q system x₀) I
  obtain ⟨columnR, hcolumnR⟩ :=
    exists_selected_column_lift q hq column Q
  have hmodel : Function.Surjective
      (matrixLinear
        ((jacobianMatrix (augmentedSystem system columnR)
          (zeroAuxPoint x₀)).map q)) := by
    exact residualJacobian_augmentedSystem_surjective_of_selected_lift
      q system x₀ column Q columnR hcolumnR hsurj
  refine ⟨column, Q, columnR, hcolumn, hgood, hcard, hcolumnR, ?_⟩
  intro actual hjet hbase
  exact exists_exact_solution_of_same_residual_firstJet
    pi q hq hker (augmentedSystem system columnR) actual
      (zeroAuxPoint x₀) hmodel hjet hpi hbase

end

end Komorebi.StrongArtin.FirstJetAuxiliaryPresentation

#print axioms Komorebi.StrongArtin.FirstJetAuxiliaryPresentation.exists_exact_solution_of_same_residual_firstJet
#print axioms Komorebi.StrongArtin.FirstJetAuxiliaryPresentation.exists_minimal_auxiliary_family_with_firstJet_lifting_property
