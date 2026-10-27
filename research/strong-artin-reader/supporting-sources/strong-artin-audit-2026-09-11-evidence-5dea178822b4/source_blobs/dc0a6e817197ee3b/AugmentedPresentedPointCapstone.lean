import AugmentedRelationAlgebra
import ResidualAugmentedJacobian

/-!
# Taylor--Wiles selection produces an actual point of the augmented algebra

The v0.21 nonlinear coordinate solution is promoted to a genuine algebra
homomorphism out of the auxiliary-augmented finite presentation.  Its values
on every universal coordinate remain in the prescribed residual fibre.
-/

namespace Komorebi.StrongArtin.AugmentedPresentedPointCapstone

open Komorebi.StrongArtin.PowerDivisibility
open Komorebi.StrongArtin.VariableJacobianHensel
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.FiniteCoordinatePolynomialHensel
open Komorebi.StrongArtin.AuxiliaryColumnCompletion
open Komorebi.StrongArtin.ObstructionFunctionalColumnRepresentation
open Komorebi.StrongArtin.AuxiliaryAugmentedPolynomialSystem
open Komorebi.StrongArtin.ResidualAugmentedJacobian
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet
open Komorebi.StrongArtin.AugmentedRelationAlgebra

noncomputable section

set_option linter.unusedSectionVars false

variable {R k ι κ Aux : Type*} [CommRing R] [Field k]
  [Fintype ι] [DecidableEq ι]
  [Fintype κ] [DecidableEq κ]
  [DecidableEq Aux]

/-- An exact zero of the v0.21 augmented evaluator satisfies every defining
relation of the corresponding augmented coordinate algebra. -/
theorem augmentedRelations_vanish_of_augmentedEval_eq_zero
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z : Sum ι Q → R)
    (hz : augmentedEval system column Q z = 0) :
    ∀ j, MvPolynomial.aeval z
      (augmentedRelationPolynomial system column Q j) = 0 := by
  intro j
  rw [aeval_augmentedRelationPolynomial_eq_augmentedEval]
  exact congrFun hz j

/-- A coordinate-level exact augmented solution determines an actual
coefficient-ring point of the presented algebra. -/
def pointOfAugmentedEvalZero
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z : Sum ι Q → R)
    (hz : augmentedEval system column Q z = 0) :
    AugmentedPresentedAlgebra system column Q →ₐ[R] R :=
  augmentedPointAlgHom system column Q z
    (augmentedRelations_vanish_of_augmentedEval_eq_zero system column Q z hz)

@[simp] theorem pointOfAugmentedEvalZero_generator
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z : Sum ι Q → R)
    (hz : augmentedEval system column Q z = 0)
    (s : Sum ι Q) :
    pointOfAugmentedEvalZero system column Q z hz
      (augmentedGenerator system column Q s) = z s := by
  exact augmentedPointAlgHom_generator system column Q z
    (augmentedRelations_vanish_of_augmentedEval_eq_zero system column Q z hz) s

/-- Coordinatewise form of residual-fibre agreement. -/
theorem coordinate_powDivisible_of_sameResidual
    (pi : R) (Q : Finset Aux) (x₀ : ι → R) (z : Sum ι Q → R)
    (hz : SameResidual pi (augmentedBasePoint Q x₀) z) :
    ∀ s, PowDivisible pi 1 (z s - augmentedBasePoint Q x₀ s) := by
  unfold SameResidual at hz
  obtain ⟨w, hw⟩ := hz
  intro s
  refine ⟨w s, ?_⟩
  have hs := congrFun hw s
  simpa [Pi.smul_apply, Pi.sub_apply] using hs

/--
**One-prime interface to an actual finite-presentation point.**
The v0.21 Taylor--Wiles selection and nonlinear Hensel theorem produce an
actual algebra homomorphism from the augmented presented algebra to the
coefficient ring.  The selected labels are admissible and cardinality-minimal,
and every universal coordinate specializes in the original residual fibre.
-/
theorem exists_augmented_presentedAlgebra_point_from_onePrimeSelectionInterface
    (pi : R) (q : R →+* k) (hq : Function.Surjective q)
    (hker : RingHom.ker q = Ideal.span ({pi} : Set R))
    (system : System ι κ R) (x₀ : ι → R)
    (I : OnePrimeSelectionInterface k
      (obstructionDual (residualBaseJacobian q system x₀)) Aux)
    (hpi : IsNilpotent pi)
    (hx₀ : PowDivisible pi 1 (evalSystem system x₀)) :
    ∃ columnBar : Aux → (κ → k),
      ∃ column : Aux → (κ → R),
      ∃ Q : Finset Aux,
        (∀ a, columnFunctional
            (residualBaseJacobian q system x₀) columnBar a =
              I.localFunctional a) ∧
        (∀ a j, q (column a j) = columnBar a j) ∧
        (∀ a ∈ Q, I.admissible a) ∧
        Q.card = Module.finrank k
          (obstructionDual (residualBaseJacobian q system x₀)) ∧
        ∃ φ : AugmentedPresentedAlgebra system column Q →ₐ[R] R,
          ∀ s, PowDivisible pi 1
            (φ (augmentedGenerator system column Q s) -
              augmentedBasePoint Q x₀ s) := by
  obtain ⟨columnBar, column, Q, hfunctional, hcolumn, hgood, hcard,
      z, hzres, hz⟩ :=
    exists_exact_solution_from_onePrimeSelectionInterface
      pi q hq hker system x₀ I hpi hx₀
  let φ := pointOfAugmentedEvalZero system column Q z hz
  refine ⟨columnBar, column, Q, hfunctional, hcolumn, hgood, hcard,
    φ, ?_⟩
  intro s
  rw [show φ (augmentedGenerator system column Q s) = z s by
    exact pointOfAugmentedEvalZero_generator system column Q z hz s]
  exact coordinate_powDivisible_of_sameResidual pi Q x₀ z hzres s

end

end Komorebi.StrongArtin.AugmentedPresentedPointCapstone

#print axioms Komorebi.StrongArtin.AugmentedPresentedPointCapstone.pointOfAugmentedEvalZero
#print axioms Komorebi.StrongArtin.AugmentedPresentedPointCapstone.exists_augmented_presentedAlgebra_point_from_onePrimeSelectionInterface
