import Mathlib.RepresentationTheory.Homological.GroupCohomology.LowDegree
import Mathlib.Algebra.BigOperators.Group.Finset.Defs

/-! Constructive degree-two averaging. Bijectivity of multiplication by the
group order is verified separately in applications; it is not H² vanishing
renamed as an input. -/
namespace Komorebi.StrongArtin.FiniteCohomologyAveraging
open scoped BigOperators

variable {G M : Type} [Group G] [Fintype G] [AddCommGroup M]
variable (rho : Representation ℤ G M)

/-- Summing the two-cocycle equation produces the unnormalized primitive. -/
theorem twoCocycle_sum_identity (c : G × G → M)
    (hc : ∀ g h t, rho g (c (h,t))-c (g*h,t)+c (g,h*t)-c (g,h)=0)
    (g h : G) :
    Fintype.card G • c (g,h) =
      rho g (∑ t, c (h,t)) - (∑ t, c (g*h,t)) + ∑ t, c (g,t) := by
  have he : (∑ t : G, c (g,h*t)) = ∑ t : G, c (g,t) :=
    Fintype.sum_equiv (Equiv.mulLeft h) _ _ (fun _ => rfl)
  have hz := Finset.sum_eq_zero (s := Finset.univ) (fun t _ => hc g h t)
  simp only [Finset.sum_sub_distrib, Finset.sum_add_distrib, ← map_sum,
    Finset.sum_const, Finset.card_univ] at hz
  rw [he] at hz
  exact (sub_eq_zero.mp hz).symm

theorem exists_twoCocycle_primitive
    (hN : Function.Bijective (fun x : M => Fintype.card G • x))
    (c : G × G → M)
    (hc : ∀ g h t, rho g (c (h,t))-c (g*h,t)+c (g,h*t)-c (g,h)=0) :
    ∃ b : G → M, ∀ g h, c (g,h)=rho g (b h)-b (g*h)+b g := by
  classical
  choose b hb using fun g : G => hN.2 (∑ t, c (g,t))
  refine ⟨b, fun g h => hN.1 ?_⟩
  dsimp only at hb ⊢
  rw [twoCocycle_sum_identity rho c hc g h]
  rw [nsmul_add,nsmul_sub,← map_nsmul,hb,hb,hb]

/-- The same order hypothesis kills degree one, needed to respect a subgroup
lift after an absolute lift has been constructed. -/
theorem exists_oneCocycle_primitive
    (hN : Function.Bijective (fun x : M => Fintype.card G • x))
    (f : G → M) (hf : ∀ g h, f (g*h)=f g+rho g (f h)) :
    ∃ x : M, ∀ g, f g=rho g x-x := by
  obtain ⟨x,hx⟩ := hN.2 (-(∑ h, f h))
  refine ⟨x, fun g => hN.1 ?_⟩
  dsimp only at hx ⊢
  have he : (∑ h : G, f (g*h)) = ∑ h : G, f h :=
    Fintype.sum_equiv (Equiv.mulLeft g) _ _ (fun _ => rfl)
  have hs : (∑ h : G, f h) = Fintype.card G • f g + rho g (∑ h : G, f h) := by
    rw [← he]
    conv_lhs => arg 2; ext h; rw [hf g h]
    rw [Finset.sum_add_distrib, Finset.sum_const, Finset.card_univ,← map_sum]
    rw [he]
  rw [nsmul_sub,← map_nsmul,hx,map_neg]
  calc
    Fintype.card G • f g = (∑ h, f h)-rho g (∑ h, f h) := eq_sub_of_add_eq hs.symm
    _ = _ := by abel

end Komorebi.StrongArtin.FiniteCohomologyAveraging
