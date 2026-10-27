import KomorebiPaperV.FiniteAdaptive

/-!
Author: Komorebi P.
Set-valued prunings use node identities, not potentially repeated node labels.
Completeness means exactly one selected node on every terminal path. This is
proved equivalent to the manuscript's covering antichain definition and to
recursive cuts, for arbitrary positive finite branching.
-/

namespace KomorebiPaperV.CompletePrunings
open KomorebiPaperV.FiniteAdaptive

variable {A : Type*}

inductive Node : FiniteAdaptive.Tree A → Type _ where
  | root (t : FiniteAdaptive.Tree A) : Node t
  | down {a : A} {n : ℕ} {children : Fin (n + 1) → FiniteAdaptive.Tree A}
      (i : Fin (n + 1)) : Node (children i) → Node (.branch a n children)

inductive OnPath : {t : FiniteAdaptive.Tree A} → Node t → Terminal t → Prop where
  | root {t : FiniteAdaptive.Tree A} (p : Terminal t) : OnPath (.root t) p
  | down {a : A} {n : ℕ} {children : Fin (n + 1) → FiniteAdaptive.Tree A}
      {i : Fin (n + 1)} {v : Node (children i)} {p : Terminal (children i)} :
      OnPath v p → OnPath (t := .branch a n children) (.down i v) (.down i p)

inductive Selected : {t : FiniteAdaptive.Tree A} → Cut t → Node t → Prop where
  | stop (t : FiniteAdaptive.Tree A) : Selected (.stop t) (.root t)
  | split {a : A} {n : ℕ} {children : Fin (n + 1) → FiniteAdaptive.Tree A}
      {q : ∀ i, Cut (children i)} {i : Fin (n + 1)} {v : Node (children i)} :
      Selected (q i) v → Selected (t := .branch a n children) (.split q) (.down i v)

def Complete {t : FiniteAdaptive.Tree A} (S : Set (Node t)) : Prop :=
  ∀ p : Terminal t, ∃! v : Node t, OnPath v p ∧ v ∈ S

theorem terminal_exists (t : FiniteAdaptive.Tree A) : Nonempty (Terminal t) := by
  induction t with
  | leaf a => exact ⟨.here⟩
  | branch a n children ih =>
    obtain ⟨p⟩ := ih 0
    exact ⟨.down 0 p⟩

theorem node_on_terminal {t : FiniteAdaptive.Tree A} (v : Node t) : ∃ p : Terminal t, OnPath v p := by
  induction v with
  | root t =>
    obtain ⟨p⟩ := terminal_exists t
    exact ⟨p, .root p⟩
  | down i v ih =>
    obtain ⟨p, hp⟩ := ih
    exact ⟨.down i p, .down hp⟩

theorem selected_stop_iff {t : FiniteAdaptive.Tree A} (v : Node t) :
    Selected (.stop t) v ↔ v = .root t := by
  constructor
  · intro h; cases h; rfl
  · rintro rfl; exact .stop t

theorem selected_split_root_false {a : A} {n : ℕ} {children : Fin (n + 1) → FiniteAdaptive.Tree A}
    (q : ∀ i, Cut (children i)) : ¬Selected (t := .branch a n children) (.split q) (.root _) := by
  intro h; cases h

theorem selected_split_down_iff {a : A} {n : ℕ} {children : Fin (n + 1) → FiniteAdaptive.Tree A}
    (q : ∀ i, Cut (children i)) (i : Fin (n + 1)) (v : Node (children i)) :
    Selected (t := .branch a n children) (.split q) (.down i v) ↔ Selected (q i) v := by
  constructor
  · intro h; cases h with | split h => exact h
  · exact Selected.split

