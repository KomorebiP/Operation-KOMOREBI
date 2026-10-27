module

public import KomorebiPhysics.RefinementCancellation

/-!
Explicit finite-radius remainder and perturbation estimates. They do not
assume noiseless data, and do not claim that cancellation is a contraction.
The bounds hold for real normed-space outputs without completeness.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics.RefinementBounds
open scoped BigOperators
open KomorebiPhysics.RefinementCancellation
variable {E : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]

/-- Explicit propagation factor for a degree-p norm envelope. -/
def amplification (b : ℝ) (p : ℕ) : ℕ → ℝ
  | 0 => 1
  | m+1 => ((b^(m+1)/b^p+1)/(b^(m+1)-1)) * amplification b p m

theorem amplification_product (b : ℝ) (p m : ℕ) :
    amplification b p m = ∏ k ∈ Finset.range m,
      ((b^(k+1)/b^p+1)/(b^(k+1)-1)) := by
  induction m with
  | zero => simp [amplification]
  | succ m ih => simp only [amplification, Finset.prod_range_succ, ih, mul_comm]

theorem amplification_pos {b : ℝ} (hb : 1 < b) (p m : ℕ) :
    0 < amplification b p m := by
  have hb0 : 0 < b := lt_trans zero_lt_one hb
  induction m with
  | zero => norm_num [amplification]
  | succ m ih =>
    simp only [amplification]
    exact mul_pos (div_pos (by positivity) (denominator_pos hb m)) ih

theorem noise_amplification_product (b : ℝ) (m : ℕ) :
    amplification b 0 m = ∏ k ∈ Finset.range m,
      ((b^(k+1)+1)/(b^(k+1)-1)) := by
  simp only [amplification_product, pow_zero, div_one]

/-- One extrapolation step's norm bound retains both sampled errors. -/
theorem step_norm_le {b : ℝ} (hb : 1 < b) (m : ℕ) (u v : E) :
    ‖(b^(m+1)-1)⁻¹ • (b^(m+1) • u - v)‖ ≤
      (b^(m+1)*‖u‖ + ‖v‖) / (b^(m+1)-1) := by
  have hp : 0 < b^(m+1) := pow_pos (lt_trans zero_lt_one hb) _
  have hd := denominator_pos hb m
  rw [norm_smul, Real.norm_eq_abs, abs_of_pos (inv_pos.mpr hd)]
  calc
    _ ≤ (b^(m+1)-1)⁻¹ * (‖b^(m+1) • u‖ + ‖v‖) :=
      mul_le_mul_of_nonneg_left (norm_sub_le _ _) (le_of_lt (inv_pos.mpr hd))
    _ = _ := by
      rw [norm_smul, Real.norm_eq_abs, abs_of_pos hp]
      ring

/-- Scale-invariant-domain estimate for the actual tower. -/
theorem tower_bound_on {b : ℝ} (hb : 1 < b) (f : ℝ → E)
    (S : Set ℝ) (hS : ∀ x ∈ S, x/b ∈ S) (C : ℝ) (p m : ℕ)
    (hf : ∀ x ∈ S, ‖f x‖ ≤ C * ‖x‖^p) {h : ℝ} (hh : h ∈ S) :
    ‖tower b f m h‖ ≤ amplification b p m * C * ‖h‖^p := by
  have hb0 : 0 < b := lt_trans zero_lt_one hb
  induction m generalizing h with
  | zero => simpa only [tower, amplification, one_mul] using hf h hh
  | succ m ih =>
    have h1 := ih (hS h hh)
    have h2 := ih hh
    have hp : 0 ≤ b^(m+1) := le_of_lt (pow_pos hb0 _)
    have hd : 0 < b^(m+1)-1 := denominator_pos hb m
    calc
      ‖tower b f (m+1) h‖ ≤
          (b^(m+1)*‖tower b f m (h/b)‖ + ‖tower b f m h‖) /
            (b^(m+1)-1) := step_norm_le hb m _ _
      _ ≤ (b^(m+1)*(amplification b p m * C * ‖h/b‖^p) +
          amplification b p m * C * ‖h‖^p) / (b^(m+1)-1) :=
        div_le_div_of_nonneg_right (add_le_add (mul_le_mul_of_nonneg_left h1 hp) h2)
          (le_of_lt hd)
      _ = _ := by
        rw [norm_div, Real.norm_eq_abs b, abs_of_pos hb0, div_pow]
        simp only [amplification]
        ring

