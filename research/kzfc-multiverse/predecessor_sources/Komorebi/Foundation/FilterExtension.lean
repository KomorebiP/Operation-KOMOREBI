import Komorebi.Foundation.FineUltrafilterCompactness

/-!
# Semantic compactness and complete filter extension

The compactness principles quantify over actual constraint predicates with declared
small scopes. The filter extension property is independently stated using Mathlib
filters and ultrafilters. No existence principle is introduced as an axiom.
-/

universe u

namespace Komorebi.CompactnessClassification

open Set Filter
open FineUltrafilterCompactness

/-- Compactness for every fixed value domain of size strictly below kappa. -/
def FixedDomainCompactness (κ : Cardinal.{u}) : Prop :=
  ∀ (I V A : Type u), Cardinal.mk A < κ →
    ∀ (scope : I → Set V), (∀ i, Cardinal.mk (scope i) < κ) →
    ∀ (satisfies : I → (V → A) → Prop),
    (∀ i a b, (∀ v ∈ scope i, a v = b v) → satisfies i a → satisfies i b) →
    (∀ J : SmallPieces κ I, ∃ a : V → A, ∀ i ∈ J.val, satisfies i a) →
    ∃ a : V → A, ∀ i, satisfies i a

/-- The two-valued semantic fragment, expressed with proposition-valued assignments. -/
def BooleanCompactness (κ : Cardinal.{u}) : Prop :=
  ∀ (I V : Type u) (scope : I → Set V), (∀ i, Cardinal.mk (scope i) < κ) →
    ∀ (satisfies : I → (V → Prop) → Prop),
    (∀ i a b, (∀ v ∈ scope i, a v = b v) → satisfies i a → satisfies i b) →
    (∀ J : SmallPieces κ I, ∃ a : V → Prop, ∀ i ∈ J.val, satisfies i a) →
    ∃ a : V → Prop, ∀ i, satisfies i a

/-- Every proper kappa-complete filter extends to a kappa-complete ultrafilter.
The inequality is in Mathlib's reversed filter order, so it means extension. -/
def CompleteFilterExtension (κ : Cardinal.{u}) : Prop :=
  ∀ (X : Type u) (F : Filter X), F.NeBot → CardinalInterFilter F κ →
    ∃ U : Ultrafilter X, (U : Filter X) ≤ F ∧
      CardinalInterFilter (U : Filter X) κ

/-- An ultrafilter on every small-pieces space, rather than an assumed compactness rule. -/
def FineUltrafilterPrinciple (κ : Cardinal.{u}) : Prop :=
  ∀ I : Type u, HasFineCompleteUltrafilter κ I

theorem fixedDomain_of_fine (κ : Cardinal.{u})
    (hf : FineUltrafilterPrinciple κ) : FixedDomainCompactness κ := by
  intro I V A hA scope hscope satisfies locality hlocal
  obtain ⟨U, hU, hFine⟩ := hf I
  let : CardinalInterFilter (U : Filter (SmallPieces κ I)) κ := hU
  exact compactness_of_fine_complete κ U hFine hA scope hscope satisfies locality hlocal

/-- The Boolean fragment really follows from the independently stated fixed-domain
principle; ULift keeps all universes aligned without restricting variable cardinality. -/
theorem boolean_of_fixedDomain (κ : Cardinal.{u}) (hκ : Cardinal.aleph0 ≤ κ)
    (h : FixedDomainCompactness κ) : BooleanCompactness κ := by
  intro I V scope hscope satisfies locality hlocal
  have hA : Cardinal.mk (ULift.{u} Prop) < κ := by
    simpa using (Cardinal.natCast_lt_aleph0 (n := 2)).trans_le hκ
  obtain ⟨a, ha⟩ := h I V (ULift.{u} Prop) hA scope hscope
    (fun i a => satisfies i (fun v => (a v).down))
    (by
      intro i a b hagree hi
      exact locality i _ _ (fun v hv => congrArg ULift.down (hagree v hv)) hi)
    (by
      intro J
      obtain ⟨a, ha⟩ := hlocal J
      exact ⟨fun v => ⟨a v⟩, ha⟩)
  exact ⟨fun v => (a v).down, ha⟩

