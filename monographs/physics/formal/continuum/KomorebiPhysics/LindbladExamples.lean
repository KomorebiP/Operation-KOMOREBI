module
public import KomorebiPhysics.LindbladDynamics
public import KomorebiPhysics.LindbladCoherence
public import KomorebiPhysics.DetailedBalance
public import KomorebiPhysics.ExtensionExamples

/-!
Exact witnesses and hypothesis-sensitivity tests for Block 05. The matrix
curve is a local derivative witness, not a globally positive ODE solution.
The old positive mixed density is reused, not counted as a new construction.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.LindbladExamples
open scoped BigOperators Matrix ComplexOrder Matrix.Norms.Elementwise
open LindbladJumps LindbladDynamics LindbladCoherence DetailedBalance
open ExtensionExamples (density hamiltonian)

/-- Source is the second index: 1 to 0 at rate 4, 0 to 1 at rate 1. -/
def rates : Fin 2 → Fin 2 → ℝ := ![![0, 4], ![1, 0]]

theorem rates_nonneg (a b : Fin 2) : 0 ≤ rates a b := by
  fin_cases a <;> fin_cases b <;> norm_num [rates]

/-- Actual amplitudes are square roots, not the rates themselves. -/
theorem jump_values :
    jump rates 0 1 = Matrix.single 0 1 (2:ℂ) ∧
    jump rates 1 0 = Matrix.single 1 0 (1:ℂ) := by
  have h4 : Real.sqrt (4:ℝ) = 2 := (Real.sqrt_eq_iff_eq_sq (by norm_num) (by norm_num)).mpr (by norm_num)
  norm_num [jump, rates, h4]

/-- Exact full coherent-matrix rate, including nonzero off-diagonal loss. -/
theorem generator_value :
    generator rates density = !![(3/2:ℂ), -5/8; -5/8, -3/2] := by
  ext i j
  fin_cases i <;> fin_cases j
  · change generator rates density 0 0 = (3/2:ℂ)
    rw [generator_diagonal rates density rates_nonneg 0]
    norm_num [rates, density, Fin.sum_univ_two]
  · change generator rates density 0 1 = (-5/8:ℂ)
    rw [generator_offdiag rates density rates_nonneg 0 1 (by decide)]
    norm_num [escapeRate, rates, density, Fin.sum_univ_two]
  · change generator rates density 1 0 = (-5/8:ℂ)
    rw [generator_offdiag rates density rates_nonneg 1 0 (by decide)]
    norm_num [escapeRate, rates, density, Fin.sum_univ_two]
  · change generator rates density 1 1 = (-3/2:ℂ)
    rw [generator_diagonal rates density rates_nonneg 1]
    norm_num [rates, density, Fin.sum_univ_two]

/-- Exact nonzero gain-minus-loss exchange for a genuinely mixed coherent state. -/
theorem current_values :
    current rates (population density) 0 1 = (3/2:ℝ) ∧
    current rates (population density) 1 0 = -(3/2:ℝ) := by
  norm_num [current, rates, population, density]

/-- Local actual matrix curve through the old positive normalized mixed state. -/
def localCurve (t : ℝ) : Matrix (Fin 2) (Fin 2) ℂ :=
  density + t • generator rates density

theorem localCurve_hasDerivAt :
    HasDerivAt localCurve (generator rates (localCurve 0)) 0 := by
  have h := ((hasDerivAt_id (0:ℝ)).smul_const (generator rates density)).const_add density
  change HasDerivAt (fun t : ℝ => density + t • generator rates density)
    (1 • generator rates density) 0 at h
  unfold localCurve
  simpa only [zero_smul, add_zero, one_smul] using h

/-- The general matrix theorem, not an assumed scalar rate, gives both derivatives. -/
theorem local_population_derivatives :
    HasDerivAt (fun t => population (localCurve t) 0) (3/2:ℝ) 0 ∧
    HasDerivAt (fun t => population (localCurve t) 1) (-(3/2:ℝ)) 0 := by
  have h0 := hasDerivAt_population rates_nonneg localCurve_hasDerivAt 0
  have h1 := hasDerivAt_population rates_nonneg localCurve_hasDerivAt 1
  constructor
  · convert h0 using 1; norm_num [localCurve, Fin.sum_univ_two, current, rates, population, density]
  · convert h1 using 1; norm_num [localCurve, Fin.sum_univ_two, current, rates, population, density]

/-- The same original matrix derivative gives an actual nonzero coherence slope. -/
theorem local_coherence_derivative :
    HasDerivAt (fun t => localCurve t 0 1) (-5/8:ℂ) 0 := by
  have h := hasDerivAt_coherence rates_nonneg localCurve_hasDerivAt 0 1 (by decide)
  convert h using 1; norm_num [escapeRate, Fin.sum_univ_two, rates, localCurve, density]

