import PresentedAlgebraPoint
import PolynomialRelationAlgebra
import AuxiliaryAugmentedPolynomialSystem
import Mathlib.Algebra.MvPolynomial.Rename

/-!
# The actual auxiliary-augmented coordinate algebra

The linear auxiliary variables of v0.21 define genuine multivariable
polynomial relations and hence a quotient algebra.  Setting all auxiliary
coordinates to zero gives a surjective specialization back to the original
presented algebra.
-/

namespace Komorebi.StrongArtin.AugmentedRelationAlgebra

open Komorebi.StrongArtin.PolynomialExpressionTaylor
open Komorebi.StrongArtin.PolynomialSystemTaylor
open Komorebi.StrongArtin.ExprMvPolynomial
open Komorebi.StrongArtin.PresentedAlgebraPoint
open Komorebi.StrongArtin.PolynomialRelationAlgebra
open Komorebi.StrongArtin.AuxiliaryAugmentedPolynomialSystem

noncomputable section

set_option linter.unusedSectionVars false

variable {R S ι κ Aux : Type*} [CommRing R] [CommRing S] [Algebra R S]
  [DecidableEq Aux]

/-- The polynomial relation obtained by adding the selected linear auxiliary
columns to one base equation. -/
def augmentedRelationPolynomial
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (j : κ) : MvPolynomial (Sum ι Q) R :=
  MvPolynomial.rename Sum.inl (Expr.toMvPolynomial (system j)) +
    ∑ a : Q,
      MvPolynomial.X (Sum.inr a) * MvPolynomial.C (column a.1 j)

/-- Evaluation of an augmented relation in an arbitrary target algebra. -/
theorem aeval_augmentedRelationPolynomial
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z : Sum ι Q → S) (j : κ) :
    MvPolynomial.aeval z (augmentedRelationPolynomial system column Q j) =
      MvPolynomial.aeval (fun i => z (Sum.inl i))
        (Expr.toMvPolynomial (system j)) +
        ∑ a : Q, z (Sum.inr a) * algebraMap R S (column a.1 j) := by
  simp [augmentedRelationPolynomial, MvPolynomial.aeval_rename]
  rfl

/-- Over the coefficient ring itself, relation evaluation is exactly the
v0.21 augmented polynomial evaluator. -/
theorem aeval_augmentedRelationPolynomial_eq_augmentedEval
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z : Sum ι Q → R) (j : κ) :
    MvPolynomial.aeval z (augmentedRelationPolynomial system column Q j) =
      augmentedEval system column Q z j := by
  rw [aeval_augmentedRelationPolynomial]
  rw [Expr.aeval_toMvPolynomial]
  rw [augmentedEval_apply]
  rfl

/-- The quotient algebra defined by the genuine auxiliary-augmented relations. -/
abbrev AugmentedPresentedAlgebra
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux) :=
  RelationAlgebra (augmentedRelationPolynomial system column Q)

/-- The coordinate class in the augmented presentation. -/
def augmentedGenerator
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (s : Sum ι Q) : AugmentedPresentedAlgebra system column Q :=
  PolynomialRelationAlgebra.generator
    (augmentedRelationPolynomial system column Q) s

/-- An exact v0.21 coordinate solution gives an actual algebra point. -/
def augmentedPointAlgHom
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z : Sum ι Q → S)
    (hz : ∀ j, MvPolynomial.aeval z
      (augmentedRelationPolynomial system column Q j) = 0) :
    AugmentedPresentedAlgebra system column Q →ₐ[R] S :=
  PolynomialRelationAlgebra.pointAlgHom
    (augmentedRelationPolynomial system column Q) z hz

@[simp] theorem augmentedPointAlgHom_generator
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (z : Sum ι Q → S)
    (hz : ∀ j, MvPolynomial.aeval z
      (augmentedRelationPolynomial system column Q j) = 0)
    (s : Sum ι Q) :
    augmentedPointAlgHom system column Q z hz
      (augmentedGenerator system column Q s) = z s := by
  exact PolynomialRelationAlgebra.pointAlgHom_generator
    (augmentedRelationPolynomial system column Q) z hz s

