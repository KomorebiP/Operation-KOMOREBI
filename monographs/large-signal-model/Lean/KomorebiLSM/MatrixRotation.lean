import KomorebiLSM.RotationP46
import KomorebiLSM.MatrixEmbedding
import Mathlib.Analysis.Matrix.PosDef
import Mathlib.Algebra.Order.Star.Real
import Mathlib.Tactic

/-! Proposition 51: an exact rational two-by-two matrix certificate for the
unchanged rational rotation process. -/
set_option autoImplicit false
namespace Komorebi.LSM.MatrixRotation
open scoped BigOperators Matrix
open FiniteInstruments

abbrev State := RotationModel.State
abbrev MatrixState := Matrix (Fin 2) (Fin 2) ℝ

noncomputable def embedding : State →ₗ[ℝ] MatrixState where
  toFun z := !![(z 0+z 1)/2,z 2/2; z 2/2,(z 0-z 1)/2]
  map_add' z w := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp <;> ring
  map_smul' c z := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp <;> ring

@[simp] theorem embedding_apply (z : State) :
    embedding z=!![(z 0+z 1)/2,z 2/2; z 2/2,(z 0-z 1)/2] := rfl

theorem embedding_hermitian (z : State) : (embedding z).IsHermitian := by
  unfold Matrix.IsHermitian
  ext i j
  fin_cases i <;> fin_cases j <;> simp [Matrix.conjTranspose_apply]

theorem embedding_injective : Function.Injective embedding := by
  intro z w h
  have h0 := congrFun (congrFun h 0) 0
  have h1 := congrFun (congrFun h 1) 1
  have h2 := congrFun (congrFun h 0) 1
  change (z 0+z 1)/2=(w 0+w 1)/2 at h0
  change (z 0-z 1)/2=(w 0-w 1)/2 at h1
  change z 2/2=w 2/2 at h2
  ext i
  fin_cases i <;> simp_all <;> linarith

@[simp] theorem embedding_trace (z : State) : (embedding z).trace=RotationModel.mass z := by
  simp [Matrix.trace,Fin.sum_univ_succ]
  ring

theorem embedding_det (z : State) :
    (embedding z).det=((z 0)^2-(z 1)^2-(z 2)^2)/4 := by
  simp [Matrix.det_fin_two]
  ring

/-- The elementary two-variable criterion, including a vanishing first pivot. -/
theorem binary_quadratic_nonneg (a b c : ℝ) (ha : 0 ≤ a) (hc : 0 ≤ c)
    (hdet : b^2 ≤ a*c) (u v : ℝ) :
    0 ≤ a*u^2+2*b*u*v+c*v^2 := by
  by_cases ha0 : a=0
  · have hb : b=0 := by nlinarith [sq_nonneg b]
    subst a
    subst b
    simpa using mul_nonneg hc (sq_nonneg v)
  · have ha' : 0<a := lt_of_le_of_ne ha (Ne.symm ha0)
    apply nonneg_of_mul_nonneg_left _ ha'
    calc
      (a*u^2+2*b*u*v+c*v^2)*a = (a*u+b*v)^2+(a*c-b^2)*v^2 := by ring
      _ ≥ 0 := add_nonneg (sq_nonneg _) (mul_nonneg (sub_nonneg.mpr hdet) (sq_nonneg _))

theorem embedding_posSemidef_iff (z : State) :
    (embedding z).PosSemidef ↔ z ∈ RotationModel.cone := by
  constructor
  · intro hz
    have hd0 := hz.diag_nonneg (i:=0)
    have hd1 := hz.diag_nonneg (i:=1)
    have hdet := hz.det_nonneg
    rw [embedding_det] at hdet
    change 0 ≤ (z 0+z 1)/2 at hd0
    change 0 ≤ (z 0-z 1)/2 at hd1
    apply Real.sqrt_le_iff.mpr
    constructor <;> nlinarith
  · intro hz
    change Real.sqrt ((z 1)^2+(z 2)^2) ≤ z 0 at hz
    have hm : 0 ≤ z 0 := (Real.sqrt_nonneg _).trans hz
    have hx := RotationModel.cone_spatial_abs hz
    have hsq := Real.sq_sqrt (show 0 ≤ (z 1)^2+(z 2)^2 by positivity)
    have hs := Real.sqrt_nonneg ((z 1)^2+(z 2)^2)
    have hdiag0 : 0 ≤ (z 0+z 1)/2 := by linarith [neg_abs_le (z 1)]
    have hdiag1 : 0 ≤ (z 0-z 1)/2 := by linarith [le_abs_self (z 1)]
    have hdet : (z 2/2)^2 ≤ ((z 0+z 1)/2)*((z 0-z 1)/2) := by nlinarith
    apply Matrix.PosSemidef.of_dotProduct_mulVec_nonneg (embedding_hermitian z)
    intro v
    have h := binary_quadratic_nonneg _ _ _ hdiag0 hdiag1 hdet (v 0) (v 1)
    have he : star v ⬝ᵥ ((embedding z) *ᵥ v) =
        (z 0+z 1)/2*(v 0)^2+2*(z 2/2)*(v 0)*(v 1)+(z 0-z 1)/2*(v 1)^2 := by
      simp [Matrix.mulVec,dotProduct,Fin.sum_univ_succ]
      ring
    rw [he]
    exact h

