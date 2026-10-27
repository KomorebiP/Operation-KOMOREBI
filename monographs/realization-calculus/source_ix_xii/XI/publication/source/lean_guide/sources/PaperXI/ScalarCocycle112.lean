import Mathlib.Algebra.Category.Grp.Injective
import Mathlib.Algebra.Group.TypeTags.Hom
import Mathlib.Analysis.Complex.Polynomial.Basic
import Mathlib.Tactic.Group
import Mathlib.Tactic.Ext

/-! Scalar cocycle classification for complex projective comparison.
No identification of the full finite centers or dyadic group lift is assumed. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ScalarCocycle112

variable {A C : Type*} [CommGroup A] [CommGroup C]

/-- The normalized multiplicative cocycle convention used by Paper XI. -/
structure Cocycle (A C : Type*) [CommGroup A] [CommGroup C] where
  coeff : A → A → C
  assoc : ∀ a b d, coeff a b * coeff (a * b) d = coeff b d * coeff a (b * d)
  one_left : ∀ a, coeff 1 a = 1
  one_right : ∀ a, coeff a 1 = 1

/-- Ratio of the coefficients in opposite orders. -/
def commutator (c : Cocycle A C) (a b : A) : C := c.coeff a b / c.coeff b a

/-- A separate carrier prevents accidental use of the direct-product group law. -/
structure Extension (c : Cocycle A C) where
  scalar : C
  base : A

namespace Extension
variable (c : Cocycle A C)

@[ext] theorem ext {x y : Extension c} (h₁ : x.scalar = y.scalar) (h₂ : x.base = y.base) :
    x = y := by cases x; cases y; cases h₁; cases h₂; rfl

instance : Mul (Extension c) := ⟨fun x y =>
  ⟨x.scalar * y.scalar * c.coeff x.base y.base, x.base * y.base⟩⟩
instance : One (Extension c) := ⟨⟨1, 1⟩⟩
instance : Inv (Extension c) := ⟨fun x =>
  ⟨x.scalar⁻¹ / c.coeff x.base⁻¹ x.base, x.base⁻¹⟩⟩

@[simp] theorem mul_scalar (x y : Extension c) :
    (x * y).scalar = x.scalar * y.scalar * c.coeff x.base y.base := rfl
@[simp] theorem mul_base (x y : Extension c) : (x * y).base = x.base * y.base := rfl
@[simp] theorem one_scalar : (1 : Extension c).scalar = 1 := rfl
@[simp] theorem one_base : (1 : Extension c).base = 1 := rfl

instance : Group (Extension c) where
  mul_assoc x y z := by
    apply ext
    · change (x.scalar * y.scalar * c.coeff x.base y.base) * z.scalar *
        c.coeff (x.base * y.base) z.base = x.scalar *
        (y.scalar * z.scalar * c.coeff y.base z.base) * c.coeff x.base (y.base * z.base)
      calc
        _ = (x.scalar * y.scalar * z.scalar) *
          (c.coeff x.base y.base * c.coeff (x.base * y.base) z.base) := by ac_rfl
        _ = _ := by rw [c.assoc]; ac_rfl
    · exact mul_assoc _ _ _
  one_mul x := by ext <;> simp [c.one_left]
  mul_one x := by ext <;> simp [c.one_right]
  inv_mul_cancel x := by
    apply ext
    · change (x.scalar⁻¹ / c.coeff x.base⁻¹ x.base) * x.scalar *
        c.coeff x.base⁻¹ x.base = 1
      simp [div_eq_mul_inv, mul_comm]
    · exact inv_mul_cancel _

/-- The twisted extension is abelian exactly where symmetric coefficients are used. -/
@[instance_reducible] def commGroup (hsym : ∀ a b, c.coeff a b = c.coeff b a) : CommGroup (Extension c) :=
  { (inferInstance : Group (Extension c)) with
    mul_comm := fun x y => by
      apply ext
      · simp only [mul_scalar, hsym x.base y.base]
        ac_rfl
      · exact mul_comm _ _ }

/-- Inclusion of the scalar subgroup. -/
def scalarInclusion : C →* Extension c where
  toFun z := ⟨z, 1⟩
  map_one' := rfl
  map_mul' z w := by ext <;> simp [c.one_left]

@[simp] theorem scalarInclusion_scalar (z : C) :
    (scalarInclusion c z).scalar = z := rfl
@[simp] theorem scalarInclusion_base (z : C) :
    (scalarInclusion c z).base = 1 := rfl

theorem scalarInclusion_injective : Function.Injective (scalarInclusion c) :=
  fun _ _ h => congrArg Extension.scalar h

/-- The fixed normalized set-theoretic section. -/
def sectionOf (a : A) : Extension c := ⟨1, a⟩

@[simp] theorem sectionOf_one : sectionOf c 1 = 1 := rfl

theorem sectionOf_mul (a b : A) :
    sectionOf c a * sectionOf c b = scalarInclusion c (c.coeff a b) * sectionOf c (a * b) := by
  ext <;> simp [sectionOf, c.one_left]

end Extension

