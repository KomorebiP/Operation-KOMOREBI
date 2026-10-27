module

public import KomorebiPhysics.LindbladJumps
public import KomorebiPhysics.InformationTransport

/-!
Additional bridges for Chapter 4.7: actual coordinate atlas, positivity and
normalization of populations, Hamiltonian plus jump evolution, exact coarse
flux, and information derivatives. The full quantum current retains its
Hamiltonian contribution. Detailed-balance monotonicity for the pure-jump
model is not silently extended to this combined generator.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.LindbladDynamics
open scoped BigOperators Matrix
open LindbladJumps InformationTransport
variable {n m : Type*} [Fintype n] [DecidableEq n]

/-- Actual complete coordinate matrix atlas for every finite basis. -/
def coordinateAtlas : MixedTransfer.MatrixAtlas n n where
  proj i := Matrix.single i i 1
  mul_proj := by
    intro i j
    by_cases hij : i = j
    · subst j
      simp
    · simp [hij, Matrix.single_mul_single_of_ne _ _ _ _ hij]
  sum_proj := Matrix.sum_single_one
  hermitian := by intro i; simp

/-- Coordinate trace probability is exactly the diagonal population. -/
theorem coordinate_probability (ρ : Matrix n n ℂ) (i : n) :
    (coordinateAtlas : MixedTransfer.MatrixAtlas n n).probability ρ i = population ρ i := by
  simp [MixedTransfer.MatrixAtlas.probability, coordinateAtlas, Matrix.trace_single_mul, population]

/-- Already-positive normalized density matrices have genuine diagonal probabilities. -/
theorem population_normalized (ρ : Matrix n n ℂ) (hρ : ρ.PosSemidef)
    (htrace : Matrix.trace ρ = 1) :
    (∑ i, population ρ i) = 1 ∧ ∀ i, 0 ≤ population ρ i ∧ population ρ i ≤ 1 := by
  simpa only [coordinate_probability] using
    (coordinateAtlas : MixedTransfer.MatrixAtlas n n).probability_normalized ρ hρ htrace

/-- The full finite matrix generator with both coherent and incoherent evolution. -/
def quantumGenerator (H : Matrix n n ℂ) (γ : n → n → ℝ) (ρ : Matrix n n ℂ) : Matrix n n ℂ :=
  MixedTransfer.generator H ρ + LindbladJumps.generator γ ρ

/-- Total packet current, retaining the Hamiltonian contribution. -/
def quantumCurrent (H : Matrix n n ℂ) (γ : n → n → ℝ) (ρ : Matrix n n ℂ) (a b : n) : ℝ :=
  (coordinateAtlas : MixedTransfer.MatrixAtlas n n).current H ρ a b + current γ (population ρ) a b

/-- Trace vanishes for the combined generator. -/
theorem trace_quantumGenerator (H : Matrix n n ℂ) (γ : n → n → ℝ) (ρ : Matrix n n ℂ) :
    Matrix.trace (quantumGenerator H γ ρ) = 0 := by
  simp [quantumGenerator, Matrix.trace_add, MixedTransfer.trace_generator, LindbladJumps.trace_generator]

/-- The coherent-plus-jump rate is Hermitian at Hermitian inputs. -/
theorem quantumGenerator_hermitian (H : Matrix n n ℂ) (γ : n → n → ℝ) (ρ : Matrix n n ℂ)
    (hH : H.conjTranspose = H) (hρ : ρ.conjTranspose = ρ) :
    (quantumGenerator H γ ρ).conjTranspose = quantumGenerator H γ ρ := by
  simp only [quantumGenerator, Matrix.conjTranspose_add,
    MixedTransfer.generator_hermitian H ρ hH hρ, generator_hermitian γ ρ hρ]

/-- Total current antisymmetry, with the Hamiltonian and density hypotheses visible. -/
theorem quantumCurrent_antisymm (H : Matrix n n ℂ) (γ : n → n → ℝ) (ρ : Matrix n n ℂ)
    (hH : H.conjTranspose = H) (hρ : ρ.conjTranspose = ρ) (a b : n) :
    quantumCurrent H γ ρ a b = -quantumCurrent H γ ρ b a := by
  unfold quantumCurrent
  rw [(coordinateAtlas : MixedTransfer.MatrixAtlas n n).current_antisymm H ρ hH hρ a b,
    current_antisymm γ (population ρ) a b]
  ring