/-- A punctured radius is stable under genuine refinement. -/
theorem punctured_ball_scale {b : ℝ} (hb : 1 < b) (δ : ℝ) {h : ℝ}
    (hh : h ≠ 0 ∧ ‖h‖ < δ) : h/b ≠ 0 ∧ ‖h/b‖ < δ := by
  have hb0 : 0 < b := lt_trans zero_lt_one hb
  refine ⟨div_ne_zero hh.1 (ne_of_gt hb0), lt_of_le_of_lt ?_ hh.2⟩
  rw [norm_div, Real.norm_eq_abs b, abs_of_pos hb0]
  exact div_le_self (norm_nonneg _) (le_of_lt hb)

theorem tower_bound_punctured {b : ℝ} (hb : 1 < b) (f : ℝ → E)
    (δ C : ℝ) (p m : ℕ)
    (hf : ∀ h : ℝ, h ≠ 0 → ‖h‖ < δ → ‖f h‖ ≤ C * ‖h‖^p)
    {h : ℝ} (hh0 : h ≠ 0) (hhδ : ‖h‖ < δ) :
    ‖tower b f m h‖ ≤ amplification b p m * C * ‖h‖^p := by
  exact tower_bound_on hb f {x : ℝ | x ≠ 0 ∧ ‖x‖ < δ}
    (fun _ hx => punctured_ball_scale hb δ hx) C p m
    (fun _ hx => hf _ hx.1 hx.2) ⟨hh0, hhδ⟩

/-- Quantified version of the cancellation theorem, with actual error constant. -/
theorem cancellation_bound {b : ℝ} (hb : 1 < b) (f : ℝ → E)
    (F : E) (c : ℕ → E) (δ C : ℝ) (m p : ℕ)
    (hf : ∀ h : ℝ, h ≠ 0 → ‖h‖ < δ →
      ‖f h - expansion F c m h‖ ≤ C * ‖h‖^p)
    {h : ℝ} (hh0 : h ≠ 0) (hhδ : ‖h‖ < δ) :
    ‖tower b f m h - F‖ ≤ amplification b p m * C * ‖h‖^p := by
  rw [tower_error_identity hb f F c m]
  exact tower_bound_punctured hb _ δ C p m hf hh0 hhδ

/-- Noisy samples propagate linearly, with a separately proved error bound. -/
theorem perturbation_bound {b : ℝ} (hb : 1 < b) (f g : ℝ → E)
    (δ ε : ℝ) (m : ℕ)
    (herr : ∀ h : ℝ, h ≠ 0 → ‖h‖ < δ → ‖g h-f h‖ ≤ ε)
    {h : ℝ} (hh0 : h ≠ 0) (hhδ : ‖h‖ < δ) :
    ‖tower b g m h - tower b f m h‖ ≤ amplification b 0 m * ε := by
  rw [← tower_sub]
  have hf : ∀ h : ℝ, h ≠ 0 → ‖h‖ < δ → ‖g h-f h‖ ≤ ε * ‖h‖^0 := by
    simpa only [pow_zero, mul_one] using herr
  simpa only [pow_zero, mul_one] using
    tower_bound_punctured hb (fun x => g x-f x) δ ε 0 m hf hh0 hhδ

/-- Truncation and sample perturbation are separate contributions. -/
theorem noisy_cancellation_bound {b : ℝ} (hb : 1 < b) (f g : ℝ → E)
    (F : E) (c : ℕ → E) (δ C ε : ℝ) (m p : ℕ)
    (hf : ∀ h : ℝ, h ≠ 0 → ‖h‖ < δ →
      ‖f h - expansion F c m h‖ ≤ C * ‖h‖^p)
    (herr : ∀ h : ℝ, h ≠ 0 → ‖h‖ < δ → ‖g h-f h‖ ≤ ε)
    {h : ℝ} (hh0 : h ≠ 0) (hhδ : ‖h‖ < δ) :
    ‖tower b g m h - F‖ ≤ amplification b p m * C * ‖h‖^p +
      amplification b 0 m * ε := by
  calc
    _ ≤ ‖tower b g m h - tower b f m h‖ + ‖tower b f m h-F‖ :=
      norm_sub_le_norm_sub_add_norm_sub _ _ _
    _ ≤ amplification b 0 m * ε + amplification b p m * C * ‖h‖^p :=
      add_le_add (perturbation_bound hb f g δ ε m herr hh0 hhδ)
        (cancellation_bound hb f F c δ C m p hf hh0 hhδ)
    _ = _ := add_comm _ _

end KomorebiPhysics.RefinementBounds
