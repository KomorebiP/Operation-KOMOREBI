import CoupledEntire
import Mathlib.Analysis.Analytic.Order

/-!
# Analytic uniqueness of the coupled equations

The proof compares vanishing orders of differences of solution germs.
No parity or coefficient recurrence is assumed of the competing functions.
-/

set_option autoImplicit false
set_option maxHeartbeats 1000000

noncomputable section

open Filter
open scoped Topology

namespace Komorebi.SpecialFunctions.Coupled.Scales

theorem analytic_scale_at_zero {f : ℂ → ℂ} (hf : AnalyticAt ℂ f 0) (c : ℂ) :
    AnalyticAt ℂ (fun z => f (c * z)) 0 := by
  exact hf.comp_of_eq (by fun_prop) (by simp)

/-- Scaling preserves a lower vanishing-order bound. A zero scale is handled
by the zero initial value, rather than by division or an inverse map. -/
theorem analytic_order_scale_ge {f : ℂ → ℂ} (_hf : AnalyticAt ℂ f 0)
    (hzero : f 0 = 0) (c : ℂ) {n : ℕ} (hn : (n : ℕ∞) ≤ analyticOrderAt f 0) :
    (n : ℕ∞) ≤ analyticOrderAt (fun z => f (c * z)) 0 := by
  by_cases hc : c = 0
  · have htop : analyticOrderAt (fun z => f (c * z)) 0 = ⊤ :=
      analyticOrderAt_eq_top.mpr (.of_forall (fun z => by simp [hc, hzero]))
    rw [htop]
    exact le_top
  · have ha : AnalyticAt ℂ (fun z : ℂ => c * z) 0 := by fun_prop
    have hd : deriv (fun z : ℂ => c * z) 0 = c := by simp
    change (n : ℕ∞) ≤ analyticOrderAt (f ∘ fun z : ℂ => c * z) 0
    rw [analyticOrderAt_comp_of_deriv_ne_zero ha (by rwa [hd]), mul_zero]
    exact hn

theorem analytic_order_mul_ge_left {f g : ℂ → ℂ}
    (hf : AnalyticAt ℂ f 0) (hg : AnalyticAt ℂ g 0)
    {n : ℕ} (hn : (n : ℕ∞) ≤ analyticOrderAt f 0) :
    (n : ℕ∞) ≤ analyticOrderAt (fun z => f z * g z) 0 := by
  change (n : ℕ∞) ≤ analyticOrderAt (f * g) 0
  rw [analyticOrderAt_mul hf hg]
  exact hn.trans le_self_add

theorem analytic_order_mul_ge_right {f g : ℂ → ℂ}
    (hf : AnalyticAt ℂ f 0) (hg : AnalyticAt ℂ g 0)
    {n : ℕ} (hn : (n : ℕ∞) ≤ analyticOrderAt g 0) :
    (n : ℕ∞) ≤ analyticOrderAt (fun z => f z * g z) 0 := by
  change (n : ℕ∞) ≤ analyticOrderAt (f * g) 0
  rw [analyticOrderAt_mul hf hg]
  exact hn.trans le_add_self

/-- The two product-difference terms preserve the common vanishing order. -/
theorem analytic_row_order_ge {h k u v : ℂ → ℂ}
    (hh : AnalyticAt ℂ h 0) (hk : AnalyticAt ℂ k 0)
    (hu : AnalyticAt ℂ u 0) (hv : AnalyticAt ℂ v 0)
    (hh0 : h 0 = 0) (hk0 : k 0 = 0) (x y : ℂ) {n : ℕ}
    (hn : (n : ℕ∞) ≤ analyticOrderAt h 0)
    (kn : (n : ℕ∞) ≤ analyticOrderAt k 0) :
    (n : ℕ∞) ≤ analyticOrderAt
      (fun z => h (x * z) * v (y * z) + u (x * z) * k (y * z)) 0 := by
  have hleft := analytic_order_mul_ge_left (analytic_scale_at_zero hh x)
    (analytic_scale_at_zero hv y) (analytic_order_scale_ge hh hh0 x hn)
  have hright := analytic_order_mul_ge_right (analytic_scale_at_zero hu x)
    (analytic_scale_at_zero hk y) (analytic_order_scale_ge hk hk0 y kn)
  exact (le_min hleft hright).trans le_analyticOrderAt_add

