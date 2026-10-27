module

public import KomorebiPhysics.RefinementCancellation
public import Mathlib.Analysis.Asymptotics.Lemmas

/-!
Analytic layer for Chapter 4.9. The limiting filter is punctured h -> 0 in
R, so no arbitrary value assigned to the sampled function at h=0 is used.
A finite-order input expansion, not convergence of an infinite formal
series, is the hypothesis. Every stage and its scaled remainder are actual
functions. All tower depths in these theorems are fixed finite depths.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.RefinementAsymptotics
open Filter Asymptotics
open scoped Topology
open KomorebiPhysics.RefinementCancellation
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- Scaling preserves the punctured limiting domain. -/
theorem tendsto_div_punctured {b : ℝ} (hb : b ≠ 0) :
    Tendsto (fun h : ℝ => h / b) (𝓝[≠] 0) (𝓝[≠] 0) := by
  refine tendsto_nhdsWithin_iff.mpr ⟨?_, ?_⟩
  · have ht : Tendsto (fun h : ℝ => h / b) (𝓝 0) (𝓝 0) := by
      simpa using (continuous_id.div_const b).tendsto (0 : ℝ)
    exact ht.mono_left nhdsWithin_le_nhds
  · filter_upwards [self_mem_nhdsWithin] with h hh
    change h ≠ 0 at hh
    change h / b ≠ 0
    exact div_ne_zero hh hb

/-- Exact rescaling of a power implies the corresponding Big-O comparison. -/
theorem scaled_power_isBigO (b : ℝ) (p : ℕ) (l : Filter ℝ) :
    (fun h : ℝ => (h/b)^p) =O[l] (fun h => h^p) := by
  simpa only [div_pow, div_eq_mul_inv, mul_comm] using
    isBigO_const_mul_self ((b^p)⁻¹) (fun h : ℝ => h^p) l

theorem scaled_isBigO {b : ℝ} (hb : b ≠ 0) {f : ℝ → E} (p : ℕ)
    (hf : f =O[𝓝[≠] 0] (fun h : ℝ => h^p)) :
    (fun h => f (h/b)) =O[𝓝[≠] 0] (fun h : ℝ => h^p) := by
  exact (hf.comp_tendsto (tendsto_div_punctured hb)).trans
    (scaled_power_isBigO b p _)

theorem scaled_isLittleO {b : ℝ} (hb : b ≠ 0) {f : ℝ → E} (p : ℕ)
    (hf : f =o[𝓝[≠] 0] (fun h : ℝ => h^p)) :
    (fun h => f (h/b)) =o[𝓝[≠] 0] (fun h : ℝ => h^p) := by
  exact (hf.comp_tendsto (tendsto_div_punctured hb)).trans_isBigO
    (scaled_power_isBigO b p _)

/-- The actual finite recursive tower preserves an input remainder order. -/
theorem tower_isBigO {b : ℝ} (hb : b ≠ 0) {f : ℝ → E} (m p : ℕ)
    (hf : f =O[𝓝[≠] 0] (fun h : ℝ => h^p)) :
    tower b f m =O[𝓝[≠] 0] (fun h : ℝ => h^p) := by
  induction m with
  | zero => exact hf
  | succ m ih =>
    have hs := (scaled_isBigO hb p ih).const_smul_left (b^(m+1))
    have ht := (hs.sub ih).const_smul_left ((b^(m+1)-1)⁻¹)
    simpa only [Pi.smul_apply, tower] using ht

theorem tower_isLittleO {b : ℝ} (hb : b ≠ 0) {f : ℝ → E} (m p : ℕ)
    (hf : f =o[𝓝[≠] 0] (fun h : ℝ => h^p)) :
    tower b f m =o[𝓝[≠] 0] (fun h : ℝ => h^p) := by
  induction m with
  | zero => exact hf
  | succ m ih =>
    have hs := (scaled_isLittleO hb p ih).const_smul_left (b^(m+1))
    have ht := (hs.sub ih).const_smul_left ((b^(m+1)-1)⁻¹)
    simpa only [Pi.smul_apply, tower] using ht

