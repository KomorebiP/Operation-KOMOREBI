import KomorebiLSM.JointRefinement
import KomorebiLSM.BayesianClosure

/-! Actual stochastic quotient kernels and their prediction/update equations. -/
set_option autoImplicit false
namespace Komorebi.LSM.FiniteBayes
open scoped BigOperators
universe u v
variable {I : Type u} {A : Type v} [Fintype I]

def IsStochastic (K : I → I → ℝ) : Prop := ∀ i, IsPrior (K i)

noncomputable def prediction (K : I → I → ℝ) (p : I → ℝ) (j : I) : ℝ :=
  ∑ i, p i * K i j

theorem pointMass_isPrior [DecidableEq I] (i : I) : IsPrior (pointMass i) := by
  constructor
  · intro j; simp only [pointMass]; positivity
  · simp [pointMass]

theorem prediction_pointMass [DecidableEq I] (K : I → I → ℝ) (i : I) :
    prediction K (pointMass i) = K i := by
  funext j
  exact pointMass_test i (fun k => K k j)

theorem prediction_isPrior (K : I → I → ℝ) (hK : IsStochastic K)
    (p : I → ℝ) (hp : IsPrior p) : IsPrior (prediction K p) := by
  constructor
  · intro j
    exact Finset.sum_nonneg (fun i _ => mul_nonneg (hp.1 i) ((hK i).1 j))
  · simp only [prediction]
    rw [Finset.sum_comm]
    simp only [← Finset.mul_sum, (hK _).2, mul_one]
    exact hp.2

theorem aggregate_prediction [DecidableEq A] (c : I → A) (K : I → I → ℝ)
    (p : I → ℝ) (a : A) :
    aggregate c (prediction K p) a = ∑ i, p i * aggregate c (K i) a := by
  unfold aggregate prediction
  have h (j : I) : (if c j = a then ∑ i, p i * K i j else 0) =
      ∑ i, if c j = a then p i * K i j else 0 := by
    by_cases hh : c j = a <;> simp [hh]
  simp only [h]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro i _
  simp [Finset.mul_sum, mul_ite]

theorem prediction_commutes_of_rows [Fintype A] [DecidableEq A]
    (c : I → A) (K : I → I → ℝ) (Kb : A → A → ℝ)
    (hrows : ∀ i, aggregate c (K i) = Kb (c i)) (p : I → ℝ) :
    aggregate c (prediction K p) = prediction Kb (aggregate c p) := by
  funext a
  rw [aggregate_prediction]
  simp only [hrows, prediction]
  exact (aggregate_weighted_sum c p (fun j => Kb j a)).symm

theorem prediction_rows_of_commutes [Fintype A] [DecidableEq A]
    (c : I → A) (K : I → I → ℝ) (Kb : A → A → ℝ)
    (hc : ∀ p, IsPrior p → aggregate c (prediction K p) = prediction Kb (aggregate c p))
    (i : I) : aggregate c (K i) = Kb (c i) := by
  classical
  have h := hc (pointMass i) (pointMass_isPrior i)
  rwa [prediction_pointMass, aggregate_pointMass, prediction_pointMass] at h

end Komorebi.LSM.FiniteBayes

namespace Komorebi.LSM.FinitePartitions
open scoped BigOperators
open FiniteBayes
universe u v w
variable {I : Type u} [Fintype I] {U : Type v} {Y : Type w}

noncomputable def quotientKernel (K : U → I → I → ℝ) (r : Setoid I)
    (h : Lumpable K r) (u : U) : Quotient r → Quotient r → ℝ :=
  Quotient.lift (fun i => blockAggregate r (K u i)) (fun i j hij => h u i j hij)

@[simp] theorem quotientKernel_mk (K : U → I → I → ℝ) (r : Setoid I)
    (h : Lumpable K r) (u : U) (i : I) :
    quotientKernel K r h u (Quotient.mk r i) = blockAggregate r (K u i) := rfl

theorem quotientKernel_stochastic (K : U → I → I → ℝ) (r : Setoid I)
    (h : Lumpable K r) (hK : ∀ u, IsStochastic (K u)) (u : U) :
    IsStochastic (quotientKernel K r h u) := by
  classical
  intro q
  induction q using Quotient.inductionOn with
  | h i => exact aggregate_prior (Quotient.mk r) (K u i) (hK u i)

theorem quotient_prediction_commutes (K : U → I → I → ℝ) (r : Setoid I)
    (h : Lumpable K r) (u : U) (p : I → ℝ) :
    blockAggregate r (prediction (K u) p) =
      prediction (quotientKernel K r h u) (blockAggregate r p) := by
  classical
  exact prediction_commutes_of_rows (Quotient.mk r) (K u)
    (quotientKernel K r h u) (fun _ => rfl) p

omit [Fintype I] in
noncomputable def quotientLikelihood (l : Y → I → ℝ) (r : Setoid I)
    (h : LikelihoodConstant l r) (y : Y) : Quotient r → ℝ :=
  Quotient.lift (l y) (fun i j hij => h y i j hij)

omit [Fintype I] in
@[simp] theorem quotientLikelihood_mk (l : Y → I → ℝ) (r : Setoid I)
    (h : LikelihoodConstant l r) (y : Y) (i : I) :
    quotientLikelihood l r h y (Quotient.mk r i) = l y i := rfl

omit [Fintype I] in
theorem quotientLikelihood_pos (l : Y → I → ℝ) (r : Setoid I)
    (h : LikelihoodConstant l r) (hl : ∀ y i, 0 < l y i) (y : Y) (q : Quotient r) :
    0 < quotientLikelihood l r h y q := by
  induction q using Quotient.inductionOn with
  | h i => exact hl y i

