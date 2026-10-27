module
public import Mathlib.LinearAlgebra.Matrix.Rank
public import Mathlib.LinearAlgebra.Dimension.Constructions
public import Mathlib.LinearAlgebra.Pi
public import Mathlib.Analysis.Complex.Basic
public import Mathlib.Algebra.Order.Floor.Div
public import Mathlib.LinearAlgebra.Matrix.Kronecker
public import Mathlib.Analysis.Matrix.PosDef
public import Mathlib.Tactic

public section
set_option autoImplicit false
set_option linter.unusedSectionVars false
set_option backward.isDefEq.respectTransparency false
set_option backward.isDefEq.respectTransparency.types false
namespace KomorebiPaperVII.SeedOrbit
open Matrix Module
open scoped Kronecker
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
  simp [Matrix.sum_apply, Matrix.mul_apply, stackSeeds, Fintype.sum_prod_type]

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

/-! Direct sums: actual simultaneous block action and its minimum seed cardinality. -/
section Blocks
variable {I : Type*} [Fintype I]

def BlockGenerates (dd mm : I → ℕ) {s : ℕ}
    (C : Fin s → (i : I) → Matrix (Fin (dd i)) (Fin (mm i)) ℂ) : Prop :=
  ∀ X : (i : I) → Matrix (Fin (dd i)) (Fin (mm i)) ℂ,
    ∃ A : Fin s → (i : I) → Matrix (Fin (dd i)) (Fin (dd i)) ℂ,
      ∀ i, ∑ a, A a i * C a i = X i

theorem block_generates_iff (dd mm : I → ℕ) {s : ℕ}
    (C : Fin s → (i : I) → Matrix (Fin (dd i)) (Fin (mm i)) ℂ) :
    BlockGenerates dd mm C ↔ ∀ i, Generates (fun a => C a i) := by
  classical
  constructor
  · intro h i Y
    let X : (j : I) → Matrix (Fin (dd j)) (Fin (mm j)) ℂ :=
      fun j => if hji : j=i then hji.symm ▸ Y else 0
    obtain ⟨A, hA⟩ := h X
    exact ⟨fun a => A a i, by simpa [X] using hA i⟩
  · intro h X
    have hi := fun i => h i (X i)
    choose A hA using hi
    exact ⟨fun a i => A i a, hA⟩

theorem exists_block_seeds_iff (dd mm : I → ℕ) (hd : ∀ i, 0 < dd i) (s : ℕ) :
    (∃ C : Fin s → (i : I) → Matrix (Fin (dd i)) (Fin (mm i)) ℂ,
      BlockGenerates dd mm C) ↔ ∀ i, mm i ≤ s * dd i := by
  classical
  constructor
  · rintro ⟨C, hC⟩ i
    let : Nonempty (Fin (dd i)) := Fin.pos_iff_nonempty.mp (hd i)
    simpa using seed_count_lower (fun a => C a i) ((block_generates_iff dd mm C).mp hC i)
  · intro h
    have hi (i : I) : ∃ C : Fin s → Matrix (Fin (dd i)) (Fin (mm i)) ℂ,
        Generates C := by
      let : Nonempty (Fin (dd i)) := Fin.pos_iff_nonempty.mp (hd i)
      exact exists_generating_seeds_iff.mpr (by simpa using h i)
    choose C hC using hi
    exact ⟨fun a i => C i a, (block_generates_iff dd mm _).mpr hC⟩

noncomputable def seedRankFormula (dd mm : I → ℕ) : ℕ :=
  Finset.univ.sup (fun i => mm i ⌈/⌉ dd i)

theorem seed_formula_le_iff (dd mm : I → ℕ) (hd : ∀ i, 0 < dd i) (s : ℕ) :
    seedRankFormula dd mm ≤ s ↔ ∀ i, mm i ≤ s * dd i := by
  simp only [seedRankFormula, Finset.sup_le_iff, Finset.mem_univ, forall_true_left]
  constructor
  · intro h i
    simpa only [Nat.mul_comm] using (ceilDiv_le_iff_le_mul (hd i)).mp (h i)
  · intro h i
    exact (ceilDiv_le_iff_le_mul (hd i)).mpr (by simpa only [Nat.mul_comm] using h i)

