import Komorebi.Foundation.ResidualClassification
import Mathlib.SetTheory.ZFC.Cardinal

/-!
# Set-coded filters and bounded intersections

All carriers, subsets, and families are genuine ZFSet objects. Carrier types are
shrunk only to align their external universe with the existing compactness API.
The arbitrary-family intersection is relative to X, including the empty family.
-/

universe u

namespace Komorebi.SetFilterCoding

open Set Filter

noncomputable def Carrier (X : ZFSet.{u}) : Type u := Shrink X

noncomputable def element (X : ZFSet.{u}) (x : Carrier X) : ZFSet.{u} :=
  ((equivShrink X).symm x).val

theorem element_mem (X : ZFSet.{u}) (x : Carrier X) : element X x ∈ X :=
  ((equivShrink X).symm x).property

theorem element_injective (X : ZFSet.{u}) : Function.Injective (element X) := by
  intro x y h
  exact (equivShrink X).symm.injective (Subtype.ext h)

theorem exists_element (X : ZFSet.{u}) {z : ZFSet.{u}} (hz : z ∈ X) :
    ∃ x : Carrier X, element X x = z :=
  ⟨equivShrink X ⟨z, hz⟩, by simp [element]⟩

noncomputable def encode (X : ZFSet.{u}) (s : Set (Carrier X)) : ZFSet.{u} :=
  ZFSet.range (fun x : s => element X x.val)

def decode (X S : ZFSet.{u}) : Set (Carrier X) := {x | element X x ∈ S}

theorem mem_encode (X : ZFSet.{u}) (s : Set (Carrier X)) (z : ZFSet.{u}) :
    z ∈ encode X s ↔ ∃ x ∈ s, element X x = z := by
  simp [encode, ZFSet.mem_range]

theorem encode_subset (X : ZFSet.{u}) (s : Set (Carrier X)) : encode X s ⊆ X := by
  intro z hz
  obtain ⟨x, _, rfl⟩ := (mem_encode X s z).mp hz
  exact element_mem X x

@[simp]
theorem decode_encode (X : ZFSet.{u}) (s : Set (Carrier X)) :
    decode X (encode X s) = s := by
  ext x
  simp only [decode, Set.mem_ofPred_eq, mem_encode]
  constructor
  · rintro ⟨y, hy, he⟩
    exact (element_injective X he) ▸ hy
  · intro hx
    exact ⟨x, hx, rfl⟩

theorem encode_decode (X S : ZFSet.{u}) (hS : S ⊆ X) :
    encode X (decode X S) = S := by
  apply ZFSet.ext
  intro z
  rw [mem_encode]
  constructor
  · rintro ⟨x, hx, rfl⟩
    exact hx
  · intro hz
    obtain ⟨x, rfl⟩ := exists_element X (hS hz)
    exact ⟨x, hz, rfl⟩

theorem encode_injective (X : ZFSet.{u}) : Function.Injective (encode X) := by
  intro s t h
  simpa using congrArg (decode X) h

@[simp]
theorem encode_empty (X : ZFSet.{u}) : encode X ∅ = ∅ := by
  apply ZFSet.ext
  intro z
  simp [mem_encode]

@[simp]
theorem encode_univ (X : ZFSet.{u}) : encode X Set.univ = X := by
  apply ZFSet.ext
  intro z
  constructor
  · exact fun hz => encode_subset X Set.univ hz
  · intro hz
    obtain ⟨x, rfl⟩ := exists_element X hz
    exact (mem_encode X Set.univ _).mpr ⟨x, Set.mem_univ _, rfl⟩

theorem encode_mono (X : ZFSet.{u}) {s t : Set (Carrier X)} (h : s ⊆ t) :
    encode X s ⊆ encode X t := by
  intro z hz
  obtain ⟨x, hx, rfl⟩ := (mem_encode X s z).mp hz
  exact (mem_encode X t _).mpr ⟨x, h hx, rfl⟩

