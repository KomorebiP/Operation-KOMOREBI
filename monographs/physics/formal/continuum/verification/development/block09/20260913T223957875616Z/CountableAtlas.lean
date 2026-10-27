module

public import KomorebiPhysics.GraphDomain
public import KomorebiPhysics.Transfer
public import Mathlib.Analysis.InnerProductSpace.l2Space

/-!
Strong orthogonal resolutions indexed by a possibly infinite type. All sums
are nets over finite subsets. Countable families are a specialization; no
finite-label instance or continuity of the unbounded generator is hidden.
-/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
open Filter
open scoped BigOperators Topology

/-- Strong completeness, projector laws, and Hermiticity only. -/
structure StrongAtlas (H I : Type*) [NormedAddCommGroup H] [InnerProductSpace ℂ H] where
  proj : I → (H →L[ℂ] H)
  idempotent : ∀ i x, proj i (proj i x) = proj i x
  orthogonal : ∀ i j, i ≠ j → ∀ x, proj i (proj j x) = 0
  selfAdjoint : ∀ i x y, inner ℂ (proj i x) y = inner ℂ x (proj i y)
  strong : ∀ x, HasSum (fun i => proj i x) x

namespace StrongAtlas
variable {H I : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable (P : StrongAtlas H I)

def partial (s : Finset I) (x : H) : H := ∑ i ∈ s, P.proj i x

def energy (x : H) (i : I) : ℝ := ‖P.proj i x‖ ^ 2

theorem partial_tendsto (x : H) : Tendsto (fun s => P.partial s x) atTop (𝓝 x) :=
  P.strong x

theorem projected_inner (x y : H) (i : I) :
    inner ℂ (P.proj i x) (P.proj i y) = inner ℂ (P.proj i x) y := by
  rw [← P.selfAdjoint, P.idempotent]

theorem packets_orthogonal (x y : H) (i j : I) (hij : i ≠ j) :
    inner ℂ (P.proj i x) (P.proj j y) = 0 := by
  rw [P.selfAdjoint, P.orthogonal i j hij, inner_zero_right]

theorem partial_inner (s : Finset I) (x y : H) :
    inner ℂ (P.partial s x) (P.partial s y) =
      ∑ i ∈ s, inner ℂ (P.proj i x) (P.proj i y) := by
  classical
  simp only [partial, sum_inner, inner_sum]
  apply Finset.sum_congr rfl
  intro i hi
  exact Finset.sum_eq_single i
    (fun j _ hji => P.packets_orthogonal x y i j (Ne.symm hji))
    (fun h => (h hi).elim)

/-- Finite Pythagoras precedes the infinite Parseval statement. -/
theorem partial_norm_sq (s : Finset I) (x : H) :
    ‖P.partial s x‖ ^ 2 = ∑ i ∈ s, P.energy x i := by
  have h := congrArg Complex.re (P.partial_inner s x x)
  simpa only [Complex.re_sum, inner_self_eq_norm_sq, energy] using h

/-- Infinite Parseval from actual strong convergence and continuity of norm. -/
theorem energy_hasSum (x : H) : HasSum (P.energy x) (‖x‖ ^ 2) := by
  have h := (P.partial_tendsto x).norm.pow 2
  simpa only [P.partial_norm_sq] using h

theorem energy_summable (x : H) : Summable (P.energy x) := (P.energy_hasSum x).summable

theorem energy_tsum (x : H) : (∑' i, P.energy x i) = ‖x‖ ^ 2 :=
  (P.energy_hasSum x).tsum_eq

theorem finite_energy_le (s : Finset I) (x : H) :
    (∑ i ∈ s, P.energy x i) ≤ ‖x‖ ^ 2 := by
  rw [← P.energy_tsum x]
  exact Summable.sum_le_tsum s (fun i _ => sq_nonneg _) (P.energy_summable x)

theorem partial_norm_le (s : Finset I) (x : H) : ‖P.partial s x‖ ≤ ‖x‖ := by
  have h := P.finite_energy_le s x
  rw [← P.partial_norm_sq] at h
  nlinarith [norm_nonneg (P.partial s x), norm_nonneg x]

/-- A finite atlas is a special case of a strong atlas. -/
def ofFinite [Fintype I] [DecidableEq I] (Q : Atlas H I) : StrongAtlas H I where
  proj := Q.proj
  idempotent i x := Q.proj_packet x i
  orthogonal i j hij x := by
    have h := congrArg (fun A : H →L[ℂ] H => A x) (Q.mul_proj i j)
    simpa [hij] using h
  selfAdjoint := Q.selfAdjoint
  strong x := by simpa only [Atlas.packet, Q.reconstruct_state] using hasSum_fintype (fun i => Q.proj i x)

end StrongAtlas

/-- Domain invariance is explicit and does not assert graph convergence. -/
structure DomainAtlas {H : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
    (T : H →ₗ.[ℂ] H) (I : Type*) where
  atlas : StrongAtlas H I
  preserves : ∀ (i : I) (x : T.domain), atlas.proj i x ∈ T.domain

namespace DomainAtlas
variable {H I : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable {T : H →ₗ.[ℂ] H} (P : DomainAtlas T I)

/-- The actual restricted projector, with its output's domain proof. -/
def project (i : I) : T.domain →ₗ[ℂ] T.domain where
  toFun x := ⟨P.atlas.proj i x, P.preserves i x⟩
  map_add' x y := Subtype.ext (map_add _ _ _)
  map_smul' c x := Subtype.ext (map_smul _ _ _)

def partial (s : Finset I) (x : T.domain) : T.domain := ∑ i ∈ s, P.project i x

theorem project_coe (i : I) (x : T.domain) :
    (P.project i x : H) = P.atlas.proj i x := rfl

theorem partial_coe (s : Finset I) (x : T.domain) :
    (P.partial s x : H) = P.atlas.partial s x := by
  simp only [partial, StrongAtlas.partial, Submodule.coe_sum, P.project_coe]

theorem action_partial (s : Finset I) (x : T.domain) :
    T (P.partial s x) = ∑ i ∈ s, T (P.project i x) := T.toFun.map_sum _ s

/-- Source graph compatibility, separate from strong completeness. -/
def GraphCompatible : Prop := ∀ x : T.domain,
  Tendsto (fun s => GraphDomain.graphNorm T (P.partial s x - x)) atTop (𝓝 0)

theorem graph_components (h : P.GraphCompatible) (x : T.domain) :
    Tendsto (fun s => (P.partial s x : H)) atTop (𝓝 (x : H)) ∧
    Tendsto (fun s => T (P.partial s x)) atTop (𝓝 (T x)) :=
  (GraphDomain.graph_convergence_iff T _ x).mp (h x)

theorem action_hasSum (h : P.GraphCompatible) (x : T.domain) :
    HasSum (fun i => T (P.project i x)) (T x) := by
  simpa only [P.action_partial] using (P.graph_components h x).2

theorem graph_iff_action : P.GraphCompatible ↔
    ∀ x : T.domain, HasSum (fun i => T (P.project i x)) (T x) := by
  constructor
  · exact P.action_hasSum
  · intro h x
    apply (GraphDomain.graph_convergence_iff T _ x).mpr
    constructor
    · simpa only [P.partial_coe] using P.atlas.partial_tendsto (x : H)
    · simpa only [P.action_partial] using h x

/-- Boundedness suffices for graph compatibility; it is not necessary and is
not imposed on the main countable/unbounded interface. -/
theorem graph_of_bounded_action (A : H →L[ℂ] H) (hA : ∀ x : T.domain, T x = A x) :
    P.GraphCompatible := by
  apply P.graph_iff_action.mpr
  intro x
  have h := (P.atlas.strong (x : H)).mapL A
  simpa only [hA, P.project_coe] using h

end DomainAtlas
end KomorebiPhysics
