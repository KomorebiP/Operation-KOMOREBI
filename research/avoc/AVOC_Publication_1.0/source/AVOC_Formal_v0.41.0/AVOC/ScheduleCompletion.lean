import AVOC.ProofScheduling
import Mathlib.Data.Fintype.Card
import Lean.Elab.Tactic.Omega

namespace Komorebi.AVOC.Scheduling

variable {P : Type*} [PartialOrder P] [DecidableEq P]

/-- A topologically ordered, duplicate-free completion of an ideal is executable. -/
theorem legal_of_topological {K : Finset P} {xs : List P}
    (hK : IsIdeal K) (hn : xs.Nodup)
    (hf : ∀ x ∈ xs, x ∉ K)
    (hi : IsIdeal (K ∪ xs.toFinset))
    (ho : xs.Pairwise (fun x y => ¬ y < x)) : Legal K xs := by
  induction xs generalizing K with
  | nil => exact legal_nil K
  | cons x xs ih =>
    obtain ⟨hnx, hnt⟩ := List.nodup_cons.mp hn
    obtain ⟨hox, hot⟩ := List.pairwise_cons.mp ho
    have hx : Ready K x := by
      refine ⟨hf x (by simp), ?_⟩
      intro y hy
      have hym := hi (Finset.mem_union_right K (by simp)) (le_of_lt hy)
      rcases Finset.mem_union.mp hym with hym | hym
      · exact hym
      · have hlist : y = x ∨ y ∈ xs := by simpa using hym
        rcases hlist with heq | hyt
        · exact False.elim ((ne_of_lt hy) heq)
        · exact False.elim (hox y hyt hy)
    refine ⟨hx, ih (ideal_insert hK hx) hnt ?_ ?_ hot⟩
    · intro y hy hym
      rcases Finset.mem_insert.mp hym with heq | hym
      · subst y
        exact hnx hy
      · exact hf y (List.mem_cons_of_mem x hy) hym
    · simpa [List.toFinset_cons, Finset.insert_union, Finset.union_insert] using hi

/-- Independent structural characterization: freshness, no duplicates, final
closure, and no prerequisite appearing after its dependent. -/
theorem legal_iff_structural {K : Finset P} {xs : List P} (hK : IsIdeal K) :
    Legal K xs ↔
      xs.Nodup ∧ (∀ x ∈ xs, x ∉ K) ∧ IsIdeal (K ∪ xs.toFinset) ∧
        xs.Pairwise (fun x y => ¬ y < x) := by
  constructor
  · intro h
    exact ⟨legal_nodup h, legal_fresh h, legal_final_ideal hK h, legal_topological h⟩
  · rintro ⟨hn,hf,hi,ho⟩
    exact legal_of_topological hK hn hf hi ho

/-- A complete list that extends the strict dependency order. -/
def LinearExtension [Fintype P] (xs : List P) : Prop :=
  xs.toFinset = Finset.univ ∧ xs.Nodup ∧
    xs.Pairwise (fun x y => ¬ y < x)

theorem complete_legal_iff_linearExtension [Fintype P] (xs : List P) :
    (Legal ∅ xs ∧ xs.toFinset = Finset.univ) ↔ LinearExtension xs := by
  constructor
  · rintro ⟨hl,hc⟩
    exact ⟨hc,legal_nodup hl,legal_topological hl⟩
  · rintro ⟨hc,hn,ho⟩
    refine ⟨legal_of_topological ideal_empty hn (by simp) ?_ ho,hc⟩
    rw [hc, Finset.empty_union]
    intro x _ y _
    exact Finset.mem_univ y

/-- Every ordering of a ready batch is legal, provided tasks occur only once. -/
theorem legal_of_all_ready {K : Finset P} {xs : List P}
    (hn : xs.Nodup) (hr : ∀ x ∈ xs, Ready K x) : Legal K xs := by
  induction xs generalizing K with
  | nil => exact legal_nil K
  | cons x xs ih =>
    obtain ⟨hnx,hnt⟩ := List.nodup_cons.mp hn
    refine ⟨hr x (by simp),ih hnt ?_⟩
    intro y hy
    apply ready_persists (hr y (List.mem_cons_of_mem x hy))
    intro heq
    subst y
    exact hnx hy

theorem frontier_batch_serializable [Fintype P] {K B : Finset P} {xs : List P}
    (hB : B ⊆ frontier K) (hn : xs.Nodup) (he : xs.toFinset = B) :
    Legal K xs := by
  apply legal_of_all_ready hn
  intro x hx
  apply mem_frontier.mp
  apply hB
  rw [← he]
  exact List.mem_toFinset.mpr hx

