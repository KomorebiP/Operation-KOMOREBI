import Mathlib.Data.Finset.Card
import Mathlib.Data.Fintype.Powerset
import Mathlib.Data.Int.Basic

/-! # A finite, declared dependency graph and its exact forward invalidation

Artifact values are heterogeneous and compared on the actual direct-input restriction.
The closure algorithm does not assume acyclicity. A rank certificate is used separately
for sound reuse and topological restoration, not as a substitute for declared inputs.
-/
namespace Komorebi.MachineTheory.Dependency
open Finset

variable {V I : Type*} [Fintype V] [DecidableEq V]

structure Graph (V I : Type*) where
  parents : V → Finset V
  direct : V → Finset I

/-- An explicitly checkable topological rank is a certificate of acyclicity. -/
def Graph.Ranked (G : Graph V I) (rank : V → ℕ) : Prop :=
  ∀ v u, u ∈ G.parents v → rank u < rank v

/-- One synchronous forward propagation, including the old affected set. -/
def expand (parents : V → Finset V) (S : Finset V) : Finset V :=
  S ∪ univ.filter (fun v => ∃ u ∈ parents v, u ∈ S)

def stages (parents : V → Finset V) (seed : Finset V) : ℕ → Finset V
  | 0 => seed
  | n+1 => expand parents (stages parents seed n)

@[simp] theorem mem_expand (parents : V → Finset V) (S : Finset V) (v : V) :
    v ∈ expand parents S ↔ v ∈ S ∨ ∃ u ∈ parents v, u ∈ S := by
  simp [expand]

theorem subset_expand (parents : V → Finset V) (S : Finset V) : S ⊆ expand parents S := by
  intro v hv
  exact (mem_expand parents S v).mpr (Or.inl hv)

theorem expand_mono (parents : V → Finset V) {S T : Finset V} (h : S ⊆ T) :
    expand parents S ⊆ expand parents T := by
  intro v hv
  rcases (mem_expand parents S v).mp hv with hv | ⟨u,hu,hs⟩
  · exact (mem_expand parents T v).mpr (Or.inl (h hv))
  · exact (mem_expand parents T v).mpr (Or.inr ⟨u,hu,h hs⟩)

theorem stages_step (parents : V → Finset V) (seed : Finset V) (n : ℕ) :
    stages parents seed n ⊆ stages parents seed (n+1) := subset_expand parents _

theorem seed_subset_stages (parents : V → Finset V) (seed : Finset V) (n : ℕ) :
    seed ⊆ stages parents seed n := by
  induction n with
  | zero => exact Subset.refl _
  | succ n ih => exact Subset.trans ih (stages_step parents seed n)

theorem bounded_stabilization (parents : V → Finset V) (seed : Finset V) :
    ∃ n ≤ Fintype.card V - seed.card,
      expand parents (stages parents seed n) = stages parents seed n := by
  by_contra h
  push Not at h
  let b := Fintype.card V - seed.card
  have growth : ∀ n, n ≤ b+1 → seed.card+n ≤ (stages parents seed n).card := by
    intro n
    induction n with
    | zero => intro _; simp [stages]
    | succ n ih =>
      intro hn
      have hn' : n ≤ b := by omega
      have hh := h n hn'
      have sub := stages_step parents seed n
      have strict : (stages parents seed n).card < (stages parents seed (n+1)).card := by
        by_contra hc
        have eq := Finset.eq_of_subset_of_card_le sub (by omega)
        exact hh eq.symm
      have previous := ih (by omega)
      omega
  have impossible := growth (b+1) le_rfl
  have top := Finset.card_le_univ (stages parents seed (b+1))
  have start := Finset.card_le_univ seed
  dsimp [b] at impossible top
  omega

theorem stable_tail (parents : V → Finset V) (seed : Finset V) (n : ℕ)
    (hs : expand parents (stages parents seed n) = stages parents seed n) :
    ∀ k, stages parents seed (n+k) = stages parents seed n := by
  intro k
  induction k with
  | zero => simp
  | succ k ih =>
    change expand parents (stages parents seed (n+k)) = _
    rw [ih,hs]

/-- A fixed number of rounds, with no chosen stopping index or reachability oracle. -/
def closure (parents : V → Finset V) (seed : Finset V) : Finset V :=
  stages parents seed (Fintype.card V)

