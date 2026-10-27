import AVOC.QRateDistortionFinite
import Mathlib.Data.Finset.Max
import Mathlib.Tactic.Linarith

namespace Komorebi.AVOC

universe u v w

/-- Scalar maximum extracted from a finite nonempty action-value signature. -/
noncomputable def qSignatureMax
    {S : Type u} {A : Type v} [Fintype A] [Nonempty A]
    (Q : S → A → ℚ) (s : S) : ℚ :=
  (Finset.univ.image (Q s)).max' (Finset.univ_nonempty.image _)

/-- Some action realizes the scalar signature maximum. -/
theorem qSignatureMax_action_exists
    {S : Type u} {A : Type v} [Fintype A] [Nonempty A]
    (Q : S → A → ℚ) (s : S) :
    ∃ a : A, qSignatureMax Q s = Q s a := by
  classical
  let vals := Finset.univ.image (Q s)
  have hne : vals.Nonempty := Finset.univ_nonempty.image _
  have hmem : vals.max' hne ∈ vals := vals.max'_mem hne
  rcases Finset.mem_image.mp hmem with ⟨a, -, ha⟩
  refine ⟨a, ?_⟩
  simp [qSignatureMax, vals, ha]

/-- Every action coordinate lies below the signature maximum. -/
theorem q_le_qSignatureMax
    {S : Type u} {A : Type v} [Fintype A] [Nonempty A]
    (Q : S → A → ℚ) (s : S) (a : A) :
    Q s a ≤ qSignatureMax Q s := by
  classical
  unfold qSignatureMax
  exact Finset.le_max' _ _ (Finset.mem_image.mpr ⟨a, by simp, rfl⟩)

/-- Coordinate-wise `η`-accuracy implies scalar-max `η`-accuracy. -/
theorem qSignatureApproximation_implies_maxValueApproximation
    {S : Type u} {A : Type v} [Fintype A] [Nonempty A]
    {Z : Type w}
    (φ : S → Z) (Q : S → A → ℚ) (Qbar : Z → A → ℚ) (η : ℚ)
    (h : QSignatureApproximation φ Q Qbar η) :
    ValueApproximation φ (qSignatureMax Q) (qSignatureMax Qbar) η := by
  intro s
  obtain ⟨aRaw, hRaw⟩ := qSignatureMax_action_exists Q s
  obtain ⟨aAbs, hAbs⟩ := qSignatureMax_action_exists Qbar (φ s)
  have hRawApprox := h s aRaw
  have hAbsApprox := h s aAbs
  have hRawBar : Qbar (φ s) aRaw ≤ qSignatureMax Qbar (φ s) :=
    q_le_qSignatureMax Qbar (φ s) aRaw
  have hAbsRaw : Q s aAbs ≤ qSignatureMax Q s :=
    q_le_qSignatureMax Q s aAbs
  rw [abs_le]
  rw [abs_le] at hRawApprox hAbsApprox
  constructor <;> linarith

/-- Exact finite Q-signature context complexity is always at least the exact
scalar-max context complexity at the same tolerance. -/
theorem exactValueCodeNumber_le_exactQCodeNumber
    {S : Type u} [Fintype S]
    {A : Type v} [Fintype A] [DecidableEq A] [Nonempty A]
    (Q : S → A → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    exactValueCodeNumber (qSignatureMax Q) η hη ≤
      exactQCodeNumber Q η hη := by
  obtain ⟨C, hcard, φ, hq⟩ := exactQCodeNumber_attained_by_context Q η hη
  have hv : ValueApproximation φ (qSignatureMax Q)
      (qSignatureMax (fun z : {c // c ∈ C} => (z : A → ℚ))) η :=
    qSignatureApproximation_implies_maxValueApproximation φ Q
      (fun z : {c // c ∈ C} => (z : A → ℚ)) η hq
  have hle := exactValueCodeNumber_le_finite_code_card φ
    (qSignatureMax Q)
    (qSignatureMax (fun z : {c // c ∈ C} => (z : A → ℚ))) η hη hv
  simpa [hcard] using hle

/-- At zero distortion, the scalar optimum may collapse states that exact
Q-signature preservation must distinguish; equality is not automatic. -/
theorem exact_scalar_context_never_richer_than_q_context
    {S : Type u} [Fintype S]
    {A : Type v} [Fintype A] [DecidableEq A] [Nonempty A]
    (Q : S → A → ℚ) :
    exactValueCodeNumber (qSignatureMax Q) 0 (by norm_num) ≤
      exactQCodeNumber Q 0 (by norm_num) := by
  exact exactValueCodeNumber_le_exactQCodeNumber Q 0 (by norm_num)

end Komorebi.AVOC
