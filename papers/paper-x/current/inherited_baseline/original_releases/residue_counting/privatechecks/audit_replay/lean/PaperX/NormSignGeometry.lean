import PaperX.CountingBoundaryTransport
import PaperX.LatticeCountingFull
import PaperX.IdealClassQuantitativeGeometry

/-! Sign restrictions on the actual number-field cone retain its boundary atlas.
This module uses the product of the real embedding coordinates; no field-norm
congruence is inferred by ignoring its sign. -/
set_option autoImplicit false
noncomputable section

namespace PaperX.NormSignGeometry
open Set MeasureTheory Module
open NumberField NumberField.InfinitePlace NumberField.mixedEmbedding
open NumberField.mixedEmbedding.fundamentalCone
open scoped Classical Pointwise

/-- Cutting along the sign of a continuous nonvanishing function creates no new
frontier away from the old frontier. -/
theorem frontier_positive_restriction {E : Type*} [TopologicalSpace E]
    {D : Set E} {f : E → ℝ} (hf : Continuous f)
    (hne : ∀ x ∈ D, f x ≠ 0) :
    frontier (D ∩ {x | 0 < f x}) ⊆ frontier D := by
  intro x hx
  rcases frontier_inter_subset D {x | 0 < f x} hx with h | h
  · exact h.1
  · by_cases hxD : x ∈ D
    · have he : (0 : ℝ) = f x := frontier_lt_subset_eq continuous_const hf h.2
      exact False.elim (hne x hxD he.symm)
    · exact ⟨h.1, fun hi => hxD (interior_subset hi)⟩

variable (K : Type*) [Field K] [NumberField K]

/-- The real-coordinate product whose sign records the real embedding signs. -/
def realProduct (x : mixedSpace K) : ℝ := ∏ w : {w : InfinitePlace K // IsReal w}, x.1 w

theorem realProduct_continuous : Continuous (realProduct K) := by
  unfold realProduct
  fun_prop

theorem realProduct_ne_zero {x : mixedSpace K} (hx : x ∈ normLeOne K) :
    realProduct K x ≠ 0 := by
  apply Finset.prod_ne_zero_iff.mpr
  intro w _
  have h := fundamentalCone.normAtPlace_pos_of_mem hx.1 w.1
  rw [normAtPlace_apply_of_isReal w.2] at h
  exact norm_pos_iff.mp h

/-- The two real-sign portions of the actual unit cone. -/
def signCone (positive : Bool) : Set (mixedSpace K) :=
  normLeOne K ∩ {x | 0 < if positive then realProduct K x else -realProduct K x}

theorem signCone_frontier_subset (positive : Bool) :
    frontier (signCone K positive) ⊆ frontier (normLeOne K) := by
  apply frontier_positive_restriction
  · cases positive <;> simp only [Bool.false_eq_true, ↓reduceIte] <;>
      first | exact (realProduct_continuous K).neg | exact realProduct_continuous K
  · intro x hx
    cases positive <;> simp only [Bool.false_eq_true, ↓reduceIte, neg_ne_zero] <;>
      exact realProduct_ne_zero K hx

theorem signCone_measurable (positive : Bool) : MeasurableSet (signCone K positive) := by
  apply (measurableSet_normLeOne K).inter
  apply measurableSet_lt measurable_const
  cases positive <;> simp only [Bool.false_eq_true, ↓reduceIte] <;>
    first | exact (realProduct_continuous K).neg.measurable | exact (realProduct_continuous K).measurable

theorem signCone_bounded (positive : Bool) : Bornology.IsBounded (signCone K positive) :=
  (isBounded_normLeOne K).subset inter_subset_left

theorem signCone_disjoint : Disjoint (signCone K true) (signCone K false) := by
  rw [Set.disjoint_left]
  intro x hx hy
  have hp : 0 < realProduct K x := hx.2
  have hn : 0 < -realProduct K x := hy.2
  linarith

theorem signCone_union : signCone K true ∪ signCone K false = normLeOne K := by
  apply Set.Subset.antisymm
  · exact union_subset inter_subset_left inter_subset_left
  · intro x hx
    rcases lt_or_gt_of_ne (realProduct_ne_zero K hx) with hn | hp
    · exact Or.inr ⟨hx, neg_pos.mpr hn⟩
    · exact Or.inl ⟨hx, hp⟩

/-- The already constructed actual boundary charts also cover either sign portion. -/
def signConeAtlas {ι : Type*} [Fintype ι]
    (e : mixedSpace K ≃L[ℝ] (ι → ℝ))
    (hcard : Fintype.card ι = Module.finrank ℚ K) (positive : Bool) :
    LatticeCounting.LipschitzBoundaryAtlas ι (e '' signCone K positive) :=
  { CountingBoundaryPolar.boundaryAtlas_image K e hcard with
    covers := by
      intro y hy
      apply (CountingBoundaryPolar.boundaryAtlas_image K e hcard).covers
      have hs := Set.image_mono (f := e.toHomeomorph) (signCone_frontier_subset K positive)
      rw [e.toHomeomorph.image_frontier, e.toHomeomorph.image_frontier] at hs
      exact hs hy }

end PaperX.NormSignGeometry
