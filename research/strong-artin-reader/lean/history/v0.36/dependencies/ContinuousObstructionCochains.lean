import ContinuousSquareZeroData

/-! Explicit degree-two continuous INHOMOGENEOUS cochains, using Mathlib's
ordinary cocycles and differential, restricted by actual continuity proofs.
No identification with the separate homogeneous `continuousCohomology` API is asserted. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable (D : Datum G A B)

def continuousOneCochains : Submodule ℤ (G → D.Kernel) where
  carrier := {b | Continuous b}
  zero_mem' := continuous_const
  add_mem' := fun ha hb => ha.add hb
  smul_mem' := fun r _b hb =>
    (continuous_of_discreteTopology : Continuous (fun x : D.Kernel => r • x)).comp hb

def continuousTwoCocycles : Submodule ℤ (groupCohomology.cocycles₂ D.coefficientRep) where
  carrier := {c | @Continuous (G × G) D.Kernel inferInstance inferInstance (fun z => c z)}
  zero_mem' := continuous_const
  add_mem' := fun ha hb => ha.add hb
  smul_mem' := fun r _c hc =>
    (continuous_of_discreteTopology : Continuous (fun x : D.Kernel => r • x)).comp hc

def continuousDifferential (hr : Continuous D.lift) :
    D.continuousOneCochains →ₗ[ℤ] D.continuousTwoCocycles where
  toFun b :=
    ⟨⟨groupCohomology.d₁₂ D.coefficientRep b.1,
      groupCohomology.d₁₂_apply_mem_cocycles₂ (A := D.coefficientRep) b.1⟩, by
      change Continuous (fun z : G × G =>
        D.action z.1 (b.1 z.2) - b.1 (z.1*z.2) + b.1 z.1)
      exact ((D.continuous_kernel_action hr).comp
        (continuous_fst.prodMk (b.property.comp continuous_snd)) |>.sub
        (b.property.comp continuous_mul)).add (b.property.comp continuous_fst)⟩
  map_add' a b := by
    apply Subtype.ext
    apply groupCohomology.cocycles₂_ext
    intro g h
    change D.action g (a.1 h+b.1 h) - (a.1 (g*h)+b.1 (g*h)) + (a.1 g+b.1 g) =
      (D.action g (a.1 h)-a.1 (g*h)+a.1 g) + (D.action g (b.1 h)-b.1 (g*h)+b.1 g)
    rw [map_add]
    abel
  map_smul' r b := by
    apply Subtype.ext
    apply groupCohomology.cocycles₂_ext
    intro g h
    change D.action g (r • b.1 h) - r • b.1 (g*h) + r • b.1 g =
      r • (D.action g (b.1 h)-b.1 (g*h)+b.1 g)
    rw [map_smul,smul_add,smul_sub]

abbrev ContinuousH2 (hr : Continuous D.lift) :=
  D.continuousTwoCocycles ⧸ LinearMap.range (D.continuousDifferential hr)

def continuousDefectOf (s : G → Aˣ) (hs : ∀ g, D.q (s g)=D.rho g)
    (hc : Continuous s) : D.continuousTwoCocycles :=
  ⟨D.defectCocycle s hs, D.continuous_normalizedDefect s hs hc⟩

noncomputable def continuousObstructionOf (hr : Continuous D.lift)
    (s : G → Aˣ) (hs : ∀ g, D.q (s g)=D.rho g) (hc : Continuous s) :
    D.ContinuousH2 hr := Submodule.Quotient.mk (D.continuousDefectOf s hs hc)

noncomputable def continuousObstruction (hr : Continuous D.lift) : D.ContinuousH2 hr :=
  D.continuousObstructionOf hr D.lift D.lift_residue hr

theorem continuousObstruction_zero_iff (hr : Continuous D.lift) :
    D.continuousObstruction hr = 0 ↔
      ∃ b : G → D.Kernel, Continuous b ∧ ∀ g h,
        D.normalizedDefect D.lift D.lift_residue (g,h) =
          D.action g (b h)-b (g*h)+b g := by
  change (Submodule.Quotient.mk (D.continuousDefectOf D.lift D.lift_residue hr) :
    D.ContinuousH2 hr) = 0 ↔ _
  rw [Submodule.Quotient.mk_eq_zero]
  constructor
  · rintro ⟨b,hb⟩
    refine ⟨b.1,b.property, fun g h => ?_⟩
    have hv := congrArg (fun z : D.continuousTwoCocycles => z.1 (g,h)) hb
    exact hv.symm
  · rintro ⟨b,hbc,hb⟩
    refine ⟨⟨b,hbc⟩, ?_⟩
    apply Subtype.ext
    apply groupCohomology.cocycles₂_ext
    intro g h
    exact (hb g h).symm

/-- Changing a CONTINUOUS provisional section changes the cocycle by a
CONTINUOUS coboundary. Equality is in a single fixed coefficient action. -/
theorem continuousObstructionOf_eq (hr : Continuous D.lift)
    (s t : G → Aˣ) (hs : ∀ g, D.q (s g)=D.rho g)
    (ht : ∀ g, D.q (t g)=D.rho g) (hsc : Continuous s) (htc : Continuous t) :
    D.continuousObstructionOf hr s hs hsc =
      D.continuousObstructionOf hr t ht htc := by
  change (Submodule.Quotient.mk (D.continuousDefectOf s hs hsc) : D.ContinuousH2 hr) =
    Submodule.Quotient.mk (D.continuousDefectOf t ht htc)
  rw [Submodule.Quotient.eq]
  let b : D.continuousOneCochains :=
    ⟨-(D.liftDifference s t hs ht), (D.continuous_liftDifference s t hs ht hsc htc).neg⟩
  refine ⟨b, ?_⟩
  apply Subtype.ext
  apply groupCohomology.cocycles₂_ext
  intro g h
  change D.action g (-(D.liftDifference s t hs ht h)) -
    (-(D.liftDifference s t hs ht (g*h))) + (-(D.liftDifference s t hs ht g)) =
    D.normalizedDefect s hs (g,h)-D.normalizedDefect t ht (g,h)
  rw [D.normalizedDefect_change s t hs ht, map_neg]
  abel

end Komorebi.StrongArtin.SquareZeroH2.Datum