theorem closure_stable (parents : V → Finset V) (seed : Finset V) :
    expand parents (closure parents seed) = closure parents seed := by
  obtain ⟨n,hn,hs⟩ := bounded_stabilization parents seed
  have hn' : n ≤ Fintype.card V := le_trans hn (Nat.sub_le _ _)
  have eq : closure parents seed = stages parents seed n := by
    simpa [closure,Nat.add_sub_of_le hn'] using stable_tail parents seed n hs (Fintype.card V-n)
  rw [eq,hs]

theorem seed_subset_closure (parents : V → Finset V) (seed : Finset V) :
    seed ⊆ closure parents seed := seed_subset_stages parents seed _

theorem closure_parent (parents : V → Finset V) (seed : Finset V) {u v : V}
    (hu : u ∈ closure parents seed) (hp : u ∈ parents v) : v ∈ closure parents seed := by
  rw [← closure_stable parents seed]
  exact (mem_expand parents _ v).mpr (Or.inr ⟨u,hp,hu⟩)

theorem closure_least (parents : V → Finset V) (seed T : Finset V)
    (hseed : seed ⊆ T) (hclosed : ∀ v u, u ∈ parents v → u ∈ T → v ∈ T) :
    closure parents seed ⊆ T := by
  have step : ∀ n, stages parents seed n ⊆ T := by
    intro n
    induction n with
    | zero => exact hseed
    | succ n ih =>
      intro v hv
      rcases (mem_expand parents _ v).mp hv with hv | ⟨u,hp,hu⟩
      · exact ih hv
      · exact hclosed v u hp (ih hu)
  exact step _

/-- Semantic forward paths from a changed direct-input vertex. -/
inductive Reach (parents : V → Finset V) (seed : Finset V) : V → Prop
  | root (v) : v ∈ seed → Reach parents seed v
  | edge {u v} : Reach parents seed u → u ∈ parents v → Reach parents seed v

theorem closure_iff_reach (parents : V → Finset V) (seed : Finset V) (v : V) :
    v ∈ closure parents seed ↔ Reach parents seed v := by
  constructor
  · have all : ∀ n v, v ∈ stages parents seed n → Reach parents seed v := by
      intro n
      induction n with
      | zero => intro v hv; exact Reach.root v hv
      | succ n ih =>
        intro v hv
        rcases (mem_expand parents _ v).mp hv with hv | ⟨u,hp,hu⟩
        · exact ih v hv
        · exact Reach.edge (ih u hu) hp
    exact all _ v
  · intro h
    induction h with
    | root v hv => exact seed_subset_closure parents seed hv
    | edge _ hp ih => exact closure_parent parents seed ih hp

theorem closure_mono (parents : V → Finset V) {S T : Finset V} (h : S ⊆ T) :
    closure parents S ⊆ closure parents T :=
  closure_least parents S _ (Subset.trans h (seed_subset_closure parents T))
    (fun _ _ hp hu => closure_parent parents T hu hp)

theorem no_stale_parent (parents : V → Finset V) (seed : Finset V) {v : V}
    (hv : v ∉ closure parents seed) {u : V} (hu : u ∈ parents v) :
    u ∉ closure parents seed := fun hs => hv (closure_parent parents seed hs hu)

variable {A : I → Type*} [∀ i, DecidableEq (A i)]

/-- The actual values visible to this local witness checker. -/
def Graph.view (G : Graph V I) (a : ∀ i, A i) (v : V) :
    (i : {i // i ∈ G.direct v}) → A i.val := fun i => a i.val

def Graph.changedRoots (G : Graph V I) (a b : ∀ i, A i) : Finset V :=
  univ.filter (fun v => ∃ i ∈ G.direct v, a i ≠ b i)

def Graph.stale (G : Graph V I) (a b : ∀ i, A i) : Finset V :=
  closure G.parents (G.changedRoots a b)

omit [DecidableEq V] in
@[simp] theorem Graph.mem_changedRoots (G : Graph V I) (a b : ∀ i, A i) (v : V) :
    v ∈ G.changedRoots a b ↔ ∃ i ∈ G.direct v, a i ≠ b i := by simp [changedRoots]

theorem Graph.nonstale_view (G : Graph V I) (a b : ∀ i, A i) {v : V}
    (hv : v ∉ G.stale a b) : G.view a v = G.view b v := by
  funext i
  by_contra he
  apply hv
  apply seed_subset_closure G.parents (G.changedRoots a b)
  exact (G.mem_changedRoots a b v).mpr ⟨i.val,i.property,he⟩

theorem Graph.nonstale_parents (G : Graph V I) (a b : ∀ i, A i) {v : V}
    (hv : v ∉ G.stale a b) {u : V} (hu : u ∈ G.parents v) : u ∉ G.stale a b :=
  no_stale_parent G.parents (G.changedRoots a b) hv hu

theorem Graph.stale_iff (G : Graph V I) (a b : ∀ i, A i) (v : V) :
    v ∈ G.stale a b ↔ Reach G.parents (G.changedRoots a b) v :=
  closure_iff_reach _ _ _

theorem Graph.same_state_not_stale (G : Graph V I) (a : ∀ i, A i) : G.stale a a = ∅ := by
  apply Finset.Subset.antisymm ?_ (Finset.empty_subset _)
  exact closure_least G.parents (G.changedRoots a a) ∅
    (by simp [changedRoots]) (by simp)

end Komorebi.MachineTheory.Dependency
