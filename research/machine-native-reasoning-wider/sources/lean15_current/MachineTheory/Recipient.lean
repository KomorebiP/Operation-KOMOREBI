import MachineTheory.Behavior
import Mathlib.Data.Finset.Card
import Mathlib.Data.Fintype.Powerset
import Mathlib.Data.Nat.Find

/-!
# Fixed-recipient artifact covering

Core 4.2. The sender is a function on attained records, never on the hidden case.
`ok` is the fixed joint acceptance predicate of all recipients, including their
actual outputs, permission and resource conditions. No decoder is redesigned by
the covering construction. Codebook cardinality is not byte length or execution cost.
-/
namespace Komorebi.MachineTheory.Recipient

universe u v w
variable {X : Type u} {H : Type v} {C : Type w}

/-- Artifacts acceptable in every case compatible with this attained record. -/
def Common (α : X → H) (ok : X → C → Prop) (h : Attained α) (c : C) : Prop :=
  ∀ x, α x = h.val → ok x c

/-- The encoder reads the sender record only. -/
def Valid (α : X → H) (ok : X → C → Prop) (f : Attained α → C) : Prop :=
  ∀ x, ok x (f (record α x))

theorem valid_iff_common (α : X → H) (ok : X → C → Prop) (f : Attained α → C) :
    Valid α ok f ↔ ∀ h, Common α ok h (f h) := by
  constructor
  · intro hf h x hx
    have he : record α x = h := Subtype.ext hx
    simpa only [he] using hf x
  · intro hf x
    exact hf (record α x) x rfl

/-- Core 4.2, existence: only attainable sender records have obligations. -/
theorem encoder_exists_iff (α : X → H) (ok : X → C → Prop) :
    (∃ f : Attained α → C, Valid α ok f) ↔ ∀ h, ∃ c, Common α ok h c := by
  constructor
  · rintro ⟨f, hf⟩ h
    exact ⟨f h, (valid_iff_common α ok f).mp hf h⟩
  · intro h
    classical
    exact ⟨fun z => Classical.choose (h z),
      (valid_iff_common α ok _).mpr (fun z => Classical.choose_spec (h z))⟩

/-- A collision whose acceptance sets are disjoint rules out every encoder. -/
theorem no_encoder_of_disjoint (α : X → H) (ok : X → C → Prop)
    (x y : X) (he : α x = α y) (hd : ∀ c, ¬ (ok x c ∧ ok y c)) :
    ¬ ∃ f : Attained α → C, Valid α ok f := by
  rintro ⟨f, hf⟩
  have hr : record α x = record α y := Subtype.ext he
  exact hd (f (record α x)) ⟨hf x, by simpa only [hr] using hf y⟩

/-- A finite codebook meets every required acceptance intersection. -/
def Hits (α : X → H) (ok : X → C → Prop) (S : Finset C) : Prop :=
  ∀ h, ∃ c, c ∈ S ∧ Common α ok h c

/-- Exactly the distinct artifacts transmitted on attained inputs. -/
noncomputable def image [Fintype X] (α : X → H) (f : Attained α → C) : Finset C := by
  classical
  exact Finset.univ.image f

@[simp] theorem mem_image [Fintype X] (α : X → H) (f : Attained α → C) (c : C) :
    c ∈ image α f ↔ ∃ h, f h = c := by
  classical
  simp [image]

theorem image_hits [Fintype X] (α : X → H) (ok : X → C → Prop)
    (f : Attained α → C) (hf : Valid α ok f) : Hits α ok (image α f) := by
  intro h
  exact ⟨f h, (mem_image α f _).mpr ⟨h, rfl⟩, (valid_iff_common α ok f).mp hf h⟩

/-- Every hitting codebook supplies a valid encoder using only its entries. -/
theorem encoder_within_iff [Fintype X] (α : X → H) (ok : X → C → Prop) (S : Finset C) :
    (∃ f : Attained α → C, Valid α ok f ∧ image α f ⊆ S) ↔ Hits α ok S := by
  constructor
  · rintro ⟨f, hf, hs⟩ h
    exact ⟨f h, hs ((mem_image α f _).mpr ⟨h, rfl⟩),
      (valid_iff_common α ok f).mp hf h⟩
  · intro hs
    classical
    let f : Attained α → C := fun h => Classical.choose (hs h)
    have spec : ∀ h, f h ∈ S ∧ Common α ok h (f h) :=
      fun h => Classical.choose_spec (hs h)
    refine ⟨f, (valid_iff_common α ok f).mpr (fun h => (spec h).2), ?_⟩
    intro c hc
    obtain ⟨h, rfl⟩ := (mem_image α f c).mp hc
    exact (spec h).1

