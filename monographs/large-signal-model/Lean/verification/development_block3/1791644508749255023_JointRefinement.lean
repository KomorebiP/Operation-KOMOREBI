import KomorebiLSM.FinitePartitions

/-! P9's actual iterative partition construction, termination and least refinement. -/
set_option autoImplicit false
namespace Komorebi.LSM.FinitePartitions
open scoped BigOperators
universe u v w
variable {I : Type u} [Fintype I] {U : Type v} {Y : Type w}

def Lumpable (K : U → I → I → ℝ) (r : Setoid I) : Prop :=
  ∀ u i j, r i j → blockAggregate r (K u i) = blockAggregate r (K u j)

def LikelihoodConstant (l : Y → I → ℝ) (r : Setoid I) : Prop :=
  ∀ y i j, r i j → l y i = l y j

noncomputable def transitionSplit (K : U → I → I → ℝ) (r : Setoid I) : Setoid I where
  r i j := r i j ∧ ∀ u k, blockMass r (K u i) k = blockMass r (K u j) k
  iseqv := {
    refl := fun _ => ⟨r.refl _, fun _ _ => rfl⟩
    symm := fun h => ⟨r.symm h.1, fun u k => (h.2 u k).symm⟩
    trans := fun h h' => ⟨r.trans h.1 h'.1, fun u k => (h.2 u k).trans (h'.2 u k)⟩ }

theorem transitionSplit_le (K : U → I → I → ℝ) (r : Setoid I) :
    transitionSplit K r ≤ r := by
  intro i j h
  exact h.1

theorem split_row_equality (K : U → I → I → ℝ) (r : Setoid I) (i j : I)
    (h : transitionSplit K r i j) (u : U) :
    blockAggregate r (K u i) = blockAggregate r (K u j) := by
  funext q
  induction q using Quotient.inductionOn with
  | h k => simpa only [blockAggregate_mk] using h.2 u k

theorem transitionSplit_fixed_iff (K : U → I → I → ℝ) (r : Setoid I) :
    transitionSplit K r = r ↔ Lumpable K r := by
  constructor
  · intro h u i j hij
    exact split_row_equality K r i j (by rwa [h]) u
  · intro h
    apply le_antisymm (transitionSplit_le K r)
    intro i j hij
    refine ⟨hij, ?_⟩
    intro u k
    simpa only [blockAggregate_mk] using congrFun (h u i j hij) (Quotient.mk r k)

theorem transitionSplit_mono (K : U → I → I → ℝ) {r s : Setoid I} (h : r ≤ s) :
    transitionSplit K r ≤ transitionSplit K s := by
  intro i j hij
  refine ⟨h hij.1, ?_⟩
  intro u k
  have he := same_fine_implies_same_coarse h (K u i) (K u j)
    (split_row_equality K r i j hij u)
  simpa only [blockAggregate_mk] using congrFun he (Quotient.mk s k)

noncomputable def refinementIter (K : U → I → I → ℝ) (r : Setoid I) : ℕ → Setoid I
  | 0 => r
  | n+1 => transitionSplit K (refinementIter K r n)

@[simp] theorem refinementIter_zero (K : U → I → I → ℝ) (r : Setoid I) :
    refinementIter K r 0 = r := rfl

@[simp] theorem refinementIter_succ (K : U → I → I → ℝ) (r : Setoid I) (n : ℕ) :
    refinementIter K r (n+1) = transitionSplit K (refinementIter K r n) := rfl

theorem refinementIter_step_le (K : U → I → I → ℝ) (r : Setoid I) (n : ℕ) :
    refinementIter K r (n+1) ≤ refinementIter K r n := transitionSplit_le _ _

theorem refinementIter_le_initial (K : U → I → I → ℝ) (r : Setoid I) (n : ℕ) :
    refinementIter K r n ≤ r := by
  induction n with
  | zero => exact le_rfl
  | succ n ih => exact le_trans (refinementIter_step_le K r n) ih

theorem refinementIter_stays_fixed (K : U → I → I → ℝ) (r : Setoid I) (n : ℕ)
    (h : refinementIter K r (n+1) = refinementIter K r n) (k : ℕ) :
    refinementIter K r (n+k) = refinementIter K r n := by
  induction k with
  | zero => simp
  | succ k ih =>
    rw [Nat.add_succ, refinementIter_succ, ih]
    exact h

theorem refinement_stabilizes (K : U → I → I → ℝ) (r : Setoid I) :
    ∃ n ≤ Fintype.card I - blockCount r,
      refinementIter K r (n+1) = refinementIter K r n := by
  let N := Fintype.card I - blockCount r
  have hcard := blockCount_le r
  by_contra h
  have hne : ∀ n ≤ N, refinementIter K r (n+1) ≠ refinementIter K r n := by
    intro n hn he
    exact h ⟨n, hn, he⟩
  have hgrow : ∀ n ≤ N+1, blockCount r + n ≤ blockCount (refinementIter K r n) := by
    intro n
    induction n with
    | zero => intro _; simp
    | succ n ih =>
      intro hn
      have hprev := ih (by omega)
      have hlt := strict_refinement_count (refinementIter_step_le K r n) (hne n (by omega))
      omega
  have hn := hgrow (N+1) le_rfl
  have hbound := blockCount_le (refinementIter K r (N+1))
  dsimp [N] at *
  omega

noncomputable def stableRefinement (K : U → I → I → ℝ) (r : Setoid I) : Setoid I :=
  refinementIter K r (Fintype.card I - blockCount r)

theorem stableRefinement_fixed (K : U → I → I → ℝ) (r : Setoid I) :
    transitionSplit K (stableRefinement K r) = stableRefinement K r := by
  obtain ⟨n, hn, he⟩ := refinement_stabilizes K r
  have hh := refinementIter_stays_fixed K r n he (Fintype.card I - blockCount r - n)
  have hnadd : n + (Fintype.card I - blockCount r - n) = Fintype.card I - blockCount r := by omega
  rw [hnadd] at hh
  unfold stableRefinement
  rw [hh]
  exact he

theorem stableRefinement_le (K : U → I → I → ℝ) (r : Setoid I) :
    stableRefinement K r ≤ r := refinementIter_le_initial _ _ _

theorem stableRefinement_lumpable (K : U → I → I → ℝ) (r : Setoid I) :
    Lumpable K (stableRefinement K r) :=
  (transitionSplit_fixed_iff _ _).mp (stableRefinement_fixed K r)

theorem stableRefinement_coarsest (K : U → I → I → ℝ) (r t : Setoid I)
    (htr : t ≤ r) (ht : Lumpable K t) : t ≤ stableRefinement K r := by
  have hfix := (transitionSplit_fixed_iff K t).mpr ht
  have hi : ∀ n, t ≤ refinementIter K r n := by
    intro n
    induction n with
    | zero => exact htr
    | succ n ih =>
      change t ≤ transitionSplit K (refinementIter K r n)
      calc t = transitionSplit K t := hfix.symm
           _ ≤ transitionSplit K (refinementIter K r n) := transitionSplit_mono K ih
  exact hi _

omit [Fintype I] in
def likelihoodSplit (r : Setoid I) (l : Y → I → ℝ) : Setoid I where
  r i j := r i j ∧ ∀ y, l y i = l y j
  iseqv := {
    refl := fun _ => ⟨r.refl _, fun _ => rfl⟩
    symm := fun h => ⟨r.symm h.1, fun y => (h.2 y).symm⟩
    trans := fun h h' => ⟨r.trans h.1 h'.1, fun y => (h.2 y).trans (h'.2 y)⟩ }

noncomputable def jointRefinement (K : U → I → I → ℝ) (l : Y → I → ℝ)
    (r : Setoid I) : Setoid I := stableRefinement K (likelihoodSplit r l)

theorem jointRefinement_refines (K : U → I → I → ℝ) (l : Y → I → ℝ) (r : Setoid I) :
    jointRefinement K l r ≤ r := by
  intro i j hij
  exact (stableRefinement_le K (likelihoodSplit r l) hij).1

theorem jointRefinement_likelihood (K : U → I → I → ℝ) (l : Y → I → ℝ) (r : Setoid I) :
    LikelihoodConstant l (jointRefinement K l r) := by
  intro y i j hij
  exact (stableRefinement_le K (likelihoodSplit r l) hij).2 y

theorem jointRefinement_lumpable (K : U → I → I → ℝ) (l : Y → I → ℝ) (r : Setoid I) :
    Lumpable K (jointRefinement K l r) := stableRefinement_lumpable _ _

theorem jointRefinement_coarsest (K : U → I → I → ℝ) (l : Y → I → ℝ)
    (r t : Setoid I) (htr : t ≤ r) (hk : Lumpable K t) (hl : LikelihoodConstant l t) :
    t ≤ jointRefinement K l r := by
  apply stableRefinement_coarsest K (likelihoodSplit r l) t
  · intro i j hij; exact ⟨htr hij, fun y => hl y i j hij⟩
  · exact hk

theorem jointRefinement_termination (K : U → I → I → ℝ) (l : Y → I → ℝ) (r : Setoid I) :
    ∃ n ≤ Fintype.card I - blockCount (likelihoodSplit r l),
      refinementIter K (likelihoodSplit r l) (n+1) = refinementIter K (likelihoodSplit r l) n :=
  refinement_stabilizes _ _

end Komorebi.LSM.FinitePartitions
