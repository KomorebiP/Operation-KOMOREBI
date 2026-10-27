import RelativeTaylorWilesJacobianCapstone
import FiniteDepthLinearizedLiftSystem
import Mathlib.LinearAlgebra.Dual.Lemmas

/-!
# Every dual-obstruction functional is represented by a Jacobian column

In finite dimension, evaluation identifies the equation space `W` with its
double dual.  Restricting a double-dual functional to the subspace
`obstructionDual J` is surjective.  Consequently every scalar functional on the
dual obstruction space has a representing column `w : W`, unique modulo the
primal Jacobian image.

This removes an abstract linear-algebra existence gap.  It does not prove that
the representing column is supplied by an arithmetic local deformation ring.
-/

namespace Komorebi.StrongArtin.ObstructionFunctionalColumnRepresentation

open Komorebi.StrongArtin.AuxiliaryColumnCompletion
open Komorebi.StrongArtin.RelativeTaylorWilesFiniteSet
open Komorebi.StrongArtin.RelativeTaylorWilesJacobianCapstone
open Komorebi.StrongArtin.FiniteDepthLinearizedLiftSystem

noncomputable section

variable {k U W Aux : Type*} [Field k]
  [AddCommGroup U] [Module k U]
  [AddCommGroup W] [Module k W]

/-- Evaluation of an equation-space vector on the dual obstruction subspace. -/
def evaluationColumnMap (J : U →ₗ[k] W) :
    W →ₗ[k] Module.Dual k (obstructionDual J) :=
  (obstructionDual J).dualRestrict.comp (Module.Dual.eval k W)

@[simp]
theorem evaluationColumnMap_apply
    (J : U →ₗ[k] W) (w : W) (φ : obstructionDual J) :
    evaluationColumnMap J w φ = φ.1 w := rfl

