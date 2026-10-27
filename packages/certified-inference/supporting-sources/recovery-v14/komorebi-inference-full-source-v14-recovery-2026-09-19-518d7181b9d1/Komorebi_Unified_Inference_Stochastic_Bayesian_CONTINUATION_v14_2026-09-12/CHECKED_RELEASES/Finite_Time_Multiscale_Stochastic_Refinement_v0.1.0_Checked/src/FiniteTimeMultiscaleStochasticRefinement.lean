module
public import Mathlib.Analysis.Normed.Operator.Basic
public import Mathlib.Analysis.ODE.Gronwall
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

/-! ## Hilbert-space stochastic covariance specialization -/

section StochasticHilbertRefinement

open scoped InnerProduct
set_option linter.unusedSectionVars false

universe uH
variable {H : Type uH} [NormedAddCommGroup H] [InnerProductSpace ℝ H] [CompleteSpace H]

/-- A bounded operator preserves every packet exactly when it commutes with all
packet projectors. -/
def CommutesWithProjectors
    (P : ProjectorFamily H coarseLane) (T : H →L[ℝ] H) : Prop :=
  ∀ a, (P.proj a).comp T = T.comp (P.proj a)

/-- Commutation with a projector family forces every off-diagonal operator
corner to vanish. -/
theorem opBlock_eq_zero_of_commutes
    (P : ProjectorFamily H coarseLane) (T : H →L[ℝ] H)
    (hT : CommutesWithProjectors P T)
    {a b : coarseLane} (hab : a ≠ b) :
    opBlock P T a b = 0 := by
  ext x
  change P.proj a (T (P.proj b x)) = 0
  have hcomm := congrArg (fun L : H →L[ℝ] H => L (P.proj b x)) (hT a)
  change P.proj a (T (P.proj b x)) = T (P.proj a (P.proj b x)) at hcomm
  rw [hcomm, P.orthogonal hab]
  exact map_zero T

/-- Projector commutation is closed under operator addition. -/
theorem CommutesWithProjectors.add
    (P : ProjectorFamily H coarseLane) {S T : H →L[ℝ] H}
    (hS : CommutesWithProjectors P S)
    (hT : CommutesWithProjectors P T) :
    CommutesWithProjectors P (S + T) := by
  intro a
  ext x
  have hs := congrArg (fun L : H →L[ℝ] H => L x) (hS a)
  have ht := congrArg (fun L : H →L[ℝ] H => L x) (hT a)
  change P.proj a (S x) = S (P.proj a x) at hs
  change P.proj a (T x) = T (P.proj a x) at ht
  change P.proj a (S x + T x) = S (P.proj a x) + T (P.proj a x)
  rw [map_add, hs, ht]

/-- Projector commutation is closed under composition. -/
theorem CommutesWithProjectors.comp
    (P : ProjectorFamily H coarseLane) {S T : H →L[ℝ] H}
    (hS : CommutesWithProjectors P S)
    (hT : CommutesWithProjectors P T) :
    CommutesWithProjectors P (S.comp T) := by
  intro a
  ext x
  have hs := congrArg (fun L : H →L[ℝ] H => L (T x)) (hS a)
  have ht := congrArg (fun L : H →L[ℝ] H => L x) (hT a)
  change P.proj a (S (T x)) = S (P.proj a (T x)) at hs
  change P.proj a (T x) = T (P.proj a x) at ht
  change P.proj a (S (T x)) = S (T (P.proj a x))
  calc
    P.proj a (S (T x)) = S (P.proj a (T x)) := hs
    _ = S (T (P.proj a x)) := congrArg S ht

