import UnramifiedQuotientDescent
import ContinuousGaugeLiftCriterion

/-! Instantiate v0.29 with procyclic local groups and genuine degree maps.
The remaining matching obstruction is an exact system of Frobenius power equations. -/
namespace Komorebi.StrongArtin.Procyclic

variable {A B I : Type} [Ring A] [Ring B] [Finite A]
variable [TopologicalSpace A] [DiscreteTopology A]
variable [TopologicalSpace B] [DiscreteTopology B]

/-- A v0.29 class vanishes exactly when the finitely valued Frobenius data glue.
No surjectivity of a localization map or nonvanishing class is assumed away. -/
theorem local_gauge_obstruction_zero_iff_frobenius_system
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : Zhat →ₜ* Bˣ) (degree : I → ℕ) (t : I → (Zhat →ₜ* Aˣ))
    (ht : ∀ i z, q (t i z) = (rho (degreeMap (degree i) z) : B)) :
    (SquareZeroH2.continuousSectionDatum q hq hsq rho.toMonoidHom).localConjugacyObstruction
      (fun _ : I => Zhat)
      (SquareZeroH2.continuousSectionDatum_continuous_lift q hq hsq rho.toMonoidHom
        rho.continuous)
      (fun i => (degreeMap (degree i)).toMonoidHom) (fun i => (degreeMap (degree i)).continuous)
      (fun i => (t i).toMonoidHom) ht (fun i => (t i).continuous) = 0 ↔
    ∃ F : Aˣ, q F = (rho frobenius : B) ∧
      ∃ u : I → Aˣ, (∀ i, q (u i) = 1) ∧
        ∀ i, u i * F ^ degree i * (u i)⁻¹ = t i frobenius := by
  rw [← SquareZeroH2.continuous_local_conjugacy_lifts_iff_constructed_class_zero
    (fun _ : I => Zhat) q hq hsq rho.toMonoidHom rho.continuous
    (fun i => (degreeMap (degree i)).toMonoidHom) (fun i => (degreeMap (degree i)).continuous)
    (fun i => (t i).toMonoidHom) ht (fun i => (t i).continuous)]
  constructor
  · rintro ⟨l, _hlc, hl, u, hu, he⟩
    refine ⟨l frobenius, hl _, u, hu, ?_⟩
    intro i
    simpa using he i frobenius
  · rintro ⟨F,hF,u,hu,he⟩
    let l : Zhat →ₜ* Aˣ := fromFrobenius (H := ProfiniteGrp.of Aˣ) F
    have hlf : l frobenius = F := fromFrobenius_frobenius (H := ProfiniteGrp.of Aˣ) F
    have hl : (unitReduction q).comp l = rho := by
      apply hom_ext
      apply Units.ext
      change q (l frobenius) = (rho frobenius : B)
      rw [hlf]
      exact hF
    refine ⟨l.toMonoidHom,l.continuous,?_,u,hu,?_⟩
    · intro z
      exact congrArg (fun f : Zhat →ₜ* Bˣ => (f z : B)) hl
    · intro i
      apply (conjugacy_iff_frobenius (H := ProfiniteGrp.of Aˣ)
        (l.comp (degreeMap (degree i))) (t i) (u i)).mpr
      change u i * l (degreeMap (degree i) frobenius) * (u i)⁻¹ = t i frobenius
      rw [degreeMap_frobenius, map_pow, hlf]
      exact he i

/-- Express the inertia-preserving result in the monoid-hom form used by the obstruction API.
The inertia subgroup need not be open. Its procyclic quotient is supplied explicitly. -/
theorem inertia_preserving_lift_in_obstruction_form [Finite B]
    {G : Type} [Group G] [TopologicalSpace G] [IsTopologicalGroup G] [CompactSpace G]
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (nu : G →ₜ* Zhat) (hnu : Function.Surjective nu)
    (rho : G →ₜ* Bˣ) (hin : ∀ g, nu g = 1 → rho g = 1) :
    ∃ l : G →* Aˣ, Continuous l ∧
      (∀ g, q (l g) = (rho g : B)) ∧
      ∀ h : nu.toMonoidHom.ker, l h = 1 := by
  obtain ⟨l,hl,hi⟩ := unramified_lift_preserving_inertia q hq hsq nu hnu rho hin
  refine ⟨l.toMonoidHom,l.continuous,?_,?_⟩
  · intro g
    exact congrArg (fun f : G →ₜ* Bˣ => (f g : B)) hl
  · intro h
    exact hi h h.property

end Komorebi.StrongArtin.Procyclic