@[simp]
theorem encode_inter (X : ZFSet.{u}) (s t : Set (Carrier X)) :
    encode X (s ∩ t) = encode X s ∩ encode X t := by
  apply ZFSet.ext
  intro z
  simp only [ZFSet.mem_inter, mem_encode, Set.mem_inter_iff]
  constructor
  · rintro ⟨x, ⟨hs, ht⟩, rfl⟩
    exact ⟨⟨x, hs, rfl⟩, ⟨x, ht, rfl⟩⟩
  · rintro ⟨⟨x, hx, rfl⟩, ⟨y, hy, he⟩⟩
    exact ⟨x, ⟨hx, (element_injective X he) ▸ hy⟩, rfl⟩

@[simp]
theorem encode_compl (X : ZFSet.{u}) (s : Set (Carrier X)) :
    encode X sᶜ = X \ encode X s := by
  apply ZFSet.ext
  intro z
  rw [ZFSet.mem_sdiff]
  constructor
  · intro hz
    obtain ⟨x, hx, rfl⟩ := (mem_encode X sᶜ z).mp hz
    refine ⟨element_mem X x, ?_⟩
    intro he
    have : x ∈ decode X (encode X s) := he
    exact hx (by simpa using this)
  · rintro ⟨hz, hn⟩
    obtain ⟨x, rfl⟩ := exists_element X hz
    apply (mem_encode X sᶜ _).mpr
    exact ⟨x, fun hx => hn ((mem_encode X s _).mpr ⟨x, hx, rfl⟩), rfl⟩

noncomputable def encodeFamily (X : ZFSet.{u}) (S : Set (Set (Carrier X))) : ZFSet.{u} :=
  ZFSet.range (fun s : S => encode X s.val)

def decodeFamily (X F : ZFSet.{u}) : Set (Set (Carrier X)) := {s | encode X s ∈ F}

@[simp]
theorem mem_encodeFamily (X : ZFSet.{u}) (S : Set (Set (Carrier X)))
    (t : ZFSet.{u}) : t ∈ encodeFamily X S ↔ ∃ s ∈ S, encode X s = t := by
  simp [encodeFamily, ZFSet.mem_range]

@[simp]
theorem decodeFamily_encodeFamily (X : ZFSet.{u}) (S : Set (Set (Carrier X))) :
    decodeFamily X (encodeFamily X S) = S := by
  ext s
  simp only [decodeFamily, Set.mem_ofPred_eq, mem_encodeFamily]
  constructor
  · rintro ⟨t, ht, he⟩
    exact (encode_injective X he) ▸ ht
  · intro hs
    exact ⟨s, hs, rfl⟩

theorem encodeFamily_subset (X : ZFSet.{u}) (S : Set (Set (Carrier X))) :
    encodeFamily X S ⊆ X.powerset := by
  intro t ht
  obtain ⟨s, _, rfl⟩ := (mem_encodeFamily X S t).mp ht
  exact ZFSet.mem_powerset.mpr (encode_subset X s)

theorem encodeFamily_decodeFamily (X F : ZFSet.{u}) (hF : F ⊆ X.powerset) :
    encodeFamily X (decodeFamily X F) = F := by
  apply ZFSet.ext
  intro t
  rw [mem_encodeFamily]
  constructor
  · rintro ⟨s, hs, rfl⟩
    exact hs
  · intro ht
    have he := encode_decode X t (ZFSet.mem_powerset.mp (hF ht))
    exact ⟨decode X t, by simpa [decodeFamily, he] using ht, he⟩

/-- The bounded intersection equals X, not the empty set, on the empty family. -/
def relInter (X S : ZFSet.{u}) : ZFSet.{u} :=
  X.sep (fun x => ∀ s ∈ S, x ∈ s)

@[simp]
theorem relInter_empty (X : ZFSet.{u}) : relInter X ∅ = X := by
  apply ZFSet.ext
  intro z
  simp [relInter]

