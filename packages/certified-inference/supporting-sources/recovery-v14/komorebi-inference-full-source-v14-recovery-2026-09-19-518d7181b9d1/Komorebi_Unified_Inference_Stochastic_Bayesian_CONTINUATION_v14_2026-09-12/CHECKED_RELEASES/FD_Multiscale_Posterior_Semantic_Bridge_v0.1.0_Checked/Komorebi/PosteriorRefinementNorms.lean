module
public import Mathlib.Analysis.Normed.Operator.Basic
public import Mathlib.Analysis.ODE.Gronwall
public import Mathlib.Analysis.Normed.Algebra.Exponential
public import Mathlib.Analysis.Normed.Operator.NormedSpace
public import Mathlib.MeasureTheory.Integral.IntervalIntegral.FundThmCalculus
public import Mathlib.Analysis.Calculus.Deriv.Mul
public import Mathlib.Tactic.FunProp
public import Mathlib.Algebra.BigOperators.Group.Finset.Basic
public import Mathlib.Analysis.InnerProductSpace.Adjoint
public import Mathlib.Tactic.Abel
public import Komorebi.PosteriorRefinementCore
@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.AbstractProjectorRefinement

open scoped BigOperators

universe uV uC uF
variable {V : Type uV} [NormedAddCommGroup V] [NormedSpace ℝ V]
variable {coarseLane : Type uC} {fineLane : Type uF}
variable [Fintype coarseLane] [Fintype fineLane] [DecidableEq coarseLane]

section MinimalOrthogonalRefinement

/-- A raw source-target corner for an arbitrary family of bounded maps. -/
def rawOpBlock
    (P : coarseLane → V →L[ℝ] V)
    (T : V →L[ℝ] V) (a b : coarseLane) : V →L[ℝ] V :=
  (P a).comp (T.comp (P b))

/-- Fine descendant corner sum under a raw refinement map. -/
def rawDescendantOpBlockSum
    (F : fineLane → V →L[ℝ] V)
    (ρ : fineLane → coarseLane)
    (T : V →L[ℝ] V) (a b : coarseLane) : V →L[ℝ] V :=
  ∑ c ∈ Finset.univ.filter (fun c => ρ c = a),
    ∑ d ∈ Finset.univ.filter (fun d => ρ d = b),
      (F c).comp (T.comp (F d))

omit [Fintype coarseLane] in
/-- **Minimal exact orthogonal refinement theorem.**
No completeness hypothesis is needed: exact coarse fiber sums alone give exact
operator-corner refinement. -/
theorem rawOpBlock_refinement
    (C : coarseLane → V →L[ℝ] V)
    (F : fineLane → V →L[ℝ] V)
    (ρ : fineLane → coarseLane)
    (hRef : ∀ a, C a = ∑ c ∈ Finset.univ.filter (fun c => ρ c = a), F c)
    (T : V →L[ℝ] V) (a b : coarseLane) :
    rawOpBlock C T a b = rawDescendantOpBlockSum F ρ T a b := by
  ext x
  classical
  change C a (T (C b x)) = _
  have ha := congrArg (fun L : V →L[ℝ] V => L (T (C b x))) (hRef a)
  simp only [sum_apply] at ha
  rw [ha]
  have hb := congrArg (fun L : V →L[ℝ] V => L x) (hRef b)
  simp only [sum_apply] at hb
  calc
    (∑ c ∈ Finset.univ.filter (fun c => ρ c = a), F c (T (C b x))) =
        ∑ c ∈ Finset.univ.filter (fun c => ρ c = a),
          F c (T (∑ d ∈ Finset.univ.filter (fun d => ρ d = b), F d x)) := by rw [hb]
    _ = ∑ c ∈ Finset.univ.filter (fun c => ρ c = a),
          ∑ d ∈ Finset.univ.filter (fun d => ρ d = b), F c (T (F d x)) := by
      apply Finset.sum_congr rfl
      intro c hc
      rw [map_sum, map_sum]
    _ = rawDescendantOpBlockSum F ρ T a b x := by
      unfold rawDescendantOpBlockSum
      simp only [sum_apply, ContinuousLinearMap.comp_apply]

