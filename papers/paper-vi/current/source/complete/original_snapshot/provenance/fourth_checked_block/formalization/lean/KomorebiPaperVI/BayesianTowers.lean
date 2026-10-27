import KomorebiPaperVI.BayesianNecessity

/-! Author: Komorebi P. Variable-state finite towers with explicit singleton boundaries. -/
namespace KomorebiPaperVI.BayesianTowers
open KomorebiPaperVI.FiniteBayes KomorebiPaperVI.Coarsening
open KomorebiPaperVI.BayesianNecessity
open scoped BigOperators
variable {I A B : Type*} [Fintype I] [Fintype A] [Fintype B]
    [DecidableEq I] [DecidableEq A] [DecidableEq B]

omit [DecidableEq I] [Fintype B] in
theorem coarsen_comp (f : I → A) (g : A → B) (p : I → ℝ) :
    coarsen g (coarsen f p)=coarsen (g ∘ f) p := by
  funext b
  dsimp [coarsen]
  have hi (q : Prop) [Decidable q] (v : I → ℝ) :
      (if q then ∑ i, v i else 0)=∑ i, if q then v i else 0 := by
    split_ifs <;> simp
  simp_rw [hi]
  rw [Finset.sum_comm]
  apply Finset.sum_congr rfl
  intro i _
  have he : (fun a => if g a=b then (if f i=a then p i else 0) else 0)=
      (fun a => if f i=a then (if g a=b then p i else 0) else 0) := by
    funext a; split_ifs <;> rfl
  rw [he]
  simp

omit [DecidableEq I] in
theorem singleton_commutes (f : I → A) (l : I → ℝ) (k : A → ℝ)
    (hl : ∀ i, 0 < l i) (hk : ∀ a, 0 < k a) [Subsingleton A] :
    AllPriorCommutes f l k := by
  intro p hp
  funext a
  have hs (v : A → ℝ) : mass v=v a :=
    Finset.sum_eq_single a (fun b _ hb => False.elim (hb (Subsingleton.elim b a))) (by simp)
  have h1 : mass (coarsen f (update p l))=1 :=
    (coarsen_mass f _).trans (posterior_mass p l (positive_evidence p l hp hl).ne')
  have h2 := posterior_mass (coarsen f p) k
    (positive_evidence _ k (coarsen_probability f p hp) hk).ne'
  exact (hs _).symm.trans (h1.trans (h2.symm.trans (hs _)))

theorem adjacent_criterion (f : I → A) (hf : Function.Surjective f)
    (l : I → ℝ) (k : A → ℝ) (hl : ∀ i, 0 < l i) (hk : ∀ a, 0 < k a) :
    AllPriorCommutes f l k ↔
      Subsingleton A ∨ ∃ c : ℝ, 0 < c ∧ ∀ i, l i=c*k (f i) := by
  cases subsingleton_or_nontrivial A with
  | inl h =>
    let := h
    exact ⟨fun _ => Or.inl h,fun _ => singleton_commutes f l k hl hk⟩
  | inr h =>
    let := h
    rw [refinement_iff f hf l k hl hk]
    simp only [not_subsingleton, false_or]

omit [DecidableEq I] in
theorem compose_commutes (f : I → A) (g : A → B) (l : I → ℝ) (k : A → ℝ) (m : B → ℝ)
    (hf : AllPriorCommutes f l k) (hg : AllPriorCommutes g k m) :
    AllPriorCommutes (g ∘ f) l m := by
  intro p hp
  rw [← coarsen_comp f g, hf p hp, hg (coarsen f p) (coarsen_probability f p hp),coarsen_comp]

section Tower
variable {X : ℕ → Type*} [∀ n, Fintype (X n)] [∀ n, DecidableEq (X n)]

def towerMap (f : ∀ n, X n → X (n+1)) (s : ℕ) : (n : ℕ) → X s → X (s+n)
  | 0 => id
  | n+1 => f (s+n) ∘ towerMap f s n

theorem coarsen_id (p : I → ℝ) : coarsen id p=p := by
  funext i; simp [coarsen]

theorem tower_commutes (f : ∀ n, X n → X (n+1)) (l : ∀ n, X n → ℝ)
    (h : ∀ n, AllPriorCommutes (f n) (l n) (l (n+1))) (s n : ℕ) :
    AllPriorCommutes (towerMap f s n) (l s) (l (s+n)) := by
  induction n with
  | zero => intro p _; simp [towerMap,coarsen_id]
  | succ n ih => exact compose_commutes (towerMap f s n) (f (s+n)) _ _ _ ih (h (s+n))

theorem tower_criterion (f : ∀ n, X n → X (n+1)) (hf : ∀ n, Function.Surjective (f n))
    (l : ∀ n, X n → ℝ) (hl : ∀ n i, 0 < l n i) :
    (∀ n, AllPriorCommutes (f n) (l n) (l (n+1))) ↔
      ∀ n, Subsingleton (X (n+1)) ∨ ∃ c : ℝ, 0 < c ∧ ∀ i, l n i=c*l (n+1) (f n i) := by
  exact forall_congr' (fun n => adjacent_criterion (f n) (hf n) _ _ (hl n) (hl (n+1)))

end Tower
end KomorebiPaperVI.BayesianTowers
