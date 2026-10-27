module
public import Mathlib.LinearAlgebra.Matrix.Rank
public import Mathlib.LinearAlgebra.Dimension.Constructions
public import Mathlib.LinearAlgebra.Pi
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Tactic

public section
set_option autoImplicit false
set_option linter.unusedSectionVars false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
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
  constructor
  · rintro ⟨A, rfl⟩ i
    exact ⟨A i, rfl⟩
  · intro h
    have h' : ∀ i, ∃ a : d → ℂ, a ᵥ* C = X i := h
    choose A hA using h'
    exact ⟨A, funext hA⟩

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


/-! Actual multi-seed matrix action and the sharp generator count. -/
variable {o k : Type*} [Fintype o] [Fintype k]
noncomputable def rowOrbit (C : Matrix d m ℂ) (o : Type*) : Submodule ℂ (o → m → ℂ) :=
  LinearMap.range (C.vecMulLinear.compLeft o)

theorem rowOrbit_mem (C : Matrix d m ℂ) (X : o → m → ℂ) :
    X ∈ rowOrbit C o ↔ ∀ i, X i ∈ rowSpace C := by
  constructor
  · rintro ⟨A, rfl⟩ i
    exact ⟨A i, rfl⟩
  · intro h
    have h' : ∀ i, ∃ a : d → ℂ, a ᵥ* C = X i := h
    choose A hA using h'
    exact ⟨A, funext hA⟩

noncomputable def rowOrbitEquiv (C : Matrix d m ℂ) :
    rowOrbit C o ≃ₗ[ℂ] (o → rowSpace C) where
  toFun X i := ⟨X.val i, (rowOrbit_mem C X.val).mp X.property i⟩
  invFun f := ⟨fun i => (f i).val, (rowOrbit_mem C _).mpr (fun i => (f i).property)⟩
  left_inv _ := rfl
  right_inv _ := rfl
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

theorem rowOrbit_dimension (C : Matrix d m ℂ) :
    finrank ℂ (rowOrbit C o) = Fintype.card o * C.rank := by
  rw [(rowOrbitEquiv (o := o) C).finrank_eq, Module.finrank_pi_fintype]
  simp [row_dimension]

theorem rowOrbit_full [Nonempty o] (C : Matrix d m ℂ) :
    rowOrbit C o = ⊤ ↔ C.rank = Fintype.card m := by
  rw [Submodule.eq_top_iff_finrank_eq, rowOrbit_dimension]
  simp only [Module.finrank_pi_fintype, Finset.sum_const,
    Finset.card_univ, smul_eq_mul, Module.finrank_self, mul_one]
  exact Nat.mul_left_cancel_iff (Fintype.card_pos (α := o))

def stackSeeds (C : k → Matrix d m ℂ) : Matrix (k × d) m ℂ := fun q j => C q.1 q.2 j

/-- The explicit k-seed action, allowing a different algebra element on each seed. -/
def Generates (C : k → Matrix d m ℂ) : Prop :=
  ∀ X : Matrix d m ℂ, ∃ A : k → Matrix d d ℂ, ∑ a, A a * C a = X

theorem stacked_action (C : k → Matrix d m ℂ) (A : k → Matrix d d ℂ) :
    (show Matrix d (k × d) ℂ from fun i q => A q.1 i q.2) * stackSeeds C = ∑ a, A a * C a := by
  ext i j
  simp [Matrix.mul_apply, stackSeeds, Fintype.sum_prod_type]

theorem generates_iff_rowOrbit (C : k → Matrix d m ℂ) :
    Generates C ↔ rowOrbit (stackSeeds C) d = ⊤ := by
  rw [Submodule.eq_top_iff']
  constructor
  · intro h X
    obtain ⟨A, hA⟩ := h X
    exact ⟨fun i q => A q.1 i q.2, (stacked_action C A).trans hA⟩
  · intro h X
    obtain ⟨A, hA⟩ := h X
    refine ⟨fun a i r => A i (a,r), ?_⟩
    rw [← stacked_action]
    exact hA

theorem generates_iff_rank [Nonempty d] (C : k → Matrix d m ℂ) :
    Generates C ↔ (stackSeeds C).rank = Fintype.card m := by
  rw [generates_iff_rowOrbit, rowOrbit_full]

theorem seed_count_lower [Nonempty d] (C : k → Matrix d m ℂ) (h : Generates C) :
    Fintype.card m ≤ Fintype.card k * Fintype.card d := by
  rw [← (generates_iff_rank C).mp h, ← Fintype.card_prod]
  exact (stackSeeds C).rank_le_card_height

/-- Realizes every attainable full column rank by an explicit coordinate embedding. -/
theorem exists_full_column_rank (h : Fintype.card m ≤ Fintype.card d) :
    ∃ C : Matrix d m ℂ, C.rank = Fintype.card m := by
  classical
  obtain ⟨f⟩ := Function.Embedding.nonempty_of_card_le h
  let C : Matrix d m ℂ := fun i j => if i=f j then 1 else 0
  have hC (x : m → ℂ) (j : m) : (C *ᵥ x) (f j) = x j := by
    simp [C, Matrix.mulVec, dotProduct, f.injective.eq_iff]
  have hi : Function.Injective C.mulVecLin := by
    intro x y hxy
    funext j
    have h := congrFun hxy (f j)
    simpa only [Matrix.mulVecLin_apply, hC] using h
  refine ⟨C, ?_⟩
  rw [Matrix.rank, LinearMap.finrank_range_of_inj hi, Module.finrank_pi]

theorem exists_generating_seeds_iff [Nonempty d] :
    (∃ C : k → Matrix d m ℂ, Generates C) ↔
      Fintype.card m ≤ Fintype.card k * Fintype.card d := by
  constructor
  · rintro ⟨C, hC⟩
    exact seed_count_lower C hC
  · intro h
    obtain ⟨D, hD⟩ := exists_full_column_rank (d := k × d) (m := m)
      (by simpa using h)
    refine ⟨fun a i j => D (a,i) j, (generates_iff_rank _).mpr ?_⟩
    exact hD

end KomorebiPaperVII.SeedOrbit