/-- For self-adjoint packet projectors, exact packet preservation is inherited
by adjoints. -/
theorem CommutesWithProjectors.adjoint
    (P : ProjectorFamily H coarseLane)
    (hSelf : ∀ a, (P.proj a).adjoint = P.proj a)
    {T : H →L[ℝ] H} (hT : CommutesWithProjectors P T) :
    CommutesWithProjectors P T.adjoint := by
  intro a
  have h := congrArg (fun L : H →L[ℝ] H => L.adjoint) (hT a)
  rw [ContinuousLinearMap.adjoint_comp, ContinuousLinearMap.adjoint_comp,
    hSelf a] at h
  exact h.symm

/-- Hilbert-space covariance/Lyapunov forcing. -/
def covarianceForcingOp
    (A P Q : H →L[ℝ] H) : H →L[ℝ] H :=
  A.comp P + P.comp A.adjoint + Q

/-- Exact residual split of the covariance forcing. -/
theorem covarianceForcingOp_residual_split
    (A0 RA P Q0 RQ : H →L[ℝ] H) :
    covarianceForcingOp (A0 + RA) P (Q0 + RQ) =
      covarianceForcingOp A0 P Q0 + covarianceForcingOp RA P RQ := by
  ext x
  simp only [covarianceForcingOp, ContinuousLinearMap.comp_apply, add_apply, map_add]
  abel

/-- An exactly packet-preserving baseline has packet-preserving Lyapunov
forcing. -/
theorem covarianceForcingOp_commutes
    (C : ProjectorFamily H coarseLane)
    (hSelf : ∀ a, (C.proj a).adjoint = C.proj a)
    (A0 P Q0 : H →L[ℝ] H)
    (hA0 : CommutesWithProjectors C A0)
    (hP : CommutesWithProjectors C P)
    (hQ0 : CommutesWithProjectors C Q0) :
    CommutesWithProjectors C (covarianceForcingOp A0 P Q0) := by
  have hAadj := CommutesWithProjectors.adjoint C hSelf hA0
  have hAP := CommutesWithProjectors.comp C hA0 hP
  have hPA := CommutesWithProjectors.comp C hP hAadj
  exact (hAP.add C hPA).add C hQ0

/-- Off a coarse packet diagonal, the full perturbed covariance forcing is
exactly the named residual forcing. -/
theorem offcoarse_covarianceForcing_eq_residual
    (C : ProjectorFamily H coarseLane)
    (hSelf : ∀ a, (C.proj a).adjoint = C.proj a)
    (A0 RA P Q0 RQ : H →L[ℝ] H)
    (hA0 : CommutesWithProjectors C A0)
    (hP : CommutesWithProjectors C P)
    (hQ0 : CommutesWithProjectors C Q0)
    {a b : coarseLane} (hab : a ≠ b) :
    opBlock C (covarianceForcingOp (A0 + RA) P (Q0 + RQ)) a b =
      opBlock C (covarianceForcingOp RA P RQ) a b := by
  rw [covarianceForcingOp_residual_split]
  have hbase := covarianceForcingOp_commutes C hSelf A0 P Q0 hA0 hP hQ0
  have hz := opBlock_eq_zero_of_commutes C (covarianceForcingOp A0 P Q0) hbase hab
  ext x
  have hzx := congrArg (fun L : H →L[ℝ] H => L x) hz
  change C.proj a (covarianceForcingOp A0 P Q0 (C.proj b x)) = 0 at hzx
  change C.proj a
      ((covarianceForcingOp A0 P Q0 + covarianceForcingOp RA P RQ) (C.proj b x)) =
    C.proj a (covarianceForcingOp RA P RQ (C.proj b x))
  rw [add_apply, map_add, hzx, zero_add]

