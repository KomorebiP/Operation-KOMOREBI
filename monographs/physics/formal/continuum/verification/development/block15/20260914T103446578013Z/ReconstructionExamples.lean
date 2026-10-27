module
public import KomorebiPhysics.HilbertSchmidtExamples
public import KomorebiPhysics.GraphReconstruction

/-! Counterexamples to conflating reconstruction topologies. The nonorthogonal
sequence is uniformly bounded by two, not asserted contractive. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace ReconstructionExamples
open Filter BoundedSpectral HilbertSchmidtExamples
open scoped Topology BigOperators lp

theorem basis_norm (n : ℕ) : ‖basis n‖ = 1 := by
  rw [basis_apply, lp.norm_single (by norm_num), norm_one]

theorem basis_inner (n : ℕ) (x : Space) : inner ℂ (basis n) x = x n := by
  rw [basis_apply, lp.inner_single_left]
  simp

/-- All these operators are actually compact, by factorization through C. -/
theorem rankOne_compact (x y : Space) : IsCompactOperator (InnerProductSpace.rankOne ℂ x y) := by
  rw [InnerProductSpace.rankOne_def']
  exact (isCompactOperator_of_locallyCompactSpace_rng
    (ContinuousLinearMap.toSpanSingleton ℂ x)).comp_clm (innerSL ℂ y)

/-- A compact projection onto coordinate zero. -/
def packet : Space →L[ℂ] Space := InnerProductSpace.rankOne ℂ (basis 0) (basis 0)

/-- A moving off-diagonal rank-one operator. -/
def escape (n : ℕ) : Space →L[ℂ] Space :=
  InnerProductSpace.rankOne ℂ (basis 0) (basis (n+1))

/-- These are not orthogonal cutoffs. They expose the missing adjoint control
in a statement assuming only strong convergence. -/
def sheared (n : ℕ) : Space →L[ℂ] Space := 1 + escape n

theorem packet_apply (x : Space) : packet x = x 0 • basis 0 := by
  rw [packet, InnerProductSpace.rankOne_apply, basis_inner]

theorem packet_compact : IsCompactOperator packet := rankOne_compact _ _

theorem packet_idempotent : packet * packet = packet := by
  ext x
  simp [mul_apply_eq_comp, packet_apply, basis_apply]

theorem packet_norm : ‖packet‖ = 1 := by
  rw [packet, InnerProductSpace.norm_rankOne, basis_norm, one_mul]

theorem escape_apply (n : ℕ) (x : Space) : escape n x = x (n+1) • basis 0 := by
  rw [escape, InnerProductSpace.rankOne_apply, basis_inner]

theorem escape_norm (n : ℕ) : ‖escape n‖ = 1 := by
  rw [escape, InnerProductSpace.norm_rankOne, basis_norm, basis_norm, one_mul]

theorem sheared_norm_le (n : ℕ) : ‖sheared n‖ ≤ 2 := by
  have h := norm_add_le (1 : Space →L[ℂ] Space) (escape n)
  have hi : ‖(1 : Space →L[ℂ] Space)‖ ≤ 1 := ContinuousLinearMap.norm_id_le
  rw [escape_norm] at h
  change ‖1 + escape n‖ ≤ 2
  linarith

theorem sheared_error_norm (n : ℕ) (x : Space) : ‖sheared n x-x‖ = ‖x (n+1)‖ := by
  simp only [sheared, add_apply, one_apply_eq_self, add_sub_cancel_left, escape_apply,
    norm_smul, basis_norm, mul_one]

/-- Strong convergence holds for every actual l2 vector, not just basis vectors. -/
theorem sheared_strong (x : Space) : Tendsto (fun n => sheared n x) atTop (𝓝 x) := by
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  simp_rw [sheared_error_norm]
  have ht : Tendsto (fun n : ℕ => n+1) atTop atTop :=
    tendsto_atTop_mono (fun n => Nat.le_succ n) tendsto_id
  have h := (SpectralGraph.norm_sq_summable x).tendsto_atTop_zero.comp ht
  simpa only [Function.comp_def, Real.sqrt_sq (norm_nonneg _), Real.sqrt_zero] using
    Real.continuous_sqrt.continuousAt.tendsto.comp h

theorem escape_packet (n : ℕ) : escape n * packet = 0 := by
  ext x
  simp [mul_apply_eq_comp, packet_apply, escape_apply, basis_apply]

theorem packet_escape (n : ℕ) : packet * escape n = escape n := by
  ext x
  simp [mul_apply_eq_comp, packet_apply, escape_apply, basis_apply]

/-- The compact sandwich error is a moving rank-one operator, not zero. -/
theorem sheared_packet_error (n : ℕ) :
    StrongReconstruction.compression (sheared n) packet - packet = escape n := by
  unfold StrongReconstruction.compression sheared
  rw [add_mul, one_mul, escape_packet, add_zero, mul_add, mul_one, packet_escape]
  abel

theorem sheared_compact_error_norm (n : ℕ) :
    ‖StrongReconstruction.compression (sheared n) packet - packet‖ = 1 := by
  rw [sheared_packet_error, escape_norm]

/-- Actual compactness of X and uniformly bounded strong S_n -> I do not
by themselves imply norm convergence of S_n X S_n. -/
theorem sheared_compact_not_norm : ¬ Tendsto
    (fun n => ‖StrongReconstruction.compression (sheared n) packet-packet‖) atTop (𝓝 0) := by
  intro h
  simp_rw [sheared_compact_error_norm] at h
  have he := tendsto_nhds_unique h tendsto_const_nhds
  norm_num at he

theorem sheared_adjoint_error (n : ℕ) :
    star (sheared n) (basis 0) - basis 0 = basis (n+1) := by
  rw [sheared, ContinuousLinearMap.star_eq_adjoint, map_add, ContinuousLinearMap.adjoint_one]
  simp only [add_apply, one_apply_eq_self, add_sub_cancel_left]
  rw [escape, InnerProductSpace.adjoint_rankOne, InnerProductSpace.rankOne_apply, basis_inner]
  simp [basis_apply]

theorem adjoint_not_strong : ¬ Tendsto (fun n => star (sheared n) (basis 0)) atTop (𝓝 (basis 0)) := by
  intro h
  have hn := (tendsto_iff_norm_sub_tendsto_zero.mp h)
  simp_rw [sheared_adjoint_error, basis_norm] at hn
  have he := tendsto_nhds_unique hn tendsto_const_nhds
  norm_num at he

/-- Each sheared approximation fails self-adjointness, so it cannot satisfy
our sufficient orthogonal-cutoff contract. -/
theorem sheared_not_selfAdjoint (n : ℕ) : ¬ IsSelfAdjoint (sheared n) := by
  intro h
  have he := sheared_adjoint_error n
  rw [h.star_eq] at he
  have hz : sheared n (basis 0) = basis 0 := by
    simp [sheared, escape_apply, basis_apply]
  rw [hz, sub_self] at he
  have hn := congrArg norm he
  rw [norm_zero, basis_norm] at hn
  norm_num at hn

/-- The HS membership hypothesis is essential: the infinite identity is not
in the square-summable-column class. -/
theorem identity_not_hs : ¬ HilbertSchmidtCore.IsHS basis (1 : Space →L[ℂ] Space) := by
  intro h
  change Summable (fun n : ℕ => ‖(1 : Space →L[ℂ] Space) (basis n)‖^2) at h
  simp only [one_apply_eq_self, basis_norm, one_pow] at h
  have ht := h.tendsto_atTop_zero
  have he := tendsto_nhds_unique ht tendsto_const_nhds
  norm_num at he

/-- The bounded-operator counterexample uses actual orthogonal spectral cutoffs. -/
theorem identity_strong : ∀ x : Space, Tendsto (fun M => SpectralTruncation.cutoff M x) atTop (𝓝 x) :=
  SpectralTruncation.cutoff_strong

theorem identity_norm_error (M : ℕ) : ‖(1 : Space →L[ℂ] Space)-SpectralTruncation.cutoff M‖ = 1 :=
  SpectralErrorBounds.identity_cutoff_norm_error M

/-- The graph theorem consumes the constructed maximal diagonal domain and
its already-proved graph-compatible coordinate atlas. -/
theorem diagonal_graph_reconstruction (eig : ℕ → ℝ)
    (x : (DiagonalDomain.operator eig).domain) :
    Tendsto (fun M => GraphReconstruction.reconstructed (DiagonalDomain.atlas eig) (Finset.range M) x)
      atTop (𝓝 (DiagonalDomain.operator eig x)) :=
  GraphReconstruction.cofinal_reconstruction (DiagonalDomain.atlas eig)
    Finset.range tendsto_finset_range (DiagonalDomain.graph_compatible eig) x

end ReconstructionExamples
end KomorebiPhysics