/-- Sharp minimum, with existence witnessed by explicit matrix seeds. -/
theorem quantum_seed_rank (dd mm : I → ℕ) (hd : ∀ i, 0 < dd i) :
    IsLeast {s : ℕ | ∃ C : Fin s → (i : I) → Matrix (Fin (dd i)) (Fin (mm i)) ℂ,
      BlockGenerates dd mm C} (seedRankFormula dd mm) := by
  constructor
  · exact (exists_block_seeds_iff dd mm hd _).mpr
      ((seed_formula_le_iff dd mm hd _).mp le_rfl)
  · intro s hs
    exact (seed_formula_le_iff dd mm hd s).mpr ((exists_block_seeds_iff dd mm hd s).mp hs)
end Blocks


/-! Bipartite tensor coefficients, minimum product length, and actual partial trace. -/

/-- Coefficients in the product of the two standard orthonormal bases. -/
def coefficientEquiv : (d × m → ℂ) ≃ₗ[ℂ] Matrix d m ℂ where
  toFun psi i j := psi (i,j)
  invFun C q := C q.1 q.2
  left_inv _ := rfl
  right_inv _ := rfl
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

theorem local_tensor_action [DecidableEq m] (A : Matrix d d ℂ) (psi : d × m → ℂ) :
    coefficientEquiv ((A ⊗ₖ (1 : Matrix m m ℂ)) *ᵥ psi) = A * coefficientEquiv psi := by
  ext i j
  simp [coefficientEquiv, Matrix.mulVec, dotProduct,
    Fintype.sum_prod_type, Matrix.one_apply, Matrix.mul_apply]

/-- A sum of s genuine product vectors, not a rank assumption. -/
def HasProductDecomposition (C : Matrix d m ℂ) (s : ℕ) : Prop :=
  ∃ u : Fin s → d → ℂ, ∃ v : Fin s → m → ℂ,
    ∀ i j, C i j = ∑ a, u a i * v a j

theorem product_decomposition_rank_bound (C : Matrix d m ℂ) {s : ℕ}
    (h : HasProductDecomposition C s) : C.rank ≤ s := by
  obtain ⟨u, v, h⟩ := h
  let U : Matrix d (Fin s) ℂ := fun i a => u a i
  let V : Matrix (Fin s) m ℂ := v
  have hc : C = U * V := by ext i j; exact h i j
  rw [hc]
  exact (Matrix.rank_mul_le_right U V).trans (by simpa using V.rank_le_card_height)

noncomputable def rowVector (C : Matrix d m ℂ) (i : d) : rowSpace C := by
  classical
  refine ⟨C i, Pi.single i 1, ?_⟩
  change Pi.single i 1 ᵥ* C = C i
  rw [Matrix.single_vecMul, one_smul]
  rfl

/-- Constructs a minimum-length product decomposition using a row-space basis. -/
theorem product_decomposition_at_rank (C : Matrix d m ℂ) : HasProductDecomposition C C.rank := by
  classical
  let b := Module.finBasisOfFinrankEq ℂ (rowSpace C) (row_dimension C)
  refine ⟨fun a i => b.repr (rowVector C i) a, fun a j => (b a).val j, ?_⟩
  intro i j
  have h := congrArg (fun x : rowSpace C => x.val j) (b.sum_repr (rowVector C i))
  simpa only [rowVector, Submodule.coe_sum, Submodule.coe_smul, Finset.sum_apply, Pi.smul_apply,
    smul_eq_mul] using h.symm

theorem product_length_minimum (C : Matrix d m ℂ) :
    IsLeast {s : ℕ | HasProductDecomposition C s} C.rank := by
  exact ⟨product_decomposition_at_rank C, fun _ h => product_decomposition_rank_bound C h⟩