/-- Exact bounded image/cover equivalence, including infeasible and empty cases. -/
theorem cardinality_budget_iff [Fintype X] (α : X → H) (ok : X → C → Prop) (k : ℕ) :
    (∃ f : Attained α → C, Valid α ok f ∧ (image α f).card ≤ k) ↔
      ∃ S : Finset C, Hits α ok S ∧ S.card ≤ k := by
  constructor
  · rintro ⟨f, hf, hk⟩
    exact ⟨image α f, image_hits α ok f hf, hk⟩
  · rintro ⟨S, hs, hk⟩
    obtain ⟨f, hf, hsub⟩ := (encoder_within_iff α ok S).mpr hs
    exact ⟨f, hf, (Finset.card_le_card hsub).trans hk⟩

def Feasible (α : X → H) (ok : X → C → Prop) : Prop :=
  ∃ f : Attained α → C, Valid α ok f

theorem image_size_exists [Fintype X] {α : X → H} {ok : X → C → Prop}
    (h : Feasible α ok) : ∃ n : ℕ, ∃ f : Attained α → C,
      Valid α ok f ∧ (image α f).card = n := by
  obtain ⟨f, hf⟩ := h
  exact ⟨_, f, hf, rfl⟩

theorem cover_size_exists [Fintype X] {α : X → H} {ok : X → C → Prop}
    (h : Feasible α ok) : ∃ n : ℕ, ∃ S : Finset C, Hits α ok S ∧ S.card = n := by
  obtain ⟨f, hf⟩ := h
  exact ⟨_, image α f, image_hits α ok f hf, rfl⟩

noncomputable def minImageSize [Fintype X] {α : X → H} {ok : X → C → Prop}
    (h : Feasible α ok) : ℕ := by
  classical
  exact Nat.find (image_size_exists h)

noncomputable def minCoverSize [Fintype X] {α : X → H} {ok : X → C → Prop}
    (h : Feasible α ok) : ℕ := by
  classical
  exact Nat.find (cover_size_exists h)

theorem minImage_attained [Fintype X] {α : X → H} {ok : X → C → Prop}
    (h : Feasible α ok) : ∃ f : Attained α → C,
      Valid α ok f ∧ (image α f).card = minImageSize h := by
  classical
  exact Nat.find_spec (image_size_exists h)

theorem minCover_attained [Fintype X] {α : X → H} {ok : X → C → Prop}
    (h : Feasible α ok) : ∃ S : Finset C, Hits α ok S ∧ S.card = minCoverSize h := by
  classical
  exact Nat.find_spec (cover_size_exists h)

theorem minImage_le [Fintype X] {α : X → H} {ok : X → C → Prop}
    (h : Feasible α ok) (f : Attained α → C) (hf : Valid α ok f) :
    minImageSize h ≤ (image α f).card := by
  classical
  exact Nat.find_min' (image_size_exists h) ⟨f, hf, rfl⟩

theorem minCover_le [Fintype X] {α : X → H} {ok : X → C → Prop}
    (h : Feasible α ok) (S : Finset C) (hs : Hits α ok S) :
    minCoverSize h ≤ S.card := by
  classical
  exact Nat.find_min' (cover_size_exists h) ⟨S, hs, rfl⟩

/-- Core 4.2, the independently defined minima are equal and are both attained. -/
theorem minimum_image_eq_cover [Fintype X] {α : X → H} {ok : X → C → Prop}
    (h : Feasible α ok) : minImageSize h = minCoverSize h := by
  apply le_antisymm
  · obtain ⟨S, hs, he⟩ := minCover_attained h
    obtain ⟨f, hf, hsub⟩ := (encoder_within_iff α ok S).mpr hs
    exact (minImage_le h f hf).trans ((Finset.card_le_card hsub).trans_eq he)
  · obtain ⟨f, hf, he⟩ := minImage_attained h
    exact (minCover_le h _ (image_hits α ok f hf)).trans_eq he

