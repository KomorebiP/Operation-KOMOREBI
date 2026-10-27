import KomorebiLSM.TreeEnergy
import KomorebiLSM.PredictiveCompletion
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.FinCases

/-! Exact finite-tree selections and a proper predictive completion.
The three-coordinate example keeps the dynamically relevant first two
coordinates and genuinely omits the third. -/
set_option autoImplicit false
open scoped BigOperators
namespace Komorebi.LSM.Block2Examples
open Module PacketTree

/-- Four leaves, with two internal children. -/
abbrev balancedTree : PacketTree := .branch 1 (fun _ => .branch 1 (fun _ => .leaf))

/-- Select the left internal node and both right leaves. -/
def mixedCut : Node balancedTree → Bool
  | .inl _ => false
  | .inr ⟨i, .inl _⟩ => decide (i = 0)
  | .inr ⟨i, .inr _⟩ => decide (i = 1)

theorem mixed_depth_cut_complete : IsCompleteCut balancedTree mixedCut := by
  rintro ⟨i, j, u⟩
  cases u
  fin_cases i <;> fin_cases j <;> rfl

/-- On the all-one selection each path contains three selected nodes. -/
theorem selecting_ancestors_and_descendants_is_not_a_cut :
    ¬ IsCompleteCut balancedTree (fun _ => true) := by
  intro h
  have hh := h ⟨0, 0, ()⟩
  norm_num [pathCount, balancedTree] at hh

/-- Deleting the only terminal node leaves an uncovered path. -/
theorem deleting_a_branch_is_not_a_cut :
    ¬ IsCompleteCut (.branch 1 (fun _ => .leaf))
      (fun v => match v with | .inl _ => false | .inr p => decide (p.1 = 0)) := by
  intro h
  have hh := h ⟨1, ()⟩
  norm_num [pathCount] at hh

/-- The mixed cut has three selected nodes, not four leaves. -/
theorem mixed_depth_selected_count :
    selectedSum balancedTree mixedCut (fun _ => (1 : ℕ)) = 3 := by
  norm_num [selectedSum, nodeSum, balancedTree, mixedCut, Fin.sum_univ_succ]

/-- A conservative mass label reconstructs across mixed depths. -/
def treeMass : Node balancedTree → ℕ
  | .inl _ => 10
  | .inr ⟨i, .inl _⟩ => if i = 0 then 3 else 7
  | .inr ⟨i, .inr ⟨j, _⟩⟩ => if i = 0 then (if j = 0 then 1 else 2)
      else (if j = 0 then 3 else 4)

theorem treeMass_conservative : Conservative balancedTree treeMass := by
  constructor
  · norm_num [treeMass, root, Fin.sum_univ_succ]
  · intro i
    fin_cases i <;> constructor
    all_goals simp [Conservative, treeMass, Fin.sum_univ_succ]

theorem mixed_depth_mass_reconstruction : selectedSum balancedTree mixedCut treeMass = 10 :=
  selectedSum_eq_root balancedTree mixedCut treeMass mixed_depth_cut_complete treeMass_conservative

/-- Additive conservation alone does not imply energy conservation. -/
theorem nonorthogonal_split_breaks_energy :
    ((1/2 : ℝ) + 1/2 = 1) ∧ ‖(1/2 : ℝ)‖^2 + ‖(1/2 : ℝ)‖^2 ≠ ‖(1 : ℝ)‖^2 := by
  norm_num

abbrev Signal := ℚ × ℚ × ℚ

def signalTransition : Signal →ₗ[ℚ] Signal where
  toFun x := (x.1/2 + x.2.1, x.1/4 + x.2.1/3, (5/6)*x.2.2)
  map_add' := by intro x y; ext <;> simp <;> ring
  map_smul' := by intro a x; ext <;> simp <;> ring

def firstRow : Dual ℚ Signal := LinearMap.fst ℚ ℚ (ℚ × ℚ)
def secondRow : Dual ℚ Signal := (LinearMap.fst ℚ ℚ ℚ).comp (LinearMap.snd ℚ ℚ (ℚ × ℚ))
def thirdRow : Dual ℚ Signal := (LinearMap.snd ℚ ℚ ℚ).comp (LinearMap.snd ℚ ℚ (ℚ × ℚ))

def initialRows : Submodule ℚ (Dual ℚ Signal) := Submodule.span ℚ {firstRow}
def relevantRows : Submodule ℚ (Dual ℚ Signal) := LinearMap.ker (Dual.eval ℚ Signal (0,0,1))
noncomputable def completedRows : Submodule ℚ (Dual ℚ Signal) :=
  predictiveCompletion (fun _ : Unit => signalTransition) initialRows

