module

public import KomorebiPhysics.MixedTransfer
public import KomorebiPhysics.UniversalBalance
public import Mathlib.Analysis.Real.Sqrt
public import Mathlib.LinearAlgebra.Matrix.ConjTranspose

/-!
Chapter 4.7, equations (4.45)--(4.52). Actual square-root jump matrices,
full gain-minus-anticommutator generator, and actual population derivatives.
All matrices are finite. General coherent inputs are allowed. A trajectory
is an explicit hypothesis, not an existence or positivity-preservation claim.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.LindbladJumps
open scoped BigOperators Matrix
variable {n m : Type*} [Fintype n] [DecidableEq n]

/-- Receiving index a, source index b. This is the actual matrix unit weighted
by the real square root of the rate. Nonnegative rates are required below. -/
def jump (γ : n → n → ℝ) (a b : n) : Matrix n n ℂ :=
  Matrix.single a b (Real.sqrt (γ a b) : ℂ)

/-- The full Lindblad expression for one jump, including both loss terms. -/
def dissipator (L ρ : Matrix n n ℂ) : Matrix n n ℂ :=
  L * ρ * L.conjTranspose - (1/2 : ℂ) •
    (L.conjTranspose * L * ρ + ρ * (L.conjTranspose * L))

/-- Equation (4.46), summed over distinct ordered labels. Self-jumps are
excluded as in the source; they would affect coherences, not populations. -/
def generator (γ : n → n → ℝ) (ρ : Matrix n n ℂ) : Matrix n n ℂ :=
  ∑ a, ∑ b, if a = b then 0 else dissipator (jump γ a b) ρ

/-- Real diagonal populations. Literal complex diagonals agree under Hermiticity. -/
def population (ρ : Matrix n n ℂ) (a : n) : ℝ := (ρ a a).re

/-- Classical gain-minus-loss current, receiving index first. -/
def current (γ : n → n → ℝ) (p : n → ℝ) (a b : n) : ℝ :=
  γ a b * p b - γ b a * p a

/-- The actual square-root definition equals the stated scaled rank-one unit. -/
omit [Fintype n] in
theorem jump_eq_smul (γ : n → n → ℝ) (a b : n) :
    jump γ a b = (Real.sqrt (γ a b) : ℂ) • Matrix.single a b 1 := by
  simp [jump]

/-- Adjoint reverses source and receiver, leaving the real amplitude fixed. -/
omit [Fintype n] in
theorem jump_adjoint (γ : n → n → ℝ) (a b : n) :
    (jump γ a b).conjTranspose = Matrix.single b a (Real.sqrt (γ a b) : ℂ) := by
  simp [jump]

/-- Square-root normalization with its explicit nonnegativity hypothesis. -/
theorem sqrt_rate_product {r : ℝ} (hr : 0 ≤ r) :
    (Real.sqrt r : ℂ) * (Real.sqrt r : ℂ) = (r : ℂ) := by
  rw [← Complex.ofReal_mul, Real.mul_self_sqrt hr]

/-- Equation (4.52): loss is supported at the source, not the receiver. -/
omit [Fintype n] in
theorem jump_adjoint_mul (γ : n → n → ℝ) (a b : n) (hγ : 0 ≤ γ a b) :
    (jump γ a b).conjTranspose * jump γ a b = Matrix.single b b (γ a b : ℂ) := by
  rw [jump_adjoint, jump, Matrix.single_mul_single_same, sqrt_rate_product hγ]

/-- The opposite product is supported at the receiving label. -/
theorem jump_mul_adjoint (γ : n → n → ℝ) (a b : n) (hγ : 0 ≤ γ a b) :
    jump γ a b * (jump γ a b).conjTranspose = Matrix.single a a (γ a b : ℂ) := by
  rw [jump_adjoint, jump, Matrix.single_mul_single_same, sqrt_rate_product hγ]

