import KomorebiLSM.InstrumentCoordinates

/-! Known finite instruments admit minimal mass-anchored predictive coordinates.
Signed coordinates are interpreted on the image of genuine beliefs, not as
independent nonnegative probabilities. No unknown-model learning is asserted. -/
set_option autoImplicit false
namespace Komorebi.LSM.FiniteInstruments
open scoped BigOperators
open Module FiniteBayes
universe u v w
variable {I : Type u} {U : Type v} {O : Type w} [Fintype I] [Fintype O]
variable {E : Type*} [AddCommGroup E] [Module ℝ E]

/-- The admissible predictive states are images of actual priors. -/
def realizableBeliefs (R : (I → ℝ) →ₗ[ℝ] E) : Set E :=
  {z | ∃ p, IsPrior p ∧ R p = z}

section Semantics
variable (T : Instrument I U O) (R : (I → ℝ) →ₗ[ℝ] E)
variable (B : U × O → E →ₗ[ℝ] E) (l : E →ₗ[ℝ] ℝ)
variable (hmass : l.comp R = mass)
variable (hB : ∀ s, (B s).comp R = R.comp (T.branch s))

/-- The scalar prediction is exactly the fine joint branch mass. -/
theorem reduced_likelihood (s : U × O) (p : I → ℝ) :
    l (B s (R p)) = mass (T.branch s p) := by
  have hs : B s (R p) = R (T.branch s p) :=
    congrArg (fun F : (I → ℝ) →ₗ[ℝ] E => F p) (hB s)
  rw [hs]
  exact congrArg (fun f : (I → ℝ) →ₗ[ℝ] ℝ => f (T.branch s p)) hmass

/-- The normalized state commutes with the observation summary. -/
theorem reduced_posterior (s : U × O) (p : I → ℝ) :
    R (normalize mass (T.branch s p)) = normalize l (B s (R p)) := by
  have hs : B s (R p) = R (T.branch s p) :=
    congrArg (fun F : (I → ℝ) →ₗ[ℝ] E => F p) (hB s)
  rw [normalize_transport R mass l hmass, hs]

theorem reduced_word_readout (w : List (U × O)) (p : I → ℝ) :
    l (wordAction B w (R p)) = mass (wordAction T.branch w p) := by
  have hw := word_intertwining T.branch B R hB w
  have hp := congrArg (fun F : (I → ℝ) →ₗ[ℝ] E => F p) hw
  change wordAction B w (R p) = R (wordAction T.branch w p) at hp
  rw [hp]
  exact congrArg (fun f : (I → ℝ) →ₗ[ℝ] ℝ => f (wordAction T.branch w p)) hmass

theorem realization_reads_all_words : ReadsAllWords T.branch R := by
  intro w
  exact ⟨l.comp (wordAction B w), fun p _ => reduced_word_readout T R B l hmass hB w p⟩

theorem reduced_likelihood_prior (a : U) (z : E) (hz : z ∈ realizableBeliefs R) :
    IsPrior (fun o => l (B (a,o) z)) := by
  obtain ⟨p,hp,rfl⟩ := hz
  simpa only [reduced_likelihood T R B l hmass hB] using T.likelihood_prior a p hp

/-- Only positive-likelihood branches have a probabilistic posterior. -/
theorem reduced_posterior_realizable (s : U × O) (z : E)
    (hz : z ∈ realizableBeliefs R) (hpos : 0 < l (B s z)) :
    normalize l (B s z) ∈ realizableBeliefs R := by
  obtain ⟨p,hp,rfl⟩ := hz
  have htrue : 0 < mass (T.branch s p) := by
    rwa [reduced_likelihood T R B l hmass hB] at hpos
  exact ⟨normalize mass (T.branch s p), T.branch_posterior_prior s p hp htrue,
    reduced_posterior T R B l hmass hB s p⟩

theorem reduced_word_probability (w : List (U × O)) (z : E)
    (hz : z ∈ realizableBeliefs R) :
    0 ≤ l (wordAction B w z) ∧ l (wordAction B w z) ≤ 1 := by
  obtain ⟨p,hp,rfl⟩ := hz
  rw [reduced_word_readout T R B l hmass hB]
  exact T.word_probability w p hp

/-- Onto coordinates promote the mass identity to the whole coordinate space. -/
theorem reduced_mass_identity (hR : Function.Surjective R) (a : U) (z : E) :
    ∑ o, l (B (a,o) z) = l z := by
  obtain ⟨p,rfl⟩ := hR z
  simp only [reduced_likelihood T R B l hmass hB]
  rw [T.instrument_mass]
  exact (congrArg (fun f : (I → ℝ) →ₗ[ℝ] ℝ => f p) hmass).symm

end Semantics

/-- A complete P26 realization is constructed from the supplied hidden instrument.
The result contains a literal first-coordinate mass row, unique transitions,
all-word equality and posterior closure on admissible branches. -/
theorem finite_instrument_closure [Nonempty I] (T : Instrument I U O) :
    ∃ (r : ℕ) (hr : 0 < r)
      (R : (I → ℝ) →ₗ[ℝ] (Fin r → ℝ))
      (B : U × O → (Fin r → ℝ) →ₗ[ℝ] (Fin r → ℝ)),
      let l : (Fin r → ℝ) →ₗ[ℝ] ℝ := LinearMap.proj ⟨0,hr⟩
      r = finrank ℝ (wordSpan T.branch mass) ∧
      LinearIndependent ℝ (fun j => (LinearMap.proj j).comp R) ∧
      Function.Surjective R ∧
      LinearMap.range R.dualMap = wordSpan T.branch mass ∧
      l.comp R = mass ∧
      (∀ s, (B s).comp R = R.comp (T.branch s)) ∧
      (∀ s D, D.comp R = R.comp (T.branch s) → D = B s) ∧
      (∀ w p, l (wordAction B w (R p)) = mass (wordAction T.branch w p)) ∧
      (∀ s z, z ∈ realizableBeliefs R → 0 < l (B s z) →
        normalize l (B s z) ∈ realizableBeliefs R) := by
  obtain ⟨r,hr,R,B,hd,hind,honto,hrow,hm,hc,hu⟩ := finite_instrument_coordinates T.branch
  refine ⟨r,hr,R,B, ?_⟩
  dsimp only
  refine ⟨?_,hind,honto,?_,hm,hc,hu,?_,?_⟩
  · rwa [instrumentCompletion_eq_wordSpan] at hd
  · rwa [instrumentCompletion_eq_wordSpan] at hrow
  · exact reduced_word_readout T R B _ hm hc
  · exact reduced_posterior_realizable T R B _ hm hc

end Komorebi.LSM.FiniteInstruments