/-- The actual combined generator gives the sum of coherent and jump currents. -/
theorem quantum_population_rate (H : Matrix n n ℂ) (γ : n → n → ℝ) (ρ : Matrix n n ℂ)
    (hγ : ∀ a b, 0 ≤ γ a b) (hH : H.conjTranspose = H) (hρ : ρ.conjTranspose = ρ) (i : n) :
    population (quantumGenerator H γ ρ) i = ∑ b, quantumCurrent H γ ρ i b := by
  have hu := (coordinateAtlas : MixedTransfer.MatrixAtlas n n).probability_rate H ρ hH hρ i
  change (coordinateAtlas : MixedTransfer.MatrixAtlas n n).probability (MixedTransfer.generator H ρ) i = _ at hu
  rw [coordinate_probability] at hu
  change population (MixedTransfer.generator H ρ) i + population (LindbladJumps.generator γ ρ) i = _
  rw [hu, population_rate γ ρ hγ]
  simp only [quantumCurrent, Finset.sum_add_distrib]

/-- Actual combined population derivative, starting with only the original matrix flow. -/
theorem hasDerivAt_quantum_population {H : Matrix n n ℂ} {γ : n → n → ℝ}
    {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hγ : ∀ a b, 0 ≤ γ a b) (hH : H.conjTranspose = H) (hρt : (ρ t).conjTranspose = ρ t)
    (hρ : HasDerivAt ρ (quantumGenerator H γ (ρ t)) t) (i : n) :
    HasDerivAt (fun s => population (ρ s) i) (∑ b, quantumCurrent H γ (ρ t) i b) t := by
  have h := Complex.reCLM.hasFDerivAt.comp_hasDerivAt t (MixedTransfer.hasDerivAt_entry hρ i i)
  change HasDerivAt (fun s => population (ρ s) i) (population (quantumGenerator H γ (ρ t)) i) t at h
  rwa [quantum_population_rate H γ (ρ t) hγ hH hρt] at h

/-- Actual total trace derivative for combined evolution. -/
theorem hasDerivAt_quantum_trace {H : Matrix n n ℂ} {γ : n → n → ℝ}
    {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hρ : HasDerivAt ρ (quantumGenerator H γ (ρ t)) t) :
    HasDerivAt (fun s => Matrix.trace (ρ s)) 0 t := by
  simpa only [one_mul, trace_quantumGenerator] using MixedTransfer.hasDerivAt_trace_mul 1 hρ

/-- Exact subsystem flux for the combined dynamics, not just a classical surrogate. -/
theorem hasDerivAt_quantum_subset {H : Matrix n n ℂ} {γ : n → n → ℝ}
    {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hγ : ∀ a b, 0 ≤ γ a b) (hH : H.conjTranspose = H) (hρt : (ρ t).conjTranspose = ρ t)
    (hρ : HasDerivAt ρ (quantumGenerator H γ (ρ t)) t) (C : Finset n) :
    HasDerivAt (fun s => ∑ i ∈ C, population (ρ s) i)
      (∑ i ∈ C, ∑ j ∈ Cᶜ, quantumCurrent H γ (ρ t) i j) t := by
  have h := HasDerivAt.fun_sum (u := C)
    (fun i _ => hasDerivAt_quantum_population hγ hH hρt hρ i)
  rwa [UniversalBalance.boundary_sum _ (quantumCurrent_antisymm H γ (ρ t) hH hρt) C] at h

