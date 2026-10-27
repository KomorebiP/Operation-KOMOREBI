import Komorebi.Multiverse.WorldNetwork

/-!
# Logical residuals between worlds

This layer abstracts away from how a world evaluates a sentence.  A later
forcing/model-theoretic instantiation may take `Holds w φ` to be satisfaction in
the ZFC model represented by `w`.  The residual is the exact disagreement set.
-/

universe u v

namespace Komorebi.Multiverse

structure WorldSemantics (N : WorldNetwork.{u}) (Sentence : Type v) where
  Holds : N.World → Sentence → Prop

namespace WorldSemantics

variable {N : WorldNetwork.{u}} {Sentence : Type v}
    (T : WorldSemantics N Sentence)

/-- Worlds agree on a chosen fragment `Γ`. -/
def AgreeOn (Γ : Set Sentence) (a b : N.World) : Prop :=
  ∀ φ ∈ Γ, (T.Holds a φ ↔ T.Holds b φ)

/-- The logical residual at a sentence: it lies in the chosen fragment and its
truth value differs between the two worlds. -/
def ResidualAt (Γ : Set Sentence) (a b : N.World) (φ : Sentence) : Prop :=
  φ ∈ Γ ∧ ¬ (T.Holds a φ ↔ T.Holds b φ)

/-- Vanishing of every sentence residual is exactly agreement on the fragment. -/
theorem agreeOn_iff_no_residual (Γ : Set Sentence) (a b : N.World) :
    T.AgreeOn Γ a b ↔ ∀ φ, ¬ T.ResidualAt Γ a b φ := by
  constructor
  · intro h φ hr
    exact hr.2 (h φ hr.1)
  · intro h φ hφ
    by_contra hne
    exact h φ ⟨hφ, hne⟩

/-- Logical disagreement is symmetric. -/
theorem residualAt_symm {Γ : Set Sentence} {a b : N.World} {φ : Sentence}
    (h : T.ResidualAt Γ a b φ) : T.ResidualAt Γ b a φ := by
  refine ⟨h.1, ?_⟩
  intro hab
  exact h.2 hab.symm

/-- Agreement on a fixed fragment is reflexive. -/
theorem agreeOn_refl (Γ : Set Sentence) (a : N.World) : T.AgreeOn Γ a a := by
  intro φ _
  exact Iff.rfl

/-- Agreement on a fixed fragment is symmetric. -/
theorem agreeOn_symm {Γ : Set Sentence} {a b : N.World}
    (h : T.AgreeOn Γ a b) : T.AgreeOn Γ b a := by
  intro φ hφ
  exact (h φ hφ).symm

/-- Agreement on a fixed fragment is transitive. -/
theorem agreeOn_trans {Γ : Set Sentence} {a b c : N.World}
    (hab : T.AgreeOn Γ a b) (hbc : T.AgreeOn Γ b c) : T.AgreeOn Γ a c := by
  intro φ hφ
  exact (hab φ hφ).trans (hbc φ hφ)

end WorldSemantics
end Komorebi.Multiverse

namespace Komorebi.Multiverse
namespace WorldSemantics

variable {N : WorldNetwork.{u}} {Sentence : Type v}
    (T : WorldSemantics N Sentence)

/-- Sentences whose truth is invariant along every admissible world transport. -/
def InvariantFragment : Set Sentence :=
  {φ | ∀ a b : N.World, N.reach a b → (T.Holds a φ ↔ T.Holds b φ)}

/-- Sentences true in every world of the indexed network. -/
def CommonCore : Set Sentence :=
  {φ | ∀ w : N.World, T.Holds w φ}

/-- Reachable worlds have zero logical residual on the transport-invariant fragment. -/
theorem reachable_agree_invariant {a b : N.World} (hab : N.reach a b) :
    T.AgreeOn T.InvariantFragment a b := by
  intro φ hφ
  exact hφ a b hab

/-- Universally true world content is automatically transport-invariant. -/
theorem commonCore_subset_invariant : T.CommonCore ⊆ T.InvariantFragment := by
  intro φ hφ a b _
  exact ⟨fun _ => hφ b, fun _ => hφ a⟩

end WorldSemantics
end Komorebi.Multiverse