/-- **Abstract stochastic projector-refinement theorem.**
For distinct coarse packets, the entire perturbed Lyapunov forcing corner is
exactly the sum of fine descendants of the named covariance residual forcing. -/
theorem offcoarse_covarianceForcing_refines_to_residual_descendants
    (C : ProjectorFamily H coarseLane)
    (F : ProjectorFamily H fineLane)
    (ρ : fineLane → coarseLane) (hR : Refines C F ρ)
    (hSelf : ∀ a, (C.proj a).adjoint = C.proj a)
    (A0 RA P Q0 RQ : H →L[ℝ] H)
    (hA0 : CommutesWithProjectors C A0)
    (hP : CommutesWithProjectors C P)
    (hQ0 : CommutesWithProjectors C Q0)
    {a b : coarseLane} (hab : a ≠ b) :
    opBlock C (covarianceForcingOp (A0 + RA) P (Q0 + RQ)) a b =
      descendantOpBlockSum F ρ (covarianceForcingOp RA P RQ) a b := by
  rw [offcoarse_covarianceForcing_eq_residual C hSelf A0 RA P Q0 RQ hA0 hP hQ0 hab]
  exact opBlock_refinement C F ρ hR (covarianceForcingOp RA P RQ) a b


/-- Quantitative abstract stochastic refinement certificate: the norm of an
off-coarse covariance-forcing corner is bounded by the total fine residual
corner budget below it. -/
theorem offcoarse_covarianceForcing_norm_le_descendant_budget
    (C : ProjectorFamily H coarseLane)
    (F : ProjectorFamily H fineLane)
    (ρ : fineLane → coarseLane) (hR : Refines C F ρ)
    (hSelf : ∀ a, (C.proj a).adjoint = C.proj a)
    (A0 RA P Q0 RQ : H →L[ℝ] H)
    (hA0 : CommutesWithProjectors C A0)
    (hP : CommutesWithProjectors C P)
    (hQ0 : CommutesWithProjectors C Q0)
    {a b : coarseLane} (hab : a ≠ b) :
    ‖opBlock C (covarianceForcingOp (A0 + RA) P (Q0 + RQ)) a b‖ ≤
      ∑ c ∈ Finset.univ.filter (fun c => ρ c = a),
        ∑ d ∈ Finset.univ.filter (fun d => ρ d = b),
          ‖(F.proj c).comp ((covarianceForcingOp RA P RQ).comp (F.proj d))‖ := by
  rw [offcoarse_covarianceForcing_eq_residual C hSelf A0 RA P Q0 RQ hA0 hP hQ0 hab]
  change ‖rawOpBlock C.proj (covarianceForcingOp RA P RQ) a b‖ ≤ _
  exact rawOpBlock_norm_le_descendant_norm_sum C.proj F.proj ρ
    (Refines.coarse_eq_fine_sum hR) (covarianceForcingOp RA P RQ) a b

/-- Abstract stochastic no-cancellation criterion under orthogonal refinement. -/
theorem offcoarse_covarianceForcing_zero_iff_descendants_zero
    (C : ProjectorFamily H coarseLane)
    (F : ProjectorFamily H fineLane)
    (ρ : fineLane → coarseLane) (hR : Refines C F ρ)
    (hSelf : ∀ a, (C.proj a).adjoint = C.proj a)
    (A0 RA P Q0 RQ : H →L[ℝ] H)
    (hA0 : CommutesWithProjectors C A0)
    (hP : CommutesWithProjectors C P)
    (hQ0 : CommutesWithProjectors C Q0)
    {a b : coarseLane} (hab : a ≠ b) :
    opBlock C (covarianceForcingOp (A0 + RA) P (Q0 + RQ)) a b = 0 ↔
      ∀ c d, ρ c = a → ρ d = b →
        (F.proj c).comp
          ((covarianceForcingOp RA P RQ).comp (F.proj d)) = 0 := by
  rw [offcoarse_covarianceForcing_eq_residual C hSelf A0 RA P Q0 RQ hA0 hP hQ0 hab]
  exact opBlock_zero_iff_descendants_zero C F ρ hR
    (covarianceForcingOp RA P RQ) a b

