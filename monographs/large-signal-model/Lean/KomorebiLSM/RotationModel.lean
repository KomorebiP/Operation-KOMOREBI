import KomorebiLSM.BehaviorProbability
import Mathlib.Analysis.SpecialFunctions.Sqrt
import Mathlib.Tactic

/-! The exact rational controlled rotation process in Proposition 46.
The three coordinates are mass and two signed spatial coordinates. -/
set_option autoImplicit false
namespace Komorebi.LSM.RotationModel
open scoped BigOperators
open FiniteInstruments

abbrev State := Fin 3 → ℝ

noncomputable def mass : State →ₗ[ℝ] ℝ := LinearMap.proj 0

def initial : State := ![1,1,0]

noncomputable def rotationMatrix : Matrix (Fin 3) (Fin 3) ℝ :=
  !![1,0,0; 0,3/5,-4/5; 0,4/5,3/5]

noncomputable def probeMatrix0 : Matrix (Fin 3) (Fin 3) ℝ :=
  !![1/2,1/2,0; 1/2,1/2,0; 0,0,0]

noncomputable def probeMatrix1 : Matrix (Fin 3) (Fin 3) ℝ :=
  !![1/2,-1/2,0; 1/2,-1/2,0; 0,0,0]

/-- Exact rational matrices whose real casts define the process. -/
def rotationMatrixQ : Matrix (Fin 3) (Fin 3) ℚ :=
  !![1,0,0; 0,3/5,-4/5; 0,4/5,3/5]
def probeMatrix0Q : Matrix (Fin 3) (Fin 3) ℚ :=
  !![1/2,1/2,0; 1/2,1/2,0; 0,0,0]
def probeMatrix1Q : Matrix (Fin 3) (Fin 3) ℚ :=
  !![1/2,-1/2,0; 1/2,-1/2,0; 0,0,0]

noncomputable def rotate : State →ₗ[ℝ] State := rotationMatrix.mulVecLin
noncomputable def probe0 : State →ₗ[ℝ] State := probeMatrix0.mulVecLin
noncomputable def probe1 : State →ₗ[ℝ] State := probeMatrix1.mulVecLin

noncomputable def matrix (s : Bool × Bool) : Matrix (Fin 3) (Fin 3) ℝ :=
  if s.1 then (if s.2 then probeMatrix1 else probeMatrix0)
  else (if s.2 then 0 else rotationMatrix)

noncomputable def operator (s : Bool × Bool) : State →ₗ[ℝ] State :=
  if s.1 then (if s.2 then probe1 else probe0)
  else (if s.2 then 0 else rotate)

@[simp] theorem operator_rotate0 : operator (false,false) = rotate := rfl
@[simp] theorem operator_rotate1 : operator (false,true) = 0 := rfl
@[simp] theorem operator_probe0 : operator (true,false) = probe0 := rfl
@[simp] theorem operator_probe1 : operator (true,true) = probe1 := rfl

theorem operator_matrix (s : Bool × Bool) : operator s = (matrix s).mulVecLin := by
  rcases s with ⟨a,o⟩
  cases a <;> cases o <;> simp [operator,matrix,rotate,probe0,probe1]

@[simp] theorem mass_apply (z : State) : mass z = z 0 := rfl

@[simp] theorem rotate_apply (z : State) :
    rotate z = ![z 0, (3/5:ℝ)*z 1-(4/5:ℝ)*z 2, (4/5:ℝ)*z 1+(3/5:ℝ)*z 2] := by
  ext i
  fin_cases i <;> simp [rotate,rotationMatrix,Matrix.mulVec,dotProduct,Fin.sum_univ_succ,sub_eq_add_neg,neg_div,neg_mul]

@[simp] theorem probe0_apply (z : State) :
    probe0 z = ((z 0+z 1)/2) • initial := by
  ext i
  fin_cases i <;> simp [probe0,probeMatrix0,initial,Matrix.mulVec,dotProduct,Fin.sum_univ_succ] <;> ring

@[simp] theorem probe1_apply (z : State) :
    probe1 z = ((z 0-z 1)/2) • initial := by
  ext i
  fin_cases i <;> simp [probe1,probeMatrix1,initial,Matrix.mulVec,dotProduct,Fin.sum_univ_succ] <;> ring

