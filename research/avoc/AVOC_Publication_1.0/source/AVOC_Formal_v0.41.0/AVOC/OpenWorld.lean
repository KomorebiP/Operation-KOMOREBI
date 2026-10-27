import AVOC.BayesianEvidence
import AVOC.ApproximateComposition
import Mathlib.Tactic.NormNum

namespace Komorebi.AVOC

universe u v w

/-- Push a certified finite rational belief through a deterministic representation. -/
def pushforwardBelief
    {Ω : Type u} {Z : Type v}
    [Fintype Ω] [Fintype Z] [DecidableEq Z]
    (φ : Ω → Z) (b : RationalBelief Ω) : RationalBelief Z where
  prob z := pushforwardRow φ b.prob z
  nonneg := by
    intro z
    unfold pushforwardRow
    exact Finset.sum_nonneg (fun _ _ => b.nonneg _)
  sum_one := by
    calc
      (∑ z : Z, pushforwardRow φ b.prob z)
          = ∑ ω : Ω, b.prob ω := by
              simpa using (sum_pushforward_mul φ b.prob (fun _ : Z => (1 : ℚ)))
      _ = 1 := b.sum_one

@[simp] theorem pushforwardBelief_prob
    {Ω : Type u} {Z : Type v}
    [Fintype Ω] [Fintype Z] [DecidableEq Z]
    (φ : Ω → Z) (b : RationalBelief Ω) (z : Z) :
    (pushforwardBelief φ b).prob z = pushforwardRow φ b.prob z := rfl

/-- Coarse mass is exactly the sum of the fine masses in the decoded fiber.
This is the mass-conservation law for hypothesis refinement. -/
theorem refinement_mass_conservation
    {Hfine : Type u} {Hcoarse : Type v}
    [Fintype Hfine] [Fintype Hcoarse] [DecidableEq Hcoarse]
    (decode : Hfine → Hcoarse) (b : RationalBelief Hfine) (h : Hcoarse) :
    (pushforwardBelief decode b).prob h =
      ∑ x ∈ Finset.univ.filter (fun x : Hfine => decode x = h), b.prob x := by
  rfl

/-- Pushing a belief through two deterministic representations is the same as
pushing it through their composite. -/
theorem pushforwardBelief_comp
    {Ω : Type u} {Y : Type v} {Z : Type w}
    [Fintype Ω] [Fintype Y] [Fintype Z]
    [DecidableEq Y] [DecidableEq Z]
    (φ : Ω → Y) (ψ : Y → Z) (b : RationalBelief Ω) :
    pushforwardBelief ψ (pushforwardBelief φ b) =
      pushforwardBelief (ψ ∘ φ) b := by
  apply RationalBelief.ext
  intro z
  exact pushforwardRow_comp φ ψ b.prob z

/-- A point mass at one world. -/
def diracBelief
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω]
    (x : Ω) : RationalBelief Ω where
  prob y := if y = x then 1 else 0
  nonneg := by
    intro y
    split <;> norm_num
  sum_one := by
    simp

@[simp] theorem diracBelief_self
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω] (x : Ω) :
    (diracBelief x).prob x = 1 := by
  simp [diracBelief]

@[simp] theorem diracBelief_other
    {Ω : Type u} [Fintype Ω] [DecidableEq Ω] {x y : Ω} (h : y ≠ x) :
    (diracBelief x).prob y = 0 := by
  simp [diracBelief, h]

/-- Deterministic pushforward maps a point mass to the point mass at its image. -/
theorem pushforward_dirac
    {Ω : Type u} {Z : Type v}
    [Fintype Ω] [Fintype Z] [DecidableEq Ω] [DecidableEq Z]
    (φ : Ω → Z) (x : Ω) :
    pushforwardBelief φ (diracBelief x) = diracBelief (φ x) := by
  classical
  apply RationalBelief.ext
  intro z
  change pushforwardRow φ (fun y => if y = x then (1 : ℚ) else 0) z =
    (if z = φ x then 1 else 0)
  simp [pushforwardRow, eq_comm]

/-- A task-relevant collision makes universal recovery of fine beliefs from the
coarse belief impossible. -/
theorem no_universal_belief_recovery_of_collision
    {Ω : Type u} {Z : Type v}
    [Fintype Ω] [Fintype Z] [DecidableEq Ω] [DecidableEq Z]
    (φ : Ω → Z) {x y : Ω} (hxy : x ≠ y) (hφ : φ x = φ y) :
    ¬ ∃ recover : RationalBelief Z → RationalBelief Ω,
        ∀ b : RationalBelief Ω, recover (pushforwardBelief φ b) = b := by
  rintro ⟨recover, hrecover⟩
  have hpush : pushforwardBelief φ (diracBelief x) =
      pushforwardBelief φ (diracBelief y) := by
    rw [pushforward_dirac, pushforward_dirac, hφ]
  have hfine : diracBelief x = diracBelief y := by
    calc
      diracBelief x = recover (pushforwardBelief φ (diracBelief x)) :=
        (hrecover (diracBelief x)).symm
      _ = recover (pushforwardBelief φ (diracBelief y)) := congrArg recover hpush
      _ = diracBelief y := hrecover (diracBelief y)
  have hp := congrArg (fun b : RationalBelief Ω => b.prob x) hfine
  have hyx : x ≠ y := hxy
  simp [diracBelief, hyx] at hp

/-- Universal preservation of all Boolean queries forces an encoding to be
injective.  Thus an archive intended to answer arbitrary future Boolean queries
admits no nontrivial exact compression. -/
theorem sufficient_for_all_bool_queries_implies_injective
    {X : Type u} {Z : Type v}
    (φ : X → Z)
    (h : ∀ q : X → Bool, TaskSufficient φ q) :
    Function.Injective φ := by
  classical
  intro x y hφ
  by_contra hxy
  let q : X → Bool := fun z => if z = x then true else false
  have hq := sufficient_preserves_target_distinctions (h q) hφ
  have hyx : y ≠ x := Ne.symm hxy
  simp [q, hyx] at hq

/-- Conversely, an injective encoding is sufficient for every Boolean query. -/
theorem injective_implies_sufficient_for_all_bool_queries
    {X : Type u} {Z : Type v}
    (φ : X → Z) (hinj : Function.Injective φ) :
    ∀ q : X → Bool, TaskSufficient φ q := by
  intro q
  apply fiber_refinement_implies_sufficient
  intro x y hxy
  exact congrArg q (hinj hxy)

/-- Exact universal-query characterization. -/
theorem sufficient_for_all_bool_queries_iff_injective
    {X : Type u} {Z : Type v}
    (φ : X → Z) :
    (∀ q : X → Bool, TaskSufficient φ q) ↔ Function.Injective φ := by
  constructor
  · exact sufficient_for_all_bool_queries_implies_injective φ
  · exact injective_implies_sufficient_for_all_bool_queries φ

end Komorebi.AVOC
