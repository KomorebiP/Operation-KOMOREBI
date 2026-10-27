import PaperICompletion6
import GeometricBoundaryConsumers
import Mathlib.Algebra.Field.ZMod

set_option autoImplicit false
noncomputable section
namespace PaperIBlock06Tests
open Polynomial
open scoped TensorProduct
open PaperIBlock03Tests PaperIBlock04Tests PaperIBlock05Tests
open Komorebi.SingleOperatorGraph
open Komorebi.SeedRankBasics
open Komorebi.PaperICompletion.CyclicClassification
open Komorebi.PaperICompletion4.IntrinsicPrimary
open Komorebi.PaperICompletion6.ScalarExtension
open Komorebi.PaperICompletion6.PrimaryCyclicCriterion
open Komorebi.PaperICompletion6.OneInvariantFactor
open Komorebi.PaperICompletion6.SixWayCyclicCriterion

-- Actual unsplit rational example: one length-two chain for X^2+1.
def squaredOneFactor : Module.AEval' squaredOperator ≃ₗ[ℚ[X]]
    ℚ[X] ⧸ Ideal.span {quadratic ^ 2} :=
  squaredPresentation.equiv.trans
    (LinearEquiv.piUnique (α := Fin 1) ℚ[X] (fun _ => ℚ[X] ⧸ Ideal.span {quadratic ^ 2}))

theorem squared_space_dimension_four : Module.finrank ℚ SquaredModule = 4 := by
  change Module.finrank ℚ (Fin 1 → ℚ[X] ⧸ Ideal.span {quadratic ^ 2}) = 4
  rw [Module.finrank_pi_fintype]
  simp [nonlinear_single_chain_base_dimension_four]

instance squaredNontrivial : Nontrivial SquaredModule :=
  Module.nontrivial_of_finrank_pos (by rw [squared_space_dimension_four]; decide)

theorem squared_minpoly_exact : minpoly ℚ squaredOperator = quadratic ^ 2 :=
  (factor_eq_minpoly squaredOperator _ (quadratic_monic.pow 2) squaredOneFactor).symm

theorem squared_cyclic : HasCyclicVector squaredOperator := by
  apply squaredPresentation.cyclic_iff_label_injective.mpr
  intro i j _
  exact @Subsingleton.elim (Fin 1) inferInstance i j

theorem squared_extended_cyclic : HasCyclicVector (squaredOperator.baseChange ℂ) :=
  (hasCyclicVector_baseChange_iff ℂ squaredOperator).mpr squared_cyclic

theorem squared_complex_minpoly_exact :
    minpoly ℂ (squaredOperator.baseChange ℂ) = (X ^ 2 + C 1 : ℂ[X]) ^ 2 := by
  rw [minpoly_baseChange, squared_minpoly_exact]
  simp [quadratic]

theorem squared_complex_minpoly_degree_four :
    (minpoly ℂ (squaredOperator.baseChange ℂ)).natDegree = 4 := by
  rw [minpoly_natDegree_baseChange, squared_minpoly_exact, Polynomial.natDegree_pow,
    quadratic_degree]

theorem squared_complex_multiplicities_one :
    ∀ a : ℂ, a ∈ spectrum ℂ (squaredOperator.baseChange ℂ) →
      Module.finrank ℂ (Module.End.eigenspace (squaredOperator.baseChange ℂ) a) = 1 :=
  (hasCyclicVector_iff_extended_spectral_multiplicities_one ℂ squaredOperator).mp squared_cyclic

theorem rational_eigenspaces_zero_but_extended_multiplicity_one :
    (∀ a : ℚ, Module.finrank ℚ (squaredOperator.eigenspace a) = 0) ∧
    (∀ a : ℂ, a ∈ spectrum ℂ (squaredOperator.baseChange ℂ) →
      Module.finrank ℂ (Module.End.eigenspace (squaredOperator.baseChange ℂ) a) = 1) :=
  ⟨rational_unsplit_eigenspace_zero, squared_complex_multiplicities_one⟩