/-- Abstract adaptive stochastic refinement trigger. -/
theorem offcoarse_covarianceForcing_ne_zero_iff_exists_descendant
    (C : ProjectorFamily H coarseLane)
    (F : ProjectorFamily H fineLane)
    (ρ : fineLane → coarseLane) (hR : Refines C F ρ)
    (hSelf : ∀ a, (C.proj a).adjoint = C.proj a)
    (A0 RA P Q0 RQ : H →L[ℝ] H)
    (hA0 : CommutesWithProjectors C A0)
    (hP : CommutesWithProjectors C P)
    (hQ0 : CommutesWithProjectors C Q0)
    {a b : coarseLane} (hab : a ≠ b) :
    opBlock C (covarianceForcingOp (A0 + RA) P (Q0 + RQ)) a b ≠ 0 ↔
      ∃ c d, ρ c = a ∧ ρ d = b ∧
        (F.proj c).comp
          ((covarianceForcingOp RA P RQ).comp (F.proj d)) ≠ 0 := by
  rw [offcoarse_covarianceForcing_eq_residual C hSelf A0 RA P Q0 RQ hA0 hP hQ0 hab]
  exact opBlock_ne_zero_iff_exists_descendant_ne_zero C F ρ hR
    (covarianceForcingOp RA P RQ) a b

end StochasticHilbertRefinement


/-! ## Finite-time multiscale covariance leakage -/

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

omit [CompleteSpace T] [DecidableEq cLane] in
/-- Left multiplication by an exactly packet-preserving operator acts inside
one coarse operator corner. -/
theorem opBlock_comp_left_of_commutes
    (C : ProjectorFamily T cLane) (A D : T →L[ℝ] T)
    (hA : CommutesWithProjectors C A) (a b : cLane) :
    opBlock C (A.comp D) a b = A.comp (opBlock C D a b) := by
  ext x
  have h := congrArg (fun L : T →L[ℝ] T => L (D (C.proj b x))) (hA a)
  change C.proj a (A (D (C.proj b x))) = A (C.proj a (D (C.proj b x))) at h
  exact h

omit [CompleteSpace T] [DecidableEq cLane] in
/-- Operator corners are additive in the transported operator. -/
theorem opBlock_add
    (C : ProjectorFamily T cLane) (S D : T →L[ℝ] T) (a b : cLane) :
    opBlock C (S + D) a b = opBlock C S a b + opBlock C D a b := by
  ext x
  simp only [opBlock, ContinuousLinearMap.comp_apply, add_apply, map_add]

/-- Right multiplication by the adjoint of an exactly packet-preserving
operator also acts inside one coarse operator corner. -/
theorem opBlock_comp_adjoint_right_of_commutes
    (C : ProjectorFamily T cLane)
    (hSelf : ∀ a, (C.proj a).adjoint = C.proj a)
    (A D : T →L[ℝ] T)
    (hA : CommutesWithProjectors C A) (a b : cLane) :
    opBlock C (D.comp A.adjoint) a b =
      (opBlock C D a b).comp A.adjoint := by
  have hAadj := CommutesWithProjectors.adjoint C hSelf hA
  ext x
  have h := congrArg (fun L : T →L[ℝ] T => L x) (hAadj b)
  change C.proj b (A.adjoint x) = A.adjoint (C.proj b x) at h
  change C.proj a (D (A.adjoint (C.proj b x))) =
    C.proj a (D (C.proj b (A.adjoint x)))
  rw [h]

