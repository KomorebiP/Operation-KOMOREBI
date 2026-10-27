module

public import KomorebiPhysics.MixedTransfer
public import KomorebiPhysics.NonlinearFlow
public import KomorebiPhysics.UniversalBalance
public import Mathlib.Tactic.FinCases
public import Mathlib.Tactic.NormNum

/-!
Exact finite witnesses and counterexamples for Block 03. All values are exact.
The affine matrix curve is a local derivative witness at t=0 only; it is not
represented as a global von Neumann solution or as positive for every t.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.ExtensionExamples
open scoped BigOperators Matrix ComplexOrder
open MixedTransfer

/-- Two coordinate projectors, with their laws proved by exact entries. -/
def binaryAtlas : MatrixAtlas (Fin 2) (Fin 2) where
  proj i := if i = 0 then !![(1:ℂ), 0; 0, 0] else !![(0:ℂ), 0; 0, 1]
  mul_proj := by
    intro i j
    fin_cases i <;> fin_cases j <;> ext a b <;> fin_cases a <;> fin_cases b <;>
      norm_num [Matrix.mul_apply, Fin.sum_univ_two]
  sum_proj := by
    ext a b
    fin_cases a <;> fin_cases b <;> norm_num [Fin.sum_univ_two]
  hermitian := by
    intro i
    fin_cases i <;> ext a b <;> fin_cases a <;> fin_cases b <;>
      norm_num [Matrix.conjTranspose_apply]

/-- A trace-one, genuinely mixed, positive density matrix. -/
def density : Matrix (Fin 2) (Fin 2) ℂ := !![(1/2:ℂ), 1/4; 1/4, 1/2]

/-- Pauli y, with off-diagonal imaginary entries. -/
def hamiltonian : Matrix (Fin 2) (Fin 2) ℂ := !![0, -Complex.I; Complex.I, 0]

/-- Hermiticity is verified for the concrete Hamiltonian. -/
theorem hamiltonian_hermitian : hamiltonian.conjTranspose = hamiltonian := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [hamiltonian, Matrix.conjTranspose_apply]

/-- Concrete density Hermiticity. -/
theorem density_hermitian : density.conjTranspose = density := by
  ext i j
  fin_cases i <;> fin_cases j <;> norm_num [density, Matrix.conjTranspose_apply]

/-- Positive factorization, not a floating eigenvalue check. -/
theorem density_posSemidef : density.PosSemidef := by
  let B : Matrix (Fin 2) (Fin 2) ℂ := !![(1/2:ℂ), 0; 1/2, 0]
  let C : Matrix (Fin 2) (Fin 2) ℂ := !![(1/2:ℂ), 0; 0, 1/2]
  have h := (Matrix.posSemidef_self_mul_conjTranspose B).add
    (Matrix.posSemidef_self_mul_conjTranspose C)
  have heq : B * B.conjTranspose + C * C.conjTranspose = density := by
    ext i j
    fin_cases i <;> fin_cases j <;>
      norm_num [B, C, density, Matrix.mul_apply, Matrix.vecMul, dotProduct, Matrix.conjTranspose_apply, Fin.sum_univ_two]
  rwa [heq] at h

/-- Density normalization is exact. -/
theorem density_trace_one : Matrix.trace density = 1 := by
  norm_num [density, Matrix.trace, Matrix.diag, Fin.sum_univ_two]

/-- The normalized state is not a pure rank-one projector. -/
theorem density_not_idempotent : density * density ≠ density := by
  intro h
  have hc := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℂ => (M 0 0).re) h
  norm_num [density, Matrix.mul_apply, Fin.sum_univ_two, Complex.mul_re] at hc

/-- The exact mixed-state current is nonzero in both directions. -/
theorem mixed_current_values :
    binaryAtlas.current hamiltonian density 0 1 = -(1/2:ℝ) ∧
      binaryAtlas.current hamiltonian density 1 0 = (1/2:ℝ) := by
  norm_num [MatrixAtlas.current, MatrixAtlas.amplitude, binaryAtlas, hamiltonian, density,
    Matrix.trace, Matrix.diag, Matrix.mul_apply, Fin.sum_univ_two,
    Complex.mul_re, Complex.mul_im]

/-- Omitting the conjugation bar in (4.14) gives a false equality. -/
theorem conjugation_is_essential :
    binaryAtlas.amplitude hamiltonian density 1 0 ≠
      binaryAtlas.amplitude hamiltonian density 0 1 := by
  intro h
  have hi := congrArg Complex.im h
  norm_num [MatrixAtlas.amplitude, binaryAtlas, hamiltonian, density,
    Matrix.trace, Matrix.diag, Matrix.mul_apply, Fin.sum_univ_two,
    Complex.mul_re, Complex.mul_im] at hi

/-- A non-Hermitian matrix is not silently promoted to a density operator. -/
def badDensity : Matrix (Fin 2) (Fin 2) ℂ := !![0, 1; 0, 0]

