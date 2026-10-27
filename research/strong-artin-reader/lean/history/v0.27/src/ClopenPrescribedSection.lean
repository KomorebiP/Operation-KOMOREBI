import ContinuousFixedRestriction
import Mathlib.Topology.Piecewise
import Mathlib.Topology.Algebra.OpenSubgroup

/-! An OPEN subgroup prescription can be extended to a continuous provisional
section, without assuming a homomorphic extension exists. -/
namespace Komorebi.StrongArtin.SquareZeroH2

variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G]
variable [TopologicalSpace A]
variable [TopologicalSpace B] [DiscreteTopology B]

noncomputable def prescribedSection
    (H : Subgroup G) (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* Bˣ) (tau : H →* Aˣ) : G → Aˣ := by
  classical
  exact fun g => if hg : g ∈ H then tau ⟨g,hg⟩ else normalizedUnitSection q hq hsq (rho g)

omit [TopologicalSpace G] [TopologicalSpace A] [TopologicalSpace B] [DiscreteTopology B] in
@[simp] theorem prescribedSection_on_subgroup
    (H : Subgroup G) (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* Bˣ) (tau : H →* Aˣ) (g : H) :
    prescribedSection H q hq hsq rho tau g = tau g := by
  classical
  simp [prescribedSection,g.property]

theorem prescribedSection_continuous
    (H : Subgroup G) (hH : IsClopen (H : Set G))
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* Bˣ) (hrho : Continuous rho)
    (tau : H →* Aˣ) (htau : Continuous tau) :
    Continuous (prescribedSection H q hq hsq rho tau) := by
  classical
  let s := prescribedSection H q hq hsq rho tau
  have h1 : ContinuousOn s (H : Set G) := by
    rw [continuousOn_iff_continuous_domRestrict]
    have he : ((H : Set G).domRestrict s) = fun h : H => tau h := by
      funext h
      exact prescribedSection_on_subgroup H q hq hsq rho tau h
    rw [he]
    exact htau
  have h2 : ContinuousOn s (H : Set G)ᶜ := by
    have hc : Continuous (fun g => normalizedUnitSection q hq hsq (rho g)) :=
      (continuous_of_discreteTopology : Continuous (normalizedUnitSection q hq hsq)).comp hrho
    apply hc.continuousOn.congr
    intro g hg
    simp only [Set.mem_compl_iff,SetLike.mem_coe] at hg
    simp [s,prescribedSection,hg]
  have hu := h1.union_of_isClosed h2 hH.isClosed hH.compl.isClosed
  simpa only [Set.union_compl_self,continuousOn_univ] using hu

noncomputable def prescribedContinuousDatum
    (H : Subgroup G) (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* Bˣ) (tau : H →* Aˣ)
    (hres : ∀ h : H, q (tau h)=(rho h : B)) : Datum G A B where
  q := q
  squareZero := hsq
  rho := (Units.coeHom B).comp rho
  lift := prescribedSection H q hq hsq rho tau
  lift_one := by
    have h := prescribedSection_on_subgroup H q hq hsq rho tau (1 : H)
    simpa using h
  lift_residue := by
    classical
    intro g
    by_cases hg : g ∈ H
    · simpa [prescribedSection,hg] using hres ⟨g,hg⟩
    · simpa [prescribedSection,hg] using normalizedUnitSection_residue q hq hsq (rho g)

omit [TopologicalSpace G] [TopologicalSpace A] [TopologicalSpace B] [DiscreteTopology B] in
theorem prescribedContinuousDatum_subgroup_multiplicative
    (H : Subgroup G) (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* Bˣ) (tau : H →* Aˣ)
    (hres : ∀ h : H, q (tau h)=(rho h : B)) :
    ∀ g ∈ H, ∀ h ∈ H,
      (prescribedContinuousDatum H q hq hsq rho tau hres).lift (g*h) =
        (prescribedContinuousDatum H q hq hsq rho tau hres).lift g *
        (prescribedContinuousDatum H q hq hsq rho tau hres).lift h := by
  classical
  intro g hg h hh
  simp only [prescribedContinuousDatum, prescribedSection,hg,hh,H.mul_mem hg hh,dite_eq_left]
  exact map_mul tau ⟨g,hg⟩ ⟨h,hh⟩

end Komorebi.StrongArtin.SquareZeroH2

namespace Komorebi.StrongArtin.SquareZeroH2
variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable [TopologicalSpace B] [DiscreteTopology B]

/-- A continuous prescribed representation on a clopen subgroup supplies a
continuous provisional section; the relative class has no hidden section input. -/
theorem continuous_prescribed_subgroup_lifts_iff
    (H : Subgroup G) (hH : IsClopen (H : Set G))
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* Bˣ) (hrho : Continuous rho)
    (tau : H →* Aˣ) (htau : Continuous tau)
    (hres : ∀ h : H, q (tau h)=(rho h : B)) :
    (∃ L : G →* Aˣ, Continuous L ∧ (∀ g, q (L g)=(rho g : B)) ∧
      ∀ h : H, L h=tau h) ↔
    (prescribedContinuousDatum H q hq hsq rho tau hres).continuousRelativeObstruction H
      (prescribedSection_continuous H hH q hq hsq rho hrho tau htau)
      (prescribedContinuousDatum_subgroup_multiplicative H q hq hsq rho tau hres)=0 := by
  let D := prescribedContinuousDatum H q hq hsq rho tau hres
  have hc : Continuous D.lift := prescribedSection_continuous H hH q hq hsq rho hrho tau htau
  have hm : ∀ g ∈ H, ∀ h ∈ H, D.lift (g*h)=D.lift g*D.lift h :=
    prescribedContinuousDatum_subgroup_multiplicative H q hq hsq rho tau hres
  change _ ↔ D.continuousRelativeObstruction H hc hm=0
  constructor
  · rintro ⟨L,hLc,hL,hfix⟩
    apply (D.continuous_fixed_restriction_lifts_iff H hc hm).mp
    refine ⟨L,hLc,hL, ?_⟩
    intro g hg
    exact (hfix ⟨g,hg⟩).trans (prescribedSection_on_subgroup H q hq hsq rho tau ⟨g,hg⟩).symm
  · intro hz
    obtain ⟨L,hLc,hL,hfix⟩ := (D.continuous_fixed_restriction_lifts_iff H hc hm).mpr hz
    refine ⟨L,hLc,hL, ?_⟩
    intro h
    exact (hfix h h.property).trans (prescribedSection_on_subgroup H q hq hsq rho tau h)

end Komorebi.StrongArtin.SquareZeroH2