theorem legal_append_iff (K : Finset P) (xs ys : List P) :
    Legal K (xs ++ ys) ↔ Legal K xs ∧ Legal (K ∪ xs.toFinset) ys := by
  induction xs generalizing K with
  | nil => simp [Legal]
  | cons x xs ih =>
    simp only [List.cons_append, legal_cons, ih, List.toFinset_cons,
      Finset.union_insert, Finset.insert_union, and_assoc]

/-- The minimum remaining task exists in every nonempty finite residual. -/
theorem frontier_nonempty [Fintype P] {K : Finset P} (hne : K ≠ Finset.univ) :
    (frontier K).Nonempty := by
  classical
  have hres : (Finset.univ \ K).Nonempty := by
    by_contra hn
    apply hne
    apply Finset.eq_univ_of_forall
    intro x
    by_contra hx
    exact hn ⟨x,by simp [hx]⟩
  obtain ⟨x,hxmin⟩ := Finset.exists_minimal hres
  refine ⟨x,mem_frontier.mpr ⟨(Finset.mem_sdiff.mp hxmin.1).2, ?_⟩⟩
  intro y hy
  by_contra hyk
  have hyres : y ∈ Finset.univ \ K := by simp [hyk]
  have hxy : x ≤ y := hxmin.2 hyres (le_of_lt hy)
  exact (not_le_of_gt hy) hxy

omit [PartialOrder P] in
theorem remaining_strictly_decreases [Fintype P] {K : Finset P} {x : P}
    (hx : x ∉ K) :
    (Finset.univ \ insert x K).card < (Finset.univ \ K).card := by
  have he : (Finset.univ \ insert x K) = (Finset.univ \ K).erase x := by
    ext y
    simp
  rw [he]
  exact Finset.card_erase_lt_of_mem (by simp [hx])

/-- Every ideal has a finite structural completion. This does not assert that
all those tasks are actually provable or solvable. -/
theorem exists_legal_completion [Fintype P] (K : Finset P) (hK : IsIdeal K) :
    ∃ xs : List P, Legal K xs ∧ K ∪ xs.toFinset = Finset.univ := by
  classical
  have aux : ∀ n : Nat, ∀ K : Finset P, (Finset.univ \ K).card = n → IsIdeal K →
      ∃ xs : List P, Legal K xs ∧ K ∪ xs.toFinset = Finset.univ := by
    intro n
    induction n using Nat.strong_induction_on with
    | h n ih =>
      intro K hcard hideal
      by_cases hdone : K = Finset.univ
      · exact ⟨[],legal_nil K,by simpa using hdone⟩
      · obtain ⟨x,hxf⟩ := frontier_nonempty hdone
        have hx := mem_frontier.mp hxf
        have hlt : (Finset.univ \ insert x K).card < n := by
          rw [← hcard]
          exact remaining_strictly_decreases hx.1
        obtain ⟨xs,hxs,hend⟩ := ih _ hlt (insert x K) rfl (ideal_insert hideal hx)
        refine ⟨x::xs,⟨hx,hxs⟩,?_⟩
        simpa [List.toFinset_cons,Finset.union_insert,Finset.insert_union] using hend
  exact aux _ K rfl hK

theorem exists_linearExtension [Fintype P] : ∃ xs : List P, LinearExtension xs := by
  obtain ⟨xs,hlegal,hend⟩ := exists_legal_completion (∅ : Finset P) ideal_empty
  exact ⟨xs,(complete_legal_iff_linearExtension xs).mp ⟨hlegal,by simpa using hend⟩⟩

theorem completed_card_add {K : Finset P} {xs : List P} (hl : Legal K xs) :
    (K ∪ xs.toFinset).card = K.card + xs.length := by
  have hd : Disjoint K xs.toFinset := by
    apply Finset.disjoint_left.mpr
    intro x hx hxlist
    exact legal_fresh hl x (List.mem_toFinset.mp hxlist) hx
  rw [Finset.card_union_of_disjoint hd, List.toFinset_card_of_nodup (legal_nodup hl)]

theorem legal_completion_length [Fintype P] {K : Finset P} {xs : List P}
    (hl : Legal K xs) (hc : K ∪ xs.toFinset = Finset.univ) :
    xs.length = Fintype.card P - K.card := by
  have h := completed_card_add hl
  rw [hc, Finset.card_univ] at h
  omega

end Komorebi.AVOC.Scheduling
