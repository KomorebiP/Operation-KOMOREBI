import KomorebiPhysics.Relativistic3DL2CellReconstruction

open scoped InnerProductSpace
open MeasureTheory WithLp
open KomorebiPhysics.Relativistic3DL2CellReconstruction
open KomorebiPhysics.Relativistic3DL2CellReconstruction.UnitVolumePartition

noncomputable section
set_option autoImplicit false

universe uΩ uI uE
variable {Ω : Type uΩ} {I : Type uI} {E : Type uE}
variable [MeasurableSpace Ω] [Fintype I] [DecidableEq I]
variable [NormedAddCommGroup E] [InnerProductSpace ℂ E] [CompleteSpace E]
variable (μ : Measure Ω) (P : UnitVolumePartition (μ := μ) (I := I))

example (ψ : PiLp 2 (fun _ : I => E)) (f : Lp E 2 μ) :
    inner ℂ (stepIsometry μ P ψ) (f - stepProjection μ P f) = 1 := by
  rw [inner_step_residual]
  norm_num
