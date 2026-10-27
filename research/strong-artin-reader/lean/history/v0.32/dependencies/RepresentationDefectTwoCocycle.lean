import SquareZeroKernelAction
import SquareZeroRepresentationDefect
import Mathlib.RepresentationTheory.Homological.GroupCohomology.LowDegree

/-! Normalize the genuine multiplication error into Mathlib's inhomogeneous H².
All coefficient operations take place in the actual square-zero ring kernel. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum
open Komorebi.StrongArtin.SquareZeroRepresentationDefect

variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable (D : Datum G A B)

/-- The normalized multiplicativity error of any unit-valued section of rho. -/
def normalizedDefect (s : G → Aˣ) (hs : ∀ g, D.q (s g) = D.rho g)
    (gh : G × G) : D.Kernel :=
  ⟨defect (fun g => (s g : A)) gh.1 gh.2 * ↑(s (gh.1 * gh.2))⁻¹,
    by simp [defect, hs]⟩

@[simp] theorem normalizedDefect_val (s : G → Aˣ)
    (hs : ∀ g, D.q (s g) = D.rho g) (g h : G) :
    (D.normalizedDefect s hs (g,h) : A) =
      ((s g : A) * s h - s (g*h)) * ↑(s (g*h))⁻¹ := rfl

theorem normalizedDefect_mul_lift (s : G → Aˣ)
    (hs : ∀ g, D.q (s g) = D.rho g) (g h : G) :
    (D.normalizedDefect s hs (g,h) : A) * s (g*h) =
      defect (fun t => (s t : A)) g h := by
  simp [normalizedDefect, mul_assoc]

theorem normalizedDefect_one_left (s : G → Aˣ)
    (hs : ∀ g, D.q (s g) = D.rho g) (hs1 : s 1 = 1) (g : G) :
    D.normalizedDefect s hs (1,g) = 0 := by
  apply Subtype.ext
  simp [normalizedDefect, defect, hs1]

theorem normalizedDefect_one_right (s : G → Aˣ)
    (hs : ∀ g, D.q (s g) = D.rho g) (hs1 : s 1 = 1) (g : G) :
    D.normalizedDefect s hs (g,1) = 0 := by
  apply Subtype.ext
  simp [normalizedDefect, defect, hs1]

/-- Associativity becomes the actual inhomogeneous two-cocycle identity. -/
theorem normalizedDefect_cocycle (s : G → Aˣ)
    (hs : ∀ g, D.q (s g) = D.rho g) (g h l : G) :
    D.action g (D.normalizedDefect s hs (h,l)) -
      D.normalizedDefect s hs (g*h,l) + D.normalizedDefect s hs (g,h*l) -
      D.normalizedDefect s hs (g,h) = 0 := by
  let c := D.normalizedDefect s hs
  have ha : (D.action g (c (h,l)) : A) * s (g*(h*l)) =
      (s g : A) * defect (fun t => (s t : A)) h l := by
    rw [D.action_eq_conjugate s hs g]
    calc
      (D.conjugate (s g) (c (h,l)) : A) * s (g*(h*l)) =
          (D.conjugate (s g) (c (h,l)) : A) * ((s g : A) * s (h*l)) :=
        D.kernel_mul_same_residue _ (by simp [hs])
      _ = (s g : A) * ((c (h,l) : A) * s (h*l)) := by
        simp [mul_assoc]
      _ = _ := by rw [normalizedDefect_mul_lift]
  have hb : (c (g,h) : A) * s ((g*h)*l) =
      defect (fun t => (s t : A)) g h * s l := by
    calc
      (c (g,h) : A) * s ((g*h)*l) = (c (g,h) : A) * ((s (g*h) : A)*s l) :=
        D.kernel_mul_same_residue _ (by simp [hs])
      _ = _ := by rw [← mul_assoc, normalizedDefect_mul_lift]
  apply Subtype.ext
  change (D.action g (c (h,l)) : A) - (c (g*h,l) : A) +
    (c (g,h*l) : A) - (c (g,h) : A) = 0
  have hz : ((D.action g (c (h,l)) : A) - (c (g*h,l) : A) +
      (c (g,h*l) : A) - (c (g,h) : A)) * s (g*(h*l)) = 0 := by
    rw [sub_mul, add_mul, sub_mul, ha]
    rw [← mul_assoc g h l, normalizedDefect_mul_lift, hb]
    rw [mul_assoc g h l, normalizedDefect_mul_lift]
    exact associativity_identity (fun t => (s t : A)) g h l
  have hh := congrArg (fun z : A => z * ↑(s (g*(h*l)))⁻¹) hz
  simpa only [mul_assoc, Units.mul_inv, mul_one, zero_mul] using hh

/-- A cocycle in Mathlib's genuine low-degree group-cohomology complex. -/
def defectCocycle (s : G → Aˣ) (hs : ∀ g, D.q (s g) = D.rho g) :
    groupCohomology.cocycles₂ D.coefficientRep :=
  ⟨D.normalizedDefect s hs, (groupCohomology.mem_cocycles₂_def _).2
    (D.normalizedDefect_cocycle s hs)⟩

noncomputable def obstructionOf (s : G → Aˣ)
    (hs : ∀ g, D.q (s g) = D.rho g) : groupCohomology.H2 D.coefficientRep :=
  groupCohomology.H2π D.coefficientRep (D.defectCocycle s hs)

noncomputable def obstruction : groupCohomology.H2 D.coefficientRep :=
  D.obstructionOf D.lift D.lift_residue

end Komorebi.StrongArtin.SquareZeroH2.Datum
