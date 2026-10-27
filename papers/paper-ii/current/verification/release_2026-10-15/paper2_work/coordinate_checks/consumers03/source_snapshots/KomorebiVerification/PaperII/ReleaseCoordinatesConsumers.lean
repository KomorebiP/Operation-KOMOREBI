import KomorebiVerification.PaperII.ReleaseCoordinatesAlgebra
import KomorebiVerification.PaperII.ReleaseCoordinatesHilbert
import KomorebiVerification.PaperII.ReleaseCoordinatesFourier

/-! Exact formal-series endpoints used by the chapter's selector and CRT statements. -/
set_option autoImplicit false
noncomputable section
namespace Komorebi.Residue
universe u
variable {R : Type u}

/-- The printed residue family satisfies the manuscript's nonzero packet convention. -/
theorem manuscript_series_residue_packet [CommRing R] [Nontrivial R]
    (N : Nat) (hN : 0 < N) :
    Komorebi.PaperII.CommonRefinement.Nonzero (seriesResidueFamily (R := R) N hN) :=
  seriesResidueProj_nonzero N hN

/-- Coefficient selectors commute even without coprimality of their moduli. -/
theorem seriesResidueProj_commute [Semiring R]
    (m n : Nat) (hm : 0 < m) (hn : 0 < n) (j : Fin m) (k : Fin n) :
    (seriesResidueProj (R := R) m hm j).comp (seriesResidueProj n hn k) =
      (seriesResidueProj n hn k).comp (seriesResidueProj m hm j) := by
  ext f a
  simp only [LinearMap.comp_apply, seriesResidueProj_coeff]
  by_cases hj : residueAddress m hm a = j <;>
    by_cases hk : residueAddress n hn a = k <;> simp [hj, hk]

/-- Dyadic-odd factorization on actual formal series, including dyadic exponent zero. -/
theorem manuscript_series_dyadic_odd [CommRing R]
    (a M : Nat) (hM : 0 < M) (hodd : Odd M) (s : Fin (2 ^ a * M)) :
    let h2 : 0 < 2 ^ a := pow_pos (by decide) a
    let c := crtComponents (2 ^ a) M h2 hM s
    seriesResidueProj (R := R) (2 ^ a * M) (Nat.mul_pos h2 hM) s =
        (seriesResidueProj (2 ^ a) h2 c.1).comp (seriesResidueProj M hM c.2) ∧
      seriesResidueProj (R := R) (2 ^ a * M) (Nat.mul_pos h2 hM) s =
        (seriesResidueProj M hM c.2).comp (seriesResidueProj (2 ^ a) h2 c.1) := by
  dsimp only
  have h := (seriesResidueProj_crt (R := R) (2 ^ a) M (pow_pos (by decide) a) hM
    (twoPow_coprime_of_odd a M hodd) s).symm
  exact ⟨h, h.trans (seriesResidueProj_commute _ _ _ _ _ _)⟩

end Komorebi.Residue

namespace Komorebi.PaperII.HilbertCoordinates
open Komorebi.Foundation
universe u v w x y
variable {𝕜 : Type u} [RCLike 𝕜]
variable {E : Type v} [NormedAddCommGroup E] [InnerProductSpace 𝕜 E]
variable {ι : Type w} {κ : Type x} {τ : Type y}
variable [Fintype ι] [Fintype κ] [Fintype τ]

theorem hilbertCoordinateChange_self (P : LinearProjectorFamily 𝕜 E ι)
    (hP : ∀ i, (P.proj i).IsSymmetric) :
    hilbertCoordinateChange P P hP hP = LinearIsometryEquiv.refl 𝕜 (HilbertPacketSpace P) := by
  ext x
  exact (hilbertPacketUnitary P hP).apply_symm_apply x

theorem hilbertCoordinateChange_symm (P : LinearProjectorFamily 𝕜 E ι)
    (Q : LinearProjectorFamily 𝕜 E κ)
    (hP : ∀ i, (P.proj i).IsSymmetric) (hQ : ∀ j, (Q.proj j).IsSymmetric) :
    (hilbertCoordinateChange P Q hP hQ).symm = hilbertCoordinateChange Q P hQ hP := by
  ext x
  rfl

theorem hilbertCoordinateChange_trans (P : LinearProjectorFamily 𝕜 E ι)
    (Q : LinearProjectorFamily 𝕜 E κ) (S : LinearProjectorFamily 𝕜 E τ)
    (hP : ∀ i, (P.proj i).IsSymmetric) (hQ : ∀ j, (Q.proj j).IsSymmetric)
    (hS : ∀ k, (S.proj k).IsSymmetric) :
    (hilbertCoordinateChange P Q hP hQ).trans (hilbertCoordinateChange Q S hQ hS) =
      hilbertCoordinateChange P S hP hS := by
  ext x
  simp only [hilbertCoordinateChange, LinearIsometryEquiv.trans_apply,
    LinearIsometryEquiv.symm_apply_apply]

end Komorebi.PaperII.HilbertCoordinates
#print axioms Komorebi.Residue.manuscript_series_residue_packet
#print axioms Komorebi.Residue.manuscript_series_dyadic_odd
#print axioms Komorebi.PaperII.HilbertCoordinates.hilbertCoordinateChange_trans
