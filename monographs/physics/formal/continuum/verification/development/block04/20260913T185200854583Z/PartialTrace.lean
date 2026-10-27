module

public import KomorebiPhysics.TensorAtlas

/-!
Finite partial traces added as an operational bridge for Chapter 4.4.
These are explicit index contractions, not assumed marginal maps. Positivity,
trace preservation, local-observable duality and actual derivatives are proved.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.PartialTrace
open scoped BigOperators Matrix Kronecker ComplexOrder
open MixedTransfer
variable {m n : Type*}

/-- Trace out the second factor, retaining the first subsystem. -/
def left [Fintype n] (ρ : Matrix (m × n) (m × n) ℂ) : Matrix m m ℂ :=
  fun a b => ∑ u, ρ (a,u) (b,u)

/-- Trace out the first factor, retaining the second subsystem. -/
def right [Fintype m] (ρ : Matrix (m × n) (m × n) ℂ) : Matrix n n ℂ :=
  fun u v => ∑ a, ρ (a,u) (a,v)

/-- The first partial trace is a sum of principal compressions. -/
theorem left_eq_sum_submatrix [Fintype n] (ρ : Matrix (m × n) (m × n) ℂ) :
    left ρ = ∑ u : n, ρ.submatrix (fun a => (a,u)) (fun b => (b,u)) := by
  ext a b
  simp only [left, Matrix.sum_apply, Matrix.submatrix_apply]

/-- The second partial trace is likewise a sum of principal compressions. -/
theorem right_eq_sum_submatrix [Fintype m] (ρ : Matrix (m × n) (m × n) ℂ) :
    right ρ = ∑ a : m, ρ.submatrix (fun u => (a,u)) (fun v => (a,v)) := by
  ext u v
  simp only [right, Matrix.sum_apply, Matrix.submatrix_apply]

/-- First partial trace is additive. -/
theorem left_add [Fintype n] (ρ σ : Matrix (m × n) (m × n) ℂ) :
    left (ρ + σ) = left ρ + left σ := by
  ext a b
  simp only [left, Matrix.add_apply, Finset.sum_add_distrib]

/-- Second partial trace is additive. -/
theorem right_add [Fintype m] (ρ σ : Matrix (m × n) (m × n) ℂ) :
    right (ρ + σ) = right ρ + right σ := by
  ext u v
  simp only [right, Matrix.add_apply, Finset.sum_add_distrib]

/-- First partial trace commutes with subtraction. -/
theorem left_sub [Fintype n] (ρ σ : Matrix (m × n) (m × n) ℂ) :
    left (ρ - σ) = left ρ - left σ := by
  ext a b
  simp only [left, Matrix.sub_apply, Finset.sum_sub_distrib]

/-- Second partial trace commutes with subtraction. -/
theorem right_sub [Fintype m] (ρ σ : Matrix (m × n) (m × n) ℂ) :
    right (ρ - σ) = right ρ - right σ := by
  ext u v
  simp only [right, Matrix.sub_apply, Finset.sum_sub_distrib]

/-- First partial trace is complex-linear. -/
theorem left_smul [Fintype n] (z : ℂ) (ρ : Matrix (m × n) (m × n) ℂ) :
    left (z • ρ) = z • left ρ := by
  ext a b
  simp only [left, Matrix.smul_apply, Finset.smul_sum]

/-- Second partial trace is complex-linear. -/
theorem right_smul [Fintype m] (z : ℂ) (ρ : Matrix (m × n) (m × n) ℂ) :
    right (z • ρ) = z • right ρ := by
  ext u v
  simp only [right, Matrix.smul_apply, Finset.smul_sum]

/-- Adjoint compatibility of the first contraction. -/
theorem left_conjTranspose [Fintype n] (ρ : Matrix (m × n) (m × n) ℂ) :
    left ρ.conjTranspose = (left ρ).conjTranspose := by
  ext a b
  simp only [left, Matrix.conjTranspose_apply, map_sum]

/-- Adjoint compatibility of the second contraction. -/
theorem right_conjTranspose [Fintype m] (ρ : Matrix (m × n) (m × n) ℂ) :
    right ρ.conjTranspose = (right ρ).conjTranspose := by
  ext u v
  simp only [right, Matrix.conjTranspose_apply, map_sum]

