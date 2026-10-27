import Komorebi.Foundation.SetCodingBridge

/-!
# Eliminating the external cardinal comparison from the set-coded sentence

Smallness below an initial ordinal K is expressed by a set-coded injection into
some member of K. No cardinality predicate is added to the membership language.
-/

universe u

namespace Komorebi.SetFilterCoding

noncomputable def graph (X Y : ZFSet.{u}) (f : Carrier X → Carrier Y) : ZFSet.{u} :=
  ZFSet.range (fun x => ZFSet.pair (element X x) (element Y (f x)))

theorem pair_mem_graph (X Y : ZFSet.{u}) (f : Carrier X → Carrier Y)
    (x y : ZFSet.{u}) :
    ZFSet.pair x y ∈ graph X Y f ↔ ∃ a, element X a = x ∧ element Y (f a) = y := by
  simp [graph, ZFSet.mem_range, ZFSet.pair_inj]

theorem graph_isFunc (X Y : ZFSet.{u}) (f : Carrier X → Carrier Y) :
    ZFSet.IsFunc X Y (graph X Y f) := by
  constructor
  · intro z hz
    obtain ⟨a, rfl⟩ := ZFSet.mem_range.mp hz
    exact ZFSet.pair_mem_prod.mpr ⟨element_mem X a, element_mem Y (f a)⟩
  · intro z hz
    obtain ⟨a, rfl⟩ := exists_element X hz
    refine ⟨element Y (f a), (pair_mem_graph X Y f _ _).mpr ⟨a, rfl, rfl⟩, ?_⟩
    intro y hy
    obtain ⟨b, hb, he⟩ := (pair_mem_graph X Y f _ _).mp hy
    simpa only [element_injective X hb] using he.symm

/-- Everything here is an ordinary set with membership and equality. -/
def SetEmbeds (X Y : ZFSet.{u}) : Prop :=
  ∃ G : ZFSet.{u}, ZFSet.IsFunc X Y G ∧
    ∀ x ∈ X, ∀ y ∈ X, ∀ z : ZFSet.{u},
      ZFSet.pair x z ∈ G → ZFSet.pair y z ∈ G → x = y

theorem setEmbeds_iff (X Y : ZFSet.{u}) :
    SetEmbeds X Y ↔ Nonempty (Carrier X ↪ Carrier Y) := by
  classical
  constructor
  · rintro ⟨G, hg, hi⟩
    have ht : ∀ a : Carrier X, ∃ b : Carrier Y,
        ZFSet.pair (element X a) (element Y b) ∈ G := by
      intro a
      obtain ⟨y, hy, _⟩ := hg.2 (element X a) (element_mem X a)
      have hyY := (ZFSet.pair_mem_prod.mp (hg.1 hy)).2
      obtain ⟨b, rfl⟩ := exists_element Y hyY
      exact ⟨b, hy⟩
    choose f hf using ht
    refine ⟨⟨f, ?_⟩⟩
    intro a b he
    apply element_injective X
    exact hi _ (element_mem X a) _ (element_mem X b) _ (hf a) (by simpa [he] using hf b)
  · rintro ⟨f⟩
    refine ⟨graph X Y f, graph_isFunc X Y f, ?_⟩
    intro x _ y _ z hx hy
    obtain ⟨a, ha, haz⟩ := (pair_mem_graph X Y f x z).mp hx
    obtain ⟨b, hb, hbz⟩ := (pair_mem_graph X Y f y z).mp hy
    have he : a = b := f.injective (element_injective Y (haz.trans hbz.symm))
    exact ha.symm.trans ((congrArg (element X) he).trans hb)

theorem setEmbeds_iff_card_le (X Y : ZFSet.{u}) :
    SetEmbeds X Y ↔ X.card ≤ Y.card :=
  (setEmbeds_iff X Y).trans (Cardinal.le_def (Carrier X) (Carrier Y)).symm

/-- A small set embeds into an ordinal strictly below the initial ordinal K. -/
def SetSmall (K S : ZFSet.{u}) : Prop := ∃ a ∈ K, SetEmbeds S a

theorem setSmall_initial_iff (κ : Cardinal.{u}) (S : ZFSet.{u}) :
    SetSmall κ.ord.toZFSet S ↔ S.card < κ := by
  simp only [SetSmall, Ordinal.mem_toZFSet_iff, setEmbeds_iff_card_le]
  constructor
  · rintro ⟨a, ⟨o, ho, rfl⟩, hs⟩
    rw [Ordinal.card_toZFSet] at hs
    exact hs.trans_lt (Cardinal.lt_ord.mp ho)
  · intro hs
    refine ⟨S.card.ord.toZFSet, ⟨S.card.ord, Cardinal.ord_lt_ord.mpr hs, rfl⟩, ?_⟩
    simp [Ordinal.card_toZFSet]

/-- The completeness definition now uses only set-coded size witnesses. -/
def InternalComplete (K X F : ZFSet.{u}) : Prop :=
  ∀ S : ZFSet.{u}, S ⊆ F → SetSmall K S → relInter X S ∈ F

theorem internalComplete_initial_iff (κ : Cardinal.{u}) (X F : ZFSet.{u}) :
    InternalComplete κ.ord.toZFSet X F ↔ SetComplete κ X F := by
  simp only [InternalComplete, SetComplete, setSmall_initial_iff]

/-- A wholly set-quantified extension predicate with one set parameter K. -/
def InternalExtension (K : ZFSet.{u}) : Prop :=
  ∀ X F : ZFSet.{u}, IsProperSetFilter X F → InternalComplete K X F →
    ∃ U : ZFSet.{u}, IsSetUltrafilter X U ∧ F ⊆ U ∧ InternalComplete K X U

theorem internalExtension_initial_iff (κ : Cardinal.{u}) :
    InternalExtension κ.ord.toZFSet ↔ SetCompleteFilterExtension κ := by
  simp only [InternalExtension, SetCompleteFilterExtension, SetExtensionAt,
    internalComplete_initial_iff]

theorem internalExtension_iff_extension (κ : Cardinal.{u}) :
    InternalExtension κ.ord.toZFSet ↔ CompactnessClassification.CompleteFilterExtension κ :=
  (internalExtension_initial_iff κ).trans (setExtension_iff_extension κ)

theorem internalExtension_iff_residual (κ : Cardinal.{u}) (hκ : κ.IsRegular) :
    InternalExtension κ.ord.toZFSet ↔ CompactnessClassification.FixedDomainKRR κ :=
  (internalExtension_initial_iff κ).trans (setExtension_iff_residual κ hκ)

end Komorebi.SetFilterCoding
