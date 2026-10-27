import ContinuousLocalConstraintComplex

/-! Compare separately prescribed local representation lifts with one global
continuous provisional section. No extension of all local prescriptions to one
section is assumed, and the local maps need not be open embeddings. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G H A B : Type} [Group G] [Group H] [Ring A] [Ring B]
variable (D : Datum G A B)

def pullbackDatum (loc : H →* G) : Datum H A B where
  q := D.q
  squareZero := D.squareZero
  rho := D.rho.comp loc
  lift h := D.lift (loc h)
  lift_one := by rw [map_one,D.lift_one]
  lift_residue h := D.lift_residue (loc h)

@[simp] theorem pullback_action (loc : H →* G) (h : H) (x : D.Kernel) :
    (D.pullbackDatum loc).action h x=D.action (loc h) x := rfl

/-- The sign is chosen so that (1-b) r equals the prescribed local lift. -/
def localCorrection (loc : H →* G) (t : H →* Aˣ)
    (ht : ∀ h, D.q (t h)=D.rho (loc h)) : H → D.Kernel :=
  -((D.pullbackDatum loc).liftDifference (fun h => D.lift (loc h)) t
    (fun h => D.lift_residue (loc h)) ht)

theorem localCorrection_val (loc : H →* G) (t : H →* Aˣ)
    (ht : ∀ h, D.q (t h)=D.rho (loc h)) (h : H) :
    (D.localCorrection loc t ht h : A)=
      -(((t h : A)-D.lift (loc h))*↑(D.lift (loc h))⁻¹) := rfl

theorem localCorrection_boundary (loc : H →* G) (t : H →* Aˣ)
    (ht : ∀ h, D.q (t h)=D.rho (loc h)) (g h : H) :
    D.normalizedDefect D.lift D.lift_residue (loc g,loc h)=
      D.action (loc g) (D.localCorrection loc t ht h)-
        D.localCorrection loc t ht (g*h)+D.localCorrection loc t ht g := by
  let E := D.pullbackDatum loc
  let b : H → D.Kernel := E.liftDifference E.lift t E.lift_residue ht
  have hz : E.normalizedDefect t ht (g,h)=0 := by
    apply Subtype.ext
    change ((t g : A)*t h-t (g*h))*↑(t (g*h))⁻¹=0
    simp
  have he := E.normalizedDefect_change E.lift t E.lift_residue ht g h
  rw [hz] at he
  have hc : E.normalizedDefect E.lift E.lift_residue (g,h)=
      D.normalizedDefect D.lift D.lift_residue (loc g,loc h) := by
    apply Subtype.ext
    change ((D.lift (loc g) : A)*D.lift (loc h)-D.lift (loc (g*h)))*
      ↑(D.lift (loc (g*h)))⁻¹ = _
    rw [map_mul]
    rfl
  rw [hc] at he
  change 0=D.normalizedDefect D.lift D.lift_residue (loc g,loc h)+
    (D.action (loc g) (b h)-b (g*h)+b g) at he
  change D.normalizedDefect D.lift D.lift_residue (loc g,loc h)=
    D.action (loc g) (-(b h))-(-(b (g*h)))+(-(b g))
  rw [map_neg]
  have hn := eq_neg_of_add_eq_zero_left he.symm
  exact hn.trans (by abel)

theorem correctedLift_at_local_iff (loc : H →* G) (t : H →* Aˣ)
    (ht : ∀ h, D.q (t h)=D.rho (loc h)) (b : G → D.Kernel) (h : H) :
    D.correctedLift (-b) (loc h)=t h ↔ b (loc h)=D.localCorrection loc t ht h := by
  constructor
  · intro he
    apply Subtype.ext
    have hv := congrArg (fun u : Aˣ => (u : A)*↑(D.lift (loc h))⁻¹) he
    change (1+((-(b (loc h))) : A))*D.lift (loc h)*↑(D.lift (loc h))⁻¹ = _ at hv
    simp only [mul_assoc,Units.mul_inv,mul_one] at hv
    change (b (loc h) : A) = -(((t h : A)-D.lift (loc h))*↑(D.lift (loc h))⁻¹)
    rw [sub_mul,Units.mul_inv]
    have hv' : 1-(b (loc h) : A)=(t h : A)*↑(D.lift (loc h))⁻¹ := by simpa only [sub_eq_add_neg] using hv
    rw [← hv']
    abel
  · intro he
    apply Units.ext
    change (1+((-(b (loc h))) : A))*D.lift (loc h)=(t h : A)
    rw [he]
    rw [D.localCorrection_val,neg_neg,add_mul,one_mul]
    simp only [mul_assoc,Units.inv_mul,mul_one]
    abel

variable [TopologicalSpace G]
variable [TopologicalSpace H]
variable [TopologicalSpace A] [DiscreteTopology A]

theorem localCorrection_continuous (hr : Continuous D.lift)
    (loc : H →* G) (hloc : Continuous loc) (t : H →* Aˣ)
    (ht : ∀ h, D.q (t h)=D.rho (loc h)) (hc : Continuous t) :
    Continuous (D.localCorrection loc t ht) := by
  exact ((D.pullbackDatum loc).continuous_liftDifference
    (fun h => D.lift (loc h)) t (fun h => D.lift_residue (loc h)) ht
    (hr.comp hloc) hc).neg

end Komorebi.StrongArtin.SquareZeroH2.Datum