/-- Hermiticity of the first reduced state is a conclusion. -/
theorem left_hermitian [Fintype n] (ρ : Matrix (m × n) (m × n) ℂ)
    (hρ : ρ.conjTranspose = ρ) : (left ρ).conjTranspose = left ρ := by
  rw [← left_conjTranspose, hρ]

/-- Hermiticity of the second reduced state is a conclusion. -/
theorem right_hermitian [Fintype m] (ρ : Matrix (m × n) (m × n) ℂ)
    (hρ : ρ.conjTranspose = ρ) : (right ρ).conjTranspose = right ρ := by
  rw [← right_conjTranspose, hρ]

/-- The first partial trace preserves the full complex trace. -/
theorem trace_left [Fintype m] [Fintype n] (ρ : Matrix (m × n) (m × n) ℂ) :
    Matrix.trace (left ρ) = Matrix.trace ρ := by
  simp only [Matrix.trace, Matrix.diag_apply, left, Fintype.sum_prod_type]

/-- The second partial trace preserves the full complex trace. -/
theorem trace_right [Fintype m] [Fintype n] (ρ : Matrix (m × n) (m × n) ℂ) :
    Matrix.trace (right ρ) = Matrix.trace ρ := by
  simp only [Matrix.trace, Matrix.diag_apply, right, Fintype.sum_prod_type]
  exact Finset.sum_comm

/-- Positivity survives discarding the second factor. -/
theorem left_posSemidef [Fintype n] (ρ : Matrix (m × n) (m × n) ℂ)
    (hρ : ρ.PosSemidef) : (left ρ).PosSemidef := by
  rw [left_eq_sum_submatrix]
  exact Matrix.posSemidef_sum Finset.univ (fun u _ => hρ.submatrix (fun a => (a,u)))

/-- Positivity survives discarding the first factor. -/
theorem right_posSemidef [Fintype m] (ρ : Matrix (m × n) (m × n) ℂ)
    (hρ : ρ.PosSemidef) : (right ρ).PosSemidef := by
  rw [right_eq_sum_submatrix]
  exact Matrix.posSemidef_sum Finset.univ (fun a _ => hρ.submatrix (fun u => (a,u)))

/-- A joint density matrix produces an actual first-subsystem density matrix. -/
theorem left_density [Fintype m] [Fintype n] (ρ : Matrix (m × n) (m × n) ℂ)
    (hρ : ρ.PosSemidef) (ht : Matrix.trace ρ = 1) :
    (left ρ).PosSemidef ∧ Matrix.trace (left ρ) = 1 :=
  ⟨left_posSemidef ρ hρ, (trace_left ρ).trans ht⟩

/-- A joint density matrix produces an actual second-subsystem density matrix. -/
theorem right_density [Fintype m] [Fintype n] (ρ : Matrix (m × n) (m × n) ℂ)
    (hρ : ρ.PosSemidef) (ht : Matrix.trace ρ = 1) :
    (right ρ).PosSemidef ∧ Matrix.trace (right ρ) = 1 :=
  ⟨right_posSemidef ρ hρ, (trace_right ρ).trans ht⟩

/-- Product-state contraction retains the trace of the discarded factor. -/
theorem left_kronecker [Fintype n] (A : Matrix m m ℂ) (B : Matrix n n ℂ) :
    left (A ⊗ₖ B) = Matrix.trace B • A := by
  ext a b
  simp only [left, Matrix.kronecker_apply, Matrix.smul_apply, smul_eq_mul,
    Matrix.trace, Matrix.diag_apply, ← Finset.mul_sum]
  exact mul_comm _ _

/-- The other product-state contraction also retains its trace factor. -/
theorem right_kronecker [Fintype m] (A : Matrix m m ℂ) (B : Matrix n n ℂ) :
    right (A ⊗ₖ B) = Matrix.trace A • B := by
  ext u v
  simp only [right, Matrix.kronecker_apply, Matrix.smul_apply, smul_eq_mul,
    Matrix.trace, Matrix.diag_apply, Finset.sum_mul]

