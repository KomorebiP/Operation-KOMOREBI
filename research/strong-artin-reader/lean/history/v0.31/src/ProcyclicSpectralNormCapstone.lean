import SimultaneousSpectralRestriction

/-! Apply the spectral norm criterion to the actual continuous local-gauge
obstruction from v0.29/v0.30. No comparison to an unnamed arithmetic H1 is assumed. -/
namespace Komorebi.StrongArtin.Procyclic
variable {A B k I L : Type} [Ring A] [Ring B] [Field k] [Finite A]
variable [TopologicalSpace A] [DiscreteTopology A]
variable [TopologicalSpace B] [DiscreteTopology B]

/-- The actual obstruction class is computed by resonances and shared invariant coordinates. -/
theorem continuous_gauge_obstruction_zero_iff_spectral_compatibility
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : Zhat →ₜ* Bˣ) (degree : L → ℕ) (t : L → (Zhat →ₜ* Aˣ))
    (ht : ∀ l z, q (t l z) = (rho (degreeMap (degree l) z) : B))
    (F : Aˣ) (hF : q F = (rho frobenius : B))
    (hV : ∀ l, q (t l frobenius) = q (F^degree l))
    (S : SquareZeroH2.FrobeniusSpectralCoordinates
      (SquareZeroH2.continuousSectionDatum q hq hsq rho.toMonoidHom) F k I) :
    (SquareZeroH2.continuousSectionDatum q hq hsq rho.toMonoidHom).localConjugacyObstruction
      (fun _ : L => Zhat)
      (SquareZeroH2.continuousSectionDatum_continuous_lift q hq hsq rho.toMonoidHom
        rho.continuous)
      (fun l => (degreeMap (degree l)).toMonoidHom) (fun l => (degreeMap (degree l)).continuous)
      (fun l => (t l).toMonoidHom) ht (fun l => (t l).continuous) = 0 ↔
    (∀ l i, S.eigenvalue i ≠ 1 → SquareZeroH2.normWeight (S.eigenvalue i) (degree l) = 0 →
      S.coordinates ((SquareZeroH2.continuousSectionDatum q hq hsq rho.toMonoidHom).unitMismatch (t l frobenius) (F^degree l) (hV l)) i = 0) ∧
    (∃ a : I → k, ∀ l i, S.eigenvalue i = 1 →
      S.coordinates ((SquareZeroH2.continuousSectionDatum q hq hsq rho.toMonoidHom).unitMismatch (t l frobenius) (F^degree l) (hV l)) i = (degree l : k)*a i) := by
  rw [gauge_obstruction_zero_iff_explicit_norm_class_zero q hq hsq rho degree t ht F hF hV]
  exact S.matchingClass_zero_iff degree (fun l => t l frobenius) hV

/-- In the nonresonant sector, a prescribed degree restriction lifts literally,
not only up to local conjugacy. The continuous source is the genuine Zhat. -/
theorem continuous_prescribed_degree_lift_of_nonresonance [Finite B]
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : Zhat →ₜ* Bˣ) (d : ℕ) (t : Zhat →ₜ* Aˣ)
    (F : Aˣ) (hF : q F = (rho frobenius : B))
    (hV : q (t frobenius) = q (F^d))
    (S : SquareZeroH2.FrobeniusSpectralCoordinates
      (SquareZeroH2.continuousSectionDatum q hq hsq rho.toMonoidHom) F k I)
    (h : ∀ i, SquareZeroH2.normWeight (S.eigenvalue i) d ≠ 0) :
    ∃ l : Zhat →ₜ* Aˣ, (unitReduction q).comp l = rho ∧ l.comp (degreeMap d) = t := by
  obtain ⟨F',hF',hp⟩ := S.prescribed_power_lifts_of_nonresonance d h (t frobenius) hV
  have hqF' : unitReduction q F' = rho frobenius := by
    apply Units.ext
    exact hF'.trans hF
  obtain ⟨l,⟨hl,he⟩,_⟩ := exists_unique_lift_with_frobenius
    (H := ProfiniteGrp.of Aˣ) (K := ProfiniteGrp.of Bˣ) (unitReduction q) rho F' hqF'
  refine ⟨l,hl,?_⟩
  apply hom_ext
  change l (degreeMap d frobenius) = t frobenius
  rw [degreeMap_frobenius,map_pow,he,hp]

end Komorebi.StrongArtin.Procyclic
