import Komorebi.SufficientResolution.Compression
import Mathlib.Algebra.Field.Rat
import Mathlib.LinearAlgebra.Prod
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.IntervalCases

/-!
# Checked examples and falsification boundaries

The three-coordinate cycle agrees with its naive coarse model through depth two
and disagrees at depth three.  This is a theorem over exact rational arithmetic,
not an external floating-point experiment.
-/

set_option autoImplicit false

namespace Komorebi.SufficientResolution.Examples

abbrev FineState := ℚ × ℚ × ℚ

/-- Observe the first coordinate and initialize the other coordinates to zero. -/
def firstCoordinate : SplitCompression ℚ FineState ℚ where
  compress := LinearMap.fst ℚ ℚ (ℚ × ℚ)
  lift :=
    { toFun := fun x => (x, 0, 0)
      map_add' := by intros; ext <;> simp
      map_smul' := by intros; ext <;> simp }
  compress_lift := by apply LinearMap.ext; intro x; rfl

/-- `(y,z1,z2)` goes to `(z1,z2,y)`. -/
def rotate : FineState →ₗ[ℚ] FineState where
  toFun x := (x.2.1, x.2.2, x.1)
  map_add' := by intros; rfl
  map_smul' := by intros; rfl

 theorem rotate_cube : rotate ^ 3 = 1 := by
  apply LinearMap.ext
  intro x
  rfl

 theorem coarse_rotate : firstCoordinate.coarse rotate = 0 := by
  apply LinearMap.ext
  intro x
  rfl

 theorem coarse_rotate_sq : firstCoordinate.coarse (rotate ^ 2) = 0 := by
  apply LinearMap.ext
  intro x
  rfl

 theorem coarse_rotate_cube : firstCoordinate.coarse (rotate ^ 3) = 1 := by
  rw [rotate_cube, SplitCompression.coarse_one]

 theorem correct_through_depth_two (n : ℕ) (hn : n ≤ 2) :
    firstCoordinate.coarse (rotate ^ n) = firstCoordinate.coarse rotate ^ n := by
  interval_cases n <;> simp [coarse_rotate, coarse_rotate_sq]

 theorem fails_at_depth_three :
    firstCoordinate.coarse (rotate ^ 3) ≠ firstCoordinate.coarse rotate ^ 3 := by
  rw [coarse_rotate_cube, coarse_rotate]
  intro h
  have h₁ := LinearMap.congr_fun h (1 : ℚ)
  norm_num at h₁

 theorem delayed_return_defect : firstCoordinate.defect (rotate ^ 2) rotate = 1 := by
  change firstCoordinate.coarse (rotate ^ 2 * rotate) -
    firstCoordinate.coarse (rotate ^ 2) * firstCoordinate.coarse rotate = 1
  rw [← pow_succ, coarse_rotate_cube, coarse_rotate_sq, zero_mul, sub_zero]

/-- A redundant exact coordinate system, not a lossy state compression. -/
def duplicateCoordinates : Resolution ℚ ℚ (ℚ × ℚ) where
  analysis :=
    { toFun x := (x, x)
      map_add' := by intros; rfl
      map_smul' := by intros; rfl }
  synthesis := LinearMap.fst ℚ ℚ ℚ
  synthesis_analysis := by apply LinearMap.ext; intro x; rfl

 theorem mismatched_duplicate_not_realizable :
    ¬ ∃ x : ℚ, duplicateCoordinates.analysis x = (0, 1) := by
  rintro ⟨x, hx⟩
  have h₁ := congrArg Prod.fst hx
  have h₂ := congrArg Prod.snd hx
  change x = 0 at h₁
  change x = 1 at h₂
  exact zero_ne_one (h₁.symm.trans h₂)

end Komorebi.SufficientResolution.Examples
