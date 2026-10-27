import Komorebi.SufficientResolution.HilbertGlobalization
import Mathlib.Analysis.InnerProductSpace.ProdL2

/-!
# The actual quotient norm and harmonic representatives

The algebraic quotient from block 01 retains Mathlib's quotient seminorm.
No norm is defined or replaced in this file. Norm preservation upgrades the
existing block-07 linear equivalence to a linear isometry equivalence.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.MetricObstruction

open OrthogonalResolution HilbertGlobalization

variable {G V W : Type*}
variable [AddCommGroup G] [Module ℝ G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V]
variable [NormedAddCommGroup W] [NormedSpace ℝ W]
variable (A : G →ₗ[ℝ] V) (delta : V →L[ℝ] W)
variable [(LinearMap.range A).HasOrthogonalProjection]
variable [(LinearMap.ker delta.toLinearMap).HasOrthogonalProjection]

/-- Norm preservation is proved against the existing quotient norm. -/
theorem quotientToHarmonic_norm (h : delta.toLinearMap.comp A = 0)
    (z : Globalization.ObstructionSpace A delta.toLinearMap) :
    ‖quotientToHarmonic A delta h z‖ = ‖z‖ := by
  apply le_antisymm
  · apply (QuotientAddGroup.le_norm_iff
      (S := (Globalization.realizationsInKernel A delta.toLinearMap).toAddSubgroup)).mpr
    intro v hv
    change Globalization.obstructionClass A delta.toLinearMap v = z at hv
    rw [← hv, quotientToHarmonic_class]
    exact obstruction_norm_le _ _ (range_le_kernel A delta h) v
  · calc
      ‖z‖ = ‖harmonicToQuotient A delta (quotientToHarmonic A delta h z)‖ :=
        congrArg norm (quotient_roundtrip A delta h z).symm
      _ ≤ ‖quotientToHarmonic A delta h z‖ :=
        Submodule.Quotient.norm_mk_le _ _

/-- Same underlying linear equivalence, now certified isometric. -/
def obstructionIsometry (h : delta.toLinearMap.comp A = 0) :
    Globalization.ObstructionSpace A delta.toLinearMap ≃ₗᵢ[ℝ]
      harmonic (LinearMap.range A) (LinearMap.ker delta.toLinearMap) where
  toLinearEquiv := obstructionEquivHarmonic A delta h
  norm_map' := quotientToHarmonic_norm A delta h

theorem isometry_toLinearEquiv (h : delta.toLinearMap.comp A = 0) :
    (obstructionIsometry A delta h).toLinearEquiv = obstructionEquivHarmonic A delta h := rfl

theorem isometry_class (h : delta.toLinearMap.comp A = 0)
    (v : LinearMap.ker delta.toLinearMap) :
    obstructionIsometry A delta h (Globalization.obstructionClass A delta.toLinearMap v) =
      harmonicFromKernel A delta h v := rfl

theorem norm_class_eq_obstruction (h : delta.toLinearMap.comp A = 0)
    (v : LinearMap.ker delta.toLinearMap) :
    ‖Globalization.obstructionClass A delta.toLinearMap v‖ =
      ‖obstruction (LinearMap.range A) (LinearMap.ker delta.toLinearMap) (v : V)‖ :=
  (quotientToHarmonic_norm A delta h (Globalization.obstructionClass A delta.toLinearMap v)).symm

/-- The quotient norm equals distance to the actual range, not merely its closure. -/
theorem norm_class_eq_infDist (h : delta.toLinearMap.comp A = 0)
    (v : LinearMap.ker delta.toLinearMap) :
    ‖Globalization.obstructionClass A delta.toLinearMap v‖ =
      Metric.infDist (v : V) (LinearMap.range A : Set V) := by
  rw [norm_class_eq_obstruction A delta h, infDist_eq_error]
  change ‖delta.ker.starProjection (v : V) - (LinearMap.range A).starProjection (v : V)‖ = _
  rw [Submodule.starProjection_eq_self_iff.mpr v.2]
  rfl

theorem distance_classes (h : delta.toLinearMap.comp A = 0)
    (v w : LinearMap.ker delta.toLinearMap) :
    dist (Globalization.obstructionClass A delta.toLinearMap v)
      (Globalization.obstructionClass A delta.toLinearMap w) =
      Metric.infDist ((v : V) - (w : V)) (LinearMap.range A : Set V) := by
  rw [dist_eq_norm]
  change ‖(Globalization.realizationsInKernel A delta.toLinearMap).mkQ v -
    (Globalization.realizationsInKernel A delta.toLinearMap).mkQ w‖ = _
  rw [← map_sub]
  exact norm_class_eq_infDist A delta h (v-w)

theorem quotient_norm_zero_iff (h : delta.toLinearMap.comp A = 0)
    (z : Globalization.ObstructionSpace A delta.toLinearMap) : ‖z‖ = 0 ↔ z = 0 := by
  rw [← quotientToHarmonic_norm A delta h, norm_eq_zero]
  exact (obstructionEquivHarmonic A delta h).map_eq_zero_iff

