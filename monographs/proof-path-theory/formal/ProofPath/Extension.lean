import ProofPath.Field

/-!
Protected extensions of the actual declared rule field.
Positive observations are extra leaves; negative observations are forbidden nodes.
-/
namespace ProofPath
namespace Field
variable {ι J : Type*} (F : Field ι J)

def seeded (S : Set ι) : Field ι J := { F with leaf := F.leaf ∪ S }

def closure (S : Set ι) : Set ι := {v | (F.seeded S).Derives v}

def Extends (S N : Set ι) (x : ι → Prop) : Prop :=
  F.Model x ∧ (∀ v, v ∈ S → x v) ∧ (∀ v, v ∈ N → ¬ x v)

theorem closure_contains_seed (S : Set ι) : S ⊆ F.closure S := by
  intro v hv
  exact Derives.leaf (Or.inr hv)

theorem closure_is_model (S : Set ι) : F.Model (F.closure S) := by
  constructor
  · intro v hv
    exact Derives.leaf (Or.inl hv)
  · intro j hc hp
    exact Derives.step j hc hp

theorem closure_le_model (S : Set ι) {x : ι → Prop}
    (hx : F.Model x) (hs : ∀ v, v ∈ S → x v) :
    ∀ v, v ∈ F.closure S → x v := by
  intro v hv
  apply (F.seeded S).derives_sound ?_ hv
  refine ⟨?_, hx.2⟩
  intro w hw
  rcases hw with hw | hw
  · exact hx.1 w hw
  · exact hs w hw

theorem closure_mono {S T : Set ι} (hst : S ⊆ T) :
    F.closure S ⊆ F.closure T := by
  exact F.closure_le_model S (F.closure_is_model T)
    (fun _ hv => F.closure_contains_seed T (hst hv))

theorem closure_idempotent (S : Set ι) :
    F.closure (F.closure S) = F.closure S := by
  apply Set.Subset.antisymm
  · exact F.closure_le_model _ (F.closure_is_model S) (fun _ hv => hv)
  · exact F.closure_contains_seed _

/-- Existence of a protected extension is decided by one least closure. -/
theorem extension_iff_avoids_closure (S N : Set ι) :
    (∃ x, F.Extends S N x) ↔ ∀ v, v ∈ N → v ∉ F.closure S := by
  constructor
  · rintro ⟨x, hx, hs, hn⟩ v hv hc
    exact hn v hv (F.closure_le_model S hx hs v hc)
  · intro h
    exact ⟨F.closure S, F.closure_is_model S,
      fun _ hv => F.closure_contains_seed S hv, h⟩

theorem extension_iff_closed_interval (S N : Set ι) (x : ι → Prop) :
    F.Extends S N x ↔
      F.Model x ∧ (∀ v, v ∈ F.closure S → x v) ∧ (∀ v, v ∈ N → ¬ x v) := by
  constructor
  · rintro ⟨hx, hs, hn⟩
    exact ⟨hx, F.closure_le_model S hx hs, hn⟩
  · rintro ⟨hx, hs, hn⟩
    exact ⟨hx, fun _ hv => hs _ (F.closure_contains_seed S hv), hn⟩

/-- This is a refutation of the fixed extension problem, not of an arbitrary theorem. -/
theorem infeasible_iff_forbidden_derivation (S N : Set ι) :
    ¬ (∃ x, F.Extends S N x) ↔ ∃ v, v ∈ N ∧ v ∈ F.closure S := by
  rw [extension_iff_avoids_closure]
  push Not
  rfl

/-- A partial valuation prescribes both true and false values on its patch. -/
theorem partial_extension_iff (U S : Set ι) (hsu : S ⊆ U) :
    (∃ x, F.Model x ∧ ∀ v, v ∈ U → (x v ↔ v ∈ S)) ↔
      F.closure S ∩ U = S := by
  constructor
  · rintro ⟨x, hx, hagree⟩
    apply Set.Subset.antisymm
    · intro v hv
      have hseed : ∀ w, w ∈ S → x w := fun w hw => (hagree w (hsu hw)).mpr hw
      exact (hagree v hv.2).mp (F.closure_le_model S hx hseed v hv.1)
    · exact fun v hv => ⟨F.closure_contains_seed S hv, hsu hv⟩
  · intro he
    refine ⟨F.closure S, F.closure_is_model S, ?_⟩
    intro v hv
    constructor
    · intro hc
      have hm : v ∈ F.closure S ∩ U := ⟨hc, hv⟩
      rw [he] at hm
      exact hm
    · exact fun hs => F.closure_contains_seed S hs

/-- Closing earlier positive data before adding later data changes no result. -/
theorem staged_closure (S T : Set ι) :
    F.closure (F.closure S ∪ T) = F.closure (S ∪ T) := by
  apply Set.Subset.antisymm
  · apply F.closure_le_model _ (F.closure_is_model (S ∪ T))
    intro v hv
    rcases hv with hv | hv
    · exact F.closure_mono (Set.subset_union_left) hv
    · exact F.closure_contains_seed (S ∪ T) (Or.inr hv)
  · apply F.closure_mono
    intro v hv
    rcases hv with hv | hv
    · exact Or.inl (F.closure_contains_seed S hv)
    · exact Or.inr hv

/-- More observations shrink the extension fiber. -/
theorem extends_antitone {S T N M : Set ι} (hst : S ⊆ T) (hnm : N ⊆ M)
    {x : ι → Prop} (hx : F.Extends T M x) : F.Extends S N x :=
  ⟨hx.1, fun _ hv => hx.2.1 _ (hst hv), fun _ hv => hx.2.2 _ (hnm hv)⟩

theorem obstruction_persists {S T N M : Set ι} (hst : S ⊆ T) (hnm : N ⊆ M)
    (h : ¬ ∃ x, F.Extends S N x) : ¬ ∃ x, F.Extends T M x := by
  rintro ⟨x, hx⟩
  exact h ⟨x, F.extends_antitone hst hnm hx⟩

end Field
end ProofPath
