import PaperICompletion5.LinearPrimaryEigenspace
import Mathlib.FieldTheory.IsAlgClosed.Basic

/-! # The geometric seed formula for arbitrary operators
No eigenbasis, diagonalization or multiplicity certificate is an input.
The spectrum is the actual algebraic spectrum. Empty spectral maxima are zero.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperICompletion5.GeometricSeedFormula
open Polynomial
open Komorebi.PaperICompletion4.OperatorIntrinsicFormula
open Komorebi.PaperICompletion5.LinearPrimaryEigenspace
open Komorebi.SeedRankBasics
open Komorebi.SingleOperatorGraph
universe u v
variable {k : Type u} [Field k]
variable {V : Type v} [AddCommGroup V] [Module k V]

/-- Geometric multiplicity values over every scalar, including zero off the spectrum. -/
def geometricMultiplicityValues (T : Module.End k V) : Set ℕ :=
  Set.range (fun a : k ↦ Module.finrank k (T.eigenspace a))

/-- The all-scalar value set is nonempty, including on a zero space. -/
theorem geometricMultiplicityValues_nonempty (T : Module.End k V) :
    (geometricMultiplicityValues T).Nonempty :=
  ⟨Module.finrank k (T.eigenspace 0), 0, rfl⟩

/-- Each geometric multiplicity is bounded by seed rank, over any field. -/
theorem eigenspace_finrank_le_seedFinrank [FiniteDimensional k V]
    (T : Module.End k V) (a : k) :
    Module.finrank k (T.eigenspace a) ≤ seedFinrank (operatorAlgebra T) V := by
  rw [← intrinsicMultiplicity_X_sub_C_eq_eigenspace T a]
  exact intrinsicMultiplicity_le_seedFinrank T (X - C a) (irreducible_X_sub_C a)

/-- The all-scalar supremum is a finite attained maximum. -/
theorem geometricMultiplicityValues_bddAbove [FiniteDimensional k V] (T : Module.End k V) :
    BddAbove (geometricMultiplicityValues T) := by
  refine ⟨seedFinrank (operatorAlgebra T) V, ?_⟩
  rintro n ⟨a, rfl⟩
  exact eigenspace_finrank_le_seedFinrank T a

/-- A presentation-free maximum of actual eigenspace dimensions. -/
def geometricSeedMaximum (T : Module.End k V) : ℕ := sSup (geometricMultiplicityValues T)

/-- A scalar attaining the maximum exists even if the whole space is zero. -/
theorem geometricSeedMaximum_attained [FiniteDimensional k V] (T : Module.End k V) :
    ∃ a : k, Module.finrank k (T.eigenspace a) = geometricSeedMaximum T :=
  Nat.sSup_mem (geometricMultiplicityValues_nonempty T) (geometricMultiplicityValues_bddAbove T)

/-- Over an algebraically closed field, every monic irreducible is a linear factor. -/
theorem monic_irreducible_eq_X_sub_C [IsAlgClosed k] (p : k[X])
    (hm : p.Monic) (hp : Irreducible p) : ∃ a : k, p = X - C a := by
  refine ⟨-p.coeff 0, ?_⟩
  simpa [hm.leadingCoeff] using
    (eq_X_add_C_of_degree_eq_one (IsAlgClosed.degree_eq_one_of_irreducible k hp))

/-- The intrinsic primary and geometric value sets are exactly equal. -/
theorem primaryValues_eq_geometricValues [FiniteDimensional k V] [IsAlgClosed k]
    (T : Module.End k V) : monicPrimaryMultiplicityValues T = geometricMultiplicityValues T := by
  ext n
  constructor
  · rintro ⟨p, hm, hp, rfl⟩
    obtain ⟨a, rfl⟩ := monic_irreducible_eq_X_sub_C p hm hp
    exact ⟨a, (intrinsicMultiplicity_X_sub_C_eq_eigenspace T a).symm⟩
  · rintro ⟨a, rfl⟩
    exact ⟨X - C a, monic_X_sub_C a, irreducible_X_sub_C a,
      intrinsicMultiplicity_X_sub_C_eq_eigenspace T a⟩

