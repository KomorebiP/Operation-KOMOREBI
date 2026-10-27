import Komorebi.SufficientResolution.ContinuousMemory
import Komorebi.SufficientResolution.FiniteMemory

/-!
# Exact continuous-time closure and finite certificates

The analytic power/exponential bridge connects the unchanged discrete proof to
continuous evolution. Finite tests are generator-moment identities, never
agreement at finitely sampled nonzero times.
-/
set_option autoImplicit false
noncomputable section
namespace Komorebi.SufficientResolution.ContinuousBlockDynamics
open ContinuousFlow
variable {V H : Type*}
variable [NormedAddCommGroup V] [NormedSpace ℝ V]
variable [NormedAddCommGroup H] [NormedSpace ℝ H]
variable (b : ContinuousBlockDynamics V H)

/-- The n-th prepared generator moment (not a sampled flow). -/
def generatorPrepared (n : ℕ) : V →L[ℝ] V :=
  (ContinuousLinearMap.fst ℝ V H).comp
    ((b.generator^n).comp (ContinuousLinearMap.inl ℝ V H))

/-- Generator coefficient of the continuous hidden-return kernel. -/
def memoryMoment (n : ℕ) : V →L[ℝ] V := b.B.comp ((b.D^n).comp b.G)

@[simp] theorem generatorPrepared_toLinearMap (n : ℕ) :
    (b.generatorPrepared n).toLinearMap = b.linear.prepared n := by
  simp only [generatorPrepared, ContinuousLinearMap.toLinearMap_comp,
    ContinuousLinearMap.toLinearMap_pow, generator_toLinearMap]
  rfl

@[simp] theorem memoryMoment_toLinearMap (n : ℕ) :
    (b.memoryMoment n).toLinearMap = b.linear.memory n := by
  simp only [memoryMoment, ContinuousLinearMap.toLinearMap_comp,
    ContinuousLinearMap.toLinearMap_pow]
  rfl

 theorem memoryMoment_zero_iff (n : ℕ) : b.memoryMoment n = 0 ↔ b.linear.memory n = 0 := by
  rw [← b.memoryMoment_toLinearMap]
  exact ContinuousLinearMap.coe_inj.symm

 theorem generatorPrepared_eq_iff (n : ℕ) :
    b.generatorPrepared n = b.A^n ↔ b.linear.prepared n = b.linear.A^n := by
  rw [← b.generatorPrepared_toLinearMap]
  change b.generatorPrepared n = b.A^n ↔ _ = b.A.toLinearMap^n
  rw [← ContinuousLinearMap.toLinearMap_pow]
  exact ContinuousLinearMap.coe_inj.symm

variable [CompleteSpace V] [CompleteSpace H]

 theorem prepared_exact_iff_generator_powers :
    (∀ t, b.prepared t = flow b.A t) ↔ (∀ n, b.generatorPrepared n = b.A^n) :=
  compressed_flow_iff_powers (ContinuousLinearMap.fst ℝ V H)
    (ContinuousLinearMap.inl ℝ V H) b.generator b.A

 theorem prepared_exact_iff_discrete :
    (∀ t, b.prepared t = flow b.A t) ↔ (∀ n, b.linear.prepared n = b.linear.A^n) := by
  rw [b.prepared_exact_iff_generator_powers]
  exact forall_congr' (fun n => b.generatorPrepared_eq_iff n)

omit [CompleteSpace V] in
 theorem memory_zero_iff_moments :
    (∀ t, b.memory t = 0) ↔ (∀ n, b.memoryMoment n = 0) :=
  sandwich_flow_zero_iff b.B b.D b.G

omit [CompleteSpace V] in
 theorem memory_zero_iff_discrete :
    (∀ t, b.memory t = 0) ↔ (∀ n, b.linear.memory n = 0) := by
  rw [b.memory_zero_iff_moments]
  exact forall_congr' (fun n => b.memoryMoment_zero_iff n)

/-- Exact prepared dynamics iff the entire continuous memory kernel vanishes. -/
 theorem prepared_exact_iff_memory_zero :
    (∀ t, b.prepared t = flow b.A t) ↔ (∀ t, b.memory t = 0) := by
  rw [b.prepared_exact_iff_discrete, b.memory_zero_iff_discrete]
  exact b.linear.prepared_powers_iff_memory_zero

/-- Finite hidden dimension reduces continuous closure to finitely many moments. -/
 theorem prepared_exact_iff_finite_memory [FiniteDimensional ℝ H] :
    (∀ t, b.prepared t = flow b.A t) ↔
      (∀ k < Module.finrank ℝ H, b.memoryMoment k = 0) := by
  rw [b.prepared_exact_iff_discrete, b.linear.prepared_powers_iff_finrank_memory]
  exact forall_congr' (fun k => forall_congr' (fun _ => (b.memoryMoment_zero_iff k).symm))

