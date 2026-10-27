import ContinuousFiniteImageCapstone
import Mathlib.Topology.Compactness.Compact

/-! Compact/profinite sources and discrete coefficients: finiteness of the
actual residual image is proved, rather than supplied as an extra interface. -/
namespace Komorebi.StrongArtin.SquareZeroH2

variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [CompactSpace G]
variable [TopologicalSpace A]
variable [TopologicalSpace B] [DiscreteTopology B]

theorem continuous_discrete_representation_finite_range
    (rho : G →* Bˣ) (hc : Continuous rho) : Finite rho.range := by
  have hr : (Set.range rho).Finite := (isCompact_range hc).finite_of_discrete
  exact hr.to_subtype

/-- A continuous representation of a compact group into discrete coefficients
lifts on its SAME finite image whenever that image order is a unit upstairs. -/
theorem compact_source_lift_of_image_order_isUnit
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* Bˣ) (hc : Continuous rho)
    (hn : IsUnit (Nat.card rho.range : A)) :
    ∃ L : G →* Aˣ, Continuous L ∧ (∀ g, q (L g)=(rho g : B)) ∧ L.ker=rho.ker := by
  have : Finite rho.range := continuous_discrete_representation_finite_range rho hc
  exact continuous_lift_of_finite_residual_image_order_isUnit q hq hsq rho hc hn

end Komorebi.StrongArtin.SquareZeroH2
