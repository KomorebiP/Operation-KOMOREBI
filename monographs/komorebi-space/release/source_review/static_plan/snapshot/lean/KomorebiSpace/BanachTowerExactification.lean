import KomorebiSpace.BanachTowers
import KomorebiSpace.RepairProjection

set_option autoImplicit false

/-!
# Actual bounded-tower exactification

The algebraic tower differential and the Banach-space convergence theorem are
connected here. The protected observable is a complete operator at a chosen
resolution level. Realization is in the explicitly constructed inverse limit,
not an unspecified underlying object. A correction operator is input data.
-/
universe u v
noncomputable section
namespace KomorebiSpace
namespace BanachTower
open Filter
open scoped Topology NNReal ENNReal
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable (X Y : BanachTower.{u,v} 𝕜)

/-- Exactification of an actual sequence of bounded resolution transports. -/
theorem geometric_exactification
    (f : ℕ → Candidates X Y) (k : ℕ) (q C : ℝ)
    (hq₀ : 0 ≤ q) (hq₁ : q < 1) (hC : 0 ≤ C)
    (hdec : ∀ n, ‖differential X Y (f (n+1))‖ ≤ q * ‖differential X Y (f n)‖)
    (hstep : ∀ n, dist (f n) (f (n+1)) ≤ C * ‖differential X Y (f n)‖)
    (hkeep : ∀ n, f n k = f 0 k) :
    ∃ g, Tendsto f atTop (𝓝 g) ∧ Exact X Y g ∧ g k = f 0 k ∧
      ∀ n, dist (f n) g ≤ (C / (1-q)) * ‖differential X Y (f n)‖ := by
  obtain ⟨g, hlim, hd, hk, hbound⟩ :=
    LinearExactification.geometric_semantic_exactification
      (differential X Y) (evaluation X Y k) f q C hq₀ hq₁ hC hdec hstep hkeep
  exact ⟨g, hlim, (exact_iff_differential_zero X Y g).mpr hd, hk, hbound⟩

/-- The sup-norm error controls every finite-resolution operator error. -/
theorem coordinate_dist_le (f g : Candidates X Y) (n : ℕ) :
    dist (f n) (g n) ≤ dist f g := by
  simpa only [dist_eq_norm, lp.coeFn_sub, Pi.sub_apply] using
    lp.norm_apply_le_norm ENNReal.top_ne_zero (f-g) n

/-- A nonzero protected level rules out the vacuous zero repair. -/
theorem nonzero_of_protected_level (f g : Candidates X Y) (k : ℕ)
    (hkeep : g k = f k) (hnonzero : f k ≠ 0) : g ≠ 0 := by
  intro hz
  apply hnonzero
  rw [← hkeep, hz]
  rfl

/-- A bounded correction operator produces an exact tower transport. -/
theorem repair_by_operator
    (A : Residuals X Y →L[𝕜] Candidates X Y) (k : ℕ)
    (q : ℝ) (hq₀ : 0 ≤ q) (hq₁ : q < 1)
    (hkeep : ∀ r, A r k = 0)
    (hcontract : ∀ f : Candidates X Y,
      ‖differential X Y f - differential X Y (A (differential X Y f))‖ ≤
        q * ‖differential X Y f‖)
    (f : Candidates X Y) :
    ∃ g, Tendsto (RepairDynamics.orbit (differential X Y) A f) atTop (𝓝 g) ∧
      Exact X Y g ∧ g k = f k ∧
      ∀ n, dist (RepairDynamics.orbit (differential X Y) A f n) g ≤
        (‖A‖ / (1-q)) *
          ‖differential X Y (RepairDynamics.orbit (differential X Y) A f n)‖ := by
  obtain ⟨g, hlim, hd, hk, hbound⟩ :=
    RepairDynamics.exactification_from_correction_operator
      (differential X Y) (evaluation X Y k) A q hq₀ hq₁ hkeep hcontract f
  exact ⟨g, hlim, (exact_iff_differential_zero X Y g).mpr hd, hk, hbound⟩