omit [Fintype coarseLane] in
/-- Fine descendants are absorbed by their coarse ancestor using only fine
idempotence, fine orthogonality, and exact fiber-sum refinement. -/
theorem raw_fine_comp_coarse_eq_fine
    (C : coarseLane → V →L[ℝ] V)
    (F : fineLane → V →L[ℝ] V)
    (ρ : fineLane → coarseLane)
    (hIdem : ∀ c x, F c (F c x) = F c x)
    (hOrth : ∀ {c d}, c ≠ d → ∀ x, F c (F d x) = 0)
    (hRef : ∀ a, C a = ∑ c ∈ Finset.univ.filter (fun c => ρ c = a), F c)
    (c : fineLane) (a : coarseLane) (hc : ρ c = a) :
    (F c).comp (C a) = F c := by
  ext x
  change F c (C a x) = F c x
  have hca := congrArg (fun L : V →L[ℝ] V => L x) (hRef a)
  simp only [sum_apply] at hca
  rw [hca, map_sum]
  classical
  rw [Finset.sum_eq_single c]
  · exact hIdem c x
  · intro d hd hdc
    exact hOrth (Ne.symm hdc) x
  · simp [hc]

omit [Fintype coarseLane] in
/-- Right-side descendant absorption under the same minimal hypotheses. -/
theorem raw_coarse_comp_fine_eq_fine
    (C : coarseLane → V →L[ℝ] V)
    (F : fineLane → V →L[ℝ] V)
    (ρ : fineLane → coarseLane)
    (hIdem : ∀ c x, F c (F c x) = F c x)
    (hOrth : ∀ {c d}, c ≠ d → ∀ x, F c (F d x) = 0)
    (hRef : ∀ a, C a = ∑ c ∈ Finset.univ.filter (fun c => ρ c = a), F c)
    (c : fineLane) (a : coarseLane) (hc : ρ c = a) :
    (C a).comp (F c) = F c := by
  ext x
  change C a (F c x) = F c x
  have hca := congrArg (fun L : V →L[ℝ] V => L (F c x)) (hRef a)
  simp only [sum_apply] at hca
  rw [hca]
  classical
  rw [Finset.sum_eq_single c]
  · exact hIdem c x
  · intro d hd hdc
    exact hOrth hdc x
  · simp [hc]

omit [Fintype coarseLane] in
/-- **Minimal no-cancellation theorem.**
A zero coarse corner is equivalent to zero of every fine descendant corner.
Neither coarse completeness nor fine completeness is assumed. -/
theorem rawOpBlock_zero_iff_descendants_zero
    (C : coarseLane → V →L[ℝ] V)
    (F : fineLane → V →L[ℝ] V)
    (ρ : fineLane → coarseLane)
    (hIdem : ∀ c x, F c (F c x) = F c x)
    (hOrth : ∀ {c d}, c ≠ d → ∀ x, F c (F d x) = 0)
    (hRef : ∀ a, C a = ∑ c ∈ Finset.univ.filter (fun c => ρ c = a), F c)
    (T : V →L[ℝ] V) (a b : coarseLane) :
    rawOpBlock C T a b = 0 ↔
      ∀ c d, ρ c = a → ρ d = b → (F c).comp (T.comp (F d)) = 0 := by
  constructor
  · intro hzero c d hc hd
    have hleft := raw_fine_comp_coarse_eq_fine C F ρ hIdem hOrth hRef c a hc
    have hright := raw_coarse_comp_fine_eq_fine C F ρ hIdem hOrth hRef d b hd
    ext x
    have hz := congrArg (fun L : V →L[ℝ] V => L (F d x)) hzero
    change C a (T (C b (F d x))) = 0 at hz
    have hrx := congrArg (fun L : V →L[ℝ] V => L x) hright
    change C b (F d x) = F d x at hrx
    rw [hrx] at hz
    have hlx := congrArg (fun L : V →L[ℝ] V => L (T (F d x))) hleft
    change F c (C a (T (F d x))) = F c (T (F d x)) at hlx
    have hzmap := congrArg (fun y => F c y) hz
    simp only [map_zero] at hzmap
    change F c (T (F d x)) = 0
    exact hlx.symm.trans hzmap
  · intro hdesc
    rw [rawOpBlock_refinement C F ρ hRef T a b]
    unfold rawDescendantOpBlockSum
    apply Finset.sum_eq_zero
    intro c hc
    apply Finset.sum_eq_zero
    intro d hd
    exact hdesc c d (by simpa using hc) (by simpa using hd)