/-- Divisible scalar coefficients split every symmetric normalized cocycle.
The cochain is constructed from a retraction of the scalar subgroup. -/
theorem symmetric_exists_cochain [DivisibleBy (Additive C) ℤ]
    (c : Cocycle A C) (hsym : ∀ a b, c.coeff a b = c.coeff b a) :
    ∃ s : A → C, s 1 = 1 ∧ ∀ a b, c.coeff a b = s a * s b / s (a * b) := by
  let : CommGroup (Extension c) := Extension.commGroup c hsym
  obtain ⟨r, hr⟩ := (Module.Baer.of_divisible (Additive C)).extension_property_addMonoidHom
    (Extension.scalarInclusion c).toAdditive
    (fun x y h => Extension.scalarInclusion_injective c h)
    (AddMonoidHom.id (Additive C))
  let R : Extension c →* C := MonoidHom.toAdditive.symm r
  have hR (z : C) : R (Extension.scalarInclusion c z) = z := by
    exact DFunLike.congr_fun hr (Additive.ofMul z)
  refine ⟨fun a => R (Extension.sectionOf c a), ?_, ?_⟩
  · exact R.map_one
  · intro a b
    have hm := congrArg R (Extension.sectionOf_mul c a b)
    rw [map_mul, map_mul, hR] at hm
    exact (eq_div_iff_mul_eq').mpr hm.symm

/-- The pointwise ratio of normalized cocycles. -/
def ratio (c d : Cocycle A C) : Cocycle A C where
  coeff a b := c.coeff a b / d.coeff a b
  assoc a b e := by
    simp only [div_mul_div_comm, c.assoc, d.assoc]
  one_left a := by simp [c.one_left, d.one_left]
  one_right a := by simp [c.one_right, d.one_right]

/-- Equality of scalar commutators makes the ratio cocycle symmetric. -/
theorem ratio_symmetric (c d : Cocycle A C)
    (h : ∀ a b, commutator c a b = commutator d a b) :
    ∀ a b, (ratio c d).coeff a b = (ratio c d).coeff b a := by
  intro a b
  apply (div_eq_div_iff_mul_eq_mul).mpr
  have hab := (div_eq_div_iff_mul_eq_mul).mp (h a b)
  simpa only [mul_comm] using hab

/-- Equal commutators imply a normalized scalar change of basis over every
coefficient group whose additive type tag is divisible. -/
theorem same_commutator_exists_cochain_of_divisible [DivisibleBy (Additive C) ℤ]
    (c d : Cocycle A C) (h : ∀ a b, commutator c a b = commutator d a b) :
    ∃ s : A → C, s 1 = 1 ∧
      ∀ a b, c.coeff a b = (s a * s b / s (a * b)) * d.coeff a b := by
  obtain ⟨s, hs, he⟩ := symmetric_exists_cochain (ratio c d) (ratio_symmetric c d h)
  refine ⟨s, hs, fun a b => ?_⟩
  exact (div_eq_iff_eq_mul).mp (he a b)

/-- Nonzero complex numbers have roots of every positive order. -/
theorem complex_units_exists_pow (z : ℂˣ) {n : ℕ} (hn : n ≠ 0) :
    ∃ w : ℂˣ, w ^ n = z := by
  obtain ⟨w, hw⟩ := IsAlgClosed.exists_pow_nat_eq (z : ℂ) (Nat.pos_of_ne_zero hn)
  have hw0 : w ≠ 0 := by
    intro h0
    rw [h0, zero_pow hn] at hw
    exact z.ne_zero hw.symm
  refine ⟨Units.mk0 w hw0, ?_⟩
  apply Units.ext
  exact hw

/-- Divisibility of complex scalar coefficients, proved from algebraic closure. -/
@[instance_reducible] def complexUnitsDivisible : DivisibleBy (Additive ℂˣ) ℤ := by
  let : DivisibleBy (Additive ℂˣ) ℕ := divisibleByOfSMulRightSurj _ _ (by
    intro n hn z
    obtain ⟨w, hw⟩ := complex_units_exists_pow z hn
    exact ⟨Additive.ofMul w, hw⟩)
  exact AddGroup.divisibleByIntOfDivisibleByNat _

/-- Complex normalized scalar cocycles with equal commutators are cohomologous.
The normalized cochain is a conclusion, not a supplied input. -/
theorem same_commutator_exists_cochain
    (c d : Cocycle A ℂˣ) (h : ∀ a b, commutator c a b = commutator d a b) :
    ∃ s : A → ℂˣ, s 1 = 1 ∧
      ∀ a b, c.coeff a b = (s a * s b / s (a * b)) * d.coeff a b := by
  let : DivisibleBy (Additive ℂˣ) ℤ := complexUnitsDivisible
  exact same_commutator_exists_cochain_of_divisible c d h

/-- Raw-function adapter for Paper XI's original `Cocycle` with normalization
stored separately: pass its coefficient and associativity fields and the two
normalization components. -/
theorem same_commutator_exists_cochain_raw
    (c d : A → A → ℂˣ)
    (hc : ∀ a b e, c a b * c (a * b) e = c b e * c a (b * e))
    (hd : ∀ a b e, d a b * d (a * b) e = d b e * d a (b * e))
    (hc₁ : ∀ a, c 1 a = 1) (hc₂ : ∀ a, c a 1 = 1)
    (hd₁ : ∀ a, d 1 a = 1) (hd₂ : ∀ a, d a 1 = 1)
    (h : ∀ a b, c a b / c b a = d a b / d b a) :
    ∃ s : A → ℂˣ, s 1 = 1 ∧ ∀ a b, c a b = (s a * s b / s (a * b)) * d a b :=
  same_commutator_exists_cochain ⟨c, hc, hc₁, hc₂⟩ ⟨d, hd, hd₁, hd₂⟩ h

#print axioms symmetric_exists_cochain
#print axioms same_commutator_exists_cochain
#print axioms same_commutator_exists_cochain_raw

end PaperXI.ScalarCocycle112