/-- A minimum codebook is exactly the image of a valid minimizing encoder. -/
theorem minimum_common_artifact [Fintype X] {α : X → H} {ok : X → C → Prop}
    (h : Feasible α ok) :
    ∃ f : Attained α → C, ∃ S : Finset C,
      Valid α ok f ∧ Hits α ok S ∧ image α f = S ∧
      S.card = minCoverSize h ∧
      (∀ g : Attained α → C, Valid α ok g → S.card ≤ (image α g).card) ∧
      (∀ T : Finset C, Hits α ok T → S.card ≤ T.card) := by
  obtain ⟨f, hf, he⟩ := minImage_attained h
  refine ⟨f, image α f, hf, image_hits α ok f hf, rfl, ?_, ?_, ?_⟩
  · exact he.trans (minimum_image_eq_cover h)
  · intro g hg
    rw [he]
    exact minImage_le h g hg
  · intro T hT
    rw [he, minimum_image_eq_cover h]
    exact minCover_le h T hT

/-- More actual sender information cannot increase the minimum image size. -/
theorem access_refinement [Fintype X] {H' : Type*} (α : X → H) (β : X → H')
    (forget : H' → H) (haccess : ∀ x, forget (β x) = α x) (ok : X → C → Prop)
    (f : Attained α → C) (hf : Valid α ok f) :
    ∃ g : Attained β → C, Valid β ok g ∧ image β g = image α f := by
  let down : Attained β → Attained α := fun h =>
    ⟨forget h.val, by obtain ⟨x, hx⟩ := h.property; exact ⟨x, by rw [← hx, haccess]⟩⟩
  have down_record : ∀ x, down (record β x) = record α x :=
    fun x => Subtype.ext (haccess x)
  refine ⟨fun h => f (down h), ?_, ?_⟩
  · intro x
    simpa only [down_record] using hf x
  · ext c
    simp only [mem_image]
    constructor
    · rintro ⟨h, hc⟩
      exact ⟨down h, hc⟩
    · rintro ⟨h, hc⟩
      obtain ⟨x, hx⟩ := h.property
      refine ⟨record β x, ?_⟩
      rw [down_record, show record α x = h from Subtype.ext hx]
      exact hc

/-- A transmitted alphabet is useful only through its fixed installed decoder. -/
theorem decoded_alphabet_bound [Fintype X] {Msg : Type*} [Fintype Msg]
    {α : X → H} {ok : X → C → Prop} (h : Feasible α ok)
    (send : Attained α → Msg) (decode : Msg → C)
    (hv : Valid α ok (decode ∘ send)) : minCoverSize h ≤ Fintype.card Msg := by
  classical
  rw [← minimum_image_eq_cover h]
  apply (minImage_le h _ hv).trans
  have hsub : image α (decode ∘ send) ⊆ Finset.univ.image decode := by
    intro c hc
    obtain ⟨z, rfl⟩ := (mem_image α (decode ∘ send) c).mp hc
    exact Finset.mem_image.mpr ⟨send z, Finset.mem_univ _, rfl⟩
  exact (Finset.card_le_card hsub).trans (by simpa using Finset.card_image_le (s := Finset.univ) (f := decode))

/-- If a unique artifact is needed in each case, every valid encoder has that image. -/
theorem forced_image [Fintype X] [DecidableEq C] (α : X → H) (target : X → C)
    (f : Attained α → C) (hf : Valid α (fun x c => c = target x) f) :
    image α f = Finset.univ.image target := by
  classical
  ext c
  rw [mem_image]
  simp only [Finset.mem_image, Finset.mem_univ, true_and]
  constructor
  · rintro ⟨h, hc⟩
    obtain ⟨x, hx⟩ := h.property
    refine ⟨x, ?_⟩
    have hr : record α x = h := Subtype.ext hx
    exact (hf x).symm.trans (by simpa only [hr] using hc)
  · rintro ⟨x, hx⟩
    exact ⟨record α x, (hf x).trans hx⟩

end Komorebi.MachineTheory.Recipient