theorem squared_intrinsic_components_cyclic (p : ℚ[X]) :
    Cyclic ℚ[X] (primarySubmodule (Module.AEval' squaredOperator) p) :=
  primary_cyclic_of_hasCyclicVector squaredOperator squared_cyclic p

theorem squared_literal_companion_basis :
    ∃ b : Module.Basis (Fin (quadratic ^ 2).natDegree) ℚ SquaredModule,
      LinearMap.toMatrix b b squaredOperator = companionMatrix (quadratic ^ 2) :=
  ⟨quotientCompanionBasis squaredOperator _ (quadratic_monic.pow 2) squaredOneFactor,
    toMatrix_quotientCompanionBasis squaredOperator _ (quadratic_monic.pow 2) squaredOneFactor⟩

theorem squared_quotient_intertwines (x : AdjoinRoot (quadratic ^ 2)) :
    squaredOperator (quotientVectorEquiv squaredOperator _ squaredOneFactor x) =
      quotientVectorEquiv squaredOperator _ squaredOneFactor
        (AdjoinRoot.root (quadratic ^ 2) * x) :=
  quotientVectorEquiv_intertwines squaredOperator _ squaredOneFactor x

-- Check the actual signs and orientation, not only an abstract similarity type.
theorem quadratic_companion_entries :
    companionMatrix quadratic ⟨0, by rw [quadratic_degree]; decide⟩
        ⟨0, by rw [quadratic_degree]; decide⟩ = 0 ∧
    companionMatrix quadratic ⟨1, by rw [quadratic_degree]; decide⟩
        ⟨0, by rw [quadratic_degree]; decide⟩ = 1 ∧
    companionMatrix quadratic ⟨0, by rw [quadratic_degree]; decide⟩
        ⟨1, by rw [quadratic_degree]; decide⟩ = -1 ∧
    companionMatrix quadratic ⟨1, by rw [quadratic_degree]; decide⟩
        ⟨1, by rw [quadratic_degree]; decide⟩ = 0 := by
  norm_num [companionMatrix, quadratic_degree, quadratic, Polynomial.coeff_one]

-- Repeated chains cannot become cyclic after changing the field.
theorem repeated_jordan_not_cyclic : ¬ HasCyclicVector repeatedJordanOperator := by
  intro h
  have hi := repeatedJordanPresentation.cyclic_iff_label_injective.mp h
  have hbad : (0 : Fin 2) = 1 := hi (show repeatedJordanPresentation.label (0 : Fin 2) =
    repeatedJordanPresentation.label (1 : Fin 2) from rfl)
  exact zero_ne_one hbad

theorem repeated_jordan_extension_not_cyclic :
    ¬ HasCyclicVector (repeatedJordanOperator.baseChange (AlgebraicClosure ℂ)) := by
  intro h
  exact repeated_jordan_not_cyclic
    ((hasCyclicVector_baseChange_iff (AlgebraicClosure ℂ) repeatedJordanOperator).mp h)

theorem jordan_actual_companion_basis :
    ∃ b : Module.Basis (Fin (minpoly ℂ jordanOperator).natDegree) ℂ JordanModule,
      LinearMap.toMatrix b b jordanOperator = companionMatrix (minpoly ℂ jordanOperator) :=
  exists_companion_basis_of_cyclic jordanOperator jordan_cyclic

-- Minimal-polynomial preservation and at-most-one-generator cyclicity include zero spaces.
theorem zero_space_minpoly_extension :
    minpoly ℂ ((0 : Module.End ℚ (Fin 0 → ℚ)).baseChange ℂ) =
      (minpoly ℚ (0 : Module.End ℚ (Fin 0 → ℚ))).map (algebraMap ℚ ℂ) :=
  minpoly_baseChange ℂ _

theorem zero_space_extension_cyclic :
    HasCyclicVector ((0 : Module.End ℚ (Fin 0 → ℚ)).baseChange ℂ) := by
  apply (hasCyclicVector_baseChange_iff ℂ _).mpr
  refine ⟨fun _ : Fin 1 => 0, ?_⟩
  exact Subsingleton.elim _ _

theorem zero_space_seed_rank_not_one :
    seedRank (operatorAlgebra (0 : Module.End ℚ (Fin 0 → ℚ))) (Fin 0 → ℚ) ≠ 1 := by
  rw [(seedRank_eq_zero_iff _ _).mpr inferInstance]
  exact zero_ne_one

-- The extension theorems have no characteristic-zero requirement.
instance primeTwo : Fact (Nat.Prime 2) := ⟨by decide⟩
theorem characteristic_two_minpoly_extension (T : Module.End (ZMod 2) (ZMod 2)) :
    minpoly (AlgebraicClosure (ZMod 2)) (T.baseChange (AlgebraicClosure (ZMod 2))) =
      (minpoly (ZMod 2) T).map (algebraMap (ZMod 2) (AlgebraicClosure (ZMod 2))) :=
  minpoly_baseChange (AlgebraicClosure (ZMod 2)) T

theorem characteristic_two_cyclicity_descent (T : Module.End (ZMod 2) (ZMod 2)) :
    HasCyclicVector (T.baseChange (AlgebraicClosure (ZMod 2))) ↔ HasCyclicVector T :=
  hasCyclicVector_baseChange_iff (AlgebraicClosure (ZMod 2)) T

-- Literal six-way instance: the algebraic closure acts on the tensor-product operator.
theorem squared_six_way_algebraicClosure :
    List.TFAE [
      HasCyclicVector squaredOperator,
      seedRank (operatorAlgebra squaredOperator) SquaredModule = 1,
      ∀ p : ℚ[X], Irreducible p →
        Nontrivial (primarySubmodule (Module.AEval' squaredOperator) p) →
        Cyclic ℚ[X] (primarySubmodule (Module.AEval' squaredOperator) p),
      HasOneInvariantFactor squaredOperator,
      minpoly ℚ squaredOperator = squaredOperator.charpoly,
      ∀ a : AlgebraicClosure ℚ, a ∈ spectrum (AlgebraicClosure ℚ)
          (squaredOperator.baseChange (AlgebraicClosure ℚ)) →
        Module.finrank (AlgebraicClosure ℚ)
          (Module.End.eigenspace (squaredOperator.baseChange (AlgebraicClosure ℚ)) a) = 1] :=
  cyclic_six_way_algebraicClosure squaredOperator

end PaperIBlock06Tests