/-- Every actual branch matrix is the real cast of an exact rational matrix. -/
theorem matrix_is_rational (s : Bool × Bool) :
    ∃ M : Matrix (Fin 3) (Fin 3) ℚ, M.map (algebraMap ℚ ℝ) = matrix s := by
  rcases s with ⟨a,o⟩
  cases a <;> cases o
  · refine ⟨rotationMatrixQ, ?_⟩
    ext i j
    fin_cases i <;> fin_cases j <;> norm_num [matrix,rotationMatrixQ,rotationMatrix]
  · refine ⟨0, ?_⟩
    ext i j
    simp [matrix]
  · refine ⟨probeMatrix0Q, ?_⟩
    ext i j
    fin_cases i <;> fin_cases j <;> norm_num [matrix,probeMatrix0Q,probeMatrix0]
  · refine ⟨probeMatrix1Q, ?_⟩
    ext i j
    fin_cases i <;> fin_cases j <;> norm_num [matrix,probeMatrix1Q,probeMatrix1]

/-- The Lorentz cone, expressed in the actual three coordinates. -/
def cone : Set State := {z | Real.sqrt ((z 1)^2+(z 2)^2) ≤ z 0}

@[simp] theorem cone_iff (z : State) : z ∈ cone ↔ Real.sqrt ((z 1)^2+(z 2)^2) ≤ z 0 := Iff.rfl

theorem cone_zero : (0 : State) ∈ cone := by simp [cone]

@[simp] theorem initial_zero : initial 0 = 1 := rfl
@[simp] theorem initial_one : initial 1 = 1 := rfl
@[simp] theorem initial_two : initial 2 = 0 := rfl

theorem initial_mem : initial ∈ cone := by
  change Real.sqrt ((1:ℝ)^2+0^2) ≤ 1
  norm_num

@[simp] theorem initial_mass : mass initial = 1 := rfl

theorem cone_mass_nonneg {z : State} (hz : z ∈ cone) : 0 ≤ mass z :=
  (Real.sqrt_nonneg _).trans hz

theorem cone_spatial_abs {z : State} (hz : z ∈ cone) : |z 1| ≤ z 0 := by
  have hsq : |z 1| ≤ Real.sqrt ((z 1)^2+(z 2)^2) := by
    rw [← Real.sqrt_sq_eq_abs]
    exact Real.sqrt_le_sqrt (by nlinarith [sq_nonneg (z 2)])
  exact hsq.trans hz

theorem cone_scale {z : State} (hz : z ∈ cone) {c : ℝ} (hc : 0 ≤ c) : c • z ∈ cone := by
  change Real.sqrt ((c*z 1)^2+(c*z 2)^2) ≤ c*z 0
  have he : (c*z 1)^2+(c*z 2)^2 = c^2*((z 1)^2+(z 2)^2) := by ring
  rw [he,Real.sqrt_mul (sq_nonneg c),Real.sqrt_sq_eq_abs,abs_of_nonneg hc]
  exact mul_le_mul_of_nonneg_left hz hc

@[simp] theorem rotate_zero (z : State) : rotate z 0 = z 0 := by
  rw [rotate_apply]
  rfl
@[simp] theorem rotate_one (z : State) : rotate z 1 = (3/5:ℝ)*z 1-(4/5:ℝ)*z 2 := by
  rw [rotate_apply]
  rfl
@[simp] theorem rotate_two (z : State) : rotate z 2 = (4/5:ℝ)*z 1+(3/5:ℝ)*z 2 := by
  rw [rotate_apply]
  rfl

theorem rotate_spatial_square (z : State) :
    (rotate z 1)^2+(rotate z 2)^2 = (z 1)^2+(z 2)^2 := by
  rw [rotate_one,rotate_two]
  ring

theorem rotate_cone {z : State} (hz : z ∈ cone) : rotate z ∈ cone := by
  change Real.sqrt ((rotate z 1)^2+(rotate z 2)^2) ≤ rotate z 0
  rw [rotate_spatial_square,rotate_zero]
  exact hz

theorem probe0_cone {z : State} (hz : z ∈ cone) : probe0 z ∈ cone := by
  rw [probe0_apply]
  apply cone_scale initial_mem
  have h := neg_abs_le (z 1)
  have hx := cone_spatial_abs hz
  linarith

theorem probe1_cone {z : State} (hz : z ∈ cone) : probe1 z ∈ cone := by
  rw [probe1_apply]
  apply cone_scale initial_mem
  have h := le_abs_self (z 1)
  have hx := cone_spatial_abs hz
  linarith