/-- Local equations determine the derivative of a difference in a neighborhood. -/
theorem derivative_difference_germ {e E f g F G : ℂ → ℂ}
    (he : AnalyticAt ℂ e 0) (hE : AnalyticAt ℂ E 0) (x y : ℂ)
    (heq : ∀ᶠ z in 𝓝 (0 : ℂ), deriv e z = 1 + f (x * z) * g (y * z))
    (hEq : ∀ᶠ z in 𝓝 (0 : ℂ), deriv E z = 1 + F (x * z) * G (y * z)) :
    deriv (fun z => e z - E z) =ᶠ[𝓝 (0 : ℂ)]
      (fun z => (f (x * z) - F (x * z)) * g (y * z) +
        F (x * z) * (g (y * z) - G (y * z))) := by
  filter_upwards [heq, hEq, he.eventually_analyticAt, hE.eventually_analyticAt] with z hz hZ hez hEz
  rw [deriv_fun_sub hez.differentiableAt hEz.differentiableAt, hz, hZ]
  ring

/-- The paired differential equations hold as identities of germs at zero. -/
def GermEquations (s : Scales) (f g : ℂ → ℂ) : Prop :=
  ∀ᶠ z in 𝓝 (0 : ℂ),
    deriv f z = 1 + f ((s.q : ℂ) * z) * g ((s.r : ℂ) * z) ∧
    deriv g z = 1 + f ((s.a : ℂ) * z) * g ((s.b : ℂ) * z)

/-- Conditional uniqueness of analytic germs, without positivity, contraction,
parity, or a recurrence hypothesis on the competing functions. -/
theorem analytic_pair_germ_unique (s : Scales) {f g F G : ℂ → ℂ}
    (hf : AnalyticAt ℂ f 0) (hg : AnalyticAt ℂ g 0)
    (hF : AnalyticAt ℂ F 0) (hG : AnalyticAt ℂ G 0)
    (hinit : f 0 = F 0 ∧ g 0 = G 0)
    (heq : s.GermEquations f g) (hEq : s.GermEquations F G) :
    f =ᶠ[𝓝 (0 : ℂ)] F ∧ g =ᶠ[𝓝 (0 : ℂ)] G := by
  have hh : AnalyticAt ℂ (fun z => f z - F z) 0 := hf.sub hF
  have hk : AnalyticAt ℂ (fun z => g z - G z) 0 := hg.sub hG
  have hh0 : f 0 - F 0 = 0 := sub_eq_zero.mpr hinit.1
  have hk0 : g 0 - G 0 = 0 := sub_eq_zero.mpr hinit.2
  have hdf := derivative_difference_germ (f := f) (g := g) (F := F) (G := G)
    hf hF (s.q : ℂ) (s.r : ℂ)
    (heq.mono (fun _ h => h.1)) (hEq.mono (fun _ h => h.1))
  have hdg := derivative_difference_germ (f := f) (g := g) (F := F) (G := G)
    hg hG (s.a : ℂ) (s.b : ℂ)
    (heq.mono (fun _ h => h.2)) (hEq.mono (fun _ h => h.2))
  have horders (n : ℕ) :
      (n : ℕ∞) ≤ analyticOrderAt (fun z => f z - F z) 0 ∧
      (n : ℕ∞) ≤ analyticOrderAt (fun z => g z - G z) 0 := by
    induction n with
    | zero => exact ⟨bot_le, bot_le⟩
    | succ n ih =>
      have hrow1 := analytic_row_order_ge hh hk hF hg hh0 hk0
        (s.q : ℂ) (s.r : ℂ) ih.1 ih.2
      have hrow2 := analytic_row_order_ge hh hk hF hg hh0 hk0
        (s.a : ℂ) (s.b : ℂ) ih.1 ih.2
      rw [← analyticOrderAt_congr hdf] at hrow1
      rw [← analyticOrderAt_congr hdg] at hrow2
      constructor
      · simpa only [Nat.cast_succ, Nat.cast_add, Nat.cast_one] using
          (analyticOrderAt_deriv_ge_iff hh hh0).mp hrow1
      · simpa only [Nat.cast_succ, Nat.cast_add, Nat.cast_one] using
          (analyticOrderAt_deriv_ge_iff hk hk0).mp hrow2
  have htop1 := ENat.eq_top_iff_forall_ge.mpr (fun n => (horders n).1)
  have htop2 := ENat.eq_top_iff_forall_ge.mpr (fun n => (horders n).2)
  exact ⟨(analyticOrderAt_eq_top.mp htop1).mono (fun _ h => sub_eq_zero.mp h),
    (analyticOrderAt_eq_top.mp htop2).mono (fun _ h => sub_eq_zero.mp h)⟩

