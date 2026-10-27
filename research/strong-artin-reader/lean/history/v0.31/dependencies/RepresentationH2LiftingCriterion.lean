import RepresentationObstructionChoice

/-! An obstruction in genuine Mathlib H² vanishes exactly when the original
unit-valued representation lifts. No slack equations or Selmer comparison are assumed. -/
namespace Komorebi.StrongArtin.SquareZeroH2.Datum

variable {G A B : Type} [Group G] [Ring A] [Ring B]
variable (D : Datum G A B)

/-- Every 1+x with x in a square-zero kernel is a unit, with inverse 1-x. -/
def kernelUnit (x : D.Kernel) : Aˣ where
  val := 1 + (x : A)
  inv := 1 - (x : A)
  val_inv := by
    have hx := D.kernel_mul x x
    noncomm_ring [hx]
  inv_val := by
    have hx := D.kernel_mul x x
    noncomm_ring [hx]

@[simp] theorem kernelUnit_val (x : D.Kernel) : (D.kernelUnit x : A) = 1 + (x : A) := rfl

@[simp] theorem kernelUnit_residue (x : D.Kernel) : D.q (D.kernelUnit x) = 1 := by
  have hx : D.q (x : A) = 0 := x.property
  simp [hx]

def correctedLift (b : G → D.Kernel) (g : G) : Aˣ := D.kernelUnit (b g) * D.lift g

@[simp] theorem correctedLift_val (b : G → D.Kernel) (g : G) :
    (D.correctedLift b g : A) = (1+(b g : A))*D.lift g := rfl

theorem correctedLift_residue (b : G → D.Kernel) (g : G) :
    D.q (D.correctedLift b g) = D.rho g := by
  change D.q ((D.kernelUnit (b g) : A) * D.lift g) = _
  rw [map_mul, D.kernelUnit_residue, one_mul, D.lift_residue]

theorem difference_corrected (b : G → D.Kernel) :
    D.liftDifference D.lift (D.correctedLift b) D.lift_residue
      (D.correctedLift_residue b) = b := by
  funext g
  apply Subtype.ext
  change (((1+(b g : A))*D.lift g) - D.lift g) * ↑(D.lift g)⁻¹ = (b g : A)
  rw [add_mul, one_mul, add_sub_cancel_left]
  simp [mul_assoc]

theorem normalizedDefect_corrected (b : G → D.Kernel) (g h : G) :
    D.normalizedDefect (D.correctedLift b) (D.correctedLift_residue b) (g,h) =
      D.normalizedDefect D.lift D.lift_residue (g,h) +
        (D.action g (b h) - b (g*h) + b g) := by
  rw [D.normalizedDefect_change D.lift (D.correctedLift b)
    D.lift_residue (D.correctedLift_residue b), D.difference_corrected]

theorem obstruction_zero_iff_boundary : D.obstruction = 0 ↔
    ∃ b : G → D.Kernel, ∀ g h,
      D.normalizedDefect D.lift D.lift_residue (g,h) =
        D.action g (b h) - b (g*h) + b g := by
  change groupCohomology.H2π D.coefficientRep
    (D.defectCocycle D.lift D.lift_residue) = 0 ↔ _
  rw [groupCohomology.H2π_eq_zero_iff]
  constructor
  · rintro ⟨b,hb⟩
    refine ⟨b, fun g h => ?_⟩
    exact (congrFun hb (g,h)).symm
  · rintro ⟨b,hb⟩
    refine ⟨b, ?_⟩
    funext gh
    exact (hb gh.1 gh.2).symm

/-- A specified primitive constructs a specified correcting representation. -/
def liftFromPrimitive (b : G → D.Kernel)
    (hb : ∀ g h, D.normalizedDefect D.lift D.lift_residue (g,h) =
      D.action g (b h) - b (g*h) + b g) : G →* Aˣ := by
  have hb1 : b 1 = 0 := by
    have h := hb 1 1
    rw [D.normalizedDefect_one_left D.lift D.lift_residue D.lift_one,
      map_one, Module.End.one_apply, one_mul, sub_self, zero_add] at h
    exact h.symm
  let t := D.correctedLift (-b)
  have hc : ∀ g h, D.normalizedDefect t (D.correctedLift_residue (-b)) (g,h) = 0 := by
    intro g h
    rw [D.normalizedDefect_corrected]
    simp only [Pi.neg_apply, map_neg]
    rw [hb g h]
    abel
  let lift : G →* Aˣ :=
    { toFun := t
      map_one' := by
        apply Units.ext
        change (1 + ((-b) 1 : A))*D.lift 1 = 1
        simp [hb1, D.lift_one]
      map_mul' := by
        intro g h
        apply Units.ext
        have hd := D.normalizedDefect_mul_lift t (D.correctedLift_residue (-b)) g h
        rw [hc] at hd
        change (0 : A) * t (g*h) = (t g : A)*t h-t (g*h) at hd
        have hm : (t g : A)*t h = t (g*h) := sub_eq_zero.mp (by simpa using hd.symm)
        exact hm.symm }
  exact lift

@[simp] theorem liftFromPrimitive_apply (b : G → D.Kernel)
    (hb : ∀ g h, D.normalizedDefect D.lift D.lift_residue (g,h) =
      D.action g (b h) - b (g*h) + b g) (g : G) :
    D.liftFromPrimitive b hb g = D.correctedLift (-b) g := rfl

/-- Necessity and sufficiency, for the original representation and actual kernel. -/
theorem representation_lifts_iff_obstruction_zero :
    (∃ lift : G →* Aˣ, ∀ g, D.q (lift g) = D.rho g) ↔ D.obstruction = 0 := by
  constructor
  · rintro ⟨lift,hlift⟩
    have he := D.obstructionOf_eq D.lift lift D.lift_residue hlift
    have hc : D.defectCocycle lift hlift = 0 := by
      ext g h
      apply Subtype.ext
      change ((lift g : A)*lift h - lift (g*h)) * ↑(lift (g*h))⁻¹ = 0
      simp
    change D.obstructionOf D.lift D.lift_residue = 0
    rw [← he]
    simp only [obstructionOf, hc, map_zero]
  · intro hzero
    obtain ⟨b,hb⟩ := D.obstruction_zero_iff_boundary.mp hzero
    exact ⟨D.liftFromPrimitive b hb, D.correctedLift_residue (-b)⟩

/-- H² vanishing suffices, but is not inferred from cocycle compatibility. -/
theorem representation_lifts_of_H2_subsingleton
    [Subsingleton (groupCohomology.H2 D.coefficientRep)] :
    ∃ lift : G →* Aˣ, ∀ g, D.q (lift g) = D.rho g := by
  exact D.representation_lifts_iff_obstruction_zero.mpr (Subsingleton.elim _ _)

end Komorebi.StrongArtin.SquareZeroH2.Datum
