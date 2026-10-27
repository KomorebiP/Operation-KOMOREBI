module
public import Mathlib.Data.Fintype.Card
public import Mathlib.Data.Set.Function
@[expose] public section

/-! Exact information recovery. Decoders on the image need no nonempty-codomain
assumption. Total decoders below explicitly require a nonempty target. -/
namespace KomorebiInformation
universe u v w z c
variable {X : Type u} {O : Type v} {Y : Type w} {E : Type z} {C : Type c}

/-- All task-relevant distinctions survive the observation. -/
def Sufficient (r : X → O) (f : X → Y) : Prop :=
  ∀ x y, r x = r y → f x = f y

/-- A concrete pair that no observation-only decoder can separate. -/
def Obstruction (r : X → O) (f : X → Y) (x y : X) : Prop :=
  r x = r y ∧ f x ≠ f y

/-- Pointwise decoder correctness; not just correctness almost surely. -/
def Decodes (r : X → O) (f : X → Y) (g : O → Y) : Prop :=
  ∀ x, g (r x) = f x

theorem sufficient_iff_no_obstruction (r : X → O) (f : X → Y) :
    Sufficient r f ↔ ¬ ∃ x y, Obstruction r f x y := by
  constructor
  · intro h ⟨x, y, heq, hne⟩
    exact hne (h x y heq)
  · intro h x y heq
    by_contra hne
    exact h ⟨x, y, heq, hne⟩

theorem decodes_implies_sufficient {r : X → O} {f : X → Y} {g : O → Y}
    (h : Decodes r f g) : Sufficient r f := by
  intro x y heq
  calc f x = g (r x) := (h x).symm
       _ = g (r y) := congrArg g heq
       _ = f y := h y

theorem sufficient_iff_image_decoder (r : X → O) (f : X → Y) :
    Sufficient r f ↔
      ∃ g : Set.range r → Y, ∀ x, g ⟨r x, Set.mem_range_self x⟩ = f x := by
  classical
  constructor
  · intro h
    let g : Set.range r → Y := fun o => f (Classical.choose o.property)
    refine ⟨g, ?_⟩
    intro x
    apply h
    exact Classical.choose_spec (Set.mem_range_self x : r x ∈ Set.range r)
  · rintro ⟨g, hg⟩ x y heq
    calc f x = g ⟨r x, Set.mem_range_self x⟩ := (hg x).symm
         _ = g ⟨r y, Set.mem_range_self y⟩ := congrArg g (Subtype.ext heq)
         _ = f y := hg y

theorem sufficient_iff_total_decoder [Nonempty Y] (r : X → O) (f : X → Y) :
    Sufficient r f ↔ ∃ g : O → Y, Decodes r f g := by
  classical
  constructor
  · intro h
    let g : O → Y := fun o => if ho : ∃ x, r x = o then
      f (Classical.choose ho) else Classical.choice ‹Nonempty Y›
    refine ⟨g, ?_⟩
    intro x
    dsimp [g]
    rw [dite_eq_left ⟨x, rfl⟩]
    exact h _ x (Classical.choose_spec (show ∃ y, r y = r x from ⟨x, rfl⟩))
  · rintro ⟨g, hg⟩
    exact decodes_implies_sufficient hg

theorem obstruction_rejects_decoder {r : X → O} {f : X → Y} {x y : X}
    (h : Obstruction r f x y) (g : O → Y) : ¬ Decodes r f g := by
  intro hg
  exact h.2 (decodes_implies_sufficient hg x y h.1)

theorem sufficient_refl (r : X → O) : Sufficient r r := by
  intro _ _ h
  exact h

theorem sufficient_trans {r : X → O} {s : X → E} {f : X → Y}
    (hrs : Sufficient r s) (hsf : Sufficient s f) : Sufficient r f := by
  intro x y h
  exact hsf x y (hrs x y h)

theorem sufficient_joint_left {r : X → O} {f : X → Y}
    (h : Sufficient r f) (u : X → E) : Sufficient (fun x => (r x, u x)) f := by
  intro x y hxy
  exact h x y (congrArg Prod.fst hxy)

/-- The helper sees only u(x); the decoder sees r(x) and the code. -/
def Repair (r : X → O) (f : X → Y) (u : X → E)
    (h : E → C) (g : O × C → Y) : Prop :=
  ∀ x, g (r x, h (u x)) = f x

theorem repair_implies_joint_sufficient {r : X → O} {f : X → Y} {u : X → E}
    {h : E → C} {g : O × C → Y} (hg : Repair r f u h g) :
    Sufficient (fun x => (r x, u x)) f := by
  intro x y hxy
  have hr := congrArg Prod.fst hxy
  have hu := congrArg Prod.snd hxy
  change r x = r y at hr
  change u x = u y at hu
  calc f x = g (r x, h (u x)) := (hg x).symm
       _ = g (r y, h (u y)) := by rw [hr, hu]
       _ = f y := hg y

theorem joint_sufficient_iff_access_repair [Nonempty Y]
    (r : X → O) (f : X → Y) (u : X → E) :
    Sufficient (fun x => (r x, u x)) f ↔
      ∃ h : E → E, ∃ g : O × E → Y, Repair r f u h g := by
  constructor
  · intro hs
    obtain ⟨g, hg⟩ := (sufficient_iff_total_decoder _ _).mp hs
    exact ⟨id, g, hg⟩
  · rintro ⟨h, g, hg⟩
    exact repair_implies_joint_sufficient hg

theorem inaccessible_pair_rejects_every_code
    {r : X → O} {f : X → Y} {u : X → E} {x y : X}
    (hr : r x = r y) (hu : u x = u y) (hf : f x ≠ f y)
    (h : E → C) (g : O × C → Y) : ¬ Repair r f u h g := by
  intro hrep
  exact hf (repair_implies_joint_sufficient hrep x y (Prod.ext hr hu))

/-- Any set of different answers in one observation fiber injects into messages. -/
theorem repair_message_injective_on_task_representatives
    {I : Type*} {r : X → O} {f : X → Y} {u : X → E}
    {h : E → C} {g : O × C → Y} (hg : Repair r f u h g)
    (s : I → X) (o : O) (hr : ∀ i, r (s i) = o)
    (hf : Function.Injective (f ∘ s)) : Function.Injective (h ∘ u ∘ s) := by
  intro i j hij
  change h (u (s i)) = h (u (s j)) at hij
  apply hf
  change f (s i) = f (s j)
  calc f (s i) = g (r (s i), h (u (s i))) := (hg (s i)).symm
       _ = g (r (s j), h (u (s j))) := by rw [hr i, hr j, hij]
       _ = f (s j) := hg (s j)

theorem repair_alphabet_lower_bound
    {I : Type*} [Fintype I] [Fintype C]
    {r : X → O} {f : X → Y} {u : X → E}
    {h : E → C} {g : O × C → Y} (hg : Repair r f u h g)
    (s : I → X) (o : O) (hr : ∀ i, r (s i) = o)
    (hf : Function.Injective (f ∘ s)) : Fintype.card I ≤ Fintype.card C :=
  Fintype.card_le_of_injective _
    (repair_message_injective_on_task_representatives hg s o hr hf)
end KomorebiInformation
