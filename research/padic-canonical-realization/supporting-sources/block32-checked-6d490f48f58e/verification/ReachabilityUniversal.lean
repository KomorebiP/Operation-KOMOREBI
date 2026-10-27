import KomorebiPadic.ReachabilityExamples
open KomorebiPadic
noncomputable section
variable {R V A : Type*} [CommRing R] [AddCommGroup V] [Module R V]

example (M : LinearReachability.System R V A) (U : Submodule R V)
    (h : LinearReachability.Closed M U) : LinearReachability.reachable M ≤ U :=
  LinearReachability.reachable_le M U h

example [Finite V] (M : LinearReachability.System R V A) {p b : ℕ}
    (hp : p.Prime) (hc : Nat.card V = p^b) :
    LinearReachability.iterate M b = LinearReachability.reachable M :=
  LinearReachability.iterate_eq_reachable M hp hc

example (M : LinearReachability.System R V A) (ds : List A) (x : LinearReachability.State M) :
    (LinearReachability.runRestricted M ds x).val = LinearReachability.run M ds x.val :=
  LinearReachability.runRestricted_embedding M ds x

example (p r : ℕ) (A B : Polynomial ℤ) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) :
    ReachableCanonicalMaskCertificate p r A B hp hr hB :=
  reachableCanonicalMaskCertificate p r A B hp hr hB hAB

example (p r : ℕ) (A B : Polynomial ℤ) (hp : p.Prime) (hr : 0 < r)
    (hB : ¬ (p : ℤ) ∣ B.coeff 0) (hAB : MaskConstantsAgree p r A B) (n : ℕ) :
    reachableMaskOutput p r A B hp hr hB
      (reachableMaskIterate p r A B hp (finiteMaskDigitWord p n hp) (reachableMaskInitial p r A B hp)) =
      PowerSeries.coeff n (canonicalMaskSeries p r A B hp hr hB) :=
  reachableMask_output_canonical_coefficient p r A B hp hr hB hAB n

example (p r : ℕ) (A B : Polynomial ℤ) (hp : p.Prime) :
    (reachableMaskSpan p r A B hp).map
      (CoordinateIdeal.boxModule (p := p) (r := r) (leastMaskIdealCapacity p r A B hp)).subtype =
      LinearReachability.reachable (profileMaskLinearSystem p r A B hp) :=
  reachableMask_image_eq_profileReachable p r A B hp

example (d : Fin 1) (x : Fin 3 → ZMod 5) (hx : x 0 = x 1 ∧ x 2 = 0) :
    LinearReachability.correlated.transition d x = 0 :=
  LinearReachability.diagonal_transition_zero d x hx

example (M : LinearReachability.System (ZMod 1) (ZMod 1) (Fin 0)) :
    LinearReachability.iterate M 0 = LinearReachability.reachable M := by
  apply LinearReachability.iterate_eq_reachable M (by decide : Nat.Prime 2)
  simp
end
