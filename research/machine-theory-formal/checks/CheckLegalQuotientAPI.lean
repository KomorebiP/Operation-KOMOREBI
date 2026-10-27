import MachineTheory.LegalQuotientExamples
import Mathlib.Data.Fintype.EquivFin

/-! Source-facing tests retain finite states/actions, the supplied legal-only
successor domain, surjectivity, and arbitrary finite action words. -/
open Komorebi.MachineTheory LegalQuotient

section Source
variable {X Z Action Label : Type*} [Fintype X] [Fintype Action]

example (label : X → Label) (D : X → Set Action) (F : ∀ x a, a ∈ D x → X)
    (π : X → Z) (hs : Function.Surjective π) :
    (∃! Q : System Z Action Label, Factors (ofEnabled label D F) Q π) ↔
      (∀ x y, π x = π y → label x = label y) ∧
      (∀ x y, π x = π y → D x = D y) ∧
      (∀ x y a, π x = π y → ∀ hx : a ∈ D x, ∀ hy : a ∈ D y,
        π (F x a hx) = π (F y a hy)) :=
  finite_source_legal_quotient label D F π hs

example (M : System X Action Label) (π : X → Z) (hs : Function.Surjective π) :
    (∃! Q : System Z Action Label, Factors M Q π) ↔
      FibreCompatible M π :=
  finite_legal_quotient M π hs

example (label : X → Label) (D : X → Set Action)
    (F : ∀ x a, a ∈ D x → X) (x : X) :
    enabled (ofEnabled label D F) x = D x :=
  enabled_ofEnabled label D F x

example (label : X → Label) (D : X → Set Action)
    (F : ∀ x a, a ∈ D x → X) (x : X) (a : Action) (ha : a ∈ D x) :
    (ofEnabled label D F).step x a = some (F x a ha) :=
  ofEnabled_step_of_mem label D F x a ha

example (M : System X Action Label) (Q : System Z Action Label) (π : X → Z) :
    Factors M Q π ↔
      (∀ x, M.label x = Q.label (π x)) ∧
      (∀ x a, Q.step (π x) a = (M.step x a).map π) :=
  factors_iff_label_step M Q π

example {M : System X Action Label} {Q : System Z Action Label} {π : X → Z}
    (h : Factors M Q π) (x : X) (word : List Action) :
    (Legal Q (π x) word ↔ Legal M x word) ∧
      execute Q (π x) word = (execute M x word).map (List.map π) ∧
      labels Q (π x) word = labels M x word :=
  finite_legal_quotient_sequences h x word
end Source

open LegalQuotientExamples

example (x : FineState) (word : List Bool) :
    (Legal coarse (forgetHistory x) word ↔ Legal fine x word) ∧
    labels coarse (forgetHistory x) word = labels fine x word :=
  ⟨history_quotient_factors.legal_iff x word, history_quotient_factors.labels_eq x word⟩

example : execute fine (true,false) [true,false] =
      some [(true,false),(false,true),(false,false)] ∧
    execute coarse true [true,true] = none :=
  ⟨repair_then_observe.1, repeated_repair_refused.2⟩

example : Factors oneSource offImage₀ onlyFalse ∧
    Factors oneSource offImage₁ onlyFalse ∧ offImage₀ ≠ offImage₁ :=
  missing_surjectivity_two_quotients