/-- Finite generator identities suffice; these are not sampled-time equalities. -/
 theorem prepared_exact_iff_finite_generator [FiniteDimensional ℝ H] :
    (∀ t, b.prepared t = flow b.A t) ↔
      (∀ n ≤ Module.finrank ℝ H + 1, b.generatorPrepared n = b.A^n) := by
  rw [b.prepared_exact_iff_discrete, b.linear.prepared_powers_iff_finite_horizon]
  exact forall_congr' (fun n => forall_congr' (fun _ => (b.generatorPrepared_eq_iff n).symm))

/-- A monic hidden-generator annihilator provides a certificate without finrank. -/
 theorem prepared_exact_of_annihilator (p : Polynomial ℝ) (hp : p.Monic)
    (hroot : Polynomial.aeval b.linear.D p = 0)
    (h : ∀ k < p.natDegree, b.memoryMoment k = 0) :
    ∀ t, b.prepared t = flow b.A t := by
  rw [b.prepared_exact_iff_discrete, b.linear.prepared_powers_iff_memory_zero]
  exact b.linear.memory_zero_of_annihilator p hp hroot
    (fun k hk => (b.memoryMoment_zero_iff k).mp (h k hk))

 theorem prepared_exact_of_B_zero (hB : b.B = 0) : ∀ t, b.prepared t = flow b.A t := by
  rw [b.prepared_exact_iff_memory_zero]
  intro t
  simp [memory, hB]

 theorem prepared_exact_of_G_zero (hG : b.G = 0) : ∀ t, b.prepared t = flow b.A t := by
  rw [b.prepared_exact_iff_memory_zero]
  intro t
  simp [memory, hG]

/-- Exact closure for every hidden initial state is strictly stronger. -/
 theorem all_state_closure_iff_B_zero :
    (∀ t y z, b.visible y z t = flow b.A t y) ↔ b.B = 0 := by
  constructor
  · intro h
    ext z
    have hf : b.visible 0 z = fun t => flow b.A t 0 := funext (fun t => h t 0 z)
    have hl := b.hasDerivAt_visible 0 z 0
    rw [hf] at hl
    have he := hl.unique (hasDerivAt_flow_apply b.A 0 0)
    simpa using he
  · intro hB t y z
    have hd : ∀ s, HasDerivAt (b.visible y z) (b.A (b.visible y z s)) s := by
      intro s
      simpa [hB] using b.hasDerivAt_visible y z s
    simpa using homogeneous_solution b.A (b.visible y z) hd t

/-- Semigroup composition of prepared maps is equivalent to exact closure. -/
 theorem prepared_semigroup_iff_exact :
    (∀ s t, b.prepared (s+t) = b.prepared s * b.prepared t) ↔
      (∀ t, b.prepared t = flow b.A t) := by
  constructor
  · intro h t
    ext y
    have hd : ∀ u, HasDerivAt (fun s => b.prepared s y) (b.A (b.prepared u y)) u := by
      intro u
      have h0 : HasDerivAt (fun s => b.prepared s (b.prepared u y))
          (b.A (b.prepared u y)) (u-u) := by
        simpa using b.hasDerivAt_visible (b.prepared u y) 0 0
      have hh := h0.scomp (h := fun s : ℝ => s-u) u ((hasDerivAt_id u).sub_const u)
      have he (s : ℝ) : b.prepared (s-u) (b.prepared u y) = b.prepared s y := by
        have heq := congrArg (fun T : V →L[ℝ] V => T y) (h (s-u) u)
        simpa using heq.symm
      simpa only [Function.comp_def, he, one_smul] using hh
    simpa using homogeneous_solution b.A (fun s => b.prepared s y) hd t
  · intro h s t
    simp only [h, flow_add]

 theorem prepared_semigroup_iff_memory_zero :
    (∀ s t, b.prepared (s+t) = b.prepared s * b.prepared t) ↔
      (∀ t, b.memory t = 0) := by
  rw [b.prepared_semigroup_iff_exact, b.prepared_exact_iff_memory_zero]

/-- A nonzero hidden-return coefficient disproves all-time exact closure. -/
 theorem nonzero_moment_forces_nonclosure (k : ℕ) (hk : b.memoryMoment k ≠ 0) :
    ∃ t, b.prepared t ≠ flow b.A t := by
  classical
  by_contra h
  push Not at h
  apply hk
  exact (b.memory_zero_iff_moments.mp (b.prepared_exact_iff_memory_zero.mp h)) k

/-- Any failure has a coefficient witness below finite hidden dimension. -/
 theorem nonclosure_has_finite_moment [FiniteDimensional ℝ H]
    (h : ¬ ∀ t, b.prepared t = flow b.A t) :
    ∃ k < Module.finrank ℝ H, b.memoryMoment k ≠ 0 := by
  classical
  by_contra hn
  apply h
  rw [b.prepared_exact_iff_finite_memory]
  push Not at hn
  exact hn

end Komorebi.SufficientResolution.ContinuousBlockDynamics
