import AVOC.BayesianObservationTransport
import Mathlib.Data.Finset.Max

namespace Komorebi.AVOC

variable {Ω : Type*} [Fintype Ω]

/-- A finite linear expected-utility row. -/
def beliefRowValue (v : Ω → ℚ) (b : RationalBelief Ω) : ℚ := ∑ w, b.prob w * v w

theorem beliefRowValue_bound (v : Ω → ℚ) (b : RationalBelief Ω) (R : ℚ)
    (hv : ∀ w, |v w| ≤ R) : |beliefRowValue v b| ≤ R := by
  calc
    _ ≤ ∑ w, |b.prob w * v w| := Finset.abs_sum_le_sum_abs _ _
    _ = ∑ w, b.prob w * |v w| := by
      apply Finset.sum_congr rfl
      intro w _
      rw [abs_mul, abs_of_nonneg (b.nonneg w)]
    _ ≤ ∑ w, b.prob w * R :=
      Finset.sum_le_sum (fun w _ => mul_le_mul_of_nonneg_left (hv w) (b.nonneg w))
    _ = R := by rw [← Finset.sum_mul, b.sum_one, one_mul]

theorem beliefRowValue_lipschitz (v : Ω → ℚ) (b c : RationalBelief Ω) (R : ℚ)
    (hv : ∀ w, |v w| ≤ R) :
    |beliefRowValue v b - beliefRowValue v c| ≤ R * beliefL1Distance b c := by
  calc
    _ ≤ ∑ w, |b.prob w * v w - c.prob w * v w| :=
      abs_sum_sub_sum_le_sum_abs_sub _ _
    _ = ∑ w, |b.prob w - c.prob w| * |v w| := by
      apply Finset.sum_congr rfl
      intro w _
      rw [← sub_mul, abs_mul]
    _ ≤ ∑ w, |b.prob w - c.prob w| * R :=
      Finset.sum_le_sum (fun w _ => mul_le_mul_of_nonneg_left (hv w) (abs_nonneg _))
    _ = R * beliefL1Distance b c := by rw [← Finset.sum_mul]; unfold beliefL1Distance; ring

/-- Finite maxima of linear belief rows provide explicitly certifiable bounded,
Lipschitz continuation tables. This is not a universal claim about LLM values. -/
noncomputable def beliefTableValue (rows : Finset (Ω → ℚ)) (hne : rows.Nonempty)
    (b : RationalBelief Ω) : ℚ :=
  (rows.image (fun v => beliefRowValue v b)).max' (hne.image _)

theorem beliefRowValue_le_table (rows : Finset (Ω → ℚ)) (hne : rows.Nonempty)
    (b : RationalBelief Ω) (v : Ω → ℚ) (hv : v ∈ rows) :
    beliefRowValue v b ≤ beliefTableValue rows hne b := by
  unfold beliefTableValue
  exact Finset.le_max' (rows.image (fun w => beliefRowValue w b)) (beliefRowValue v b)
    (Finset.mem_image.mpr ⟨v, hv, rfl⟩)

theorem beliefTableValue_attained (rows : Finset (Ω → ℚ)) (hne : rows.Nonempty)
    (b : RationalBelief Ω) :
    ∃ v ∈ rows, beliefTableValue rows hne b = beliefRowValue v b := by
  have ht : beliefTableValue rows hne b ∈ rows.image (fun v => beliefRowValue v b) :=
    Finset.max'_mem _ _
  obtain ⟨v, hv, he⟩ := Finset.mem_image.mp ht
  exact ⟨v, hv, he.symm⟩

theorem beliefTableValue_bound (rows : Finset (Ω → ℚ)) (hne : rows.Nonempty)
    (R : ℚ) (hv : ∀ v ∈ rows, ∀ w, |v w| ≤ R) (b : RationalBelief Ω) :
    |beliefTableValue rows hne b| ≤ R := by
  obtain ⟨v, hm, he⟩ := beliefTableValue_attained rows hne b
  rw [he]
  exact beliefRowValue_bound v b R (hv v hm)

theorem beliefTableValue_lipschitz (rows : Finset (Ω → ℚ)) (hne : rows.Nonempty)
    (R : ℚ) (hv : ∀ v ∈ rows, ∀ w, |v w| ≤ R) (b c : RationalBelief Ω) :
    |beliefTableValue rows hne b - beliefTableValue rows hne c| ≤ R * beliefL1Distance b c := by
  obtain ⟨v, hvb, heb⟩ := beliefTableValue_attained rows hne b
  obtain ⟨w, hwc, hec⟩ := beliefTableValue_attained rows hne c
  have hvmax := beliefRowValue_le_table rows hne c v hvb
  have hwmax := beliefRowValue_le_table rows hne b w hwc
  have hvdiff := (abs_le.mp (beliefRowValue_lipschitz v b c R (hv v hvb))).2
  have hwdiff := (abs_le.mp (beliefRowValue_lipschitz w b c R (hv w hwc))).1
  apply abs_le.mpr
  constructor <;> linarith

end Komorebi.AVOC
