import PaperICompletion4
import PrimaryBoundaryConsumers

set_option autoImplicit false
noncomputable section
open scoped Pointwise
namespace PaperIBlock04Tests
open Polynomial
open PaperIBlock03Tests
open Komorebi.PaperICompletion3.PrimarySeedFormula
open Komorebi.PaperICompletion3.OperatorPrimaryAPI
open Komorebi.PaperICompletion4.ResidueQuotient
open Komorebi.PaperICompletion4.IntrinsicPrimary
open Komorebi.PaperICompletion4.GroupedPrimary
open Komorebi.PaperICompletion4.OperatorIntrinsicFormula

-- Explicit nonlinear primary modules with the actual X-action as their operator.
theorem quadratic_monic : quadratic.Monic := monic_X_pow_add_C 1 (by decide)

abbrev RepeatedModule := (i : Fin 2) → ℚ[X] ⧸ Ideal.span {quadratic ^ (i.val + 1)}
abbrev SquaredModule := (i : Fin 1) → ℚ[X] ⧸ Ideal.span {quadratic ^ 2}

instance repeatedCoordinateFinite (i : Fin 2) :
    Module.Finite ℚ (ℚ[X] ⧸ Ideal.span {quadratic ^ (i.val + 1)}) :=
  (quadratic_monic.pow _).finite_quotient
instance squaredCoordinateFinite : Module.Finite ℚ (ℚ[X] ⧸ Ideal.span {quadratic ^ 2}) :=
  (quadratic_monic.pow 2).finite_quotient

def repeatedOperator : Module.End ℚ RepeatedModule :=
  DistribSMul.toLinearMap ℚ RepeatedModule (X : ℚ[X])
def squaredOperator : Module.End ℚ SquaredModule :=
  DistribSMul.toLinearMap ℚ SquaredModule (X : ℚ[X])