/-- Setting auxiliary coordinates to zero and retaining the base quotient
coordinates. -/
def baseVariableImage
    (system : System ι κ R) (Q : Finset Aux) :
    Sum ι Q → PresentedAlgebra system
  | Sum.inl i => PresentedAlgebraPoint.generator system i
  | Sum.inr _ => 0

/-- The augmented relations vanish after all auxiliary variables are set to
zero in the base presented algebra. -/
theorem baseVariableImage_satisfies
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux) :
    ∀ j, MvPolynomial.aeval (baseVariableImage system Q)
      (augmentedRelationPolynomial system column Q j) = 0 := by
  intro j
  rw [aeval_augmentedRelationPolynomial]
  have hbase :
      MvPolynomial.aeval (fun i => baseVariableImage system Q (Sum.inl i))
          (Expr.toMvPolynomial (system j)) =
        Ideal.Quotient.mk (PresentedAlgebraPoint.relationIdeal system)
          (Expr.toMvPolynomial (system j)) := by
    change MvPolynomial.aeval (PresentedAlgebraPoint.generator system)
        (Expr.toMvPolynomial (system j)) = _
    rw [PresentedAlgebraPoint.aeval_generator_eq_mk]
    rfl
  rw [hbase, PresentedAlgebraPoint.relation_mk_eq_zero]
  simp [baseVariableImage]

/-- The Taylor--Wiles augmentation specialization from the enlarged coordinate
algebra to the original one. -/
def baseSpecialization
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux) :
    AugmentedPresentedAlgebra system column Q →ₐ[R] PresentedAlgebra system :=
  PolynomialRelationAlgebra.pointAlgHom
    (augmentedRelationPolynomial system column Q)
    (baseVariableImage system Q)
    (baseVariableImage_satisfies system column Q)

@[simp] theorem baseSpecialization_baseGenerator
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (i : ι) :
    baseSpecialization system column Q
      (augmentedGenerator system column Q (Sum.inl i)) =
        PresentedAlgebraPoint.generator system i := by
  exact PolynomialRelationAlgebra.pointAlgHom_generator
    (augmentedRelationPolynomial system column Q)
    (baseVariableImage system Q)
    (baseVariableImage_satisfies system column Q) (Sum.inl i)

@[simp] theorem baseSpecialization_auxGenerator
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux)
    (a : Q) :
    baseSpecialization system column Q
      (augmentedGenerator system column Q (Sum.inr a)) = 0 := by
  exact PolynomialRelationAlgebra.pointAlgHom_generator
    (augmentedRelationPolynomial system column Q)
    (baseVariableImage system Q)
    (baseVariableImage_satisfies system column Q) (Sum.inr a)

/-- Setting the auxiliary variables to zero is surjective onto the base
presented algebra. -/
theorem baseSpecialization_surjective
    (system : System ι κ R) (column : Aux → (κ → R)) (Q : Finset Aux) :
    Function.Surjective (baseSpecialization system column Q) := by
  intro y
  obtain ⟨p, rfl⟩ := Ideal.Quotient.mk_surjective y
  refine ⟨Ideal.Quotient.mk
      (PolynomialRelationAlgebra.relationFamilyIdeal
        (augmentedRelationPolynomial system column Q))
      (MvPolynomial.rename Sum.inl p), ?_⟩
  change PolynomialRelationAlgebra.pointAlgHom
      (augmentedRelationPolynomial system column Q)
      (baseVariableImage system Q)
      (baseVariableImage_satisfies system column Q)
      (Ideal.Quotient.mk
        (PolynomialRelationAlgebra.relationFamilyIdeal
          (augmentedRelationPolynomial system column Q))
        (MvPolynomial.rename Sum.inl p)) = _
  rw [PolynomialRelationAlgebra.pointAlgHom_mk]
  rw [MvPolynomial.aeval_rename]
  change MvPolynomial.aeval (PresentedAlgebraPoint.generator system) p = _
  rw [PresentedAlgebraPoint.aeval_generator_eq_mk]
  rfl

end

end Komorebi.StrongArtin.AugmentedRelationAlgebra

#print axioms Komorebi.StrongArtin.AugmentedRelationAlgebra.aeval_augmentedRelationPolynomial_eq_augmentedEval
#print axioms Komorebi.StrongArtin.AugmentedRelationAlgebra.baseSpecialization_surjective
