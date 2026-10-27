import FiniteQuotientObstructionVanishing
import ContinuousFixedRestriction

/-! Constructive vanishing with a prescribed subgroup lift, under order
invertibility for the finite group and subgroup. The primitive is adjusted by a
zero-coboundary so that it vanishes on the subgroup EXACTLY. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum
open FiniteCohomologyAveraging

variable {G A B : Type} [Group G] [Fintype G] [Ring A] [Ring B]
variable (D : Datum G A B) (H : Subgroup G) [Fintype H]

theorem relative_primitive_of_groupOrders_isUnit
    (hG : IsUnit (Fintype.card G : A)) (hHcard : IsUnit (Fintype.card H : A))
    (hH : ∀ g ∈ H, ∀ h ∈ H, D.lift (g*h)=D.lift g*D.lift h) :
    ∃ b : G → D.Kernel, (∀ g ∈ H, b g=0) ∧ ∀ g h,
      D.normalizedDefect D.lift D.lift_residue (g,h)=D.action g (b h)-b (g*h)+b g := by
  obtain ⟨b,hb⟩ := exists_twoCocycle_primitive D.action
    (D.kernel_nsmul_bijective_of_isUnit _ hG)
    (D.normalizedDefect D.lift D.lift_residue)
    (D.normalizedDefect_cocycle D.lift D.lift_residue)
  have hbf : ∀ g h : H, b (g*h)=b g+D.action g (b h) := by
    intro g h
    have hc : D.normalizedDefect D.lift D.lift_residue (g,h)=0 := by
      apply Subtype.ext
      change ((D.lift g : A)*D.lift h-D.lift (g*h))*↑(D.lift (g*h))⁻¹=0
      rw [hH g g.property h h.property,Units.val_mul,sub_self,zero_mul]
    have he := hb g h
    rw [hc] at he
    have he' : b g+D.action g (b h)-b (g*h)=0 := by
      calc
        b g+D.action g (b h)-b (g*h) = D.action g (b h)-b (g*h)+b g := by abel
        _ = 0 := he.symm
    exact (sub_eq_zero.mp he').symm
  obtain ⟨x,hx⟩ := exists_oneCocycle_primitive (D.action.comp H.subtype)
    (D.kernel_nsmul_bijective_of_isUnit _ hHcard) (fun h : H => b h) hbf
  refine ⟨fun g => b g-(D.action g x-x), ?_, ?_⟩
  · intro g hg
    exact sub_eq_zero.mpr (hx ⟨g,hg⟩)
  · intro g h
    rw [hb g h,map_sub,map_sub]
    have hm : D.action g (D.action h x)=D.action (g*h) x := by
      rw [map_mul]
      rfl
    rw [hm]
    apply Subtype.ext
    simp only [AddSubgroup.coe_add,AddSubgroup.coe_sub]
    abel

theorem relativeObstruction_zero_of_groupOrders_isUnit
    (hG : IsUnit (Fintype.card G : A)) (hHcard : IsUnit (Fintype.card H : A))
    (hH : ∀ g ∈ H, ∀ h ∈ H, D.lift (g*h)=D.lift g*D.lift h) :
    D.relativeObstruction H hH=0 := by
  exact (D.relativeObstruction_zero_iff H hH).mpr
    (D.relative_primitive_of_groupOrders_isUnit H hG hHcard hH)

theorem fixed_restriction_lifts_of_groupOrders_isUnit
    (hG : IsUnit (Fintype.card G : A)) (hHcard : IsUnit (Fintype.card H : A))
    (hH : ∀ g ∈ H, ∀ h ∈ H, D.lift (g*h)=D.lift g*D.lift h) :
    ∃ L : G →* Aˣ, (∀ g, D.q (L g)=D.rho g) ∧ ∀ g ∈ H, L g=D.lift g := by
  exact (D.fixed_restriction_lifts_iff_relativeObstruction_zero H hH).mpr
    (D.relativeObstruction_zero_of_groupOrders_isUnit H hG hHcard hH)

end Komorebi.StrongArtin.SquareZeroH2.Datum
