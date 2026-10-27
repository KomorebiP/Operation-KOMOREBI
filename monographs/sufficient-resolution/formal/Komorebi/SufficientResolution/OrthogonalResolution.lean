import Mathlib.Analysis.InnerProductSpace.Projection.Basic
import Mathlib.Topology.MetricSpace.HausdorffDistance
import Mathlib.Tactic.Abel
import Mathlib.Tactic.Linarith

/-!
# Orthogonal resolution of realizability and compatibility

For nested subspaces R <= K admitting orthogonal projections, the actual
orthogonal projectors give three canonical components. No finite-dimensional
hypothesis or automatically supplied globalization assumption is used.
-/

set_option autoImplicit false
noncomputable section

namespace Komorebi.SufficientResolution.OrthogonalResolution

variable {V : Type*} [NormedAddCommGroup V] [InnerProductSpace ℝ V]
variable (R K : Submodule ℝ V) [R.HasOrthogonalProjection] [K.HasOrthogonalProjection]

/-- The part represented by a global object. -/
def realized : V →L[ℝ] V := R.starProjection

/-- Compatible data modulo the represented part. -/
def obstruction : V →L[ℝ] V := K.starProjection - R.starProjection

/-- The component rejected by the compatibility tests. -/
def inconsistency : V →L[ℝ] V := ContinuousLinearMap.id ℝ V - K.starProjection

/-- Canonical representative space for compatible but unrealizable data. -/
def harmonic : Submodule ℝ V := K ⊓ Rᗮ

 theorem realized_mem (v : V) : realized R v ∈ R := R.starProjection_apply_mem v

 theorem inconsistency_mem (v : V) : inconsistency K v ∈ Kᗮ :=
  Submodule.sub_starProjection_mem_orthogonal v

 theorem obstruction_mem (h : R ≤ K) (v : V) : obstruction R K v ∈ harmonic R K := by
  constructor
  · exact K.sub_mem (K.starProjection_apply_mem v) (h (R.starProjection_apply_mem v))
  · have hi := Submodule.sub_starProjection_mem_orthogonal (K := R) (K.starProjection v)
    have he := congrArg (fun f : V →L[ℝ] V => f v)
      (Submodule.starProjection_comp_starProjection_of_le h)
    change R.starProjection (K.starProjection v) = R.starProjection v at he
    change K.starProjection v - R.starProjection v ∈ Rᗮ
    rw [← he]
    exact hi

 theorem components_sum (v : V) :
    realized R v + obstruction R K v + inconsistency K v = v := by
  simp only [realized, obstruction, inconsistency, sub_apply,
    ContinuousLinearMap.id_apply]
  abel

 theorem error_split (v : V) :
    v - realized R v = obstruction R K v + inconsistency K v := by
  simp only [realized, obstruction, inconsistency, sub_apply,
    ContinuousLinearMap.id_apply]
  abel

 theorem realized_obstruction_orthogonal (h : R ≤ K) (v : V) :
    inner ℝ (realized R v) (obstruction R K v) = 0 :=
  (obstruction_mem R K h v).2 _ (realized_mem R v)

 theorem realized_inconsistency_orthogonal (h : R ≤ K) (v : V) :
    inner ℝ (realized R v) (inconsistency K v) = 0 :=
  inconsistency_mem K v _ (h (realized_mem R v))

 theorem obstruction_inconsistency_orthogonal (h : R ≤ K) (v : V) :
    inner ℝ (obstruction R K v) (inconsistency K v) = 0 :=
  inconsistency_mem K v _ (obstruction_mem R K h v).1

 theorem error_norm_sq (h : R ≤ K) (v : V) :
    ‖v - realized R v‖ ^ 2 = ‖obstruction R K v‖ ^ 2 + ‖inconsistency K v‖ ^ 2 := by
  rw [error_split R K v]
  simpa only [pow_two] using norm_add_sq_eq_norm_sq_add_norm_sq_of_inner_eq_zero
    (obstruction R K v) (inconsistency K v) (obstruction_inconsistency_orthogonal R K h v)

 theorem norm_sq_components (h : R ≤ K) (v : V) :
    ‖v‖ ^ 2 = ‖realized R v‖ ^ 2 + ‖obstruction R K v‖ ^ 2 + ‖inconsistency K v‖ ^ 2 := by
  have hp := Submodule.norm_sq_eq_add_norm_sq_starProjection v R
  rw [Submodule.starProjection_orthogonal_val] at hp
  change ‖v‖ ^ 2 = ‖realized R v‖ ^ 2 + ‖v - realized R v‖ ^ 2 at hp
  rw [error_norm_sq R K h v] at hp
  linarith

