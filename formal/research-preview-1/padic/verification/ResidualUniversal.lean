import KomorebiPadic.ResidualMinimalityExamples
open KomorebiPadic KomorebiPadic.ResidualRealization
noncomputable section
variable {R V W A : Type*} [CommRing R] [AddCommGroup V] [Module R V]
  [AddCommGroup W] [Module R W]
example (M : LinearObservability.System R V A) :
    LinearMap.ker (behaviorMap M) = LinearObservability.unobservable M := behaviorMap_ker M
example (f : Behavior R A) : LinearReachability.reachable (residualSystem f).dynamics = ⊤ := residual_reachable f
example (M : LinearObservability.System R V A) (hR : IsReachable M) (hO : IsObservable M) :
    V ≃ₗ[R] ResidualState (behavior M) := equivResidual M _ hR hO rfl
example (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (hM : IsReachable M) (hN : IsReachable N) (hO : IsObservable N) (hf : behavior N = behavior M) :
    ∃! g : V →ₗ[R] W, Simulation M N g := existsUnique_comparison M N _ hM hN hO rfl hf
example [Finite W] (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    (hR : IsReachable M) (hO : IsObservable M) (hf : behavior N = behavior M) :
    Nat.card V ≤ Nat.card W := minimal_cardinality M N hR hO hf
example [Finite V] [Finite W] (M : LinearObservability.System R V A) (N : LinearObservability.System R W A)
    {p b c : ℕ} (hp : p.Prime) (hV : Nat.card V = p^b) (hW : Nat.card W = p^c) :
    behavior M = behavior N ↔ ∀ u : List A, u.length < b+c → behavior M u = behavior N u :=
  behavior_eq_iff_finite_words M N hp hV hW
example (p r : ℕ) (P Q : Polynomial ℤ) (hp : p.Prime) (hr : 0 < r)
    (hQ : ¬ (p : ℤ) ∣ Q.coeff 0) (hPQ : MaskConstantsAgree p r P Q) :
    MinimalCanonicalMaskCertificate p r P Q hp hr hQ := compileCanonicalMask p r P Q hp hr hQ hPQ
example (p r : ℕ) (P Q : Polynomial ℤ) (hp : p.Prime) (hr : 0 < r)
    (hQ : ¬ (p : ℤ) ∣ Q.coeff 0) (hPQ : MaskConstantsAgree p r P Q) :
    ObservableMaskState p r P Q hp hr hQ ≃ₗ[ZMod (p^r)]
      ResidualState (canonicalMaskWordBehavior p r P Q hp hr hQ) :=
  minimalMaskEquivResidual p r P Q hp hr hQ hPQ
end