theorem norm_zero_iff_realizable (h : delta.toLinearMap.comp A = 0)
    (v : LinearMap.ker delta.toLinearMap) :
    ‖Globalization.obstructionClass A delta.toLinearMap v‖ = 0 ↔
      ∃ g : G, A g = (v : V) := by
  rw [quotient_norm_zero_iff A delta h, Globalization.obstructionClass_zero_iff]

/-- Every representative splits into minimum class norm and removable realized energy. -/
theorem representative_energy (h : delta.toLinearMap.comp A = 0)
    (v : LinearMap.ker delta.toLinearMap) :
    ‖v‖ ^ 2 = ‖Globalization.obstructionClass A delta.toLinearMap v‖ ^ 2 +
      ‖realized (LinearMap.range A) (v : V)‖ ^ 2 := by
  have he := norm_sq_components (LinearMap.range A) (LinearMap.ker delta.toLinearMap)
    (range_le_kernel A delta h) (v : V)
  rw [(inconsistency_zero_iff _ _).mpr v.2, norm_zero, zero_pow (by decide), add_zero] at he
  rw [norm_class_eq_obstruction A delta h]
  change ‖(v : V)‖ ^ 2 = _
  linarith

theorem harmonicToQuotient_norm (h : delta.toLinearMap.comp A = 0)
    (v : harmonic (LinearMap.range A) (LinearMap.ker delta.toLinearMap)) :
    ‖harmonicToQuotient A delta v‖ = ‖v‖ := by
  rw [← quotientToHarmonic_norm A delta h, harmonic_roundtrip]

/-- The canonical harmonic representative actually attains the quotient infimum. -/
theorem minimum_representative_exists (h : delta.toLinearMap.comp A = 0)
    (z : Globalization.ObstructionSpace A delta.toLinearMap) :
    ∃ v : LinearMap.ker delta.toLinearMap,
      Globalization.obstructionClass A delta.toLinearMap v = z ∧ ‖v‖ = ‖z‖ := by
  let u := quotientToHarmonic A delta h z
  refine ⟨⟨(u : V), u.2.1⟩, quotient_roundtrip A delta h z, ?_⟩
  exact quotientToHarmonic_norm A delta h z

omit [(LinearMap.range A).HasOrthogonalProjection]
  [(LinearMap.ker delta.toLinearMap).HasOrthogonalProjection] in
/-- Any realization shift leaves both the class and its norm unchanged. -/
theorem realization_shift (h : delta.toLinearMap.comp A = 0)
    (v : LinearMap.ker delta.toLinearMap) (g : G) :
    Globalization.obstructionClass A delta.toLinearMap
      (v + ⟨A g, range_le_kernel A delta h (LinearMap.mem_range_self A g)⟩) =
    Globalization.obstructionClass A delta.toLinearMap v := by
  change (Globalization.realizationsInKernel A delta.toLinearMap).mkQ _ = _
  rw [map_add]
  have hz : Globalization.obstructionClass A delta.toLinearMap
      ⟨A g, range_le_kernel A delta h (LinearMap.mem_range_self A g)⟩ = 0 :=
    (Globalization.obstructionClass_zero_iff A delta.toLinearMap _).mpr ⟨g, rfl⟩
  change Globalization.obstructionClass A delta.toLinearMap v + _ = _
  change (Globalization.realizationsInKernel A delta.toLinearMap).mkQ
    ⟨A g, range_le_kernel A delta h (LinearMap.mem_range_self A g)⟩ = 0 at hz
  rw [hz, add_zero]

omit [(LinearMap.ker delta.toLinearMap).HasOrthogonalProjection] in
/-- Construct projection inside the compatible space, rather than replacing its metric. -/
theorem compatibleRangeProjection (h : delta.toLinearMap.comp A = 0) :
    (Globalization.realizationsInKernel A delta.toLinearMap).HasOrthogonalProjection where
  exists_orthogonal v := by
    let r : LinearMap.ker delta.toLinearMap :=
      ⟨(LinearMap.range A).starProjection (v : V),
        range_le_kernel A delta h ((LinearMap.range A).starProjection_apply_mem v)⟩
    refine ⟨r, (LinearMap.range A).starProjection_apply_mem v, ?_⟩
    intro w hw
    change inner ℝ (w : V) ((v : V) - (LinearMap.range A).starProjection (v : V)) = 0
    exact (Submodule.sub_starProjection_mem_orthogonal (K := LinearMap.range A) (v : V))
      (w : V) hw

/-- The standard quotient inner product is preserved as well as its pre-existing norm. -/
theorem quotient_inner_preserved (h : delta.toLinearMap.comp A = 0)
    [(Globalization.realizationsInKernel A delta.toLinearMap).HasOrthogonalProjection]
    (z w : Globalization.ObstructionSpace A delta.toLinearMap) :
    inner ℝ (obstructionIsometry A delta h z) (obstructionIsometry A delta h w) =
      inner ℝ z w :=
  LinearIsometryEquiv.inner_map_map (𝕜 := ℝ) (obstructionIsometry A delta h) z w

theorem distance_isometry (h : delta.toLinearMap.comp A = 0)
    (z w : Globalization.ObstructionSpace A delta.toLinearMap) :
    dist (quotientToHarmonic A delta h z) (quotientToHarmonic A delta h w) = dist z w :=
  (obstructionIsometry A delta h).dist_map z w

end Komorebi.SufficientResolution.MetricObstruction
