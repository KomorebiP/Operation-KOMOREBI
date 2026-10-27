import Mathlib.Algebra.Group.Hom.Basic
import Mathlib.Algebra.Ring.Hom.Defs
import Mathlib.Tactic.NoncommRing

/-! Exact associativity is a moving identity for representation equations.
In a square-zero extension its defects and corrections give the actual
multiplicativity lifting criterion. No cohomology comparison is assumed here. -/
namespace Komorebi.StrongArtin.SquareZeroRepresentationDefect

variable {G A B : Type*} [Group G] [Ring A] [Ring B]

/-- Multiplicativity error of an arbitrary chosen lift. -/
def defect (r : G → A) (g h : G) : A := r g * r h - r (g * h)

/-- The exact, lift-dependent associativity relation on a two-cochain. -/
def relation (r : G → A) (e : G → G → A) (g h l : G) : A :=
  r g * e h l - e (g * h) l + e g (h * l) - e g h * r l

/-- Linearized change in the multiplication equations. -/
def correction (r b : G → A) (g h : G) : A :=
  b g * r h + r g * b h - b (g * h)

/-- Perturb the chosen lifts by a kernel-valued one-cochain. -/
def perturb (r b : G → A) (g : G) : A := r g + b g

/-- Associativity gives an exact nonlinear relation, not just a tangent identity. -/
theorem associativity_identity (r : G → A) (g h l : G) :
    relation r (defect r) g h l = 0 := by
  simp only [relation, defect, mul_assoc]
  noncomm_ring

/-- The nonlinear remainder is precisely the product of the two corrections. -/
theorem defect_perturb (r b : G → A) (g h : G) :
    defect (perturb r b) g h = defect r g h + correction r b g h + b g * b h := by
  simp only [defect, perturb, correction]
  noncomm_ring

/-- The apparent failure of the linear relation to square to zero is measured
by products of the original defect and the correction. -/
theorem relation_correction (r b : G → A) (g h l : G) :
    relation r (correction r b) g h l =
      defect r g h * b l - b g * defect r h l := by
  simp only [relation, correction, defect, mul_assoc]
  noncomm_ring

/-- An actual residual representation puts every multiplicativity defect in
its square-zero extension kernel. -/
theorem defect_maps_to_zero (q : A →+* B) (rho : G →* B)
    (r : G → A) (hr : ∀ g, q (r g) = rho g) (g h : G) :
    q (defect r g h) = 0 := by
  simp [defect, hr]

/-- On kernel-valued errors, changing coefficient lifts does not change the
relation operator when the kernel is square zero. -/
theorem relation_independent_of_coefficient_lifts
    (q : A →+* B)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a * b = 0)
    (r s : G → A) (hrs : ∀ g, q (r g) = q (s g))
    (e : G → G → A) (he : ∀ g h, q (e g h) = 0) (g h l : G) :
    relation r e g h l = relation s e g h l := by
  have hleft : r g * e h l = s g * e h l := by
    have hh := hsq (r g - s g) (e h l) (by simp [hrs]) (he h l)
    simpa only [sub_mul, sub_eq_zero] using hh
  have hright : e g h * r l = e g h * s l := by
    have hh := hsq (e g h) (r l - s l) (he g h) (by simp [hrs])
    simpa only [mul_sub, sub_eq_zero] using hh
  simp only [relation, hleft, hright]

/-- The linearized correction is a compatible error on a square-zero kernel. -/
theorem correction_satisfies_relation
    (q : A →+* B) (rho : G →* B)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a * b = 0)
    (r b : G → A) (hr : ∀ g, q (r g) = rho g)
    (hb : ∀ g, q (b g) = 0) (g h l : G) :
    relation r (correction r b) g h l = 0 := by
  rw [relation_correction]
  rw [hsq _ _ (defect_maps_to_zero q rho r hr g h) (hb l),
    hsq _ _ (hb g) (defect_maps_to_zero q rho r hr h l), sub_self]

/-- In the actual square-zero lifting problem, there is no nonlinear remainder. -/
theorem defect_perturb_of_square_zero
    (q : A →+* B)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a * b = 0)
    (r b : G → A) (hb : ∀ g, q (b g) = 0) (g h : G) :
    defect (perturb r b) g h = defect r g h + correction r b g h := by
  rw [defect_perturb, hsq _ _ (hb g) (hb h), add_zero]

/-- Actual representation lifts exist exactly when the original defect can be
cancelled by a normalized kernel-valued correction. This is a lifting
criterion; it does not assert the vanishing of all such obstructions. -/
theorem representation_lift_iff_defect_correctable
    (q : A →+* B) (rho : G →* B)
    (hsq : ∀ a b, q a = 0 → q b = 0 → a * b = 0)
    (r : G → A) (hr : ∀ g, q (r g) = rho g) (hrone : r 1 = 1) :
    (∃ lift : G →* A, ∀ g, q (lift g) = rho g) ↔
      ∃ b : G → A, b 1 = 0 ∧ (∀ g, q (b g) = 0) ∧
        ∀ g h, defect r g h + correction r b g h = 0 := by
  constructor
  · rintro ⟨lift, hlift⟩
    let b : G → A := fun g => lift g - r g
    have hb : ∀ g, q (b g) = 0 := by intro g; simp [b, hlift, hr]
    refine ⟨b, by simp [b, hrone], hb, ?_⟩
    intro g h
    rw [← defect_perturb_of_square_zero q hsq r b hb g h]
    simp [defect, perturb, b]
  · rintro ⟨b, hb1, hb, heq⟩
    let lift : G →* A :=
      { toFun := perturb r b
        map_one' := by simp [perturb, hrone, hb1]
        map_mul' := by
          intro g h
          have hd : defect (perturb r b) g h = 0 := by
            rw [defect_perturb_of_square_zero q hsq r b hb g h]
            exact heq g h
          exact (sub_eq_zero.mp hd).symm }
    refine ⟨lift, ?_⟩
    intro g
    change q (r g + b g) = rho g
    rw [map_add, hr, hb, add_zero]

end Komorebi.StrongArtin.SquareZeroRepresentationDefect
