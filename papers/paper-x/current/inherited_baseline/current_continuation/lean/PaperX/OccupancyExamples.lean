import PaperX.JointOccupancy

/-! Actual split operators and the rank sequence 3,2,1,0. Every individual
selected eigenvalue is present, but their joint packet can be empty. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.OccupancyExamples

open scoped BigOperators Matrix
open LinearMap Module.End PaperX.SpectralProjectors PaperX.JointOccupancy
attribute [local instance] Classical.propDecidable
universe u v
variable {K : Type u} [Field K] {J : Type v} [Fintype J] [DecidableEq J]

/-- Diagonal coordinate multiplication is an actual linear endomorphism. -/
def diagOp (c : J → K) : Module.End K (J → K) :=
  LinearMap.pi fun j => c j • LinearMap.proj j

omit [Fintype J] [DecidableEq J] in
theorem diag_apply (c x : J → K) (j : J) : diagOp c x j = c j * x j := rfl

theorem diag_basis (c : J → K) (j : J) :
    diagOp c (Pi.basisFun K J j) = c j • Pi.basisFun K J j := by
  ext i
  simp [diagOp, Pi.basisFun_apply, Pi.single_apply]
  split_ifs with h
  · subst i; rfl
  · simp

theorem diag_split (c : J → K) : Split (diagOp c) := by
  apply top_unique
  rw [← (Pi.basisFun K J).span_eq]
  apply Submodule.span_le.mpr
  rintro _ ⟨j,rfl⟩
  exact (le_iSup (fun a : K => (diagOp c).eigenspace a) (c j))
    (mem_eigenspace_iff.mpr (diag_basis c j))

theorem diag_commute (c d : J → K) : Commute (diagOp c) (diagOp d) := by
  ext x j
  simp [Module.End.mul_apply, diag_apply, mul_left_comm]

theorem diag_mul (c d : J → K) : diagOp c * diagOp d = diagOp (fun j => c j * d j) := by
  ext x j
  simp [Module.End.mul_apply, diag_apply, mul_assoc]

theorem diag_one : diagOp (fun _ : J => (1 : K)) = 1 := by
  ext x j
  simp [diag_apply]

theorem spectral_diag (c : J → K) (a : K) :
    spectral (diagOp c) a = diagOp (fun j => if c j = a then 1 else 0) := by
  apply (Pi.basisFun K J).ext
  intro j
  rw [spectral_on_eigenvector _ a (c j) _ (diag_basis c j), diag_basis]
  split_ifs <;> simp

/-- The full diagonal trace calculation, not a rank assigned by definition. -/
theorem trace_diag (c : J → K) : LinearMap.trace K (J → K) (diagOp c) = ∑ j, c j := by
  rw [LinearMap.trace_eq_matrix_trace K (Pi.basisFun K J)]
  simp [Matrix.trace, diag_apply]

/-- Four conditions, all individually feasible. -/
def values : Fin 4 → Fin 4 → ℚ :=
  ![![1,1,1,0], ![2,2,0,0], ![3,0,0,0], ![0,4,4,4]]

def target : Fin 4 → ℚ := ![1,2,3,4]

def operators (i : Fin 4) : Module.End ℚ (Fin 4 → ℚ) := diagOp (values i)

def masks : Fin 4 → Fin 4 → ℚ :=
  ![![1,1,1,0], ![1,1,0,0], ![1,0,0,0], ![0,1,1,1]]

theorem actual_projectors (i : Fin 4) : spectral (operators i) (target i) = diagOp (masks i) := by
  rw [operators, spectral_diag]
  congr 1
  fin_cases i <;> ext j <;> fin_cases j <;> norm_num [values,target,masks]

theorem all_targets_present (i : Fin 4) : (operators i).HasEigenvalue (target i) := by
  have h (j : Fin 4) (hc : values i j = target i) : (operators i).HasEigenvalue (target i) := by
    exact (operators i).hasEigenvalue_of_hasEigenvector
      ⟨mem_eigenspace_iff.mpr (hc ▸ diag_basis (values i) j), (Pi.basisFun ℚ (Fin 4)).ne_zero j⟩
  fin_cases i
  · exact h 0 (by norm_num [values,target])
  · exact h 0 (by norm_num [values,target])
  · exact h 0 (by norm_num [values,target])
  · exact h 1 (by norm_num [values,target])

theorem projector_prefixes :
    joint operators target [0] = diagOp ![1,1,1,0] ∧
    joint operators target [0,1] = diagOp ![1,1,0,0] ∧
    joint operators target [0,1,2] = diagOp ![1,0,0,0] ∧
    joint operators target [0,1,2,3] = 0 := by
  simp only [joint_cons, joint_nil, mul_one, actual_projectors, diag_mul]
  refine ⟨rfl, ?_, ?_, ?_⟩
  · apply congrArg diagOp; decide +kernel
  · apply congrArg diagOp; decide +kernel
  · ext x j; fin_cases j <;> simp [diag_apply,masks]

theorem occupancy_traces :
    LinearMap.trace ℚ (Fin 4 → ℚ) (joint operators target [0]) = 3 ∧
    LinearMap.trace ℚ (Fin 4 → ℚ) (joint operators target [0,1]) = 2 ∧
    LinearMap.trace ℚ (Fin 4 → ℚ) (joint operators target [0,1,2]) = 1 ∧
    LinearMap.trace ℚ (Fin 4 → ℚ) (joint operators target [0,1,2,3]) = 0 := by
  rcases projector_prefixes with ⟨h1,h2,h3,h4⟩
  rw [h1,h2,h3,h4]
  norm_num [trace_diag, Fin.sum_univ_succ]

theorem occupancy_dimensions :
    Module.finrank ℚ (jointSpace operators target [0]) = 3 ∧
    Module.finrank ℚ (jointSpace operators target [0,1]) = 2 ∧
    Module.finrank ℚ (jointSpace operators target [0,1,2]) = 1 ∧
    Module.finrank ℚ (jointSpace operators target [0,1,2,3]) = 0 := by
  have htr := occupancy_traces
  simp only [trace_eq_dimension operators target (fun i => diag_split (values i))
    (fun i j => diag_commute (values i) (values j))] at htr
  exact_mod_cast htr

theorem joint_packet_empty : ¬ Occupied operators target [0,1,2,3] := by
  rw [occupied_iff_trace_ne_zero operators target (fun i => diag_split (values i))
    (fun i j => diag_commute (values i) (values j))]
  simp [occupancy_traces.2.2.2]

theorem smaller_packet_occupied : Occupied operators target [0,1,2] := by
  rw [occupied_iff_trace_ne_zero operators target (fun i => diag_split (values i))
    (fun i j => diag_commute (values i) (values j)), occupancy_traces.2.2.1]
  norm_num

end PaperX.OccupancyExamples