/-- Pulling a local left multiplier through the first contraction. -/
theorem left_mul_local [Fintype m] [Fintype n] [DecidableEq n]
    (A : Matrix m m ℂ) (ρ : Matrix (m × n) (m × n) ℂ) :
    left ((A ⊗ₖ (1 : Matrix n n ℂ)) * ρ) = A * left ρ := by
  ext a b
  simp only [left, Matrix.mul_apply, Fintype.sum_prod_type, Matrix.kronecker_apply,
    Matrix.one_apply, mul_ite, mul_one, mul_zero, ite_mul, zero_mul,
    Finset.sum_ite_eq, Finset.mem_univ, ite_true, Finset.mul_sum]
  exact Finset.sum_comm

/-- Pulling a local right multiplier through the first contraction. -/
theorem left_local_mul [Fintype m] [Fintype n] [DecidableEq n]
    (ρ : Matrix (m × n) (m × n) ℂ) (A : Matrix m m ℂ) :
    left (ρ * (A ⊗ₖ (1 : Matrix n n ℂ))) = left ρ * A := by
  ext a b
  simp only [left, Matrix.mul_apply, Fintype.sum_prod_type, Matrix.kronecker_apply,
    Matrix.one_apply, mul_ite, mul_one, mul_zero, Finset.sum_ite_eq',
    Finset.mem_univ, ite_true, Finset.sum_mul]
  exact Finset.sum_comm

/-- Pulling a local left multiplier through the second contraction. -/
theorem right_mul_local [Fintype m] [Fintype n] [DecidableEq m]
    (B : Matrix n n ℂ) (ρ : Matrix (m × n) (m × n) ℂ) :
    right (((1 : Matrix m m ℂ) ⊗ₖ B) * ρ) = B * right ρ := by
  ext u v
  simp only [right, Matrix.mul_apply, Fintype.sum_prod_type, Matrix.kronecker_apply,
    Matrix.one_apply, ite_mul, one_mul, zero_mul, Finset.sum_ite_eq,
    Finset.mem_univ, ite_true, Finset.mul_sum]
  exact Finset.sum_comm

