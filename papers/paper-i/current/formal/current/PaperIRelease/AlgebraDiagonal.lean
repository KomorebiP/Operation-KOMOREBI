import PaperIRelease.AlgebraSupport

set_option autoImplicit false
set_option maxHeartbeats 2000000

namespace Komorebi.PaperIRelease
open Komorebi.Foundation

universe u v w
variable {K : Type u} [Field K]
variable {X : Type v} [AddCommGroup X] [Module K X]
variable {I : Type w} [Fintype I]

/-- The literal diagonal-block projection on the ambient endomorphism space. -/
def diagonalProjection (P : LinearProjectorFamily K X I) :
    Module.End K (Module.End K X) where
  toFun T := ∑ i, transferBlock P P T i i
  map_add' S T := by
    ext x
    simp [transferBlock, Finset.sum_add_distrib]
  map_smul' c T := by
    ext x
    simp [transferBlock, Finset.smul_sum]

@[simp] theorem diagonalProjection_apply (P : LinearProjectorFamily K X I)
    (T : Module.End K X) (x : X) :
    diagonalProjection P T x = ∑ i, P.proj i (T (P.proj i x)) := by
  simp [diagonalProjection, transferBlock]

theorem proj_diagonalProjection (P : LinearProjectorFamily K X I)
    (T : Module.End K X) (i : I) (x : X) :
    P.proj i (diagonalProjection P T x) = P.proj i (T (P.proj i x)) := by
  classical
  rw [diagonalProjection_apply]
  rw [map_sum, Finset.sum_eq_single i]
  · exact P.idempotent i _
  · intro j _ hji
    exact P.orthogonal hji.symm _
  · simp

theorem diagonalProjection_proj (P : LinearProjectorFamily K X I)
    (T : Module.End K X) (i : I) (x : X) :
    diagonalProjection P T (P.proj i x) = P.proj i (T (P.proj i x)) := by
  classical
  rw [diagonalProjection_apply]
  rw [Finset.sum_eq_single i]
  · rw [P.idempotent]
  · intro j _ hji
    rw [P.orthogonal hji, map_zero, map_zero]
  · simp

theorem diagonalProjection_commutes (P : LinearProjectorFamily K X I)
    (T : Module.End K X) (i : I) :
    (diagonalProjection P T).comp (P.proj i) = (P.proj i).comp (diagonalProjection P T) := by
  ext x
  exact (diagonalProjection_proj P T i x).trans (proj_diagonalProjection P T i x).symm

theorem diagonalProjection_of_commutes (P : LinearProjectorFamily K X I)
    (T : Module.End K X)
    (h : ∀ i, T.comp (P.proj i) = (P.proj i).comp T) :
    diagonalProjection P T = T := by
  ext x
  rw [diagonalProjection_apply]
  calc
    (∑ i, P.proj i (T (P.proj i x))) = ∑ i, T (P.proj i x) := by
      apply Finset.sum_congr rfl
      intro i _
      have hh := LinearMap.congr_fun (h i) (P.proj i x)
      simpa only [LinearMap.comp_apply, P.idempotent] using hh.symm
    _ = T x := by rw [← map_sum, P.complete]

theorem commutes_iff_diagonalProjection (P : LinearProjectorFamily K X I)
    (T : Module.End K X) :
    (∀ i, T.comp (P.proj i) = (P.proj i).comp T) ↔ diagonalProjection P T = T := by
  constructor
  · exact diagonalProjection_of_commutes P T
  · intro h i
    rw [← h]
    exact diagonalProjection_commutes P T i

theorem diagonalProjection_idempotent (P : LinearProjectorFamily K X I)
    (T : Module.End K X) :
    diagonalProjection P (diagonalProjection P T) = diagonalProjection P T :=
  diagonalProjection_of_commutes P _ (diagonalProjection_commutes P T)

theorem offdiagonal_zero_of_commutes (P : LinearProjectorFamily K X I)
    (T : Module.End K X)
    (h : ∀ i, T.comp (P.proj i) = (P.proj i).comp T)
    {b a : I} (hba : b ≠ a) : transferBlock P P T b a = 0 := by
  ext x
  change P.proj b (T (P.proj a x)) = 0
  have hh := LinearMap.congr_fun (h a) x
  change T (P.proj a x) = P.proj a (T x) at hh
  rw [hh, P.orthogonal hba]

theorem diagonalProjection_of_offdiagonal_zero (P : LinearProjectorFamily K X I)
    (T : Module.End K X)
    (h : ∀ b a, b ≠ a → transferBlock P P T b a = 0) :
    diagonalProjection P T = T := by
  classical
  ext x
  calc
    diagonalProjection P T x = ∑ b, ∑ a, P.proj b (T (P.proj a x)) := by
      rw [diagonalProjection_apply]
      apply Finset.sum_congr rfl
      intro b _
      symm
      rw [Finset.sum_eq_single b]
      · intro a _ hab
        exact LinearMap.congr_fun (h b a hab.symm) x
      · simp
    _ = T x := transferBlock_reconstruction P P T x

/-- The three commutant criteria are equivalent for actual ambient operators. -/
theorem commutes_iff_offdiagonal_zero (P : LinearProjectorFamily K X I)
    (T : Module.End K X) :
    (∀ i, T.comp (P.proj i) = (P.proj i).comp T) ↔
    (∀ b a, b ≠ a → transferBlock P P T b a = 0) := by
  constructor
  · intro h b a hba
    exact offdiagonal_zero_of_commutes P T h hba
  · intro h
    exact (commutes_iff_diagonalProjection P T).mpr
      (diagonalProjection_of_offdiagonal_zero P T h)

variable [DecidableEq I]

def blockDiagonalSubalgebra (P : LinearProjectorFamily K X I) :
    Subalgebra K (Module.End K X) :=
  supportSubalgebra P Eq (fun _ => rfl) (fun _ _ _ hab hbc => hab.trans hbc)

/-- The range of the linear idempotent is precisely the block-diagonal subalgebra. -/
theorem diagonalProjection_range (P : LinearProjectorFamily K X I) :
    LinearMap.range (diagonalProjection P) = (blockDiagonalSubalgebra P).toSubmodule := by
  ext T
  constructor
  · rintro ⟨S, rfl⟩
    apply (operatorSupported_iff_ambient P Eq _).mpr
    intro b a hab
    exact offdiagonal_zero_of_commutes P _ (diagonalProjection_commutes P S) (Ne.symm hab)
  · intro h
    have hh := (operatorSupported_iff_ambient P Eq T).mp h
    exact ⟨T, diagonalProjection_of_offdiagonal_zero P T (fun b a hba => hh b a hba.symm)⟩

end Komorebi.PaperIRelease
