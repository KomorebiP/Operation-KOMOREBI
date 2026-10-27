import KomorebiLSM.UniformIntervalMoments
import Mathlib.MeasureTheory.Integral.Bochner.Set

/-! The exact average separation of two interval-uniform points. The factor
one third is derived from the two triangles, rather than supplied as data. -/
set_option autoImplicit false
namespace Komorebi.LSM.CellDistance
open MeasureTheory intervalIntegral
open scoped ENNReal

/-- Split the absolute difference at the observation point. -/
theorem integral_abs_sub (a b y : ℝ) (hay : a≤y) (hyb : y≤b) :
    (∫ v in a..b, |y-v|)=((y-a)^2+(b-y)^2)/2 := by
  have hl : (∫ v in a..y, |y-v|)=(y-a)^2/2 := by
    calc
      _ = ∫ v in a..y, y-v := by
        apply integral_congr
        intro v hv
        rw [Set.uIcc_of_le hay] at hv
        exact abs_of_nonneg (sub_nonneg.mpr hv.2)
      _ = _ := by
        rw [intervalIntegral.integral_sub (f := fun v : ℝ => y) (g := fun v : ℝ => v)
          intervalIntegrable_const (continuous_id.intervalIntegrable a y),
          intervalIntegral.integral_const,integral_id]
        simp only [smul_eq_mul]
        ring
  have hr : (∫ v in y..b, |y-v|)=(b-y)^2/2 := by
    calc
      _ = ∫ v in y..b, v-y := by
        apply integral_congr
        intro v hv
        rw [Set.uIcc_of_le hyb] at hv
        change |y-v|=v-y
        rw [abs_of_nonpos (sub_nonpos.mpr hv.1)]
        ring
      _ = _ := by
        rw [intervalIntegral.integral_sub (f := fun v : ℝ => v) (g := fun v : ℝ => y)
          (continuous_id.intervalIntegrable y b) intervalIntegrable_const,
          integral_id,intervalIntegral.integral_const]
        simp only [smul_eq_mul]
        ring
  rw [← integral_add_adjacent_intervals (f := fun v : ℝ => |y-v|)
    ((continuous_const.sub continuous_id).abs.intervalIntegrable a y)
    ((continuous_const.sub continuous_id).abs.intervalIntegrable y b),hl,hr]
  ring

/-- The unnormalized double-distance integral over the two triangles. -/
theorem double_integral_abs_sub (a b : ℝ) (hab : a≤b) :
    (∫ y in a..b,∫ v in a..b,|y-v|)=(b-a)^3/3 := by
  have he : (∫ y in a..b,∫ v in a..b,|y-v|)=
      ∫ y in a..b,((y-a)^2+(b-y)^2)/2 := by
    apply integral_congr
    intro y hy
    rw [Set.uIcc_of_le hab] at hy
    exact integral_abs_sub a b y hy.1 hy.2
  rw [he]
  have hp : (fun y : ℝ => ((y-a)^2+(b-y)^2)/2)=
      (fun y => y^2-(a+b)*y+(a^2+b^2)/2) := by funext y;ring
  have hs : IntervalIntegrable (fun y : ℝ => y^2) volume a b :=
    (continuous_id.pow 2).intervalIntegrable a b
  have ht : IntervalIntegrable (fun y : ℝ => (a+b)*y) volume a b :=
    (continuous_const.mul continuous_id).intervalIntegrable a b
  rw [hp,intervalIntegral.integral_add (hs.sub ht) intervalIntegrable_const,
    intervalIntegral.integral_sub hs ht,integral_pow,intervalIntegral.integral_const_mul,
    integral_id,intervalIntegral.integral_const]
  simp only [smul_eq_mul]
  ring

/-- Two independent uniform points have expected separation width/3. -/
theorem uniform_double_distance (a b : ℝ) (hab : a<b) :
    (∫ y,∫ v,dist y v∂AveragedCongruence.uniformInterval a b
      ∂AveragedCongruence.uniformInterval a b)=(b-a)/3 := by
  simp_rw [Real.dist_eq,AveragedCongruence.integral_uniformInterval hab]
  rw [intervalIntegral.integral_const_mul,double_integral_abs_sub a b hab.le]
  field_simp [ne_of_gt (sub_pos.mpr hab)]

/-- The original uniform reference restricted to an interior cell is exactly
half Lebesgue measure on that cell. -/
theorem uniform_restrict_cell (a b : ℝ) (ha : -1≤a) (hb : b≤1) :
    UniformIntervalMoments.measure.restrict (Set.Ioc a b)=
      (2:ℝ≥0∞)⁻¹ • volume.restrict (Set.Ioc a b) := by
  have hsub : Set.Ioc a b⊆Set.Ioc (-1 : ℝ) 1 :=
    fun _ h => ⟨lt_of_le_of_lt ha h.1,le_trans h.2 hb⟩
  unfold UniformIntervalMoments.measure AveragedCongruence.uniformInterval ProbabilityTheory.cond
  rw [Measure.restrict_smul,Measure.restrict_restrict_of_subset hsub,Real.volume_Ioc]
  norm_num

theorem uniform_cell_integral (a b : ℝ) (ha : -1≤a) (hb : b≤1) (hab : a≤b)
    (f : ℝ → ℝ) :
    (∫ y in Set.Ioc a b,f y∂UniformIntervalMoments.measure)=
      (1/2:ℝ)*∫ y in a..b,f y := by
  rw [uniform_restrict_cell a b ha hb,MeasureTheory.integral_smul_measure,
    ← intervalIntegral.integral_of_le hab]
  norm_num

theorem uniform_cell_mass (a b : ℝ) (ha : -1≤a) (hb : b≤1) (hab : a≤b) :
    UniformIntervalMoments.measure.real (Set.Ioc a b)=(b-a)/2 := by
  have h := uniform_cell_integral a b ha hb hab (fun _ => 1)
  simpa [intervalIntegral.integral_const,smul_eq_mul,div_eq_mul_inv,mul_comm] using h

/-- The double cell integral under du/2 is width cubed over twelve. -/
theorem uniform_cell_double_distance (a b : ℝ) (ha : -1≤a) (hb : b≤1) (hab : a≤b) :
    (∫ y in Set.Ioc a b,∫ v in Set.Ioc a b,dist y v∂UniformIntervalMoments.measure
      ∂UniformIntervalMoments.measure)=(b-a)^3/12 := by
  rw [uniform_cell_integral a b ha hb hab]
  simp_rw [uniform_cell_integral a b ha hb hab,Real.dist_eq]
  rw [intervalIntegral.integral_const_mul,double_integral_abs_sub a b hab]
  ring

end Komorebi.LSM.CellDistance
