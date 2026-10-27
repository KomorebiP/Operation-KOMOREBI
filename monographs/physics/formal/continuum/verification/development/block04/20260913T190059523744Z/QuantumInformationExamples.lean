module

public import KomorebiPhysics.PartialTrace
public import KomorebiPhysics.InformationTransport
public import KomorebiPhysics.EntanglementWitness
public import KomorebiPhysics.ExtensionExamples

/-!
Exact tests for Block 04. The Bell example is a positive normalized pure joint
state, not a product of marginal states and not a finite nonnegative mixture
of product pure states. The scalar probability trajectories are used locally
at t=0; their affine formulas are not globally positive for all real t.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.QuantumInformationExamples
open scoped BigOperators Matrix Kronecker ComplexOrder
open MixedTransfer InformationTransport EntanglementWitness
open ExtensionExamples (binaryAtlas)

/-- Unnormalized vector |00>+|11>. -/
def bellVector (x : Fin 2 × Fin 2) : ℂ := if x.1 = x.2 then 1 else 0

/-- The exact normalized Bell density; no irrational numerical approximation. -/
def bell : Matrix (Fin 2 × Fin 2) (Fin 2 × Fin 2) ℂ :=
  (1/2 : ℝ) • pureState bellVector

/-- The maximally mixed one-qubit density matrix. -/
def halfIdentity : Matrix (Fin 2) (Fin 2) ℂ := !![(1/2:ℂ),0;0,1/2]

/-- Exact entries of the Bell density. -/
theorem bell_entries (x y : Fin 2 × Fin 2) :
    bell x y = if x.1 = x.2 ∧ y.1 = y.2 then (1/2:ℂ) else 0 := by
  by_cases hx : x.1 = x.2 <;> by_cases hy : y.1 = y.2 <;>
    norm_num [bell, bellVector, pureState, Matrix.vecMulVec_apply, hx, hy]

/-- The joint Bell matrix is positive semidefinite by a positive rank-one factor. -/
theorem bell_posSemidef : bell.PosSemidef :=
  (pureState_posSemidef bellVector).smul (by norm_num : 0 ≤ (1/2:ℝ))

/-- Exact trace-one normalization. -/
theorem bell_trace_one : Matrix.trace bell = 1 := by
  norm_num [Matrix.trace, Matrix.diag_apply, Fintype.sum_prod_type,
    Fin.sum_univ_two, bell_entries]

/-- The joint state is a pure projector, even though both reduced states are mixed. -/
theorem bell_idempotent : bell * bell = bell := by
  ext x y
  rcases x with ⟨a,u⟩
  rcases y with ⟨b,v⟩
  fin_cases a <;> fin_cases u <;> fin_cases b <;> fin_cases v <;>
    norm_num [Matrix.mul_apply, Fintype.sum_prod_type, Fin.sum_univ_two, bell_entries]

/-- The actual first partial trace of the Bell state. -/
theorem bell_left : PartialTrace.left bell = halfIdentity := by
  ext a b
  fin_cases a <;> fin_cases b <;>
    norm_num [PartialTrace.left, halfIdentity, Fin.sum_univ_two, bell_entries]

/-- The actual second partial trace of the Bell state. -/
theorem bell_right : PartialTrace.right bell = halfIdentity := by
  ext u v
  fin_cases u <;> fin_cases v <;>
    norm_num [PartialTrace.right, halfIdentity, Fin.sum_univ_two, bell_entries]

/-- The reduced state is not idempotent. -/
theorem halfIdentity_not_idempotent : halfIdentity * halfIdentity ≠ halfIdentity := by
  intro h
  have he := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℂ => (M 0 0).re) h
  norm_num [halfIdentity, Matrix.mul_apply, Fin.sum_univ_two] at he

/-- The actual joint coordinate probabilities are 1/2 on 00 and 11 and zero
on the two crossed outcomes. -/
theorem bell_joint_probability (i j : Fin 2) :
    (binaryAtlas.tensor binaryAtlas).probability bell (i,j) =
      if i = j then (1/2:ℝ) else 0 := by
  fin_cases i <;> fin_cases j <;>
    norm_num [MatrixAtlas.probability, MatrixAtlas.tensor_proj, binaryAtlas,
      Matrix.trace, Matrix.diag_apply, Matrix.mul_apply, Matrix.kroneckerMap_apply,
      Fintype.sum_prod_type, Fin.sum_univ_two, bell_entries, Complex.mul_re]

/-- Each one-qubit coordinate marginal is uniform. -/
theorem halfIdentity_probability (i : Fin 2) :
    binaryAtlas.probability halfIdentity i = (1/2:ℝ) := by
  fin_cases i <;>
    norm_num [MatrixAtlas.probability, binaryAtlas, halfIdentity, Matrix.trace,
      Matrix.diag_apply, Matrix.mul_apply, Fin.sum_univ_two]

