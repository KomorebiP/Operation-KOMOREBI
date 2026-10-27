import KTG.Basic

namespace KTG

universe u v

/-- Minimal action data. Algebraic action laws can be added later when a concrete
    application needs them. -/
structure KAction (Γ : Type u) (X : Type v) where
  act : Γ → X → X

/-- An object is coric for an action if every transformation fixes it exactly.
    Later versions may replace equality by canonical isomorphism. -/
def Coric {Γ : Type u} {X : Type v} (A : KAction Γ X) (x : X) : Prop :=
  ∀ γ, A.act γ x = x

/-- Bi-coricity with respect to two independent transformation families. -/
def BiCoric
    {Γ₁ : Type u} {Γ₂ : Type v} {X : Type (max u v)}
    (A₁ : KAction Γ₁ X) (A₂ : KAction Γ₂ X) (x : X) : Prop :=
  Coric A₁ x ∧ Coric A₂ x

end KTG
