module
public import Mathlib.Data.Finset.Lattice.Fold
public import Mathlib.Data.Finset.Card
public import Mathlib.Logic.Relation
public import Mathlib.Tactic

/-!
Author: Komorebi P.
Paper VIII 6.6 and 10.3. Acyclicity means no nonempty directed cycle.
The level function is constructed from this hypothesis, not supplied as a
certificate. Tasks have unit duration and unrestricted parallelism. The empty
graph has depth zero, and zero-edge paths are included.
-/
public section
set_option autoImplicit false
namespace KomorebiPaperVIII
namespace DAG
open scoped BigOperators
variable {V : Type*} [Fintype V]

structure Graph (V : Type*) where
  edge : V → V → Prop
  acyclic : ∀ v, ¬ Relation.TransGen edge v v

variable (G : Graph V)

noncomputable def ancestors (v : V) : Finset V := by
  classical
  exact Finset.univ.filter (fun u => Relation.TransGen G.edge u v)

theorem mem_ancestors (u v : V) :
    u ∈ G.ancestors v ↔ Relation.TransGen G.edge u v := by
  classical
  simp [ancestors]

theorem ancestors_strict {u v : V} (h : G.edge u v) :
    G.ancestors u ⊂ G.ancestors v := by
  classical
  apply Finset.ssubset_iff_subset_ne.mpr
  constructor
  · intro a ha
    exact (G.mem_ancestors a v).2
      (((G.mem_ancestors a u).1 ha).trans (Relation.TransGen.single h))
  · intro he
    have hm : u ∈ G.ancestors u := by
      rw [he]
      exact (G.mem_ancestors u v).2 (Relation.TransGen.single h)
    exact G.acyclic u ((G.mem_ancestors u u).1 hm)

theorem ancestors_card_lt {u v : V} (h : G.edge u v) :
    (G.ancestors u).card < (G.ancestors v).card :=
  Finset.card_lt_card (G.ancestors_strict h)

theorem wellFounded : WellFounded G.edge :=
  Subrelation.wf (fun _ _ h => G.ancestors_card_lt h)
    (measure (fun v => (G.ancestors v).card)).wf

noncomputable def level : V → ℕ := by
  classical
  exact G.wellFounded.fix (fun v f =>
    1 + Finset.univ.sup (fun u : {u // G.edge u v} => f u.val u.property))

theorem level_eq (v : V) :
    G.level v = 1 + Finset.univ.sup (fun u : {u // G.edge u v} => G.level u.val) := by
  classical
  exact WellFounded.fix_eq G.wellFounded _ v

theorem level_positive (v : V) : 0 < G.level v := by
  classical
  rw [G.level_eq]
  omega

theorem edge_level {u v : V} (h : G.edge u v) : G.level u < G.level v := by
  classical
  have hm := Finset.le_sup (f := fun w : {u // G.edge u v} => G.level w.val)
    (Finset.mem_univ (⟨u,h⟩ : {u // G.edge u v}))
  rw [G.level_eq v]
  omega

/-- Paths are oriented source a to target b and record their edge count. -/
def Path : ℕ → V → V → Prop
  | 0, b, a => b = a
  | n+1, b, a => ∃ c, G.edge c b ∧ Path n c a

theorem path_level_bound (n : ℕ) (b a : V) (h : G.Path n b a) :
    G.level a + n ≤ G.level b := by
  induction n generalizing b a with
  | zero =>
    have hab : b = a := h
    subst b
    omega
  | succ n ih =>
    obtain ⟨c,hc,hp⟩ := h
    have h1 := ih c a hp
    have h2 := G.edge_level hc
    omega

/-- Every level is witnessed by an actual directed path, not only an upper bound. -/
theorem level_attained (v : V) :
    ∃ n a, G.Path n v a ∧ G.level v = n+1 := by
  classical
  induction v using G.wellFounded.induction with
  | h v ih =>
    by_cases hp : ∃ u, G.edge u v
    · letI : Nonempty {u // G.edge u v} := by
        obtain ⟨u,hu⟩ := hp
        exact ⟨⟨u,hu⟩⟩
      obtain ⟨u,_,hu⟩ := Finset.exists_mem_eq_sup
        (Finset.univ : Finset {u // G.edge u v}) Finset.univ_nonempty
        (fun u => G.level u.val)
      obtain ⟨n,a,hpath,hn⟩ := ih u.val u.property
      refine ⟨n+1,a,⟨u.val,u.property,hpath⟩,?_⟩
      rw [G.level_eq,hu,hn]
      omega
    · haveI : IsEmpty {u // G.edge u v} := ⟨fun u => hp ⟨u.val,u.property⟩⟩
      exact ⟨0,v,rfl,by simp [G.level_eq]⟩

/-- Stages are positive integers; zero denotes that no task has run yet. -/
def ValidSchedule (s : V → ℕ) : Prop :=
  (∀ v, 0 < s v) ∧ ∀ u v, G.edge u v → s u < s v

theorem level_valid : G.ValidSchedule G.level :=
  ⟨G.level_positive,fun _ _ h => G.edge_level h⟩

theorem level_minimal (s : V → ℕ) (hs : G.ValidSchedule s) (v : V) :
    G.level v ≤ s v := by
  classical
  induction v using G.wellFounded.induction with
  | h v ih =>
    rw [G.level_eq]
    have hm : Finset.univ.sup (fun u : {u // G.edge u v} => G.level u.val) ≤ s v - 1 := by
      apply Finset.sup_le
      intro u _
      have h1 := ih u.val u.property
      have h2 := hs.2 u.val v u.property
      omega
    have hpos := hs.1 v
    omega

noncomputable def depth : ℕ := Finset.univ.sup G.level

theorem level_le_depth (v : V) : G.level v ≤ G.depth :=
  Finset.le_sup (Finset.mem_univ v)

/-- Item 10.3: a constructed schedule achieves the least possible stage count. -/
theorem optimal_depth (s : V → ℕ) (hs : G.ValidSchedule s) :
    G.depth ≤ Finset.univ.sup s := by
  classical
  exact Finset.sup_le (fun v _ => (G.level_minimal s hs v).trans
    (Finset.le_sup (Finset.mem_univ v)))

theorem path_length_le_depth (n : ℕ) (b a : V) (h : G.Path n b a) :
    n+1 ≤ G.depth := by
  have h1 := G.path_level_bound n b a h
  have h2 := G.level_positive a
  have h3 := G.level_le_depth b
  omega

/-- Item 6.6: for nonempty graphs, depth is one plus the longest edge-path length. -/
theorem depth_attained [Nonempty V] :
    ∃ n b a, G.Path n b a ∧ G.depth = n+1 ∧
      ∀ m c d, G.Path m c d → m ≤ n := by
  classical
  obtain ⟨b,_,hb⟩ := Finset.exists_mem_eq_sup (Finset.univ : Finset V)
    Finset.univ_nonempty G.level
  obtain ⟨n,a,hp,hn⟩ := G.level_attained b
  refine ⟨n,b,a,hp,hb.trans hn,?_⟩
  intro m c d hm
  have hbound := G.path_length_le_depth m c d hm
  change G.depth = G.level b at hb
  omega

theorem empty_depth [IsEmpty V] : G.depth = 0 := by
  classical
  simp [depth]

theorem same_level_independent {u v : V} (h : G.level u = G.level v) :
    ¬ G.edge u v ∧ ¬ G.edge v u := by
  constructor <;> intro he
  · have := G.edge_level he; omega
  · have := G.edge_level he; omega

end DAG
end KomorebiPaperVIII
