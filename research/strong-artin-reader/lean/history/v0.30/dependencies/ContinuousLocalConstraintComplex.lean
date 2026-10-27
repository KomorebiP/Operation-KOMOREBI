import ContinuousRepresentationLifting

/-! Continuous degree-two obstruction pairs for simultaneous literal local
prescriptions. Local groups may map to G by arbitrary continuous homomorphisms.
This is an explicit low-degree cochain quotient, not an asserted comparison to
an arithmetic Selmer complex or to Mathlib's homogeneous continuous cohomology. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G A B I : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable (D : Datum G A B) (L : I → Type)
variable [∀ i, Group (L i)] [∀ i, TopologicalSpace (L i)]

def localOneCochains : Submodule ℤ (∀ i, L i → D.Kernel) where
  carrier := {a | ∀ i, Continuous (a i)}
  zero_mem' := fun _ => continuous_const
  add_mem' := fun ha hb i => (ha i).add (hb i)
  smul_mem' := fun r _a ha i =>
    (continuous_of_discreteTopology : Continuous (fun x : D.Kernel => r • x)).comp (ha i)

def restrictOne (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    D.continuousOneCochains →ₗ[ℤ] D.localOneCochains L where
  toFun b := ⟨fun i h => b.1 (loc i h), fun i => b.property.comp (hloc i)⟩
  map_add' _ _ := rfl
  map_smul' _ _ := rfl

def localConstraintPairs (loc : ∀ i, L i →* G) :
    Submodule ℤ (D.continuousTwoCocycles × D.localOneCochains L) where
  carrier := {z | ∀ i g h,
    z.1.1 (loc i g,loc i h) =
      D.action (loc i g) (z.2.1 i h)-z.2.1 i (g*h)+z.2.1 i g}
  zero_mem' := by
    intro i g h
    change (0 : D.Kernel)=D.action (loc i g) 0-0+0
    simp
  add_mem' := by
    intro a b ha hb i g h
    change a.1.1 (loc i g,loc i h)+b.1.1 (loc i g,loc i h) =
      D.action (loc i g) (a.2.1 i h+b.2.1 i h) -
        (a.2.1 i (g*h)+b.2.1 i (g*h))+(a.2.1 i g+b.2.1 i g)
    rw [ha i g h,hb i g h,map_add]
    abel
  smul_mem' := by
    intro r a ha i g h
    change r • a.1.1 (loc i g,loc i h) =
      D.action (loc i g) (r • a.2.1 i h)-r • a.2.1 i (g*h)+r • a.2.1 i g
    rw [ha i g h,map_smul]
    change (r • (D.action (loc i g) (a.2.1 i h)-a.2.1 i (g*h)+a.2.1 i g) : D.Kernel) = _
    rw [smul_add,smul_sub]

def localConstraintDifferential (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :
    D.continuousOneCochains →ₗ[ℤ] D.localConstraintPairs L loc where
  toFun b := ⟨(D.continuousDifferential hr b,D.restrictOne L loc hloc b),by
    intro i g h
    change D.action (loc i g) (b.1 (loc i h))-b.1 (loc i g*loc i h)+b.1 (loc i g) =
      D.action (loc i g) (b.1 (loc i h))-b.1 (loc i (g*h))+b.1 (loc i g)
    rw [map_mul]⟩
  map_add' a b := by
    apply Subtype.ext
    exact Prod.ext (map_add _ _ _) (map_add _ _ _)
  map_smul' r b := by
    apply Subtype.ext
    exact Prod.ext (map_smul _ _ _) (map_smul _ _ _)

abbrev LocalConstraintH2 (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i)) :=
  D.localConstraintPairs L loc ⧸ LinearMap.range (D.localConstraintDifferential L hr loc hloc)

noncomputable def localConstraintClass (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc) : D.LocalConstraintH2 L hr loc hloc :=
  Submodule.Quotient.mk z

theorem localConstraintClass_zero_iff (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z : D.localConstraintPairs L loc) :
    D.localConstraintClass L hr loc hloc z = 0 ↔
      ∃ b : D.continuousOneCochains,
        D.continuousDifferential hr b=z.1.1 ∧ D.restrictOne L loc hloc b=z.1.2 := by
  change (Submodule.Quotient.mk z : D.LocalConstraintH2 L hr loc hloc)=0 ↔ _
  rw [Submodule.Quotient.mk_eq_zero]
  constructor
  · rintro ⟨b,hb⟩
    exact ⟨b,congrArg (fun x : D.localConstraintPairs L loc => x.1.1) hb,
      congrArg (fun x : D.localConstraintPairs L loc => x.1.2) hb⟩
  · rintro ⟨b,hb,hl⟩
    refine ⟨b,?_⟩
    apply Subtype.ext
    exact Prod.ext hb hl

/-- This is an explicit boundary calculation in one fixed coefficient action. -/
theorem localConstraintClass_eq_of_boundary (hr : Continuous D.lift)
    (loc : ∀ i, L i →* G) (hloc : ∀ i, Continuous (loc i))
    (z z' : D.localConstraintPairs L loc) (b : D.continuousOneCochains)
    (he : z-z'=D.localConstraintDifferential L hr loc hloc b) :
    D.localConstraintClass L hr loc hloc z=D.localConstraintClass L hr loc hloc z' := by
  change (Submodule.Quotient.mk z : D.LocalConstraintH2 L hr loc hloc)=Submodule.Quotient.mk z'
  rw [Submodule.Quotient.eq]
  exact ⟨b,he.symm⟩

end Komorebi.StrongArtin.SquareZeroH2.Datum