/-- Natural-valued seed rank equals the largest actual eigenspace dimension. -/
theorem operator_seedFinrank_eq_geometricSeedMaximum
    [FiniteDimensional k V] [IsAlgClosed k] (T : Module.End k V) :
    seedFinrank (operatorAlgebra T) V = geometricSeedMaximum T := by
  rw [operator_seedFinrank_eq_intrinsicSeedMaximum]
  unfold intrinsicSeedMaximum geometricSeedMaximum
  rw [primaryValues_eq_geometricValues T]

/-- Cardinal-valued seed rank equals the same finite maximum. -/
theorem operator_seedRank_eq_geometricSeedMaximum
    [FiniteDimensional k V] [IsAlgClosed k] (T : Module.End k V) :
    seedRank (operatorAlgebra T) V = (geometricSeedMaximum T : Cardinal) := by
  rw [operator_seedRank_eq_intrinsicSeedMaximum,
    ← operator_seedFinrank_eq_intrinsicSeedMaximum T,
    operator_seedFinrank_eq_geometricSeedMaximum T]

/-- Spectral values use the actual algebraic spectrum, not a supplied list of eigenvalues. -/
def spectralMultiplicityValues (T : Module.End k V) : Set ℕ :=
  {n | ∃ a : k, a ∈ spectrum k T ∧ Module.finrank k (T.eigenspace a) = n}

/-- The spectral value set is bounded whether or not it is empty. -/
theorem spectralMultiplicityValues_bddAbove [FiniteDimensional k V] (T : Module.End k V) :
    BddAbove (spectralMultiplicityValues T) := by
  refine ⟨seedFinrank (operatorAlgebra T) V, ?_⟩
  rintro n ⟨a, _, rfl⟩
  exact eigenspace_finrank_le_seedFinrank T a

/-- Geometric multiplicity is zero outside the spectrum. -/
theorem eigenspace_finrank_eq_zero_of_not_mem_spectrum [FiniteDimensional k V]
    (T : Module.End k V) (a : k) (ha : a ∉ spectrum k T) :
    Module.finrank k (T.eigenspace a) = 0 := by
  have hn : ¬T.HasEigenvalue a := fun h ↦ ha h.mem_spectrum
  have hb : T.eigenspace a = ⊥ := by
    simpa only [Module.End.hasEigenvalue_iff, not_not] using hn
  rw [hb]
  exact finrank_bot k V

/-- The spectral supremum uses the natural-number empty-set convention, namely zero. -/
def spectralSeedMaximum (T : Module.End k V) : ℕ := sSup (spectralMultiplicityValues T)

/-- Restricting from all scalars to the spectrum removes only zero values. -/
theorem geometricSeedMaximum_eq_spectralSeedMaximum [FiniteDimensional k V]
    (T : Module.End k V) : geometricSeedMaximum T = spectralSeedMaximum T := by
  apply le_antisymm
  · apply csSup_le (geometricMultiplicityValues_nonempty T)
    rintro n ⟨a, rfl⟩
    by_cases ha : a ∈ spectrum k T
    · exact le_csSup (spectralMultiplicityValues_bddAbove T) ⟨a, ha, rfl⟩
    · change Module.finrank k (T.eigenspace a) ≤ spectralSeedMaximum T
      rw [eigenspace_finrank_eq_zero_of_not_mem_spectrum T a ha]
      exact Nat.zero_le _
  · apply csSup_le'
    rintro n ⟨a, _, rfl⟩
    exact le_csSup (geometricMultiplicityValues_bddAbove T) ⟨a, rfl⟩

/-- The exact printed geometric formula, including the empty-spectrum convention. -/
theorem operator_seedFinrank_eq_spectralSeedMaximum
    [FiniteDimensional k V] [IsAlgClosed k] (T : Module.End k V) :
    seedFinrank (operatorAlgebra T) V = spectralSeedMaximum T := by
  rw [operator_seedFinrank_eq_geometricSeedMaximum, geometricSeedMaximum_eq_spectralSeedMaximum]

/-- Cardinal-valued version of the printed formula. -/
theorem operator_seedRank_eq_spectralSeedMaximum
    [FiniteDimensional k V] [IsAlgClosed k] (T : Module.End k V) :
    seedRank (operatorAlgebra T) V = (spectralSeedMaximum T : Cardinal) := by
  rw [operator_seedRank_eq_geometricSeedMaximum, geometricSeedMaximum_eq_spectralSeedMaximum]

end Komorebi.PaperICompletion5.GeometricSeedFormula
