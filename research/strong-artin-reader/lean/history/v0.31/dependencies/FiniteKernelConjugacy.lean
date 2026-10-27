import FiniteQuotientObstructionVanishing
import LocalLiftMismatch

/-! Constructive H1 rigidity across a square-zero coefficient extension.
Two lifts of the same finite-group representation are conjugate by 1+kernel
when the finite-group order is a unit. This is not simultaneous strict gluing. -/
namespace Komorebi.StrongArtin.SquareZeroH2

variable {G A B : Type} [Group G] [Ring A] [Ring B]

namespace Datum
variable (D : Datum G A B)

theorem kernelUnit_conjugation (u : Aˣ) (x : D.Kernel) :
    D.kernelUnit (-x)*u*(D.kernelUnit (-x))⁻¹=
      D.kernelUnit (D.conjugate u x-x)*u := by
  apply Units.ext
  change (1+(-(x : A)))*(u : A)*(1-(-(x : A)))=
    (1+((u : A)*(x : A)*↑u⁻¹-(x : A)))*(u : A)
  have hc : (x : A)*((u : A)*(x : A))=0 := by
    apply D.squareZero _ _ x.property
    have hx : D.q (x : A)=0 := x.property
    simp [hx]
  simp only [sub_neg_eq_add,add_mul,one_mul,sub_mul,mul_assoc,Units.inv_mul,mul_one]
  noncomm_ring [hc]

end Datum

/-- Construct a strict kernel conjugator, not merely an equivalence of classes. -/
theorem same_residue_representations_kernel_conjugate [Fintype G]
    (q : A →+* B) (hsq : ∀ a b, q a=0 → q b=0 → a*b=0)
    (r t : G →* Aˣ) (ht : ∀ g, q (t g)=q (r g))
    (hn : IsUnit (Fintype.card G : A)) :
    ∃ u : Aˣ, q u=1 ∧ ∀ g, t g=u*r g*u⁻¹ := by
  let D : Datum G A B :=
    { q := q, squareZero := hsq,
      rho := q.toMonoidHom.comp ((Units.coeHom A).comp r),
      lift := r, lift_one := r.map_one, lift_residue := fun _ => rfl }
  let f : G → D.Kernel := D.liftDifference r t D.lift_residue ht
  have hc (s : G →* Aˣ) (hs : ∀ g, D.q (s g)=D.rho g) (g h : G) :
      D.normalizedDefect s hs (g,h)=0 := by
    apply Subtype.ext
    change ((s g : A)*s h-s (g*h))*↑(s (g*h))⁻¹=0
    simp
  have hf : ∀ g h, f (g*h)=f g+D.action g (f h) := by
    intro g h
    have he := D.normalizedDefect_change r t D.lift_residue ht g h
    rw [hc t ht,hc r D.lift_residue,zero_add] at he
    change 0=D.action g (f h)-f (g*h)+f g at he
    have hz : f g+D.action g (f h)-f (g*h)=0 := by
      calc
        _ = D.action g (f h)-f (g*h)+f g := by abel
        _ = 0 := he.symm
    exact (sub_eq_zero.mp hz).symm
  obtain ⟨x,hx⟩ := FiniteCohomologyAveraging.exists_oneCocycle_primitive
    D.action (D.kernel_nsmul_bijective_of_isUnit _ hn) f hf
  refine ⟨D.kernelUnit (-x),D.kernelUnit_residue _,fun g => ?_⟩
  rw [D.kernelUnit_conjugation]
  apply Units.ext
  have he := D.lift_eq_one_add_difference r t D.lift_residue ht g
  change (t g : A)=(1+((D.conjugate (r g) x-x : D.Kernel) : A))*(r g : A)
  change (t g : A)=(1+(f g : A))*(r g : A) at he
  rw [hx] at he
  exact he

end Komorebi.StrongArtin.SquareZeroH2
