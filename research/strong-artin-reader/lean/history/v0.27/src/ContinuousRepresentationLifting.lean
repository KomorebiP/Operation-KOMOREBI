import ContinuousObstructionCochains

namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable (D : Datum G A B)

/-- Exact continuous lifting criterion on the original representation. -/
theorem continuous_representation_lifts_iff (hr : Continuous D.lift) :
    (∃ L : G →* Aˣ, Continuous L ∧ ∀ g, D.q (L g)=D.rho g) ↔
      D.continuousObstruction hr = 0 := by
  constructor
  · rintro ⟨L,hLc,hL⟩
    have he := D.continuousObstructionOf_eq hr D.lift L D.lift_residue hL hr hLc
    have hz : D.continuousDefectOf L hL hLc = 0 := by
      apply Subtype.ext
      apply groupCohomology.cocycles₂_ext
      intro g h
      apply Subtype.ext
      change ((L g : A)*L h-L (g*h))*↑(L (g*h))⁻¹=0
      simp
    change D.continuousObstructionOf hr D.lift D.lift_residue hr = 0
    rw [he]
    change (Submodule.Quotient.mk (D.continuousDefectOf L hL hLc) : D.ContinuousH2 hr)=0
    rw [hz]
    rfl
  · intro hz
    obtain ⟨b,hbc,hb⟩ := (D.continuousObstruction_zero_iff hr).mp hz
    exact ⟨D.liftFromPrimitive b hb, D.continuous_liftFromPrimitive hr b hbc hb,
      D.correctedLift_residue (-b)⟩

theorem continuous_zero_implies_ordinary_zero (hr : Continuous D.lift)
    (h : D.continuousObstruction hr = 0) : D.obstruction = 0 := by
  obtain ⟨b,_,hb⟩ := (D.continuousObstruction_zero_iff hr).mp h
  exact D.obstruction_zero_iff_boundary.mpr ⟨b,hb⟩

/-- A discrete SOURCE is a verification specialization, not an assumption
on the profinite source in the main continuous theorem. -/
theorem continuous_zero_iff_ordinary_zero_of_discrete_source [DiscreteTopology G]
    (hr : Continuous D.lift) : D.continuousObstruction hr = 0 ↔ D.obstruction=0 := by
  constructor
  · exact D.continuous_zero_implies_ordinary_zero hr
  · intro hz
    obtain ⟨b,hb⟩ := D.obstruction_zero_iff_boundary.mp hz
    exact (D.continuousObstruction_zero_iff hr).mpr ⟨b,continuous_of_discreteTopology,hb⟩

end Komorebi.StrongArtin.SquareZeroH2.Datum

namespace Komorebi.StrongArtin.SquareZeroH2

variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable [TopologicalSpace B] [DiscreteTopology B]

/-- No section is an input: the normalized continuous one is constructed. -/
theorem continuous_lifts_iff_constructed_obstruction_zero
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* Bˣ) (hrho : Continuous rho) :
    (∃ L : G →* Aˣ, Continuous L ∧ ∀ g, q (L g)=(rho g : B)) ↔
      (continuousSectionDatum q hq hsq rho).continuousObstruction
        (continuousSectionDatum_continuous_lift q hq hsq rho hrho) = 0 := by
  exact (continuousSectionDatum q hq hsq rho).continuous_representation_lifts_iff _

end Komorebi.StrongArtin.SquareZeroH2
