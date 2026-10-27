import PaperXI.CentralExtension
import Mathlib.LinearAlgebra.BilinearForm.Properties
import Mathlib.RingTheory.Finiteness.Cardinality
import Mathlib.Algebra.Group.TypeTags.Basic
import Mathlib.Tactic

/-! Actual Heisenberg groups on abstract bilinear spaces, their central extensions,
and center-preserving lifts of arbitrary form-preserving linear equivalences.
No choice of symplectic coordinates is used. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.AbstractHeisenberg

variable {K V : Type*} [Field K] [AddCommGroup V] [Module K V]

/-- The actual group space attached to a bilinear form. -/
@[ext]
structure Element (b : LinearMap.BilinForm K V) where
  vector : V
  central : K

variable (b : LinearMap.BilinForm K V)

instance instMul : Mul (Element b) where
  mul h k := ⟨h.vector + k.vector,
    h.central + k.central + (2 : K)⁻¹ * b h.vector k.vector⟩

instance instOne : One (Element b) where
  one := ⟨0, 0⟩

/-- The correction allows the group construction for every bilinear form.
For an alternating form the correction vanishes. -/
instance instInv : Inv (Element b) where
  inv h := ⟨-h.vector, -h.central + (2 : K)⁻¹ * b h.vector h.vector⟩

@[simp] theorem mul_vector (h k : Element b) : (h * k).vector = h.vector + k.vector := rfl
@[simp] theorem mul_central (h k : Element b) :
    (h * k).central = h.central + k.central + (2 : K)⁻¹ * b h.vector k.vector := rfl
@[simp] theorem one_vector : (1 : Element b).vector = 0 := rfl
@[simp] theorem one_central : (1 : Element b).central = 0 := rfl
@[simp] theorem inv_vector (h : Element b) : h⁻¹.vector = -h.vector := rfl
@[simp] theorem inv_central (h : Element b) :
    h⁻¹.central = -h.central + (2 : K)⁻¹ * b h.vector h.vector := rfl

instance instGroup : Group (Element b) where
  mul_assoc h k l := by
    ext <;> simp [map_add, add_assoc]
    ring
  one_mul h := by ext <;> simp
  mul_one h := by ext <;> simp
  inv_mul_cancel h := by
    ext <;> simp

/-- The group is literally a copy of the abstract vector space times the center. -/
def coordinates : Element b ≃ V × K where
  toFun h := (h.vector, h.central)
  invFun h := ⟨h.1, h.2⟩
  left_inv h := by cases h; rfl
  right_inv h := by cases h; rfl

instance instFinite [Finite V] [Finite K] : Finite (Element b) :=
  Finite.of_injective (coordinates b) (coordinates b).injective

/-- Over a finite field, a finite-dimensional abstract space gives a finite actual group. -/
theorem finite_of_finite_field [Finite K] [FiniteDimensional K V] : Finite (Element b) := by
  let : Finite V := Module.finite_of_finite K
  infer_instance

/-- The distinguished central element with scalar coordinate `z`. -/
def centralElement (z : K) : Element b := ⟨0, z⟩

@[simp] theorem centralElement_vector (z : K) : (centralElement b z).vector = 0 := rfl
@[simp] theorem centralElement_central (z : K) : (centralElement b z).central = z := rfl
@[simp] theorem centralElement_zero : centralElement b 0 = 1 := rfl
@[simp] theorem centralElement_mul (z t : K) :
    centralElement b z * centralElement b t = centralElement b (z + t) := by
  ext <;> simp

theorem centralElement_commute (z : K) (h : Element b) :
    centralElement b z * h = h * centralElement b z := by
  ext <;> simp [add_comm]

/-- The actual central inclusion, using multiplicative notation for the additive field. -/
def inclusion : Multiplicative K →* Element b where
  toFun z := centralElement b z.toAdd
  map_one' := rfl
  map_mul' z t := (centralElement_mul b z.toAdd t.toAdd).symm

/-- The actual quotient homomorphism onto the additive abstract vector space. -/
def quotient : Element b →* Multiplicative V where
  toFun h := Multiplicative.ofAdd h.vector
  map_one' := rfl
  map_mul' _ _ := rfl

