import PaperX.CountingBoundaryAtlas
import PaperX.LatticeCountingInterface

set_option autoImplicit false
noncomputable section

namespace PaperX.CountingBoundaryPolar

open NumberField NumberField.mixedEmbedding
open NumberField.mixedEmbedding.fundamentalCone
open PaperX.LatticeCounting
open scoped Classical

variable (K : Type*) [Field K] [NumberField K]

/-- The actual cone supplies the grid-counting atlas after any continuous linear coordinates. -/
theorem nonempty_boundaryAtlas_image {ι : Type*} [Fintype ι]
    (e : mixedSpace K ≃L[ℝ] (ι → ℝ))
    (hcard : Fintype.card ι = Module.finrank ℚ K) :
    Nonempty (LipschitzBoundaryAtlas ι (e '' normLeOne K)) := by
  let P (n : ℕ) : Prop := ∃ m : ℕ, ∃ C : NNReal,
      ∃ f : Fin m → (Fin (n - 1) → ℝ) → mixedSpace K,
        (∀ j, LipschitzOnWith C (f j) (Set.Icc (0 : Fin (n - 1) → ℝ) 1)) ∧
        frontier (normLeOne K) ⊆ ⋃ j : Fin m,
          f j '' Set.Icc (0 : Fin (n - 1) → ℝ) 1
  have hd : P (Module.finrank ℚ K) := exists_boundary_atlas K
  have h : P (Fintype.card ι) := Eq.mpr (congrArg P hcard) hd
  obtain ⟨m, C, f, hf, hcover⟩ := h
  refine ⟨{ charts := m
            lip := ‖e.toContinuousLinearMap‖₊ * C
            map := fun j v => e (f j v)
            lipschitz := fun j => e.toContinuousLinearMap.lipschitzWith.comp_lipschitzOnWith (hf j)
            covers := ?_ }⟩
  intro y hy
  have hy' : y ∈ e '' frontier (normLeOne K) := by
    change y ∈ e.toHomeomorph '' frontier (normLeOne K)
    rw [e.toHomeomorph.image_frontier]
    exact hy
  obtain ⟨x, hx, rfl⟩ := hy'
  obtain ⟨j, v, hv, heq⟩ := Set.mem_iUnion.mp (hcover hx)
  refine Set.mem_iUnion.mpr ⟨j, v, hv, ?_⟩
  exact congrArg e heq

def boundaryAtlas_image {ι : Type*} [Fintype ι]
    (e : mixedSpace K ≃L[ℝ] (ι → ℝ))
    (hcard : Fintype.card ι = Module.finrank ℚ K) :
    LipschitzBoundaryAtlas ι (e '' normLeOne K) :=
  Classical.choice (nonempty_boundaryAtlas_image K e hcard)

end PaperX.CountingBoundaryPolar
