import KomorebiVerification.SingleOperatorGraph
import Mathlib.Analysis.InnerProductSpace.Spectrum
import Mathlib.Analysis.Matrix.Hermitian

/-!
# Internally constructed spectral certificates for Paper I

The old graph theorem takes a multiplicity-grouped eigenbasis as an input.
This extension first groups any finite eigenbasis by equality of eigenvalues,
then obtains that basis from the finite-dimensional spectral theorem.  The
public self-adjoint theorem takes no eigenbasis, extraction polynomial,
quotient map, multiplicity function, or maximizer as an input.
-/

set_option autoImplicit false

noncomputable section

namespace Komorebi.PaperICompletion.SpectralCertificates

open Komorebi.SingleOperatorGraph
open scoped BigOperators

universe u v w

section Grouping
variable {k : Type u} [Field k] {I : Type v} [Fintype I]
variable {V : Type w} [AddCommGroup V] [Module k V]

/-- The distinct eigenvalue labels of a finite indexed eigenvalue list. -/
def EigenLabels (μ : I → k) := Set.range μ

noncomputable instance eigenLabelsFintype (μ : I → k) : Fintype (EigenLabels μ) :=
  (Set.finite_range μ).fintype

/-- The actual number of entries of the list equal to a specified scalar. -/
def eigenMultiplicity (μ : I → k) (value : k) : ℕ := Nat.card {i : I // μ i = value}

/-- A finite coordinate system for one eigenvalue fibre. -/
def eigenFibreEquiv (μ : I → k) (value : k) :
    {i : I // μ i = value} ≃ Fin (eigenMultiplicity μ value) := by
  classical
  exact Fintype.equivFinOfCardEq (by simp [eigenMultiplicity, Nat.card_eq_fintype_card])

/-- Re-index the whole basis by distinct eigenvalues and their multiplicities. -/
def groupedIndexEquiv (μ : I → k) :
    (Σ value : EigenLabels μ, Fin (eigenMultiplicity μ value.val)) ≃ I :=
  (Equiv.sigmaCongrRight fun value : EigenLabels μ ↦ (eigenFibreEquiv μ value.val).symm).trans
    (Equiv.sigmaSubtypeFiberEquiv μ (fun value ↦ value ∈ Set.range μ)
      (fun i ↦ Set.mem_range_self i))

omit [Field k] in
theorem groupedIndex_eigenvalue (μ : I → k)
    (z : Σ value : EigenLabels μ, Fin (eigenMultiplicity μ value.val)) :
    μ (groupedIndexEquiv μ z) = z.1.val := by
  change μ ((eigenFibreEquiv μ z.1.val).symm z.2).val = z.1.val
  exact ((eigenFibreEquiv μ z.1.val).symm z.2).property

/-- The multiplicity-grouped basis, constructed rather than supplied. -/
def groupedEigenbasis (μ : I → k) (b : Module.Basis I k V) :
    Module.Basis (Σ value : EigenLabels μ, Fin (eigenMultiplicity μ value.val)) k V :=
  b.reindex (groupedIndexEquiv μ).symm

theorem groupedEigenbasis_is_eigenbasis (T : Module.End k V)
    (μ : I → k) (b : Module.Basis I k V)
    (hEigen : ∀ i, T (b i) = μ i • b i)
    (z : Σ value : EigenLabels μ, Fin (eigenMultiplicity μ value.val)) :
    T (groupedEigenbasis μ b z) = z.1.val • groupedEigenbasis μ b z := by
  simp only [groupedEigenbasis, Module.Basis.reindex_apply, Equiv.symm_symm]
  rw [hEigen, groupedIndex_eigenvalue μ z]

/-- Maximum repeated-eigenvalue count, with the empty-list value fixed at zero. -/
def maxEigenMultiplicity (μ : I → k) : ℕ :=
  Finset.univ.sup fun value : EigenLabels μ ↦ eigenMultiplicity μ value.val

omit [Field k] in
theorem eigenMultiplicity_le_max (μ : I → k) (value : EigenLabels μ) :
    eigenMultiplicity μ value.val ≤ maxEigenMultiplicity μ := by
  unfold maxEigenMultiplicity
  exact Finset.le_sup (f := fun z : EigenLabels μ ↦ eigenMultiplicity μ z.val)
    (Finset.mem_univ value)

/-- Distinct labels, grouped basis, projectors, and maximizer are all built internally. -/
theorem seedNumber_isLeast_of_eigenbasis [Nonempty I]
    (T : Module.End k V) (μ : I → k) (b : Module.Basis I k V)
    (hEigen : ∀ i, T (b i) = μ i • b i) :
    IsLeast {r : ℕ | SeedNumberLE T r} (maxEigenMultiplicity μ) := by
  classical
  let i : I := Classical.arbitrary I
  have hnonempty : (Finset.univ : Finset (EigenLabels μ)).Nonempty :=
    ⟨⟨μ i, Set.mem_range_self i⟩, Finset.mem_univ _⟩
  obtain ⟨value, _hvalue, hmax⟩ := Finset.exists_mem_eq_sup Finset.univ hnonempty
    (fun value : EigenLabels μ ↦ eigenMultiplicity μ value.val)
  exact diagonalizable_seedNumber_isLeast_of_distinct_eigenvalues T
    (maxEigenMultiplicity μ) (fun value : EigenLabels μ ↦ eigenMultiplicity μ value.val)
    Subtype.val (groupedEigenbasis μ b)
    (groupedEigenbasis_is_eigenbasis T μ b hEigen) Subtype.val_injective
    (eigenMultiplicity_le_max μ) value hmax.symm

end Grouping

section SelfAdjoint
variable {𝕜 : Type u} [RCLike 𝕜]
variable {V : Type v} [NormedAddCommGroup V] [InnerProductSpace 𝕜 V]
variable [FiniteDimensional 𝕜 V]

/-- The list supplied by the proven finite-dimensional spectral theorem. -/
def spectralList (T : Module.End 𝕜 V) (hT : T.IsSymmetric) :
    Fin (Module.finrank 𝕜 V) → 𝕜 :=
  fun i ↦ (hT.eigenvalues rfl i : 𝕜)

/-- Multiplicities here are intrinsic eigenspace dimensions, not abstract input numbers. -/
theorem spectralList_multiplicity_eq_finrank
    (T : Module.End 𝕜 V) (hT : T.IsSymmetric) (value : 𝕜) :
    eigenMultiplicity (spectralList T hT) value =
      Module.finrank 𝕜 (Module.End.eigenspace T value) := by
  classical
  simpa [eigenMultiplicity, Nat.card_eq_fintype_card, Fintype.card_subtype, spectralList]
    using hT.card_filter_eigenvalues_eq rfl value

/-- Exact seed number from self-adjointness alone, including the zero space. -/
theorem selfAdjoint_seedNumber_isLeast
    (T : Module.End 𝕜 V) (hT : T.IsSymmetric) :
    IsLeast {r : ℕ | SeedNumberLE T r}
      (maxEigenMultiplicity (spectralList T hT)) := by
  classical
  by_cases hdim : Module.finrank 𝕜 V = 0
  · let : Subsingleton V := (Module.finrank_zero_iff).mp hdim
    have hmax : maxEigenMultiplicity (spectralList T hT) = 0 := by
      apply Finset.sup_eq_zero.mpr
      intro value _
      obtain ⟨i, _hi⟩ := value.property
      exact False.elim (by have := i.isLt; omega)
    rw [hmax]
    exact seedNumber_zero_isLeast_of_subsingleton T
  · let : NeZero (Module.finrank 𝕜 V) := ⟨hdim⟩
    exact seedNumber_isLeast_of_eigenbasis T (spectralList T hT)
      (hT.eigenvectorBasis rfl).toBasis (hT.apply_eigenvectorBasis rfl)

/-- The result concerns the actual image algebra generated by the operator. -/
theorem selfAdjoint_operatorAlgebra_seedRanks
    (T : Module.End 𝕜 V) (hT : T.IsSymmetric) :
    Komorebi.SeedRankBasics.seedFinrank (operatorAlgebra T) V =
        maxEigenMultiplicity (spectralList T hT) ∧
      Komorebi.SeedRankBasics.seedRank (operatorAlgebra T) V =
        (maxEigenMultiplicity (spectralList T hT) : Cardinal) := by
  have h := selfAdjoint_seedNumber_isLeast T hT
  exact ⟨operatorAlgebra_seedFinrank_eq_of_seedNumber_isLeast T _ h,
    operatorAlgebra_seedRank_eq_of_seedNumber_isLeast T _ h⟩

/-- The formula is a maximum of intrinsic eigenspace dimensions. -/
theorem selfAdjoint_seedRank_eq_max_eigenspace_finrank
    (T : Module.End 𝕜 V) (hT : T.IsSymmetric) :
    Komorebi.SeedRankBasics.seedRank (operatorAlgebra T) V =
      ((Finset.univ.sup fun value : EigenLabels (spectralList T hT) ↦
        Module.finrank 𝕜 (Module.End.eigenspace T value.val)) : Cardinal) := by
  rw [(selfAdjoint_operatorAlgebra_seedRanks T hT).2]
  simp only [maxEigenMultiplicity, spectralList_multiplicity_eq_finrank]

end SelfAdjoint

section Matrix
variable {𝕜 : Type u} [RCLike 𝕜] {n : Type v} [Fintype n] [DecidableEq n]

/-- A Hermitian matrix needs no caller-supplied spectral certificate. -/
theorem hermitian_matrix_seedNumber_isLeast
    (A : Matrix n n 𝕜) (hA : A.IsHermitian) :
    IsLeast {r : ℕ | SeedNumberLE A.toEuclideanLin r}
      (maxEigenMultiplicity (spectralList A.toEuclideanLin
        (Matrix.isSymmetric_toEuclideanLin_iff.mpr hA))) :=
  selfAdjoint_seedNumber_isLeast A.toEuclideanLin
    (Matrix.isSymmetric_toEuclideanLin_iff.mpr hA)

/-- In the real case, ordinary matrix symmetry is the sufficient input. -/
theorem real_symmetric_matrix_seedNumber_isLeast
    (A : Matrix n n ℝ) (hA : A.IsSymm) :
    IsLeast {r : ℕ | SeedNumberLE A.toEuclideanLin r}
      (maxEigenMultiplicity (spectralList A.toEuclideanLin
        (Matrix.isSymmetric_toEuclideanLin_iff.mpr
          (Matrix.isHermitian_iff_isSymm.mpr hA)))) :=
  hermitian_matrix_seedNumber_isLeast A (Matrix.isHermitian_iff_isSymm.mpr hA)

end Matrix
end Komorebi.PaperICompletion.SpectralCertificates
