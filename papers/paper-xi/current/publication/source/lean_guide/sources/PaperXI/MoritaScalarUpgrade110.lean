import PaperXI.MoritaLattice110
import Mathlib.RingTheory.Finiteness.Basic
import Mathlib.Algebra.Module.Submodule.RestrictScalars

/-! Finite generation passes from a genuine base-integer lattice to the same
carrier with extension-integer scalars. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.MoritaScalarUpgrade110
open Matrix PaperXI.MoritaLattice110

section StableSubmodule
variable {R S M : Type*} [Semiring R] [Semiring S] [AddCommGroup M]
  [Module R M] [Module S M] [SMul R S] [IsScalarTower R S M]

/-- The same actual additive lattice, with larger scalars proved to preserve it. -/
def upgrade (L : Submodule R M) (hstable : ∀ s : S, ∀ x ∈ L, s • x ∈ L) :
    Submodule S M where
  carrier := (L : Set M)
  zero_mem' := L.zero_mem
  add_mem' := L.add_mem
  smul_mem' s {x} hx := hstable s x hx

@[simp] theorem upgrade_restrictScalars (L : Submodule R M)
    (hstable : ∀ s : S, ∀ x ∈ L, s • x ∈ L) :
    (upgrade L hstable).restrictScalars R = L := by ext x; rfl

/-- A finite generating set of the original lattice also generates it over the
larger ring; no free basis or rank is supplied as a premise. -/
theorem upgrade_fg (L : Submodule R M)
    (hstable : ∀ s : S, ∀ x ∈ L, s • x ∈ L) (hfg : L.FG) :
    (upgrade L hstable).FG := by
  exact Submodule.FG.of_restrictScalars R (by simpa using hfg)

end StableSubmodule

section MatrixStability
variable {S D m : Type*} [Ring S] [Ring D] [Module S D]
  [Fintype m] [DecidableEq m]

/-- Extension-integer scalar stability follows from the actual maximal-order
matrix bimodule through its scalar matrices. -/
theorem scalar_stable_of_matrix_bimodule (φ : S →+* D)
    (hsmul : ∀ (s : S) (x : D), s • x = φ s * x)
    (L : AddSubgroup (Matrix m m D)) (hL : IsMatrixBimodule φ L) :
    ∀ s : S, ∀ x ∈ L, s • x ∈ L := by
  intro s x hx
  have h := hL.1 (Matrix.scalar m s) x hx
  have he : (Matrix.scalar m s).map φ * x = s • x := by
    ext i j
    simp [Matrix.scalar_apply, Matrix.diagonal_map, Matrix.diagonal_mul, hsmul]
  rwa [he] at h

end MatrixStability
end PaperXI.MoritaScalarUpgrade110
