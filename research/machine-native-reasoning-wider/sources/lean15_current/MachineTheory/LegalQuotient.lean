import Mathlib.Data.Fintype.Basic
import Mathlib.Data.Set.Basic

/-! # Quotients preserving labels and legal operations

Core 8.2. `none` means disabled, while `some y` records the unique legal successor.
Thus there are no unspecified successors on disabled actions. `ofEnabled` embeds
the manuscript's separately supplied enabled sets and dependent legal successors
into this canonical partial representation without changing them.

The quotient below is constructed by choosing an actual representative of each
fibre. Compatibility is the three explicit local conditions on the input system,
not the prior existence of a quotient. No nonempty state space is assumed.
These are conditions on encoded institutional permissions, not a derivation of
external moral or legal authority.
-/
namespace Komorebi.MachineTheory.LegalQuotient

universe u v w l

/-- A deterministic partial operational system with protected labels. -/
@[ext] structure System (X : Type u) (Action : Type v) (Label : Type l) where
  label : X → Label
  step : X → Action → Option X

variable {X : Type u} {Z : Type w} {Action : Type v} {Label : Type l}

/-- Exactly the actions for which the system supplies a legal successor. -/
def enabled (M : System X Action Label) (x : X) : Set Action :=
  {a | (M.step x a).isSome}

/-- Enabled actions and existing legal successors are the same domain. -/
theorem mem_enabled_iff (M : System X Action Label) (x : X) (a : Action) :
    a ∈ enabled M x ↔ ∃ y, M.step x a = some y := by
  cases hs : M.step x a <;> simp [enabled, hs]

/-- A disabled action has no successor in the partial system. -/
theorem not_enabled_iff (M : System X Action Label) (x : X) (a : Action) :
    a ∉ enabled M x ↔ M.step x a = none := by
  cases hs : M.step x a <;> simp [enabled, hs]

/-- The source's given enabled sets and legal-only successor function. -/
noncomputable def ofEnabled (label : X → Label) (D : X → Set Action)
    (F : ∀ x a, a ∈ D x → X) : System X Action Label := by
  classical
  exact ⟨label, fun x a => if h : a ∈ D x then some (F x a h) else none⟩

@[simp] theorem ofEnabled_label (label : X → Label) (D : X → Set Action)
    (F : ∀ x a, a ∈ D x → X) (x : X) : (ofEnabled label D F).label x = label x := rfl

/-- Translation preserves every supplied legal successor. -/
theorem ofEnabled_step_of_mem (label : X → Label) (D : X → Set Action)
    (F : ∀ x a, a ∈ D x → X) (x : X) (a : Action) (ha : a ∈ D x) :
    (ofEnabled label D F).step x a = some (F x a ha) := by
  simp [ofEnabled, ha]

/-- Translation invents no successor for a disabled action. -/
theorem ofEnabled_step_of_not_mem (label : X → Label) (D : X → Set Action)
    (F : ∀ x a, a ∈ D x → X) (x : X) (a : Action) (ha : a ∉ D x) :
    (ofEnabled label D F).step x a = none := by
  simp [ofEnabled, ha]

/-- The encoded permission set is literally the source's supplied set. -/
@[simp] theorem enabled_ofEnabled (label : X → Label) (D : X → Set Action)
    (F : ∀ x a, a ∈ D x → X) (x : X) : enabled (ofEnabled label D F) x = D x := by
  classical
  ext a
  by_cases ha : a ∈ D x <;> simp [enabled, ofEnabled, ha]

/-- Recover the typed legal successor without assigning disabled-action values. -/
noncomputable def legalSuccessor (M : System X Action Label) (x : X) (a : Action)
    (ha : a ∈ enabled M x) : X :=
  Classical.choose ((mem_enabled_iff M x a).mp ha)

theorem legalSuccessor_spec (M : System X Action Label) (x : X) (a : Action)
    (ha : a ∈ enabled M x) : M.step x a = some (legalSuccessor M x a ha) :=
  Classical.choose_spec ((mem_enabled_iff M x a).mp ha)

/-- Translating a partial system to legal-only successors and back changes nothing. -/
theorem ofEnabled_reconstruct (M : System X Action Label) :
    ofEnabled M.label (enabled M) (legalSuccessor M) = M := by
  apply System.ext
  · rfl
  · funext x a
    by_cases ha : a ∈ enabled M x
    · exact (ofEnabled_step_of_mem _ _ _ x a ha).trans (legalSuccessor_spec M x a ha).symm
    · exact (ofEnabled_step_of_not_mem _ _ _ x a ha).trans ((not_enabled_iff M x a).mp ha).symm

/-- The source's three separate equations for quotient data. -/
structure Factors (M : System X Action Label) (Q : System Z Action Label) (π : X → Z) : Prop where
  label_eq : ∀ x, M.label x = Q.label (π x)
  enabled_eq : ∀ x, enabled M x = enabled Q (π x)
  successor_eq : ∀ x a y, M.step x a = some y → Q.step (π x) a = some (π y)

