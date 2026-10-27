import Mathlib.Order.Antisymmetrization
import Mathlib.Order.Preorder.Finite
import Mathlib.Data.Fintype.Card
import Mathlib.Data.Finset.Card
import Mathlib.Data.Nat.Find
import Mathlib.SetTheory.Cardinal.Finite

/-!
Paper X, 7.3: minimum generating sets for a finite directed graph.
Edges are supplied; reachability is the actual reflexive-transitive closure.
Components are the quotient by mutual reachability, not stipulated labels.
No decidability of the edge relation is needed for the structural theorem.
-/
set_option autoImplicit false
namespace PaperX.DirectedSeeds

universe u
variable {V : Type u}

abbrev Reach (E : V → V → Prop) : V → V → Prop := Relation.ReflTransGen E

abbrev Component (E : V → V → Prop) := Antisymmetrization V (Reach E)

def component (E : V → V → Prop) : V → Component E :=
  toAntisymmetrization (Reach E)

theorem component_eq_iff (E : V → V → Prop) (a b : V) :
    component E a = component E b ↔ Reach E a b ∧ Reach E b a :=
  toAntisymmetrization_eq (Reach E) a b

/-- A component has no incoming path from a different component. -/
def IsSource (E : V → V → Prop) (c : Component E) : Prop :=
  ∀ a b, component E b = c → Reach E a b → component E a = c

