import Std

namespace KTG

universe u v w

/-- `φ` factors through a public abstraction map `q`. This is the precise safety
    condition for hiding internal data from a downstream observable. -/
structure FactorsThrough
    {Z : Type u} {Q : Type v} {Λ : Type w}
    (q : Z → Q) (φ : Z → Λ) where
  publicValue : Q → Λ
  factor : ∀ z, φ z = publicValue (q z)

/-- Safely hidden internal states with the same public abstraction have the same
    observable value. -/
theorem same_fiber_same_value
    {Z : Type u} {Q : Type v} {Λ : Type w}
    {q : Z → Q} {φ : Z → Λ}
    (h : FactorsThrough q φ)
    {z₁ z₂ : Z} (hq : q z₁ = q z₂) :
    φ z₁ = φ z₂ := by
  rw [h.factor z₁, h.factor z₂, hq]

end KTG
