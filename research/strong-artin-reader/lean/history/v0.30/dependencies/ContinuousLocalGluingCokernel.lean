import SimultaneousLocalLiftCriterion

/-! After the absolute H2 obstruction has been cancelled, simultaneous strict
prescriptions are measured by the cokernel of restriction on continuous Z1.
The use of Z1 (not H1) is intentional: prescriptions are preserved literally. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G A B I : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable (D : Datum G A B) (L : I → Type)
variable [∀ i, Group (L i)] [∀ i, TopologicalSpace (L i)]

abbrev globalOneCocycles (hr : Continuous D.lift) :=
  LinearMap.ker (D.continuousDifferential hr)

def localOneCocycles (loc : ∀ i, L i →* G) : Submodule ℤ (D.localOneCochains L) where
  carrier := {a | ∀ i g h,
    D.action (loc i g) (a.1 i h)-a.1 i (g*h)+a.1 i g=0}
  zero_mem' := by intro i g h; change D.action (loc i g) 0-0+0=0; simp
  add_mem' := by
    intro a b ha hb i g h
    change D.action (loc i g) (a.1 i h+b.1 i h)-
      (a.1 i (g*h)+b.1 i (g*h))+(a.1 i g+b.1 i g)=0
    rw [map_add]
    have h1 := ha i g h
    have h2 := hb i g h
    calc
      _ = (D.action (loc i g) (a.1 i h)-a.1 i (g*h)+a.1 i g) +
          (D.action (loc i g) (b.1 i h)-b.1 i (g*h)+b.1 i g) := by abel
      _ = 0 := by rw [h1,h2,add_zero]
  smul_mem' := by
    intro r a ha i g h
    change D.action (loc i g) (r • a.1 i h)-r • a.1 i (g*h)+r • a.1 i g=0
    rw [map_smul,← smul_sub,← smul_add,ha i g h,smul_zero]

