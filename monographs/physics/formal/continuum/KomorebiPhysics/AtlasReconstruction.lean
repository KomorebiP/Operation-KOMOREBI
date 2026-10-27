module
public import KomorebiPhysics.CountableAtlas
public import KomorebiPhysics.CompactReconstruction
public import KomorebiPhysics.HilbertSchmidtReconstruction

/-! Actual finite-subset cutoff operators from a strong orthogonal atlas.
Finite numbers of sectors do not imply finite-dimensional ranges. -/
@[expose] public section
noncomputable section
set_option autoImplicit false
namespace KomorebiPhysics
namespace AtlasReconstruction
open Filter StrongReconstruction
open scoped Topology BigOperators
variable {H I : Type*} [NormedAddCommGroup H] [InnerProductSpace ℂ H]
variable (P : StrongAtlas H I)

/-- The finite operator sum, not a cutoff supplied with its limiting laws. -/
def cutoff (s : Finset I) : H →L[ℂ] H := ∑ i ∈ s, P.proj i

theorem cutoff_apply (s : Finset I) (x : H) : cutoff P s x = P.partialSum s x := by
  simp only [cutoff, sum_apply, StrongAtlas.partialSum]

theorem cutoff_norm_le (s : Finset I) : ‖cutoff P s‖ ≤ 1 := by
  apply (cutoff P s).opNorm_le_bound zero_le_one
  intro x
  simpa only [one_mul, cutoff_apply] using P.partial_norm_le s x

theorem cutoff_symmetric (s : Finset I) (x y : H) :
    inner ℂ (cutoff P s x) y = inner ℂ x (cutoff P s y) := by
  simp only [cutoff_apply, StrongAtlas.partialSum, sum_inner, inner_sum, P.selfAdjoint]

theorem cutoff_project [DecidableEq I] (s : Finset I) (i : I) (x : H) :
    cutoff P s (P.proj i x) = if i ∈ s then P.proj i x else 0 := by
  classical
  simp only [cutoff_apply, StrongAtlas.partialSum]
  by_cases hi : i ∈ s
  · rw [ite_eq_left hi]
    exact Finset.sum_eq_single i
      (fun j _ hji => P.orthogonal j i hji x)
      (fun hn => (hn hi).elim) |>.trans (P.idempotent i x)
  · rw [ite_eq_right hi]
    apply Finset.sum_eq_zero
    intro j hj
    exact P.orthogonal j i (by intro h; subst j; exact hi hj) x

theorem cutoff_idempotent (s : Finset I) : cutoff P s * cutoff P s = cutoff P s := by
  classical
  ext x
  change cutoff P s (cutoff P s x) = cutoff P s x
  rw [cutoff_apply P s x]
  simp only [StrongAtlas.partialSum, map_sum, cutoff_project]
  apply Finset.sum_congr rfl
  intro i hi
  exact ite_eq_left hi

theorem cutoff_strong (x : H) :
    Tendsto (fun s : Finset I => cutoff P s x) atTop (𝓝 x) := by
  simpa only [cutoff_apply] using P.partial_tendsto x

/-- Bounded reconstruction for the actual strong-atlas cutoff net. -/
theorem bounded_reconstruction (X : H →L[ℂ] H) (x : H) :
    Tendsto (fun s : Finset I => compression (cutoff P s) X x) atTop (𝓝 (X x)) :=
  compression_strong (cutoff P) (cutoff_norm_le P) (cutoff_strong P) X x

variable [CompleteSpace H]

theorem cutoff_selfAdjoint (s : Finset I) : IsSelfAdjoint (cutoff P s) := by
  rw [isSelfAdjoint_iff, ContinuousLinearMap.star_eq_adjoint]
  exact ((ContinuousLinearMap.eq_adjoint_iff (cutoff P s) (cutoff P s)).mpr
    (cutoff_symmetric P s)).symm

/-- Compact reconstruction with the constructed self-adjoint contractions. -/
theorem compact_reconstruction (X : H →L[ℂ] H) (hX : IsCompactOperator X) :
    Tendsto (fun s : Finset I => ‖compression (cutoff P s) X-X‖) atTop (𝓝 0) :=
  CompactReconstruction.compact_compression (cutoff P) (cutoff_norm_le P)
    (cutoff_strong P) (cutoff_selfAdjoint P) X hX

/-- HS reconstruction for any Hilbert basis. Its norm is proved basis independent. -/
theorem hs_reconstruction {J : Type*} (b : HilbertBasis J ℂ H)
    (X : H →L[ℂ] H) (hX : HilbertSchmidtCore.IsHS b X) :
    Tendsto (fun s : Finset I => HilbertSchmidtCore.hsNorm b (compression (cutoff P s) X-X))
      atTop (𝓝 0) :=
  HilbertSchmidtReconstruction.compression_norm_tendsto b (cutoff P) (cutoff_norm_le P)
    (cutoff_strong P) (cutoff_selfAdjoint P) X hX

end AtlasReconstruction
end KomorebiPhysics