/-- A coarse covariance-error corner has a closed propagation estimate plus a
fine-descendant forcing budget. -/
theorem errorBlock_rhs_norm_le_descendantBudget
    (C : ProjectorFamily T cLane) (F : ProjectorFamily T fLane)
    (ρ : fLane → cLane) (hR : Refines C F ρ)
    (hSelf : ∀ a, (C.proj a).adjoint = C.proj a)
    (A0 D R : T →L[ℝ] T)
    (hA0 : CommutesWithProjectors C A0)
    (a b : cLane) :
    ‖opBlock C (A0.comp D + D.comp A0.adjoint + R) a b‖ ≤
      2 * ‖A0‖ * ‖opBlock C D a b‖ + descendantNormBudget F ρ R a b := by
  have hleft := opBlock_comp_left_of_commutes C A0 D hA0 a b
  have hright := opBlock_comp_adjoint_right_of_commutes C hSelf A0 D hA0 a b
  have hRnorm : ‖opBlock C R a b‖ ≤ descendantNormBudget F ρ R a b := by
    change ‖rawOpBlock C.proj R a b‖ ≤ _
    exact rawOpBlock_norm_le_descendant_norm_sum C.proj F.proj ρ
      (Refines.coarse_eq_fine_sum hR) R a b
  rw [opBlock_add, opBlock_add]
  calc
    ‖opBlock C (A0.comp D) a b + opBlock C (D.comp A0.adjoint) a b + opBlock C R a b‖
        ≤ ‖opBlock C (A0.comp D) a b + opBlock C (D.comp A0.adjoint) a b‖ +
            ‖opBlock C R a b‖ := norm_add_le _ _
    _ ≤ (‖opBlock C (A0.comp D) a b‖ + ‖opBlock C (D.comp A0.adjoint) a b‖) +
          ‖opBlock C R a b‖ := by gcongr; exact norm_add_le _ _
    _ ≤ (‖A0‖ * ‖opBlock C D a b‖) +
          (‖opBlock C D a b‖ * ‖A0.adjoint‖) + descendantNormBudget F ρ R a b := by
      gcongr
      · rw [hleft]
        exact ContinuousLinearMap.opNorm_comp_le _ _
      · rw [hright]
        exact ContinuousLinearMap.opNorm_comp_le _ _
    _ = 2 * ‖A0‖ * ‖opBlock C D a b‖ + descendantNormBudget F ρ R a b := by
      rw [norm_map]
      ring

/-- Finite-horizon multiscale Grönwall certificate.  A uniform fine residual
budget controls the accumulated norm of one coarse covariance-error corner. -/
theorem errorBlock_norm_le_gronwall
    (C : ProjectorFamily T cLane) (F : ProjectorFamily T fLane)
    (ρ : fLane → cLane) (hR : Refines C F ρ)
    (hSelf : ∀ a, (C.proj a).adjoint = C.proj a)
    (A0 : T →L[ℝ] T) (hA0 : CommutesWithProjectors C A0)
    (D Ddot R : ℝ → T →L[ℝ] T)
    (a b : cLane) (t0 t1 ε : ℝ)
    (hcont : ContinuousOn (fun t => opBlock C (D t) a b) (Icc t0 t1))
    (hderiv : ∀ t ∈ Ico t0 t1,
      HasDerivWithinAt (fun s => opBlock C (D s) a b)
        (opBlock C (Ddot t) a b) (Ici t) t)
    (hdyn : ∀ t ∈ Ico t0 t1,
      Ddot t = A0.comp (D t) + (D t).comp A0.adjoint + R t)
    (hbudget : ∀ t ∈ Ico t0 t1, descendantNormBudget F ρ (R t) a b ≤ ε) :
    ∀ t ∈ Icc t0 t1,
      ‖opBlock C (D t) a b‖ ≤
        gronwallBound ‖opBlock C (D t0) a b‖ (2 * ‖A0‖) ε (t - t0) := by
  apply norm_le_gronwallBound_of_norm_deriv_right_le hcont hderiv (le_refl _) 
  intro t ht
  rw [hdyn t ht]
  exact (errorBlock_rhs_norm_le_descendantBudget C F ρ hR hSelf A0 (D t) (R t)
    hA0 a b).trans (by gcongr; exact hbudget t ht)