theorem cut_complete {t : FiniteAdaptive.Tree A} (q : Cut t) : Complete {v | Selected q v} := by
  induction q with
  | stop t =>
    intro p
    refine ⟨.root t, ⟨.root p, .stop t⟩, ?_⟩
    intro v hv
    exact (selected_stop_iff v).mp hv.2
  | @split a n children q ih =>
    intro p
    cases p with
    | down i p =>
      obtain ⟨v, hv, hu⟩ := ih i p
      refine ⟨.down i v, ⟨.down hv.1, .split hv.2⟩, ?_⟩
      intro w hw
      cases hw.1 with
      | root p => exact False.elim (selected_split_root_false q hw.2)
      | down hp =>
        have he := hu _ ⟨hp, (selected_split_down_iff q _ _).mp hw.2⟩
        cases he
        rfl

/-- Literal rooted-tree ancestry, including equality. -/
inductive Ancestor : {t : FiniteAdaptive.Tree A} → Node t → Node t → Prop where
  | root {t : FiniteAdaptive.Tree A} (v : Node t) : Ancestor (.root t) v
  | down {a : A} {n : ℕ} {children : Fin (n + 1) → FiniteAdaptive.Tree A}
      {i : Fin (n + 1)} {u v : Node (children i)} :
      Ancestor u v → Ancestor (t := .branch a n children) (.down i u) (.down i v)

theorem ancestor_onPath {t : FiniteAdaptive.Tree A} {u v : Node t} (h : Ancestor u v)
    {p : Terminal t} (hp : OnPath v p) : OnPath u p := by
  induction h with
  | root v => exact .root p
  | down h ih =>
    cases hp with | down hp => exact .down (ih hp)

def CoveringAntichain {t : FiniteAdaptive.Tree A} (S : Set (Node t)) : Prop :=
  (∀ p : Terminal t, ∃ v ∈ S, OnPath v p) ∧
  (∀ u ∈ S, ∀ v ∈ S, Ancestor u v → u = v)

theorem path_nodes_comparable {t : FiniteAdaptive.Tree A} {u v : Node t} {p : Terminal t}
    (hu : OnPath u p) (hv : OnPath v p) : Ancestor u v ∨ Ancestor v u := by
  induction hu with
  | root p => exact Or.inl (.root _)
  | @down a n children i u p hu ih =>
    cases hv with
    | root p => exact Or.inr (.root _)
    | down hv =>
      rcases ih hv with h | h
      · exact Or.inl (.down h)
      · exact Or.inr (.down h)

theorem complete_iff_covering_antichain {t : FiniteAdaptive.Tree A} (S : Set (Node t)) :
    Complete S ↔ CoveringAntichain S := by
  constructor
  · intro h
    constructor
    · intro p
      obtain ⟨v, hv, _⟩ := h p
      exact ⟨v, hv.2, hv.1⟩
    · intro u hu v hv huv
      obtain ⟨p, hp⟩ := node_on_terminal v
      obtain ⟨w, _, hw⟩ := h p
      exact (hw u ⟨ancestor_onPath huv hp, hu⟩).trans (hw v ⟨hp, hv⟩).symm
  · rintro ⟨hcover, hanti⟩ p
    obtain ⟨v, hv, hp⟩ := hcover p
    refine ⟨v, ⟨hp, hv⟩, ?_⟩
    intro u hu
    rcases path_nodes_comparable hu.1 hp with h | h
    · exact hanti u hu.2 v hv h
    · exact (hanti v hv u hu.2 h).symm

theorem complete_root_unique {t : FiniteAdaptive.Tree A} (S : Set (Node t)) (h : Complete S)
    (hr : Node.root t ∈ S) (v : Node t) : v ∈ S ↔ v = .root t := by
  constructor
  · intro hv
    obtain ⟨p, hp⟩ := node_on_terminal v
    obtain ⟨w, _, hw⟩ := h p
    exact (hw v ⟨hp, hv⟩).trans (hw (.root t) ⟨.root p, hr⟩).symm
  · rintro rfl; exact hr