theorem operator_cone (s : Bool × Bool) {z : State} (hz : z ∈ cone) : operator s z ∈ cone := by
  rcases s with ⟨a,o⟩
  cases a <;> cases o <;> simp only [operator_rotate0,operator_rotate1,operator_probe0,operator_probe1,LinearMap.zero_apply]
  · exact rotate_cone hz
  · exact cone_zero
  · exact probe0_cone hz
  · exact probe1_cone hz

theorem word_cone (w : List (Bool × Bool)) {z : State} (hz : z ∈ cone) :
    wordAction operator w z ∈ cone := by
  induction w generalizing z with
  | nil => exact hz
  | cons s w ih => exact ih (operator_cone s hz)

/-- Every future experiment has nonnegative mass on the actual Lorentz cone. -/
theorem all_word_mass_nonneg (w : List (Bool × Bool)) {z : State} (hz : z ∈ cone) :
    0 ≤ mass (wordAction operator w z) := cone_mass_nonneg (word_cone w hz)

/-- The actual branch operators conserve mass for both actions. -/
theorem operator_mass (a : Bool) (z : State) : ∑ o, mass (operator (a,o) z) = mass z := by
  rw [Fintype.sum_bool]
  cases a
  · change mass (0 : State) + mass (rotate z) = mass z
    simp
  · change mass (probe1 z) + mass (probe0 z) = mass z
    rw [probe0_apply,probe1_apply,map_smul,map_smul,initial_mass]
    simp only [mass_apply,smul_eq_mul]
    ring

noncomputable def process (w : List (Bool × Bool)) : ℝ := mass (wordAction operator w initial)

noncomputable def realization : Behavior.Realization process State where
  initial := initial
  operator := operator
  readout := mass
  correct _ := rfl

/-- Every normalized point of the invariant cone defines a genuine causal law. -/
theorem causal_of_normalized_cone (z : State) (hz : z ∈ cone) (hm : mass z = 1) :
    Behavior.CausalLaw (fun w => mass (wordAction operator w z)) := by
  refine ⟨hm,?_,?_⟩
  · intro w
    exact all_word_mass_nonneg w hz
  · intro h a
    simpa only [wordAction_append,wordAction_cons,wordAction_nil,
      LinearMap.id_comp,LinearMap.comp_apply] using operator_mass a (wordAction operator h z)

theorem normalized_word_probability (z : State) (hz : z ∈ cone) (hm : mass z = 1)
    (w : List (Bool × Bool)) :
    0 ≤ mass (wordAction operator w z) ∧ mass (wordAction operator w z) ≤ 1 :=
  (causal_of_normalized_cone z hz hm).word_bounds w

/-- Conditioning a positive branch remains in the normalized cone. -/
theorem posterior_cone (s : Bool × Bool) (z : State) (hz : z ∈ cone)
    (hp : 0 < mass (operator s z)) :
    normalize mass (operator s z) ∈ cone ∧ mass (normalize mass (operator s z)) = 1 := by
  exact ⟨cone_scale (operator_cone s hz) (inv_nonneg.mpr hp.le),
    normalize_mass mass (operator s z) (ne_of_gt hp)⟩

/-- Every positive probe output is reset to the declared boundary state. -/
theorem probe0_posterior (z : State) (hp : 0 < (z 0+z 1)/2) :
    normalize mass (probe0 z) = initial := by
  rw [probe0_apply]
  unfold FiniteInstruments.normalize
  rw [map_smul,initial_mass]
  simp only [smul_eq_mul,mul_one]
  rw [smul_smul,inv_mul_cancel₀ (ne_of_gt hp),one_smul]

theorem probe1_posterior (z : State) (hp : 0 < (z 0-z 1)/2) :
    normalize mass (probe1 z) = initial := by
  rw [probe1_apply]
  unfold FiniteInstruments.normalize
  rw [map_smul,initial_mass]
  simp only [smul_eq_mul,mul_one]
  rw [smul_smul,inv_mul_cancel₀ (ne_of_gt hp),one_smul]

/-- This is a causal law from the constructed cone, not from entrywise positivity. -/
theorem process_causal : Behavior.CausalLaw process := by
  refine ⟨initial_mass,?_,?_⟩
  · intro w
    exact cone_mass_nonneg (word_cone w initial_mem)
  · intro h a
    simpa only [process,wordAction_append,wordAction_cons,wordAction_nil,
      LinearMap.id_comp,LinearMap.comp_apply] using operator_mass a (wordAction operator h initial)

theorem process_probability (w : List (Bool × Bool)) : 0 ≤ process w ∧ process w ≤ 1 :=
  process_causal.word_bounds w

end Komorebi.LSM.RotationModel
