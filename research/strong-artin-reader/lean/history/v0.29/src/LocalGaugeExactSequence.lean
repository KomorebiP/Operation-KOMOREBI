import ContinuousH1GluingObstruction

/-! The secondary H1 localization cokernel is EXACTLY the kernel of forgetting
local gauge data in degree two. We do not assert that the absolute map is surjective. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G A B I : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable (D : Datum G A B) (L : I → Type)
variable [∀ i, Group (L i)] [∀ i, TopologicalSpace (L i)]

def zeroGlobalLocalPair (loc : ∀ i, L i →* G) :
    D.localOneCocycles L loc →ₗ[ℤ] D.localConstraintPairs L loc where
  toFun a := ⟨(0,a.1),fun i g h => (a.property i g h).symm⟩
  map_add' a b := by apply Subtype.ext; exact Prod.ext (by simp) rfl
  map_smul' r a := by apply Subtype.ext; exact Prod.ext (by simp) rfl

noncomputable def localCocycleToGaugeH2 (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    D.localOneCocycles L loc →ₗ[ℤ] D.LocalGaugeH2 L hr loc hloc :=
  ((LinearMap.range (D.localGaugeDifferential L hr loc hloc)).mkQ).comp
    (D.zeroGlobalLocalPair L loc)

theorem localCocycleToGaugeH2_zero_iff (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (a : D.localOneCocycles L loc) :
    D.localCocycleToGaugeH2 L hr loc hloc a=0 ↔
      D.h1GluingProjection L hr loc hloc a=0 := by
  change D.localGaugeClass L hr loc hloc (D.zeroGlobalLocalPair L loc a)=0 ↔ _
  rw [D.localGaugeClass_zero_iff,D.h1GluingProjection_zero_iff]
  constructor
  · rintro ⟨b,x,hb,ha⟩
    exact ⟨⟨b,hb⟩,x,Subtype.ext ha⟩
  · rintro ⟨b,x,hb⟩
    exact ⟨b.1,x,b.property,congrArg Subtype.val hb⟩

noncomputable def localH1ToGaugeH2 (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    D.GaugeLocalH1 L hr loc hloc →ₗ[ℤ] D.LocalGaugeH2 L hr loc hloc :=
  (LinearMap.range (D.localGaugeCoboundary L hr loc hloc)).liftQ
    (D.localCocycleToGaugeH2 L hr loc hloc) (by
      rintro a ⟨x,rfl⟩
      rw [LinearMap.mem_ker,D.localCocycleToGaugeH2_zero_iff,D.h1GluingProjection_zero_iff]
      exact ⟨0,x,by rw [map_zero,zero_add]⟩)

noncomputable def h1GluingToGaugeH2 (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    D.LocalH1GluingCokernel L hr loc hloc →ₗ[ℤ] D.LocalGaugeH2 L hr loc hloc :=
  (LinearMap.range (D.gaugeRestrictionH1 L hr loc hloc)).liftQ
    (D.localH1ToGaugeH2 L hr loc hloc) (by
      rintro a ⟨z,rfl⟩
      obtain ⟨b,rfl⟩ := (LinearMap.range (D.globalGaugeCoboundary hr)).mkQ_surjective z
      change D.localCocycleToGaugeH2 L hr loc hloc (D.restrictOneCocycles L hr loc hloc b)=0
      rw [D.localCocycleToGaugeH2_zero_iff,D.h1GluingProjection_restrict])

@[simp] theorem h1GluingToGaugeH2_projection (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (a : D.localOneCocycles L loc) :
    D.h1GluingToGaugeH2 L hr loc hloc (D.h1GluingProjection L hr loc hloc a)=
      D.localCocycleToGaugeH2 L hr loc hloc a := rfl

theorem h1GluingProjection_surjective (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    Function.Surjective (D.h1GluingProjection L hr loc hloc) :=
  (LinearMap.range (D.gaugeRestrictionH1 L hr loc hloc)).mkQ_surjective.comp
    (LinearMap.range (D.localGaugeCoboundary L hr loc hloc)).mkQ_surjective

theorem h1GluingToGaugeH2_injective (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    Function.Injective (D.h1GluingToGaugeH2 L hr loc hloc) := by
  apply (LinearMap.ker_eq_bot).mp
  apply (Submodule.eq_bot_iff _).mpr
  intro y hy
  obtain ⟨a,rfl⟩ := D.h1GluingProjection_surjective L hr loc hloc y
  change D.localCocycleToGaugeH2 L hr loc hloc a=0 at hy
  exact (D.localCocycleToGaugeH2_zero_iff L hr loc hloc a).mp hy

noncomputable def gaugePairToAbsolute (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) :
    D.localConstraintPairs L loc →ₗ[ℤ] D.ContinuousH2 hr :=
  ((LinearMap.range (D.continuousDifferential hr)).mkQ).comp
    ((LinearMap.fst ℤ _ _).comp (D.localConstraintPairs L loc).subtype)

noncomputable def gaugeForgetAbsolute (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    D.LocalGaugeH2 L hr loc hloc →ₗ[ℤ] D.ContinuousH2 hr :=
  (LinearMap.range (D.localGaugeDifferential L hr loc hloc)).liftQ
    (D.gaugePairToAbsolute L hr loc) (by
      rintro z ⟨⟨b,x⟩,rfl⟩
      change (Submodule.Quotient.mk (D.continuousDifferential hr b+0) : D.ContinuousH2 hr)=0
      rw [add_zero,Submodule.Quotient.mk_eq_zero]
      exact ⟨b,rfl⟩)

@[simp] theorem gaugeForgetAbsolute_localCocycle (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (a : D.localOneCocycles L loc) :
    D.gaugeForgetAbsolute L hr loc hloc (D.localCocycleToGaugeH2 L hr loc hloc a)=0 := rfl

/-- Exactness; this is NOT a claim that every absolute H2 class admits local lifts. -/
theorem h1Gluing_image_eq_absolute_kernel (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    LinearMap.range (D.h1GluingToGaugeH2 L hr loc hloc)=
      LinearMap.ker (D.gaugeForgetAbsolute L hr loc hloc) := by
  ext y
  constructor
  · rintro ⟨x,rfl⟩
    obtain ⟨a,rfl⟩ := D.h1GluingProjection_surjective L hr loc hloc x
    change D.gaugeForgetAbsolute L hr loc hloc (D.localCocycleToGaugeH2 L hr loc hloc a)=0
    exact D.gaugeForgetAbsolute_localCocycle L hr loc hloc a
  · intro hy
    obtain ⟨z,rfl⟩ := (LinearMap.range (D.localGaugeDifferential L hr loc hloc)).mkQ_surjective y
    change (Submodule.Quotient.mk z.1.1 : D.ContinuousH2 hr)=0 at hy
    rw [Submodule.Quotient.mk_eq_zero] at hy
    obtain ⟨b,hb⟩ := hy
    let a := D.localMismatchAfterPrimitive L hr loc hloc z b hb
    refine ⟨D.h1GluingProjection L hr loc hloc a,?_⟩
    change D.localGaugeClass L hr loc hloc (D.zeroGlobalLocalPair L loc a)=
      D.localGaugeClass L hr loc hloc z
    symm
    apply D.localGaugeClass_eq_of_boundary L hr loc hloc z (D.zeroGlobalLocalPair L loc a) b 0
    apply Subtype.ext
    apply Prod.ext
    · change z.1.1-0=D.continuousDifferential hr b+0
      rw [hb,sub_zero,add_zero]
    · change z.1.2-(z.1.2-D.restrictOne L loc hloc b)=
        D.restrictOne L loc hloc b+(D.localGaugeCoboundary L hr loc hloc 0).1
      rw [map_zero]
      change z.1.2-(z.1.2-D.restrictOne L loc hloc b)=D.restrictOne L loc hloc b+0
      abel

end Komorebi.StrongArtin.SquareZeroH2.Datum
