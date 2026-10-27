import KomorebiSpace.Exactification
import KomorebiSpace.Correction
import Mathlib.Analysis.Normed.Operator.ContinuousLinearMap
import Mathlib.Analysis.Normed.Module.Basic

set_option autoImplicit false

/-!
# Exactification preserving mathematical meaning

A continuous linear residual d and a continuous linear semantic map p are kept
separate. Converging controlled corrections with p(fₙ)=p(f₀) yield an actual
x with d(x)=0 and p(x)=p(f₀), and annihilate the constrained obstruction class.
-/
universe u v w z
namespace KomorebiSpace
namespace LinearExactification
open Filter
open scoped Topology
variable {𝕜 : Type u} [NontriviallyNormedField 𝕜]
variable {E : Type v} {R : Type w} {S : Type z}
variable [NormedAddCommGroup E] [NormedSpace 𝕜 E] [CompleteSpace E]
variable [NormedAddCommGroup R] [NormedSpace 𝕜 R]
variable [NormedAddCommGroup S] [NormedSpace 𝕜 S]

/-- The abstract obstruction quotient instantiated by genuine continuous linear maps. -/
def problem (d : E →L[𝕜] R) (p : E →L[𝕜] S) : CorrectionProblem E R S :=
  ⟨d.toAddMonoidHom, p.toAddMonoidHom⟩

omit [CompleteSpace E] in
theorem semantic_limit (p : E →L[𝕜] S) (f : ℕ → E) {x : E}
    (hx : Tendsto f atTop (𝓝 x)) (hsem : ∀ n, p (f n) = p (f 0)) :
    p x = p (f 0) := by
  have hp : Tendsto (fun n => p (f n)) atTop (𝓝 (p x)) :=
    p.continuous.continuousAt.tendsto.comp hx
  have hs : Tendsto (fun n => p (f n)) atTop (𝓝 (p (f 0))) := by
    simpa only [hsem] using
      (tendsto_const_nhds : Tendsto (fun _ : ℕ => p (f 0)) atTop (𝓝 (p (f 0))))
  exact tendsto_nhds_unique hp hs

/-- Main realization theorem in the complete normed linear model. -/
theorem summable_semantic_exactification (d : E →L[𝕜] R) (p : E →L[𝕜] S)
    (f : ℕ → E) (b : ℕ → ℝ) (hb : Summable b)
    (hstep : ∀ n, dist (f n) (f (n+1)) ≤ b n)
    (hvanish : Tendsto (fun n => ‖d (f n)‖) atTop (𝓝 0))
    (hsem : ∀ n, p (f n) = p (f 0)) :
    ∃ x, Tendsto f atTop (𝓝 x) ∧ d x = 0 ∧ p x = p (f 0) ∧
      ∀ n, dist (f n) x ≤ ∑' k, b (n+k) := by
  obtain ⟨x, hx, hz, htail⟩ := Exactification.summable_exactification
    (fun y => ‖d y‖) (fun _ => norm_nonneg _) d.continuous.norm.lowerSemicontinuous
    f b hb hstep hvanish
  exact ⟨x, hx, norm_eq_zero.mp hz, semantic_limit p f hx hsem, htail⟩

theorem geometric_semantic_exactification (d : E →L[𝕜] R) (p : E →L[𝕜] S)
    (f : ℕ → E) (q C : ℝ) (hq₀ : 0 ≤ q) (hq₁ : q < 1) (hC : 0 ≤ C)
    (hdec : ∀ n, ‖d (f (n+1))‖ ≤ q * ‖d (f n)‖)
    (hstep : ∀ n, dist (f n) (f (n+1)) ≤ C * ‖d (f n)‖)
    (hsem : ∀ n, p (f n) = p (f 0)) :
    ∃ x, Tendsto f atTop (𝓝 x) ∧ d x = 0 ∧ p x = p (f 0) ∧
      ∀ n, dist (f n) x ≤ (C/(1-q)) * ‖d (f n)‖ := by
  obtain ⟨x, hx, hz, htail⟩ := Exactification.geometric_exactification
    (fun y => ‖d y‖) (fun _ => norm_nonneg _) d.continuous.norm.lowerSemicontinuous
    f q C hq₀ hq₁ hC hdec hstep
  exact ⟨x, hx, norm_eq_zero.mp hz, semantic_limit p f hx hsem, htail⟩

/-- Controlled semantic-preserving exactification forces the obstruction to vanish. -/
theorem controlled_obstruction_vanishes (d : E →L[𝕜] R) (p : E →L[𝕜] S)
    (f : ℕ → E) (b : ℕ → ℝ) (hb : Summable b)
    (hstep : ∀ n, dist (f n) (f (n+1)) ≤ b n)
    (hvanish : Tendsto (fun n => ‖d (f n)‖) atTop (𝓝 0))
    (hsem : ∀ n, p (f n) = p (f 0)) :
    (problem d p).obstruction (f 0) = 0 := by
  obtain ⟨x, _, hd, hp, _⟩ := summable_semantic_exactification d p f b hb hstep hvanish hsem
  exact ((problem d p).flatten_iff (f 0)).2 ⟨x, hd, hp⟩

end LinearExactification
end KomorebiSpace