/-- Explicit exponential form of the multiscale bound when the initial coarse
error corner vanishes and the baseline drift is nonzero. -/
theorem errorBlock_norm_le_exp_of_zero_initial
    (C : ProjectorFamily T cLane) (F : ProjectorFamily T fLane)
    (ρ : fLane → cLane) (hR : Refines C F ρ)
    (hSelf : ∀ a, (C.proj a).adjoint = C.proj a)
    (A0 : T →L[ℝ] T) (hA0 : CommutesWithProjectors C A0)
    (hA0ne : A0 ≠ 0)
    (D Ddot R : ℝ → T →L[ℝ] T)
    (a b : cLane) (t0 t1 ε : ℝ)
    (hcont : ContinuousOn (fun t => opBlock C (D t) a b) (Icc t0 t1))
    (hderiv : ∀ t ∈ Ico t0 t1,
      HasDerivWithinAt (fun s => opBlock C (D s) a b)
        (opBlock C (Ddot t) a b) (Ici t) t)
    (hdyn : ∀ t ∈ Ico t0 t1,
      Ddot t = A0.comp (D t) + (D t).comp A0.adjoint + R t)
    (hbudget : ∀ t ∈ Ico t0 t1, descendantNormBudget F ρ (R t) a b ≤ ε)
    (hinit : opBlock C (D t0) a b = 0) :
    ∀ t ∈ Icc t0 t1,
      ‖opBlock C (D t) a b‖ ≤
        ε / (2 * ‖A0‖) * (Real.exp ((2 * ‖A0‖) * (t - t0)) - 1) := by
  intro t ht
  have h := errorBlock_norm_le_gronwall C F ρ hR hSelf A0 hA0 D Ddot R
    a b t0 t1 ε hcont hderiv hdyn hbudget t ht
  have hnorm : ‖A0‖ ≠ 0 := norm_ne_zero_iff.mpr hA0ne
  have hK : 2 * ‖A0‖ ≠ 0 := mul_ne_zero (by norm_num) hnorm
  rw [hinit, norm_zero, gronwallBound_of_K_ne_0 hK] at h
  simpa only [zero_mul, zero_add] using h

/-- If the baseline drift vanishes, zero initial error grows at most linearly
with the uniform fine residual budget. -/
theorem errorBlock_norm_le_linear_of_zero_baseline
    (C : ProjectorFamily T cLane) (F : ProjectorFamily T fLane)
    (ρ : fLane → cLane) (hR : Refines C F ρ)
    (hSelf : ∀ a, (C.proj a).adjoint = C.proj a)
    (D Ddot R : ℝ → T →L[ℝ] T)
    (a b : cLane) (t0 t1 ε : ℝ)
    (hcont : ContinuousOn (fun t => opBlock C (D t) a b) (Icc t0 t1))
    (hderiv : ∀ t ∈ Ico t0 t1,
      HasDerivWithinAt (fun s => opBlock C (D s) a b)
        (opBlock C (Ddot t) a b) (Ici t) t)
    (hdyn : ∀ t ∈ Ico t0 t1, Ddot t = R t)
    (hbudget : ∀ t ∈ Ico t0 t1, descendantNormBudget F ρ (R t) a b ≤ ε)
    (hinit : opBlock C (D t0) a b = 0) :
    ∀ t ∈ Icc t0 t1, ‖opBlock C (D t) a b‖ ≤ ε * (t - t0) := by
  intro t ht
  have h := errorBlock_norm_le_gronwall C F ρ hR hSelf 0
    (by intro a; simp) D Ddot R a b t0 t1 ε
    hcont hderiv (by intro s hs; simpa using hdyn s hs) hbudget t ht
  rw [hinit, norm_zero] at h
  simpa [gronwallBound_K0] using h

/-- Time-dependent fine stochastic residual budget below one coarse corner. -/
def stochasticDescendantBudget
    (F : ProjectorFamily T fLane) (ρ : fLane → cLane)
    (RA P RQ : ℝ → T →L[ℝ] T) (t : ℝ) (a b : cLane) : ℝ :=
  descendantNormBudget F ρ (covarianceForcingOp (RA t) (P t) (RQ t)) a b