/-- Equation (4.51), for every matrix rho, without deleting coherences by assumption. -/
theorem jump_gain (γ : n → n → ℝ) (ρ : Matrix n n ℂ) (a b : n)
    (hγ : 0 ≤ γ a b) :
    jump γ a b * ρ * (jump γ a b).conjTranspose =
      Matrix.single a a ((γ a b : ℂ) * ρ b b) := by
  rw [jump_adjoint, jump, Matrix.single_mul_mul_single]
  congr 1
  calc
    _ = ((Real.sqrt (γ a b) : ℂ) * (Real.sqrt (γ a b) : ℂ)) * ρ b b := by ring
    _ = _ := by rw [sqrt_rate_product hγ]

/-- Left multiplication by an actual matrix unit. -/
theorem single_mul_entry (a b i j : n) (c : ℂ) (ρ : Matrix n n ℂ) :
    (Matrix.single a b c * ρ) i j = if a = i then c * ρ b j else 0 := by
  by_cases h : a = i
  · subst i
    simp
  · exact (Matrix.single_mul_apply_of_ne c a b i j (Ne.symm h) ρ).trans (ite_eq_right h).symm

/-- Right multiplication by an actual matrix unit. -/
theorem mul_single_entry (a b i j : n) (c : ℂ) (ρ : Matrix n n ℂ) :
    (ρ * Matrix.single a b c) i j = if b = j then ρ i a * c else 0 := by
  by_cases h : b = j
  · subst j
    simp
  · exact (Matrix.mul_single_apply_of_ne c a b i j (Ne.symm h) ρ).trans (ite_eq_right h).symm

/-- Every entry of the one-jump generator, retaining off-diagonal loss. -/
theorem dissipator_jump_entry (γ : n → n → ℝ) (ρ : Matrix n n ℂ)
    (a b i j : n) (hγ : 0 ≤ γ a b) :
    dissipator (jump γ a b) ρ i j =
      (if a = i ∧ a = j then (γ a b : ℂ) * ρ b b else 0) -
        (1/2 : ℂ) * ((if b = i then (γ a b : ℂ) * ρ b j else 0) +
          (if b = j then ρ i b * (γ a b : ℂ) else 0)) := by
  rw [dissipator, jump_gain γ ρ a b hγ, jump_adjoint_mul γ a b hγ]
  simp only [Matrix.sub_apply, Matrix.add_apply, Matrix.smul_apply, smul_eq_mul,
    Matrix.single_apply, single_mul_entry, mul_single_entry]

/-- A single jump gives equal diagonal gain and loss at the correct labels. -/
theorem dissipator_jump_diagonal (γ : n → n → ℝ) (ρ : Matrix n n ℂ)
    (a b i : n) (hγ : 0 ≤ γ a b) :
    dissipator (jump γ a b) ρ i i =
      (if a = i then (γ a b : ℂ) * ρ b b else 0) -
        (if b = i then (γ a b : ℂ) * ρ b b else 0) := by
  rw [dissipator_jump_entry γ ρ a b i i hγ]
  by_cases ha : a = i <;> by_cases hb : b = i
  all_goals simp only [ha, hb, and_self, ite_true, ite_false]
  all_goals try { subst i }
  all_goals ring

/-- Self-jumps have zero population contribution. This does not assert a
zero full dissipator for self-jumps. -/
theorem self_jump_diagonal (γ : n → n → ℝ) (ρ : Matrix n n ℂ)
    (a i : n) (hγ : 0 ≤ γ a a) : dissipator (jump γ a a) ρ i i = 0 := by
  rw [dissipator_jump_diagonal γ ρ a a i hγ, sub_self]

