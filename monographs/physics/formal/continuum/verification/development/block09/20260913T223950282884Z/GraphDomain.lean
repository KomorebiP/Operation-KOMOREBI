module

public import Mathlib.Analysis.InnerProductSpace.LinearPMap
public import Mathlib.Analysis.Calculus.MeanValue
public import Mathlib.Tactic.Linarith

/-!
Chapter 6.1: the Hamiltonian is a genuinely partially defined linear map.
Its domain carries its ambient subspace norm by default. The graph norm below
is a separate, actual L2-product norm. No ambient boundedness is assumed.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace GraphDomain
open Filter
open scoped Topology

variable {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable (T : H →ₗ.[ℂ] H)

/-- Actual graph embedding, not an assumed norm equivalence. -/
def graphMap : T.domain →ₗ[ℂ] WithLp 2 (H × H) :=
  (WithLp.linearEquiv 2 ℂ (H × H)).symm.toLinearMap.comp
    (T.domain.subtype.prod T.toFun)

/-- Source graph norm (6.2), implemented by the Hilbert L2-product norm. -/
def graphNorm (x : T.domain) : ℝ := ‖graphMap T x‖

theorem graphMap_fst (x : T.domain) : (graphMap T x).fst = (x : H) := rfl

theorem graphMap_snd (x : T.domain) : (graphMap T x).snd = T x := rfl

theorem graphMap_injective : Function.Injective (graphMap T) := by
  intro x y h
  apply Subtype.ext
  exact congrArg WithLp.fst h

/-- The literal squared graph norm, not the sup-product norm. -/
theorem graphNorm_sq (x : T.domain) :
    graphNorm T x ^ 2 = ‖(x : H)‖ ^ 2 + ‖T x‖ ^ 2 :=
  WithLp.prod_norm_sq_eq_of_L2 _

theorem graphNorm_nonneg (x : T.domain) : 0 ≤ graphNorm T x := norm_nonneg _

theorem graphNorm_zero : graphNorm T 0 = 0 := by simp [graphNorm]

theorem graphNorm_eq_zero (x : T.domain) : graphNorm T x = 0 ↔ x = 0 := by
  rw [graphNorm, norm_eq_zero, ← (graphMap T).map_zero,
    (graphMap_injective T).eq_iff]

theorem graphNorm_add_le (x y : T.domain) :
    graphNorm T (x + y) ≤ graphNorm T x + graphNorm T y := by
  simpa only [graphNorm, map_add] using norm_add_le (graphMap T x) (graphMap T y)

theorem graphNorm_smul (c : ℂ) (x : T.domain) :
    graphNorm T (c • x) = ‖c‖ * graphNorm T x := by
  simp only [graphNorm, map_smul, norm_smul]

theorem graphNorm_neg (x : T.domain) : graphNorm T (-x) = graphNorm T x := by
  simp only [graphNorm, map_neg, norm_neg]

theorem norm_le_graphNorm (x : T.domain) : ‖(x : H)‖ ≤ graphNorm T x :=
  WithLp.norm_fst_le H H (graphMap T x)

theorem action_norm_le_graphNorm (x : T.domain) : ‖T x‖ ≤ graphNorm T x :=
  WithLp.norm_snd_le H H (graphMap T x)

/-- Graph convergence has both required components. No continuity of T is used. -/
theorem graph_convergence_iff {α : Type*} {l : Filter α}
    (u : α → T.domain) (x : T.domain) :
    Tendsto (fun a => graphNorm T (u a - x)) l (𝓝 0) ↔
      Tendsto (fun a => (u a : H)) l (𝓝 (x : H)) ∧
      Tendsto (fun a => T (u a)) l (𝓝 (T x)) := by
  have eqn : (fun a => graphNorm T (u a - x)) =
      (fun a => ‖graphMap T (u a) - graphMap T x‖) := by
    funext a
    simp only [graphNorm, map_sub]
  rw [eqn, ← tendsto_iff_norm_sub_tendsto_zero]
  constructor
  · intro h
    exact ⟨(WithLp.fstL 2 ℂ H H).continuous.tendsto _ |>.comp h,
      (WithLp.sndL 2 ℂ H H).continuous.tendsto _ |>.comp h⟩
  · rintro ⟨hu, hT⟩
    exact (WithLp.prod_continuous_toLp 2 H H).tendsto _ |>.comp
      (hu.prodMk_nhds hT)

/-- The source squared-error formulation is equivalent to graph-norm convergence. -/
theorem squared_graph_convergence_iff {α : Type*} {l : Filter α}
    (u : α → T.domain) (x : T.domain) :
    Tendsto (fun a => ‖(u a : H) - x‖ ^ 2 + ‖T (u a) - T x‖ ^ 2) l (𝓝 0) ↔
      Tendsto (fun a => graphNorm T (u a - x)) l (𝓝 0) := by
  have hn : ∀ a, ‖(u a : H) - x‖ ^ 2 + ‖T (u a) - T x‖ ^ 2 =
      graphNorm T (u a - x) ^ 2 := by
    intro a
    rw [graphNorm_sq, LinearPMap.map_sub]
    rfl
  simp_rw [hn]
  constructor
  · intro h
    have hh := Real.continuous_sqrt.continuousAt.tendsto.comp h
    simpa only [Function.comp_def, Real.sqrt_sq (graphNorm_nonneg T _),
      Real.sqrt_zero] using hh
  · intro h
    simpa only [zero_pow (by decide : 2 ≠ 0)] using h.pow 2

/-- Symmetry is weaker than self-adjointness. It is precisely what the current
identities use, and is not represented by an everywhere bounded operator. -/
def IsSymmetric : Prop := T.IsFormalAdjoint T

theorem symmetric_self_im_zero (hT : IsSymmetric T) (x : T.domain) :
    (inner ℂ (x : H) (T x)).im = 0 := by
  have h := hT x x
  have hc := inner_conj_symm (𝕜 := ℂ) (T x) (x : H)
  have hi := congrArg Complex.im hc
  rw [h] at hi
  simp only [Complex.conj_im] at hi
  linarith

/-- Bounded operators are included as a consistency case, not the definition
of every operator in the unbounded interface. -/
def ofBounded (A : H →L[ℂ] H) : H →ₗ.[ℂ] H where
  domain := ⊤
  toFun := A.toLinearMap.comp (⊤ : Submodule ℂ H).subtype

theorem ofBounded_apply (A : H →L[ℂ] H) (x : (ofBounded A).domain) :
    ofBounded A x = A x := rfl

end GraphDomain
end KomorebiPhysics
