import MachineTheory.DependencyGraph

/-! # Selective certificate reuse

The checker receives only a typed restriction of the actual artifact state.
`Complete` is an explicit semantic locality obligation, not a hash property.
Old witnesses carry established old claims. New external premises remain explicit.
-/
namespace Komorebi.MachineTheory.Dependency
open Finset
variable {V I : Type*} [Fintype V] [DecidableEq V]
variable {A : I → Type*} [∀ i, DecidableEq (A i)] {W : V → Type*}

structure System (G : Graph V I) (A : I → Type*) (W : V → Type*) where
  claim : (∀ i, A i) → V → Prop
  external : (∀ i, A i) → V → Prop
  check : (v : V) → ((i : {i // i ∈ G.direct v}) → A i.val) → W v → Bool
  sound : ∀ a v w, check v (G.view a v) w = true → external a v →
    (∀ u ∈ G.parents v, claim a u) → claim a v

variable {G : Graph V I} (S : System G A W)

/-- Semantic completeness for the declared restriction and parent claims.
It is a proof obligation supplied by an instance, not automatically inferred. -/
def System.Complete : Prop :=
  ∀ a b v, G.view a v = G.view b v →
    (∀ u ∈ G.parents v, S.claim a u ↔ S.claim b u) →
    (S.external a v ↔ S.external b v) → (S.claim a v ↔ S.claim b v)

def System.Established (a : ∀ i, A i) (v : V) (w : W v) : Prop :=
  S.check v (G.view a v) w = true ∧ S.external a v ∧ S.claim a v

/-- Outside the exact forward closure, the full claim meaning is preserved.
The induction uses the checked topological rank and all parent meanings. -/
theorem System.nonstale_meaning (complete : S.Complete)
    (rank : V → ℕ) (ordered : G.Ranked rank)
    (a b : ∀ i, A i)
    (external : ∀ v, v ∉ G.stale a b → (S.external a v ↔ S.external b v))
    (v : V) (hv : v ∉ G.stale a b) : S.claim a v ↔ S.claim b v := by
  have go : ∀ n v, rank v = n → v ∉ G.stale a b → (S.claim a v ↔ S.claim b v) := by
    intro n
    induction n using Nat.strong_induction_on with
    | h n ih =>
      intro v hn hclean
      apply complete a b v (G.nonstale_view a b hclean)
      · intro u hu
        exact ih (rank u) (by rw [← hn]; exact ordered v u hu) u rfl
          (G.nonstale_parents a b hclean hu)
      · exact external v hclean
  exact go (rank v) v rfl hv

/-- Core 7.1, reuse direction. Equal names or digests do not appear as premises. -/
theorem System.selective_reuse (complete : S.Complete)
    (rank : V → ℕ) (ordered : G.Ranked rank)
    (a b : ∀ i, A i) (old : ∀ v, W v)
    (previously_established : ∀ v, S.Established a v (old v))
    (external_now : ∀ v, v ∉ G.stale a b → S.external b v) :
    ∀ v, v ∉ G.stale a b → S.Established b v (old v) := by
  intro v hv
  obtain ⟨hc,he,hp⟩ := previously_established v
  refine ⟨?_,external_now v hv,?_⟩
  · rw [← G.nonstale_view a b hv]
    exact hc
  · have hm := S.nonstale_meaning complete rank ordered a b
      (fun u hu => ⟨fun _ => external_now u hu,fun _ => (previously_established u).2.1⟩) v hv
    exact hm.mp hp

omit [Fintype V] [DecidableEq V] [∀ i, DecidableEq (A i)] in
/-- This local restoration rule consumes actual revised parents and external premises. -/
theorem System.restore (b : ∀ i, A i) (v : V) (w : W v)
    (checked : S.check v (G.view b v) w = true) (he : S.external b v)
    (parents : ∀ u ∈ G.parents v, S.claim b u) : S.Established b v w :=
  ⟨checked,he,S.sound b v w checked he parents⟩

/-- A checker's equality is obtained from its actual restricted input. -/
theorem System.check_unchanged (a b : ∀ i, A i) (v : V) (w : W v)
    (hv : v ∉ G.stale a b) : S.check v (G.view a v) w = S.check v (G.view b v) w := by
  rw [G.nonstale_view a b hv]

end Komorebi.MachineTheory.Dependency