/-- The valid marginal identities do not imply factorization of joint probabilities. -/
theorem bell_probability_does_not_factor :
    (binaryAtlas.tensor binaryAtlas).probability bell (0,0) ≠
      binaryAtlas.probability (PartialTrace.left bell) 0 *
        binaryAtlas.probability (PartialTrace.right bell) 0 := by
  rw [bell_joint_probability, bell_left, bell_right, halfIdentity_probability]
  norm_num

/-- The density cannot be reconstructed by multiplying the two reduced states. -/
theorem bell_not_product_of_marginals :
    bell ≠ PartialTrace.left bell ⊗ₖ PartialTrace.right bell := by
  intro h
  have he := congrArg
    (fun M : Matrix (Fin 2 × Fin 2) (Fin 2 × Fin 2) ℂ => (M (0,0) (1,1)).re) h
  norm_num [bell_entries, bell_left, bell_right, halfIdentity, Matrix.kronecker_apply] at he

/-- Discarding coherence gives a different joint density with the same marginals. -/
def dephased : Matrix (Fin 2 × Fin 2) (Fin 2 × Fin 2) ℂ :=
  Matrix.diagonal (fun x => if x.1 = x.2 then (1/2:ℂ) else 0)

/-- The coherence-free comparison is also a positive density matrix. -/
theorem dephased_posSemidef : dephased.PosSemidef := by
  apply Matrix.PosSemidef.diagonal
  intro x
  by_cases hx : x.1 = x.2 <;> norm_num [hx, Complex.nonneg_iff]

/-- Its normalization is not merely inferred from a picture. -/
theorem dephased_trace_one : Matrix.trace dephased = 1 := by
  norm_num [dephased, Matrix.trace, Matrix.diag_apply, Fintype.sum_prod_type,
    Fin.sum_univ_two]

/-- The two different joint densities have identical actual reduced states. -/
theorem same_marginals :
    PartialTrace.left dephased = PartialTrace.left bell ∧
      PartialTrace.right dephased = PartialTrace.right bell := by
  rw [bell_left, bell_right]
  constructor
  · ext a b
    fin_cases a <;> fin_cases b <;>
      norm_num [PartialTrace.left, dephased, Matrix.diagonal_apply, Fin.sum_univ_two, halfIdentity]
  · ext u v
    fin_cases u <;> fin_cases v <;>
      norm_num [PartialTrace.right, dephased, Matrix.diagonal_apply, Fin.sum_univ_two, halfIdentity]

/-- Marginal agreement does not determine joint coherence. -/
theorem joint_states_differ : dephased ≠ bell := by
  intro h
  have he := congrArg
    (fun M : Matrix (Fin 2 × Fin 2) (Fin 2 × Fin 2) ℂ => (M (0,0) (1,1)).re) h
  norm_num [dephased, Matrix.diagonal_apply, bell_entries] at he

/-- The antisymmetric vector |01>-|10>, left unnormalized to keep exact integers. -/
def antisymmetricVector (x : Fin 2 × Fin 2) : ℂ :=
  if x = (0,1) then 1 else if x = (1,0) then -1 else 0

/-- An exact negative quadratic pairing for the partially transposed Bell state. -/
theorem bell_partialTranspose_pairing :
    star antisymmetricVector ⬝ᵥ
      (partialTransposeRight bell *ᵥ antisymmetricVector) = (-1:ℂ) := by
  norm_num [partialTransposeRight, antisymmetricVector, Matrix.mulVec, dotProduct,
    Fintype.sum_prod_type, Fin.sum_univ_two, bell_entries]

/-- The partial transpose fails positivity, established by the explicit vector. -/
theorem bell_partialTranspose_not_posSemidef : ¬ (partialTransposeRight bell).PosSemidef := by
  intro h
  have hq := h.dotProduct_mulVec_nonneg antisymmetricVector
  rw [bell_partialTranspose_pairing] at hq
  norm_num [Complex.nonneg_iff] at hq

/-- This excludes every finite nonnegative mixture of product pure states,
not just one tensor-product representation. -/
theorem bell_not_finite_product_mixture : ¬ HasFiniteProductDecomposition bell :=
  no_decomposition_of_partialTranspose_not_posSemidef bell bell_partialTranspose_not_posSemidef

/-- A trace factor cannot be omitted when the discarded factor is not normalized. -/
theorem partial_trace_identity_factor :
    PartialTrace.left ((1 : Matrix (Fin 2) (Fin 2) ℂ) ⊗ₖ
      (1 : Matrix (Fin 2) (Fin 2) ℂ)) = (2:ℂ) • (1 : Matrix (Fin 2) (Fin 2) ℂ) := by
  rw [PartialTrace.left_kronecker]
  norm_num

