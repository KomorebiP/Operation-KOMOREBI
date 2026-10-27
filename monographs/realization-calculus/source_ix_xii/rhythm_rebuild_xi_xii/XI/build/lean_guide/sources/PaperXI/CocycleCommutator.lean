import Mathlib.GroupTheory.QuotientGroup.Basic
import Mathlib.Tactic.Ext

/-! Paper XI, Propositions 8.1–8.2. Multiplicative notation for the abelian
index group. Values may lie in any commutative group, including ℂˣ. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.CocycleCommutator

variable {A C : Type*} [CommGroup A] [CommGroup C]

/-- The associativity identity for scalar coefficients of a twisted product.
Normalization is separate: arbitrary changes of basis need not preserve it. -/
structure Cocycle (A C : Type*) [CommGroup A] [CommGroup C] where
  coeff : A → A → C
  assoc : ∀ a b d, coeff a b * coeff (a * b) d = coeff b d * coeff a (b * d)

def Normalized (c : Cocycle A C) : Prop :=
  (∀ a, c.coeff 1 a = 1) ∧ (∀ a, c.coeff a 1 = 1)

/-- A change of scalar choices changes coefficients by this coboundary. -/
def rescale (c : Cocycle A C) (s : A → C) : Cocycle A C where
  coeff a b := s a * s b / s (a * b) * c.coeff a b
  assoc a b d := by
    calc
      _ = (s a * s b * s d / s (a * (b * d))) *
          (c.coeff a b * c.coeff (a * b) d) := by
            rw [mul_assoc a b d]
            simp [div_eq_mul_inv, mul_assoc, mul_comm, mul_left_comm]
      _ = (s a * s b * s d / s (a * (b * d))) *
          (c.coeff b d * c.coeff a (b * d)) := by rw [c.assoc]
      _ = _ := by simp [div_eq_mul_inv, mul_assoc, mul_comm, mul_left_comm]

/-- The scalar commutator. -/
def commutator (c : Cocycle A C) (a b : A) : C := c.coeff a b / c.coeff b a

@[simp] theorem commutator_self (c : Cocycle A C) (a : A) :
    commutator c a a = 1 := by simp [commutator]

theorem commutator_swap (c : Cocycle A C) (a b : A) :
    commutator c b a = (commutator c a b)⁻¹ := by simp [commutator]

theorem commutator_rescale (c : Cocycle A C) (s : A → C) (a b : A) :
    commutator (rescale c s) a b = commutator c a b := by
  simp only [commutator, rescale, mul_comm b a]
  simp [div_eq_mul_inv, mul_assoc, mul_comm, mul_left_comm]

theorem commutator_mul_left (c : Cocycle A C) (a b d : A) :
    commutator c (a * b) d = commutator c a d * commutator c b d := by
  have h₁ := c.assoc a b d
  have h₂ := c.assoc d a b
  have h₃ := c.assoc a d b
  simp only [commutator]
  rw [mul_comm d a] at h₂
  rw [mul_comm d b] at h₃
  have h₁' : c.coeff (a * b) d = c.coeff b d * c.coeff a (b * d) / c.coeff a b := by
    apply (eq_div_iff_mul_eq').2
    simpa [mul_comm] using h₁
  have h₂' : c.coeff d (a * b) = c.coeff d a * c.coeff (a * d) b / c.coeff a b := by
    apply (eq_div_iff_mul_eq').2
    simpa [mul_comm] using h₂.symm
  have h₃' : c.coeff a (b * d) = c.coeff a d * c.coeff (a * d) b / c.coeff d b := by
    apply (eq_div_iff_mul_eq').2
    simpa [mul_comm] using h₃.symm
  rw [h₁', h₂', h₃']
  simp [div_eq_mul_inv, mul_assoc, mul_comm, mul_left_comm]

theorem commutator_mul_right (c : Cocycle A C) (a b d : A) :
    commutator c a (b * d) = commutator c a b * commutator c a d := by
  rw [commutator_swap, commutator_mul_left]
  simp [commutator, div_eq_mul_inv, mul_assoc, mul_comm, mul_left_comm]

@[simp] theorem commutator_one_left (c : Cocycle A C) (a : A) :
    commutator c 1 a = 1 := by
  have h := commutator_mul_left c 1 1 a
  simpa only [one_mul, left_eq_mul] using h

@[simp] theorem commutator_one_right (c : Cocycle A C) (a : A) :
    commutator c a 1 = 1 := by rw [commutator_swap, commutator_one_left, inv_one]

/-- The commutator as a homomorphism into the character group. -/
def characterMap (c : Cocycle A C) : A →* (A →* C) where
  toFun a :=
    { toFun := commutator c a
      map_one' := commutator_one_right c a
      map_mul' := commutator_mul_right c a }
  map_one' := by ext a; exact commutator_one_left c a
  map_mul' a b := by ext d; exact commutator_mul_left c a b d

@[simp] theorem characterMap_apply (c : Cocycle A C) (a b : A) :
    characterMap c a b = commutator c a b := rfl

/-- The radical is a subgroup, defined as the kernel of the character map. -/
def radical (c : Cocycle A C) : Subgroup A := (characterMap c).ker

@[simp] theorem mem_radical_iff (c : Cocycle A C) (a : A) :
    a ∈ radical c ↔ ∀ b, commutator c a b = 1 := by
  change characterMap c a = 1 ↔ _
  constructor
  · intro h b; exact DFunLike.congr_fun h b
  · intro h; exact MonoidHom.ext h

theorem radical_rescale (c : Cocycle A C) (s : A → C) :
    radical (rescale c s) = radical c := by
  ext a
  simp only [mem_radical_iff, commutator_rescale]

/-- Rescaling preserves normalized coefficients precisely when the scalar at
identity is 1. This hypothesis is unnecessary for commutator invariance. -/
theorem normalized_rescale (c : Cocycle A C) (hc : Normalized c)
    (s : A → C) (hs : s 1 = 1) : Normalized (rescale c s) := by
  constructor <;> intro a <;> simp [rescale, hc.1, hc.2, hs]

theorem normalized_rescale_iff (c : Cocycle A C) (hc : Normalized c)
    (s : A → C) : Normalized (rescale c s) ↔ s 1 = 1 := by
  constructor
  · intro h
    have h₁ := h.1 1
    simpa [rescale, hc.1, hc.2] using h₁
  · exact normalized_rescale c hc s

end PaperXI.CocycleCommutator