theorem quotient_bayes_commutes (l : Y → I → ℝ) (r : Setoid I)
    (h : LikelihoodConstant l r) (y : Y) (p : I → ℝ) :
    blockAggregate r (posterior p (l y)) =
      posterior (blockAggregate r p) (quotientLikelihood l r h y) := by
  classical
  exact posterior_coarsening_pullback (Quotient.mk r) p (quotientLikelihood l r h y)

omit [Fintype I] in
theorem nontrivial_refinement {r s : Setoid I} [Nontrivial (Quotient s)]
    (h : r ≤ s) : Nontrivial (Quotient r) := by
  obtain ⟨q1, q2, hq⟩ := exists_pair_ne (Quotient s)
  obtain ⟨p1, hp1⟩ := coarsenMap_surjective h q1
  obtain ⟨p2, hp2⟩ := coarsenMap_surjective h q2
  refine ⟨⟨p1,p2,?_⟩⟩
  intro he
  exact hq (hp1.symm.trans ((congrArg (coarsenMap h) he).trans hp2))

noncomputable def JointlyClosed (K : U → I → I → ℝ) (l : Y → I → ℝ)
    (r : Setoid I) : Prop := by
  classical
  exact ∃ (Kb : U → Quotient r → Quotient r → ℝ) (lb : Y → Quotient r → ℝ),
    (∀ u, IsStochastic (Kb u)) ∧ (∀ y q, 0 < lb y q) ∧
    (∀ u p, IsPrior p → blockAggregate r (prediction (K u) p) =
      prediction (Kb u) (blockAggregate r p)) ∧
    (∀ y p, IsPrior p → blockAggregate r (posterior p (l y)) =
      posterior (blockAggregate r p) (lb y))

theorem joint_closed_iff (K : U → I → I → ℝ) (l : Y → I → ℝ) (r : Setoid I)
    [Nontrivial (Quotient r)] (hK : ∀ u, IsStochastic (K u)) (hl : ∀ y i, 0 < l y i) :
    JointlyClosed K l r ↔ Lumpable K r ∧ LikelihoodConstant l r := by
  classical
  constructor
  · rintro ⟨Kb, lb, _, hlb, hpred, hbay⟩
    constructor
    · intro u i j hij
      have hi := prediction_rows_of_commutes (Quotient.mk r) (K u) (Kb u) (hpred u) i
      have hj := prediction_rows_of_commutes (Quotient.mk r) (K u) (Kb u) (hpred u) j
      change blockAggregate r (K u i) = Kb u (Quotient.mk r i) at hi
      change blockAggregate r (K u j) = Kb u (Quotient.mk r j) at hj
      rw [hi, hj, Quotient.sound hij]
    · intro y i j hij
      exact likelihood_constant_on_fibers (Quotient.mk r) Quotient.mk_surjective
        (l y) (lb y) (hl y) (hlb y) (hbay y) i j (Quotient.sound hij)
  · rintro ⟨hk, hlik⟩
    exact ⟨quotientKernel K r hk, quotientLikelihood l r hlik,
      quotientKernel_stochastic K r hk hK, quotientLikelihood_pos l r hlik hl,
      fun u p _ => quotient_prediction_commutes K r hk u p,
      fun y p _ => quotient_bayes_commutes l r hlik y p⟩

theorem jointRefinement_closed (K : U → I → I → ℝ) (l : Y → I → ℝ) (r : Setoid I)
    (hK : ∀ u, IsStochastic (K u)) (hl : ∀ y i, 0 < l y i) :
    JointlyClosed K l (jointRefinement K l r) := by
  classical
  let t := jointRefinement K l r
  have hk : Lumpable K t := jointRefinement_lumpable K l r
  have hlik : LikelihoodConstant l t := jointRefinement_likelihood K l r
  exact ⟨quotientKernel K t hk, quotientLikelihood l t hlik,
    quotientKernel_stochastic K t hk hK, quotientLikelihood_pos l t hlik hl,
    fun u p _ => quotient_prediction_commutes K t hk u p,
    fun y p _ => quotient_bayes_commutes l t hlik y p⟩

theorem jointlyClosed_refines_completion (K : U → I → I → ℝ) (l : Y → I → ℝ)
    (r s : Setoid I) [Nontrivial (Quotient r)]
    (hK : ∀ u, IsStochastic (K u)) (hl : ∀ y i, 0 < l y i)
    (hsr : s ≤ r) (hs : JointlyClosed K l s) : s ≤ jointRefinement K l r := by
  letI := nontrivial_refinement hsr
  have h := (joint_closed_iff K l s hK hl).mp hs
  exact jointRefinement_coarsest K l r s hsr h.1 h.2

theorem coarsest_jointly_closed (K : U → I → I → ℝ) (l : Y → I → ℝ)
    (r : Setoid I) [Nontrivial (Quotient r)]
    (hK : ∀ u, IsStochastic (K u)) (hl : ∀ y i, 0 < l y i) :
    ∃! t : Setoid I, t ≤ r ∧ JointlyClosed K l t ∧
      ∀ s : Setoid I, s ≤ r → JointlyClosed K l s → s ≤ t := by
  have htr := jointRefinement_refines K l r
  have htc := jointRefinement_closed K l r hK hl
  have hleast := jointlyClosed_refines_completion K l r
  refine ⟨jointRefinement K l r, ⟨htr, htc, ?_⟩, ?_⟩
  · intro s hsr hsc
    exact hleast s hK hl hsr hsc
  · intro s hs
    exact le_antisymm (hleast s hK hl hs.1 hs.2.1)
      (hs.2.2 (jointRefinement K l r) htr htc)

end Komorebi.LSM.FinitePartitions