/-- Positive normalized detailed-balance reference for the asymmetric rates. -/
def reference : Fin 2 → ℝ := ![4/5, 1/5]

theorem reference_conditions :
    (∀ a, 0 < reference a) ∧ (∑ a, reference a) = 1 ∧ Balanced rates reference := by
  constructor
  · intro a; fin_cases a <;> norm_num [reference]
  constructor
  · norm_num [reference, Fin.sum_univ_two]
  · intro a b
    fin_cases a <;> fin_cases b <;> norm_num [rates, reference]

/-- Exact dissipation; no floating logarithm evaluations are used. -/
theorem dissipation_value :
    dissipation rates reference (population density) = 3 * Real.log 2 := by
  rw [dissipation_eq_activeFlux reference_conditions.2.2 rates_nonneg reference_conditions.1 (population density)
    (by intro a; fin_cases a <;> norm_num [population, density])]
  have h4 : Real.log (4:ℝ) = 2 * Real.log 2 := by
    calc
      _ = Real.log ((2:ℝ)^2) := by norm_num
      _ = _ := by rw [Real.log_pow]; norm_num
  norm_num [activeFluxCost, current, rates, population, density, Fin.sum_univ_two,
    Real.log_div, h4]
  ring

/-- Actual relative-entropy slope from the original matrix equation. -/
theorem local_relativeEntropy_derivative :
    HasDerivAt (fun t => relativeEntropy (population (localCurve t)) reference)
      (-(3 * Real.log 2)) 0 := by
  have h := hasDerivAt_matrix_relativeEntropy reference rates_nonneg
    reference_conditions.2.2 reference_conditions.1
    (by intro a; fin_cases a <;> norm_num [localCurve, population, density]) localCurve_hasDerivAt
  simpa only [localCurve, zero_smul, add_zero, dissipation_value] using h

/-- The sign is strict for this nonequilibrium witness. -/
theorem local_relativeEntropy_strictly_decreases :
    deriv (fun t => relativeEntropy (population (localCurve t)) reference) 0 < 0 := by
  rw [local_relativeEntropy_derivative.deriv]
  have h : 0 < Real.log (2:ℝ) := Real.log_pos (by norm_num)
  linarith

/-- Loss is at the source. Reversing that support gives a wrong operator. -/
theorem source_support_is_essential :
    (jump rates 0 1).conjTranspose * jump rates 0 1 ≠ Matrix.single 0 0 (4:ℂ) := by
  rw [jump_adjoint_mul rates 0 1 (rates_nonneg 0 1)]
  intro h
  have he := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℂ => (M 0 0).re) h
  norm_num [rates, Matrix.single_apply] at he

/-- Squaring a rate instead of its square root changes the generator normalization. -/
theorem square_root_is_essential :
    (Matrix.single (0:Fin 2) (1:Fin 2) (4:ℂ)).conjTranspose * Matrix.single (0:Fin 2) (1:Fin 2) (4:ℂ) ≠
      Matrix.single 1 1 (4:ℂ) := by
  intro h
  have he := congrArg (fun M : Matrix (Fin 2) (Fin 2) ℂ => (M 1 1).re) h
  norm_num [Matrix.single_apply, Matrix.mul_apply, Matrix.conjTranspose_apply, Fin.sum_univ_two] at he

/-- The square-root theorem is false for a negative rate. -/
theorem rate_nonnegativity_is_essential :
    (Real.sqrt (-4:ℝ) : ℂ) * (Real.sqrt (-4:ℝ) : ℂ) ≠ (-4:ℂ) := by
  norm_num [Real.sqrt_eq_zero_of_nonpos]

/-- The gain term alone adds trace; it cannot replace the full dissipator. -/
theorem loss_terms_are_essential :
    Matrix.trace (jump rates 0 1 * density * (jump rates 0 1).conjTranspose) = (2:ℂ) := by
  rw [jump_gain rates density 0 1 (rates_nonneg 0 1)]
  norm_num [Matrix.trace, Matrix.diag, Matrix.single_apply, rates, density, Fin.sum_univ_two]

/-- Omitting the half factor doubles loss and destroys zero trace. -/
theorem half_factor_is_essential :
    Matrix.trace (jump rates 0 1 * density * (jump rates 0 1).conjTranspose -
      ((jump rates 0 1).conjTranspose * jump rates 0 1 * density +
        density * ((jump rates 0 1).conjTranspose * jump rates 0 1))) = (-2:ℂ) := by
  rw [jump_values.1]
  norm_num [Matrix.trace, Matrix.diag, Matrix.single_apply, Matrix.mul_apply,
    Matrix.conjTranspose_apply, Matrix.vecMul, dotProduct, density, Fin.sum_univ_two]