@[simp]
theorem encode_sInter (X : ZFSet.{u}) (S : Set (Set (Carrier X))) :
    encode X (⋂₀ S) = relInter X (encodeFamily X S) := by
  apply ZFSet.ext
  intro z
  simp only [relInter, ZFSet.mem_sep]
  constructor
  · intro hz
    obtain ⟨x, hx, rfl⟩ := (mem_encode X (⋂₀ S) z).mp hz
    refine ⟨element_mem X x, ?_⟩
    intro t ht
    obtain ⟨s, hs, rfl⟩ := (mem_encodeFamily X S t).mp ht
    exact (mem_encode X s _).mpr ⟨x, hx s hs, rfl⟩
  · rintro ⟨hz, h⟩
    obtain ⟨x, rfl⟩ := exists_element X hz
    apply (mem_encode X (⋂₀ S) _).mpr
    refine ⟨x, ?_, rfl⟩
    intro s hs
    have he : x ∈ decode X (encode X s) := h _ ((mem_encodeFamily X S _).mpr ⟨s, hs, rfl⟩)
    simpa using he

/-- Pure membership and set operations, without an external filter in the definition. -/
structure IsSetFilter (X F : ZFSet.{u}) : Prop where
  bounded : F ⊆ X.powerset
  top : X ∈ F
  upward : ∀ S T, S ∈ F → S ⊆ T → T ⊆ X → T ∈ F
  meet : ∀ S T, S ∈ F → T ∈ F → S ∩ T ∈ F

def IsProperSetFilter (X F : ZFSet.{u}) : Prop := IsSetFilter X F ∧ (∅ : ZFSet) ∉ F

def IsSetUltrafilter (X F : ZFSet.{u}) : Prop :=
  IsSetFilter X F ∧ ∀ S, S ⊆ X → (S ∈ F ↔ X \ S ∉ F)

noncomputable def codeFilter (X : ZFSet.{u}) (F : Filter (Carrier X)) : ZFSet.{u} :=
  encodeFamily X F.sets

@[simp]
theorem encode_mem_codeFilter (X : ZFSet.{u}) (F : Filter (Carrier X))
    (s : Set (Carrier X)) : encode X s ∈ codeFilter X F ↔ s ∈ F := by
  change s ∈ decodeFamily X (encodeFamily X F.sets) ↔ s ∈ F.sets
  rw [decodeFamily_encodeFamily]

theorem codeFilter_isSetFilter (X : ZFSet.{u}) (F : Filter (Carrier X)) :
    IsSetFilter X (codeFilter X F) := by
  refine ⟨encodeFamily_subset X F.sets, ?_, ?_, ?_⟩
  · simpa using (encode_mem_codeFilter X F Set.univ).mpr Filter.univ_mem
  · intro S T hS hST hTX
    have hSX := ZFSet.mem_powerset.mp (encodeFamily_subset X F.sets hS)
    have hs : decode X S ∈ F := (encode_mem_codeFilter X F _).mp (by simpa [encode_decode X S hSX] using hS)
    have ht : decode X T ∈ F := Filter.mem_of_superset hs (fun _ hz => hST hz)
    simpa [encode_decode X T hTX] using (encode_mem_codeFilter X F _).mpr ht
  · intro S T hS hT
    obtain ⟨s, hs, rfl⟩ := (mem_encodeFamily X F.sets S).mp hS
    obtain ⟨t, ht, rfl⟩ := (mem_encodeFamily X F.sets T).mp hT
    simpa using (encode_mem_codeFilter X F (s ∩ t)).mpr (Filter.inter_mem hs ht)

noncomputable def decodeFilter (X F : ZFSet.{u}) (hF : IsSetFilter X F) :
    Filter (Carrier X) where
  sets := decodeFamily X F
  univ_sets := by simpa [decodeFamily] using hF.top
  sets_of_superset := by
    intro s t hs hst
    exact hF.upward _ _ hs (encode_mono X hst) (encode_subset X t)
  inter_sets := by
    intro s t hs ht
    change encode X (s ∩ t) ∈ F
    rw [encode_inter]
    exact hF.meet _ _ hs ht

@[simp]
theorem codeFilter_decodeFilter (X F : ZFSet.{u}) (hF : IsSetFilter X F) :
    codeFilter X (decodeFilter X F hF) = F :=
  encodeFamily_decodeFamily X F hF.bounded

@[simp]
theorem decodeFilter_codeFilter (X : ZFSet.{u}) (F : Filter (Carrier X)) :
    decodeFilter X (codeFilter X F) (codeFilter_isSetFilter X F) = F := by
  apply Filter.ext
  intro s
  exact encode_mem_codeFilter X F s