/-- Schmidt rank defined independently as the least number of product-vector summands. -/
noncomputable def schmidtRank (psi : d × m → ℂ) : ℕ := by
  classical
  exact Nat.find (show ∃ s, HasProductDecomposition (coefficientEquiv psi) s from
    ⟨_, product_decomposition_at_rank _⟩)

theorem schmidt_rank_eq_matrix_rank (psi : d × m → ℂ) :
    schmidtRank psi = (coefficientEquiv psi).rank := by
  classical
  unfold schmidtRank
  apply le_antisymm
  · exact Nat.find_min' _ (product_decomposition_at_rank _)
  · exact product_decomposition_rank_bound _ (Nat.find_spec _)

noncomputable def localOrbit (psi : d × m → ℂ) : Submodule ℂ (d × m → ℂ) :=
  (orbitSpace (coefficientEquiv psi)).map coefficientEquiv.symm.toLinearMap

theorem local_orbit_is_tensor_span [DecidableEq m] (psi : d × m → ℂ) :
    localOrbit psi = Submodule.span ℂ
      (Set.range fun A : Matrix d d ℂ => (A ⊗ₖ (1 : Matrix m m ℂ)) *ᵥ psi) := by
  rw [localOrbit, ← orbit_span, Submodule.map_span, ← Set.range_comp]
  congr 2
  funext A
  apply coefficientEquiv.injective
  simpa using (local_tensor_action A psi).symm

theorem local_orbit_schmidt_dimension (psi : d × m → ℂ) :
    finrank ℂ (localOrbit psi) = Fintype.card d * schmidtRank psi := by
  rw [localOrbit, LinearEquiv.finrank_map_eq, orbit_dimension, schmidt_rank_eq_matrix_rank]

/-- The actual B-reduced matrix obtained by tracing the A-index of |psi><psi|. -/
def reducedB (psi : d × m → ℂ) : Matrix m m ℂ :=
  fun j l => ∑ i, psi (i,j) * star (psi (i,l))

theorem partial_trace_gram (psi : d × m → ℂ) :
    reducedB psi = (coefficientEquiv psi)ᵀ * ((coefficientEquiv psi)ᵀ)ᴴ := by
  ext j l
  rfl

open scoped ComplexOrder

theorem reduced_rank_eq_schmidt (psi : d × m → ℂ) :
    (reducedB psi).rank = schmidtRank psi := by
  rw [partial_trace_gram, Matrix.rank_self_mul_conjTranspose,
    Matrix.rank_transpose, schmidt_rank_eq_matrix_rank]

theorem reduced_positive (psi : d × m → ℂ) : (reducedB psi).PosSemidef := by
  rw [partial_trace_gram]
  exact Matrix.posSemidef_self_mul_conjTranspose _

theorem reduced_full_support_iff (psi : d × m → ℂ) :
    LinearMap.range (reducedB psi).mulVecLin = ⊤ ↔ schmidtRank psi = Fintype.card m := by
  rw [Submodule.eq_top_iff_finrank_eq, ← Matrix.rank, reduced_rank_eq_schmidt,
    Module.finrank_pi]

theorem local_orbit_full_iff [Nonempty d] (psi : d × m → ℂ) :
    localOrbit psi = ⊤ ↔ schmidtRank psi = Fintype.card m := by
  rw [Submodule.eq_top_iff_finrank_eq, local_orbit_schmidt_dimension, Module.finrank_pi,
    Fintype.card_prod]
  exact Nat.mul_left_cancel_iff (Fintype.card_pos (α := d))

/-- Full local controllability of the state orbit iff the actual reduced state has full support. -/
theorem local_orbit_reduced_support [Nonempty d] (psi : d × m → ℂ) :
    localOrbit psi = ⊤ ↔ LinearMap.range (reducedB psi).mulVecLin = ⊤ := by
  rw [local_orbit_full_iff, reduced_full_support_iff]

end KomorebiPaperVII.SeedOrbit