/-- Exact coarse populations and double-summed fluxes for arbitrary address maps.
No closed, state-independent coarse Markov rate matrix is presumed. -/
theorem hasDerivAt_coarse_population [Fintype m] [DecidableEq m] (f : n → m)
    {γ : n → n → ℝ} {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hγ : ∀ a b, 0 ≤ γ a b) (hρ : HasDerivAt ρ (LindbladJumps.generator γ (ρ t)) t) (a : m) :
    HasDerivAt (fun s => ∑ i ∈ Atlas.fiber f a, population (ρ s) i)
      (∑ b, ∑ i ∈ Atlas.fiber f a, ∑ j ∈ Atlas.fiber f b, current γ (population (ρ t)) i j) t := by
  have h := UniversalBalance.hasDerivAt_coarse (s := fun _ => 0) f
    (fun i => by simpa only [zero_add] using hasDerivAt_population hγ hρ i) a
  simpa only [Finset.sum_const_zero, zero_add] using h

/-- Shannon derivative from the original jump-matrix flow, with strict positivity. -/
theorem hasDerivAt_entropy {γ : n → n → ℝ} {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hγ : ∀ a b, 0 ≤ γ a b) (hρ : HasDerivAt ρ (LindbladJumps.generator γ (ρ t)) t)
    (hp : ∀ i, 0 < population (ρ t) i) :
    HasDerivAt (fun s => entropy (population (ρ s)))
      (-(1/2 : ℝ) * ∑ i, ∑ j, current γ (population (ρ t)) i j *
        Real.log (population (ρ t) i / population (ρ t) j)) t :=
  hasDerivAt_entropy_current _ (current_antisymm γ (population (ρ t)))
    (hasDerivAt_population hγ hρ) hp

/-- Real-order moment derivative from the actual jump-matrix flow. -/
theorem hasDerivAt_powerSum {γ : n → n → ℝ} {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (q : ℝ) (hγ : ∀ a b, 0 ≤ γ a b) (hρ : HasDerivAt ρ (LindbladJumps.generator γ (ρ t)) t)
    (hp : ∀ i, 0 < population (ρ t) i) :
    HasDerivAt (fun s => powerSum (population (ρ s)) q)
      ((q/2) * ∑ i, ∑ j, current γ (population (ρ t)) i j *
        ((population (ρ t) i) ^ (q-1) - (population (ρ t) j) ^ (q-1))) t :=
  hasDerivAt_powerSum_current q _ (current_antisymm γ (population (ρ t)))
    (hasDerivAt_population hγ hρ) hp

/-- Renyi derivative retains q != 1 and its nonempty positive-domain conditions. -/
theorem hasDerivAt_renyi [Nonempty n] {γ : n → n → ℝ} {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (q : ℝ) (hq : q ≠ 1) (hγ : ∀ a b, 0 ≤ γ a b)
    (hρ : HasDerivAt ρ (LindbladJumps.generator γ (ρ t)) t) (hp : ∀ i, 0 < population (ρ t) i) :
    HasDerivAt (fun s => renyi (population (ρ s)) q)
      (q / (2 * (1-q) * powerSum (population (ρ t)) q) *
        ∑ i, ∑ j, current γ (population (ρ t)) i j *
          ((population (ρ t) i) ^ (q-1) - (population (ρ t) j) ^ (q-1))) t :=
  hasDerivAt_renyi_current q hq _ (current_antisymm γ (population (ρ t)))
    (hasDerivAt_population hγ hρ) hp

/-- The Shannon identity extends to combined evolution with the full current;
it does not acquire an unconditional production sign. -/
theorem hasDerivAt_quantum_entropy {H : Matrix n n ℂ} {γ : n → n → ℝ}
    {ρ : ℝ → Matrix n n ℂ} {t : ℝ}
    (hγ : ∀ a b, 0 ≤ γ a b) (hH : H.conjTranspose = H) (hρt : (ρ t).conjTranspose = ρ t)
    (hρ : HasDerivAt ρ (quantumGenerator H γ (ρ t)) t)
    (hp : ∀ i, 0 < population (ρ t) i) :
    HasDerivAt (fun s => entropy (population (ρ s)))
      (-(1/2 : ℝ) * ∑ i, ∑ j, quantumCurrent H γ (ρ t) i j *
        Real.log (population (ρ t) i / population (ρ t) j)) t :=
  hasDerivAt_entropy_current _ (quantumCurrent_antisymm H γ (ρ t) hH hρt)
    (hasDerivAt_quantum_population hγ hH hρt hρ) hp

end KomorebiPhysics.LindbladDynamics
