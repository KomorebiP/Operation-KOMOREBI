import FiniteRelativeObstructionVanishing
import ClopenPrescribedSection

/-! The finite quotient in the absolute vanishing theorem can be the actual
residual image. No discrete topology is imposed on the source group. -/
namespace Komorebi.StrongArtin.SquareZeroH2

variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable [TopologicalSpace B] [DiscreteTopology B]

omit [IsTopologicalGroup G] [DiscreteTopology A] in
theorem continuous_lift_of_finite_residual_image_order_isUnit
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* Bˣ) (hrho : Continuous rho) [Finite rho.range]
    (hn : IsUnit (Nat.card rho.range : A)) :
    ∃ L : G →* Aˣ, Continuous L ∧ (∀ g, q (L g)=(rho g : B)) ∧
      L.ker = rho.ker := by
  classical
  let : Fintype rho.range := Fintype.ofFinite _
  have hlabel : Continuous rho.rangeRestrict := hrho.subtype_mk _
  have hn' : IsUnit (Fintype.card rho.range : A) := by
    simpa only [Nat.card_eq_fintype_card] using hn
  obtain ⟨LQ,hLQ,hc,_⟩ := continuous_representation_lifts_through_finite_quotient
    rho.rangeRestrict hlabel q hq hsq rho.range.subtype hn'
  refine ⟨LQ.comp rho.rangeRestrict,hc,fun g => hLQ (rho.rangeRestrict g), ?_⟩
  apply le_antisymm
  · intro g hg
    apply Units.ext
    change (rho g : B)=1
    calc
      (rho g : B)=q (LQ (rho.rangeRestrict g)) := (hLQ (rho.rangeRestrict g)).symm
      _ = 1 := by
        have h : LQ (rho.rangeRestrict g)=1 := hg
        rw [h]
        exact map_one q
  · intro g hg
    have hr : rho.rangeRestrict g=1 := by
      apply Subtype.ext
      exact hg
    change LQ (rho.rangeRestrict g)=1
    rw [hr,map_one]

theorem continuous_obstruction_zero_of_finite_residual_image_order_isUnit
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* Bˣ) (hrho : Continuous rho) [Finite rho.range]
    (hn : IsUnit (Nat.card rho.range : A)) :
    (continuousSectionDatum q hq hsq rho).continuousObstruction
      (continuousSectionDatum_continuous_lift q hq hsq rho hrho)=0 := by
  obtain ⟨L,hLc,hL,_⟩ := continuous_lift_of_finite_residual_image_order_isUnit q hq hsq rho hrho hn
  exact (continuous_lifts_iff_constructed_obstruction_zero q hq hsq rho hrho).mp ⟨L,hLc,hL⟩

omit [DiscreteTopology A] in
/-- The clopen-subgroup criterion applies to every OPEN subgroup of a topological group. -/
theorem open_subgroup_prescription_has_continuous_section
    (H : Subgroup G) (hH : IsOpen (H : Set G))
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* Bˣ) (hrho : Continuous rho)
    (tau : H →* Aˣ) (htau : Continuous tau)
    (hres : ∀ h : H, q (tau h)=(rho h : B)) :
    ∃ D : Datum G A B, D.q=q ∧ D.rho=(Units.coeHom B).comp rho ∧
      Continuous D.lift ∧ ∀ h : H, D.lift h=tau h := by
  refine ⟨prescribedContinuousDatum H q hq hsq rho tau hres,rfl,rfl, ?_, ?_⟩
  · exact prescribedSection_continuous H ⟨H.isClosed_of_isOpen hH,hH⟩ q hq hsq rho hrho tau htau
  · exact prescribedSection_on_subgroup H q hq hsq rho tau

end Komorebi.StrongArtin.SquareZeroH2

namespace Komorebi.StrongArtin.SquareZeroH2
variable {G Q A B : Type} [Group G] [Group Q] [Fintype Q] [Ring A] [Ring B]
variable [TopologicalSpace G] [TopologicalSpace Q] [DiscreteTopology Q] [TopologicalSpace A]

/-- Same finite quotient, with a specified subgroup lift preserved exactly.
The subgroup prescription is required to factor through the displayed finite subgroup. -/
theorem continuous_finite_quotient_lift_preserving_subgroup
    (label : G →* Q) (hlabel : Continuous label)
    (K : Subgroup Q) [Fintype K]
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : Q →* Bˣ) (tau : K →* Aˣ)
    (htau : ∀ h : K, q (tau h)=(rho h : B))
    (hQ : IsUnit (Fintype.card Q : A)) (hK : IsUnit (Fintype.card K : A)) :
    ∃ LQ : Q →* Aˣ, (∀ a, q (LQ a)=(rho a : B)) ∧
      Continuous (LQ.comp label) ∧
      ∀ g (hg : label g ∈ K), (LQ.comp label) g=tau ⟨label g,hg⟩ := by
  let D := prescribedContinuousDatum K q hq hsq rho tau htau
  have hm : ∀ g ∈ K, ∀ h ∈ K, D.lift (g*h)=D.lift g*D.lift h :=
    prescribedContinuousDatum_subgroup_multiplicative K q hq hsq rho tau htau
  obtain ⟨LQ,hLQ,hfix⟩ := D.fixed_restriction_lifts_of_groupOrders_isUnit K hQ hK hm
  refine ⟨LQ,hLQ,(continuous_of_discreteTopology : Continuous LQ).comp hlabel, ?_⟩
  intro g hg
  exact (hfix (label g) hg).trans (prescribedSection_on_subgroup K q hq hsq rho tau ⟨label g,hg⟩)

end Komorebi.StrongArtin.SquareZeroH2