/-- The three actual input conditions on equal fibres, before a quotient is constructed. -/
structure FibreCompatible (M : System X Action Label) (π : X → Z) : Prop where
  label_eq : ∀ x y, π x = π y → M.label x = M.label y
  enabled_eq : ∀ x y, π x = π y → enabled M x = enabled M y
  successor_eq : ∀ x y a x' y', π x = π y →
    M.step x a = some x' → M.step y a = some y' → π x' = π y'

/-- Legal-domain equations imply equality of the complete canonical partial steps. -/
theorem Factors.step_map {M : System X Action Label} {Q : System Z Action Label} {π : X → Z}
    (h : Factors M Q π) (x : X) (a : Action) :
    Q.step (π x) a = (M.step x a).map π := by
  cases hx : M.step x a with
  | none =>
      have hn : a ∉ enabled M x := (not_enabled_iff M x a).mpr hx
      rw [h.enabled_eq x] at hn
      simpa [hx] using (not_enabled_iff Q (π x) a).mp hn
  | some y => simpa [hx] using h.successor_eq x a y hx

/-- Pointwise partial-step agreement supplies all three source equations. -/
theorem factors_of_label_step (M : System X Action Label) (Q : System Z Action Label) (π : X → Z)
    (hl : ∀ x, M.label x = Q.label (π x))
    (hs : ∀ x a, Q.step (π x) a = (M.step x a).map π) : Factors M Q π := by
  refine ⟨hl, ?_, ?_⟩
  · intro x
    ext a
    simp [enabled, hs]
  · intro x a y hy
    rw [hs, hy]
    rfl

/-- The partial representation is equivalent to, rather than weaker than, the source contract. -/
theorem factors_iff_label_step (M : System X Action Label) (Q : System Z Action Label) (π : X → Z) :
    Factors M Q π ↔
      (∀ x, M.label x = Q.label (π x)) ∧
      (∀ x a, Q.step (π x) a = (M.step x a).map π) :=
  ⟨fun h => ⟨h.label_eq, h.step_map⟩, fun h => factors_of_label_step M Q π h.1 h.2⟩

