import KomorebiVerification.PaperII.CommonRefinement

/-!
# Finite collections of commuting packet systems

A finite-list induction constructs the coarsest common refinement by supported
binary products. The empty list uses the supported identity family. In a zero
module this support is empty, rather than containing a forbidden zero packet.
-/

set_option autoImplicit false
noncomputable section
namespace Komorebi.PaperII.CommonRefinement

open Komorebi.Foundation Komorebi.PaperII.NestedRefinement

universe u v w z
variable {R : Type u} {M : Type v} [Semiring R] [AddCommMonoid M] [Module R M]

/-- A finite, zero-free packet system with its actual index type. -/
structure Packet (R : Type u) (M : Type v)
    [Semiring R] [AddCommMonoid M] [Module R M] where
  Index : Type w
  indexFintype : Fintype Index
  family : @LinearProjectorFamily R M Index _ _ _ indexFintype
  nonzero : @Nonzero R M _ _ _ Index indexFintype family

attribute [instance] Packet.indexFintype

/-- The second packet is a refinement of the first, using the inherited relation. -/
def HasRefinement (P S : Packet.{u,v,w} R M) : Prop :=
  ∃ parent : S.Index → P.Index, Refines P.family S.family parent

theorem refinement_trans (P Q S : Packet.{u,v,w} R M)
    (hp : HasRefinement P Q) (hq : HasRefinement Q S) : HasRefinement P S := by
  rcases hp with ⟨p, hp⟩
  rcases hq with ⟨q, hq⟩
  exact ⟨p ∘ q, hp.trans hq⟩

/-- The binary meet constructs its own index subtype and both projector axioms. -/
def meetPacket (P Q : Packet.{u,v,w} R M)
    (h : CrossCommutes P.family Q.family) : Packet.{u,v,w} R M where
  Index := Support (product P.family Q.family h)
  indexFintype := inferInstance
  family := common P.family Q.family h
  nonzero := supported_nonzero _

theorem meet_left (P Q : Packet.{u,v,w} R M)
    (h : CrossCommutes P.family Q.family) : HasRefinement P (meetPacket P Q h) :=
  ⟨fun k => k.val.1, common_refines_left P.family Q.family h P.nonzero⟩

theorem meet_right (P Q : Packet.{u,v,w} R M)
    (h : CrossCommutes P.family Q.family) : HasRefinement Q (meetPacket P Q h) :=
  ⟨fun k => k.val.2, common_refines_right P.family Q.family h Q.nonzero⟩

theorem meet_coarsest (P Q S : Packet.{u,v,w} R M)
    (h : CrossCommutes P.family Q.family)
    (hp : HasRefinement P S) (hq : HasRefinement Q S) :
    HasRefinement (meetPacket P Q h) S := by
  rcases hp with ⟨p, hp⟩
  rcases hq with ⟨q, hq⟩
  exact ⟨jointParent P.family Q.family h S.family S.nonzero p q hp hq,
    common_coarsest P.family Q.family h S.family S.nonzero p q hp hq⟩

theorem cross_symm (P Q : Packet.{u,v,w} R M)
    (h : CrossCommutes P.family Q.family) : CrossCommutes Q.family P.family :=
  fun j i x => (h i j x).symm

theorem cross_self (P : Packet.{u,v,w} R M) : CrossCommutes P.family P.family := by
  intro i j x
  by_cases h : i = j
  · subst j
    rfl
  · rw [P.family.orthogonal h, P.family.orthogonal (Ne.symm h)]

/-- A product of two families commuting with a third still commutes with it. -/
theorem meet_cross (P Q S : Packet.{u,v,w} R M)
    (h : CrossCommutes P.family Q.family)
    (hp : CrossCommutes P.family S.family) (hq : CrossCommutes Q.family S.family) :
    CrossCommutes (meetPacket P Q h).family S.family := by
  intro k j x
  change P.family.proj k.val.1 (Q.family.proj k.val.2 (S.family.proj j x)) =
    S.family.proj j (P.family.proj k.val.1 (Q.family.proj k.val.2 x))
  rw [hq k.val.2 j x, hp k.val.1 j (Q.family.proj k.val.2 x)]

/-- A single identity before zero removal, valid even on the zero module. -/
def oneFamily : LinearProjectorFamily R M (ULift.{w} Unit) where
  proj _ := LinearMap.id
  idempotent := by intros; rfl
  orthogonal := by
    intro i j h
    exact False.elim (h (Subsingleton.elim i j))
  complete := by intro x; simp

