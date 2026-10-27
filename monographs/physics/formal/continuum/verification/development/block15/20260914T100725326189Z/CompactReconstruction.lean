module
public import KomorebiPhysics.StrongReconstruction
public import Mathlib.Analysis.Normed.Operator.Compact.Basic

/-! Compact reconstruction. Left convergence uses compact images of the unit
ball. Right convergence uses self-adjoint cutoffs and a Gram-operator argument,
not the false implication from strong convergence to strong adjoint convergence. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace CompactReconstruction
open Filter StrongReconstruction
open scoped Topology
variable {H α : Type*} [NormedAddCommGroup H]
variable {l : Filter α}
section Normed
variable [NormedSpace ℂ H]

/-- Strong convergence of contractions is uniform on every compact set. -/
theorem uniform_compact (S : α → H →L[ℂ] H)
    (hS : ∀ a, ‖S a‖ ≤ 1) (hs : ∀ x, Tendsto (fun a => S a x) l (𝓝 x))
    {K : Set H} (hK : IsCompact K) {ε : ℝ} (hε : 0 < ε) :
    ∀ᶠ a in l, ∀ x ∈ K, ‖S a x-x‖ < ε := by
  obtain ⟨t, _, ht, hcover⟩ := hK.finite_cover_balls (by positivity : 0 < ε/3)
  have he : ∀ᶠ a in l, ∀ y ∈ t, ‖S a y-y‖ < ε/3 := by
    apply ht.eventually_all.mpr
    intro y _
    have hy : Tendsto (fun a => ‖S a y-y‖) l (𝓝 0) := by
      simpa using ((hs y).sub_const y).norm
    exact hy.eventually (gt_mem_nhds (by positivity))
  filter_upwards [he] with a ha x hx
  obtain ⟨y, hy, hxy⟩ := Set.mem_iUnion₂.mp (hcover hx)
  have hd : ‖x-y‖ < ε/3 := by simpa only [Metric.mem_ball, dist_eq_norm] using hxy
  have hid : S a x-x = S a (x-y) + (S a y-y) + (y-x) := by rw [map_sub]; abel
  rw [hid]
  have hn1 := norm_add_le (S a (x-y)) (S a y-y)
  have hn2 := norm_add_le (S a (x-y)+(S a y-y)) (y-x)
  have hn3 := contraction_apply (S a) (hS a) (x-y)
  rw [norm_sub_rev y x] at hn2
  have hn4 := ha y hy
  linarith

/-- Norm convergence on the left of a compact operator requires no adjoint hypothesis. -/
theorem compact_left (S : α → H →L[ℂ] H)
    (hS : ∀ a, ‖S a‖ ≤ 1) (hs : ∀ x, Tendsto (fun a => S a x) l (𝓝 x))
    (X : H →L[ℂ] H) (hX : IsCompactOperator X) :
    Tendsto (fun a => ‖(S a-1)*X‖) l (𝓝 0) := by
  obtain ⟨K, hK, hXK⟩ := (show IsCompactOperator X.toLinearMap from hX).image_closedBall_subset_compact 1
  apply Metric.tendsto_nhds.mpr
  intro ε hε
  filter_upwards [uniform_compact S hS hs hK (half_pos hε)] with a ha
  rw [dist_zero_right, Real.norm_eq_abs, abs_of_nonneg (norm_nonneg _)]
  apply lt_of_le_of_lt _ (half_lt_self hε)
  apply ContinuousLinearMap.opNorm_le_of_unit_norm (le_of_lt (half_pos hε))
  intro x hx
  change ‖S a (X x) - X x‖ ≤ ε/2
  apply le_of_lt (ha (X x) _)
  exact hXK ⟨x, by simp [Metric.mem_closedBall, dist_zero_right, hx], rfl⟩

theorem compact_left_operator (S : α → H →L[ℂ] H)
    (hS : ∀ a, ‖S a‖ ≤ 1) (hs : ∀ x, Tendsto (fun a => S a x) l (𝓝 x))
    (X : H →L[ℂ] H) (hX : IsCompactOperator X) :
    Tendsto (fun a => S a * X) l (𝓝 X) := by
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  simpa only [sub_mul, one_mul] using compact_left S hS hs X hX

