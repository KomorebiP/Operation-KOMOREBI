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

end Komorebi.LSM.FinitePartitions