/-- The repaired tower realizes an actual map of coherent inverse-limit points. -/
theorem repair_and_realize
    (A : Residuals X Y →L[𝕜] Candidates X Y) (k : ℕ)
    (q : ℝ) (hq₀ : 0 ≤ q) (hq₁ : q < 1)
    (hkeep : ∀ r, A r k = 0)
    (hcontract : ∀ f : Candidates X Y,
      ‖differential X Y f - differential X Y (A (differential X Y f))‖ ≤
        q * ‖differential X Y f‖)
    (f : Candidates X Y) :
    ∃ g : Candidates X Y, ∃ F : X.Point → Y.Point,
      Exact X Y g ∧ g k = f k ∧
      Tendsto (RepairDynamics.orbit (differential X Y) A f) atTop (𝓝 g) ∧
      dist f g ≤ (‖A‖ / (1-q)) * ‖differential X Y f‖ ∧
      (∀ x n, (F x).val n = g n (x.val n)) ∧
      ∀ x, (F x).val k = f k (x.val k) := by
  obtain ⟨g, hlim, hexact, hk, hb⟩ :=
    repair_by_operator X Y A k q hq₀ hq₁ hkeep hcontract f
  refine ⟨g, onLimit X Y g hexact, hexact, hk, hlim, hb 0, ?_, ?_⟩
  · intro x n
    rfl
  · intro x
    change g k (x.val k) = f k (x.val k)
    rw [hk]

/-- Canonicity of repair requires separation by the protected level. -/
theorem unique_repair_of_separation
    (A : Residuals X Y →L[𝕜] Candidates X Y) (k : ℕ)
    (q : ℝ) (hq₀ : 0 ≤ q) (hq₁ : q < 1)
    (hkeep : ∀ r, A r k = 0)
    (hcontract : ∀ f : Candidates X Y,
      ‖differential X Y f - differential X Y (A (differential X Y f))‖ ≤
        q * ‖differential X Y f‖)
    (hsep : ∀ a b : Candidates X Y, Exact X Y a → Exact X Y b → a k = b k → a = b)
    (f : Candidates X Y) :
    ∃! g : Candidates X Y, Exact X Y g ∧ g k = f k := by
  obtain ⟨g, _, hg, hk, _⟩ := repair_by_operator X Y A k q hq₀ hq₁ hkeep hcontract f
  refine ⟨g, ⟨hg, hk⟩, ?_⟩
  intro z hz
  exact hsep z g hz.1 hg (hz.2.trans hk.symm)

/-- The abstract limiting projector instantiated on actual tower candidates. -/
def exactificationProjection (k : ℕ)
    (B : RepairDynamics.Scheme (differential X Y) (evaluation X Y k)) :
    Candidates X Y →L[𝕜] Candidates X Y := B.projection

theorem projection_exact_preserving_idempotent (k : ℕ)
    (B : RepairDynamics.Scheme (differential X Y) (evaluation X Y k))
    (f : Candidates X Y) :
    Exact X Y (exactificationProjection X Y k B f) ∧
      exactificationProjection X Y k B f k = f k ∧
      exactificationProjection X Y k B (exactificationProjection X Y k B f) =
        exactificationProjection X Y k B f := by
  exact ⟨(exact_iff_differential_zero X Y _).mpr (B.limit_exact f),
    B.limit_semantics f, B.projection_idempotent f⟩

/-- The stability bound includes the proved sizes of the actual bonding maps. -/
theorem projection_stability_bound (k : ℕ)
    (B : RepairDynamics.Scheme (differential X Y) (evaluation X Y k)) :
    ‖exactificationProjection X Y k B‖ ≤
      1 + (‖B.correction‖ / (1-B.rate)) * ((X.bound : ℝ) + Y.bound) := by
  have hC : 0 ≤ ‖B.correction‖ / (1-B.rate) :=
    div_nonneg (norm_nonneg _) (le_of_lt (sub_pos.mpr B.rate_lt_one))
  calc
    ‖exactificationProjection X Y k B‖ ≤
        1 + (‖B.correction‖ / (1-B.rate)) * ‖differential X Y‖ := B.projection_bound
    _ ≤ 1 + (‖B.correction‖ / (1-B.rate)) * ((X.bound : ℝ) + Y.bound) :=
      add_le_add le_rfl (mul_le_mul_of_nonneg_left (differential_opNorm X Y) hC)

end BanachTower
end KomorebiSpace
end
