import PaperXI.FractionMatrix106
import PaperXI.CuspidalCartan105
import Mathlib.RingTheory.DiscreteValuationRing.Basic
import Mathlib.Data.Finset.Max

/-! Normalized Cartan decomposition over the fraction field of a DVR. -/
set_option autoImplicit false
noncomputable section
namespace PaperXI.DVRCartan106
open Matrix
variable {ι R F : Type*} [Fintype ι] [DecidableEq ι]
  [CommRing R] [IsDomain R] [IsDiscreteValuationRing R]
  [Field F] [Algebra R F] [IsFractionRing R F]

def unitsDiagonal (u : ι → Rˣ) : GL ι R where
  val := diagonal (fun i => (u i : R))
  inv := diagonal (fun i => ((u i)⁻¹ : Rˣ))
  val_inv := by simp [diagonal_mul_diagonal]
  inv_val := by simp [diagonal_mul_diagonal]

theorem normalize_diagonal [Nonempty ι] (π : R) (hπ : Irreducible π)
    (d : ι → R) (hd : ∀ i, algebraMap R F (d i) ≠ 0) :
    ∃ c : Fˣ, ∃ U : GL ι R, ∃ a : ι → ℕ,
      (∃ i, a i = 0) ∧
      SplitRadical105.diagonalGL (fun i => algebraMap R F (d i)) hd =
        GeneralLinearGroup.scalar ι c * (GeneralLinearGroup.map (algebraMap R F) U *
          SplitRadical105.cartan (algebraMap R F π)
            (fun h => hπ.ne_zero ((IsFractionRing.injective R F) (h.trans (map_zero _).symm))) a) := by
  have hdR : ∀ i, d i ≠ 0 := fun i h => hd i (by rw [h, map_zero])
  choose n u hu using fun i => IsDiscreteValuationRing.eq_unit_mul_pow_irreducible (hdR i) hπ
  obtain ⟨j, _, hj⟩ := Finset.exists_max_image Finset.univ n Finset.univ_nonempty
  have hn : ∀ i, n i ≤ n j := fun i => hj i (Finset.mem_univ i)
  have hpF : algebraMap R F π ≠ 0 :=
    fun h => hπ.ne_zero ((IsFractionRing.injective R F) (h.trans (map_zero _).symm))
  refine ⟨Units.mk0 ((algebraMap R F π) ^ n j) (pow_ne_zero _ hpF),
    unitsDiagonal u, fun i => n j - n i, ⟨j, Nat.sub_self _⟩, ?_⟩
  apply Units.ext
  ext i k
  change diagonal (fun i => algebraMap R F (d i)) i k =
    (Matrix.scalar ι ((algebraMap R F π) ^ n j) *
      ((diagonal (fun i => (u i : R))).map (algebraMap R F) *
        diagonal (fun i => ((algebraMap R F π) ^ (n j - n i))⁻¹))) i k
  rw [Matrix.diagonal_map (map_zero _), Matrix.diagonal_mul_diagonal, Matrix.scalar_apply, ← Matrix.smul_eq_diagonal_mul]
  by_cases hik : i = k
  · subst k
    simp only [Matrix.diagonal_apply_eq, Matrix.smul_apply, smul_eq_mul]
    rw [hu i, map_mul, map_pow]
    have hpow : (algebraMap R F π) ^ n j =
        (algebraMap R F π) ^ n i * (algebraMap R F π) ^ (n j - n i) := by
      rw [← pow_add, Nat.add_sub_of_le (hn i)]
    rw [hpow]
    field_simp
  · simp [Matrix.smul_apply, hik]

theorem hasCartan [Nonempty ι] (π : R) (hπ : Irreducible π) :
    CuspidalCartan105.HasCartan (ι := ι) (algebraMap R F) π
      (fun h => hπ.ne_zero ((IsFractionRing.injective R F) (h.trans (map_zero _).symm))) := by
  intro g
  obtain ⟨c, P, Q, d, hd, he⟩ := FractionMatrix106.exists_integral_diagonal (R := R) g
  obtain ⟨z, U, a, ha, hdiag⟩ := normalize_diagonal π hπ d hd
  refine ⟨c * z, P * U, Q, a, ha, ?_⟩
  rw [he, hdiag, map_mul, map_mul]
  have hc := GeneralLinearGroup.scalar_commute z (GeneralLinearGroup.map (algebraMap R F) P)
  simp only [mul_assoc]
  rw [← mul_assoc (GeneralLinearGroup.map (algebraMap R F) P)
    (GeneralLinearGroup.scalar ι z), ← hc, mul_assoc]

end PaperXI.DVRCartan106