/-- **Finite-time stochastic multiscale covariance theorem.**  If the covariance
error obeys the exact baseline-plus-residual Lyapunov equation and the total
fine residual leakage below one coarse corner is uniformly at most `ε`, then
that coarse covariance-error corner is controlled by the Grönwall envelope. -/
theorem stochastic_errorBlock_norm_le_gronwall
    (C : ProjectorFamily T cLane) (F : ProjectorFamily T fLane)
    (ρ : fLane → cLane) (hR : Refines C F ρ)
    (hSelf : ∀ a, (C.proj a).adjoint = C.proj a)
    (A0 : T →L[ℝ] T) (hA0 : CommutesWithProjectors C A0)
    (D Ddot RA P RQ : ℝ → T →L[ℝ] T)
    (a b : cLane) (t0 t1 ε : ℝ)
    (hcont : ContinuousOn (fun t => opBlock C (D t) a b) (Icc t0 t1))
    (hderiv : ∀ t ∈ Ico t0 t1,
      HasDerivWithinAt (fun s => opBlock C (D s) a b)
        (opBlock C (Ddot t) a b) (Ici t) t)
    (hdyn : ∀ t ∈ Ico t0 t1,
      Ddot t = A0.comp (D t) + (D t).comp A0.adjoint +
        covarianceForcingOp (RA t) (P t) (RQ t))
    (hbudget : ∀ t ∈ Ico t0 t1,
      stochasticDescendantBudget F ρ RA P RQ t a b ≤ ε) :
    ∀ t ∈ Icc t0 t1,
      ‖opBlock C (D t) a b‖ ≤
        gronwallBound ‖opBlock C (D t0) a b‖ (2 * ‖A0‖) ε (t - t0) := by
  exact errorBlock_norm_le_gronwall C F ρ hR hSelf A0 hA0 D Ddot
    (fun t => covarianceForcingOp (RA t) (P t) (RQ t)) a b t0 t1 ε
    hcont hderiv hdyn (by simpa [stochasticDescendantBudget] using hbudget)

/-- Explicit stochastic multiscale stability bound from zero initial coarse
covariance error. -/
theorem stochastic_errorBlock_norm_le_exp_of_zero_initial
    (C : ProjectorFamily T cLane) (F : ProjectorFamily T fLane)
    (ρ : fLane → cLane) (hR : Refines C F ρ)
    (hSelf : ∀ a, (C.proj a).adjoint = C.proj a)
    (A0 : T →L[ℝ] T) (hA0 : CommutesWithProjectors C A0)
    (hA0ne : A0 ≠ 0)
    (D Ddot RA P RQ : ℝ → T →L[ℝ] T)
    (a b : cLane) (t0 t1 ε : ℝ)
    (hcont : ContinuousOn (fun t => opBlock C (D t) a b) (Icc t0 t1))
    (hderiv : ∀ t ∈ Ico t0 t1,
      HasDerivWithinAt (fun s => opBlock C (D s) a b)
        (opBlock C (Ddot t) a b) (Ici t) t)
    (hdyn : ∀ t ∈ Ico t0 t1,
      Ddot t = A0.comp (D t) + (D t).comp A0.adjoint +
        covarianceForcingOp (RA t) (P t) (RQ t))
    (hbudget : ∀ t ∈ Ico t0 t1,
      stochasticDescendantBudget F ρ RA P RQ t a b ≤ ε)
    (hinit : opBlock C (D t0) a b = 0) :
    ∀ t ∈ Icc t0 t1,
      ‖opBlock C (D t) a b‖ ≤
        ε / (2 * ‖A0‖) * (Real.exp ((2 * ‖A0‖) * (t - t0)) - 1) := by
  exact errorBlock_norm_le_exp_of_zero_initial C F ρ hR hSelf A0 hA0 hA0ne
    D Ddot (fun t => covarianceForcingOp (RA t) (P t) (RQ t))
    a b t0 t1 ε hcont hderiv hdyn
    (by simpa [stochasticDescendantBudget] using hbudget) hinit

end FiniteTimeMultiscale

end Komorebi.AbstractProjectorRefinement
