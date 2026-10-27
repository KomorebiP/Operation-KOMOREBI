import PaperICompletion5
import IntrinsicBoundaryConsumers

set_option autoImplicit false
noncomputable section
namespace PaperIBlock05Tests
open Polynomial
open scoped Pointwise
open Komorebi.PaperICompletion3.PrimarySeedFormula
open Komorebi.PaperICompletion3.OperatorPrimaryAPI
open Komorebi.PaperICompletion4.ResidueQuotient
open Komorebi.PaperICompletion4.OperatorIntrinsicFormula
open Komorebi.PaperICompletion5.LinearPrimaryEigenspace
open Komorebi.PaperICompletion5.GeometricSeedFormula
open Komorebi.PaperICompletion5.CyclicGeometricCriterion
open Komorebi.PaperICompletion.CyclicClassification
open Komorebi.SeedRankBasics
open Komorebi.SingleOperatorGraph

-- Literal multiplication by X on one size-two primary chain over the complex numbers.
abbrev JordanModule := (i : Fin 1) → ℂ[X] ⧸ Ideal.span {X ^ 2}
instance jordanCoordinateFinite : Module.Finite ℂ (ℂ[X] ⧸ Ideal.span {X ^ 2}) :=
  (monic_X.pow 2).finite_quotient

def jordanOperator : Module.End ℂ JordanModule :=
  DistribSMul.toLinearMap ℂ JordanModule (X : ℂ[X])

def jordanPresentation : PrimaryPresentation jordanOperator where
  Index := Fin 1
  indexFintype := inferInstance
  prime := fun _ ↦ X
  irreducible := fun _ ↦ irreducible_X
  exponent := fun _ ↦ 2
  positive := fun _ ↦ by decide
  equiv := LinearEquiv.ofAEval jordanOperator (LinearEquiv.refl ℂ _) (fun _ ↦ rfl)

theorem jordan_space_dimension_two : Module.finrank ℂ JordanModule = 2 := by
  simp [JordanModule, Module.finrank_pi, finrank_quotient_span_eq_natDegree]

theorem jordan_intrinsic_multiplicity_one : intrinsicMultiplicity jordanOperator X = 1 := by
  rw [intrinsicMultiplicity_eq_fiber jordanPresentation X irreducible_X]
  unfold fiberMultiplicity
  exact (Fintype.card_congr (Equiv.subtypeUnivEquiv (fun _ ↦ rfl))).trans (Fintype.card_fin 1)

theorem jordan_eigenspace_dimension_one :
    Module.finrank ℂ (jordanOperator.eigenspace 0) = 1 := by
  rw [← intrinsicMultiplicity_X_sub_C_eq_eigenspace]
  simpa using jordan_intrinsic_multiplicity_one

theorem jordan_square_zero : jordanOperator ^ 2 = 0 := by
  ext x i
  change (X : ℂ[X]) • ((X : ℂ[X]) • x i) = 0
  rw [smul_smul, ← pow_two, Algebra.smul_def]
  have hX : (algebraMap ℂ[X] (ℂ[X] ⧸ Ideal.span {(X : ℂ[X]) ^ 2})) (X ^ 2) = 0 :=
    Ideal.Quotient.eq_zero_iff_mem.mpr (Ideal.subset_span (Set.mem_singleton _))
  rw [hX, zero_mul]

theorem jordan_nonzero : jordanOperator ≠ 0 := by
  intro h
  have hdim := jordan_eigenspace_dimension_one
  rw [h, Module.End.eigenspace_def, zero_smul, sub_zero, LinearMap.ker_zero,
    finrank_top, jordan_space_dimension_two] at hdim
  omega