def restrictOneCocycles (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    D.globalOneCocycles hr →ₗ[ℤ] D.localOneCocycles L loc where
  toFun b := ⟨D.restrictOne L loc hloc b.1,by
    intro i g h
    have hv := congrArg (fun c : D.continuousTwoCocycles => c.1 (loc i g,loc i h)) b.property
    change D.action (loc i g) (b.1.1 (loc i h))-b.1.1 (loc i g*loc i h)+b.1.1 (loc i g)=0 at hv
    change D.action (loc i g) (b.1.1 (loc i h))-b.1.1 (loc i (g*h))+b.1.1 (loc i g)=0
    rw [map_mul]
    exact hv⟩
  map_add' a b := by apply Subtype.ext; exact map_add _ _ _
  map_smul' r b := by apply Subtype.ext; exact map_smul _ _ _

abbrev StrictLocalGluingCokernel (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :=
  D.localOneCocycles L loc ⧸ LinearMap.range (D.restrictOneCocycles L hr loc hloc)

def localMismatchAfterPrimitive (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc)
    (b0 : D.continuousOneCochains) (hb0 : D.continuousDifferential hr b0=z.1.1) :
    D.localOneCocycles L loc :=
  ⟨z.1.2-D.restrictOne L loc hloc b0,by
    intro i g h
    have hc := z.property i g h
    have hd := congrArg (fun c : D.continuousTwoCocycles => c.1 (loc i g,loc i h)) hb0
    change D.action (loc i g) (b0.1 (loc i h))-b0.1 (loc i g*loc i h)+b0.1 (loc i g)=
      z.1.1.1 (loc i g,loc i h) at hd
    change D.action (loc i g) (z.1.2.1 i h-b0.1 (loc i h))-
      (z.1.2.1 i (g*h)-b0.1 (loc i (g*h)))+(z.1.2.1 i g-b0.1 (loc i g))=0
    rw [map_sub,map_mul]
    rw [hc] at hd
    calc
      _ = (D.action (loc i g) (z.1.2.1 i h)-z.1.2.1 i (g*h)+z.1.2.1 i g) -
          (D.action (loc i g) (b0.1 (loc i h))-b0.1 (loc i g*loc i h)+b0.1 (loc i g)) := by abel
      _ = 0 := sub_eq_zero.mpr hd.symm⟩

noncomputable def strictGluingObstruction (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc)
    (b0 : D.continuousOneCochains) (hb0 : D.continuousDifferential hr b0=z.1.1) :
    D.StrictLocalGluingCokernel L hr loc hloc :=
  Submodule.Quotient.mk (D.localMismatchAfterPrimitive L hr loc hloc z b0 hb0)

theorem strictGluingObstruction_zero_iff (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc)
    (b0 : D.continuousOneCochains) (hb0 : D.continuousDifferential hr b0=z.1.1) :
    D.strictGluingObstruction L hr loc hloc z b0 hb0=0 ↔
      ∃ b : D.globalOneCocycles hr,
        D.restrictOneCocycles L hr loc hloc b=D.localMismatchAfterPrimitive L hr loc hloc z b0 hb0 := by
  change (Submodule.Quotient.mk _ : D.StrictLocalGluingCokernel L hr loc hloc)=0 ↔ _
  rw [Submodule.Quotient.mk_eq_zero]
  rfl

/-- The absolute obstruction and the remaining strict local mismatch are separate. -/
theorem localConstraint_zero_iff_gluing_zero (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc)
    (b0 : D.continuousOneCochains) (hb0 : D.continuousDifferential hr b0=z.1.1) :
    D.localConstraintClass L hr loc hloc z=0 ↔
      D.strictGluingObstruction L hr loc hloc z b0 hb0=0 := by
  rw [D.localConstraintClass_zero_iff,D.strictGluingObstruction_zero_iff]
  constructor
  · rintro ⟨b,hb,hl⟩
    have hz : D.continuousDifferential hr (b-b0)=0 := by rw [map_sub,hb,hb0,sub_self]
    refine ⟨⟨b-b0,hz⟩,?_⟩
    apply Subtype.ext
    change D.restrictOne L loc hloc (b-b0)=z.1.2-D.restrictOne L loc hloc b0
    rw [map_sub,hl]
  · rintro ⟨b,hb⟩
    refine ⟨b.1+b0,?_,?_⟩
    · rw [map_add,b.property,hb0,zero_add]
    · have he := congrArg (fun a : D.localOneCocycles L loc => a.1) hb
      change D.restrictOne L loc hloc b.1=z.1.2-D.restrictOne L loc hloc b0 at he
      rw [map_add,he,sub_add_cancel]

/-- A different global primitive yields the same element of the gluing cokernel. -/
theorem strictGluingObstruction_independent_primitive (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc)
    (b0 b1 : D.continuousOneCochains)
    (hb0 : D.continuousDifferential hr b0=z.1.1)
    (hb1 : D.continuousDifferential hr b1=z.1.1) :
    D.strictGluingObstruction L hr loc hloc z b0 hb0=
      D.strictGluingObstruction L hr loc hloc z b1 hb1 := by
  change (Submodule.Quotient.mk _ : D.StrictLocalGluingCokernel L hr loc hloc)=Submodule.Quotient.mk _
  rw [Submodule.Quotient.eq]
  have hz : D.continuousDifferential hr (b1-b0)=0 := by rw [map_sub,hb1,hb0,sub_self]
  refine ⟨⟨b1-b0,hz⟩,?_⟩
  apply Subtype.ext
  change D.restrictOne L loc hloc (b1-b0)=
    (z.1.2-D.restrictOne L loc hloc b0)-(z.1.2-D.restrictOne L loc hloc b1)
  rw [map_sub]
  abel

/-- Surjective restriction suffices only AFTER the absolute class is cancelled. -/
theorem localConstraint_zero_of_surjective_restriction (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc)
    (b0 : D.continuousOneCochains) (hb0 : D.continuousDifferential hr b0=z.1.1)
    (hs : Function.Surjective (D.restrictOneCocycles L hr loc hloc)) :
    D.localConstraintClass L hr loc hloc z=0 := by
  rw [D.localConstraint_zero_iff_gluing_zero L hr loc hloc z b0 hb0,
    D.strictGluingObstruction_zero_iff]
  exact hs _

end Komorebi.StrongArtin.SquareZeroH2.Datum
