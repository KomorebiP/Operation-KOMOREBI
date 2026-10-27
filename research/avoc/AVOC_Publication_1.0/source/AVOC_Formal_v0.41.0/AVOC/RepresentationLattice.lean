import AVOC.OpenWorld

namespace Komorebi.AVOC

universe u v w z

/-- Pairing two representations keeps every distinction visible in either. -/
def JoinEncoding
    {X : Type u} {A : Type v} {B : Type w}
    (φ : X → A) (ψ : X → B) : X → A × B :=
  fun x => (φ x, ψ x)

/-- The joint representation refines its left component. -/
theorem join_refines_left
    {X : Type u} {A : Type v} {B : Type w}
    (φ : X → A) (ψ : X → B) :
    Refines (JoinEncoding φ ψ) φ := by
  exact ⟨Prod.fst, by intro x; rfl⟩

/-- The joint representation refines its right component. -/
theorem join_refines_right
    {X : Type u} {A : Type v} {B : Type w}
    (φ : X → A) (ψ : X → B) :
    Refines (JoinEncoding φ ψ) ψ := by
  exact ⟨Prod.snd, by intro x; rfl⟩

/-- Any representation refining both components also refines their joint
representation. -/
theorem refines_join_of_refines_both
    {X : Type u} {C : Type z} {A : Type v} {B : Type w}
    {χ : X → C} {φ : X → A} {ψ : X → B}
    (hφ : Refines χ φ) (hψ : Refines χ ψ) :
    Refines χ (JoinEncoding φ ψ) := by
  rcases hφ with ⟨dφ, hdφ⟩
  rcases hψ with ⟨dψ, hdψ⟩
  refine ⟨fun c => (dφ c, dψ c), ?_⟩
  intro x
  simp [JoinEncoding, hdφ x, hdψ x]

/-- Universal property of the representation join. -/
theorem refines_join_iff
    {X : Type u} {C : Type z} {A : Type v} {B : Type w}
    {χ : X → C} {φ : X → A} {ψ : X → B} :
    Refines χ (JoinEncoding φ ψ) ↔ Refines χ φ ∧ Refines χ ψ := by
  constructor
  · intro h
    exact ⟨refines_trans h (join_refines_left φ ψ),
      refines_trans h (join_refines_right φ ψ)⟩
  · rintro ⟨hφ, hψ⟩
    exact refines_join_of_refines_both hφ hψ

/-- Joining context cannot destroy exact task sufficiency inherited from the
left representation. -/
theorem join_sufficient_of_left
    {X : Type u} {A : Type v} {B : Type w} {Y : Type z}
    {φ : X → A} {ψ : X → B} {T : X → Y}
    (h : TaskSufficient φ T) :
    TaskSufficient (JoinEncoding φ ψ) T := by
  exact sufficient_of_refines (join_refines_left φ ψ) h

/-- Joining context cannot destroy exact task sufficiency inherited from the
right representation. -/
theorem join_sufficient_of_right
    {X : Type u} {A : Type v} {B : Type w} {Y : Type z}
    {φ : X → A} {ψ : X → B} {T : X → Y}
    (h : TaskSufficient ψ T) :
    TaskSufficient (JoinEncoding φ ψ) T := by
  exact sufficient_of_refines (join_refines_right φ ψ) h

/-- A joint representation is sufficient for both tasks whenever the two
component representations separately preserve their respective tasks. -/
theorem join_preserves_two_tasks
    {X : Type u} {A : Type v} {B : Type w} {Y₁ : Type z} {Y₂ : Type*}
    {φ : X → A} {ψ : X → B} {T₁ : X → Y₁} {T₂ : X → Y₂}
    (h₁ : TaskSufficient φ T₁) (h₂ : TaskSufficient ψ T₂) :
    TaskSufficient (JoinEncoding φ ψ) (fun x => (T₁ x, T₂ x)) := by
  rcases h₁ with ⟨d₁, hd₁⟩
  rcases h₂ with ⟨d₂, hd₂⟩
  refine ⟨fun p => (d₁ p.1, d₂ p.2), ?_⟩
  intro x
  simp [JoinEncoding, hd₁ x, hd₂ x]

end Komorebi.AVOC
