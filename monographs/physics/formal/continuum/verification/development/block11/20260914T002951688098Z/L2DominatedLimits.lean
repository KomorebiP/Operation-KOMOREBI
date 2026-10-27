module
public import Mathlib.Analysis.InnerProductSpace.l2Space
public import Mathlib.Analysis.Normed.Group.Tannery
public import Mathlib.Analysis.Calculus.Deriv.Slope
public import Mathlib.Tactic

/-! Dominated coordinate convergence promoted to the actual Hilbert norm.
The domination is square summable, not just coordinatewise bounded. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace L2DominatedLimits
open Filter
open scoped Topology BigOperators lp

variable {I α : Type*} {l : Filter α}

/-- General square-norm dominated convergence, including arbitrary filters. -/
theorem tendsto_zero {u : α → ℓ²(I, ℂ)} {bound : I → ℝ}
    (hs : Summable (fun i => bound i ^ 2))
    (hc : ∀ i, Tendsto (fun a => u a i) l (𝓝 0))
    (hb : ∀ᶠ a in l, ∀ i, ‖u a i‖ ≤ bound i) :
    Tendsto u l (𝓝 0) := by
  have ht : Tendsto (fun a => ∑' i, ‖u a i‖ ^ 2) l (𝓝 0) := by
    simpa only [tsum_zero] using tendsto_tsum_of_dominated_convergence (g := fun _ : I => (0 : ℝ)) hs
      (fun i => by simpa using (hc i).norm.pow 2)
      (by
        filter_upwards [hb] with a ha i
        rw [Real.norm_eq_abs, abs_of_nonneg (sq_nonneg _)]
        exact pow_le_pow_left₀ (norm_nonneg _) (ha i) 2)
  have he : ∀ a, (∑' i, ‖u a i‖ ^ 2) = ‖u a‖ ^ 2 := by
    intro a
    simpa using (lp.norm_rpow_eq_tsum (by norm_num : 0 < (2 : ENNReal).toReal) (u a)).symm
  simp_rw [he] at ht
  have hn := Real.continuous_sqrt.continuousAt.tendsto.comp ht
  have hn' : Tendsto (fun a => ‖u a‖) l (𝓝 0) := by
    simpa only [Function.comp_def, Real.sqrt_sq (norm_nonneg _), Real.sqrt_zero] using hn
  exact tendsto_zero_iff_norm_tendsto_zero.mpr hn'

/-- Norm convergence follows from square-summable domination of the error. -/
theorem tendsto {u : α → ℓ²(I, ℂ)} {x : ℓ²(I, ℂ)} {bound : I → ℝ}
    (hs : Summable (fun i => bound i ^ 2))
    (hc : ∀ i, Tendsto (fun a => u a i) l (𝓝 (x i)))
    (hb : ∀ᶠ a in l, ∀ i, ‖u a i - x i‖ ≤ bound i) :
    Tendsto u l (𝓝 x) := by
  apply tendsto_iff_norm_sub_tendsto_zero.mpr
  apply tendsto_zero_iff_norm_tendsto_zero.mp
  apply tendsto_zero hs
  · intro i
    simpa only [lp.coeFn_sub, Pi.sub_apply, sub_self] using (hc i).sub_const (x i)
  · exact hb

/-- A usable Hilbert-space bound: the dominating sequence is an actual l2 vector. -/
theorem tendsto_of_vector_bound {u : α → ℓ²(I, ℂ)} {x : ℓ²(I, ℂ)}
    (v : ℓ²(I, ℂ)) (hc : ∀ i, Tendsto (fun a => u a i) l (𝓝 (x i)))
    (hb : ∀ᶠ a in l, ∀ i, ‖u a i - x i‖ ≤ ‖v i‖) :
    Tendsto u l (𝓝 x) := by
  apply tendsto (bound := fun i => ‖v i‖) _ hc hb
  simpa using (lp.memℓp v).summable (by norm_num : 0 < (2 : ENNReal).toReal)

/-- Coordinate derivatives plus domination of slope error prove an l2 derivative.
Coordinate differentiability by itself is explicitly insufficient. -/
theorem hasDerivAt_of_dominated_slope {f : ℝ → ℓ²(I, ℂ)} {y : ℓ²(I, ℂ)} {t : ℝ}
    {bound : I → ℝ} (hs : Summable (fun i => bound i ^ 2))
    (hc : ∀ i, HasDerivAt (fun s => f s i) (y i) t)
    (hb : ∀ᶠ s in 𝓝[≠] t, ∀ i, ‖slope f t s i - y i‖ ≤ bound i) :
    HasDerivAt f y t := by
  apply hasDerivAt_iff_tendsto_slope.mpr
  apply tendsto hs
  · intro i
    simpa only [slope_def_module, lp.coeFn_smul, lp.coeFn_sub, Pi.smul_apply, Pi.sub_apply]
      using (hc i).tendsto_slope
  · exact hb

end L2DominatedLimits
end KomorebiPhysics