theorem complete_child {a : A} {n : ℕ} {children : Fin (n + 1) → FiniteAdaptive.Tree A}
    (S : Set (Node (.branch a n children))) (h : Complete S)
    (hr : Node.root _ ∉ S) (i : Fin (n + 1)) :
    Complete {v | Node.down i v ∈ S} := by
  intro p
  obtain ⟨v, hv, hu⟩ := h (.down i p)
  cases hv.1 with
  | root p => exact False.elim (hr hv.2)
  | @down _ _ _ _ v _ hp =>
    refine ⟨v, ⟨hp, hv.2⟩, ?_⟩
    intro w hw
    have he := hu (.down i w) ⟨.down hw.1, hw.2⟩
    cases he
    rfl

theorem complete_has_cut (t : FiniteAdaptive.Tree A) (S : Set (Node t)) (h : Complete S) :
    ∃ q : Cut t, ∀ v : Node t, Selected q v ↔ v ∈ S := by
  classical
  induction t with
  | leaf a =>
    refine ⟨.stop _, ?_⟩
    intro v
    cases v with
    | root t =>
      have hroot : Node.root (.leaf a) ∈ S := by
        obtain ⟨w, hw, _⟩ := h .here
        cases w
        exact hw.2
      simp [selected_stop_iff, hroot]
  | branch a n children ih =>
    by_cases hr : Node.root (.branch a n children) ∈ S
    · exact ⟨.stop _, fun v => (selected_stop_iff v).trans
        (complete_root_unique S h hr v).symm⟩
    · have hex : ∀ i, ∃ q : Cut (children i), ∀ v,
          Selected q v ↔ Node.down i v ∈ S :=
        fun i => ih i _ (complete_child S h hr i)
      choose q hq using hex
      refine ⟨.split q, ?_⟩
      intro v
      cases v with
      | root t => simp [selected_split_root_false, hr]
      | down i v => exact (selected_split_down_iff q i v).trans (hq i v)

theorem cut_ext (t : FiniteAdaptive.Tree A) (q r : Cut t)
    (h : ∀ v, Selected q v ↔ Selected r v) : q = r := by
  induction q with
  | stop t =>
    cases r with
    | stop t => rfl
    | split r =>
      exact False.elim (selected_split_root_false r ((h (.root _)).mp (.stop _)))
  | @split a n children q ih =>
    cases r with
    | stop t =>
      exact False.elim (selected_split_root_false q ((h (.root _)).mpr (.stop _)))
    | split r =>
      have he : q = r := by
        funext i
        apply ih i (r i)
        intro v
        exact (selected_split_down_iff q i v).symm.trans
          ((h (.down i v)).trans (selected_split_down_iff r i v))
      cases he
      rfl

noncomputable def pruningEquiv (t : FiniteAdaptive.Tree A) :
    Cut t ≃ {S : Set (Node t) // Complete S} where
  toFun q := ⟨{v | Selected q v}, cut_complete q⟩
  invFun S := (complete_has_cut t S.1 S.2).choose
  left_inv q := by
    apply cut_ext
    exact (complete_has_cut t _ (cut_complete q)).choose_spec
  right_inv S := by
    apply Subtype.ext
    ext v
    exact (complete_has_cut t S.1 S.2).choose_spec v

theorem complete_pruning_finite (t : FiniteAdaptive.Tree A) :
    Finite {S : Set (Node t) // Complete S} :=
  Finite.of_equiv (Cut t) (pruningEquiv t)

theorem complete_pruning_minimum (t : FiniteAdaptive.Tree A)
    (J : {S : Set (Node t) // Complete S} → ℝ) :
    ∃ S, ∀ T, J S ≤ J T := by
  obtain ⟨q, hq⟩ := arbitrary_objective_minimum t (J ∘ pruningEquiv t)
  refine ⟨pruningEquiv t q, ?_⟩
  intro S
  simpa only [Function.comp_def, (pruningEquiv t).apply_symm_apply] using
    hq ((pruningEquiv t).symm S)

end KomorebiPaperV.CompletePrunings