/-- A normalized entire solution uses actual derivatives at every point. -/
def IsEntireSolution (s : Scales) (f g : ℂ → ℂ) : Prop :=
  f 0 = 0 ∧ g 0 = 0 ∧ ∀ z : ℂ,
    HasDerivAt f (1 + f ((s.q : ℂ) * z) * g ((s.r : ℂ) * z)) z ∧
    HasDerivAt g (1 + f ((s.a : ℂ) * z) * g ((s.b : ℂ) * z)) z

theorem entire_solution_differentiable {s : Scales} {f g : ℂ → ℂ}
    (hsol : s.IsEntireSolution f g) : Differentiable ℂ f ∧ Differentiable ℂ g :=
  ⟨fun z => (hsol.2.2 z).1.differentiableAt, fun z => (hsol.2.2 z).2.differentiableAt⟩

/-- Identity of germs extends to the whole plane for entire solution pairs. -/
theorem entire_solution_unique (s : Scales) {f g F G : ℂ → ℂ}
    (hsol : s.IsEntireSolution f g) (hSol : s.IsEntireSolution F G) : f = F ∧ g = G := by
  have hd := entire_solution_differentiable hsol
  have hD := entire_solution_differentiable hSol
  have heq : s.GermEquations f g := .of_forall (fun z =>
    ⟨(hsol.2.2 z).1.deriv, (hsol.2.2 z).2.deriv⟩)
  have hEq : s.GermEquations F G := .of_forall (fun z =>
    ⟨(hSol.2.2 z).1.deriv, (hSol.2.2 z).2.deriv⟩)
  have he := s.analytic_pair_germ_unique (hd.1.analyticAt 0) (hd.2.analyticAt 0)
    (hD.1.analyticAt 0) (hD.2.analyticAt 0)
    ⟨hsol.1.trans hSol.1.symm, hsol.2.1.trans hSol.2.1.symm⟩ heq hEq
  have hfA : AnalyticOnNhd ℂ f Set.univ := fun z _ => hd.1.analyticAt z
  have hgA : AnalyticOnNhd ℂ g Set.univ := fun z _ => hd.2.analyticAt z
  have hFA : AnalyticOnNhd ℂ F Set.univ := fun z _ => hD.1.analyticAt z
  have hGA : AnalyticOnNhd ℂ G Set.univ := fun z _ => hD.2.analyticAt z
  exact ⟨hfA.eq_of_eventuallyEq hFA he.1, hgA.eq_of_eventuallyEq hGA he.2⟩