/-- A probability trajectory with direction a, interpreted locally near t=0. -/
def packetCurve (a t : ℝ) (i : Fin 2) : ℝ :=
  if i = 0 then 1/4 + a*t else 3/4 - a*t

/-- Its time-independent antisymmetric current matrix. -/
def packetCurrent (a : ℝ) (i j : Fin 2) : ℝ :=
  if i = 0 ∧ j = 1 then a else if i = 1 ∧ j = 0 then -a else 0

/-- The exact current is antisymmetric for any direction. -/
theorem packetCurrent_antisymm (a : ℝ) (i j : Fin 2) :
    packetCurrent a i j = -packetCurrent a j i := by
  fin_cases i <;> fin_cases j <;> simp [packetCurrent]

/-- The affine trajectories sum to one, but are not asserted globally nonnegative. -/
theorem packetCurve_sum_one (a t : ℝ) : (∑ i, packetCurve a t i) = 1 := by
  norm_num [packetCurve, Fin.sum_univ_two]
  ring

/-- All required logarithm and real-power arguments are positive at t=0. -/
theorem packetCurve_positive (a : ℝ) (i : Fin 2) : 0 < packetCurve a 0 i := by
  fin_cases i <;> norm_num [packetCurve]

/-- Actual component derivatives obey the declared current equation. -/
theorem packetCurve_hasDerivAt (a t : ℝ) (i : Fin 2) :
    HasDerivAt (fun s => packetCurve a s i) (∑ j, packetCurrent a i j) t := by
  fin_cases i
  · have h := ((hasDerivAt_id t).const_mul a).const_add (1/4:ℝ)
    change HasDerivAt (fun s : ℝ => 1/4 + a*s) (a*1) t at h
    simpa only [packetCurve, packetCurrent, Fin.sum_univ_two, ↓reduceIte,
      zero_add, mul_one] using h
  · have h := (hasDerivAt_const t (3/4:ℝ)).sub ((hasDerivAt_id t).const_mul a)
    change HasDerivAt (fun s : ℝ => 3/4 - a*s) (0-a*1) t at h
    simpa only [packetCurve, packetCurrent, Fin.sum_univ_two, ↓reduceIte,
      add_zero, mul_one, zero_sub] using h

/-- The general current theorem gives the exact entropy rate a log 3. -/
theorem packet_entropy_rate (a : ℝ) :
    HasDerivAt (fun t => entropy (packetCurve a t)) (a * Real.log 3) 0 := by
  have h := hasDerivAt_entropy_current (packetCurrent a) (packetCurrent_antisymm a)
    (packetCurve_hasDerivAt a 0) (packetCurve_positive a)
  norm_num [packetCurve, packetCurrent, Fin.sum_univ_two, one_div, Real.log_inv] at h
  convert h using 1
  ring

/-- Entropy can increase under antisymmetric exchange. -/
theorem positive_entropy_rate : 0 < deriv (fun t => entropy (packetCurve 1 t)) 0 := by
  rw [(packet_entropy_rate 1).deriv, one_mul]
  exact Real.log_pos (by norm_num)

/-- Reversing the same exchange makes the packet entropy decrease. -/
theorem negative_entropy_rate : deriv (fun t => entropy (packetCurve (-1) t)) 0 < 0 := by
  rw [(packet_entropy_rate (-1)).deriv, neg_one_mul]
  exact neg_neg_of_pos (Real.log_pos (by norm_num))

/-- The moment formula has its correct factor of one half. -/
theorem packet_powerSum_two_rate (a : ℝ) :
    HasDerivAt (fun t => powerSum (packetCurve a t) 2) (-a) 0 := by
  have h := hasDerivAt_powerSum_current 2 (packetCurrent a) (packetCurrent_antisymm a)
    (packetCurve_hasDerivAt a 0) (packetCurve_positive a)
  norm_num [packetCurve, packetCurrent, Fin.sum_univ_two] at h
  convert h using 1
  ring

/-- The Renyi denominator is exercised at a nonuniform positive distribution. -/
theorem packet_renyi_two_rate (a : ℝ) :
    HasDerivAt (fun t => renyi (packetCurve a t) 2) (8*a/5) 0 := by
  have h := hasDerivAt_renyi_current 2 (by norm_num) (packetCurrent a)
    (packetCurrent_antisymm a) (packetCurve_hasDerivAt a 0) (packetCurve_positive a)
  norm_num [packetCurve, packetCurrent, powerSum, Fin.sum_univ_two, Real.rpow_two] at h
  convert h using 1
  ring

end KomorebiPhysics.QuantumInformationExamples
