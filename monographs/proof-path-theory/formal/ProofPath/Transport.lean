import ProofPath.Extension

/-!
An explicit interpretation contract between declared rule fields.
It transports actual inductive derivations and pulls target models back.
-/
namespace ProofPath
variable {ι κ ν J K M : Type*}

structure RuleTransport (F : Field ι J) (G : Field κ K) where
  node : ι → κ
  rule : J → K
  leaves : ∀ v, v ∈ F.leaf → node v ∈ G.leaf
  certified : ∀ j, F.certified j → G.certified (rule j)
  premises : ∀ j w, w ∈ G.premises (rule j) → ∃ v, v ∈ F.premises j ∧ node v = w
  conclusion : ∀ j, node (F.conclusion j) = G.conclusion (rule j)

namespace RuleTransport
variable {F : Field ι J} {G : Field κ K} {H : Field ν M}

def identity (F : Field ι J) : RuleTransport F F where
  node := id
  rule := id
  leaves := fun _ h => h
  certified := fun _ h => h
  premises := fun _ w h => ⟨w, h, rfl⟩
  conclusion := fun _ => rfl

def comp (a : RuleTransport F G) (b : RuleTransport G H) : RuleTransport F H where
  node := b.node ∘ a.node
  rule := b.rule ∘ a.rule
  leaves := fun v h => b.leaves _ (a.leaves v h)
  certified := fun j h => b.certified _ (a.certified j h)
  premises := by
    intro j w hw
    obtain ⟨u, hu, he⟩ := b.premises (a.rule j) w hw
    obtain ⟨v, hv, hvu⟩ := a.premises j u hu
    exact ⟨v, hv, (congrArg b.node hvu).trans he⟩
  conclusion := fun j => (congrArg b.node (a.conclusion j)).trans (b.conclusion (a.rule j))

@[ext] theorem ext (a b : RuleTransport F G)
    (hn : a.node = b.node) (hr : a.rule = b.rule) : a = b := by
  cases a
  cases b
  cases hn
  cases hr
  rfl

theorem identity_comp (a : RuleTransport F G) : comp (identity F) a = a := by
  apply ext <;> rfl

theorem comp_identity (a : RuleTransport F G) : comp a (identity G) = a := by
  apply ext <;> rfl

theorem comp_assoc {ω N : Type*} {Q : Field ω N}
    (a : RuleTransport F G) (b : RuleTransport G H) (c : RuleTransport H Q) :
    comp (comp a b) c = comp a (comp b c) := by
  apply ext <;> rfl

theorem derives_map (a : RuleTransport F G) {v : ι} (hv : F.Derives v) :
    G.Derives (a.node v) := by
  induction hv with
  | leaf h => exact Field.Derives.leaf (a.leaves _ h)
  | step j hc _ ih =>
    rw [a.conclusion j]
    apply Field.Derives.step (a.rule j) (a.certified j hc)
    intro w hw
    obtain ⟨v, hv, h⟩ := a.premises j w hw
    rw [← h]
    exact ih v hv

theorem model_pullback (a : RuleTransport F G) {x : κ → Prop} (hx : G.Model x) :
    F.Model (x ∘ a.node) := by
  constructor
  · exact fun v hv => hx.1 _ (a.leaves v hv)
  · intro j hc hp
    change x (a.node (F.conclusion j))
    rw [a.conclusion j]
    apply hx.2 (a.rule j) (a.certified j hc)
    intro w hw
    obtain ⟨v, hv, he⟩ := a.premises j w hw
    rw [← he]
    exact hp v hv

theorem extension_pullback (a : RuleTransport F G) (S N : Set ι)
    {x : κ → Prop} (hx : G.Extends (a.node '' S) (a.node '' N) x) :
    F.Extends S N (x ∘ a.node) := by
  refine ⟨a.model_pullback hx.1, ?_, ?_⟩
  · exact fun v hv => hx.2.1 _ ⟨v, hv, rfl⟩
  · exact fun v hv => hx.2.2 _ ⟨v, hv, rfl⟩

/-- Infeasibility transports in the direction opposite to model pullback. -/
theorem obstruction_pushforward (a : RuleTransport F G) (S N : Set ι)
    (h : ¬ ∃ x, F.Extends S N x) :
    ¬ ∃ x, G.Extends (a.node '' S) (a.node '' N) x := by
  rintro ⟨x, hx⟩
  exact h ⟨x ∘ a.node, a.extension_pullback S N hx⟩

/-- Semantic soundness is transported, not manufactured by the node labels. -/
theorem semantic_transport (a : RuleTransport F G) (meaning : κ → Prop)
    (hm : G.Model meaning) {v : ι} (hv : F.Derives v) : meaning (a.node v) :=
  G.derives_sound hm (a.derives_map hv)

/-- Positive observations are transported as admitted data, not renamed conclusions. -/
def seeded (a : RuleTransport F G) (S : Set ι) :
    RuleTransport (F.seeded S) (G.seeded (a.node '' S)) where
  node := a.node
  rule := a.rule
  leaves := by
    intro v hv
    rcases hv with hv | hv
    · exact Or.inl (a.leaves v hv)
    · exact Or.inr ⟨v, hv, rfl⟩
  certified := a.certified
  premises := a.premises
  conclusion := a.conclusion

theorem closure_map (a : RuleTransport F G) (S : Set ι) {v : ι}
    (hv : v ∈ F.closure S) : a.node v ∈ G.closure (a.node '' S) :=
  (a.seeded S).derives_map hv

theorem obstruction_witness_map (a : RuleTransport F G) (S N : Set ι) {v : ι}
    (hn : v ∈ N) (hv : v ∈ F.closure S) :
    a.node v ∈ a.node '' N ∧ a.node v ∈ G.closure (a.node '' S) :=
  ⟨⟨v, hn, rfl⟩, a.closure_map S hv⟩

end RuleTransport
end ProofPath
