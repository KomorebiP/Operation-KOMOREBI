import PaperX.CountingBoundaryCover

set_option autoImplicit false
noncomputable section

namespace PaperX.CountingBoundaryPolar

open NumberField NumberField.InfinitePlace NumberField.mixedEmbedding
open NumberField.mixedEmbedding.fundamentalCone
open scoped Classical

variable (K : Type*) [Field K] [NumberField K]

abbrev FaceCoordinates (w : InfinitePlace K) :=
  {i : Coordinate K // i ≠ Sum.inl w}
abbrev FaceIndex := Signs K × InfinitePlace K × Bool
abbrev BoundaryParameters := Fin (Module.finrank ℚ K - 1) → ℝ

theorem faceCoordinates_card (w : InfinitePlace K) :
    Fintype.card (FaceCoordinates K w) = Module.finrank ℚ K - 1 := by
  simp only [FaceCoordinates, ne_eq, Fintype.card_subtype_compl, Fintype.card_subtype_eq,
    coordinate_card]

def faceEquiv (w : InfinitePlace K) :
    FaceCoordinates K w ≃ Fin (Module.finrank ℚ K - 1) :=
  Fintype.equivFinOfCardEq (faceCoordinates_card K w)

def insertFace (w : InfinitePlace K) (b : Bool) (v : BoundaryParameters K) : Parameters K :=
  fun i => if h : i = Sum.inl w then (if b then 1 else 0) else v (faceEquiv K w ⟨i, h⟩)

def faceChart (j : FaceIndex K) (v : BoundaryParameters K) : mixedSpace K :=
  polarChart K j.1 (insertFace K j.2.1 j.2.2 v)

theorem insertFace_contDiff (w : InfinitePlace K) (b : Bool) :
    ContDiff ℝ 1 (insertFace K w b) := by
  apply contDiff_pi.mpr
  intro i
  dsimp [insertFace]
  by_cases h : i = Sum.inl w
  · simp only [dite_eq_left h]
    exact contDiff_const
  · simp only [dite_eq_right h]
    exact contDiff_apply ℝ ℝ (faceEquiv K w ⟨i, h⟩)

theorem faceChart_contDiff (j : FaceIndex K) : ContDiff ℝ 1 (faceChart K j) :=
  (polarChart_contDiff K j.1).comp (insertFace_contDiff K j.2.1 j.2.2)

theorem faceChart_lipschitz (j : FaceIndex K) : ∃ C : NNReal,
    LipschitzOnWith C (faceChart K j) (Set.Icc (0 : BoundaryParameters K) 1) := by
  apply (faceChart_contDiff K j).contDiffOn.exists_lipschitzOnWith (by decide)
  · exact convex_Icc _ _
  · exact isCompact_Icc

theorem faceChart_common_lipschitz : ∃ C : NNReal, ∀ j : FaceIndex K,
    LipschitzOnWith C (faceChart K j) (Set.Icc (0 : BoundaryParameters K) 1) := by
  let c : FaceIndex K → NNReal := fun j => (faceChart_lipschitz K j).choose
  refine ⟨Finset.univ.sup c, fun j => ?_⟩
  exact (faceChart_lipschitz K j).choose_spec.weaken
    (Finset.le_sup (f := c) (Finset.mem_univ j))

def restrictFace (w : InfinitePlace K) (u : Parameters K) : BoundaryParameters K :=
  fun i => u ((faceEquiv K w).symm i).1

theorem insertFace_restrictFace (w : InfinitePlace K) (b : Bool) (u : Parameters K)
    (hu : u (Sum.inl w) = if b then 1 else 0) :
    insertFace K w b (restrictFace K w u) = u := by
  ext i
  by_cases hi : i = Sum.inl w
  · subst i
    simp [insertFace, hu]
  · simp [insertFace, restrictFace, hi]

theorem restrictFace_mem_cube (w : InfinitePlace K) {u : Parameters K}
    (hu : u ∈ Set.Icc (0 : Parameters K) 1) :
    restrictFace K w u ∈ Set.Icc (0 : BoundaryParameters K) 1 :=
  ⟨fun _ => hu.1 _, fun _ => hu.2 _⟩

/-- Actual mixed-space frontier covered by finitely many smooth charts of dimension `d-1`. -/
theorem frontier_faceChart_cover :
    frontier (normLeOne K) ⊆
      ⋃ j : FaceIndex K, faceChart K j '' Set.Icc (0 : BoundaryParameters K) 1 := by
  intro x hx
  obtain ⟨s, u, hu, ⟨w, hw⟩, heq⟩ := frontier_cube_faces K hx
  rcases hw with hw | hw
  · refine Set.mem_iUnion.mpr ⟨(s, w, false), restrictFace K w u,
      restrictFace_mem_cube K w hu, ?_⟩
    dsimp [faceChart]
    rw [insertFace_restrictFace K w false u (by simpa using hw)]
    exact heq
  · refine Set.mem_iUnion.mpr ⟨(s, w, true), restrictFace K w u,
      restrictFace_mem_cube K w hu, ?_⟩
    dsimp [faceChart]
    rw [insertFace_restrictFace K w true u (by simpa using hw)]
    exact heq

/-- A uniform Lipschitz boundary atlas with the exact parameter dimension, including degree one. -/
theorem exists_boundary_atlas :
    ∃ m : ℕ, ∃ C : NNReal,
    ∃ f : Fin m → BoundaryParameters K → mixedSpace K,
      (∀ j, LipschitzOnWith C (f j) (Set.Icc (0 : BoundaryParameters K) 1)) ∧
      frontier (normLeOne K) ⊆
        ⋃ j : Fin m, f j '' Set.Icc (0 : BoundaryParameters K) 1 := by
  obtain ⟨C, hC⟩ := faceChart_common_lipschitz K
  let e := Fintype.equivFin (FaceIndex K)
  refine ⟨Fintype.card (FaceIndex K), C, fun j => faceChart K (e.symm j),
    fun j => hC _, ?_⟩
  intro x hx
  obtain ⟨j, hj⟩ := Set.mem_iUnion.mp (frontier_faceChart_cover K hx)
  refine Set.mem_iUnion.mpr ⟨e j, ?_⟩
  simpa using hj

end PaperX.CountingBoundaryPolar