theorem entire_solution_eq (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {f g : ℂ → ℂ} (hsol : s.IsEntireSolution f g) : f = s.U ∧ g = s.V :=
  s.entire_solution_unique hsol (s.coupled_entire_solution hs hstrict)

theorem coupled_entire_exists_unique (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    ∃! pair : (ℂ → ℂ) × (ℂ → ℂ), s.IsEntireSolution pair.1 pair.2 := by
  refine ⟨(s.U, s.V), s.coupled_entire_solution hs hstrict, ?_⟩
  intro pair hp
  have he := s.entire_solution_eq hs hstrict hp
  exact Prod.ext he.1 he.2

/-- An arbitrary normalized analytic solution germ is the canonical germ;
neither oddness nor any coefficient formula is assumed of it. -/
theorem analytic_solution_germ_eq (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {f g : ℂ → ℂ} (hf : AnalyticAt ℂ f 0) (hg : AnalyticAt ℂ g 0)
    (hzero : f 0 = 0 ∧ g 0 = 0) (heq : s.GermEquations f g) :
    f =ᶠ[𝓝 (0 : ℂ)] s.U ∧ g =ᶠ[𝓝 (0 : ℂ)] s.V := by
  have hd := s.coupled_entire hs hstrict
  have hcanonical := s.coupled_entire_solution hs hstrict
  exact s.analytic_pair_germ_unique hf hg (hd.1.analyticAt 0) (hd.2.analyticAt 0)
    ⟨hzero.1.trans hcanonical.1.symm, hzero.2.trans hcanonical.2.1.symm⟩ heq
    (.of_forall (fun z => s.coupled_entire_equations hs hstrict z))

/-- Reverse analytic-to-series bridge in the manuscript's ordinary odd-series
normalization. The coefficients are the already proved unique recurrence. -/
theorem analytic_solution_hasSum (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {f g : ℂ → ℂ} (hf : AnalyticAt ℂ f 0) (hg : AnalyticAt ℂ g 0)
    (hzero : f 0 = 0 ∧ g 0 = 0) (heq : s.GermEquations f g) :
    ∀ᶠ z in 𝓝 (0 : ℂ),
      HasSum (fun n => ((s.coefficients n).1 : ℂ) * z ^ (2 * n + 1)) (f z) ∧
      HasSum (fun n => ((s.coefficients n).2 : ℂ) * z ^ (2 * n + 1)) (g z) := by
  have he := s.analytic_solution_germ_eq hs hstrict hf hg hzero heq
  filter_upwards [he.1, he.2] with z hz hZ
  rw [hz, hZ]
  exact ⟨(s.coefficient_series_entire hs hstrict z).1.of_norm.hasSum,
    (s.coefficient_series_entire hs hstrict z).2.of_norm.hasSum⟩

theorem entire_solution_hasSum (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {f g : ℂ → ℂ} (hsol : s.IsEntireSolution f g) (z : ℂ) :
    HasSum (fun n => ((s.coefficients n).1 : ℂ) * z ^ (2 * n + 1)) (f z) ∧
    HasSum (fun n => ((s.coefficients n).2 : ℂ) * z ^ (2 * n + 1)) (g z) := by
  have he := s.entire_solution_eq hs hstrict hsol
  rw [he.1, he.2]
  exact ⟨(s.coefficient_series_entire hs hstrict z).1.of_norm.hasSum,
    (s.coefficient_series_entire hs hstrict z).2.of_norm.hasSum⟩

theorem entire_solution_odd (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1)
    {f g : ℂ → ℂ} (hsol : s.IsEntireSolution f g) (z : ℂ) :
    f (-z) = -f z ∧ g (-z) = -g z := by
  have he := s.entire_solution_eq hs hstrict hsol
  rw [he.1, he.2]
  exact s.coupled_odd z

/-- Appendix F.1 in the ordinary-series formulation used by the manuscript:
unique normalized entire pair, its canonical recurrence and positive coefficients,
its convergent odd expansions, and oddness of the constructed pair. -/
theorem coupled_F1_contract (s : Scales) (hs : s.positive)
    (hstrict : s.q < 1 ∧ s.r < 1 ∧ s.a < 1 ∧ s.b < 1) :
    (∃! pair : (ℂ → ℂ) × (ℂ → ℂ), s.IsEntireSolution pair.1 pair.2) ∧
    s.IsCoefficientSolution s.coefficients ∧
    (∀ n, 0 < (s.coefficients n).1 ∧ 0 < (s.coefficients n).2) ∧
    (∀ z : ℂ,
      HasSum (fun n => ((s.coefficients n).1 : ℂ) * z ^ (2 * n + 1)) (s.U z) ∧
      HasSum (fun n => ((s.coefficients n).2 : ℂ) * z ^ (2 * n + 1)) (s.V z)) ∧
    (∀ z : ℂ, s.U (-z) = -s.U z ∧ s.V (-z) = -s.V z) := by
  refine ⟨s.coupled_entire_exists_unique hs hstrict, s.coefficients_solution,
    s.coefficients_positive hs, ?_, s.coupled_odd⟩
  intro z
  exact ⟨(s.coefficient_series_entire hs hstrict z).1.of_norm.hasSum,
    (s.coefficient_series_entire hs hstrict z).2.of_norm.hasSum⟩

end Komorebi.SpecialFunctions.Coupled.Scales