/-- The actual empty-family meet: identity on a nonzero module, empty on a zero module. -/
def identityPacket : Packet.{u,v,w} R M where
  Index := Support (oneFamily (R := R) (M := M))
  indexFintype := inferInstance
  family := supported oneFamily
  nonzero := supported_nonzero _

theorem identity_cross (P : Packet.{u,v,w} R M) :
    CrossCommutes (identityPacket (R := R) (M := M)).family P.family := by
  intro i j x
  rfl

/-- Every zero-free packet system refines the supported identity family. -/
theorem identity_coarsest (P : Packet.{u,v,w} R M) :
    HasRefinement (identityPacket (R := R) (M := M)) P := by
  classical
  let parent : P.Index → Support (oneFamily (R := R) (M := M)) := fun a =>
    ⟨ULift.up (), by
      intro hz
      have hz' : ∀ x : M, x = 0 := by
        intro x
        exact LinearMap.congr_fun hz x
      exact P.nonzero a (by ext x; exact hz' _)⟩
  refine ⟨parent, refines_of_absorption _ P.family (supported_nonzero _) parent ?_⟩
  intro i a x
  have hi : parent a = i := Subtype.ext (Subsingleton.elim _ _)
  simp only [hi, ↓reduceIte]
  rfl

/-- Binary existence is equivalent to cross commutation; no host is assumed. -/
theorem exists_common_iff (P Q : Packet.{u,v,w} R M) :
    (∃ S : Packet.{u,v,w} R M, HasRefinement P S ∧ HasRefinement Q S) ↔
      CrossCommutes P.family Q.family := by
  constructor
  · rintro ⟨S, ⟨p, hp⟩, ⟨q, hq⟩⟩
    exact commutes_of_common_refinement P.family Q.family S.family p q hp hq
  · intro h
    exact ⟨meetPacket P Q h, meet_left P Q h, meet_right P Q h⟩

/-- Construct a coarsest common refinement for a finite list, allowing repeats. -/
theorem list_common_coarsest {T : Type z} (F : T → Packet.{u,v,w} R M)
    (hc : ∀ s t, CrossCommutes (F s).family (F t).family) (l : List T) :
    ∃ S : Packet.{u,v,w} R M,
      (∀ t, CrossCommutes S.family (F t).family) ∧
      (∀ t ∈ l, HasRefinement (F t) S) ∧
      (∀ U : Packet.{u,v,w} R M,
        (∀ t ∈ l, HasRefinement (F t) U) → HasRefinement S U) := by
  induction l with
  | nil =>
    refine ⟨identityPacket, ?_, ?_, ?_⟩
    · intro t
      exact identity_cross (F t)
    · intro t ht
      simp only [List.not_mem_nil] at ht
    · intro U _
      exact identity_coarsest U
  | cons t l ih =>
    rcases ih with ⟨S, hs, hr, hu⟩
    let h : CrossCommutes (F t).family S.family := cross_symm S (F t) (hs t)
    refine ⟨meetPacket (F t) S h, ?_, ?_, ?_⟩
    · intro s
      exact meet_cross (F t) S (F s) h (hc t s) (hs s)
    · intro s hsl
      rcases List.mem_cons.mp hsl with hst | hsl
      · subst s
        exact meet_left (F t) S h
      · exact refinement_trans (F s) S _ (hr s hsl) (meet_right (F t) S h)
    · intro U hU
      exact meet_coarsest (F t) S U h (hU t (by simp))
        (hu U (fun s hsl => hU s (List.mem_cons_of_mem t hsl)))

/-- The finite-family part of the manuscript theorem, together with its universal property. -/
theorem finite_common_coarsest {T : Type z} [Fintype T]
    (F : T → Packet.{u,v,w} R M)
    (hc : ∀ s t, s ≠ t → CrossCommutes (F s).family (F t).family) :
    ∃ S : Packet.{u,v,w} R M,
      (∀ t, HasRefinement (F t) S) ∧
      (∀ U : Packet.{u,v,w} R M,
        (∀ t, HasRefinement (F t) U) → HasRefinement S U) := by
  classical
  have hc' : ∀ s t, CrossCommutes (F s).family (F t).family := by
    intro s t
    by_cases h : s = t
    · subst t
      exact cross_self (F s)
    · exact hc s t h
  obtain ⟨S, _, hr, hu⟩ := list_common_coarsest F hc' Finset.univ.toList
  refine ⟨S, ?_, ?_⟩
  · intro t
    exact hr t (by simp)
  · intro U hU
    exact hu U (fun t _ => hU t)

end Komorebi.PaperII.CommonRefinement