@[simp] theorem embedding_initial : embedding RotationModel.initial=!![1,0;0,0] := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [RotationModel.initial,Matrix.cons_val_two]

def interiorWitness : State := ![1,0,0]

theorem embedding_interior : (embedding interiorWitness).PosDef := by
  have he : embedding interiorWitness=(1/2:ℝ) • (1:MatrixState) := by
    ext i j
    fin_cases i <;> fin_cases j <;> norm_num [interiorWitness,Matrix.one_apply,Matrix.cons_val_two]
  rw [he]
  exact Matrix.PosDef.one.smul (by norm_num)


/-- Integer matrices and rational weights are the complete congruence data. -/
def rotationKQ : Matrix (Fin 2) (Fin 2) ℚ := !![2,-1;1,2]
def probeK0Q : Matrix (Fin 2) (Fin 2) ℚ := !![1,0;0,0]
def probeK1Q : Matrix (Fin 2) (Fin 2) ℚ := !![0,1;0,0]

noncomputable def rotationK : MatrixState := rotationKQ.map (algebraMap ℚ ℝ)
noncomputable def probeK0 : MatrixState := probeK0Q.map (algebraMap ℚ ℝ)
noncomputable def probeK1 : MatrixState := probeK1Q.map (algebraMap ℚ ℝ)

def branchWeightQ (s : Bool × Bool) : ℚ :=
  if s.1 then 1 else (if s.2 then 0 else 1/5)

def branchKQ (s : Bool × Bool) : Matrix (Fin 2) (Fin 2) ℚ :=
  if s.1 then (if s.2 then probeK1Q else probeK0Q)
  else (if s.2 then 0 else rotationKQ)

noncomputable def branchWeight (s : Bool × Bool) : ℝ := (algebraMap ℚ ℝ) (branchWeightQ s)
noncomputable def branchK (s : Bool × Bool) : MatrixState := (branchKQ s).map (algebraMap ℚ ℝ)

