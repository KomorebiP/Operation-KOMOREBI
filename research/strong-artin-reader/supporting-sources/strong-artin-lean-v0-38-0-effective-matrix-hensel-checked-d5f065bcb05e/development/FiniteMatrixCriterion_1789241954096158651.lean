import EffectiveMatrixRoot

namespace Komorebi.StrongArtin.MatrixHensel
noncomputable section
open scoped Matrix.Norms.Elementwise
attribute [local instance] padicMatrixNormedRing padicMatrixUltra padicMatrixComplete

variable {p : ℕ} [Fact p.Prime]
variable {ι : Type*} [Fintype ι] [DecidableEq ι] [Nonempty ι]

/-- This test takes only finite-ring inputs. -/
def finiteMatrixTest (q : ℕ) (B : Matrix (ι × ι) (ι × ι) (ZMod (p^q)))
    (A U : Matrix ι ι (ZMod (p^q))) (d : ℕ) : Prop :=
  ∀ i j, (∑ t : ι × ι, B (i,j) t * (U-A^d) t.1 t.2) = 0

theorem integral_test_iff_finite (q d : ℕ)
    (B : Matrix (ι × ι) (ι × ι) (PadicInt p)) (A U : Matrix ι ι (PadicInt p)) :
    (PadicInt.toZModPow q).mapMatrix (integralAction B (U-A^d)) = 0 ↔
    finiteMatrixTest q ((PadicInt.toZModPow q).mapMatrix B)
      ((PadicInt.toZModPow q).mapMatrix A) ((PadicInt.toZModPow q).mapMatrix U) d := by
  have he : (PadicInt.toZModPow q).mapMatrix (integralAction B (U-A^d)) =
      fun i j => ∑ t : ι × ι, (PadicInt.toZModPow q) (B (i,j) t) *
        (((PadicInt.toZModPow q).mapMatrix U - ((PadicInt.toZModPow q).mapMatrix A)^d) t.1 t.2) := by
    ext i j
    change (PadicInt.toZModPow q) (∑ t : ι × ι, B (i,j) t * (U-A^d) t.1 t.2) = _
    rw [map_sum]
    simp only [map_mul]
    have hh := map_sub ((PadicInt.toZModPow q).mapMatrix) U (A^d)
    rw [map_pow] at hh
    congr 1
    ext t
    rw [← hh]
    rfl
  rw [he]
  constructor
  · intro h i j
    exact congrFun (congrFun h i) j
  · intro h
    ext i j
    exact h i j

theorem matrix_unit_root_finite_iff (A U : (Matrix ι ι (PadicInt p))ˣ) (d s m : ℕ)
    (hd : d ≠ 0) (hsm : s < m) (B : Matrix (ι × ι) (ι × ι) (PadicInt p))
    (hc : InverseCertificate (integralMatrix A.val) d s B) :
    (∃! F : (Matrix ι ι (PadicInt p))ˣ, F^d = U ∧
      (PadicInt.toZModPow m).mapMatrix F.val = (PadicInt.toZModPow m).mapMatrix A.val) ↔
    finiteMatrixTest (m+s) ((PadicInt.toZModPow (m+s)).mapMatrix B)
      ((PadicInt.toZModPow (m+s)).mapMatrix A.val)
      ((PadicInt.toZModPow (m+s)).mapMatrix U.val) d := by
  rw [matrix_unit_root_iff A U d s m hd hsm B hc]
  exact integral_test_iff_finite (m+s) d B A.val U.val

end
end Komorebi.StrongArtin.MatrixHensel
