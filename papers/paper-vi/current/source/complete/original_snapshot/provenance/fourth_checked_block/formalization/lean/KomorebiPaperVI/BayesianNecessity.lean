import KomorebiPaperVI.Coarsening

/-! Author: Komorebi P. All-prior necessity is derived from actual two-state priors. -/
namespace KomorebiPaperVI.BayesianNecessity
open KomorebiPaperVI.FiniteBayes KomorebiPaperVI.Coarsening
open scoped BigOperators
variable {I A : Type*} [Fintype I] [Fintype A] [DecidableEq I] [DecidableEq A]

noncomputable def pairPrior (i j : I) (x : I) : ℝ :=
  (if x=i then 1/2 else 0)+(if x=j then 1/2 else 0)

omit [Fintype A] [DecidableEq A] in
theorem pair_weighted_sum (i j : I) (w : I → ℝ) :
    (∑ x, w x*pairPrior i j x)=(w i+w j)/2 := by
  simp [pairPrior, mul_add, Finset.sum_add_distrib]
  ring

omit [Fintype A] [DecidableEq A] in
theorem pair_probability (i j : I) : IsProbability (pairPrior i j) := by
  constructor
  · intro x; unfold pairPrior; split_ifs <;> norm_num
  · simpa [IsProbability, mass] using pair_weighted_sum i j (fun _ => 1)

omit [Fintype A] in
theorem pair_fiber_weight (f : I → A) (i j : I) (w : I → ℝ) (a : A) :
    coarsen f (fun x => w x*pairPrior i j x) a =
      ((if f i=a then w i else 0)+(if f j=a then w j else 0))/2 := by
  have he : coarsen f (fun x => w x*pairPrior i j x) a =
      ∑ x, (if f x=a then w x else 0)*pairPrior i j x := by
    apply Finset.sum_congr rfl
    intro x _; split_ifs <;> simp
  rw [he, pair_weighted_sum]

omit [Fintype A] in
theorem pair_coarsen (f : I → A) (i j : I) :
    coarsen f (pairPrior i j)=pairPrior (f i) (f j) := by
  funext a
  have he := pair_fiber_weight f i j (fun _ => 1) a
  simp only [one_mul] at he
  rw [he]
  rw [add_div]
  have h1 : (if f i=a then (1:ℝ) else 0)/2=(if a=f i then 1/2 else 0) := by
    by_cases hi : f i=a
    · simp [hi]
    · simp [hi, Ne.symm hi]
  have h2 : (if f j=a then (1:ℝ) else 0)/2=(if a=f j then 1/2 else 0) := by
    by_cases hj : f j=a
    · simp [hj]
    · simp [hj, Ne.symm hj]
  rw [h1,h2]
  rfl

omit [Fintype A] in
theorem pair_coarse_posterior (f : I → A) (l : I → ℝ) (i j : I) (hij : f i≠f j) :
    coarsen f (update (pairPrior i j) l) (f i)=l i/(l i+l j) := by
  simp only [coarsen_posterior]
  rw [pair_fiber_weight]
  have he : evidence (pairPrior i j) l=(l i+l j)/2 := pair_weighted_sum i j l
  rw [he]
  simp only [ite_true, ite_eq_right hij.symm, add_zero]
  rw [div_div_div_comm]
  norm_num

def AllPriorCommutes (f : I → A) (l : I → ℝ) (k : A → ℝ) : Prop :=
  ∀ p, IsProbability p → coarsen f (update p l)=update (coarsen f p) k

theorem cross_packet_ratio (f : I → A) (l : I → ℝ) (k : A → ℝ)
    (hl : ∀ i, 0 < l i) (hk : ∀ a, 0 < k a)
    (h : AllPriorCommutes f l k) (i j : I) (hij : f i≠f j) :
    l i*k (f j)=l j*k (f i) := by
  have he := congrFun (h (pairPrior i j) (pair_probability i j)) (f i)
  rw [pair_coarse_posterior f l i j hij, pair_coarsen] at he
  have hco : update (pairPrior (f i) (f j)) k (f i)=k (f i)/(k (f i)+k (f j)) := by
    dsimp [update]
    rw [show evidence (pairPrior (f i) (f j)) k=(k (f i)+k (f j))/2 from
      pair_weighted_sum _ _ _]
    simp only [pairPrior, ite_true, ite_eq_right hij, add_zero]
    rw [mul_div_assoc, div_div_div_comm]
    norm_num [div_eq_mul_inv]
  rw [hco] at he
  have hc := (div_eq_div_iff (ne_of_gt (add_pos (hl i) (hl j)))
    (ne_of_gt (add_pos (hk (f i)) (hk (f j))))).mp he
  nlinarith

theorem all_packet_ratio (f : I → A) (hf : Function.Surjective f) [Nontrivial A]
    (l : I → ℝ) (k : A → ℝ) (hl : ∀ i, 0 < l i) (hk : ∀ a, 0 < k a)
    (h : AllPriorCommutes f l k) (i j : I) : l i*k (f j)=l j*k (f i) := by
  by_cases hij : f i=f j
  · obtain ⟨b,hb⟩ := exists_ne (f i)
    obtain ⟨u,hu⟩ := hf b
    have hiu : f i≠f u := by rw [hu]; exact hb.symm
    have hju : f j≠f u := by rw [← hij]; exact hiu
    have h1 := cross_packet_ratio f l k hl hk h i u hiu
    have h2 := cross_packet_ratio f l k hl hk h j u hju
    rw [← hij] at h2
    have heq : l i=l j := by nlinarith [hk (f u)]
    rw [hij, heq]
  · exact cross_packet_ratio f l k hl hk h i j hij

omit [DecidableEq I] in
theorem positive_evidence (p l : I → ℝ) (hp : IsProbability p) (hl : ∀ i, 0 < l i) :
    0 < evidence p l := by
  have hex : ∃ i, 0 < p i := by
    by_contra h
    push Not at h
    have hz : mass p=0 := Finset.sum_eq_zero (fun i _ => le_antisymm (h i) (hp.1 i))
    linarith [hp.2]
  obtain ⟨i,hi⟩ := hex
  exact Finset.sum_pos' (fun j _ => mul_nonneg (hl j).le (hp.1 j))
    ⟨i,Finset.mem_univ i,mul_pos (hl i) hi⟩

theorem refinement_iff (f : I → A) (hf : Function.Surjective f) [Nontrivial A]
    (l : I → ℝ) (k : A → ℝ) (hl : ∀ i, 0 < l i) (hk : ∀ a, 0 < k a) :
    AllPriorCommutes f l k ↔ ∃ c : ℝ, 0 < c ∧ ∀ i, l i=c*k (f i) := by
  constructor
  · intro h
    obtain ⟨a⟩ := (inferInstance : Nonempty A)
    obtain ⟨i,hi⟩ := hf a
    refine ⟨l i/k (f i), div_pos (hl i) (hk (f i)), ?_⟩
    intro j
    have he := all_packet_ratio f hf l k hl hk h j i
    apply (eq_div_iff (ne_of_gt (hk (f i)))).mpr at he
    calc
      l j = (l i*k (f j))/k (f i) := he
      _ = _ := by ring
  · rintro ⟨c,hc,he⟩ p hp
    have heq : l=fun i => c*k (f i) := funext he
    rw [heq]
    exact scaled_blockwise_sufficiency f p k c hc.ne'
      (positive_evidence p (k ∘ f) hp (fun i => hk (f i))).ne'

end KomorebiPaperVI.BayesianNecessity
