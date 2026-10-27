import PaperXI.SmithMatrix106
import PaperXI.SplitRadical105
import Mathlib.RingTheory.Localization.FractionRing
import Mathlib.RingTheory.Localization.Integer

/-! Clear denominators and retain both integral basis changes. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.FractionMatrix106
open Matrix
open scoped nonZeroDivisors
variable {ι R F : Type*} [Fintype ι] [DecidableEq ι]
  [CommRing R] [IsDomain R] [IsPrincipalIdealRing R]
  [Field F] [Algebra R F] [IsFractionRing R F]

omit [IsPrincipalIdealRing R] in
theorem exists_integral_multiple (g : GL ι F) :
    ∃ b : R, ∃ A : Matrix ι ι R,
      b ≠ 0 ∧ A.det ≠ 0 ∧ A.map (algebraMap R F) = (algebraMap R F b) • g.val := by
  obtain ⟨b, hb⟩ := IsLocalization.exist_integer_multiples_of_finite
    (R⁰) (fun ij : ι × ι => g ij.1 ij.2)
  choose A hA using hb
  have hb0 : (b : R) ≠ 0 := nonZeroDivisors.ne_zero b.property
  have hbF : algebraMap R F (b : R) ≠ 0 := fun h => hb0 ((IsFractionRing.injective R F) (h.trans (map_zero _).symm))
  let M : Matrix ι ι R := fun i j => A (i, j)
  have hm : M.map (algebraMap R F) = (algebraMap R F (b : R)) • g.val := by
    ext i j
    change algebraMap R F (A (i, j)) = algebraMap R F (b : R) * g i j
    simpa only [Algebra.smul_def] using hA (i, j)
  have hdet : M.det ≠ 0 := by
    intro h
    have he := congrArg Matrix.det hm
    change (RingHom.mapMatrix (algebraMap R F) M).det = _ at he
    rw [← RingHom.map_det, h, map_zero, Matrix.det_smul] at he
    exact (mul_ne_zero (pow_ne_zero _ hbF) g.det_ne_zero) he.symm
  exact ⟨b, M, hb0, hdet, hm⟩

theorem exists_integral_diagonal (g : GL ι F) :
    ∃ c : Fˣ, ∃ P Q : GL ι R, ∃ d : ι → R, ∃ hd : ∀ i, algebraMap R F (d i) ≠ 0,
      g = GeneralLinearGroup.scalar ι c *
        (GeneralLinearGroup.map (algebraMap R F) P *
          SplitRadical105.diagonalGL (fun i => algebraMap R F (d i)) hd *
          GeneralLinearGroup.map (algebraMap R F) Q) := by
  obtain ⟨b, A, hb, hA, he⟩ := exists_integral_multiple (R := R) g
  obtain ⟨P, Q, d, hd, hdiag⟩ := SmithMatrix106.exists_diagonal A hA
  have hbF : algebraMap R F b ≠ 0 := fun h => hb ((IsFractionRing.injective R F) (h.trans (map_zero _).symm))
  let c : Fˣ := (Units.mk0 (algebraMap R F b) hbF)⁻¹
  refine ⟨c, P, Q, d, fun i h => hd i ((IsFractionRing.injective R F) (h.trans (map_zero _).symm)), ?_⟩
  apply Units.ext
  change g.val = Matrix.scalar ι (algebraMap R F b)⁻¹ *
    (P.val.map (algebraMap R F) * diagonal (fun i => algebraMap R F (d i)) *
      Q.val.map (algebraMap R F))
  have hdmap := congrArg (fun M : Matrix ι ι R => M.map (algebraMap R F)) hdiag
  rw [Matrix.map_mul, Matrix.map_mul, Matrix.diagonal_map (map_zero _)] at hdmap
  rw [← hdmap, he, Matrix.scalar_apply, ← Matrix.smul_eq_diagonal_mul, smul_smul, inv_mul_cancel₀ hbF, one_smul]

end PaperXI.FractionMatrix106