/-- Deleting density Hermiticity can destroy current antisymmetry. -/
theorem density_hermiticity_is_essential :
    binaryAtlas.current hamiltonian badDensity 0 1 ≠
      -binaryAtlas.current hamiltonian badDensity 1 0 := by
  norm_num [MatrixAtlas.current, MatrixAtlas.amplitude, binaryAtlas, hamiltonian, badDensity,
    Matrix.trace, Matrix.diag, Matrix.mul_apply, Fin.sum_univ_two,
    Complex.mul_re, Complex.mul_im]

/-- An upper-triangular non-Hermitian Hamiltonian test matrix. -/
def badHamiltonian : Matrix (Fin 2) (Fin 2) ℂ := !![0, -Complex.I; 0, 0]

/-- Positive rho alone does not compensate for a non-Hermitian Hamiltonian. -/
theorem hamiltonian_hermiticity_is_essential :
    binaryAtlas.current badHamiltonian density 0 1 ≠
      -binaryAtlas.current badHamiltonian density 1 0 := by
  norm_num [MatrixAtlas.current, MatrixAtlas.amplitude, binaryAtlas, badHamiltonian, density,
    Matrix.trace, Matrix.diag, Matrix.mul_apply, Fin.sum_univ_two,
    Complex.mul_re, Complex.mul_im]

/-- An actual nonconstant matrix curve with the required slope at zero. -/
def localCurve (t : ℝ) : Matrix (Fin 2) (Fin 2) ℂ :=
  density + t • generator hamiltonian density

/-- Genuine matrix-valued derivative. The equation is asserted only at zero. -/
theorem localCurve_hasDerivAt :
    HasDerivAt localCurve (generator hamiltonian (localCurve 0)) 0 := by
  letI : NormedAddCommGroup (Matrix (Fin 2) (Fin 2) ℂ) :=
    inferInstanceAs (NormedAddCommGroup (Fin 2 → Fin 2 → ℂ))
  letI : NormedSpace ℝ (Matrix (Fin 2) (Fin 2) ℂ) :=
    inferInstanceAs (NormedSpace ℝ (Fin 2 → Fin 2 → ℂ))
  have h := (hasDerivAt_const (0:ℝ) density).add
    ((hasDerivAt_id (0:ℝ)).smul_const (generator hamiltonian density))
  simpa only [localCurve, zero_smul, add_zero, one_smul, zero_add] using h

/-- The new trace-derivative theorem produces the exact observed local rates. -/
theorem local_probability_derivatives :
    HasDerivAt (fun t => binaryAtlas.probability (localCurve t) 0) (-(1/2:ℝ)) 0 ∧
    HasDerivAt (fun t => binaryAtlas.probability (localCurve t) 1) (1/2:ℝ) 0 := by
  have hρ : (localCurve 0).conjTranspose = localCurve 0 := by
    simpa only [localCurve, zero_smul, add_zero] using density_hermitian
  have h0 := binaryAtlas.hasDerivAt_probability hamiltonian_hermitian hρ localCurve_hasDerivAt 0
  have h1 := binaryAtlas.hasDerivAt_probability hamiltonian_hermitian hρ localCurve_hasDerivAt 1
  simp only [localCurve, zero_smul, add_zero, Fin.sum_univ_two,
    binaryAtlas.current_diagonal hamiltonian density hamiltonian_hermitian density_hermitian,
    mixed_current_values.1, mixed_current_values.2, add_zero, zero_add] at h0 h1
  exact ⟨h0, h1⟩

/-- An overlapping binary incidence candidate, not an address-map incidence. -/
def overlap : Matrix (Fin 2) (Fin 2) ℝ := fun _ _ => 1

/-- The candidate meets the entrywise binary test. -/
theorem overlap_is_binary (i j : Fin 2) : overlap i j = 0 ∨ overlap i j = 1 := Or.inr rfl

/-- Binary entries alone do not ensure a binary matrix composite. -/
theorem overlap_product_not_binary :
    (overlap * overlap) 0 0 = 2 ∧ (overlap * overlap) 0 0 ≠ 0 ∧
      (overlap * overlap) 0 0 ≠ 1 := by
  norm_num [overlap, Matrix.mul_apply, Fin.sum_univ_two]

/-- No partition address can have this overlapping incidence. -/
theorem overlap_not_incidence :
    ¬ ∃ f : Fin 2 → Fin 2, RefinementTower.incidence f = overlap := by
  rintro ⟨f, hf⟩
  have h := RefinementTower.incidence_column_sum f 0
  rw [hf] at h
  norm_num [overlap, Fin.sum_univ_two] at h

/-- Nonzero sources are not cancelled by antisymmetric exchange. -/
theorem source_total_derivative (t : ℝ) :
    HasDerivAt (fun u : ℝ => ∑ _i : Fin 2, u) 2 t := by
  simpa only [Fin.sum_univ_two, Pi.add_apply, id_eq, one_add_one_eq_two] using (hasDerivAt_id t).add (hasDerivAt_id t)

/-- An exact counterexample to declaring every source-driven balance conserved. -/
theorem source_total_not_conserved :
    deriv (fun u : ℝ => ∑ _i : Fin 2, u) 0 ≠ 0 := by
  rw [(source_total_derivative 0).deriv]
  norm_num

end KomorebiPhysics.ExtensionExamples