/-- Actual order improvement from a finite expansion through degree m.
The input is the remainder of the original f, not an extrapolated error. -/
theorem cancellation_isBigO {b : ℝ} (hb : 1 < b) (f : ℝ → E)
    (F : E) (c : ℕ → E) (m p : ℕ)
    (hexp : (fun h => f h - expansion F c m h) =O[𝓝[≠] 0]
      (fun h : ℝ => h^p)) :
    (fun h => tower b f m h - F) =O[𝓝[≠] 0] (fun h : ℝ => h^p) := by
  have ht := tower_isBigO (ne_of_gt (lt_trans zero_lt_one hb)) m p hexp
  exact ht.congr_left (fun h => (tower_error_identity hb f F c m h).symm)

theorem cancellation_isLittleO {b : ℝ} (hb : 1 < b) (f : ℝ → E)
    (F : E) (c : ℕ → E) (m p : ℕ)
    (hexp : (fun h => f h - expansion F c m h) =o[𝓝[≠] 0]
      (fun h : ℝ => h^p)) :
    (fun h => tower b f m h - F) =o[𝓝[≠] 0] (fun h : ℝ => h^p) := by
  have ht := tower_isLittleO (ne_of_gt (lt_trans zero_lt_one hb)) m p hexp
  exact ht.congr_left (fun h => (tower_error_identity hb f F c m h).symm)

/-- Equation (4.62), with its finite analytic expansion hypothesis explicit. -/
theorem dyadic_order_improvement (f : ℝ → E) (F : E) (c : ℕ → E) (m : ℕ)
    (hexp : (fun h => f h - expansion F c m h) =O[𝓝[≠] 0]
      (fun h : ℝ => h^(m+1))) :
    (fun h => table 2 f h m 0 - F) =O[𝓝[≠] 0] (fun h : ℝ => h^(m+1)) := by
  simpa only [table_base_column] using cancellation_isBigO (by norm_num : (1 : ℝ) < 2)
    f F c m (m+1) hexp

/-- Fixed-column extension of the source's zero-column order statement. -/
theorem table_order_improvement {b : ℝ} (hb : 1 < b) (f : ℝ → E)
    (F : E) (c : ℕ → E) (m j p : ℕ)
    (hexp : (fun h => f h - expansion F c m h) =O[𝓝[≠] 0]
      (fun h : ℝ => h^p)) :
    (fun h => table b f h m j - F) =O[𝓝[≠] 0] (fun h : ℝ => h^p) := by
  exact scaled_isBigO (pow_ne_zero j (ne_of_gt (lt_trans zero_lt_one hb))) p
    (cancellation_isBigO hb f F c m p hexp)

/-- Convergence is a genuine topological consequence of the order estimate. -/
theorem tower_tendsto {b : ℝ} (hb : 1 < b) (f : ℝ → E)
    (F : E) (c : ℕ → E) (m p : ℕ) (hp : 0 < p)
    (hexp : (fun h => f h - expansion F c m h) =O[𝓝[≠] 0]
      (fun h : ℝ => h^p)) :
    Tendsto (tower b f m) (𝓝[≠] 0) (𝓝 F) := by
  have hpw : Tendsto (fun h : ℝ => h^p) (𝓝[≠] 0) (𝓝 0) := by
    have ht := ((continuous_id.pow p).tendsto (0 : ℝ)).mono_left nhdsWithin_le_nhds
    simpa only [zero_pow (Nat.ne_of_gt hp)] using ht
  have ht := (cancellation_isBigO hb f F c m p hexp).trans_tendsto hpw
  have ha := ht.add_const F
  simpa only [zero_add, sub_add_cancel] using ha

end KomorebiPhysics.RefinementAsymptotics