abbrev Source (E : V → V → Prop) := {c : Component E // IsSource E c}

theorem source_iff (E : V → V → Prop) (v : V) :
    IsSource E (component E v) ↔ ∀ a, Reach E a v → Reach E v a := by
  constructor
  · intro h a ha
    exact ((component_eq_iff E a v).1 (h a v rfl ha)).2
  · intro h a b hb hab
    have hbv := ((component_eq_iff E b v).1 hb).1
    have hav := hab.trans hbv
    exact (component_eq_iff E a v).2 ⟨hav, h a hav⟩

/-- The path-based source definition agrees with no incoming external edge. -/
theorem source_iff_no_external_edge (E : V → V → Prop) (c : Component E) :
    IsSource E c ↔
      ∀ a b, component E b = c → E a b → component E a = c := by
  constructor
  · intro h a b hb hab
    exact h a b hb (.single hab)
  · intro h a b hb hab
    induction hab using Relation.ReflTransGen.head_induction_on with
    | refl => exact hb
    | @head a d had _ ih => exact h a d ih had

/-- Every vertex in a finite graph lies downstream of an actual source component. -/
theorem source_reaches [Finite V] (E : V → V → Prop) (v : V) :
    ∃ a, IsSource E (component E a) ∧ Reach E a v := by
  let : Preorder V :=
    { le := Reach E
      le_refl := fun _ => .refl
      le_trans := fun _ _ _ => Relation.ReflTransGen.trans }
  obtain ⟨a, hav, ha⟩ := Finite.exists_le_minimal (p := fun _ : V => True) (a := v) trivial
  exact ⟨a, (source_iff E a).2 (fun b hba => ha.2 trivial hba), hav⟩

/-- All vertices, including seeds themselves by the empty path, are covered. -/
def Covers (E : V → V → Prop) (S : Finset V) : Prop :=
  ∀ v, ∃ s ∈ S, Reach E s v

def MeetsSources (E : V → V → Prop) (S : Finset V) : Prop :=
  ∀ c : Source E, ∃ s ∈ S, component E s = c.val

noncomputable def representative (E : V → V → Prop) (c : Component E) : V :=
  ofAntisymmetrization (Reach E) c

theorem component_representative (E : V → V → Prop) (c : Component E) :
    component E (representative E c) = c :=
  toAntisymmetrization_ofAntisymmetrization (Reach E) c

theorem covers_meets_sources (E : V → V → Prop) (S : Finset V)
    (hS : Covers E S) : MeetsSources E S := by
  intro c
  obtain ⟨s, hs, hpath⟩ := hS (representative E c.val)
  exact ⟨s, hs, c.property s _ (component_representative E c.val) hpath⟩

/-- Covering is exactly meeting all source components, for finite graphs. -/
theorem covers_iff_meets_sources [Finite V] (E : V → V → Prop) (S : Finset V) :
    Covers E S ↔ MeetsSources E S := by
  refine ⟨covers_meets_sources E S, ?_⟩
  intro h v
  obtain ⟨a, ha, hav⟩ := source_reaches E v
  obtain ⟨s, hs, heq⟩ := h ⟨component E a, ha⟩
  exact ⟨s, hs, (((component_eq_iff E s a).1 heq).1).trans hav⟩

/-- Finiteness is inherited by the actual quotient and its source subtype. -/
instance componentFinite [Finite V] (E : V → V → Prop) : Finite (Component E) :=
  inferInstanceAs (Finite (Quotient (AntisymmRel.setoid V (Reach E))))

noncomputable instance sourceFintype [Finite V] (E : V → V → Prop) : Fintype (Source E) :=
  Fintype.ofFinite _

noncomputable def sourceRepresentative (E : V → V → Prop) (c : Source E) : V :=
  representative E c.val

theorem sourceRepresentative_injective (E : V → V → Prop) :
    Function.Injective (sourceRepresentative E) := by
  intro a b h
  apply Subtype.ext
  simpa only [sourceRepresentative, component_representative] using congrArg (component E) h

noncomputable def canonicalSeeds [Finite V] (E : V → V → Prop) : Finset V := by
  classical
  exact Finset.univ.image (sourceRepresentative E)

theorem canonicalSeeds_cover [Finite V] (E : V → V → Prop) :
    Covers E (canonicalSeeds E) := by
  classical
  apply (covers_iff_meets_sources E _).2
  intro c
  exact ⟨sourceRepresentative E c, Finset.mem_image.mpr ⟨c, Finset.mem_univ c, rfl⟩,
    component_representative E c.val⟩

theorem canonicalSeeds_card [Finite V] (E : V → V → Prop) :
    (canonicalSeeds E).card = Nat.card (Source E) := by
  classical
  simp only [canonicalSeeds, Finset.card_image_of_injective _ (sourceRepresentative_injective E),
    Finset.card_univ, Nat.card_eq_fintype_card]

/-- Every covering seed set has at least one distinct member per source component. -/
theorem source_count_le [Finite V] (E : V → V → Prop) (S : Finset V)
    (hS : Covers E S) : Nat.card (Source E) ≤ S.card := by
  classical
  have h := covers_meets_sources E S hS
  choose s hs hc using h
  let f : Source E → {v // v ∈ S} := fun c => ⟨s c, hs c⟩
  have hf : Function.Injective f := by
    intro a b heq
    apply Subtype.ext
    have hs' : s a = s b := congrArg Subtype.val heq
    exact (hc a).symm.trans ((congrArg (component E) hs').trans (hc b))
  simpa only [Nat.card_eq_fintype_card, Fintype.card_coe] using Fintype.card_le_of_injective f hf

/-- Existence of an optimal seed set, with the lower bound proved separately. -/
theorem minimum_seed_set [Finite V] (E : V → V → Prop) :
    ∃ S : Finset V, Covers E S ∧ S.card = Nat.card (Source E) ∧
      ∀ T : Finset V, Covers E T → S.card ≤ T.card := by
  refine ⟨canonicalSeeds E, canonicalSeeds_cover E, canonicalSeeds_card E, ?_⟩
  intro T hT
  rw [canonicalSeeds_card]
  exact source_count_le E T hT

theorem exists_cover_card [Finite V] (E : V → V → Prop) :
    ∃ n : ℕ, ∃ S : Finset V, Covers E S ∧ S.card = n :=
  ⟨_, canonicalSeeds E, canonicalSeeds_cover E, rfl⟩

/-- Rank is the least cardinality of a genuinely covering finite seed set. -/
noncomputable def seedRank [Finite V] (E : V → V → Prop) : ℕ :=
  by
  classical
  exact Nat.find (exists_cover_card E)

theorem seedRank_realized [Finite V] (E : V → V → Prop) :
    ∃ S : Finset V, Covers E S ∧ S.card = seedRank E :=
  by
  classical
  exact Nat.find_spec (exists_cover_card E)

theorem seedRank_le [Finite V] (E : V → V → Prop) (S : Finset V)
    (hS : Covers E S) : seedRank E ≤ S.card :=
  by
  classical
  exact Nat.find_min' (exists_cover_card E) ⟨S, hS, rfl⟩

/-- Paper X 7.3, with the minimization and component count independently defined. -/
theorem directed_minimum_seed [Finite V] (E : V → V → Prop) :
    seedRank E = Nat.card (Source E) := by
  apply Nat.le_antisymm
  · simpa only [canonicalSeeds_card] using seedRank_le E _ (canonicalSeeds_cover E)
  · obtain ⟨S, hS, hcard⟩ := seedRank_realized E
    rw [← hcard]
    exact source_count_le E S hS

end PaperX.DirectedSeeds