@[simp] theorem inclusion_apply (z : Multiplicative K) :
    inclusion b z = centralElement b z.toAdd := rfl
@[simp] theorem quotient_apply (h : Element b) :
    quotient b h = Multiplicative.ofAdd h.vector := rfl

/-- The abstract group gives an actual central extension with all exactness proofs. -/
def datum : CentralExtension.Datum (Multiplicative K) (Element b) (Multiplicative V) where
  i := inclusion b
  q := quotient b
  i_injective := by
    intro z t h
    exact congrArg (fun h : Element b => Multiplicative.ofAdd h.central) h
  q_surjective a := ⟨⟨a.toAdd, 0⟩, rfl⟩
  range_i_eq_ker_q := by
    ext h
    constructor
    · rintro ⟨z, rfl⟩
      rfl
    · intro hh
      change h.vector = 0 at hh
      refine ⟨Multiplicative.ofAdd h.central, ?_⟩
      ext
      · exact hh.symm
      · rfl
  central z h := centralElement_commute b z.toAdd h

@[simp] theorem datum_i (z : Multiplicative K) : (datum b).i z = centralElement b z.toAdd := rfl
@[simp] theorem datum_q (h : Element b) : (datum b).q h = Multiplicative.ofAdd h.vector := rfl

/-- For an alternating form the inverse has the expected negated coordinates. -/
theorem inv_central_of_isAlt (hb : b.IsAlt) (h : Element b) :
    h⁻¹.central = -h.central := by simp [hb h.vector]

/-- The actual group commutation law has the bilinear scalar in odd characteristic. -/
theorem mul_swap (hb : b.IsAlt) (h2 : (2 : K) ≠ 0) (h k : Element b) :
    h * k = centralElement b (b h.vector k.vector) * (k * h) := by
  ext
  · simp [add_comm]
  · simp only [mul_central, centralElement_central, centralElement_vector, map_zero,
      LinearMap.zero_apply, mul_zero, add_zero]
    rw [← hb.neg_eq h.vector k.vector]
    field_simp
    ring

/-- The commutator is proved on actual abstract group elements, without a coordinate model. -/
theorem commutator (hb : b.IsAlt) (h2 : (2 : K) ≠ 0) (h k : Element b) :
    h * k * h⁻¹ * k⁻¹ = centralElement b (b h.vector k.vector) := by
  rw [mul_swap b hb h2 h k]
  group

section Lift

variable {V' : Type*} [AddCommGroup V'] [Module K V']
variable (b' : LinearMap.BilinForm K V')

/-- A form-preserving map of arbitrary abstract spaces lifts by its literal action on vectors. -/
def lift (e : V ≃ₗ[K] V') (he : ∀ v w, b' (e v) (e w) = b v w) :
    Element b ≃* Element b' where
  toFun h := ⟨e h.vector, h.central⟩
  invFun h := ⟨e.symm h.vector, h.central⟩
  left_inv h := by ext <;> simp
  right_inv h := by ext <;> simp
  map_mul' h k := by
    ext
    · exact e.map_add h.vector k.vector
    · simp only [mul_central]
      rw [he]

@[simp] theorem lift_vector (e : V ≃ₗ[K] V')
    (he : ∀ v w, b' (e v) (e w) = b v w) (h : Element b) :
    (lift b b' e he h).vector = e h.vector := rfl

@[simp] theorem lift_central (e : V ≃ₗ[K] V')
    (he : ∀ v w, b' (e v) (e w) = b v w) (h : Element b) :
    (lift b b' e he h).central = h.central := rfl

@[simp] theorem lift_inclusion (e : V ≃ₗ[K] V')
    (he : ∀ v w, b' (e v) (e w) = b v w) (z : Multiplicative K) :
    lift b b' e he ((datum b).i z) = (datum b').i z := by
  ext <;> simp [lift]

/-- The lift induces the supplied abstract linear equivalence on the actual quotients. -/
theorem lift_quotient (e : V ≃ₗ[K] V')
    (he : ∀ v w, b' (e v) (e w) = b v w) (h : Element b) :
    (datum b').q (lift b b' e he h) =
      Multiplicative.ofAdd (e ((datum b).q h).toAdd) := rfl

end Lift

end PaperXI.AbstractHeisenberg