end Normed
section Hilbert
variable [InnerProductSpace ℂ H] [CompleteSpace H]

/-- The quantitative Gram estimate supplies the missing co-range control. -/
theorem right_error_sq_bound (S X : H →L[ℂ] H) (hS : ‖S‖ ≤ 1)
    (hsa : IsSelfAdjoint S) :
    ‖X*(S-1)‖^2 ≤ 2 * ‖(S-1)*(star X * X)‖ := by
  have he : star (X*(S-1)) * (X*(S-1)) = ((S-1)*(star X*X))*(S-1) := by
    rw [star_mul, star_sub, hsa.star_eq, star_one]
    noncomm_ring
  have hn : ‖star (X*(S-1)) * (X*(S-1))‖ = ‖X*(S-1)‖^2 := by
    simpa only [sq] using ContinuousLinearMap.norm_adjoint_comp_self (X*(S-1))
  have hb : ‖S-1‖ ≤ 2 := by
    have h := norm_sub_le S (1 : H →L[ℂ] H)
    have hi : ‖(1 : H →L[ℂ] H)‖ ≤ 1 := norm_one_le
    linarith
  rw [← hn, he]
  exact (norm_mul_le _ _).trans (by nlinarith [norm_nonneg ((S-1)*(star X*X))])

/-- Compact right reconstruction uses self-adjointness, unlike left reconstruction. -/
theorem compact_right (S : α → H →L[ℂ] H)
    (hS : ∀ a, ‖S a‖ ≤ 1) (hs : ∀ x, Tendsto (fun a => S a x) l (𝓝 x))
    (hsa : ∀ a, IsSelfAdjoint (S a))
    (X : H →L[ℂ] H) (hX : IsCompactOperator X) :
    Tendsto (fun a => ‖X*(S a-1)‖) l (𝓝 0) := by
  have hg : IsCompactOperator (star X * X) := hX.clm_comp (star X)
  have ht := (compact_left S hS hs (star X*X) hg).const_mul 2
  have hq : Tendsto (fun a => ‖X*(S a-1)‖^2) l (𝓝 0) := by
    exact squeeze_zero (fun _ => sq_nonneg _) (fun a => right_error_sq_bound (S a) X (hS a) (hsa a))
      (by simpa using ht)
  have hroot := Real.continuous_sqrt.continuousAt.tendsto.comp hq
  simpa only [Function.comp_def, Real.sqrt_sq (norm_nonneg _), Real.sqrt_zero] using hroot

/-- The literal compact sandwich convergence in operator norm. -/
theorem compact_compression (S : α → H →L[ℂ] H)
    (hS : ∀ a, ‖S a‖ ≤ 1) (hs : ∀ x, Tendsto (fun a => S a x) l (𝓝 x))
    (hsa : ∀ a, IsSelfAdjoint (S a))
    (X : H →L[ℂ] H) (hX : IsCompactOperator X) :
    Tendsto (fun a => ‖compression (S a) X-X‖) l (𝓝 0) := by
  have hb : ∀ a, ‖compression (S a) X-X‖ ≤ ‖X*(S a-1)‖ + ‖(S a-1)*X‖ := by
    intro a
    rw [error_identity, mul_assoc]
    exact (norm_add_le _ _).trans (add_le_add
      ((norm_mul_le _ _).trans (by nlinarith [hS a, norm_nonneg (X*(S a-1))])) le_rfl)
  exact squeeze_zero (fun _ => norm_nonneg _) hb (by
    simpa using (compact_right S hS hs hsa X hX).add (compact_left S hS hs X hX))

theorem compact_compression_operator (S : α → H →L[ℂ] H)
    (hS : ∀ a, ‖S a‖ ≤ 1) (hs : ∀ x, Tendsto (fun a => S a x) l (𝓝 x))
    (hsa : ∀ a, IsSelfAdjoint (S a))
    (X : H →L[ℂ] H) (hX : IsCompactOperator X) :
    Tendsto (fun a => compression (S a) X) l (𝓝 X) :=
  tendsto_iff_norm_sub_tendsto_zero.mpr (compact_compression S hS hs hsa X hX)

end Hilbert
end CompactReconstruction
end KomorebiPhysics
