import PaperXI.HenselianFieldLift

/-! Residue embedding of an actual restricted valuation ring. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.ValuationResidueEmbedding
open IsLocalRing
variable {F L : Type*} [Field F] [Field L]
variable (A : ValuationSubring L) (f : F →+* L)
def inclusion : A.comap f →+* A where
  toFun x := ⟨f x.val, x.property⟩
  map_one' := Subtype.ext (map_one f)
  map_zero' := Subtype.ext (map_zero f)
  map_add' x y := Subtype.ext (map_add f x.val y.val)
  map_mul' x y := Subtype.ext (map_mul f x.val y.val)
@[simp] theorem inclusion_val (x : A.comap f) :
    (inclusion A f x : L) = f x.val := rfl
instance inclusion_local : IsLocalHom (inclusion A f) where
  map_nonunit x hx := by
    obtain ⟨y, hy⟩ := isUnit_iff_exists_inv.mp hx
    have hp : f (x : F) * (y : L) = 1 := congrArg (fun z : A => (z : L)) hy
    have hx0 : (x : F) ≠ 0 := by
      intro h; simp [h] at hp
    have hf0 : f (x : F) ≠ 0 := (map_ne_zero f).mpr hx0
    have hyv : (y : L) = (f (x : F))⁻¹ := by
      apply mul_left_cancel₀ hf0
      rw [hp, mul_inv_cancel₀ hf0]
    refine isUnit_iff_exists_inv.mpr ⟨⟨(x : F)⁻¹, ?_⟩, ?_⟩
    · change f ((x : F)⁻¹) ∈ A
      rw [map_inv₀, ← hyv]
      exact y.property
    · exact Subtype.ext (mul_inv_cancel₀ hx0)
def residueMap : ResidueField (A.comap f) →+* ResidueField A :=
  ResidueField.map (inclusion A f)
@[simp] theorem residueMap_residue (x : A.comap f) :
    residueMap A f (residue (A.comap f) x) = residue A (inclusion A f x) := rfl
theorem residueMap_injective : Function.Injective (residueMap A f) :=
  (residueMap A f).injective
theorem mem_range_iff (z : ResidueField A) :
    z ∈ Set.range (residueMap A f) ↔
      ∃ x : F, ∃ hx : f x ∈ A, residue A ⟨f x, hx⟩ = z := by
  constructor
  · rintro ⟨a, ha⟩
    obtain ⟨x, rfl⟩ := residue_surjective a
    exact ⟨x.val, x.property, ha⟩
  · rintro ⟨x, hx, h⟩
    exact ⟨residue (A.comap f) ⟨x, hx⟩, h⟩
end PaperXI.ValuationResidueEmbedding
