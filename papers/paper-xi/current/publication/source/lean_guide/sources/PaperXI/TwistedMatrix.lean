import PaperXI.TwistedSimple
import Mathlib.RingTheory.SimpleModule.IsAlgClosed
import Mathlib.Analysis.Complex.Polynomial.Basic
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.Data.Nat.Sqrt

/-! The matrix-algebra part of Paper XI, Proposition 8.3. Simplicity is proved
for the constructed twisted algebra before invoking Wedderburn–Artin. No
finite-image condition is imposed on the cocycle. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.TwistedMatrix

open Module CocycleCommutator

/-- A finite-dimensional simple complex algebra has square dimension and an
actual matrix-algebra equivalence of that degree. -/
theorem exists_matrix (R : Type*) [Ring R] [Algebra ℂ R]
    [FiniteDimensional ℂ R] [IsSimpleRing R] :
    ∃ n : ℕ, 0 < n ∧ Module.finrank ℂ R = n ^ 2 ∧
      Nonempty (R ≃ₐ[ℂ] Matrix (Fin n) (Fin n) ℂ) := by
  obtain ⟨n, hn, ⟨e⟩⟩ := IsSimpleRing.exists_algEquiv_matrix_of_isAlgClosed ℂ R
  refine ⟨n, Nat.pos_of_ne_zero (NeZero.ne n), ?_, ⟨e⟩⟩
  simpa [Module.finrank_matrix, pow_two] using e.toLinearEquiv.finrank_eq

/-- The matrix size is the integer square root of the algebra dimension. -/
theorem matrix_sqrt (R : Type*) [Ring R] [Algebra ℂ R]
    [FiniteDimensional ℂ R] [IsSimpleRing R] :
    Nonempty (R ≃ₐ[ℂ]
      Matrix (Fin (Nat.sqrt (Module.finrank ℂ R)))
        (Fin (Nat.sqrt (Module.finrank ℂ R))) ℂ) := by
  obtain ⟨n, _, hd, he⟩ := exists_matrix R
  rw [hd, Nat.sqrt_eq']
  exact he

variable {A : Type*} [CommGroup A] [Fintype A]

/-- Nondegeneracy proves that the order of the index group is a positive square. -/
theorem order_square (c : Cocycle A ℂˣ) (hc : Normalized c)
    (hnd : radical c = ⊥) : ∃ n : ℕ, 0 < n ∧ Fintype.card A = n ^ 2 := by
  let : IsSimpleRing (TwistedAlgebra.Algebra c hc) := TwistedSimple.isSimpleRing c hc hnd
  obtain ⟨n, hn, hd, _⟩ := exists_matrix (TwistedAlgebra.Algebra c hc)
  exact ⟨n, hn, (TwistedAlgebra.finrank_eq_card c hc).symm.trans hd⟩

/-- Proposition 8.3's actual twisted-algebra isomorphism, at the claimed degree. -/
theorem classification (c : Cocycle A ℂˣ) (hc : Normalized c)
    (hnd : radical c = ⊥) :
    Nonempty (TwistedAlgebra.Algebra c hc ≃ₐ[ℂ]
      Matrix (Fin (Nat.sqrt (Fintype.card A))) (Fin (Nat.sqrt (Fintype.card A))) ℂ) := by
  let : IsSimpleRing (TwistedAlgebra.Algebra c hc) := TwistedSimple.isSimpleRing c hc hnd
  rw [← TwistedAlgebra.finrank_eq_card c hc]
  exact matrix_sqrt (TwistedAlgebra.Algebra c hc)

end PaperXI.TwistedMatrix
