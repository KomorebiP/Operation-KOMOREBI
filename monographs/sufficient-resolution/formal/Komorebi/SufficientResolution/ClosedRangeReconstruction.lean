import Komorebi.SufficientResolution.SourceConditioning

/-!
# Explicit closed-range reconstruction and the coercivity criterion

The public closed-range constructor receives an IsClosed hypothesis on the actual
range. Positive off-kernel coercivity is equivalent to this closed-range condition.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.ClosedRangeReconstruction

open MinimumNormReconstruction MinimumNormOptimality SourceConditioning HilbertConditioning

variable {G V : Type*}
variable [NormedAddCommGroup G] [InnerProductSpace ℝ G] [CompleteSpace G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V] [CompleteSpace V]
variable (A : G →L[ℝ] V)

/-- Public constructor with closedness of the actual range explicit. -/
def closedRecover (hclosed : IsClosed (A.range : Set V)) : V →L[ℝ] G :=
  let : CompleteSpace A.range := hclosed.completeSpace_coe
  recover A

 theorem closed_recover_mem (hclosed : IsClosed (A.range : Set V)) (v : V) :
    closedRecover A hclosed v ∈ A.kerᗮ := by
  let : CompleteSpace A.range := hclosed.completeSpace_coe
  exact recover_mem A v

 theorem closed_recover_image (hclosed : IsClosed (A.range : Set V)) (g : G) :
    closedRecover A hclosed (A g) = A.kerᗮ.starProjection g := by
  let : CompleteSpace A.range := hclosed.completeSpace_coe
  exact recover_image A g

 theorem closed_recover_residual_orthogonal (hclosed : IsClosed (A.range : Set V)) (v : V) :
    v-A (closedRecover A hclosed v) ∈ A.rangeᗮ := by
  let : CompleteSpace A.range := hclosed.completeSpace_coe
  change v-A (recover A v) ∈ A.rangeᗮ
  rw [image_recover]
  exact Submodule.sub_starProjection_mem_orthogonal v

 theorem closed_recover_best (hclosed : IsClosed (A.range : Set V)) (v : V) :
    ‖v-A (closedRecover A hclosed v)‖ = Metric.infDist v (A.range : Set V) := by
  let : CompleteSpace A.range := hclosed.completeSpace_coe
  exact recover_best_error A v

 theorem closed_recover_minimum_norm (hclosed : IsClosed (A.range : Set V))
    (v : V) (g : G) (hg : ‖v-A g‖ = Metric.infDist v (A.range : Set V)) :
    ‖closedRecover A hclosed v‖ ≤ ‖g‖ := by
  let : CompleteSpace A.range := hclosed.completeSpace_coe
  exact minimum_norm A v g ((least_squares_iff A v g).mp hg)

 theorem closed_recover_penrose (hclosed : IsClosed (A.range : Set V)) :
    (∀ g, A (closedRecover A hclosed (A g)) = A g) ∧
    (∀ v, closedRecover A hclosed (A (closedRecover A hclosed v)) = closedRecover A hclosed v) := by
  let : CompleteSpace A.range := hclosed.completeSpace_coe
  exact ⟨penrose_image A, penrose_recover A⟩

 theorem closed_range_has_coercivity (hclosed : IsClosed (A.range : Set V)) :
    ∃ alpha : ℝ, 0 < alpha ∧ CoerciveOffKernel A alpha := by
  let : CompleteSpace A.range := hclosed.completeSpace_coe
  exact exists_source_coercivity A

