import PaperX.WeilSpecialChain
import Mathlib.GroupTheory.SemidirectProduct
import Mathlib.Tactic.NormNum

/-! A nonzero twisted cocycle on the actual affine group. This is an algebraic
model, with no asserted identification with an arithmetic Weil group. -/
set_option autoImplicit false
noncomputable section
namespace PaperX.AffineMonodromy
open PaperX.WeilData PaperX.WeilSpecialChain PaperX.SpecialMonodromy

variable (K : Type*) [Field K]

def scaleAut (a : Kˣ) : MulAut (Multiplicative K) where
  toFun x := Multiplicative.ofAdd ((a : K) * x.toAdd)
  invFun x := Multiplicative.ofAdd ((a⁻¹ : Kˣ) * x.toAdd)
  left_inv x := by simp
  right_inv x := by simp
  map_mul' x y := by
    change Multiplicative.ofAdd ((a : K) * (x.toAdd + y.toAdd)) = _
    simp [mul_add]

def scaling : Kˣ →* MulAut (Multiplicative K) where
  toFun := scaleAut K
  map_one' := by ext x; simp [scaleAut]
  map_mul' a b := by ext x; simp [scaleAut, mul_assoc]

abbrev Affine := Multiplicative K ⋊[scaling K] Kˣ

def norm : Affine K →* Kˣ := SemidirectProduct.rightHom
def coordinate (g : Affine K) : K := g.left.toAdd

theorem coordinate_one : coordinate K 1 = 0 := rfl

theorem coordinate_mul (g h : Affine K) :
    coordinate K (g * h) = coordinate K g + (norm K g : K) * coordinate K h := rfl

def translation (a : K) : Affine K := ⟨Multiplicative.ofAdd a, 1⟩
def dilation (a : Kˣ) : Affine K := ⟨1, a⟩

theorem translation_coordinate (a : K) : coordinate K (translation K a) = a := rfl
theorem dilation_coordinate (a : Kˣ) : coordinate K (dilation K a) = 0 := rfl
theorem translation_norm (a : K) : norm K (translation K a) = 1 := rfl
theorem dilation_norm (a : Kˣ) : norm K (dilation K a) = a := rfl

def chain (n : ℕ) : Datum (norm K) (Fin n → K) := chainDatum (norm K) 1 n

abbrev G := Affine ℚ
def ν : G →* ℚˣ := norm ℚ
def t : G → ℚ := coordinate ℚ
def u : G := translation ℚ 1
def d : G := dilation ℚ (Units.mk0 (1/3) (by norm_num))
def datum3 : Datum ν (Fin 3 → ℚ) := chain ℚ 3

theorem cocycle_identity (g h : G) : t (g * h) = t g + (ν g : ℚ) * t h := rfl
theorem translation_value : t u = 1 ∧ ν u = 1 := ⟨rfl, rfl⟩
theorem dilation_value : t d = 0 ∧ (ν d : ℚ) = 1/3 := ⟨rfl, rfl⟩

theorem product_values : t (d * u) = 1/3 ∧ t (u * d) = 1 := by
  constructor <;> norm_num [cocycle_identity, translation_value.1,
    translation_value.2, dilation_value.1, dilation_value.2]

theorem noncommuting_elements : d * u ≠ u * d := by
  intro h
  have ht := congrArg t h
  rw [product_values.1, product_values.2] at ht
  norm_num at ht

theorem nonzero_monodromy : datum3.N ^ 2 ≠ 0 ∧ datum3.N ^ 3 = 0 :=
  ⟨shift_previous_power_nonzero 3 (by decide), shift_nilpotent 3⟩

theorem translation_action : datum3.r u = 1 := by
  apply LinearMap.ext
  intro x
  funext j
  simp [datum3, chain, chainDatum, chainRep, diagonalF, ν, norm, u, translation,
    SemidirectProduct.rightHom]

theorem dilation_action (x : Fin 3 → ℚ) (j : Fin 3) :
    datum3.r d x j = 3 ^ j.val * x j := by
  simp [datum3, chain, chainDatum, chainRep, diagonalF, ν, norm, d, dilation,
    SemidirectProduct.rightHom]


end PaperX.AffineMonodromy
