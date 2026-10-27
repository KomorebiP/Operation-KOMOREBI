module
public import KomorebiPhysics.SpectralSolutions

/-! Uniform-in-time approximation of each state and, on the generator domain,
of its actual velocity. Uniformity over the entire unit ball is not asserted. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace SpectralEvolution
open Filter BoundedSpectral HarmonicSurrogates SpectralTruncation
open scoped Topology BigOperators lp
variable (eig : ℕ → ℝ)

theorem cutoff_commutes (M : ℕ) (t : ℝ) (x : Space) :
    cutoff M (evolution eig t x) = evolution eig t (cutoff M x) := by
  apply lp.ext
  funext n
  simp only [cutoff_apply, evolution_apply]
  split_ifs <;> simp

/-- Each fixed-state cutoff error is exactly independent of time. -/
theorem cutoff_error_time (M : ℕ) (t : ℝ) (x : Space) :
    ‖evolution eig t x - cutoff M (evolution eig t x)‖ = ‖x - cutoff M x‖ := by
  rw [cutoff_commutes, ← map_sub, norm_preserved]

/-- All real times, but one fixed state: this is not operator-norm convergence. -/
theorem cutoff_uniform_in_time (x : Space) (ε : ℝ) (hε : 0 < ε) :
    ∃ N : ℕ, ∀ M ≥ N, ∀ t : ℝ,
      ‖evolution eig t x - cutoff M (evolution eig t x)‖ < ε := by
  obtain ⟨N, hN⟩ := Metric.tendsto_atTop.mp (cutoff_strong x) ε hε
  refine ⟨N, fun M hM t => ?_⟩
  rw [cutoff_error_time, norm_sub_rev]
  exact hN M hM

/-- Every finite-support cutoff is placed in the actual domain, even when the
original state is not in that domain. -/
def cutoffDomain (M : ℕ) (x : Space) : (DiagonalDomain.operator eig).domain :=
  ∑ n ∈ Finset.range M, DiagonalDomain.single eig n (x n)

theorem cutoffDomain_coe (M : ℕ) (x : Space) :
    (cutoffDomain eig M x : Space) = cutoff M x := by
  simp only [cutoffDomain, Submodule.coe_sum, DiagonalDomain.single_coe]
  symm
  simpa only [cutoff, diagonal_one, ContinuousLinearMap.id_apply] using truncate_vector_sum 1 M x

theorem cutoffDomain_action (M : ℕ) (x : (DiagonalDomain.operator eig).domain) :
    DiagonalDomain.operator eig (cutoffDomain eig M (x : Space)) =
      cutoff M (DiagonalDomain.operator eig x) := by
  apply lp.ext
  funext n
  simp only [DiagonalDomain.operator_apply, cutoffDomain_coe, cutoff_apply]
  split_ifs <;> simp

theorem cutoff_hasDerivAt (M : ℕ) (x : Space) (t : ℝ) :
    HasDerivAt (fun s => cutoff M (evolution eig s x))
      ((-Complex.I) • DiagonalDomain.operator eig
        (domainEvolution eig t (cutoffDomain eig M x))) t := by
  simpa only [cutoffDomain_coe, ← cutoff_commutes] using orbit_hasDerivAt eig (cutoffDomain eig M x) t

/-- Strong convergence of approximants cannot justify differentiating without
controlling this additional generator tail. -/
theorem cutoff_velocity_error (M : ℕ) (x : (DiagonalDomain.operator eig).domain) (t : ℝ) :
    ‖deriv (fun s => evolution eig s (x : Space)) t -
      deriv (fun s => cutoff M (evolution eig s (x : Space))) t‖ =
      ‖DiagonalDomain.operator eig x - cutoff M (DiagonalDomain.operator eig x)‖ := by
  rw [deriv_orbit, (cutoff_hasDerivAt eig M (x : Space) t).deriv,
    ← smul_sub, norm_smul, norm_neg, Complex.norm_I, one_mul,
    operator_commutes, operator_commutes, cutoffDomain_action, ← map_sub, norm_preserved]

theorem cutoff_velocity_uniform (x : (DiagonalDomain.operator eig).domain)
    (ε : ℝ) (hε : 0 < ε) :
    ∃ N : ℕ, ∀ M ≥ N, ∀ t : ℝ,
      ‖deriv (fun s => evolution eig s (x : Space)) t -
        deriv (fun s => cutoff M (evolution eig s (x : Space))) t‖ < ε := by
  obtain ⟨N, hN⟩ := Metric.tendsto_atTop.mp (cutoff_strong (DiagonalDomain.operator eig x)) ε hε
  refine ⟨N, fun M hM t => ?_⟩
  rw [cutoff_velocity_error, norm_sub_rev]
  exact hN M hM

end SpectralEvolution
end KomorebiPhysics