/- Coercivity is sufficient for closed range, not merely a consequence of it. -/
omit [CompleteSpace V] in
 theorem closed_range_of_coercivity (alpha : ℝ) (ha : 0 < alpha)
    (hc : CoerciveOffKernel A alpha) : IsClosed (A.range : Set V) := by
  let f : A.kerᗮ →L[ℝ] V := A.domRestrict A.kerᗮ
  have hb : ∀ x : A.kerᗮ, ‖x‖ ≤ alpha⁻¹ * ‖f x‖ := by
    intro x
    have hh := hc (x : G) x.2
    have hd : ‖(x : G)‖ ≤ ‖A (x : G)‖ / alpha := by
      apply (le_div_iff₀ ha).mpr
      nlinarith
    change ‖(x : G)‖ ≤ alpha⁻¹ * ‖A (x : G)‖
    simpa only [div_eq_mul_inv, mul_comm] using hd
  have hf : AntilipschitzWith (⟨alpha⁻¹, inv_nonneg.mpr ha.le⟩ : NNReal) f :=
    AddMonoidHomClass.antilipschitz_of_bound f hb
  have hr : Set.range f = (A.range : Set V) := by
    ext v
    constructor
    · rintro ⟨x, rfl⟩
      exact A.mem_range_self (x : G)
    · rintro ⟨g, rfl⟩
      exact ⟨A.kerᗮ.orthogonalProjectionOnto g, source_projection_image A g⟩
  rw [← hr]
  exact hf.isClosed_range f.uniformContinuous

 theorem closed_range_iff_coercivity :
    IsClosed (A.range : Set V) ↔ ∃ alpha : ℝ, 0 < alpha ∧ CoerciveOffKernel A alpha := by
  constructor
  · exact closed_range_has_coercivity A
  · rintro ⟨alpha, ha, hc⟩
    exact closed_range_of_coercivity A alpha ha hc

/- Any bounded recovery of the identifiable source already forces closed range. -/
omit [CompleteSpace V] in
 theorem closed_range_of_bounded_recovery (B : V →L[ℝ] G)
    (hB : ∀ g, B (A g) = A.kerᗮ.starProjection g) :
    IsClosed (A.range : Set V) := by
  let c : ℝ := ‖B‖+1
  have hc : 0 < c := by dsimp [c]; linarith [norm_nonneg B]
  apply closed_range_of_coercivity A c⁻¹ (inv_pos.mpr hc)
  intro g hg
  have hr : B (A g) = g := (hB g).trans (Submodule.starProjection_eq_self_iff.mpr hg)
  have hb : ‖g‖ ≤ c * ‖A g‖ := by
    calc
      ‖g‖ = ‖B (A g)‖ := congrArg norm hr.symm
      _ ≤ ‖B‖ * ‖A g‖ := B.le_opNorm _
      _ ≤ c * ‖A g‖ := mul_le_mul_of_nonneg_right (by dsimp [c]; linarith) (norm_nonneg _)
  calc
    c⁻¹ * ‖g‖ ≤ c⁻¹ * (c * ‖A g‖) := mul_le_mul_of_nonneg_left hb (inv_nonneg.mpr hc.le)
    _ = ‖A g‖ := by rw [← mul_assoc, inv_mul_cancel₀ hc.ne', one_mul]

 theorem bounded_recovery_iff_closed_range :
    (∃ B : V →L[ℝ] G, ∀ g, B (A g) = A.kerᗮ.starProjection g) ↔
      IsClosed (A.range : Set V) := by
  constructor
  · rintro ⟨B, hB⟩
    exact closed_range_of_bounded_recovery A B hB
  · intro hc
    exact ⟨closedRecover A hc, closed_recover_image A hc⟩

 theorem nonclosed_no_bounded_recovery (hn : ¬ IsClosed (A.range : Set V)) :
    ¬ ∃ B : V →L[ℝ] G, ∀ g, B (A g) = A.kerᗮ.starProjection g := by
  intro h
  exact hn ((bounded_recovery_iff_closed_range A).mp h)

omit [CompleteSpace G] [CompleteSpace V] in
 theorem finite_source_closed_range [FiniteDimensional ℝ G] :
    IsClosed (A.range : Set V) := A.range.closed_of_finiteDimensional

omit [CompleteSpace G] [CompleteSpace V] in
 theorem finite_target_closed_range [FiniteDimensional ℝ V] :
    IsClosed (A.range : Set V) := A.range.closed_of_finiteDimensional

end Komorebi.SufficientResolution.ClosedRangeReconstruction