/-- Literal complex diagonal reduction of the actual distinct-jump sum. -/
theorem generator_diagonal (γ : n → n → ℝ) (ρ : Matrix n n ℂ)
    (hγ : ∀ a b, 0 ≤ γ a b) (i : n) :
    generator γ ρ i i = ∑ b, ((γ i b : ℂ) * ρ b b - (γ b i : ℂ) * ρ i i) := by
  have hterm (a b : n) :
      (if a = b then (0 : Matrix n n ℂ) else dissipator (jump γ a b) ρ) i i =
        (if a = i then (γ a b : ℂ) * ρ b b else 0) -
          (if b = i then (γ a b : ℂ) * ρ b b else 0) := by
    by_cases hab : a = b
    · subst b
      simp
    · simp only [hab, ite_false, dissipator_jump_diagonal γ ρ a b i (hγ a b)]
  have hin : (∑ a, ∑ b, if a = i then (γ a b : ℂ) * ρ b b else 0) =
      ∑ b, (γ i b : ℂ) * ρ b b := by
    rw [Finset.sum_comm]
    simp
  have hout : (∑ a, ∑ b, if b = i then (γ a b : ℂ) * ρ b b else 0) =
      ∑ a, (γ a i : ℂ) * ρ i i := by simp
  simp only [generator, Matrix.sum_apply, hterm, Finset.sum_sub_distrib]
  rw [hin, hout]

/-- Equation (4.48) is a consequence of the matrix calculation. -/
theorem population_rate (γ : n → n → ℝ) (ρ : Matrix n n ℂ)
    (hγ : ∀ a b, 0 ≤ γ a b) (i : n) :
    population (generator γ ρ) i = ∑ b, current γ (population ρ) i b := by
  simp only [population, generator_diagonal γ ρ hγ, Complex.re_sum,
    Complex.sub_re, Complex.mul_re, Complex.ofReal_re, Complex.ofReal_im,
    zero_mul, sub_zero, current]

/-- Hermitian input gives literally real diagonal probabilities. -/
omit [Fintype n] [DecidableEq n] in
theorem population_cast (ρ : Matrix n n ℂ) (hρ : ρ.conjTranspose = ρ) (i : n) :
    (population ρ i : ℂ) = ρ i i := by
  have h := congrArg (fun M : Matrix n n ℂ => (M i i).im) hρ
  simp only [Matrix.conjTranspose_apply, Complex.star_def, Complex.conj_im] at h
  apply Complex.ext
  · rfl
  · simp only [Complex.ofReal_im]
    linarith

/-- Equation (4.49), without assuming any current antisymmetry. -/
omit [Fintype n] [DecidableEq n] in
theorem current_antisymm (γ : n → n → ℝ) (p : n → ℝ) (a b : n) :
    current γ p a b = -current γ p b a := by unfold current; ring

/-- Diagonal rate entries cancel in population current even when nonzero. -/
omit [Fintype n] [DecidableEq n] in
theorem current_diagonal (γ : n → n → ℝ) (p : n → ℝ) (a : n) :
    current γ p a a = 0 := by simp [current]

/-- Actual population derivatives from the original matrix derivative. -/
theorem hasDerivAt_population {γ : n → n → ℝ} {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hγ : ∀ a b, 0 ≤ γ a b) (hρ : HasDerivAt ρ (generator γ (ρ t)) t) (i : n) :
    HasDerivAt (fun s => population (ρ s) i)
      (∑ b, current γ (population (ρ t)) i b) t := by
  have h := Complex.reCLM.hasFDerivAt.comp_hasDerivAt t
    (MixedTransfer.hasDerivAt_entry hρ i i)
  change HasDerivAt (fun s => population (ρ s) i) (population (generator γ (ρ t)) i) t at h
  rwa [population_rate γ (ρ t) hγ] at h

/-- A general single-jump dissipator has zero trace, for arbitrary L and rho. -/
omit [DecidableEq n] in
theorem trace_dissipator (L ρ : Matrix n n ℂ) : Matrix.trace (dissipator L ρ) = 0 := by
  simp only [dissipator, Matrix.trace_sub, Matrix.trace_smul, Matrix.trace_add,
    smul_eq_mul]
  rw [Matrix.trace_mul_cycle L ρ L.conjTranspose,
    Matrix.trace_mul_comm ρ (L.conjTranspose * L)]
  ring

/-- The generator has zero complex trace even without rate nonnegativity. -/
theorem trace_generator (γ : n → n → ℝ) (ρ : Matrix n n ℂ) :
    Matrix.trace (generator γ ρ) = 0 := by
  simp only [generator, Matrix.trace_sum]
  apply Finset.sum_eq_zero
  intro a _
  apply Finset.sum_eq_zero
  intro b _
  by_cases hab : a = b <;> simp [hab, trace_dissipator]