theorem codeFilter_proper_iff (X : ZFSet.{u}) (F : Filter (Carrier X)) :
    IsProperSetFilter X (codeFilter X F) ↔ F.NeBot := by
  rw [IsProperSetFilter, and_iff_right (codeFilter_isSetFilter X F)]
  have h := encode_mem_codeFilter X F ∅
  rw [encode_empty] at h
  rw [h, Filter.empty_mem_iff_bot, neBot_iff]

theorem codeFilter_ultra (X : ZFSet.{u}) (U : Ultrafilter (Carrier X)) :
    IsSetUltrafilter X (codeFilter X U) := by
  refine ⟨codeFilter_isSetFilter X U, ?_⟩
  intro S hS
  have he := encode_decode X S hS
  rw [← he, ← encode_compl, encode_mem_codeFilter, encode_mem_codeFilter]
  exact (Ultrafilter.compl_notMem_iff).symm


noncomputable def familyEquiv (X : ZFSet.{u}) (S : Set (Set (Carrier X))) :
    S ≃ Carrier (encodeFamily X S) :=
  Equiv.ofBijective
    (fun s => equivShrink (encodeFamily X S)
      ⟨encode X s.val, (mem_encodeFamily X S _).mpr ⟨s.val, s.property, rfl⟩⟩)
    (by
      constructor
      · intro s t h
        have he := congrArg (element (encodeFamily X S)) h
        simp only [element, Equiv.symm_apply_apply] at he
        exact Subtype.ext (encode_injective X he)
      · intro y
        obtain ⟨s, hs, he⟩ := (mem_encodeFamily X S _).mp (element_mem _ y)
        refine ⟨⟨s, hs⟩, ?_⟩
        apply element_injective (encodeFamily X S)
        simpa only [element, Equiv.symm_apply_apply] using he)

theorem card_encodeFamily (X : ZFSet.{u}) (S : Set (Set (Carrier X))) :
    (encodeFamily X S).card = Cardinal.mk S :=
  (Cardinal.mk_congr (familyEquiv X S)).symm

/-- Cardinality is still an external interface here. It is not a hidden formula symbol. -/
def SetComplete (κ : Cardinal.{u}) (X F : ZFSet.{u}) : Prop :=
  ∀ S : ZFSet.{u}, S ⊆ F → S.card < κ → relInter X S ∈ F

theorem codeFilter_complete_iff (κ : Cardinal.{u}) (X : ZFSet.{u})
    (F : Filter (Carrier X)) :
    SetComplete κ X (codeFilter X F) ↔ CardinalInterFilter F κ := by
  constructor
  · intro h
    refine ⟨?_⟩
    intro S hS hm
    have hb : encodeFamily X S ⊆ codeFilter X F := by
      intro s hs
      obtain ⟨t, ht, rfl⟩ := (mem_encodeFamily X S s).mp hs
      exact (encode_mem_codeFilter X F t).mpr (hm t ht)
    have hc := h (encodeFamily X S) hb (by simpa [card_encodeFamily] using hS)
    rw [← encode_sInter, encode_mem_codeFilter] at hc
    exact hc
  · intro h S hSF hS
    let : CardinalInterFilter F κ := h
    have hSP : S ⊆ X.powerset := fun _ hs => (codeFilter_isSetFilter X F).bounded (hSF hs)
    have he := encodeFamily_decodeFamily X S hSP
    have hD : Cardinal.mk (decodeFamily X S) < κ := by
      rw [← card_encodeFamily, he]
      exact hS
    have hm : ∀ s ∈ decodeFamily X S, s ∈ F := by
      intro s hs
      exact (encode_mem_codeFilter X F s).mp (hSF hs)
    have hc := (cardinal_sInter_mem hD).mpr hm
    have hec := (encode_mem_codeFilter X F _).mpr hc
    simpa only [encode_sInter, he] using hec