/-- Necessity uses the actual quotient equations. It does not need surjectivity. -/
theorem compatible_of_factors {M : System X Action Label} {Q : System Z Action Label} {π : X → Z}
    (h : Factors M Q π) : FibreCompatible M π := by
  refine ⟨?_, ?_, ?_⟩
  · intro x y hxy
    rw [h.label_eq x, h.label_eq y, hxy]
  · intro x y hxy
    rw [h.enabled_eq x, h.enabled_eq y, hxy]
  · intro x y a x' y' hxy hx hy
    have hxq := h.successor_eq x a x' hx
    rw [hxy] at hxq
    exact Option.some.inj (hxq.symm.trans (h.successor_eq y a y' hy))

/-- Equal fibres have equal projected partial steps, including equal disabled status. -/
theorem FibreCompatible.step_map_eq {M : System X Action Label} {π : X → Z}
    (h : FibreCompatible M π) (x y : X) (hxy : π x = π y) (a : Action) :
    (M.step x a).map π = (M.step y a).map π := by
  cases hx : M.step x a with
  | none =>
      have hn : a ∉ enabled M x := (not_enabled_iff M x a).mpr hx
      rw [h.enabled_eq x y hxy] at hn
      rw [(not_enabled_iff M y a).mp hn]
  | some x' =>
      have he : a ∈ enabled M x := (mem_enabled_iff M x a).mpr ⟨x',hx⟩
      rw [h.enabled_eq x y hxy] at he
      obtain ⟨y',hy⟩ := (mem_enabled_iff M y a).mp he
      rw [hy]
      exact congrArg some (h.successor_eq x y a x' y' hxy hx hy)

/-- An actual representative of every quotient state, supplied only by surjectivity. -/
noncomputable def representative (π : X → Z) (hs : Function.Surjective π) (z : Z) : X :=
  Classical.choose (hs z)

theorem representative_spec (π : X → Z) (hs : Function.Surjective π) (z : Z) :
    π (representative π hs z) = z := Classical.choose_spec (hs z)

/-- Explicit candidate quotient data, defined by representative labels and projected steps. -/
noncomputable def representativeQuotient (M : System X Action Label) (π : X → Z)
    (hs : Function.Surjective π) : System Z Action Label where
  label z := M.label (representative π hs z)
  step z a := (M.step (representative π hs z) a).map π

/-- Compatibility makes the explicit representative construction a true quotient. -/
theorem representativeQuotient_factors (M : System X Action Label) (π : X → Z)
    (hs : Function.Surjective π) (h : FibreCompatible M π) :
    Factors M (representativeQuotient M π hs) π := by
  apply factors_of_label_step
  · intro x
    exact h.label_eq x _ (representative_spec π hs (π x)).symm
  · intro x a
    exact h.step_map_eq _ x (representative_spec π hs (π x)) a

/-- Core 8.2 existence criterion, proved by constructing quotient data from representatives. -/
theorem exists_quotient_iff (M : System X Action Label) (π : X → Z)
    (hs : Function.Surjective π) :
    (∃ Q : System Z Action Label, Factors M Q π) ↔ FibreCompatible M π :=
  ⟨fun ⟨_,h⟩ => compatible_of_factors h,
    fun h => ⟨representativeQuotient M π hs, representativeQuotient_factors M π hs h⟩⟩

/-- Surjectivity makes the actual partial quotient data unique on its whole domain. -/
theorem quotient_unique (M : System X Action Label) (π : X → Z) (hs : Function.Surjective π)
    (Q R : System Z Action Label) (hQ : Factors M Q π) (hR : Factors M R π) : Q = R := by
  apply System.ext
  · funext z
    obtain ⟨x,rfl⟩ := hs z
    exact (hQ.label_eq x).symm.trans (hR.label_eq x)
  · funext z a
    obtain ⟨x,rfl⟩ := hs z
    exact (hQ.step_map x a).trans (hR.step_map x a).symm

/-- Compatibility is equivalent to existence of exactly one canonical partial quotient. -/
theorem existsUnique_quotient_iff (M : System X Action Label) (π : X → Z)
    (hs : Function.Surjective π) :
    (∃! Q : System Z Action Label, Factors M Q π) ↔ FibreCompatible M π := by
  constructor
  · intro h
    exact (exists_quotient_iff M π hs).mp h.exists
  · intro h
    obtain ⟨Q,hQ⟩ := (exists_quotient_iff M π hs).mpr h
    exact ⟨Q,hQ, fun R hR => quotient_unique M π hs R Q hR hQ⟩

/-- Source-facing finite institutional-state and finite-action version of Core 8.2. -/
theorem finite_legal_quotient [Fintype X] [Fintype Action]
    (M : System X Action Label) (π : X → Z) (hs : Function.Surjective π) :
    (∃! Q : System Z Action Label, Factors M Q π) ↔ FibreCompatible M π :=
  existsUnique_quotient_iff M π hs

/-- The canonical partial compatibility test is exactly the source's raw-input test. -/
theorem ofEnabled_fibre_iff (label : X → Label) (D : X → Set Action)
    (F : ∀ x a, a ∈ D x → X) (π : X → Z) :
    FibreCompatible (ofEnabled label D F) π ↔
      (∀ x y, π x = π y → label x = label y) ∧
      (∀ x y, π x = π y → D x = D y) ∧
      (∀ x y a, π x = π y → ∀ hx : a ∈ D x, ∀ hy : a ∈ D y,
        π (F x a hx) = π (F y a hy)) := by
  constructor
  · intro h
    refine ⟨h.label_eq, ?_, ?_⟩
    · intro x y hxy
      simpa only [enabled_ofEnabled] using h.enabled_eq x y hxy
    · intro x y a hxy hx hy
      exact h.successor_eq x y a _ _ hxy
        (ofEnabled_step_of_mem label D F x a hx)
        (ofEnabled_step_of_mem label D F y a hy)
  · rintro ⟨hl,hd,hf⟩
    refine ⟨hl, ?_, ?_⟩
    · intro x y hxy
      simpa only [enabled_ofEnabled] using hd x y hxy
    · intro x y a x' y' hxy hx hy
      have hmx : a ∈ D x := by
        simpa only [enabled_ofEnabled] using
          (mem_enabled_iff (ofEnabled label D F) x a).mpr ⟨x',hx⟩
      have hmy : a ∈ D y := by
        simpa only [enabled_ofEnabled] using
          (mem_enabled_iff (ofEnabled label D F) y a).mpr ⟨y',hy⟩
      have heX : F x a hmx = x' :=
        Option.some.inj ((ofEnabled_step_of_mem label D F x a hmx).symm.trans hx)
      have heY : F y a hmy = y' :=
        Option.some.inj ((ofEnabled_step_of_mem label D F y a hmy).symm.trans hy)
      rw [← heX, ← heY]
      exact hf x y a hxy hmx hmy

/-- Core 8.2 stated directly for finite states, supplied permissions and legal successors. -/
theorem finite_source_legal_quotient [Fintype X] [Fintype Action]
    (label : X → Label) (D : X → Set Action) (F : ∀ x a, a ∈ D x → X)
    (π : X → Z) (hs : Function.Surjective π) :
    (∃! Q : System Z Action Label, Factors (ofEnabled label D F) Q π) ↔
      (∀ x y, π x = π y → label x = label y) ∧
      (∀ x y, π x = π y → D x = D y) ∧
      (∀ x y a, π x = π y → ∀ hx : a ∈ D x, ∀ hy : a ∈ D y,
        π (F x a hx) = π (F y a hy)) :=
  (finite_legal_quotient (ofEnabled label D F) π hs).trans (ofEnabled_fibre_iff label D F π)

end Komorebi.MachineTheory.LegalQuotient
