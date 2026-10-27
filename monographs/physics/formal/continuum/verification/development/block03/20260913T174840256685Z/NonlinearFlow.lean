module

public import KomorebiPhysics.Refinement

/-!
Chapter 4.1 (4.1)--(4.5). State- and time-dependent bounded skew flow.
Only the operator at the actual trajectory value is used in the first
energy derivative. No derivative of the generator map is assumed.
These are conservation theorems for given solutions, not ODE existence.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace NonlinearFlow
open scoped BigOperators
variable {H I J : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
  [Fintype I] [DecidableEq I] [Fintype J] [DecidableEq J]

/-- Actual state/time dependent vector field; this is not its linearization. -/
def field (A : H → ℝ → (H →L[ℂ] H)) (ψ : H) (t : ℝ) : H := A ψ t ψ

/-- Pointwise conservation only requires skewness at the state actually reached. -/
theorem hasDerivAt_total {A : H → ℝ → (H →L[ℂ] H)} {ψ : ℝ → H} {t : ℝ}
    (hA : IsSkew (A (ψ t) t)) (hψ : HasDerivAt ψ (field A (ψ t) t) t) :
    HasDerivAt (fun s => ‖ψ s‖ ^ 2) 0 t :=
  hasDerivAt_total_energy (A (ψ t) t) hA hψ

/-- Global conservation along a given all-time trajectory, without any
assumption on A away from that trajectory. -/
theorem total_constant (A : H → ℝ → (H →L[ℂ] H)) (ψ : ℝ → H)
    (hA : ∀ t, IsSkew (A (ψ t) t))
    (hψ : ∀ t, HasDerivAt ψ (field A (ψ t) t) t) (s t : ℝ) :
    ‖ψ s‖ ^ 2 = ‖ψ t‖ ^ 2 := by
  exact is_const_of_deriv_eq_zero
    (fun u => (hasDerivAt_total (hA u) (hψ u)).differentiableAt)
    (fun u => (hasDerivAt_total (hA u) (hψ u)).deriv) s t

/-- The packet balance (4.4) differentiates the actual projected norm. -/
theorem hasDerivAt_packet (P : Atlas H I) {A : H → ℝ → (H →L[ℂ] H)}
    {ψ : ℝ → H} {t : ℝ} (hψ : HasDerivAt ψ (field A (ψ t) t) t) (i : I) :
    HasDerivAt (fun s => P.energy (ψ s) i)
      (∑ j, P.current (A (ψ t) t) (ψ t) i j) t :=
  P.hasDerivAt_packet_energy (A (ψ t) t) hψ i

/-- The state dependence introduces no extra term into current antisymmetry. -/
theorem current_antisymm (P : Atlas H I) (A : H → ℝ → (H →L[ℂ] H))
    (ψ : H) (t : ℝ) (hA : IsSkew (A ψ t)) (i j : I) :
    P.current (A ψ t) ψ i j = -P.current (A ψ t) ψ j i :=
  P.current_antisymm (A ψ t) hA ψ i j

/-- Equation (4.5), cancellation of every instantaneous internal exchange. -/
theorem current_total_zero (P : Atlas H I) (A : H → ℝ → (H →L[ℂ] H))
    (ψ : H) (t : ℝ) (hA : IsSkew (A ψ t)) :
    (∑ i, ∑ j, P.current (A ψ t) ψ i j) = 0 :=
  P.total_current_zero (A ψ t) hA ψ

/-- Actual derivative of total packet energy, not a field in a solution structure. -/
theorem hasDerivAt_sum_packets (P : Atlas H I) {A : H → ℝ → (H →L[ℂ] H)}
    {ψ : ℝ → H} {t : ℝ} (hA : IsSkew (A (ψ t) t))
    (hψ : HasDerivAt ψ (field A (ψ t) t) t) :
    HasDerivAt (fun s => ∑ i, P.energy (ψ s) i) 0 t :=
  P.hasDerivAt_sum_packet_energy (A (ψ t) t) hA hψ

/-- The all-time packet sum is invariant along the nonlinear flow. -/
theorem sum_packets_constant (P : Atlas H I) (A : H → ℝ → (H →L[ℂ] H))
    (ψ : ℝ → H) (hA : ∀ t, IsSkew (A (ψ t) t))
    (hψ : ∀ t, HasDerivAt ψ (field A (ψ t) t) t) (s t : ℝ) :
    (∑ i, P.energy (ψ s) i) = ∑ i, P.energy (ψ t) i := by
  simpa only [Atlas.energy, ← P.norm_sq_reconstruct] using total_constant A ψ hA hψ s t

/-- A selected subsystem changes only through its current boundary. -/
theorem hasDerivAt_subset (P : Atlas H I) {A : H → ℝ → (H →L[ℂ] H)}
    {ψ : ℝ → H} {t : ℝ} (hA : IsSkew (A (ψ t) t))
    (hψ : HasDerivAt ψ (field A (ψ t) t) t) (s : Finset I) :
    HasDerivAt (fun u => ∑ i ∈ s, P.energy (ψ u) i)
      (∑ i ∈ s, ∑ j ∈ sᶜ, P.current (A (ψ t) t) (ψ t) i j) t :=
  P.hasDerivAt_subset_energy (A (ψ t) t) hA hψ s

/-- Exact fine-current expansion for a coarse packet along a nonlinear flow. -/
theorem hasDerivAt_coarse (P : Atlas H I) (f : I → J)
    {A : H → ℝ → (H →L[ℂ] H)} {ψ : ℝ → H} {t : ℝ}
    (hψ : HasDerivAt ψ (field A (ψ t) t) t) (a : J) :
    HasDerivAt (fun u => (P.coarsen f).energy (ψ u) a)
      (∑ b, ∑ i ∈ Atlas.fiber f a, ∑ j ∈ Atlas.fiber f b,
        P.current (A (ψ t) t) (ψ t) i j) t :=
  P.hasDerivAt_coarse_energy f (A (ψ t) t) hψ a

end NonlinearFlow
end KomorebiPhysics
