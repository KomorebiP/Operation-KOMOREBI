import Mathlib.RingTheory.SimpleModule.WedderburnArtin
import Mathlib.RepresentationTheory.AlgebraRepresentation.Basic
import Mathlib.Analysis.Complex.Polynomial.Basic
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.Data.Nat.Sqrt
import Mathlib.Tactic

/-! Actual simple modules over a finite-dimensional simple complex algebra:
uniqueness, automatic finite dimensionality, and the square-root dimension. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.SimpleModuleClassification

variable (R : Type*) [Ring R] [Algebra ℂ R] [FiniteDimensional ℂ R] [IsSimpleRing R]

/-- Any two simple modules over the actual algebra are linearly equivalent as modules. -/
theorem equivalent (M N : Type*) [AddCommGroup M] [Module R M] [IsSimpleModule R M]
    [AddCommGroup N] [Module R N] [IsSimpleModule R N] : Nonempty (M ≃ₗ[R] N) := by
  let : IsArtinianRing R := IsArtinianRing.of_finite ℂ R
  obtain ⟨I, ⟨e⟩⟩ := IsSemisimpleRing.exists_linearEquiv_ideal_of_isSimpleModule R M
  obtain ⟨J, ⟨f⟩⟩ := IsSemisimpleRing.exists_linearEquiv_ideal_of_isSimpleModule R N
  let : IsSimpleModule R I := IsSimpleModule.congr e.symm
  let : IsSimpleModule R J := IsSimpleModule.congr f.symm
  exact ⟨e.trans ((IsSimpleRing.isIsotypic R R J I).some.trans f.symm)⟩

/-- The regular module is a positive finite sum of copies of any given simple module. -/
theorem regular_decomposition (M : Type*) [AddCommGroup M] [Module R M]
    [IsSimpleModule R M] :
    ∃ n : ℕ, 0 < n ∧ Nonempty (R ≃ₗ[R] (Fin n → M)) := by
  let : IsArtinianRing R := IsArtinianRing.of_finite ℂ R
  obtain ⟨n, hn, S, hS, ⟨e⟩⟩ := (IsSimpleRing.isIsotypic R R).linearEquiv_fun
  let f : S ≃ₗ[R] M := (equivalent R S M).some
  exact ⟨n, Nat.pos_of_ne_zero (NeZero.ne n),
    ⟨e.trans (LinearEquiv.piCongrRight (fun _ : Fin n => f))⟩⟩

/-- The algebra has an actual simple left ideal, hence an actual simple module. -/
theorem exists_simple_ideal : ∃ I : Ideal R, IsSimpleModule R I := by
  let : IsArtinianRing R := IsArtinianRing.of_finite ℂ R
  obtain ⟨_, _, I, hI, _⟩ := (IsSimpleRing.isIsotypic R R).linearEquiv_fun
  exact ⟨I, hI⟩

variable (M : Type*) [AddCommGroup M] [Module R M] [Module ℂ M]
variable [IsScalarTower ℂ R M] [IsSimpleModule R M]

/-- The module equivalence restricts to a complex linear equivalence preserving the action. -/
theorem equivalent_complex (N : Type*) [AddCommGroup N] [Module R N] [Module ℂ N]
    [IsScalarTower ℂ R N] [IsSimpleModule R N] :
    ∃ e : M ≃ₗ[ℂ] N, ∀ (r : R) (w : M), e (r • w) = r • e w := by
  obtain ⟨e⟩ := equivalent R M N
  exact ⟨e.restrictScalars ℂ, fun r w => e.map_smul r w⟩

include R in
/-- Finite dimensionality is a conclusion, obtained by identifying a simple module
with an actual ideal of the finite-dimensional algebra. -/
theorem finiteDimensional : FiniteDimensional ℂ M := by
  let : IsArtinianRing R := IsArtinianRing.of_finite ℂ R
  obtain ⟨I, ⟨e⟩⟩ := IsSemisimpleRing.exists_linearEquiv_ideal_of_isSimpleModule R M
  let : FiniteDimensional ℂ I := Module.Finite.of_injective
    (I.subtype.restrictScalars ℂ) I.subtype_injective
  exact (e.restrictScalars ℂ).symm.finiteDimensional

include R in
/-- Simple modules have positive complex dimension. -/
theorem finrank_pos : 0 < Module.finrank ℂ M := by
  let : FiniteDimensional ℂ M := finiteDimensional R M
  let : Nontrivial M := IsSimpleModule.nontrivial R M
  exact Module.finrank_pos

/-- Schur's lemma as an algebra equivalence, after deriving finite dimensionality. -/
def scalarEndEquiv : ℂ ≃ₐ[ℂ] Module.End R M := by
  let : FiniteDimensional ℂ M := finiteDimensional R M
  exact AlgEquiv.ofBijective (Algebra.ofId ℂ (Module.End R M))
    (IsSimpleModule.algebraMap_end_bijective_of_isAlgClosed ℂ)

/-- The actual commuting endomorphism algebra is one-dimensional over the center. -/
theorem finrank_end : Module.finrank ℂ (Module.End R M) = 1 := by
  have h := (scalarEndEquiv R M).toLinearEquiv.finrank_eq
  simpa using h.symm

/-- Every simple module has dimension whose square is the dimension of the algebra. -/
theorem finrank_sq : (Module.finrank ℂ M) ^ 2 = Module.finrank ℂ R := by
  let : FiniteDimensional ℂ M := finiteDimensional R M
  obtain ⟨n, hn, ⟨e⟩⟩ := regular_decomposition R M
  have hregular : Module.finrank ℂ R = n * Module.finrank ℂ M := by
    have h := (e.restrictScalars ℂ).finrank_eq
    simpa [Module.finrank_pi_fintype] using h
  let eEnd : Module.End R R ≃ₐ[ℂ] Matrix (Fin n) (Fin n) (Module.End R M) :=
    (e.conjAlgEquiv ℂ).trans (endVecAlgEquivMatrixEnd (Fin n) ℂ R M)
  let eSelf : Rᵐᵒᵖ ≃ₐ[ℂ] Module.End R R := AlgEquiv.moduleEndSelf ℂ
  have hend : Module.finrank ℂ R = n * n := by
    calc
      Module.finrank ℂ R = Module.finrank ℂ Rᵐᵒᵖ :=
        (MulOpposite.opLinearEquiv ℂ).finrank_eq
      _ = Module.finrank ℂ (Module.End R R) := eSelf.toLinearEquiv.finrank_eq
      _ = Module.finrank ℂ (Matrix (Fin n) (Fin n) (Module.End R M)) :=
        eEnd.toLinearEquiv.finrank_eq
      _ = n * n := by simp [Module.finrank_matrix, finrank_end R M]
  have hdim : Module.finrank ℂ M = n := Nat.eq_of_mul_eq_mul_left hn
    (hregular.symm.trans hend)
  rw [hdim, pow_two, ← hend]

/-- The positive simple-module dimension is the natural square root of the algebra dimension. -/
theorem finrank_sqrt : Module.finrank ℂ M = Nat.sqrt (Module.finrank ℂ R) := by
  rw [← finrank_sq R M, Nat.sqrt_eq']

end PaperXI.SimpleModuleClassification
