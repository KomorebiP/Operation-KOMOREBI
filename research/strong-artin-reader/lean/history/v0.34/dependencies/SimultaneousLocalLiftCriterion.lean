import LocalLiftMismatch

/-! The continuous local prescriptions are arbitrary actual representation lifts
along a family of continuous group homomorphisms. No clopenness, extendability
of the prescriptions as one section, or vanishing is assumed. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G A B I : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable (D : Datum G A B) (L : I → Type)
variable [∀ i, Group (L i)] [∀ i, TopologicalSpace (L i)]

def prescribedLocalPair (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i)) : D.localConstraintPairs L loc :=
  ⟨(D.continuousDefectOf D.lift D.lift_residue hr,
    ⟨fun i => D.localCorrection (loc i) (t i) (ht i),
      fun i => D.localCorrection_continuous hr (loc i) (hloc i) (t i) (ht i) (htc i)⟩),
    fun i g h => D.localCorrection_boundary (loc i) (t i) (ht i) g h⟩

noncomputable def simultaneousLocalObstruction (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i)) : D.LocalConstraintH2 L hr loc hloc :=
  D.localConstraintClass L hr loc hloc (D.prescribedLocalPair L hr loc hloc t ht htc)

theorem simultaneousLocalObstruction_zero_iff (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i)) :
    D.simultaneousLocalObstruction L hr loc hloc t ht htc=0 ↔
      ∃ b : G → D.Kernel, Continuous b ∧
        (∀ g h, D.normalizedDefect D.lift D.lift_residue (g,h)=
          D.action g (b h)-b (g*h)+b g) ∧
        ∀ i h, b (loc i h)=D.localCorrection (loc i) (t i) (ht i) h := by
  unfold simultaneousLocalObstruction
  rw [D.localConstraintClass_zero_iff]
  constructor
  · rintro ⟨b,hb,hbl⟩
    refine ⟨b.1,b.property,fun g h => ?_,fun i h => ?_⟩
    · exact (congrArg (fun c : D.continuousTwoCocycles => c.1 (g,h)) hb).symm
    · exact congrArg (fun a : D.localOneCochains L => a.1 i h) hbl
  · rintro ⟨b,hbc,hb,hbl⟩
    refine ⟨⟨b,hbc⟩,?_,?_⟩
    · apply Subtype.ext
      apply groupCohomology.cocycles₂_ext
      intro g h
      exact (hb g h).symm
    · apply Subtype.ext
      funext i h
      exact hbl i h

/-- Liftability of the ORIGINAL representation with ALL prescriptions simultaneously. -/
theorem continuous_simultaneous_local_lifts_iff (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i)) :
    (∃ lift : G →* Aˣ, Continuous lift ∧
      (∀ g, D.q (lift g)=D.rho g) ∧ ∀ i h, lift (loc i h)=t i h) ↔
      D.simultaneousLocalObstruction L hr loc hloc t ht htc=0 := by
  rw [D.simultaneousLocalObstruction_zero_iff]
  constructor
  · rintro ⟨lift,hlc,hl,hfix⟩
    let b : G → D.Kernel := -D.liftDifference D.lift lift D.lift_residue hl
    have hbc : Continuous b :=
      (D.continuous_liftDifference D.lift lift D.lift_residue hl hr hlc).neg
    refine ⟨b,hbc,fun g h => ?_,fun i h => ?_⟩
    · have hz : D.normalizedDefect lift hl (g,h)=0 := by
        apply Subtype.ext
        change ((lift g : A)*lift h-lift (g*h))*↑(lift (g*h))⁻¹=0
        simp
      have he := D.normalizedDefect_change D.lift lift D.lift_residue hl g h
      rw [hz] at he
      change D.normalizedDefect D.lift D.lift_residue (g,h)=
        D.action g (-(D.liftDifference D.lift lift D.lift_residue hl h))-
          (-(D.liftDifference D.lift lift D.lift_residue hl (g*h)))+
          (-(D.liftDifference D.lift lift D.lift_residue hl g))
      rw [map_neg]
      exact (eq_neg_of_add_eq_zero_left he.symm).trans (by abel)
    · apply Subtype.ext
      change -(((lift (loc i h) : A)-D.lift (loc i h))*↑(D.lift (loc i h))⁻¹)=_
      rw [hfix i h]
      rfl
  · rintro ⟨b,hbc,hb,hbl⟩
    refine ⟨D.liftFromPrimitive b hb,D.continuous_liftFromPrimitive hr b hbc hb,
      D.correctedLift_residue (-b),fun i h => ?_⟩
    rw [D.liftFromPrimitive_apply]
    exact (D.correctedLift_at_local_iff (loc i) (t i) (ht i) b h).mpr (hbl i h)

theorem simultaneous_zero_implies_absolute_zero (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i))
    (hz : D.simultaneousLocalObstruction L hr loc hloc t ht htc=0) :
    D.continuousObstruction hr=0 := by
  obtain ⟨lift,hc,hl,_⟩ := (D.continuous_simultaneous_local_lifts_iff L hr loc hloc t ht htc).mpr hz
  exact (D.continuous_representation_lifts_iff hr).mp ⟨lift,hc,hl⟩

end Komorebi.StrongArtin.SquareZeroH2.Datum

namespace Komorebi.StrongArtin.SquareZeroH2
variable {G A B I : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable [TopologicalSpace B] [DiscreteTopology B]
variable (L : I → Type) [∀ i, Group (L i)] [∀ i, TopologicalSpace (L i)]

/-- No provisional section or already existing absolute representation lift is an input. -/
theorem continuous_local_family_lifts_iff_constructed_obstruction_zero
    (q : A →+* B) (hq : Function.Surjective q)
    (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (rho : G →* Bˣ) (hrho : Continuous rho)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, q (t i h)=(rho (loc i h) : B))
    (htc : ∀ i, Continuous (t i)) :
    (∃ lift : G →* Aˣ, Continuous lift ∧
      (∀ g, q (lift g)=(rho g : B)) ∧ ∀ i h, lift (loc i h)=t i h) ↔
    (continuousSectionDatum q hq hsq rho).simultaneousLocalObstruction L
      (continuousSectionDatum_continuous_lift q hq hsq rho hrho) loc hloc t ht htc=0 := by
  exact (continuousSectionDatum q hq hsq rho).continuous_simultaneous_local_lifts_iff
    L (continuousSectionDatum_continuous_lift q hq hsq rho hrho) loc hloc t ht htc

end Komorebi.StrongArtin.SquareZeroH2
