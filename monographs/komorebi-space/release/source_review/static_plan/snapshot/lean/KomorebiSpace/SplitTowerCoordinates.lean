import KomorebiSpace.SplitTowerSemantics

set_option autoImplicit false

/-!
# Residual-semantic coordinates as a continuous linear equivalence

For split towers with a strict propagation gap, candidate transports are
continuously linearly equivalent to protected semantic data times residuals.
The forward map is (observable, differential). Its inverse is the explicit
exact repair plus the explicit residual correction.
-/
universe u v
noncomputable section
open scoped NNReal ENNReal
namespace KomorebiSpace
namespace BanachTower
namespace Splitting
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (X : BanachTower.{u,v} 𝕜) {Y : BanachTower.{u,v} 𝕜}
variable (L : Splitting Y)

/-- Valid protected profiles are exactly the fixed points of the observable. -/
def semanticSpace : Submodule 𝕜 (Candidates X Y) :=
  LinearMap.ker ((L.observable X - ContinuousLinearMap.id 𝕜 _).toLinearMap)

@[simp] theorem mem_semanticSpace (s : Candidates X Y) :
    s ∈ L.semanticSpace X ↔ L.observable X s = s := by
  change L.observable X s - s = 0 ↔ _
  exact sub_eq_zero

variable (hgap : (L.bound : ℝ) * X.bound < 1)

/-- A genuine bijective linear coordinate map, with an explicit inverse. -/
def coordinateEquiv : Candidates X Y ≃ₗ[𝕜] (L.semanticSpace X × Residuals X Y) where
  toFun f := (⟨L.observable X f, (L.mem_semanticSpace X _).mpr
    (L.observable_idempotent X f)⟩, differential X Y f)
  invFun z := L.repair X hgap z.1.val + L.correction X hgap z.2
  left_inv f := by
    apply L.residual_observable_injective X
    · simp
    · simp
  right_inv z := by
    apply Prod.ext
    · apply Subtype.ext
      change L.observable X (L.repair X hgap z.1.val + L.correction X hgap z.2) = z.1.val
      simp only [map_add, repair_preserves_observable, observable_correction, add_zero]
      exact (L.mem_semanticSpace X _).mp z.1.property
    · change differential X Y (L.repair X hgap z.1.val + L.correction X hgap z.2) = z.2
      simp
  map_add' f g := by
    apply Prod.ext
    · apply Subtype.ext
      exact map_add (L.observable X) f g
    · exact map_add (differential X Y) f g
  map_smul' c f := by
    apply Prod.ext
    · apply Subtype.ext
      exact map_smul (L.observable X) c f
    · exact map_smul (differential X Y) c f

@[simp] theorem coordinate_semantics (f : Candidates X Y) :
    ((L.coordinateEquiv X hgap f).1 : Candidates X Y) = L.observable X f := rfl

@[simp] theorem coordinate_residual (f : Candidates X Y) :
    (L.coordinateEquiv X hgap f).2 = differential X Y f := rfl

@[simp] theorem coordinate_inverse (z : L.semanticSpace X × Residuals X Y) :
    (L.coordinateEquiv X hgap).symm z =
      L.repair X hgap z.1.val + L.correction X hgap z.2 := rfl

theorem coordinate_bound (f : Candidates X Y) :
    ‖L.coordinateEquiv X hgap f‖ ≤
      max (1 + (L.bound : ℝ) * Y.bound) ((X.bound : ℝ) + Y.bound) * ‖f‖ := by
  change max ‖L.observable X f‖ ‖differential X Y f‖ ≤ _
  apply max_le
  · exact (L.observable_bound X f).trans
      (mul_le_mul_of_nonneg_right (le_max_left _ _) (norm_nonneg f))
  · exact (differential_bound X Y f).trans
      (mul_le_mul_of_nonneg_right (le_max_right _ _) (norm_nonneg f))

theorem coordinate_inverse_bound (z : L.semanticSpace X × Residuals X Y) :
    ‖(L.coordinateEquiv X hgap).symm z‖ ≤
      (‖L.repair X hgap‖ + ‖L.correction X hgap‖) * ‖z‖ := by
  have h1 : ‖z.1.val‖ ≤ ‖z‖ := le_max_left _ _
  have h2 : ‖z.2‖ ≤ ‖z‖ := le_max_right _ _
  calc
    ‖(L.coordinateEquiv X hgap).symm z‖ ≤
        ‖L.repair X hgap z.1.val‖ + ‖L.correction X hgap z.2‖ := norm_add_le _ _
    _ ≤ ‖L.repair X hgap‖ * ‖z.1.val‖ + ‖L.correction X hgap‖ * ‖z.2‖ :=
      add_le_add ((L.repair X hgap).le_opNorm _) ((L.correction X hgap).le_opNorm _)
    _ ≤ ‖L.repair X hgap‖ * ‖z‖ + ‖L.correction X hgap‖ * ‖z‖ :=
      add_le_add (mul_le_mul_of_nonneg_left h1 (norm_nonneg _))
        (mul_le_mul_of_nonneg_left h2 (norm_nonneg _))
    _ = (‖L.repair X hgap‖ + ‖L.correction X hgap‖) * ‖z‖ := by ring

/-- The coordinate system preserves both linear and topological structure. -/
def coordinates : Candidates X Y ≃L[𝕜] (L.semanticSpace X × Residuals X Y) :=
  (L.coordinateEquiv X hgap).toContinuousLinearEquivOfBounds
    (max (1 + (L.bound : ℝ) * Y.bound) ((X.bound : ℝ) + Y.bound))
    (‖L.repair X hgap‖ + ‖L.correction X hgap‖)
    (L.coordinate_bound X hgap) (L.coordinate_inverse_bound X hgap)

/-- In these coordinates, exactness is exactly the zero residual slice. -/
theorem exact_iff_zero_residual_coordinate (f : Candidates X Y) :
    Exact X Y f ↔ (L.coordinates X hgap f).2 = 0 :=
  exact_iff_differential_zero X Y f

/-- Repair keeps the semantic coordinate and sets the residual coordinate to zero. -/
theorem coordinates_repair (f : Candidates X Y) :
    L.coordinates X hgap (L.repair X hgap f) = ((L.coordinates X hgap f).1, 0) := by
  apply Prod.ext
  · apply Subtype.ext
    exact L.repair_preserves_observable X hgap f
  · exact L.repair_differential_zero X hgap f

/-- Correction inserts a residual without changing any protected coordinate. -/
theorem coordinates_correction (r : Residuals X Y) :
    L.coordinates X hgap (L.correction X hgap r) = (0, r) := by
  apply Prod.ext
  · apply Subtype.ext
    exact L.observable_correction X hgap r
  · exact L.differential_correction X hgap r

end Splitting
end BanachTower
end KomorebiSpace
end