instance repeatedArtinian : IsArtinian ℚ[X] (Module.AEval' repeatedOperator) :=
  isArtinian_of_tower ℚ inferInstance

def repeatedPresentation : PrimaryPresentation repeatedOperator where
  Index := Fin 2
  indexFintype := inferInstance
  prime := fun _ ↦ quadratic
  irreducible := fun _ ↦ quadratic_irreducible
  exponent := fun i ↦ i.val + 1
  positive := fun _ ↦ Nat.succ_pos _
  equiv := LinearEquiv.ofAEval repeatedOperator (LinearEquiv.refl ℚ _) (fun _ ↦ rfl)

def squaredPresentation : PrimaryPresentation squaredOperator where
  Index := Fin 1
  indexFintype := inferInstance
  prime := fun _ ↦ quadratic
  irreducible := fun _ ↦ quadratic_irreducible
  exponent := fun _ ↦ 2
  positive := fun _ ↦ by decide
  equiv := LinearEquiv.ofAEval squaredOperator (LinearEquiv.refl ℚ _) (fun _ ↦ rfl)

theorem quadratic_label_ne_X : Ideal.span {quadratic} ≠ Ideal.span {(X : ℚ[X])} := by
  intro h
  have hmem : quadratic ∈ Ideal.span {(X : ℚ[X])} := by
    rw [← h]
    exact Ideal.subset_span (Set.mem_singleton _)
  have hd := Polynomial.X_dvd_iff.mp (Ideal.mem_span_singleton.mp hmem)
  norm_num [quadratic] at hd

theorem nonlinear_repeated_intrinsic_dimension_two :
    intrinsicMultiplicity repeatedOperator quadratic = 2 := by
  rw [intrinsicMultiplicity_eq_fiber repeatedPresentation quadratic quadratic_irreducible]
  unfold fiberMultiplicity
  exact (Fintype.card_congr (Equiv.subtypeUnivEquiv (fun _ ↦ rfl))).trans (Fintype.card_fin 2)

theorem nonlinear_squared_intrinsic_dimension_one :
    intrinsicMultiplicity squaredOperator quadratic = 1 := by
  rw [intrinsicMultiplicity_eq_fiber squaredPresentation quadratic quadratic_irreducible]
  unfold fiberMultiplicity
  exact (Fintype.card_congr (Equiv.subtypeUnivEquiv (fun _ ↦ rfl))).trans (Fintype.card_fin 1)

theorem absent_X_intrinsic_dimension_zero :
    intrinsicMultiplicity repeatedOperator (X : ℚ[X]) = 0 := by
  apply intrinsicMultiplicity_eq_zero_of_absent repeatedPresentation X irreducible_X
  intro i
  exact quadratic_label_ne_X

theorem repeated_primary_is_whole : primarySubmodule RepeatedModule quadratic = ⊤ := by
  apply top_unique
  intro x _
  apply (primaryProduct_mem_iff (fun _ : Fin 2 ↦ quadratic) (fun _ ↦ quadratic_irreducible)
    (fun i : Fin 2 ↦ i.val + 1) quadratic quadratic_irreducible x).mpr
  intro i hi
  exact (hi rfl).elim

theorem absent_primary_component_is_zero : primarySubmodule RepeatedModule (X : ℚ[X]) = ⊥ := by
  ext x
  rw [primaryProduct_mem_iff (fun _ : Fin 2 ↦ quadratic) (fun _ ↦ quadratic_irreducible)
    (fun i : Fin 2 ↦ i.val + 1) X irreducible_X, Submodule.mem_bot]
  constructor
  · intro h
    exact funext (fun i ↦ h i quadratic_label_ne_X)
  · rintro rfl i _
    rfl

theorem associated_negative_quadratic_same_intrinsic_dimension :
    intrinsicMultiplicity repeatedOperator (-quadratic) = 2 := by
  rw [intrinsicMultiplicity_eq_of_span_eq repeatedOperator (-quadratic) quadratic
    (Associated.irreducible (show Associated quadratic (-quadratic) from
      ⟨-1, mul_neg_one quadratic⟩) quadratic_irreducible)
    quadratic_irreducible (by simp), nonlinear_repeated_intrinsic_dimension_two]

theorem chosen_presentation_individual_fibre_two :
    fiberMultiplicity (chosenPrimaryPresentation repeatedOperator).label (Ideal.span {quadratic}) = 2 := by
  rw [← intrinsicMultiplicity_eq_fiber (chosenPrimaryPresentation repeatedOperator)
    quadratic quadratic_irreducible, nonlinear_repeated_intrinsic_dimension_two]

theorem repeated_intrinsic_maximum_two : intrinsicSeedMaximum repeatedOperator = 2 := by
  rw [← operator_seedFinrank_eq_intrinsicSeedMaximum repeatedOperator,
    operator_seedFinrank_eq_intrinsic_primary_max repeatedPresentation]
  change (Finset.univ.sup fun _ : Fin 2 ↦ intrinsicMultiplicity repeatedOperator quadratic) = 2
  rw [nonlinear_repeated_intrinsic_dimension_two]
  simp only [Finset.sup_const (Finset.univ_nonempty (α := Fin 2))]

theorem squared_intrinsic_maximum_one : intrinsicSeedMaximum squaredOperator = 1 := by
  rw [← operator_seedFinrank_eq_intrinsicSeedMaximum squaredOperator,
    operator_seedFinrank_eq_intrinsic_primary_max squaredPresentation]
  change (Finset.univ.sup fun _ : Fin 1 ↦ intrinsicMultiplicity squaredOperator quadratic) = 1
  rw [nonlinear_squared_intrinsic_dimension_one]
  simp only [Finset.sup_const (Finset.univ_nonempty (α := Fin 1))]

theorem zero_space_intrinsic_maximum_zero :
    intrinsicSeedMaximum (0 : Module.End ℚ (Fin 0 → ℚ)) = 0 := by
  rw [← operator_seedFinrank_eq_intrinsicSeedMaximum,
    operator_seedFinrank_eq_primaryGeneratorCount]
  exact zero_operator_on_zero_space_count_zero

theorem zero_space_each_intrinsic_dimension_zero (p : ℚ[X]) (hp : Irreducible p) :
    intrinsicMultiplicity (0 : Module.End ℚ (Fin 0 → ℚ)) p = 0 := by
  apply Nat.eq_zero_of_le_zero
  have h := intrinsicMultiplicity_le_seedFinrank (0 : Module.End ℚ (Fin 0 → ℚ)) p hp
  rwa [operator_seedFinrank_eq_intrinsicSeedMaximum, zero_space_intrinsic_maximum_zero] at h

-- A genuine counterexample guards the Artinian hypothesis in the primary/global bridge.
theorem free_polynomial_primary_component_zero :
    primarySubmodule ℚ[X] (X : ℚ[X]) = ⊥ := by
  ext x
  change (∃ n : ℕ, X ^ n * x = 0) ↔ x = 0
  constructor
  · rintro ⟨n, hn⟩
    exact (mul_eq_zero.mp hn).resolve_left (pow_ne_zero n X_ne_zero)
  · rintro rfl
    exact ⟨0, mul_zero _⟩

theorem free_polynomial_primary_map_not_surjective :
    ¬ Function.Surjective (primaryToGlobal ℚ[X] (X : ℚ[X])) := by
  intro hs
  let q : ScalarQuotient ℚ[X] (X : ℚ[X]) := Submodule.Quotient.mk 1
  obtain ⟨x, hx⟩ := hs q
  have hx0 : (x : ℚ[X]) = 0 := by
    have h : (x : ℚ[X]) ∈ (⊥ : Submodule ℚ[X] ℚ[X]) :=
      (le_of_eq free_polynomial_primary_component_zero) x.property
    simpa only [Submodule.mem_bot] using h
  have hq : q = 0 := by
    rw [← hx]
    change Submodule.Quotient.mk (x : ℚ[X]) = 0
    rw [hx0, Submodule.Quotient.mk_zero]
  have hdiv : (X : ℚ[X]) ∣ 1 := by
    have hmem := (Submodule.Quotient.mk_eq_zero _).mp hq
    obtain ⟨y, hy⟩ := (mem_scalarImage_iff (X : ℚ[X]) _).mp hmem
    exact ⟨y, hy.symm⟩
  have hh := Polynomial.X_dvd_iff.mp hdiv
  norm_num at hh

-- Exact kernel and representative behavior, specialized to a nonlinear operator.
theorem nonlinear_primary_global_kernel_exact :
    (primaryToGlobal (Module.AEval' repeatedOperator) quadratic).ker =
      quadratic • (⊤ : Submodule ℚ[X]
        (primarySubmodule (Module.AEval' repeatedOperator) quadratic)) :=
  primaryToGlobal_ker _ _

theorem nonlinear_primary_quotient_respects_inclusion
    (x : primarySubmodule (Module.AEval' repeatedOperator) quadratic) :
    primaryQuotientEquivGlobal (Module.AEval' repeatedOperator) quadratic
        (Submodule.Quotient.mk x) = Submodule.Quotient.mk (x : Module.AEval' repeatedOperator) := by
  exact primaryQuotientEquivGlobal_mk _ _ x

end PaperIBlock04Tests
