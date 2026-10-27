import Komorebi.SufficientResolution.MetricObstruction

/-!
# Minimum-norm representatives in the actual obstruction quotient

These representatives are compatible local vectors, not global sources. Source
reconstruction and its separate conditioning remain in block 08.
-/
set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.MetricRepresentatives

open OrthogonalResolution HilbertGlobalization MetricObstruction

variable {G V W : Type*}
variable [AddCommGroup G] [Module ℝ G]
variable [NormedAddCommGroup V] [InnerProductSpace ℝ V]
variable [NormedAddCommGroup W] [NormedSpace ℝ W]
variable (A : G →ₗ[ℝ] V) (delta : V →L[ℝ] W)
variable [(LinearMap.range A).HasOrthogonalProjection]
variable [(LinearMap.ker delta.toLinearMap).HasOrthogonalProjection]

/-- The canonical minimum-norm representative, still inside the original compatible space. -/
def minimumRepresentative (h : delta.toLinearMap.comp A = 0) :
    Globalization.ObstructionSpace A delta.toLinearMap →ₗ[ℝ] delta.ker :=
  (Submodule.inclusion (show harmonic (LinearMap.range A) delta.ker ≤ delta.ker from inf_le_left)).comp
    (quotientToHarmonic A delta h)

theorem minimumRepresentative_class (h : delta.toLinearMap.comp A = 0)
    (v : delta.ker) :
    (minimumRepresentative A delta h (Globalization.obstructionClass A delta.toLinearMap v) : V) =
      obstruction (LinearMap.range A) delta.ker (v : V) := rfl

theorem minimumRepresentative_norm (h : delta.toLinearMap.comp A = 0)
    (z : Globalization.ObstructionSpace A delta.toLinearMap) :
    ‖minimumRepresentative A delta h z‖ = ‖z‖ :=
  quotientToHarmonic_norm A delta h z

theorem class_minimumRepresentative (h : delta.toLinearMap.comp A = 0)
    (z : Globalization.ObstructionSpace A delta.toLinearMap) :
    Globalization.obstructionClass A delta.toLinearMap (minimumRepresentative A delta h z) = z :=
  quotient_roundtrip A delta h z

/-- The selected lift is an isometric linear embedding, not just a set-theoretic choice. -/
def minimumSection (h : delta.toLinearMap.comp A = 0) :
    Globalization.ObstructionSpace A delta.toLinearMap →ₗᵢ[ℝ] delta.ker where
  toLinearMap := minimumRepresentative A delta h
  norm_map' := minimumRepresentative_norm A delta h

theorem representative_difference (h : delta.toLinearMap.comp A = 0)
    (z : Globalization.ObstructionSpace A delta.toLinearMap) (v : delta.ker)
    (hv : Globalization.obstructionClass A delta.toLinearMap v = z) :
    ((v - minimumRepresentative A delta h z : delta.ker) : V) =
      realized (LinearMap.range A) (v : V) := by
  rw [← hv]
  change (v : V) - obstruction (LinearMap.range A) delta.ker (v : V) = _
  change (v : V) - (delta.ker.starProjection (v : V) -
    (LinearMap.range A).starProjection (v : V)) = _
  rw [Submodule.starProjection_eq_self_iff.mpr v.2]
  simp only [sub_sub_cancel]
  rfl

theorem representative_error_energy (h : delta.toLinearMap.comp A = 0)
    (z : Globalization.ObstructionSpace A delta.toLinearMap) (v : delta.ker)
    (hv : Globalization.obstructionClass A delta.toLinearMap v = z) :
    ‖v‖^2 = ‖z‖^2 + ‖v - minimumRepresentative A delta h z‖^2 := by
  have hd : ‖v - minimumRepresentative A delta h z‖ =
      ‖realized (LinearMap.range A) (v : V)‖ :=
    congrArg norm (representative_difference A delta h z v hv)
  rw [hd, ← hv]
  exact representative_energy A delta h v

theorem minimum_norm (h : delta.toLinearMap.comp A = 0)
    (z : Globalization.ObstructionSpace A delta.toLinearMap) (v : delta.ker)
    (hv : Globalization.obstructionClass A delta.toLinearMap v = z) :
    ‖minimumRepresentative A delta h z‖ ≤ ‖v‖ := by
  rw [minimumRepresentative_norm, ← hv]
  exact Submodule.Quotient.norm_mk_le _ _

theorem equal_norm_iff_minimum (h : delta.toLinearMap.comp A = 0)
    (z : Globalization.ObstructionSpace A delta.toLinearMap) (v : delta.ker)
    (hv : Globalization.obstructionClass A delta.toLinearMap v = z) :
    ‖v‖ = ‖z‖ ↔ v = minimumRepresentative A delta h z := by
  constructor
  · intro hn
    have he := representative_error_energy A delta h z v hv
    rw [hn] at he
    have hz : ‖v - minimumRepresentative A delta h z‖ = 0 := by
      nlinarith [norm_nonneg (v-minimumRepresentative A delta h z)]
    exact sub_eq_zero.mp (norm_eq_zero.mp hz)
  · rintro rfl
    exact minimumRepresentative_norm A delta h z

/-- Every quotient class attains its infimum at exactly one compatible vector. -/
theorem unique_minimum_representative (h : delta.toLinearMap.comp A = 0)
    (z : Globalization.ObstructionSpace A delta.toLinearMap) :
    ∃! v : delta.ker,
      Globalization.obstructionClass A delta.toLinearMap v = z ∧ ‖v‖ = ‖z‖ := by
  refine ⟨minimumRepresentative A delta h z,
    ⟨class_minimumRepresentative A delta h z, minimumRepresentative_norm A delta h z⟩, ?_⟩
  intro v hv
  exact (equal_norm_iff_minimum A delta h z v hv.1).mp hv.2

theorem representative_distance (h : delta.toLinearMap.comp A = 0)
    (z w : Globalization.ObstructionSpace A delta.toLinearMap) :
    dist (minimumRepresentative A delta h z) (minimumRepresentative A delta h w) = dist z w :=
  (minimumSection A delta h).dist_map z w

end Komorebi.SufficientResolution.MetricRepresentatives
