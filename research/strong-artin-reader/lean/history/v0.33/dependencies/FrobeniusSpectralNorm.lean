import FrobeniusSingleRestriction
import Mathlib.Algebra.Field.GeomSum
import Mathlib.Algebra.CharP.Lemmas

/-! Exact norm image in a supplied diagonalization of the ACTUAL square-zero
kernel action. Diagonalizability is a substantive hypothesis, not inferred from
residual finite image or from a list of eigenvalues. -/
namespace Komorebi.StrongArtin.SquareZeroH2
open scoped BigOperators

variable {G A B k I : Type} [Group G] [Ring A] [Ring B] [Field k]

/-- Concrete coordinates for conjugation on the actual coefficient kernel. -/
structure FrobeniusSpectralCoordinates (D : Datum G A B) (F : Aˣ) (k I : Type)
    [Field k] where
  coordinates : D.Kernel ≃+ (I → k)
  eigenvalue : I → k
  conjugate_coordinates : ∀ x i,
    coordinates (D.conjugate F x) i = eigenvalue i * coordinates x i

/-- The scalar multiplier of a degree-d Frobenius restriction. -/
def normWeight (a : k) (d : ℕ) : k := ∑ j ∈ Finset.range d, a^j

@[simp] theorem normWeight_one (d : ℕ) : normWeight (1 : k) d = (d : k) := by
  simp [normWeight]

theorem normWeight_of_ne_one (a : k) (h : a ≠ 1) (d : ℕ) :
    normWeight a d = (a^d - 1) / (a-1) := by
  exact geom_sum_eq h d

/-- The two distinct resonance mechanisms: degree torsion and root collision. -/
theorem normWeight_zero_iff (a : k) (d : ℕ) :
    normWeight a d = 0 ↔
      (a = 1 ∧ (d : k) = 0) ∨ (a ≠ 1 ∧ a^d = 1) := by
  by_cases h : a = 1
  · subst a
    simp
  · rw [normWeight_of_ne_one a h d]
    simp [div_eq_zero_iff, sub_eq_zero, h]

namespace FrobeniusSpectralCoordinates
variable {D : Datum G A B} {F : Aˣ}
variable (S : FrobeniusSpectralCoordinates D F k I)

theorem conjugate_pow_coordinates (n : ℕ) (x : D.Kernel) (i : I) :
    S.coordinates (D.conjugate (F^n) x) i = S.eigenvalue i ^ n * S.coordinates x i := by
  induction n with
  | zero => simp
  | succ n ih =>
    rw [pow_succ', D.conjugate_mul]
    change S.coordinates (D.conjugate F (D.conjugate (F^n) x)) i = _
    rw [S.conjugate_coordinates, ih, pow_succ', mul_assoc]

theorem norm_coordinates (d : ℕ) (x : D.Kernel) (i : I) :
    S.coordinates (D.frobeniusNorm F d x) i =
      normWeight (S.eigenvalue i) d * S.coordinates x i := by
  induction d with
  | zero => simp [normWeight]
  | succ d ih =>
    rw [D.frobeniusNorm_succ, map_add]
    change S.coordinates (D.frobeniusNorm F d x) i +
      S.coordinates (D.conjugate (F^d) x) i = _
    rw [ih, S.conjugate_pow_coordinates]
    simp only [normWeight, Finset.sum_range_succ, add_mul]

/-- Explicit correction: divide on each nonresonant coordinate. -/
theorem norm_image_iff (d : ℕ) (e : D.Kernel) :
    (∃ x, D.frobeniusNorm F d x = e) ↔
    ∀ i, normWeight (S.eigenvalue i) d = 0 → S.coordinates e i = 0 := by
  constructor
  · rintro ⟨x, rfl⟩ i hi
    rw [S.norm_coordinates, hi, zero_mul]
  · intro he
    let x := S.coordinates.symm (fun i => S.coordinates e i / normWeight (S.eigenvalue i) d)
    refine ⟨x, S.coordinates.injective ?_⟩
    funext i
    rw [S.norm_coordinates]
    have hx : S.coordinates x i = S.coordinates e i / normWeight (S.eigenvalue i) d :=
      congrFun (S.coordinates.apply_symm_apply _) i
    rw [hx]
    by_cases hi : normWeight (S.eigenvalue i) d = 0
    · rw [hi, zero_mul, he i hi]
    · exact mul_div_cancel₀ _ hi

/-- Necessary and sufficient spectral criterion for an actual prescribed root. -/
theorem prescribed_power_iff (V : Aˣ) (d : ℕ) (hV : D.q V = D.q (F^d)) :
    (∃ F' : Aˣ, D.q F' = D.q F ∧ F'^d = V) ↔
    ∀ i, normWeight (S.eigenvalue i) d = 0 →
      S.coordinates (D.unitMismatch V (F^d) hV) i = 0 := by
  rw [D.power_lifting_iff_norm_image, S.norm_image_iff]

/-- No spectral resonance implies every compatible prescribed Frobenius power lifts. -/
theorem prescribed_power_lifts_of_nonresonance (d : ℕ)
    (h : ∀ i, normWeight (S.eigenvalue i) d ≠ 0)
    (V : Aˣ) (hV : D.q V = D.q (F^d)) :
    ∃ F' : Aˣ, D.q F' = D.q F ∧ F'^d = V := by
  apply (S.prescribed_power_iff V d hV).mpr
  intro i hi
  exact (h i hi).elim

/-- A nonzero mismatch in any resonant coordinate is a rigorous obstruction. -/
theorem no_prescribed_power_of_resonant_mismatch (V : Aˣ) (d : ℕ)
    (hV : D.q V = D.q (F^d)) (i : I)
    (hi : normWeight (S.eigenvalue i) d = 0)
    (he : S.coordinates (D.unitMismatch V (F^d) hV) i ≠ 0) :
    ¬ ∃ F' : Aˣ, D.q F' = D.q F ∧ F'^d = V := by
  intro h
  exact he ((S.prescribed_power_iff V d hV).mp h i hi)

end FrobeniusSpectralCoordinates
end Komorebi.StrongArtin.SquareZeroH2
