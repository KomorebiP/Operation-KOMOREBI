import KomorebiSpace.RepairDynamics

set_option autoImplicit false

/-!
# A bounded projection onto exact candidates

A fixed bounded correction operator with geometric contraction determines a
bounded linear projection onto the exact kernel. Different valid correction
operators need not give the same projection without semantic separation.
-/
universe u v w z
noncomputable section
namespace KomorebiSpace
namespace RepairDynamics
open Filter
open scoped Topology
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable {E : Type v} {R : Type w} {S : Type z}
variable [NormedAddCommGroup E] [NormedSpace 𝕜 E]
variable [NormedAddCommGroup R] [NormedSpace 𝕜 R]
variable [NormedAddCommGroup S] [NormedSpace 𝕜 S]

/-- Data sufficient to construct a protected exactification projection. -/
structure Scheme (d : E →L[𝕜] R) (p : E →L[𝕜] S) where
  correction : R →L[𝕜] E
  rate : ℝ
  rate_nonneg : 0 ≤ rate
  rate_lt_one : rate < 1
  preserve : ∀ r, p (correction r) = 0
  contract : ∀ x, ‖d x - d (correction (d x))‖ ≤ rate * ‖d x‖

theorem orbit_add (d : E →L[𝕜] R) (A : R →L[𝕜] E) (x y : E) (n : ℕ) :
    orbit d A (x+y) n = orbit d A x n + orbit d A y n := by
  induction n with
  | zero => rfl
  | succ n ih =>
    simp only [orbit_succ, step, ih, map_add]
    abel

theorem orbit_smul (d : E →L[𝕜] R) (A : R →L[𝕜] E) (c : 𝕜) (x : E) (n : ℕ) :
    orbit d A (c • x) n = c • orbit d A x n := by
  induction n with
  | zero => rfl
  | succ n ih => simp [orbit_succ, step, ih, smul_sub]

variable [CompleteSpace E]
namespace Scheme
variable {d : E →L[𝕜] R} {p : E →L[𝕜] S} (B : Scheme d p)

def limit (x : E) : E :=
  Classical.choose (exactification_from_correction_operator d p B.correction
    B.rate B.rate_nonneg B.rate_lt_one B.preserve B.contract x)

theorem limit_spec (x : E) :
    Tendsto (orbit d B.correction x) atTop (𝓝 (B.limit x)) ∧
      d (B.limit x) = 0 ∧ p (B.limit x) = p x ∧
      ∀ n, dist (orbit d B.correction x n) (B.limit x) ≤
        (‖B.correction‖ / (1-B.rate)) * ‖d (orbit d B.correction x n)‖ :=
  Classical.choose_spec (exactification_from_correction_operator d p B.correction
    B.rate B.rate_nonneg B.rate_lt_one B.preserve B.contract x)

theorem tendsto_limit (x : E) :
    Tendsto (orbit d B.correction x) atTop (𝓝 (B.limit x)) := (B.limit_spec x).1

@[simp] theorem limit_exact (x : E) : d (B.limit x) = 0 := (B.limit_spec x).2.1

@[simp] theorem limit_semantics (x : E) : p (B.limit x) = p x :=
  (B.limit_spec x).2.2.1

theorem limit_error (x : E) :
    dist x (B.limit x) ≤ (‖B.correction‖ / (1-B.rate)) * ‖d x‖ :=
  (B.limit_spec x).2.2.2 0

/-- The limit fixes all exact elements, independently of semantic injectivity. -/
theorem limit_fixes_exact (x : E) (hx : d x = 0) : B.limit x = x := by
  have h : Tendsto (orbit d B.correction x) atTop (𝓝 x) := by
    change Tendsto (fun n => orbit d B.correction x n) atTop (𝓝 x)
    simpa only [orbit_fixes_exact d B.correction x hx] using
      (tendsto_const_nhds : Tendsto (fun _ : ℕ => x) atTop (𝓝 x))
  exact tendsto_nhds_unique (B.tendsto_limit x) h

theorem limit_add (x y : E) : B.limit (x+y) = B.limit x + B.limit y := by
  have h : Tendsto (orbit d B.correction (x+y)) atTop (𝓝 (B.limit x + B.limit y)) := by
    change Tendsto (fun n => orbit d B.correction (x+y) n) atTop (𝓝 (B.limit x + B.limit y))
    simpa only [orbit_add] using (B.tendsto_limit x).add (B.tendsto_limit y)
  exact tendsto_nhds_unique (B.tendsto_limit (x+y)) h

