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
open scoped Topology BigOperators
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
  simp only [div_pow]
  simpa only [div_eq_mul_inv, mul_comm] using
    isBigO_const_mul_self ((b^p)⁻¹) (fun h : ℝ => h^p) l

omit [NormedSpace ℝ E] in
theorem scaled_isBigO {b : ℝ} (hb : b ≠ 0) {f : ℝ → E} (p : ℕ)
    (hf : f =O[𝓝[≠] 0] (fun h : ℝ => h^p)) :
    (fun h => f (h/b)) =O[𝓝[≠] 0] (fun h : ℝ => h^p) := by
  exact (hf.comp_tendsto (tendsto_div_punctured hb)).trans
    (scaled_power_isBigO b p _)

omit [NormedSpace ℝ E] in
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
    exact ht

theorem tower_isLittleO {b : ℝ} (hb : b ≠ 0) {f : ℝ → E} (m p : ℕ)
    (hf : f =o[𝓝[≠] 0] (fun h : ℝ => h^p)) :
    tower b f m =o[𝓝[≠] 0] (fun h : ℝ => h^p) := by
  induction m with
  | zero => exact hf
  | succ m ih =>
    have hs := (scaled_isLittleO hb p ih).const_smul_left (b^(m+1))
    have ht := (hs.sub ih).const_smul_left ((b^(m+1)-1)⁻¹)
    exact ht

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
    have ht : Tendsto (fun h : ℝ => h^p) (𝓝 0) (𝓝 ((0 : ℝ)^p)) :=
      (continuous_id.pow p).tendsto (0 : ℝ)
    simpa only [zero_pow (Nat.ne_of_gt hp)] using
      ht.mono_left (nhdsWithin_le_nhds (s := ({0}ᶜ : Set ℝ)))
  have ht := (cancellation_isBigO hb f F c m p hexp).trans_tendsto hpw
  have ha := ht.add_const F
  simpa only [zero_add, sub_add_cancel] using ha


/-- The full finite expansion is transported, not just its constant term. -/
theorem transformed_expansion_isBigO {b : ℝ} (hb : 1 < b) (f : ℝ → E)
    (F : E) (c : ℕ → E) (n m p : ℕ)
    (hexp : (fun h => f h-expansion F c n h) =O[𝓝[≠] 0]
      (fun h : ℝ => h^p)) :
    (fun h => tower b f m h - (F + ∑ k ∈ Finset.range n,
      (coefficient b m (k+1)*h^(k+1)) • c k)) =O[𝓝[≠] 0]
        (fun h : ℝ => h^p) := by
  have ht := tower_isBigO (ne_of_gt (lt_trans zero_lt_one hb)) m p hexp
  exact ht.congr_left (fun h => (transformed_error_identity hb f F c n m h).symm)

/-- A lower nonzero monomial cannot satisfy a higher-order bound near zero. -/
theorem power_not_isBigO_higher (p q : ℕ) (hpq : p < q) :
    ¬ ((fun h : ℝ => h^p) =O[𝓝[≠] 0] (fun h : ℝ => h^q)) := by
  intro hO
  have ho : (fun h : ℝ => h^q) =o[𝓝[≠] 0] (fun h : ℝ => h^p) :=
    (isLittleO_pow_pow hpq).mono nhdsWithin_le_nhds
  have he := (hO.trans_isLittleO ho).bound (by norm_num : (0 : ℝ) < 1/2)
  have hf : ∀ᶠ h : ℝ in 𝓝[≠] 0, False := by
    filter_upwards [he, self_mem_nhdsWithin] with h hh hn
    change h ≠ 0 at hn
    have hp : 0 < ‖h^p‖ := norm_pos_iff.mpr (pow_ne_zero p hn)
    linarith
  exact hf.exists.elim (fun _ hh => hh)

/-- Sharpness: depth m does not generally improve beyond order m+1. -/
theorem tower_not_extra_order {b : ℝ} (hb : 1 < b) (m : ℕ) :
    ¬ (tower b (fun h : ℝ => h^(m+1)) m =O[𝓝[≠] 0]
      (fun h : ℝ => h^(m+2))) := by
  intro hO
  have heq : tower b (fun h : ℝ => h^(m+1)) m =
      fun h : ℝ => coefficient b m (m+1)*h^(m+1) := by
    funext h
    simpa only [smul_eq_mul, mul_one] using tower_monomial b m (m+1) (1 : ℝ) h
  rw [heq] at hO
  have hbase : (fun h : ℝ => h^(m+1)) =O[𝓝[≠] 0] (fun h : ℝ => h^(m+2)) :=
    (isBigO_const_mul_left_iff (coefficient_ne_zero_above hb m (m+1) (by omega))).mp hO
  exact power_not_isBigO_higher (m+1) (m+2) (by omega) hbase


/-- The remainder argument works on any filter stable under sampling. -/
theorem tower_isBigO_filter (b : ℝ) (l : Filter ℝ)
    (hscale : Tendsto (fun h : ℝ => h/b) l l) (f : ℝ → E) (m p : ℕ)
    (hf : f =O[l] (fun h : ℝ => h^p)) :
    tower b f m =O[l] (fun h : ℝ => h^p) := by
  induction m with
  | zero => exact hf
  | succ m ih =>
    have hs := ((ih.comp_tendsto hscale).trans (scaled_power_isBigO b p l)).const_smul_left
      (b^(m+1))
    exact (hs.sub ih).const_smul_left ((b^(m+1)-1)⁻¹)

/-- Positive step sizes stay positive under a positive refinement ratio. -/
theorem tendsto_div_positive {b : ℝ} (hb : 0 < b) :
    Tendsto (fun h : ℝ => h/b) (𝓝[>] 0) (𝓝[>] 0) := by
  refine tendsto_nhdsWithin_iff.mpr ⟨?_, ?_⟩
  · have ht : Tendsto (fun h : ℝ => h/b) (𝓝 0) (𝓝 0) := by
      simpa using (continuous_id.div_const b).tendsto (0 : ℝ)
    exact ht.mono_left nhdsWithin_le_nhds
  · filter_upwards [self_mem_nhdsWithin] with h hh
    exact div_pos hh hb

/-- One-sided physical step-size version. No negative-h expansion is needed. -/
theorem positive_step_order_improvement {b : ℝ} (hb : 1 < b) (f : ℝ → E)
    (F : E) (c : ℕ → E) (m : ℕ)
    (hexp : (fun h => f h-expansion F c m h) =O[𝓝[>] 0]
      (fun h : ℝ => h^(m+1))) :
    (fun h => table b f h m 0-F) =O[𝓝[>] 0] (fun h : ℝ => h^(m+1)) := by
  have ht := tower_isBigO_filter b (𝓝[>] 0)
    (tendsto_div_positive (lt_trans zero_lt_one hb)) _ m (m+1) hexp
  exact ht.congr_left (fun h => by
    rw [table_base_column, tower_error_identity hb f F c m])

end KomorebiPhysics.RefinementAsymptotics