noncomputable def congruence (K : MatrixState) : MatrixState →ₗ[ℝ] MatrixState :=
  { toFun := fun X => K*X*Kᵀ
    map_add' := fun X Y => by simp [Matrix.mul_add,Matrix.add_mul]
    map_smul' := fun c X => by simp }

@[simp] theorem congruence_apply (K X : MatrixState) : congruence K X=K*X*Kᵀ := rfl

noncomputable def matrixOperator (s : Bool × Bool) : MatrixState →ₗ[ℝ] MatrixState :=
  branchWeight s • congruence (branchK s)

@[simp] theorem matrixOperator_apply (s : Bool × Bool) (X : MatrixState) :
    matrixOperator s X=branchWeight s • (branchK s*X*(branchK s)ᵀ) := rfl

theorem branchWeight_nonnegative (s : Bool × Bool) : 0 ≤ branchWeight s := by
  rcases s with ⟨a,o⟩
  cases a <;> cases o <;> norm_num [branchWeight,branchWeightQ]

theorem embedding_rotate (z : State) :
    embedding (RotationModel.rotate z)=(1/5:ℝ) • (rotationK*embedding z*rotationKᵀ) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [rotationK,rotationKQ,Matrix.mul_apply,Fin.sum_univ_succ] <;> ring

theorem embedding_probe0 (z : State) :
    embedding (RotationModel.probe0 z)=probeK0*embedding z*probeK0ᵀ := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [probeK0,probeK0Q,RotationModel.initial,Matrix.mul_apply,Fin.sum_univ_succ,
      Matrix.cons_val_two]

theorem embedding_probe1 (z : State) :
    embedding (RotationModel.probe1 z)=probeK1*embedding z*probeK1ᵀ := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    simp [probeK1,probeK1Q,RotationModel.initial,Matrix.mul_apply,Fin.sum_univ_succ,
      Matrix.cons_val_two]

theorem embedding_operator (s : Bool × Bool) (z : State) :
    embedding (RotationModel.operator s z)=matrixOperator s (embedding z) := by
  rcases s with ⟨a,o⟩
  cases a <;> cases o
  · simpa [branchWeight,branchWeightQ,branchK,branchKQ,rotationK] using embedding_rotate z
  · rw [RotationModel.operator_rotate1,LinearMap.zero_apply,map_zero]
    simp [branchWeight,branchWeightQ]
  · simpa [branchWeight,branchWeightQ,branchK,branchKQ,probeK0] using embedding_probe0 z
  · simpa [branchWeight,branchWeightQ,branchK,branchKQ,probeK1] using embedding_probe1 z

theorem rotationK_gram : rotationKᵀ*rotationK=5 • (1:MatrixState) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [rotationK,rotationKQ,Matrix.mul_apply,Fin.sum_univ_succ,Matrix.one_apply]

theorem probeK_gram : probeK0ᵀ*probeK0+probeK1ᵀ*probeK1=(1:MatrixState) := by
  ext i j
  fin_cases i <;> fin_cases j <;>
    norm_num [probeK0,probeK0Q,probeK1,probeK1Q,Matrix.mul_apply,Fin.sum_univ_succ,
      Matrix.one_apply]

theorem matrixOperator_trace_mass (a : Bool) (X : MatrixState) :
    ∑ o : Bool, (matrixOperator (a,o) X).trace=X.trace := by
  cases a <;>
    simp [matrixOperator,congruence,branchWeight,branchWeightQ,branchK,branchKQ,
      rotationKQ,probeK0Q,probeK1Q,Matrix.trace,Matrix.mul_apply,Fin.sum_univ_succ] <;> ring

theorem embedding_word (w : List (Bool × Bool)) (z : State) :
    embedding (wordAction RotationModel.operator w z)=
      wordAction matrixOperator w (embedding z) := by
  induction w generalizing z with
  | nil => rfl
  | cons s w ih =>
    simpa only [wordAction_cons,LinearMap.comp_apply,embedding_operator] using ih (RotationModel.operator s z)

theorem word_probability_unchanged (w : List (Bool × Bool)) (z : State) :
    (wordAction matrixOperator w (embedding z)).trace=
      RotationModel.mass (wordAction RotationModel.operator w z) := by
  rw [← embedding_word,embedding_trace]

noncomputable def matrixProcess (w : List (Bool × Bool)) : ℝ :=
  (wordAction matrixOperator w (embedding RotationModel.initial)).trace

theorem matrixProcess_eq : matrixProcess=RotationModel.process := by
  funext w
  exact word_probability_unchanged w RotationModel.initial

theorem matrixProcess_causal : Behavior.CausalLaw matrixProcess := by
  rw [matrixProcess_eq]
  exact RotationModel.process_causal

theorem matrixProcess_probability (w : List (Bool × Bool)) :
    0 ≤ matrixProcess w ∧ matrixProcess w ≤ 1 := matrixProcess_causal.word_bounds w


/-- The embedding itself has exact rational coefficients. -/
def embeddingQ : (Fin 3 → ℚ) →ₗ[ℚ] Matrix (Fin 2) (Fin 2) ℚ where
  toFun z := !![(z 0+z 1)/2,z 2/2; z 2/2,(z 0-z 1)/2]
  map_add' z w := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp <;> ring
  map_smul' c z := by
    ext i j
    fin_cases i <;> fin_cases j <;> simp <;> ring

theorem embedding_rational_cast (z : Fin 3 → ℚ) :
    (embeddingQ z).map (algebraMap ℚ ℝ)=embedding (fun i => (algebraMap ℚ ℝ) (z i)) := by
  ext i j
  fin_cases i <;> fin_cases j <;> simp [embeddingQ]

theorem normalized_base_disk (z : State) :
    (embedding z).PosSemidef ∧ (embedding z).trace=1 ↔
      z 0=1 ∧ Real.sqrt ((z 1)^2+(z 2)^2) ≤ 1 := by
  rw [embedding_posSemidef_iff,embedding_trace]
  change (Real.sqrt ((z 1)^2+(z 2)^2) ≤ z 0 ∧ z 0=1) ↔ _
  constructor
  · rintro ⟨hr,hm⟩
    exact ⟨hm,by simpa only [hm] using hr⟩
  · rintro ⟨hm,hr⟩
    exact ⟨by simpa only [hm] using hr,hm⟩

theorem initial_matrix_normalized :
    (embedding RotationModel.initial).PosSemidef ∧ (embedding RotationModel.initial).trace=1 :=
  ⟨(embedding_posSemidef_iff _).mpr RotationModel.initial_mem,by simp⟩

theorem no_finite_positive_generator_certificate (n : ℕ) :
    ¬ ∃ V : (Fin n → ℝ) →ₗ[ℝ] State,
      RotationModel.mass.comp V=FiniteInstruments.mass ∧
      RotationModel.initial ∈ PositiveLift.hull V ∧
      ∀ s z, z ∈ PositiveLift.hull V → RotationModel.operator s z ∈ PositiveLift.hull V := by
  rintro ⟨V,hm,hi,hb⟩
  exact RotationConeGeometry.no_finite_normalized_generator_certificate V hm hi hb


/-- Each matrix branch preserves the whole positive semidefinite cone. -/
theorem matrixOperator_posSemidef (s : Bool × Bool) {X : MatrixState} (hX : X.PosSemidef) :
    (matrixOperator s X).PosSemidef := by
  rw [matrixOperator_apply]
  apply Matrix.PosSemidef.smul _ (branchWeight_nonnegative s)
  simpa only [Matrix.conjTranspose_eq_transpose_of_trivial] using
    hX.mul_mul_conjTranspose_same (branchK s)

theorem matrix_word_posSemidef (w : List (Bool × Bool)) {X : MatrixState}
    (hX : X.PosSemidef) : (wordAction matrixOperator w X).PosSemidef := by
  induction w generalizing X with
  | nil => exact hX
  | cons s w ih =>
    exact ih (matrixOperator_posSemidef s hX)

theorem rational_branch_certificate (s : Bool × Bool) :
    ∃ (c : ℚ) (K : Matrix (Fin 2) (Fin 2) ℚ), 0 ≤ c ∧
      ∀ z : State, embedding (RotationModel.operator s z)=
        (algebraMap ℚ ℝ) c •
          (K.map (algebraMap ℚ ℝ)*embedding z*(K.map (algebraMap ℚ ℝ))ᵀ) := by
  refine ⟨branchWeightQ s,branchKQ s,?_,embedding_operator s⟩
  rcases s with ⟨a,o⟩
  cases a <;> cases o <;> norm_num [branchWeightQ]

/-- All clauses concern the unchanged source process, alongside its finite
positive-generator obstruction. Matrix positivity changes the certificate
language and does not attenuate the model. -/
theorem exact_rational_matrix_witness :
    Function.Injective embedding ∧
    (∀ z, (embedding z).IsHermitian) ∧
    (∀ z, (embedding z).trace=RotationModel.mass z) ∧
    (∀ z, (embedding z).PosSemidef ↔ z ∈ RotationModel.cone) ∧
    (embedding interiorWitness).PosDef ∧
    embedding RotationModel.initial=!![1,0;0,0] ∧
    (∀ s, 0 ≤ branchWeight s) ∧
    (∀ s z, embedding (RotationModel.operator s z)=matrixOperator s (embedding z)) ∧
    (∀ a X, ∑ o : Bool, (matrixOperator (a,o) X).trace=X.trace) ∧
    (∀ w, matrixProcess w=RotationModel.process w) ∧
    (∀ n : ℕ, ¬ ∃ V : (Fin n → ℝ) →ₗ[ℝ] State,
      RotationModel.mass.comp V=FiniteInstruments.mass ∧
      RotationModel.initial ∈ PositiveLift.hull V ∧
      ∀ s z, z ∈ PositiveLift.hull V → RotationModel.operator s z ∈ PositiveLift.hull V) := by
  exact ⟨embedding_injective,embedding_hermitian,embedding_trace,embedding_posSemidef_iff,
    embedding_interior,embedding_initial,branchWeight_nonnegative,embedding_operator,
    matrixOperator_trace_mass,fun w => congrFun matrixProcess_eq w,
    no_finite_positive_generator_certificate⟩


/-- The displayed rational witness is an instance of the generic matrix
embedding certificate language, with its actual interior matrix. -/
noncomputable def certificate : MatrixEmbedding.Embedding State (Fin 2) where
  J := embedding
  symmetric := embedding_hermitian
  injective := embedding_injective
  interior := interiorWitness
  interior_posDef := embedding_interior

@[simp] theorem certificate_mass : certificate.mass=RotationModel.mass := by
  apply LinearMap.ext
  intro z
  exact embedding_trace z

@[simp] theorem certificate_cone : certificate.cone=RotationModel.cone := by
  ext z
  exact embedding_posSemidef_iff z

end Komorebi.LSM.MatrixRotation