theorem first_row_initial : firstRow ∈ initialRows := Submodule.subset_span (by simp)

theorem initial_rows_relevant : initialRows ≤ relevantRows := by
  apply Submodule.span_le.mpr
  intro f hf
  have he : f = firstRow := by simpa using hf
  subst f
  rfl

theorem relevant_rows_invariant :
    CommonInvariant (fun _ : Unit => signalTransition.dualMap) relevantRows := by
  intro i w hw
  obtain ⟨f, hf, rfl⟩ := Submodule.mem_map.mp hw
  change f (signalTransition (0,0,1)) = 0
  have hv : f (0,0,1) = 0 := hf
  have he : signalTransition (0,0,1) = (5/6 : ℚ) • (0,0,1) := by
    norm_num [signalTransition]
  rw [he, map_smul, hv, smul_zero]

theorem completion_omits_irrelevant_direction : completedRows ≤ relevantRows :=
  invariantCompletion_minimal _ _ _ initial_rows_relevant relevant_rows_invariant

theorem first_row_completed : firstRow ∈ completedRows :=
  initial_le_invariantCompletion _ _ first_row_initial

theorem pullback_creates_second_row :
    signalTransition.dualMap firstRow - (1/2 : ℚ) • firstRow = secondRow := by
  apply LinearMap.ext
  intro x
  simp [signalTransition, firstRow, secondRow]
  ring

theorem second_row_completed : secondRow ∈ completedRows := by
  have hinv : CommonInvariant (fun _ : Unit => signalTransition.dualMap) completedRows :=
    invariantCompletion_invariant _ _
  have hp : signalTransition.dualMap firstRow ∈ completedRows :=
    hinv () (Submodule.mem_map.mpr ⟨firstRow, first_row_completed, rfl⟩)
  rw [← pullback_creates_second_row]
  exact completedRows.sub_mem hp (completedRows.smul_mem _ first_row_completed)

theorem relevant_row_decomposition (f : Dual ℚ Signal) (hf : f ∈ relevantRows) :
    f = f (1,0,0) • firstRow + f (0,1,0) • secondRow := by
  have hz : f (0,0,1) = 0 := hf
  apply LinearMap.ext
  intro x
  have hx : x = x.1 • (1,0,0) + x.2.1 • (0,1,0) + x.2.2 • (0,0,1) := by
    ext <;> simp
  have hfx := congrArg f hx
  simp only [map_add, map_smul, hz, smul_eq_mul, mul_zero, add_zero] at hfx
  change f x = f (1,0,0) * x.1 + f (0,1,0) * x.2.1
  rw [hfx]
  ring

theorem completion_is_exactly_two_coordinate_rows : completedRows = relevantRows := by
  apply le_antisymm completion_omits_irrelevant_direction
  intro f hf
  rw [relevant_row_decomposition f hf]
  exact completedRows.add_mem (completedRows.smul_mem _ first_row_completed)
    (completedRows.smul_mem _ second_row_completed)

theorem third_row_not_completed : thirdRow ∉ completedRows := by
  intro h
  have hr := completion_omits_irrelevant_direction h
  change thirdRow (0,0,1) = 0 at hr
  norm_num [thirdRow] at hr

theorem completion_is_proper : completedRows ≠ ⊤ := by
  intro h
  exact third_row_not_completed (h ▸ Submodule.mem_top)

theorem first_coordinate_not_closed :
    ¬ ∃ F : ℚ → ℚ, ∀ x : Signal, F (firstRow x) = firstRow (signalTransition x) := by
  rintro ⟨F, h⟩
  have h0 := h (0,0,0)
  have h1 := h (0,1,0)
  norm_num [firstRow, signalTransition] at h0 h1
  exact (by norm_num : (0 : ℚ) ≠ 1) (h0.symm.trans h1)

/-- With no declared operations, no observable enrichment is needed. -/
theorem empty_family_completion (V : Type*) [AddCommGroup V] [Module ℚ V]
    (W : Submodule ℚ V) : invariantCompletion (fun i : Empty => i.elim) W = W := by
  apply le_antisymm
  · exact invariantCompletion_minimal _ _ W le_rfl (fun i => i.elim)
  · exact initial_le_invariantCompletion _ _

end Komorebi.LSM.Block2Examples
