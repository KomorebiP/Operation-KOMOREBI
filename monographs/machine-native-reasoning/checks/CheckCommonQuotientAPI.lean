import MachineTheory.CommonQuotientExamples

open Komorebi.MachineTheory.CommonQuotient

variable {K V Y Z A Θ : Type*}
variable [Field K] [AddCommGroup V] [Module K V] [AddCommGroup Y] [Module K Y]
variable [AddCommGroup Z] [Module K Z]

-- Direct all-vector source statement, not merely a restatement of a presumed quotient.
example (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (Q : V →ₗ[K] Y) :
    (∀ θ w v, Q (wordMap (T θ) w v) = Q (wordMap (T θ₀) w v)) ↔
      discrepancy T θ₀ ≤ LinearMap.ker Q := by
  constructor
  · intro h
    apply discrepancy_invisible_of_agreement T θ₀ Q
    intro θ w
    exact LinearMap.ext (h θ w)
  · intro h θ w v
    exact LinearMap.congr_fun (agreement_of_discrepancy_invisible T θ₀ Q h θ w) v

-- Given actual arbitrary common linear data, the fixed-model source agreement follows.
example (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (Q : V →ₗ[K] Y)
    (r : V →ₗ[K] Z) (G : A → Z →ₗ[K] Z) (q : Z →ₗ[K] Y)
    (h : ∀ θ a, r.comp (T θ a) = (G a).comp r) (hq : Q = q.comp r) :
    ObservableAgreement T θ₀ Q := agreement_of_factor T θ₀ Q r G q h hq

-- Even when source update/readout symbols are only functions, necessity remains valid.
example (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (Q : V →ₗ[K] Y)
    (r : V → Z) (G : A → Z → Z) (q : Z → Y)
    (h : ∀ θ a v, r (T θ a v) = G a (r v)) (hq : ∀ v, Q v = q (r v)) :
    ObservableAgreement T θ₀ Q := agreement_of_function_factor T θ₀ Q r G q h hq

example [Fintype A] [Fintype Θ] [FiniteDimensional K V]
    (T : Θ → A → V →ₗ[K] V) (R : A → V →ₗ[K] V) (θ₀ : Θ)
    (hR : T θ₀ = R) (Q : V →ₗ[K] Y) :
    (∀ θ w, Q.comp (wordMap (T θ) w) = Q.comp (wordMap R w)) ↔
      Nonempty (CommonModel T Q) := (source_core24_reference T R θ₀ hR Q).1

example [FiniteDimensional K V] (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) :
    stage T θ₀ (Module.finrank K V) = discrepancy T θ₀ := stage_finrank_eq T θ₀

example (T : Θ → A → V →ₗ[K] V) (θ₀ : Θ) (Q : V →ₗ[K] Y)
    (h : ObservableAgreement T θ₀ Q) (w : List (Θ × A)) (v : V) :
    Q (switchedMap T w v) = Q (wordMap (T θ₀) (w.map Prod.snd) v) :=
  switching_output T θ₀ Q h w v

#check source_core24
#check canonicalModel
#check comparisonMap_unique
#check discrepancy_reference_independent
#check Examples.no_agreement_from_immediate_invisibility
#check Examples.one_initial_is_not_enough
#check Examples.good_projection_not_injective