noncomputable def decodeUltrafilter (X F : ZFSet.{u}) (hF : IsSetUltrafilter X F) :
    Ultrafilter (Carrier X) :=
  Ultrafilter.ofComplNotMemIff (decodeFilter X F hF.1) (by
    intro s
    change encode X sᶜ ∉ F ↔ encode X s ∈ F
    rw [encode_compl]
    exact (hF.2 (encode X s) (encode_subset X s)).symm)

@[simp]
theorem codeFilter_decodeUltrafilter (X F : ZFSet.{u}) (hF : IsSetUltrafilter X F) :
    codeFilter X (decodeUltrafilter X F hF) = F :=
  codeFilter_decodeFilter X F hF.1

theorem codeFilter_subset_iff (X : ZFSet.{u}) (F G : Filter (Carrier X)) :
    codeFilter X F ⊆ codeFilter X G ↔ G ≤ F := by
  constructor
  · intro h s hs
    exact (encode_mem_codeFilter X G s).mp (h ((encode_mem_codeFilter X F s).mpr hs))
  · intro h s hs
    obtain ⟨t, ht, rfl⟩ := (mem_encodeFamily X F.sets s).mp hs
    exact (encode_mem_codeFilter X G t).mpr (h ht)

/-- The set-coded extension statement on one given set. -/
def SetExtensionAt (κ : Cardinal.{u}) (X : ZFSet.{u}) : Prop :=
  ∀ F : ZFSet.{u}, IsProperSetFilter X F → SetComplete κ X F →
    ∃ U : ZFSet.{u}, IsSetUltrafilter X U ∧ F ⊆ U ∧ SetComplete κ X U

theorem setExtensionAt_iff (κ : Cardinal.{u}) (X : ZFSet.{u}) :
    SetExtensionAt κ X ↔
      (∀ F : Filter (Carrier X), F.NeBot → CardinalInterFilter F κ →
        ∃ U : Ultrafilter (Carrier X), (U : Filter (Carrier X)) ≤ F ∧
          CardinalInterFilter (U : Filter (Carrier X)) κ) := by
  constructor
  · intro h F hp hc
    obtain ⟨U, hU, hFU, hcomp⟩ := h (codeFilter X F)
      ((codeFilter_proper_iff X F).mpr hp) ((codeFilter_complete_iff κ X F).mpr hc)
    refine ⟨decodeUltrafilter X U hU, ?_, ?_⟩
    · apply (codeFilter_subset_iff X F _).mp
      simpa using hFU
    · apply (codeFilter_complete_iff κ X _).mp
      simpa using hcomp
  · intro h F hp hc
    let f := decodeFilter X F hp.1
    have hf : codeFilter X f = F := codeFilter_decodeFilter X F hp.1
    obtain ⟨U, hU, hcomp⟩ := h f
      ((codeFilter_proper_iff X f).mp (by simpa [hf] using hp))
      ((codeFilter_complete_iff κ X f).mp (by simpa [hf] using hc))
    refine ⟨codeFilter X U, codeFilter_ultra X U, ?_,
      (codeFilter_complete_iff κ X U).mpr hcomp⟩
    simpa [hf] using (codeFilter_subset_iff X f U).mpr hU

def SetCompleteFilterExtension (κ : Cardinal.{u}) : Prop :=
  ∀ X : ZFSet.{u}, SetExtensionAt κ X

theorem setExtension_of_extension (κ : Cardinal.{u})
    (h : CompactnessClassification.CompleteFilterExtension κ) :
    SetCompleteFilterExtension κ := by
  intro X
  exact (setExtensionAt_iff κ X).mpr (h (Carrier X))


/-- Regression control: the unbounded ZFSet intersection convention would reject
all proper filters as soon as the empty family is required to be small. -/
theorem absolute_intersection_complete_impossible (κ : Cardinal.{u}) (hκ : 0 < κ)
    (X F : ZFSet.{u}) (hp : IsProperSetFilter X F) :
    ¬ (∀ S : ZFSet.{u}, S ⊆ F → S.card < κ → ZFSet.sInter S ∈ F) := by
  intro h
  have he := h ∅ (by intro z hz; exact (ZFSet.notMem_empty z hz).elim)
    (by simpa using hκ)
  exact hp.2 (by simpa using he)

end Komorebi.SetFilterCoding
