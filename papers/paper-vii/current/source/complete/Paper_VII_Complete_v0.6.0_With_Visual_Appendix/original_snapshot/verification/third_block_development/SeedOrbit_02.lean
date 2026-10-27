module
public import Mathlib.LinearAlgebra.Matrix.Rank
public import Mathlib.LinearAlgebra.Dimension.Constructions
public import Mathlib.LinearAlgebra.Pi
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Tactic

public section
set_option autoImplicit false
set_option linter.unusedSectionVars false
namespace KomorebiPaperVII.SeedOrbit
open Matrix Module
variable {d m : Type*} [Fintype d] [Fintype m]

/-- The row space is the actual image of right multiplication by C. -/
noncomputable def rowSpace (C : Matrix d m ℂ) : Submodule ℂ (m → ℂ) :=
  LinearMap.range C.vecMulLinear

/-- Actual algebra orbit. It is already a linear subspace. -/
noncomputable def orbitSpace (C : Matrix d m ℂ) : Submodule ℂ (Matrix d m ℂ) :=
  LinearMap.range (C.vecMulLinear.compLeft d)

theorem mem_orbit_iff (C X : Matrix d m ℂ) :
    X ∈ orbitSpace C ↔ ∃ A : Matrix d d ℂ, A * C = X := by
  rfl

theorem mem_orbit_iff_rows (C X : Matrix d m ℂ) :
    X ∈ orbitSpace C ↔ ∀ i, X i ∈ rowSpace C := by
  rw [orbitSpace, LinearMap.range_compLeft]
  simp only [Submodule.mem_pi, Set.mem_univ, forall_true_left, rowSpace]

noncomputable def orbitRowEquiv (C : Matrix d m ℂ) :
    orbitSpace C ≃ₗ[ℂ] (d → rowSpace C) where
  toFun X i := ⟨X.val i, (mem_orbit_iff_rows C X.val).mp X.property i⟩
  invFun f := ⟨fun i => (f i).val, (mem_orbit_iff_rows C _).mpr (fun i => (f i).property)⟩
  left_inv _ := rfl
  right_inv _ := rfl
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

theorem row_dimension (C : Matrix d m ℂ) :
    finrank ℂ (rowSpace C) = C.rank := by
  rw [rowSpace, range_vecMulLinear, ← Matrix.rank_eq_finrank_span_row]

theorem orbit_dimension (C : Matrix d m ℂ) :
    finrank ℂ (orbitSpace C) = Fintype.card d * C.rank := by
  rw [(orbitRowEquiv C).finrank_eq, Module.finrank_pi_fintype]
  simp [row_dimension]

theorem orbit_span (C : Matrix d m ℂ) :
    Submodule.span ℂ (Set.range fun A : Matrix d d ℂ => A * C) = orbitSpace C := by
  change Submodule.span ℂ (orbitSpace C : Set (Matrix d m ℂ)) = orbitSpace C
  exact Submodule.span_eq _

theorem span_orbit_dimension (C : Matrix d m ℂ) :
    finrank ℂ (Submodule.span ℂ (Set.range fun A : Matrix d d ℂ => A * C)) =
      Fintype.card d * C.rank := by
  rw [orbit_span, orbit_dimension]

theorem cyclic_iff_full_rank [Nonempty d] (C : Matrix d m ℂ) :
    orbitSpace C = ⊤ ↔ C.rank = Fintype.card m := by
  rw [Submodule.eq_top_iff_finrank_eq, orbit_dimension]
  have hdim : finrank ℂ (Matrix d m ℂ) = Fintype.card d * Fintype.card m := by
    change finrank ℂ (d → m → ℂ) = _
    simp [Module.finrank_pi_fintype]
  rw [hdim]
  exact Nat.mul_left_cancel_iff (Fintype.card_pos)

theorem cyclic_multiplicity_bound [Nonempty d] (C : Matrix d m ℂ)
    (h : orbitSpace C = ⊤) : Fintype.card m ≤ Fintype.card d := by
  rw [← (cyclic_iff_full_rank C).mp h]
  exact C.rank_le_card_height

end KomorebiPaperVII.SeedOrbit