theorem limit_smul (c : 𝕜) (x : E) : B.limit (c • x) = c • B.limit x := by
  have h : Tendsto (orbit d B.correction (c • x)) atTop (𝓝 (c • B.limit x)) := by
    change Tendsto (fun n => orbit d B.correction (c • x) n) atTop (𝓝 (c • B.limit x))
    simpa only [orbit_smul] using (B.tendsto_limit x).const_smul c
  exact tendsto_nhds_unique (B.tendsto_limit (c • x)) h

/-- A supplied correction scheme yields linearity of its limiting repair. -/
def linearProjection : E →ₗ[𝕜] E where
  toFun := B.limit
  map_add' := B.limit_add
  map_smul' := B.limit_smul

def stabilityConstant : ℝ := 1 + (‖B.correction‖ / (1-B.rate)) * ‖d‖

omit [CompleteSpace E] in
theorem stabilityConstant_nonneg : 0 ≤ B.stabilityConstant := by
  have h : 0 < 1-B.rate := sub_pos.mpr B.rate_lt_one
  unfold stabilityConstant
  positivity

theorem limit_bound (x : E) : ‖B.limit x‖ ≤ B.stabilityConstant * ‖x‖ := by
  have hC : 0 ≤ ‖B.correction‖ / (1-B.rate) :=
    div_nonneg (norm_nonneg _) (le_of_lt (sub_pos.mpr B.rate_lt_one))
  calc
    ‖B.limit x‖ = dist 0 (B.limit x) := (dist_zero_left _).symm
    _ ≤ dist 0 x + dist x (B.limit x) := dist_triangle _ _ _
    _ = ‖x‖ + dist x (B.limit x) := by rw [dist_zero_left]
    _ ≤ ‖x‖ + (‖B.correction‖ / (1-B.rate)) * ‖d x‖ :=
      add_le_add le_rfl (B.limit_error x)
    _ ≤ ‖x‖ + (‖B.correction‖ / (1-B.rate)) * (‖d‖ * ‖x‖) :=
      add_le_add le_rfl (mul_le_mul_of_nonneg_left (d.le_opNorm x) hC)
    _ = B.stabilityConstant * ‖x‖ := by unfold stabilityConstant; ring

/-- The exactification limit is a constructed bounded linear operator. -/
def projection : E →L[𝕜] E :=
  B.linearProjection.mkContinuous B.stabilityConstant B.limit_bound

@[simp] theorem projection_apply (x : E) : B.projection x = B.limit x := rfl

theorem projection_bound : ‖B.projection‖ ≤ B.stabilityConstant :=
  ContinuousLinearMap.opNorm_le_bound _ B.stabilityConstant_nonneg B.limit_bound

/-- Idempotence: repeated exactification introduces no further change. -/
theorem projection_idempotent (x : E) : B.projection (B.projection x) = B.projection x :=
  B.limit_fixes_exact _ (B.limit_exact x)

/-- The image is exactly the zero-residual kernel. -/
theorem projection_image_iff (y : E) : (∃ x, B.projection x = y) ↔ d y = 0 := by
  constructor
  · rintro ⟨x, rfl⟩
    exact B.limit_exact x
  · intro hy
    exact ⟨y, B.limit_fixes_exact y hy⟩

/-- Every candidate splits into an exact part and a semantically invisible correction. -/
theorem exact_residual_splitting (x : E) :
    x = B.projection x + (x - B.projection x) ∧
    d (B.projection x) = 0 ∧ p (x - B.projection x) = 0 ∧
    d (x - B.projection x) = d x ∧ B.projection (x - B.projection x) = 0 := by
  refine ⟨by abel, B.limit_exact x, ?_, ?_, ?_⟩
  · simp only [map_sub, projection_apply, limit_semantics, sub_self]
  · simp only [map_sub, projection_apply, limit_exact, sub_zero]
  · rw [map_sub, B.projection_idempotent, sub_self]

/-- Different valid schemes agree only under the stated separation hypothesis. -/
theorem scheme_independent (B' : Scheme d p)
    (hsep : ∀ a b, d a = 0 → d b = 0 → p a = p b → a = b) :
    B.projection = B'.projection := by
  ext x
  exact hsep _ _ (B.limit_exact x) (B'.limit_exact x)
    ((B.limit_semantics x).trans (B'.limit_semantics x).symm)

end Scheme
end RepairDynamics
end KomorebiSpace
end