/-- Exact Pythagorean identity for every candidate reconstruction, not only the minimizer. -/
 theorem candidate_error_sq (v : V) {r : V} (hr : r ∈ R) :
    ‖v - r‖ ^ 2 = ‖v - realized R v‖ ^ 2 + ‖realized R v - r‖ ^ 2 := by
  have ho : inner ℝ (v - realized R v) (realized R v - r) = 0 :=
    Submodule.starProjection_inner_eq_zero _ _ (R.sub_mem (realized_mem R v) hr)
  have hp := norm_add_sq_eq_norm_sq_add_norm_sq_of_inner_eq_zero _ _ ho
  have he : (v - realized R v) + (realized R v - r) = v - r := by abel
  simpa only [he, pow_two] using hp

 theorem best_approximation (v : V) {r : V} (hr : r ∈ R) :
    ‖v - realized R v‖ ≤ ‖v - r‖ := by
  have he := candidate_error_sq R v hr
  nlinarith [sq_nonneg ‖realized R v - r‖, norm_nonneg (v - realized R v), norm_nonneg (v - r)]

 theorem best_approximation_unique (v : V) {r : V} (hr : r ∈ R) :
    ‖v - r‖ = ‖v - realized R v‖ ↔ r = realized R v := by
  constructor
  · intro he
    have hp := candidate_error_sq R v hr
    rw [he] at hp
    have hn : ‖realized R v - r‖ = 0 := by nlinarith [norm_nonneg (realized R v - r)]
    exact (sub_eq_zero.mp (norm_eq_zero.mp hn)).symm
  · rintro rfl
    rfl

/-- Equality with Mathlib's metric distance to the actual represented subspace. -/
 theorem infDist_eq_error (v : V) :
    Metric.infDist v (R : Set V) = ‖v - realized R v‖ := by
  apply le_antisymm
  · simpa only [dist_eq_norm] using Metric.infDist_le_dist_of_mem (realized_mem R v)
  · apply (Metric.le_infDist (show (R : Set V).Nonempty from ⟨0, R.zero_mem⟩)).mpr
    intro r hr
    simpa only [dist_eq_norm] using best_approximation R v hr

 theorem infDist_sq_decomposition (h : R ≤ K) (v : V) :
    Metric.infDist v (R : Set V) ^ 2 =
      ‖obstruction R K v‖ ^ 2 + ‖inconsistency K v‖ ^ 2 := by
  rw [infDist_eq_error R v, error_norm_sq R K h v]

 theorem inconsistency_zero_iff (v : V) : inconsistency K v = 0 ↔ v ∈ K := by
  change v - K.starProjection v = 0 ↔ v ∈ K
  rw [sub_eq_zero, eq_comm, Submodule.starProjection_eq_self_iff]

 theorem obstruction_zero_iff_of_compatible (v : V) (hv : v ∈ K) :
    obstruction R K v = 0 ↔ v ∈ R := by
  change K.starProjection v - R.starProjection v = 0 ↔ v ∈ R
  rw [Submodule.starProjection_eq_self_iff.mpr hv, sub_eq_zero, eq_comm,
    Submodule.starProjection_eq_self_iff]

 theorem realizable_iff_components_zero (h : R ≤ K) (v : V) :
    v ∈ R ↔ obstruction R K v = 0 ∧ inconsistency K v = 0 := by
  constructor
  · intro hv
    exact ⟨(obstruction_zero_iff_of_compatible R K v (h hv)).mpr hv,
      (inconsistency_zero_iff K v).mpr (h hv)⟩
  · rintro ⟨ho, hi⟩
    exact (obstruction_zero_iff_of_compatible R K v ((inconsistency_zero_iff K v).mp hi)).mp ho

 theorem obstruction_on_harmonic (v : V) (hv : v ∈ harmonic R K) :
    obstruction R K v = v := by
  change K.starProjection v - R.starProjection v = v
  rw [Submodule.starProjection_eq_self_iff.mpr hv.1,
    show R.starProjection v = 0 from by
      change v ∈ LinearMap.ker R.starProjection.toLinearMap
      rw [Submodule.ker_starProjection]
      exact hv.2, sub_zero]

 theorem obstruction_idempotent (h : R ≤ K) (v : V) :
    obstruction R K (obstruction R K v) = obstruction R K v :=
  obstruction_on_harmonic R K _ (obstruction_mem R K h v)