theorem jordan_no_eigenbasis :
    ¬ ∃ (b : Module.Basis (Fin 2) ℂ JordanModule) (a : Fin 2 → ℂ),
      ∀ i, jordanOperator (b i) = a i • b i := by
  rintro ⟨b, a, ha⟩
  have hzero : ∀ i, a i = 0 := by
    intro i
    have hsq := congrArg (fun S : Module.End ℂ JordanModule ↦ S (b i)) jordan_square_zero
    change jordanOperator (jordanOperator (b i)) = 0 at hsq
    rw [ha i, map_smul, ha i, smul_smul] at hsq
    have hmul : a i * a i = 0 := (smul_eq_zero.mp hsq).resolve_right (b.ne_zero i)
    exact (mul_self_eq_zero.mp hmul)
  apply jordan_nonzero
  apply b.ext
  intro i
  simp only [ha i, hzero i, zero_smul, LinearMap.zero_apply]

theorem jordan_cyclic : HasCyclicVector jordanOperator := by
  apply jordanPresentation.cyclic_iff_label_injective.mpr
  exact Function.injective_of_subsingleton _

theorem jordan_geometric_maximum_one : geometricSeedMaximum jordanOperator = 1 := by
  let : Nontrivial JordanModule := Module.nontrivial_of_finrank_pos (by
    rw [jordan_space_dimension_two]; decide)
  exact (hasCyclicVector_iff_geometricSeedMaximum_one jordanOperator).mp jordan_cyclic

theorem jordan_spectral_maximum_one : spectralSeedMaximum jordanOperator = 1 := by
  rw [← geometricSeedMaximum_eq_spectralSeedMaximum, jordan_geometric_maximum_one]

-- Two primary chains for the same eigenvalue, of different lengths.
abbrev RepeatedJordanModule := (i : Fin 2) → ℂ[X] ⧸ Ideal.span {X ^ (i.val + 1)}
instance repeatedJordanCoordinateFinite (i : Fin 2) :
    Module.Finite ℂ (ℂ[X] ⧸ Ideal.span {X ^ (i.val + 1)}) :=
  (monic_X.pow _).finite_quotient

def repeatedJordanOperator : Module.End ℂ RepeatedJordanModule :=
  DistribSMul.toLinearMap ℂ RepeatedJordanModule (X : ℂ[X])

def repeatedJordanPresentation : PrimaryPresentation repeatedJordanOperator where
  Index := Fin 2
  indexFintype := inferInstance
  prime := fun _ ↦ X
  irreducible := fun _ ↦ irreducible_X
  exponent := fun i ↦ i.val + 1
  positive := fun _ ↦ Nat.succ_pos _
  equiv := LinearEquiv.ofAEval repeatedJordanOperator (LinearEquiv.refl ℂ _) (fun _ ↦ rfl)

theorem repeated_jordan_intrinsic_two : intrinsicMultiplicity repeatedJordanOperator X = 2 := by
  rw [intrinsicMultiplicity_eq_fiber repeatedJordanPresentation X irreducible_X]
  unfold fiberMultiplicity
  exact (Fintype.card_congr (Equiv.subtypeUnivEquiv (fun _ ↦ rfl))).trans (Fintype.card_fin 2)

theorem repeated_jordan_eigenspace_two :
    Module.finrank ℂ (repeatedJordanOperator.eigenspace 0) = 2 := by
  rw [← intrinsicMultiplicity_X_sub_C_eq_eigenspace]
  simpa using repeated_jordan_intrinsic_two

theorem repeated_jordan_seed_count_two :
    seedFinrank (operatorAlgebra repeatedJordanOperator) RepeatedJordanModule = 2 := by
  rw [operator_seedFinrank_eq_intrinsic_primary_max repeatedJordanPresentation]
  change (Finset.univ.sup fun _ : Fin 2 ↦ intrinsicMultiplicity repeatedJordanOperator X) = 2
  rw [repeated_jordan_intrinsic_two]
  simp only [Finset.sup_const (Finset.univ_nonempty (α := Fin 2))]

theorem repeated_jordan_spectral_maximum_two : spectralSeedMaximum repeatedJordanOperator = 2 := by
  rw [← operator_seedFinrank_eq_spectralSeedMaximum, repeated_jordan_seed_count_two]