/-- The full single-jump expression maps Hermitian rho to a Hermitian rate. -/
omit [DecidableEq n] in
theorem dissipator_hermitian (L ρ : Matrix n n ℂ) (hρ : ρ.conjTranspose = ρ) :
    (dissipator L ρ).conjTranspose = dissipator L ρ := by
  simp only [dissipator, Matrix.conjTranspose_sub, Matrix.conjTranspose_add,
    Matrix.conjTranspose_smul, Matrix.conjTranspose_mul,
    Matrix.conjTranspose_conjTranspose, hρ]
  norm_num only [star_div₀, star_one, star_ofNat]
  simp only [Matrix.mul_assoc]
  congr 2
  exact add_comm _ _

/-- Hermiticity of the actual summed generator is derived from its expression. -/
theorem generator_hermitian (γ : n → n → ℝ) (ρ : Matrix n n ℂ)
    (hρ : ρ.conjTranspose = ρ) :
    (generator γ ρ).conjTranspose = generator γ ρ := by
  simp only [generator, Matrix.conjTranspose_sum]
  apply Finset.sum_congr rfl
  intro a _
  apply Finset.sum_congr rfl
  intro b _
  by_cases hab : a = b <;> simp [hab, dissipator_hermitian _ _ hρ]

/-- Actual complex-trace derivative, without a separate scalar balance input. -/
theorem hasDerivAt_trace {γ : n → n → ℝ} {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hρ : HasDerivAt ρ (generator γ (ρ t)) t) :
    HasDerivAt (fun s => Matrix.trace (ρ s)) 0 t := by
  simpa only [one_mul, trace_generator] using MixedTransfer.hasDerivAt_trace_mul 1 hρ

/-- Total population cancellation is a finite antisymmetric sum theorem. -/
theorem total_current_zero (γ : n → n → ℝ) (p : n → ℝ) :
    (∑ a, ∑ b, current γ p a b) = 0 :=
  antisymmetric_sum_zero _ Finset.univ (fun a _ b _ => current_antisymm γ p a b)

/-- Actual total-population derivative. -/
theorem hasDerivAt_total_population {γ : n → n → ℝ} {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hγ : ∀ a b, 0 ≤ γ a b) (hρ : HasDerivAt ρ (generator γ (ρ t)) t) :
    HasDerivAt (fun s => ∑ i, population (ρ s) i) 0 t := by
  simpa only [total_current_zero] using HasDerivAt.fun_sum (u := Finset.univ)
    (fun i _ => hasDerivAt_population hγ hρ i)

/-- Exact subsystem flux from the original matrix flow. -/
theorem hasDerivAt_subset_population {γ : n → n → ℝ} {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hγ : ∀ a b, 0 ≤ γ a b) (hρ : HasDerivAt ρ (generator γ (ρ t)) t) (C : Finset n) :
    HasDerivAt (fun s => ∑ i ∈ C, population (ρ s) i)
      (∑ i ∈ C, ∑ j ∈ Cᶜ, current γ (population (ρ t)) i j) t := by
  have h := HasDerivAt.fun_sum (u := C) (fun i _ => hasDerivAt_population hγ hρ i)
  rwa [UniversalBalance.boundary_sum _ (current_antisymm γ (population (ρ t))) C] at h

/-- All-time trace conservation for an actual given flow; the rates may
vary with state and time. This is not an existence theorem. -/
theorem trace_constant (γ : Matrix n n ℂ → ℝ → n → n → ℝ)
    (ρ : ℝ → Matrix n n ℂ)
    (hρ : ∀ t, HasDerivAt ρ (generator (γ (ρ t) t) (ρ t)) t) (s t : ℝ) :
    Matrix.trace (ρ s) = Matrix.trace (ρ t) :=
  is_const_of_deriv_eq_zero
    (fun u => (hasDerivAt_trace (hρ u)).differentiableAt)
    (fun u => (hasDerivAt_trace (hρ u)).deriv) s t

end KomorebiPhysics.LindbladJumps
