import RepresentationH2LiftingCriterion

/-! Fixed-restriction lifting uses the kernel of restriction on COCHAINS.
This is not a quotient of the coefficient module, and is not simply absolute H². -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable (D : Datum G A B) (H : Subgroup G)

/-- Cochains whose correction preserves the entire prescribed subgroup lift. -/
def relativeOneCochains : Submodule ℤ (G → D.Kernel) where
  carrier := {b | ∀ g ∈ H, b g = 0}
  zero_mem' := by intro g hg; rfl
  add_mem' := by intro a b ha hb g hg; simp [ha g hg, hb g hg]
  smul_mem' := by intro r b hb g hg; simp [hb g hg]

/-- Actual two-cocycles restricting to zero on H × H. -/
def relativeTwoCocycles : Submodule ℤ (groupCohomology.cocycles₂ D.coefficientRep) where
  carrier := {c | ∀ g ∈ H, ∀ h ∈ H, c (g,h) = 0}
  zero_mem' := by intro g hg h hh; rfl
  add_mem' := by intro a b ha hb g hg h hh; change a (g,h)+b (g,h)=0; rw [ha g hg h hh,hb g hg h hh,add_zero]
  smul_mem' := by intro r c hc g hg h hh; change r • c (g,h)=0; rw [hc g hg h hh,smul_zero]

/-- Restriction commutes with the actual group-cochain differential. -/
def relativeDifferential : D.relativeOneCochains H →ₗ[ℤ] D.relativeTwoCocycles H where
  toFun b :=
    ⟨⟨groupCohomology.d₁₂ D.coefficientRep b.1,
        groupCohomology.d₁₂_apply_mem_cocycles₂ (A := D.coefficientRep) b.1⟩, by
      intro g hg h hh
      change D.action g (b.1 h) - b.1 (g*h) + b.1 g = 0
      rw [b.property h hh,b.property (g*h) (H.mul_mem hg hh),b.property g hg]
      simp⟩
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


/-- Degree two of the kernel-of-restriction cochain complex. -/
abbrev RelativeH2 := D.relativeTwoCocycles H ⧸ LinearMap.range (D.relativeDifferential H)

def relativeDefect
    (hH : ∀ g ∈ H, ∀ h ∈ H, D.lift (g*h) = D.lift g * D.lift h) :
    D.relativeTwoCocycles H :=
  ⟨D.defectCocycle D.lift D.lift_residue, by
    intro g hg h hh
    apply Subtype.ext
    change ((D.lift g : A)*D.lift h-D.lift (g*h))*↑(D.lift (g*h))⁻¹ = 0
    rw [hH g hg h hh,Units.val_mul,sub_self,zero_mul]⟩

noncomputable def relativeObstruction
    (hH : ∀ g ∈ H, ∀ h ∈ H, D.lift (g*h) = D.lift g * D.lift h) : D.RelativeH2 H :=
  Submodule.Quotient.mk (D.relativeDefect H hH)

/-- A primitive must vanish on the subgroup, not only exist globally. -/
theorem relativeObstruction_zero_iff
    (hH : ∀ g ∈ H, ∀ h ∈ H, D.lift (g*h) = D.lift g * D.lift h) :
    D.relativeObstruction H hH = 0 ↔
      ∃ b : G → D.Kernel, (∀ g ∈ H, b g = 0) ∧ ∀ g h,
        D.normalizedDefect D.lift D.lift_residue (g,h) =
          D.action g (b h)-b (g*h)+b g := by
  change (Submodule.Quotient.mk (D.relativeDefect H hH) : D.RelativeH2 H) = 0 ↔ _
  rw [Submodule.Quotient.mk_eq_zero]
  constructor
  · rintro ⟨b,hb⟩
    refine ⟨b.1,b.property, fun g h => ?_⟩
    have hv := congrArg (fun z : D.relativeTwoCocycles H => z.1 (g,h)) hb
    exact hv.symm
  · rintro ⟨b,hbH,hb⟩
    refine ⟨⟨b,hbH⟩, ?_⟩
    apply Subtype.ext
    apply groupCohomology.cocycles₂_ext
    intro g h
    exact (hb g h).symm

/-- Vanishing of the relative class is exactly lifting with the fixed subgroup map. -/
theorem fixed_restriction_lifts_iff_relativeObstruction_zero
    (hH : ∀ g ∈ H, ∀ h ∈ H, D.lift (g*h) = D.lift g * D.lift h) :
    (∃ lift : G →* Aˣ, (∀ g, D.q (lift g) = D.rho g) ∧
      ∀ g ∈ H, lift g = D.lift g) ↔ D.relativeObstruction H hH = 0 := by
  rw [D.relativeObstruction_zero_iff H hH]
  constructor
  · rintro ⟨lift,hlift,hfixed⟩
    let b := D.liftDifference D.lift lift D.lift_residue hlift
    refine ⟨-b, ?_, ?_⟩
    · intro g hg
      change -(b g)=0
      have hb : b g = 0 := by
        apply Subtype.ext
        simp [b,liftDifference,hfixed g hg]
      rw [hb,neg_zero]
    · intro g h
      have he := D.normalizedDefect_change D.lift lift D.lift_residue hlift g h
      have hz : D.normalizedDefect lift hlift (g,h)=0 := by
        apply Subtype.ext
        change ((lift g : A)*lift h-lift (g*h))*↑(lift (g*h))⁻¹=0
        simp
      rw [hz] at he
      change 0 = D.normalizedDefect D.lift D.lift_residue (g,h)+
        (D.action g (b h)-b (g*h)+b g) at he
      simp only [Pi.neg_apply,map_neg]
      exact eq_neg_of_add_eq_zero_left he.symm |>.trans (by abel)
  · rintro ⟨b,hbH,hb⟩
    refine ⟨D.liftFromPrimitive b hb, D.correctedLift_residue (-b), ?_⟩
    intro g hg
    rw [D.liftFromPrimitive_apply]
    apply Units.ext
    change (1+((-b) g : A))*D.lift g = (D.lift g : A)
    simp [hbH g hg]

/-- Forgetting the prescribed subgroup condition loses information, but preserves vanishing. -/
theorem relative_zero_implies_absolute_zero
    (hH : ∀ g ∈ H, ∀ h ∈ H, D.lift (g*h) = D.lift g * D.lift h)
    (hz : D.relativeObstruction H hH = 0) : D.obstruction = 0 := by
  obtain ⟨lift,hlift,_⟩ := (D.fixed_restriction_lifts_iff_relativeObstruction_zero H hH).mpr hz
  exact D.representation_lifts_iff_obstruction_zero.mp ⟨lift,hlift⟩

end Komorebi.StrongArtin.SquareZeroH2.Datum
