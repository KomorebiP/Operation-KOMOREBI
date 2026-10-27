import RepresentationDefectTwoCocycle
import Mathlib.Tactic.Abel

/-! Changing the chosen unit lifts adds an actual group two-coboundary. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum
open Komorebi.StrongArtin.SquareZeroRepresentationDefect

variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable (D : Datum G A B)

def liftDifference (s t : G → Aˣ)
    (hs : ∀ g, D.q (s g) = D.rho g) (ht : ∀ g, D.q (t g) = D.rho g)
    (g : G) : D.Kernel :=
  ⟨((t g : A) - s g) * ↑(s g)⁻¹, by simp [hs, ht]⟩

theorem liftDifference_mul (s t : G → Aˣ)
    (hs : ∀ g, D.q (s g) = D.rho g) (ht : ∀ g, D.q (t g) = D.rho g)
    (g : G) :
    (D.liftDifference s t hs ht g : A) * s g = (t g : A) - s g := by
  simp [liftDifference, mul_assoc]

theorem lift_eq_one_add_difference (s t : G → Aˣ)
    (hs : ∀ g, D.q (s g) = D.rho g) (ht : ∀ g, D.q (t g) = D.rho g)
    (g : G) :
    (t g : A) = (1 + (D.liftDifference s t hs ht g : A)) * s g := by
  rw [add_mul, one_mul, D.liftDifference_mul]
  abel

/-- The exact coboundary transformation law in the fixed coefficient module. -/
theorem normalizedDefect_change (s t : G → Aˣ)
    (hs : ∀ g, D.q (s g) = D.rho g) (ht : ∀ g, D.q (t g) = D.rho g)
    (g h : G) :
    D.normalizedDefect t ht (g,h) = D.normalizedDefect s hs (g,h) +
      (D.action g (D.liftDifference s t hs ht h) -
        D.liftDifference s t hs ht (g*h) + D.liftDifference s t hs ht g) := by
  let b := D.liftDifference s t hs ht
  let cs := D.normalizedDefect s hs
  let ct := D.normalizedDefect t ht
  have hct : (ct (g,h) : A) * s (g*h) = defect (fun a => (t a : A)) g h := by
    calc
      (ct (g,h) : A) * s (g*h) = (ct (g,h) : A) * t (g*h) :=
        D.kernel_mul_same_residue _ (by rw [hs, ht])
      _ = _ := D.normalizedDefect_mul_lift t ht g h
  have hact : (D.action g (b h) : A) * s (g*h) = (s g : A) * (b h : A) * s h := by
    rw [D.action_eq_conjugate s hs g]
    calc
      (D.conjugate (s g) (b h) : A) * s (g*h) =
        (D.conjugate (s g) (b h) : A) * ((s g : A) * s h) :=
        D.kernel_mul_same_residue _ (by simp [hs])
      _ = _ := by simp [mul_assoc]
  have hcross : (b g : A) * (s g : A) * (b h : A) = 0 := by
    apply D.squareZero
    · have hg : D.q (b g : A) = 0 := (b g).property
      simp [hg]
    · exact (b h).property
  have hbg : (b g : A) * s (g*h) = (b g : A) * s g * s h := by
    rw [mul_assoc]
    exact D.kernel_mul_same_residue _ (by simp [hs])
  apply Subtype.ext
  change (ct (g,h) : A) = (cs (g,h) : A) +
    ((D.action g (b h) : A) - (b (g*h) : A) + (b g : A))
  have hm : (ct (g,h) : A) * s (g*h) =
      ((cs (g,h) : A) + ((D.action g (b h) : A) - (b (g*h) : A) + (b g : A))) *
        s (g*h) := by
    rw [hct, add_mul, add_mul, sub_mul, normalizedDefect_mul_lift, hact, hbg]
    change (t g : A) * t h - t (g*h) =
      ((s g : A)*s h - s (g*h)) +
        ((s g : A)*(b h : A)*s h - (b (g*h) : A)*s (g*h) + (b g : A)*s g*s h)
    rw [D.lift_eq_one_add_difference s t hs ht g,
      D.lift_eq_one_add_difference s t hs ht h,
      D.lift_eq_one_add_difference s t hs ht (g*h)]
    change (1+(b g : A))*s g*((1+(b h : A))*s h) - (1+(b (g*h) : A))*s (g*h) = _
    have hz : (b g : A) * s g * (b h : A) * s h = 0 := by rw [hcross, zero_mul]
    have hz' : (b g : A) * ((s g : A) * ((b h : A) * s h)) = 0 := by
      simpa only [mul_assoc] using hz
    noncomm_ring [hz']
  have hh := congrArg (fun z : A => z * ↑(s (g*h))⁻¹) hm
  simpa only [mul_assoc, Units.mul_inv, mul_one] using hh

/-- The obstruction is independent of every chosen unit-valued section. -/
theorem obstructionOf_eq (s t : G → Aˣ)
    (hs : ∀ g, D.q (s g) = D.rho g) (ht : ∀ g, D.q (t g) = D.rho g) :
    D.obstructionOf t ht = D.obstructionOf s hs := by
  apply (groupCohomology.H2π_eq_iff _ _).2
  refine ⟨D.liftDifference s t hs ht, ?_⟩
  funext gh
  rcases gh with ⟨g,h⟩
  change D.action g (D.liftDifference s t hs ht h) -
      D.liftDifference s t hs ht (g*h) + D.liftDifference s t hs ht g =
    D.normalizedDefect t ht (g,h) - D.normalizedDefect s hs (g,h)
  rw [D.normalizedDefect_change s t hs ht g h]
  abel

end Komorebi.StrongArtin.SquareZeroH2.Datum