/-- In finite dimension every functional on the dual obstruction space is
represented by evaluation at an equation-space vector. -/
theorem evaluationColumnMap_surjective
    [FiniteDimensional k W] (J : U →ₗ[k] W) :
    Function.Surjective (evaluationColumnMap J) := by
  intro ℓ
  obtain ⟨Φ, hΦ⟩ :=
    (Subspace.dualRestrict_surjective
      (W := obstructionDual J)) ℓ
  obtain ⟨w, hw⟩ := (Module.evalEquiv k W).surjective Φ
  refine ⟨w, ?_⟩
  change (obstructionDual J).dualRestrict
      (Module.Dual.eval k W w) = ℓ
  have hw' : Module.Dual.eval k W w = Φ := by
    simpa only [Module.evalEquiv_apply] using hw
  rw [hw']
  exact hΦ

/-- Every one-prime scalar local functional has a representing equation-space
column. -/
theorem exists_representing_column
    [FiniteDimensional k W]
    (J : U →ₗ[k] W)
    (ℓ : Module.Dual k (obstructionDual J)) :
    ∃ w : W, ∀ φ : obstructionDual J, ℓ φ = φ.1 w := by
  obtain ⟨w, hw⟩ := evaluationColumnMap_surjective J ℓ
  refine ⟨w, ?_⟩
  intro φ
  have h := congrArg
    (fun f : Module.Dual k (obstructionDual J) => f φ) hw
  simpa [evaluationColumnMap_apply] using h.symm

/-- A whole family of scalar local functionals can be represented
simultaneously by a family of columns. -/
theorem exists_representing_columns
    [FiniteDimensional k W]
    (J : U →ₗ[k] W)
    (localFunctional : Aux → Module.Dual k (obstructionDual J)) :
    ∃ column : Aux → W,
      ∀ a : Aux, columnFunctional J column a = localFunctional a := by
  choose column hcolumn using fun a =>
    evaluationColumnMap_surjective J (localFunctional a)
  refine ⟨column, ?_⟩
  intro a
  apply LinearMap.ext
  intro φ
  have h := congrArg
    (fun f : Module.Dual k (obstructionDual J) => f φ) (hcolumn a)
  simpa [evaluationColumnMap_apply, columnFunctional_apply] using h

/--
**Functional-to-column Taylor--Wiles capstone.** Any abstract v0.15 one-prime
selection interface on the dual obstruction space admits a representing family
of equation-space columns.  Exactly the dual-obstruction dimension many
admissible labels can then be selected so that the augmented Jacobian is
surjective.
-/
theorem exists_representing_columns_and_surjective_auxiliary_set
    [DecidableEq Aux] [FiniteDimensional k W]
    (J : U →ₗ[k] W)
    (I : OnePrimeSelectionInterface k (obstructionDual J) Aux) :
    ∃ column : Aux → W, ∃ Q : Finset Aux,
      (∀ a : Aux, columnFunctional J column a = I.localFunctional a) ∧
      (∀ a ∈ Q, I.admissible a) ∧
      Q.card = Module.finrank k (obstructionDual J) ∧
      Function.Surjective (augmentedMap J column Q) := by
  obtain ⟨column, hcolumn⟩ :=
    exists_representing_columns J I.localFunctional
  have hdetect : ∀ φ : obstructionDual J, φ ≠ 0 →
      ∃ a : Aux, I.admissible a ∧ columnFunctional J column a φ ≠ 0 := by
    intro φ hφ
    obtain ⟨a, ha, hlocal⟩ := I.detects φ hφ
    refine ⟨a, ha, ?_⟩
    rw [hcolumn a]
    exact hlocal
  obtain ⟨Q, hgood, hcard, hsurj⟩ :=
    exists_exact_admissible_columns_making_augmentedMap_surjective
      J column I.admissible hdetect
  exact ⟨column, Q, hcolumn, hgood, hcard, hsurj⟩

/-- The same represented columns support every compatible state-dependent
linearized lift system through every finite depth. -/
theorem exists_representing_columns_supporting_finite_depth_lifts
    [DecidableEq Aux] [FiniteDimensional k W]
    (J : U →ₗ[k] W)
    (I : OnePrimeSelectionInterface k (obstructionDual J) Aux) :
    ∃ column : Aux → W, ∃ Q : Finset Aux,
      (∀ a : Aux, columnFunctional J column a = I.localFunctional a) ∧
      (∀ a ∈ Q, I.admissible a) ∧
      Q.card = Module.finrank k (obstructionDual J) ∧
      Function.Surjective (augmentedMap J column Q) ∧
      ∀ {State : Type*}
        (initial : State)
        (defect : ℕ → State → W)
        (update : ℕ → State → (U × (Q → k)) → State)
        (Valid : ℕ → State → Prop),
        Valid 0 initial →
        (∀ n s correction,
          Valid n s →
          augmentedMap J column Q correction + defect n s = 0 →
          Valid (n + 1) (update n s correction)) →
        ∀ N : ℕ, ∃ state : State, Valid N state := by
  obtain ⟨column, hcolumn⟩ :=
    exists_representing_columns J I.localFunctional
  have hdetect : ∀ φ : obstructionDual J, φ ≠ 0 →
      ∃ a : Aux, I.admissible a ∧ columnFunctional J column a φ ≠ 0 := by
    intro φ hφ
    obtain ⟨a, ha, hlocal⟩ := I.detects φ hφ
    refine ⟨a, ha, ?_⟩
    rw [hcolumn a]
    exact hlocal
  obtain ⟨Q, hgood, hcard, hsurj, hlift⟩ :=
    exists_exact_admissible_columns_supporting_finite_depth_lifts
      J column I.admissible hdetect
  exact ⟨column, Q, hcolumn, hgood, hcard, hsurj, hlift⟩

end

end Komorebi.StrongArtin.ObstructionFunctionalColumnRepresentation

#print axioms Komorebi.StrongArtin.ObstructionFunctionalColumnRepresentation.evaluationColumnMap_surjective
#print axioms Komorebi.StrongArtin.ObstructionFunctionalColumnRepresentation.exists_representing_columns
#print axioms Komorebi.StrongArtin.ObstructionFunctionalColumnRepresentation.exists_representing_columns_and_surjective_auxiliary_set
#print axioms Komorebi.StrongArtin.ObstructionFunctionalColumnRepresentation.exists_representing_columns_supporting_finite_depth_lifts
