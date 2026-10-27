import PaperXI.CentralExtension
import Mathlib.Analysis.Complex.Basic

/-! The normalized central and scalar cocycles of an actual central extension.
The defect and its cocycle law are derived from group multiplication. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CentralExtension

open CocycleCommutator
variable {Z H A : Type*} [CommGroup Z] [Group H] [CommGroup A]
variable (D : Datum Z H A)

/-- The actual central coordinate of the section's multiplicative defect. -/
def defect (a b : A) : Z := coordinate D (sectionMap D a * sectionMap D b)

theorem section_mul (a b : A) :
    sectionMap D a * sectionMap D b = D.i (defect D a b) * sectionMap D (a * b) := by
  simpa only [defect, map_mul, q_section] using
    normal_form D (sectionMap D a * sectionMap D b)

@[simp] theorem defect_one_left (a : A) : defect D 1 a = 1 := by
  simp [defect]

@[simp] theorem defect_one_right (a : A) : defect D a 1 = 1 := by
  simp [defect]

theorem normal_form_mul (z w : Z) (a b : A) :
    (D.i z * sectionMap D a) * (D.i w * sectionMap D b) =
      D.i (z * w * defect D a b) * sectionMap D (a * b) := by
  calc
    _ = (D.i z * D.i w) * (sectionMap D a * sectionMap D b) := by
      rw [mul_assoc (D.i z), ← mul_assoc (sectionMap D a), ← D.central]
      simp only [mul_assoc]
    _ = _ := by rw [section_mul]; simp only [map_mul, mul_assoc]

/-- The central coordinate multiplication law, derived from the actual group. -/
theorem coordinate_mul (h k : H) :
    coordinate D (h * k) =
      coordinate D h * coordinate D k * defect D (D.q h) (D.q k) := by
  apply coordinate_eq_of_eq D (h * k) _ (D.q h * D.q k)
  calc
    h * k = (D.i (coordinate D h) * sectionMap D (D.q h)) *
        (D.i (coordinate D k) * sectionMap D (D.q k)) :=
      congrArg₂ (fun x y : H => x * y) (normal_form D h) (normal_form D k)
    _ = _ := normal_form_mul D _ _ _ _

/-- Associativity in the middle group forces the central cocycle identity. -/
theorem defect_assoc (a b d : A) :
    defect D a b * defect D (a * b) d = defect D b d * defect D a (b * d) := by
  have h := congrArg (coordinate D)
    (mul_assoc (sectionMap D a) (sectionMap D b) (sectionMap D d))
  simpa only [coordinate_mul, coordinate_section, q_section, map_mul, one_mul, mul_one] using h

/-- The actual central-valued normalized cocycle attached to the section. -/
def centralCocycle : Cocycle A Z where
  coeff := defect D
  assoc := defect_assoc D

theorem normalized_centralCocycle : Normalized (centralCocycle D) :=
  ⟨defect_one_left D, defect_one_right D⟩

/-- Apply the actual central character to the actual section defect. -/
def scalarCocycle (ζ : Z →* ℂˣ) : Cocycle A ℂˣ where
  coeff a b := ζ (defect D a b)
  assoc a b d := by
    simpa only [map_mul] using congrArg ζ (defect_assoc D a b d)

@[simp] theorem scalarCocycle_coeff (ζ : Z →* ℂˣ) (a b : A) :
    (scalarCocycle D ζ).coeff a b = ζ (defect D a b) := rfl

theorem normalized_scalarCocycle (ζ : Z →* ℂˣ) : Normalized (scalarCocycle D ζ) := by
  constructor <;> intro a <;> simp

/-- Normal-form multiplication expressed directly for two middle-group elements. -/
theorem product_normal_form (h k : H) :
    h * k = D.i (coordinate D h * coordinate D k * defect D (D.q h) (D.q k)) *
      sectionMap D (D.q h * D.q k) := by
  simpa only [map_mul, coordinate_mul] using normal_form D (h * k)

/-- The two actual lifts commute by the quotient's central defect ratio. -/
theorem lift_commutation (h k : H) :
    h * k = D.i (defect D (D.q h) (D.q k) / defect D (D.q k) (D.q h)) * (k * h) := by
  have hz : (defect D (D.q h) (D.q k) / defect D (D.q k) (D.q h)) *
      (coordinate D k * coordinate D h * defect D (D.q k) (D.q h)) =
      coordinate D h * coordinate D k * defect D (D.q h) (D.q k) := by
    simp [div_eq_mul_inv, mul_assoc, mul_comm, mul_left_comm]
  calc
    h * k = D.i (coordinate D h * coordinate D k * defect D (D.q h) (D.q k)) *
        sectionMap D (D.q h * D.q k) := product_normal_form D h k
    _ = D.i (defect D (D.q h) (D.q k) / defect D (D.q k) (D.q h)) *
        (D.i (coordinate D k * coordinate D h * defect D (D.q k) (D.q h)) *
          sectionMap D (D.q k * D.q h)) := by
      rw [← mul_assoc, ← D.i.map_mul, hz, mul_comm (D.q k) (D.q h)]
    _ = _ := congrArg
      (fun t => D.i (defect D (D.q h) (D.q k) / defect D (D.q k) (D.q h)) * t)
      (product_normal_form D k h).symm

/-- The central preimage of the commutator, with convention `[h,k]=h k h⁻¹ k⁻¹`. -/
def centralCommutator (h k : H) : Z := coordinate D (h * k * h⁻¹ * k⁻¹)

theorem centralCommutator_eq (h k : H) :
    centralCommutator D h k = defect D (D.q h) (D.q k) / defect D (D.q k) (D.q h) := by
  have heq : h * k * h⁻¹ * k⁻¹ =
      D.i (defect D (D.q h) (D.q k) / defect D (D.q k) (D.q h)) := by
    rw [lift_commutation D h k]
    group
  simp only [centralCommutator, heq, coordinate_i]

theorem i_centralCommutator (h k : H) :
    D.i (centralCommutator D h k) = h * k * h⁻¹ * k⁻¹ := by
  rw [centralCommutator_eq, lift_commutation D h k]
  group

/-- Changing either lift leaves the actual central commutator unchanged. -/
theorem centralCommutator_lift_independent (h h' k k' : H)
    (hh : D.q h = D.q h') (hk : D.q k = D.q k') :
    centralCommutator D h k = centralCommutator D h' k' := by
  simp only [centralCommutator_eq, hh, hk]

/-- The scalar bicharacter is the central character evaluated on the actual
commutator of any two lifts. -/
theorem scalar_commutator (ζ : Z →* ℂˣ) (h k : H) :
    commutator (scalarCocycle D ζ) (D.q h) (D.q k) = ζ (centralCommutator D h k) := by
  simp only [CocycleCommutator.commutator, scalarCocycle_coeff, centralCommutator_eq, map_div]

end PaperXI.CentralExtension
