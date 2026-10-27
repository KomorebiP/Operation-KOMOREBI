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
@[expose] public section

noncomputable section
set_option autoImplicit false

namespace Komorebi.AbstractProjectorRefinement

open scoped BigOperators

universe uV uC uF
variable {V : Type uV} [NormedAddCommGroup V] [NormedSpace ℝ V]
variable {coarseLane : Type uC} {fineLane : Type uF}
variable [Fintype coarseLane] [Fintype fineLane] [DecidableEq coarseLane]

structure ProjectorFamily (V : Type uV) (lane : Type*)
    [NormedAddCommGroup V] [NormedSpace ℝ V] [Fintype lane] where
  proj : lane → V →L[ℝ] V
  idempotent : ∀ i x, proj i (proj i x) = proj i x
  orthogonal : ∀ {i j}, i ≠ j → ∀ x, proj i (proj j x) = 0
  complete : ∀ x, (∑ i, proj i x) = x

/-- Exact refinement of a coarse projector resolution by a fine one. -/
structure Refines
    (C : ProjectorFamily V coarseLane)
    (F : ProjectorFamily V fineLane)
    (ρ : fineLane → coarseLane) : Prop where
  coarse_eq_fine_sum : ∀ a,
    C.proj a = ∑ c ∈ Finset.univ.filter (fun c => ρ c = a), F.proj c

namespace Refines

/-- A fine descendant is unchanged after first projecting to its coarse ancestor. -/
theorem fine_comp_coarse_eq_fine
    (C : ProjectorFamily V coarseLane)
    (F : ProjectorFamily V fineLane)
    (ρ : fineLane → coarseLane) (hR : Refines C F ρ)
    (c : fineLane) (a : coarseLane) (hc : ρ c = a) :
    (F.proj c).comp (C.proj a) = F.proj c := by
  ext x
  change F.proj c (C.proj a x) = F.proj c x
  have hca := congrArg (fun L : V →L[ℝ] V => L x)
    (Refines.coarse_eq_fine_sum hR a)
  simp only [sum_apply] at hca
  rw [hca, map_sum]
  classical
  rw [Finset.sum_eq_single c]
  · exact F.idempotent c x
  · intro d hd hdc
    have hcd : c ≠ d := Ne.symm hdc
    exact F.orthogonal hcd x
  · simp [hc]

/-- A fine descendant is unchanged when its coarse ancestor is applied after it. -/
theorem coarse_comp_fine_eq_fine
    (C : ProjectorFamily V coarseLane)
    (F : ProjectorFamily V fineLane)
    (ρ : fineLane → coarseLane) (hR : Refines C F ρ)
    (c : fineLane) (a : coarseLane) (hc : ρ c = a) :
    (C.proj a).comp (F.proj c) = F.proj c := by
  ext x
  change C.proj a (F.proj c x) = F.proj c x
  have hca := congrArg (fun L : V →L[ℝ] V => L (F.proj c x))
    (Refines.coarse_eq_fine_sum hR a)
  simp only [sum_apply] at hca
  rw [hca]
  classical
  rw [Finset.sum_eq_single c]
  · exact F.idempotent c x
  · intro d hd hdc
    exact F.orthogonal hdc x
  · simp [hc]

end Refines

/-- Source-target operator corner under one finite projector resolution. -/
def opBlock
    (P : ProjectorFamily V coarseLane)
    (T : V →L[ℝ] V) (a b : coarseLane) : V →L[ℝ] V :=
  (P.proj a).comp (T.comp (P.proj b))

/-- Sum of fine source-target corners descending from one coarse corner. -/
def descendantOpBlockSum
    (F : ProjectorFamily V fineLane)
    (ρ : fineLane → coarseLane)
    (T : V →L[ℝ] V) (a b : coarseLane) : V →L[ℝ] V :=
  ∑ c ∈ Finset.univ.filter (fun c => ρ c = a),
    ∑ d ∈ Finset.univ.filter (fun d => ρ d = b),
      (F.proj c).comp (T.comp (F.proj d))

