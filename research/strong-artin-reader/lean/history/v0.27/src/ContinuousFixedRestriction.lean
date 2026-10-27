import ContinuousRepresentationLifting
import FixedRestrictionObstruction

/-! Strict fixed-subgroup lifting on continuous cochains. The subgroup may be
arbitrary; an initial continuous extension of its prescribed lifts is assumed here
and constructed separately for clopen subgroups. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable [TopologicalSpace G] [IsTopologicalGroup G]
variable [TopologicalSpace A] [DiscreteTopology A]
variable (D : Datum G A B) (H : Subgroup G)

def continuousRelativeOneCochains : Submodule ℤ D.continuousOneCochains where
  carrier := {b | ∀ g ∈ H, b.1 g = 0}
  zero_mem' := by intro g hg; rfl
  add_mem' := by
    intro a b ha hb g hg
    change a.1 g+b.1 g=0
    rw [ha g hg,hb g hg,add_zero]
  smul_mem' := by intro r b hb g hg; change r • b.1 g=0; rw [hb g hg,smul_zero]

def continuousRelativeTwoCocycles : Submodule ℤ D.continuousTwoCocycles where
  carrier := {c | ∀ g ∈ H, ∀ h ∈ H, c.1 (g,h)=0}
  zero_mem' := by intro g hg h hh; rfl
  add_mem' := by
    intro a b ha hb g hg h hh
    change a.1 (g,h)+b.1 (g,h)=0
    rw [ha g hg h hh,hb g hg h hh,add_zero]
  smul_mem' := by
    intro r c hc g hg h hh
    change r • c.1 (g,h)=0
    rw [hc g hg h hh,smul_zero]

def continuousRelativeDifferential (hr : Continuous D.lift) :
    D.continuousRelativeOneCochains H →ₗ[ℤ] D.continuousRelativeTwoCocycles H where
  toFun b := ⟨D.continuousDifferential hr b.1, by
    intro g hg h hh
    change D.action g (b.1.1 h) - b.1.1 (g*h) + b.1.1 g = 0
    rw [b.property h hh,b.property (g*h) (H.mul_mem hg hh),b.property g hg]
    simp⟩
  map_add' a b := by apply Subtype.ext; exact map_add (D.continuousDifferential hr) _ _
  map_smul' r b := by apply Subtype.ext; exact map_smul (D.continuousDifferential hr) _ _

abbrev ContinuousRelativeH2 (hr : Continuous D.lift) :=
  D.continuousRelativeTwoCocycles H ⧸ LinearMap.range (D.continuousRelativeDifferential H hr)

def continuousRelativeDefect (hr : Continuous D.lift)
    (hH : ∀ g ∈ H, ∀ h ∈ H, D.lift (g*h)=D.lift g*D.lift h) :
    D.continuousRelativeTwoCocycles H :=
  ⟨D.continuousDefectOf D.lift D.lift_residue hr, by
    intro g hg h hh
    apply Subtype.ext
    change ((D.lift g : A)*D.lift h-D.lift (g*h))*↑(D.lift (g*h))⁻¹=0
    rw [hH g hg h hh,Units.val_mul,sub_self,zero_mul]⟩

noncomputable def continuousRelativeObstruction (hr : Continuous D.lift)
    (hH : ∀ g ∈ H, ∀ h ∈ H, D.lift (g*h)=D.lift g*D.lift h) :
    D.ContinuousRelativeH2 H hr := Submodule.Quotient.mk (D.continuousRelativeDefect H hr hH)

theorem continuousRelativeObstruction_zero_iff (hr : Continuous D.lift)
    (hH : ∀ g ∈ H, ∀ h ∈ H, D.lift (g*h)=D.lift g*D.lift h) :
    D.continuousRelativeObstruction H hr hH=0 ↔
      ∃ b : G → D.Kernel, Continuous b ∧ (∀ g ∈ H, b g=0) ∧ ∀ g h,
        D.normalizedDefect D.lift D.lift_residue (g,h)=D.action g (b h)-b (g*h)+b g := by
  change (Submodule.Quotient.mk (D.continuousRelativeDefect H hr hH) :
    D.ContinuousRelativeH2 H hr)=0 ↔ _
  rw [Submodule.Quotient.mk_eq_zero]
  constructor
  · rintro ⟨b,hb⟩
    refine ⟨b.1.1,b.1.property,b.property,fun g h => ?_⟩
    exact (congrArg (fun z : D.continuousRelativeTwoCocycles H => z.1.1 (g,h)) hb).symm
  · rintro ⟨b,hbc,hbH,hb⟩
    refine ⟨⟨⟨b,hbc⟩,hbH⟩, ?_⟩
    apply Subtype.ext
    apply Subtype.ext
    apply groupCohomology.cocycles₂_ext
    intro g h
    exact (hb g h).symm

theorem continuous_fixed_restriction_lifts_iff (hr : Continuous D.lift)
    (hH : ∀ g ∈ H, ∀ h ∈ H, D.lift (g*h)=D.lift g*D.lift h) :
    (∃ L : G →* Aˣ, Continuous L ∧ (∀ g, D.q (L g)=D.rho g) ∧
      ∀ g ∈ H, L g=D.lift g) ↔ D.continuousRelativeObstruction H hr hH=0 := by
  rw [D.continuousRelativeObstruction_zero_iff H hr hH]
  constructor
  · rintro ⟨L,hLc,hL,hfix⟩
    let b := D.liftDifference D.lift L D.lift_residue hL
    refine ⟨-b,(D.continuous_liftDifference D.lift L D.lift_residue hL hr hLc).neg, ?_, ?_⟩
    · intro g hg
      have hb : b g=0 := by apply Subtype.ext; simp [b,liftDifference,hfix g hg]
      change -(b g)=0
      rw [hb,neg_zero]
    · intro g h
      have he := D.normalizedDefect_change D.lift L D.lift_residue hL g h
      have hz : D.normalizedDefect L hL (g,h)=0 := by
        apply Subtype.ext
        change ((L g : A)*L h-L (g*h))*↑(L (g*h))⁻¹=0
        simp
      rw [hz] at he
      change 0 = D.normalizedDefect D.lift D.lift_residue (g,h)+
        (D.action g (b h)-b (g*h)+b g) at he
      simp only [Pi.neg_apply,map_neg]
      exact eq_neg_of_add_eq_zero_left he.symm |>.trans (by abel)
  · rintro ⟨b,hbc,hbH,hb⟩
    refine ⟨D.liftFromPrimitive b hb,D.continuous_liftFromPrimitive hr b hbc hb,
      D.correctedLift_residue (-b), ?_⟩
    intro g hg
    rw [D.liftFromPrimitive_apply]
    apply Units.ext
    change (1+((-b) g : A))*D.lift g=(D.lift g : A)
    simp [hbH g hg]

theorem continuous_relative_zero_implies_absolute_zero (hr : Continuous D.lift)
    (hH : ∀ g ∈ H, ∀ h ∈ H, D.lift (g*h)=D.lift g*D.lift h)
    (hz : D.continuousRelativeObstruction H hr hH=0) :
    D.continuousObstruction hr=0 := by
  obtain ⟨L,hLc,hL,_⟩ := (D.continuous_fixed_restriction_lifts_iff H hr hH).mpr hz
  exact (D.continuous_representation_lifts_iff hr).mp ⟨L,hLc,hL⟩

end Komorebi.StrongArtin.SquareZeroH2.Datum