/-- A self-jump changes coherences despite zero population derivative. -/
theorem self_jump_is_not_zero :
    dissipator (Matrix.single (0:Fin 2) 0 (2:ℂ)) density 0 1 = (-1/2:ℂ) := by
  norm_num [dissipator, Matrix.single_apply, Matrix.mul_apply,
    Matrix.conjTranspose_apply, Matrix.vecMul, dotProduct, density, Fin.sum_univ_two]

/-- Omitting coherent current changes the total population current. -/
theorem coherent_current_is_essential :
    quantumCurrent hamiltonian rates density 0 1 = 1 ∧
      quantumCurrent hamiltonian rates density 0 1 ≠ current rates (population density) 0 1 := by
  norm_num [quantumCurrent, coordinateAtlas, MixedTransfer.MatrixAtlas.current,
    MixedTransfer.MatrixAtlas.amplitude, Matrix.trace, Matrix.diag, Matrix.mul_apply,
    Matrix.single_apply, Fin.sum_univ_two, hamiltonian, density, current, population, rates,
    Complex.mul_re, Complex.mul_im]

/-- Zero edges are represented explicitly, not by a hidden log(0/0) convention. -/
theorem inactive_flux_is_zero (p : Fin 2 → ℝ) (a b : Fin 2) :
    activeFluxCost (fun _ _ => 0) p a b = 0 := by simp [activeFluxCost]

/-- Normalized positive distributions can differ with zero dissipation on a
reducible, empty transition graph. -/
theorem zero_dissipation_does_not_force_equilibrium :
    (∀ _a : Fin 2, 0 < (1/2:ℝ)) ∧ (∑ _a : Fin 2, (1/2:ℝ)) = 1 ∧
      dissipation (fun _ _ => 0) reference (fun _ => (1/2:ℝ)) = 0 ∧
      (fun _ : Fin 2 => (1/2:ℝ)) ≠ reference := by
  refine ⟨fun _ => by norm_num, by norm_num [Fin.sum_univ_two], ?_, ?_⟩
  · simp [dissipation, conductance]
  · intro h
    have he := congrFun h 0
    norm_num [reference] at he

/-- A second normalized positive state, biased toward the receiving sector. -/
def biasedDensity : Matrix (Fin 2) (Fin 2) ℂ := Matrix.diagonal ![3/4, 1/4]

theorem biasedDensity_conditions : biasedDensity.PosSemidef ∧ Matrix.trace biasedDensity = 1 := by
  constructor
  · apply Matrix.posSemidef_diagonal_iff.mpr
    intro i
    fin_cases i <;> norm_num [Complex.nonneg_iff]
  · norm_num [biasedDensity, Matrix.trace, Matrix.diag, Fin.sum_univ_two]

/-- A local solution witness for exactly the same nonnegative jump rates. -/
def biasedCurve (t : ℝ) : Matrix (Fin 2) (Fin 2) ℂ :=
  biasedDensity + t • generator rates biasedDensity

theorem biasedCurve_hasDerivAt :
    HasDerivAt biasedCurve (generator rates (biasedCurve 0)) 0 := by
  have h := ((hasDerivAt_id (0:ℝ)).smul_const (generator rates biasedDensity)).const_add biasedDensity
  change HasDerivAt (fun t : ℝ => biasedDensity + t • generator rates biasedDensity)
    (1 • generator rates biasedDensity) 0 at h
  unfold biasedCurve
  simpa only [zero_smul, add_zero, one_smul] using h

/-- A positive uniform reference is not a detailed-balance reference for these rates. -/
theorem uniform_reference_not_balanced : ¬ Balanced rates (fun _ => (1/2:ℝ)) := by
  intro h
  have he := h 0 1
  norm_num [rates] at he

/-- Without detailed balance with the chosen reference, the relative entropy
can increase even along an actual positive-state matrix-flow derivative. -/
theorem wrong_reference_derivative :
    HasDerivAt (fun t => relativeEntropy (population (biasedCurve t)) (fun _ => (1/2:ℝ)))
      (Real.log 3 / 4) 0 := by
  have hp : ∀ a, 0 < population (biasedCurve 0) a := by
    intro a
    fin_cases a <;> norm_num [population, biasedCurve, biasedDensity]
  have h := hasDerivAt_relativeEntropy_raw (fun _ : Fin 2 => (1/2:ℝ)) (by intro a; norm_num)
    hp (hasDerivAt_population rates_nonneg biasedCurve_hasDerivAt)
  convert h using 1
  norm_num [Fin.sum_univ_two, ratio, biasedCurve, biasedDensity, population, rates, current, Real.log_div]
  ring

theorem wrong_reference_strictly_increases :
    0 < deriv (fun t => relativeEntropy (population (biasedCurve t)) (fun _ => (1/2:ℝ))) 0 := by
  rw [wrong_reference_derivative.deriv]
  exact div_pos (Real.log_pos (by norm_num)) (by norm_num)

end KomorebiPhysics.LindbladExamples
