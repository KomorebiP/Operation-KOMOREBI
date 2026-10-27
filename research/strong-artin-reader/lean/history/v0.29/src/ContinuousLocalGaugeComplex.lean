import ContinuousGaugeCoboundaries

/-! Degree-two compatible pairs modulo global corrections AND local degree-zero
changes. This is the explicit low-degree mapping-fibre convention, not an
asserted comparison with an arithmetic Selmer complex. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G A B I : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable (D : Datum G A B) (L : I → Type)
variable [∀ i, Group (L i)] [∀ i, TopologicalSpace (L i)]

def localGaugePair (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    (I → D.Kernel) →ₗ[ℤ] D.localConstraintPairs L loc where
  toFun x := ⟨(0,(D.localGaugeCoboundary L hr loc hloc x).1),by
    intro i g h
    exact ((D.localGaugeCoboundary L hr loc hloc x).property i g h).symm⟩
  map_add' x y := by
    apply Subtype.ext
    apply Prod.ext
    · simp
    · exact congrArg Subtype.val (map_add (D.localGaugeCoboundary L hr loc hloc) x y)
  map_smul' r x := by
    apply Subtype.ext
    apply Prod.ext
    · simp
    · exact congrArg Subtype.val (map_smul (D.localGaugeCoboundary L hr loc hloc) r x)

def localGaugeDifferential (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    (D.continuousOneCochains × (I → D.Kernel)) →ₗ[ℤ] D.localConstraintPairs L loc :=
  (D.localConstraintDifferential L hr loc hloc).comp (LinearMap.fst ℤ _ _) +
    (D.localGaugePair L hr loc hloc).comp (LinearMap.snd ℤ _ _)

abbrev LocalGaugeH2 (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :=
  D.localConstraintPairs L loc ⧸ LinearMap.range (D.localGaugeDifferential L hr loc hloc)

noncomputable def localGaugeClass (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc) : D.LocalGaugeH2 L hr loc hloc :=
  Submodule.Quotient.mk z

theorem localGaugeClass_zero_iff (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc) :
    D.localGaugeClass L hr loc hloc z=0 ↔
      ∃ b : D.continuousOneCochains, ∃ x : I → D.Kernel,
        D.continuousDifferential hr b=z.1.1 ∧
        D.restrictOne L loc hloc b+(D.localGaugeCoboundary L hr loc hloc x).1=z.1.2 := by
  change (Submodule.Quotient.mk z : D.LocalGaugeH2 L hr loc hloc)=0 ↔ _
  rw [Submodule.Quotient.mk_eq_zero]
  constructor
  · rintro ⟨⟨b,x⟩,he⟩
    refine ⟨b,x,?_,?_⟩
    · have hc := congrArg (fun p : D.localConstraintPairs L loc => p.1.1) he
      change D.continuousDifferential hr b+0=z.1.1 at hc
      simpa only [add_zero] using hc
    · exact congrArg (fun p : D.localConstraintPairs L loc => p.1.2) he
  · rintro ⟨b,x,hc,ha⟩
    refine ⟨(b,x),?_⟩
    apply Subtype.ext
    apply Prod.ext
    · change D.continuousDifferential hr b+0=z.1.1
      simpa only [add_zero] using hc
    · exact ha

theorem strict_boundary_is_gauge_boundary (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    LinearMap.range (D.localConstraintDifferential L hr loc hloc) ≤
      LinearMap.range (D.localGaugeDifferential L hr loc hloc) := by
  rintro z ⟨b,rfl⟩
  refine ⟨(b,0),?_⟩
  change D.localConstraintDifferential L hr loc hloc b+D.localGaugePair L hr loc hloc 0=_
  rw [map_zero,add_zero]

noncomputable def strictToGaugeH2 (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    D.LocalConstraintH2 L hr loc hloc →ₗ[ℤ] D.LocalGaugeH2 L hr loc hloc :=
  (LinearMap.range (D.localConstraintDifferential L hr loc hloc)).liftQ
    (LinearMap.range (D.localGaugeDifferential L hr loc hloc)).mkQ (by
      intro z hz
      change Submodule.Quotient.mk z=0
      rw [Submodule.Quotient.mk_eq_zero]
      exact D.strict_boundary_is_gauge_boundary L hr loc hloc hz)

theorem strictToGaugeH2_surjective (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    Function.Surjective (D.strictToGaugeH2 L hr loc hloc) := by
  intro y
  obtain ⟨z,rfl⟩ := (LinearMap.range (D.localGaugeDifferential L hr loc hloc)).mkQ_surjective y
  exact ⟨Submodule.Quotient.mk z,rfl⟩

theorem strict_zero_implies_gauge_zero (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc) (hz : D.localConstraintClass L hr loc hloc z=0) :
    D.localGaugeClass L hr loc hloc z=0 := by
  obtain ⟨b,hc,hl⟩ := (D.localConstraintClass_zero_iff L hr loc hloc z).mp hz
  apply (D.localGaugeClass_zero_iff L hr loc hloc z).mpr
  refine ⟨b,0,hc,?_⟩
  rw [map_zero]
  change D.restrictOne L loc hloc b+0=z.1.2
  simpa only [add_zero] using hl

theorem localGaugeClass_eq_of_boundary (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z z' : D.localConstraintPairs L loc) (b : D.continuousOneCochains) (x : I → D.Kernel)
    (he : z-z'=D.localGaugeDifferential L hr loc hloc (b,x)) :
    D.localGaugeClass L hr loc hloc z=D.localGaugeClass L hr loc hloc z' := by
  change (Submodule.Quotient.mk z : D.LocalGaugeH2 L hr loc hloc)=Submodule.Quotient.mk z'
  rw [Submodule.Quotient.eq]
  exact ⟨(b,x),he.symm⟩

end Komorebi.StrongArtin.SquareZeroH2.Datum
