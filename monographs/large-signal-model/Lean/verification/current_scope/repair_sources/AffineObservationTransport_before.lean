import KomorebiLSM.ObservationPolicyTransport
import KomorebiLSM.BernsteinKernel
import KomorebiLSM.UniformIntervalMoments
import Mathlib.MeasureTheory.Measure.Lebesgue.Basic

set_option autoImplicit false
namespace Komorebi.LSM.AffineObservationTransport
open MeasureTheory ContinuousInstrument ContinuousRecords ObservationEquivalence
noncomputable section

/-- The actual affine observation equivalence, with its literal inverse. -/
def equiv : ℝ ≃ᵐ ℝ where
  toFun v := 2*v-1
  invFun u := (u+1)/2
  left_inv v := by ring
  right_inv u := by ring
  measurable_toFun := by fun_prop
  measurable_invFun := by fun_prop

@[simp] theorem equiv_apply (v : ℝ) : equiv v=2*v-1 := rfl
@[simp] theorem equiv_symm_apply (u : ℝ) : equiv.symm u=(u+1)/2 := rfl

theorem preimage_interval : equiv ⁻¹' Set.Icc (-1 : ℝ) 1=Set.Icc (0 : ℝ) 1 := by
  ext v
  change (-1≤2*v-1 ∧ 2*v-1≤1) ↔ (0≤v ∧ v≤1)
  constructor <;> rintro ⟨h0,h1⟩ <;> constructor <;> linarith

/-- The factor one half is derived from actual Lebesgue scaling and translation. -/
theorem map_volume : volume.map equiv=ENNReal.ofReal (1/2 : ℝ) • volume := by
  have he : (equiv : ℝ → ℝ)=(fun x : ℝ => x+(-1)) ∘ (fun v : ℝ => 2*v) := by
    funext v
    simp only [equiv_apply,Function.comp_apply]
    ring
  rw [he,← Measure.map_map (by fun_prop) (by fun_prop),
    Real.map_volume_mul_left (by norm_num : (2 : ℝ)≠0),Measure.map_smul,
    (measurePreserving_add_right volume (-1)).map_eq]
  norm_num

/-- The unit-interval Bernstein reference pushes forward to the actual normalized symmetric reference. -/
theorem measure_preserving : MeasurePreserving equiv BernsteinKernel.measure UniformIntervalMoments.measure := by
  refine ⟨equiv.measurable,?_⟩
  calc
    BernsteinKernel.measure.map equiv = (volume.map equiv).restrict (Set.Icc (-1 : ℝ) 1) := by
      rw [Measure.restrict_map equiv.measurable measurableSet_Icc,preimage_interval]
      rfl
    _ = (ENNReal.ofReal (1/2 : ℝ) • volume).restrict (Set.Icc (-1 : ℝ) 1) := by rw [map_volume]
    _ = UniformIntervalMoments.measure := by
      rw [Measure.restrict_smul]
      unfold UniformIntervalMoments.measure AveragedCongruence.uniformInterval ProbabilityTheory.cond
      rw [Real.volume_Ioc,restrict_Ioc_eq_restrict_Icc]
      norm_num

theorem inverse_measure_preserving :
    MeasurePreserving equiv.symm UniformIntervalMoments.measure BernsteinKernel.measure :=
  measure_preserving.symm equiv

variable {E A : Type*} [NormedAddCommGroup E] [NormedSpace ℝ E]
variable {C : BaseNorm.ProbabilityCone E}

/-- Symmetric-interval densities pulled to the actual Bernstein reference. -/
def pullInstrument (D : DensityInstrument (A := A) C UniformIntervalMoments.measure) :
    DensityInstrument (A := A) C BernsteinKernel.measure :=
  ObservationEquivalence.pullInstrument equiv measure_preserving D

@[simp] theorem pullInstrument_op (D : DensityInstrument (A := A) C UniformIntervalMoments.measure)
    (a : A) (v : ℝ) : (pullInstrument D).op a v=D.op a (2*v-1) := rfl

/-- Unit-interval fitted densities moved to the actual symmetric reference. -/
def pushInstrument (D : DensityInstrument (A := A) C BernsteinKernel.measure) :
    DensityInstrument (A := A) C UniformIntervalMoments.measure :=
  ObservationEquivalence.pullInstrument equiv.symm inverse_measure_preserving D

@[simp] theorem pushInstrument_op (D : DensityInstrument (A := A) C BernsteinKernel.measure)
    (a : A) (u : ℝ) : (pushInstrument D).op a u=D.op a ((u+1)/2) := rfl

section Records
variable [MeasurableSpace A] [Fintype A] [MeasurableSingletonClass A]

def pullPolicy (π : Policy (A := A) (Y := ℝ)) : Policy (A := A) (Y := ℝ) :=
  ObservationEquivalence.pullPolicy equiv π

def pushPolicy (π : Policy (A := A) (Y := ℝ)) : Policy (A := A) (Y := ℝ) :=
  ObservationEquivalence.pullPolicy equiv.symm π

theorem pull_recordLaw (D : DensityInstrument (A := A) C UniformIntervalMoments.measure)
    (π : Policy (A := A) (Y := ℝ)) (z : E) (N : ℕ) :
    (recordLaw (pullInstrument D) (pullPolicy π) z N).map
      (historyEquiv (stepEquiv equiv) N)=recordLaw D π z N :=
  recordLaw_map equiv measure_preserving D π z N

theorem push_recordLaw (D : DensityInstrument (A := A) C BernsteinKernel.measure)
    (π : Policy (A := A) (Y := ℝ)) (z : E) (N : ℕ) :
    (recordLaw (pushInstrument D) (pushPolicy π) z N).map
      (historyEquiv (stepEquiv equiv.symm) N)=recordLaw D π z N :=
  recordLaw_map equiv.symm inverse_measure_preserving D π z N

/-- The pushed fit uses the same target adaptive policy as the native symmetric-interval model. -/
theorem push_recordLaw_forward (D : DensityInstrument (A := A) C BernsteinKernel.measure)
    (π : Policy (A := A) (Y := ℝ)) (z : E) (N : ℕ) :
    (recordLaw D (pullPolicy π) z N).map (historyEquiv (stepEquiv equiv) N)=
      recordLaw (pushInstrument D) π z N :=
  forward_recordLaw equiv measure_preserving D π z N

end Records
end
end Komorebi.LSM.AffineObservationTransport