/-- Pulling a local right multiplier through the second contraction. -/
theorem right_local_mul [Fintype m] [Fintype n] [DecidableEq m]
    (ρ : Matrix (m × n) (m × n) ℂ) (B : Matrix n n ℂ) :
    right (ρ * ((1 : Matrix m m ℂ) ⊗ₖ B)) = right ρ * B := by
  ext u v
  simp only [right, Matrix.mul_apply, Fintype.sum_prod_type, Matrix.kronecker_apply,
    Matrix.one_apply, ite_mul, one_mul, zero_mul, mul_ite, mul_zero,
    Finset.sum_ite_eq', Finset.mem_univ, ite_true, Finset.sum_mul]
  exact Finset.sum_comm

/-- Remote factors are cyclic under the first partial trace. This is not a
claim that arbitrary operators are cyclic under a partial trace. -/
theorem left_remote_cycle [Fintype m] [Fintype n] [DecidableEq m]
    (B : Matrix n n ℂ) (ρ : Matrix (m × n) (m × n) ℂ) :
    left (((1 : Matrix m m ℂ) ⊗ₖ B) * ρ) =
      left (ρ * ((1 : Matrix m m ℂ) ⊗ₖ B)) := by
  ext a b
  simp only [left, Matrix.mul_apply, Fintype.sum_prod_type, Matrix.kronecker_apply,
    Matrix.one_apply, ite_mul, one_mul, zero_mul, mul_ite, mul_zero,
    Finset.sum_ite_eq, Finset.sum_ite_eq', Finset.mem_univ, ite_true]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro u _
  apply Finset.sum_congr rfl
  intro v _
  exact mul_comm _ _

/-- Remote factors are cyclic under the second partial trace. -/
theorem right_remote_cycle [Fintype m] [Fintype n] [DecidableEq n]
    (A : Matrix m m ℂ) (ρ : Matrix (m × n) (m × n) ℂ) :
    right ((A ⊗ₖ (1 : Matrix n n ℂ)) * ρ) =
      right (ρ * (A ⊗ₖ (1 : Matrix n n ℂ))) := by
  ext u v
  simp only [right, Matrix.mul_apply, Fintype.sum_prod_type, Matrix.kronecker_apply,
    Matrix.one_apply, mul_ite, mul_one, mul_zero, ite_mul, zero_mul,
    Finset.sum_ite_eq, Finset.sum_ite_eq', Finset.mem_univ, ite_true]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro a _
  apply Finset.sum_congr rfl
  intro b _
  exact mul_comm _ _

/-- Local-observable duality for every joint matrix, without a state-factorization
or Hermiticity hypothesis. -/
theorem trace_local_left [Fintype m] [Fintype n] [DecidableEq n]
    (A : Matrix m m ℂ) (ρ : Matrix (m × n) (m × n) ℂ) :
    Matrix.trace ((A ⊗ₖ (1 : Matrix n n ℂ)) * ρ) = Matrix.trace (A * left ρ) := by
  rw [← trace_left ((A ⊗ₖ (1 : Matrix n n ℂ)) * ρ), left_mul_local]

/-- The corresponding second-subsystem observable duality. -/
theorem trace_local_right [Fintype m] [Fintype n] [DecidableEq m]
    (B : Matrix n n ℂ) (ρ : Matrix (m × n) (m × n) ℂ) :
    Matrix.trace (((1 : Matrix m m ℂ) ⊗ₖ B) * ρ) = Matrix.trace (B * right ρ) := by
  rw [← trace_right (((1 : Matrix m m ℂ) ⊗ₖ B) * ρ), right_mul_local]

/-- The probability of the actual first reduced state is the joint marginal. -/
theorem probability_left [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]
    {I J : Type*} [Fintype I] [DecidableEq I] [Fintype J] [DecidableEq J]
    (P : MatrixAtlas m I) (Q : MatrixAtlas n J)
    (ρ : Matrix (m × n) (m × n) ℂ) (i : I) :
    P.probability (left ρ) i = ∑ j, (P.tensor Q).probability ρ (i,j) := by
  rw [P.tensor_marginal_left Q, trace_local_left]
  rfl

/-- The probability of the actual second reduced state is the other marginal. -/
theorem probability_right [Fintype m] [DecidableEq m] [Fintype n] [DecidableEq n]
    {I J : Type*} [Fintype I] [DecidableEq I] [Fintype J] [DecidableEq J]
    (P : MatrixAtlas m I) (Q : MatrixAtlas n J)
    (ρ : Matrix (m × n) (m × n) ℂ) (j : J) :
    Q.probability (right ρ) j = ∑ i, (P.tensor Q).probability ρ (i,j) := by
  rw [P.tensor_marginal_right Q, trace_local_right]
  rfl

/-- Actual time differentiation commutes with the finite first contraction. -/
theorem hasDerivAt_left [Fintype m] [Fintype n]
    {ρ : ℝ → Matrix (m × n) (m × n) ℂ} {dρ : Matrix (m × n) (m × n) ℂ} {t : ℝ}
    (hρ : HasDerivAt ρ dρ t) :
    HasDerivAt (fun s => left (ρ s)) (left dρ) t := by
  apply hasDerivAt_pi.mpr
  intro a
  apply hasDerivAt_pi.mpr
  intro b
  exact HasDerivAt.fun_sum (u := Finset.univ)
    (fun u _ => MixedTransfer.hasDerivAt_entry hρ (a,u) (b,u))

/-- Actual time differentiation commutes with the finite second contraction. -/
theorem hasDerivAt_right [Fintype m] [Fintype n]
    {ρ : ℝ → Matrix (m × n) (m × n) ℂ} {dρ : Matrix (m × n) (m × n) ℂ} {t : ℝ}
    (hρ : HasDerivAt ρ dρ t) :
    HasDerivAt (fun s => right (ρ s)) (right dρ) t := by
  apply hasDerivAt_pi.mpr
  intro u
  apply hasDerivAt_pi.mpr
  intro v
  exact HasDerivAt.fun_sum (u := Finset.univ)
    (fun a _ => MixedTransfer.hasDerivAt_entry hρ (a,u) (a,v))

end KomorebiPhysics.PartialTrace