/-- The three components are unique among vectors in their stated orthogonal sectors. -/
 theorem unique_components (h : R ≤ K) (v r o i : V)
    (hr : r ∈ R) (ho : o ∈ harmonic R K) (hi : i ∈ Kᗮ)
    (he : v = r + o + i) :
    realized R v = r ∧ obstruction R K v = o ∧ inconsistency K v = i := by
  have hpr : R.starProjection v = r :=
    Submodule.eq_starProjection_of_mem_orthogonal' hr
      (Rᗮ.add_mem ho.2 (Submodule.orthogonal_le h hi)) (by rw [he]; abel)
  have hpk : K.starProjection v = r+o :=
    Submodule.eq_starProjection_of_mem_orthogonal' (K.add_mem (h hr) ho.1) hi he
  refine ⟨hpr, ?_, ?_⟩
  · change K.starProjection v - R.starProjection v = o
    rw [hpk, hpr]
    abel
  · change v - K.starProjection v = i
    rw [hpk, he]
    abel

 theorem obstruction_range (h : R ≤ K) :
    LinearMap.range (obstruction R K).toLinearMap = harmonic R K := by
  apply le_antisymm
  · rintro v ⟨x, rfl⟩
    exact obstruction_mem R K h x
  · intro v hv
    exact ⟨v, obstruction_on_harmonic R K v hv⟩

 theorem obstruction_norm_le (h : R ≤ K) (v : V) : ‖obstruction R K v‖ ≤ ‖v‖ := by
  have hp := norm_sq_components R K h v
  nlinarith [sq_nonneg ‖realized R v‖, sq_nonneg ‖inconsistency K v‖,
    norm_nonneg (obstruction R K v), norm_nonneg v]

 theorem inconsistency_norm_le (v : V) : ‖inconsistency K v‖ ≤ ‖v‖ := by
  rw [show inconsistency K v = Kᗮ.starProjection v from
    (Submodule.starProjection_orthogonal_val v).symm]
  exact Kᗮ.norm_starProjection_apply_le v

 theorem obstruction_noise_bound (h : R ≤ K) (v w : V) :
    ‖obstruction R K v - obstruction R K w‖ ≤ ‖v - w‖ := by
  rw [← map_sub]
  exact obstruction_norm_le R K h (v-w)

 theorem inconsistency_noise_bound (v w : V) :
    ‖inconsistency K v - inconsistency K w‖ ≤ ‖v - w‖ := by
  rw [← map_sub]
  exact inconsistency_norm_le K (v-w)

 theorem realized_noise_bound (v w : V) :
    ‖realized R v - realized R w‖ ≤ ‖v - w‖ := by
  rw [← map_sub]
  exact R.norm_starProjection_apply_le (v-w)

end Komorebi.SufficientResolution.OrthogonalResolution
