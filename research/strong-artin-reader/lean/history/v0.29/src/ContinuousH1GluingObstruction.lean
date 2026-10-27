import ContinuousGaugeLiftCriterion

/-! After absolute cancellation, the local-conjugacy obstruction lies in the
cokernel on actual continuous H1 quotients, rather than the strict Z1 cokernel. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G A B I : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable (D : Datum G A B) (L : I → Type)
variable [∀ i, Group (L i)] [∀ i, TopologicalSpace (L i)]

abbrev LocalH1GluingCokernel (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :=
  D.GaugeLocalH1 L hr loc hloc ⧸ LinearMap.range (D.gaugeRestrictionH1 L hr loc hloc)

noncomputable def h1GluingProjection (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    D.localOneCocycles L loc →ₗ[ℤ] D.LocalH1GluingCokernel L hr loc hloc :=
  ((LinearMap.range (D.gaugeRestrictionH1 L hr loc hloc)).mkQ).comp
    (LinearMap.range (D.localGaugeCoboundary L hr loc hloc)).mkQ

theorem h1GluingProjection_zero_iff (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (a : D.localOneCocycles L loc) :
    D.h1GluingProjection L hr loc hloc a=0 ↔
      ∃ z : D.globalOneCocycles hr, ∃ x : I → D.Kernel,
        D.restrictOneCocycles L hr loc hloc z+D.localGaugeCoboundary L hr loc hloc x=a := by
  change (Submodule.Quotient.mk (Submodule.Quotient.mk a) :
    D.LocalH1GluingCokernel L hr loc hloc)=0 ↔ _
  rw [Submodule.Quotient.mk_eq_zero]
  constructor
  · rintro ⟨zH,hzH⟩
    obtain ⟨z,rfl⟩ := (LinearMap.range (D.globalGaugeCoboundary hr)).mkQ_surjective zH
    have he := hzH.symm
    change (Submodule.Quotient.mk a : D.GaugeLocalH1 L hr loc hloc)=
      Submodule.Quotient.mk (D.restrictOneCocycles L hr loc hloc z) at he
    rw [Submodule.Quotient.eq] at he
    obtain ⟨x,hx⟩ := he
    exact ⟨z,x,by rw [hx]; abel⟩
  · rintro ⟨z,x,hx⟩
    refine ⟨Submodule.Quotient.mk z,?_⟩
    change (Submodule.Quotient.mk (D.restrictOneCocycles L hr loc hloc z) :
      D.GaugeLocalH1 L hr loc hloc)=Submodule.Quotient.mk a
    rw [Submodule.Quotient.eq]
    refine ⟨-x,?_⟩
    rw [map_neg]
    rw [← hx]
    abel

@[simp] theorem h1GluingProjection_restrict (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.globalOneCocycles hr) :
    D.h1GluingProjection L hr loc hloc (D.restrictOneCocycles L hr loc hloc z)=0 := by
  apply (D.h1GluingProjection_zero_iff L hr loc hloc _).mpr
  exact ⟨z,0,by rw [map_zero,add_zero]⟩

noncomputable def h1GluingObstruction (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc)
    (b0 : D.continuousOneCochains) (hb0 : D.continuousDifferential hr b0=z.1.1) :
    D.LocalH1GluingCokernel L hr loc hloc :=
  D.h1GluingProjection L hr loc hloc (D.localMismatchAfterPrimitive L hr loc hloc z b0 hb0)

theorem localGauge_zero_iff_h1Gluing_zero (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc)
    (b0 : D.continuousOneCochains) (hb0 : D.continuousDifferential hr b0=z.1.1) :
    D.localGaugeClass L hr loc hloc z=0 ↔ D.h1GluingObstruction L hr loc hloc z b0 hb0=0 := by
  unfold h1GluingObstruction
  rw [D.localGaugeClass_zero_iff,D.h1GluingProjection_zero_iff]
  constructor
  · rintro ⟨b,x,hb,ha⟩
    have hz : D.continuousDifferential hr (b-b0)=0 := by rw [map_sub,hb,hb0,sub_self]
    refine ⟨⟨b-b0,hz⟩,x,?_⟩
    apply Subtype.ext
    change D.restrictOne L loc hloc (b-b0)+(D.localGaugeCoboundary L hr loc hloc x).1=
      z.1.2-D.restrictOne L loc hloc b0
    rw [map_sub]
    calc
      _ = (D.restrictOne L loc hloc b+(D.localGaugeCoboundary L hr loc hloc x).1)-
          D.restrictOne L loc hloc b0 := by abel
      _ = _ := by rw [ha]
  · rintro ⟨a,x,ha⟩
    refine ⟨a.1+b0,x,?_,?_⟩
    · rw [map_add,a.property,hb0,zero_add]
    · have he := congrArg (fun w : D.localOneCocycles L loc => w.1) ha
      change D.restrictOne L loc hloc a.1+(D.localGaugeCoboundary L hr loc hloc x).1=
        z.1.2-D.restrictOne L loc hloc b0 at he
      rw [map_add]
      calc
        _ = (D.restrictOne L loc hloc a.1+(D.localGaugeCoboundary L hr loc hloc x).1)+
            D.restrictOne L loc hloc b0 := by abel
        _ = _ := by rw [he,sub_add_cancel]

theorem h1GluingObstruction_independent_primitive (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc) (b0 b1 : D.continuousOneCochains)
    (hb0 : D.continuousDifferential hr b0=z.1.1)
    (hb1 : D.continuousDifferential hr b1=z.1.1) :
    D.h1GluingObstruction L hr loc hloc z b0 hb0=
      D.h1GluingObstruction L hr loc hloc z b1 hb1 := by
  have hz : D.continuousDifferential hr (b1-b0)=0 := by rw [map_sub,hb1,hb0,sub_self]
  have he : D.localMismatchAfterPrimitive L hr loc hloc z b0 hb0-
      D.localMismatchAfterPrimitive L hr loc hloc z b1 hb1=
      D.restrictOneCocycles L hr loc hloc ⟨b1-b0,hz⟩ := by
    apply Subtype.ext
    change (z.1.2-D.restrictOne L loc hloc b0)-(z.1.2-D.restrictOne L loc hloc b1)=
      D.restrictOne L loc hloc (b1-b0)
    rw [map_sub]
    abel
  apply sub_eq_zero.mp
  unfold h1GluingObstruction
  rw [← map_sub,he,D.h1GluingProjection_restrict]

/-- This is a criterion, not an assertion that localization is surjective. -/
theorem localGauge_zero_of_surjective_h1_restriction (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc)
    (b0 : D.continuousOneCochains) (hb0 : D.continuousDifferential hr b0=z.1.1)
    (hs : Function.Surjective (D.gaugeRestrictionH1 L hr loc hloc)) :
    D.localGaugeClass L hr loc hloc z=0 := by
  rw [D.localGauge_zero_iff_h1Gluing_zero L hr loc hloc z b0 hb0]
  change (Submodule.Quotient.mk _ : D.LocalH1GluingCokernel L hr loc hloc)=0
  rw [Submodule.Quotient.mk_eq_zero]
  exact hs _

theorem local_conjugacy_lifts_iff_h1_gluing_zero (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (t : ∀ i, L i →* Aˣ) (ht : ∀ i h, D.q (t i h)=D.rho (loc i h))
    (htc : ∀ i, Continuous (t i))
    (b0 : D.continuousOneCochains)
    (hb0 : D.continuousDifferential hr b0=(D.prescribedLocalPair L hr loc hloc t ht htc).1.1) :
    (∃ lift : G →* Aˣ, Continuous lift ∧
      (∀ g, D.q (lift g)=D.rho g) ∧
      ∃ u : I → Aˣ, (∀ i, D.q (u i)=1) ∧
        ∀ i h, u i*lift (loc i h)*(u i)⁻¹=t i h) ↔
    D.h1GluingObstruction L hr loc hloc (D.prescribedLocalPair L hr loc hloc t ht htc) b0 hb0=0 := by
  rw [D.continuous_local_conjugacy_lifts_iff]
  exact D.localGauge_zero_iff_h1Gluing_zero L hr loc hloc _ b0 hb0

end Komorebi.StrongArtin.SquareZeroH2.Datum