-- An unsplit rational operator has no rational eigenvalues but still needs a seed.
open PaperIBlock03Tests PaperIBlock04Tests

theorem quadratic_label_ne_linear (a : ℚ) :
    Ideal.span {quadratic} ≠ Ideal.span {X - C a} := by
  intro h
  have hmem : quadratic ∈ Ideal.span {X - C a} := by
    rw [← h]
    exact Ideal.subset_span (Set.mem_singleton _)
  exact quadratic_no_rational_root a (dvd_iff_isRoot.mp (Ideal.mem_span_singleton.mp hmem))

theorem rational_unsplit_eigenspace_zero (a : ℚ) :
    Module.finrank ℚ (squaredOperator.eigenspace a) = 0 := by
  rw [← intrinsicMultiplicity_X_sub_C_eq_eigenspace]
  apply intrinsicMultiplicity_eq_zero_of_absent squaredPresentation _ (irreducible_X_sub_C a)
  intro i
  exact quadratic_label_ne_linear a

theorem rational_unsplit_geometric_maximum_zero : geometricSeedMaximum squaredOperator = 0 := by
  apply Nat.eq_zero_of_le_zero
  apply csSup_le (geometricMultiplicityValues_nonempty squaredOperator)
  rintro n ⟨a, rfl⟩
  change Module.finrank ℚ (squaredOperator.eigenspace a) ≤ 0
  rw [rational_unsplit_eigenspace_zero]

theorem rational_unsplit_seed_count_one :
    seedFinrank (operatorAlgebra squaredOperator) SquaredModule = 1 := by
  rw [operator_seedFinrank_eq_intrinsicSeedMaximum, squared_intrinsic_maximum_one]

theorem algClosed_hypothesis_cannot_be_dropped :
    seedFinrank (operatorAlgebra squaredOperator) SquaredModule ≠ geometricSeedMaximum squaredOperator := by
  rw [rational_unsplit_seed_count_one, rational_unsplit_geometric_maximum_zero]
  decide

-- Zero-space convention, actual kernel and literal quotient representatives.
theorem zero_space_geometric_maximum :
    geometricSeedMaximum (0 : Module.End ℂ (Fin 0 → ℂ)) = 0 := by
  apply Nat.eq_zero_of_le_zero
  apply csSup_le (geometricMultiplicityValues_nonempty _)
  rintro n ⟨a, rfl⟩
  change Module.finrank ℂ ((0 : Module.End ℂ (Fin 0 → ℂ)).eigenspace a) ≤ 0
  simp

theorem zero_space_spectral_maximum :
    spectralSeedMaximum (0 : Module.End ℂ (Fin 0 → ℂ)) = 0 := by
  rw [← geometricSeedMaximum_eq_spectralSeedMaximum, zero_space_geometric_maximum]

theorem literal_cokernel_kernel (p : ℂ[X]) :
    (polynomialCokernelMap jordanOperator p).ker =
      (p • (⊤ : Submodule ℂ[X] (Module.AEval' jordanOperator))).restrictScalars ℂ :=
  polynomialCokernelMap_ker _ _

theorem literal_cokernel_representative (p : ℂ[X]) (x : JordanModule) :
    polynomialQuotientEquivCokernel jordanOperator p
        (Submodule.Quotient.mk (Module.AEval'.of jordanOperator x)) =
      Submodule.Quotient.mk x :=
  polynomialQuotientEquivCokernel_mk _ _ _

theorem jordan_one_factor_presentation :
    Nonempty (Module.AEval' jordanOperator ≃ₗ[ℂ[X]]
      ℂ[X] ⧸ Ideal.span {minpoly ℂ jordanOperator}) :=
  (hasCyclicVector_iff_minpoly_quotient_presentation jordanOperator).mp jordan_cyclic

end PaperIBlock05Tests