/-- Exact coarse-to-fine operator block refinement. -/
theorem opBlock_refinement
    (C : ProjectorFamily V coarseLane)
    (F : ProjectorFamily V fineLane)
    (ρ : fineLane → coarseLane) (hR : Refines C F ρ)
    (T : V →L[ℝ] V) (a b : coarseLane) :
    opBlock C T a b = descendantOpBlockSum F ρ T a b := by
  ext x
  classical
  change C.proj a (T (C.proj b x)) = _
  have ha := congrArg (fun L : V →L[ℝ] V => L (T (C.proj b x)))
    (Refines.coarse_eq_fine_sum hR a)
  simp only [sum_apply] at ha
  rw [ha]
  have hb := congrArg (fun L : V →L[ℝ] V => L x)
    (Refines.coarse_eq_fine_sum hR b)
  simp only [sum_apply] at hb
  calc
    (∑ c ∈ Finset.univ.filter (fun c => ρ c = a), F.proj c (T (C.proj b x))) =
        ∑ c ∈ Finset.univ.filter (fun c => ρ c = a),
          F.proj c (T (∑ d ∈ Finset.univ.filter (fun d => ρ d = b), F.proj d x)) := by
      rw [hb]
    _ = ∑ c ∈ Finset.univ.filter (fun c => ρ c = a),
          ∑ d ∈ Finset.univ.filter (fun d => ρ d = b), F.proj c (T (F.proj d x)) := by
      apply Finset.sum_congr rfl
      intro c hc
      rw [map_sum, map_sum]
    _ = descendantOpBlockSum F ρ T a b x := by
      unfold descendantOpBlockSum
      simp only [sum_apply, ContinuousLinearMap.comp_apply]

/-- **Abstract orthogonal no-cancellation theorem.**
A coarse operator corner is zero iff every fine descendant corner is zero. -/
theorem opBlock_zero_iff_descendants_zero
    (C : ProjectorFamily V coarseLane)
    (F : ProjectorFamily V fineLane)
    (ρ : fineLane → coarseLane) (hR : Refines C F ρ)
    (T : V →L[ℝ] V) (a b : coarseLane) :
    opBlock C T a b = 0 ↔
      ∀ c d, ρ c = a → ρ d = b →
        (F.proj c).comp (T.comp (F.proj d)) = 0 := by
  constructor
  · intro hzero c d hc hd
    have hleft := Refines.fine_comp_coarse_eq_fine C F ρ hR c a hc
    have hright := Refines.coarse_comp_fine_eq_fine C F ρ hR d b hd
    ext x
    have hz := congrArg (fun L : V →L[ℝ] V => L (F.proj d x)) hzero
    change C.proj a (T (C.proj b (F.proj d x))) = 0 at hz
    have hrx := congrArg (fun L : V →L[ℝ] V => L x) hright
    change C.proj b (F.proj d x) = F.proj d x at hrx
    rw [hrx] at hz
    have hlx := congrArg (fun L : V →L[ℝ] V => L (T (F.proj d x))) hleft
    change F.proj c (C.proj a (T (F.proj d x))) = F.proj c (T (F.proj d x)) at hlx
    have hzmap := congrArg (fun y => F.proj c y) hz
    simp only [map_zero] at hzmap
    change F.proj c (T (F.proj d x)) = 0
    exact hlx.symm.trans hzmap
  · intro hdesc
    rw [opBlock_refinement C F ρ hR T a b]
    unfold descendantOpBlockSum
    apply Finset.sum_eq_zero
    intro c hc
    apply Finset.sum_eq_zero
    intro d hd
    have hca : ρ c = a := by simpa using hc
    have hdb : ρ d = b := by simpa using hd
    exact hdesc c d hca hdb

/-- Adaptive criterion for an arbitrary orthogonal projector refinement. -/
theorem opBlock_ne_zero_iff_exists_descendant_ne_zero
    (C : ProjectorFamily V coarseLane)
    (F : ProjectorFamily V fineLane)
    (ρ : fineLane → coarseLane) (hR : Refines C F ρ)
    (T : V →L[ℝ] V) (a b : coarseLane) :
    opBlock C T a b ≠ 0 ↔
      ∃ c d, ρ c = a ∧ ρ d = b ∧
        (F.proj c).comp (T.comp (F.proj d)) ≠ 0 := by
  constructor
  · intro hcoarse
    by_contra hnone
    push Not at hnone
    apply hcoarse
    exact (opBlock_zero_iff_descendants_zero C F ρ hR T a b).2
      (fun c d hc hd => hnone c d hc hd)
  · rintro ⟨c, d, hc, hd, hcd⟩ hzero
    have hall := (opBlock_zero_iff_descendants_zero C F ρ hR T a b).1 hzero
    exact hcd (hall c d hc hd)




/-! ## Minimal-hypothesis orthogonal refinement -/


end Komorebi.AbstractProjectorRefinement