omit [Fintype coarseLane] in
/-- Minimal adaptive-refinement trigger. -/
theorem rawOpBlock_ne_zero_iff_exists_descendant_ne_zero
    (C : coarseLane → V →L[ℝ] V)
    (F : fineLane → V →L[ℝ] V)
    (ρ : fineLane → coarseLane)
    (hIdem : ∀ c x, F c (F c x) = F c x)
    (hOrth : ∀ {c d}, c ≠ d → ∀ x, F c (F d x) = 0)
    (hRef : ∀ a, C a = ∑ c ∈ Finset.univ.filter (fun c => ρ c = a), F c)
    (T : V →L[ℝ] V) (a b : coarseLane) :
    rawOpBlock C T a b ≠ 0 ↔
      ∃ c d, ρ c = a ∧ ρ d = b ∧ (F c).comp (T.comp (F d)) ≠ 0 := by
  constructor
  · intro hcoarse
    by_contra hnone
    push Not at hnone
    exact hcoarse ((rawOpBlock_zero_iff_descendants_zero C F ρ hIdem hOrth hRef T a b).2
      (fun c d hc hd => hnone c d hc hd))
  · rintro ⟨c,d,hc,hd,hcd⟩ hzero
    have hall := (rawOpBlock_zero_iff_descendants_zero C F ρ hIdem hOrth hRef T a b).1 hzero
    exact hcd (hall c d hc hd)


omit [Fintype coarseLane] in
/-- Quantitative refinement certificate: the norm of a coarse corner is bounded
by the total norm budget of all fine descendant corners. -/
theorem rawOpBlock_norm_le_descendant_norm_sum
    (C : coarseLane → V →L[ℝ] V)
    (F : fineLane → V →L[ℝ] V)
    (ρ : fineLane → coarseLane)
    (hRef : ∀ a, C a = ∑ c ∈ Finset.univ.filter (fun c => ρ c = a), F c)
    (T : V →L[ℝ] V) (a b : coarseLane) :
    ‖rawOpBlock C T a b‖ ≤
      ∑ c ∈ Finset.univ.filter (fun c => ρ c = a),
        ∑ d ∈ Finset.univ.filter (fun d => ρ d = b),
          ‖(F c).comp (T.comp (F d))‖ := by
  rw [rawOpBlock_refinement C F ρ hRef T a b]
  unfold rawDescendantOpBlockSum
  calc
    ‖∑ c ∈ Finset.univ.filter (fun c => ρ c = a),
        ∑ d ∈ Finset.univ.filter (fun d => ρ d = b),
          (F c).comp (T.comp (F d))‖ ≤
      ∑ c ∈ Finset.univ.filter (fun c => ρ c = a),
        ‖∑ d ∈ Finset.univ.filter (fun d => ρ d = b),
          (F c).comp (T.comp (F d))‖ :=
      norm_sum_le _ _
    _ ≤ ∑ c ∈ Finset.univ.filter (fun c => ρ c = a),
        ∑ d ∈ Finset.univ.filter (fun d => ρ d = b),
          ‖(F c).comp (T.comp (F d))‖ := by
      apply Finset.sum_le_sum
      intro c hc
      exact norm_sum_le _ _

end MinimalOrthogonalRefinement

section FiniteTimeMultiscale

open Set
open scoped InnerProduct

universe uT
variable {T : Type uT} [NormedAddCommGroup T] [InnerProductSpace ℝ T] [CompleteSpace T]
variable {cLane : Type uC} {fLane : Type uF}
variable [Fintype cLane] [Fintype fLane] [DecidableEq cLane]

/-- Total fine-descendant operator-norm budget below a coarse corner. -/
def descendantNormBudget
    (F : ProjectorFamily T fLane) (ρ : fLane → cLane)
    (R : T →L[ℝ] T) (a b : cLane) : ℝ :=
  ∑ c ∈ Finset.univ.filter (fun c => ρ c = a),
    ∑ d ∈ Finset.univ.filter (fun d => ρ d = b),
      ‖(F.proj c).comp (R.comp (F.proj d))‖


end FiniteTimeMultiscale
end Komorebi.AbstractProjectorRefinement
