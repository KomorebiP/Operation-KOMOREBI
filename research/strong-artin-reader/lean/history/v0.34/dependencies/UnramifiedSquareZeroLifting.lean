import ProcyclicFrobeniusLifting
import ContinuousRepresentationLifting
import MatrixSquareZeroObstruction
import Mathlib.Topology.Instances.Matrix

/-! Actual vanishing for the free procyclic (unramified) quotient.
Coefficients are finite and discrete; no residual image-order restriction occurs. -/
namespace Komorebi.StrongArtin.Procyclic

variable {A B : Type} [Ring A] [Ring B]
variable [TopologicalSpace A] [DiscreteTopology A]
variable [TopologicalSpace B] [DiscreteTopology B]

def unitReduction (q : A →+* B) : Aˣ →ₜ* Bˣ where
  toMonoidHom := Units.map q.toMonoidHom
  continuous_toFun := continuous_of_discreteTopology

omit [DiscreteTopology B] in
@[simp] theorem unitReduction_val (q : A →+* B) (u : Aˣ) :
    ((unitReduction q u : Bˣ) : B) = q u := rfl

omit [DiscreteTopology B] in
theorem unitReduction_surjective (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a*b = 0) :
    Function.Surjective (unitReduction q) := by
  intro u
  obtain ⟨v,hv⟩ := SquareZeroH2.units_lift_across_square_zero q hq hsq u
  exact ⟨v, Units.ext hv⟩

/-- A chosen lift of Frobenius is allowed to have larger finite order. -/
theorem procyclic_representation_lifts [Finite A] [Finite B]
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a*b = 0)
    (rho : Zhat →ₜ* Bˣ) :
    ∃ l : Zhat →ₜ* Aˣ, (unitReduction q).comp l = rho := by
  exact exists_lift_of_surjective (H := ProfiniteGrp.of Aˣ) (K := ProfiniteGrp.of Bˣ)
    (unitReduction q) (unitReduction_surjective q hq hsq) rho

/-- Vanishing of the actual constructed continuous inhomogeneous obstruction. -/
theorem procyclic_continuous_obstruction_zero [Finite A] [Finite B]
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a*b = 0)
    (rho : Zhat →ₜ* Bˣ) :
    (SquareZeroH2.continuousSectionDatum q hq hsq rho.toMonoidHom).continuousObstruction
      (SquareZeroH2.continuousSectionDatum_continuous_lift q hq hsq rho.toMonoidHom
        rho.continuous) = 0 := by
  obtain ⟨l,hl⟩ := procyclic_representation_lifts q hq hsq rho
  apply (SquareZeroH2.continuous_lifts_iff_constructed_obstruction_zero q hq hsq
    rho.toMonoidHom rho.continuous).mp
  refine ⟨l.toMonoidHom,l.continuous,fun g => ?_⟩
  exact congrArg (fun f : Zhat →ₜ* Bˣ => (f g : B)) hl

/-- Pullback preserves the declared inertia kernel, with no quotient enlargement on the source. -/
theorem unramified_pullback_lifts {G : Type} [Group G] [TopologicalSpace G]
    [Finite A] [Finite B]
    (nu : G →ₜ* Zhat) (rho : Zhat →ₜ* Bˣ)
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a*b = 0) :
    ∃ l : G →ₜ* Aˣ,
      (unitReduction q).comp l = rho.comp nu ∧
      ∀ g, nu g = 1 → l g = 1 := by
  obtain ⟨s,hs⟩ := procyclic_representation_lifts q hq hsq rho
  refine ⟨s.comp nu, ?_, ?_⟩
  · apply DFunLike.ext
    intro g
    exact congrArg (fun f : Zhat →ₜ* Bˣ => f (nu g)) hs
  · intro g hg
    change s (nu g) = 1
    rw [hg,map_one]

/-- Invertible matrices are handled via the actual matrix reduction homomorphism. -/
theorem procyclic_matrix_representation_lifts
    {R S n : Type} [CommRing R] [CommRing S] [Finite R] [Finite S]
    [Fintype n] [DecidableEq n]
    [TopologicalSpace R] [DiscreteTopology R]
    [TopologicalSpace S] [DiscreteTopology S]
    (q : R →+* S) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a*b = 0)
    (rho : Zhat →ₜ* (Matrix n n S)ˣ) :
    ∃ l : Zhat →ₜ* (Matrix n n R)ˣ,
      (unitReduction q.mapMatrix).comp l = rho := by
  exact procyclic_representation_lifts q.mapMatrix
    (SquareZeroH2.matrix_map_surjective q hq)
    (SquareZeroH2.matrix_kernel_squareZero q hsq) rho

end Komorebi.StrongArtin.Procyclic