/-- The exact requirements used to construct an ultrafilter from a truth assignment. -/
inductive FilterRequirement (κ : Cardinal.{u}) {X : Type u} (F : Filter X)
  | top
  | compl (s : Set X)
  | meet (s t : Set X)
  | smallInter (S : SmallPieces κ (Set X))
  | accept (s : {s : Set X // s ∈ F})

namespace FilterRequirement

variable {κ : Cardinal.{u}} {X : Type u} {F : Filter X}

def scope : FilterRequirement κ F → Set (Set X)
  | .top => {univ}
  | .compl s => {sᶜ, s}
  | .meet s t => {s ∩ t, s, t}
  | .smallInter S => insert (⋂₀ S.val) S.val
  | .accept s => {s.val}

def Holds : FilterRequirement κ F → (Set X → Prop) → Prop
  | .top, a => a univ
  | .compl s, a => (a sᶜ ↔ ¬ a s)
  | .meet s t, a => (a (s ∩ t) ↔ a s ∧ a t)
  | .smallInter S, a => (a (⋂₀ S.val) ↔ ∀ s ∈ S.val, a s)
  | .accept s, a => a s.val

/-- The only requirements that constrain the point chosen for local satisfiability. -/
def seed : FilterRequirement κ F → Set X
  | .accept s => s.val
  | _ => univ

theorem seed_mem (r : FilterRequirement κ F) : r.seed ∈ F := by
  cases r <;> simp only [seed]
  all_goals first | exact Filter.univ_mem | exact Subtype.property _

theorem scope_small (hκ : Cardinal.aleph0 ≤ κ) (r : FilterRequirement κ F) :
    Cardinal.mk r.scope < κ := by
  cases r with
  | top => exact (Set.finite_singleton _).lt_aleph0.trans_le hκ
  | compl s => exact ((Set.finite_singleton s).insert sᶜ).lt_aleph0.trans_le hκ
  | meet s t => exact (((Set.finite_singleton t).insert s).insert (s ∩ t)).lt_aleph0.trans_le hκ
  | accept s => exact (Set.finite_singleton _).lt_aleph0.trans_le hκ
  | smallInter S =>
    exact Cardinal.mk_insert_le.trans_lt
      (Cardinal.add_lt_of_lt hκ S.property (Cardinal.natCast_lt_aleph0.trans_le hκ))

theorem locality (r : FilterRequirement κ F) (a b : Set X → Prop)
    (h : ∀ s ∈ r.scope, a s = b s) (ha : r.Holds a) : r.Holds b := by
  cases r with
  | top =>
    change b univ
    change a univ at ha
    exact (h univ (by simp [scope])) ▸ ha
  | accept s =>
    change b s.val
    change a s.val at ha
    exact (h s.val (by simp [scope])) ▸ ha
  | compl s =>
    change b sᶜ ↔ ¬ b s
    change a sᶜ ↔ ¬ a s at ha
    rwa [h sᶜ (by simp [scope]), h s (by simp [scope])] at ha
  | meet s t =>
    change b (s ∩ t) ↔ b s ∧ b t
    change a (s ∩ t) ↔ a s ∧ a t at ha
    rwa [h (s ∩ t) (by simp [scope]), h s (by simp [scope]),
      h t (by simp [scope])] at ha
  | smallInter S =>
    change b (⋂₀ S.val) ↔ ∀ s ∈ S.val, b s
    change a (⋂₀ S.val) ↔ ∀ s ∈ S.val, a s at ha
    rw [← h (⋂₀ S.val) (by simp [scope])]
    apply ha.trans
    exact forall₂_congr (fun s hs => (h s (by simp [scope, hs])).to_iff)

/-- Evaluation at a point satisfies every Boolean and intersection law literally. -/
theorem point_holds (r : FilterRequirement κ F) (x : X) (hx : x ∈ r.seed) :
    r.Holds (fun s => x ∈ s) := by
  cases r <;> simp_all [Holds, seed]

/-- Completeness of the starting proper filter proves every small subsystem satisfiable. -/
theorem locally_satisfiable [F.NeBot] [CardinalInterFilter F κ]
    (J : SmallPieces κ (FilterRequirement κ F)) :
    ∃ a : Set X → Prop, ∀ r ∈ J.val, r.Holds a := by
  have hm : (⋂ r : J.val, r.val.seed) ∈ F :=
    (Filter.cardinal_iInter_mem J.property).mpr (fun r => seed_mem r.val)
  obtain ⟨x, hx⟩ := Filter.nonempty_of_mem hm
  refine ⟨fun s => x ∈ s, ?_⟩
  intro r hr
  exact point_holds r x (Set.mem_iInter.mp hx ⟨r, hr⟩)

/-- Construct a genuine Mathlib filter from a globally satisfying truth assignment. -/
def truthFilter (a : Set X → Prop) (ha : ∀ r : FilterRequirement κ F, r.Holds a) :
    Filter X where
  sets := {s | a s}
  univ_sets := ha .top
  sets_of_superset := by
    intro s t hs hst
    have hi : a (s ∩ t) := by rwa [Set.inter_eq_left.mpr hst]
    exact (ha (.meet s t)).mp hi |>.2
  inter_sets := by
    intro s t hs ht
    exact (ha (.meet s t)).mpr ⟨hs, ht⟩

/-- The complement law yields maximality, not merely a proper filter. -/
def truthUltrafilter (a : Set X → Prop)
    (ha : ∀ r : FilterRequirement κ F, r.Holds a) : Ultrafilter X :=
  Ultrafilter.ofComplNotMemIff (truthFilter a ha) (by
    intro s
    change ¬ a sᶜ ↔ a s
    have hc : a sᶜ ↔ ¬ a s := ha (.compl s)
    rw [hc]
    exact not_not)

theorem truthUltrafilter_extends (a : Set X → Prop)
    (ha : ∀ r : FilterRequirement κ F, r.Holds a) :
    (truthUltrafilter a ha : Filter X) ≤ F := by
  intro s hs
  exact ha (.accept ⟨s, hs⟩)

theorem truthUltrafilter_complete (a : Set X → Prop)
    (ha : ∀ r : FilterRequirement κ F, r.Holds a) :
    CardinalInterFilter (truthUltrafilter a ha : Filter X) κ := by
  refine ⟨?_⟩
  intro S hS hm
  exact (ha (.smallInter ⟨S, hS⟩)).mpr hm

end FilterRequirement

/-- The substantive converse: two-valued constraint compactness constructs a complete
ultrafilter extending any given proper complete filter. -/
theorem extension_of_boolean (κ : Cardinal.{u}) (hκ : Cardinal.aleph0 ≤ κ)
    (h : BooleanCompactness κ) : CompleteFilterExtension κ := by
  intro X F hF hcomplete
  let : F.NeBot := hF
  let : CardinalInterFilter F κ := hcomplete
  obtain ⟨a, ha⟩ := h (FilterRequirement κ F) (Set X)
    FilterRequirement.scope (FilterRequirement.scope_small hκ)
    FilterRequirement.Holds FilterRequirement.locality
    FilterRequirement.locally_satisfiable
  exact ⟨FilterRequirement.truthUltrafilter a ha,
    FilterRequirement.truthUltrafilter_extends a ha,
    FilterRequirement.truthUltrafilter_complete a ha⟩

end Komorebi.CompactnessClassification
