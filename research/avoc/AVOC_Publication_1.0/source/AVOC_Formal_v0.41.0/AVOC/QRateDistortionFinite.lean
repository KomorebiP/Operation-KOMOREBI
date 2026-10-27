import AVOC.QRateDistortion
import Mathlib.Data.Finset.Card
import Mathlib.Tactic.Linarith

namespace Komorebi.AVOC

universe u v w

/-- A finite set of complete action-value signatures covers all raw Q-vectors
to coordinate tolerance `η`. -/
def QCenterCover
    {S : Type u} {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (η : ℚ) (C : Finset (A → ℚ)) : Prop :=
  ∀ s, ∃ c ∈ C, ∀ a, |Q s a - c a| ≤ η

/-- The decoded signatures used by a finite code form a Q-center cover. -/
theorem qCenterCover_of_qSignatureApproximation
    {S : Type u} {A : Type v} [Fintype A] [DecidableEq A]
    {Z : Type w} [Fintype Z] [DecidableEq Z]
    (φ : S → Z) (Q : S → A → ℚ) (Qbar : Z → A → ℚ) (η : ℚ)
    (h : QSignatureApproximation φ Q Qbar η) :
    QCenterCover Q η (Finset.univ.image Qbar) := by
  classical
  intro s
  refine ⟨Qbar (φ s), ?_, ?_⟩
  · simp
  · intro a
    exact h s a

/-- A finite Q-code contributes no more distinct decoded signatures than codes. -/
theorem q_decoder_center_card_le_code_card
    {A : Type v} [Fintype A] [DecidableEq A] {Z : Type w} [Fintype Z] [DecidableEq Z]
    (Qbar : Z → A → ℚ) :
    (Finset.univ.image Qbar).card ≤ Fintype.card Z := by
  classical
  simpa using Finset.card_image_le (s := (Finset.univ : Finset Z)) (f := Qbar)

/-- Every finite accurate Q-code induces a signature cover of no larger cardinality. -/
theorem finite_q_code_gives_center_cover_card_bound
    {S : Type u} {A : Type v} [Fintype A] [DecidableEq A]
    {Z : Type w} [Fintype Z] [DecidableEq Z]
    (φ : S → Z) (Q : S → A → ℚ) (Qbar : Z → A → ℚ) (η : ℚ)
    (h : QSignatureApproximation φ Q Qbar η) :
    ∃ C : Finset (A → ℚ),
      QCenterCover Q η C ∧ C.card ≤ Fintype.card Z := by
  classical
  refine ⟨Finset.univ.image Qbar,
    qCenterCover_of_qSignatureApproximation φ Q Qbar η h,
    q_decoder_center_card_le_code_card Qbar⟩

/-- Chosen signature center realizing a finite Q-cover. -/
noncomputable def chosenQCoverCenter
    {S : Type u} {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (η : ℚ) (C : Finset (A → ℚ))
    (hcover : QCenterCover Q η C) (s : S) : A → ℚ :=
  Classical.choose (hcover s)

/-- The chosen Q-center belongs to its cover. -/
theorem chosenQCoverCenter_mem
    {S : Type u} {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (η : ℚ) (C : Finset (A → ℚ))
    (hcover : QCenterCover Q η C) (s : S) :
    chosenQCoverCenter Q η C hcover s ∈ C :=
  (Classical.choose_spec (hcover s)).1

/-- The chosen Q-center approximates every action coordinate. -/
theorem chosenQCoverCenter_accurate
    {S : Type u} {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (η : ℚ) (C : Finset (A → ℚ))
    (hcover : QCenterCover Q η C) (s : S) (a : A) :
    |Q s a - chosenQCoverCenter Q η C hcover s a| ≤ η :=
  (Classical.choose_spec (hcover s)).2 a

/-- Every finite Q-signature center cover is itself an accurate context code. -/
theorem q_center_cover_gives_finite_code
    {S : Type u} {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (η : ℚ) (C : Finset (A → ℚ))
    (hcover : QCenterCover Q η C) :
    ∃ φ : S → {c // c ∈ C},
      QSignatureApproximation φ Q
        (fun z : {c // c ∈ C} => (z : A → ℚ)) η := by
  let φ : S → {c // c ∈ C} := fun s =>
    ⟨chosenQCoverCenter Q η C hcover s,
      chosenQCoverCenter_mem Q η C hcover s⟩
  refine ⟨φ, ?_⟩
  intro s a
  simpa [φ] using chosenQCoverCenter_accurate Q η C hcover s a

/-- The Q-center-code subtype has exactly the cover cardinality. -/
theorem q_center_code_card_eq
    {A : Type v} [Fintype A] [DecidableEq A] (C : Finset (A → ℚ)) :
    Fintype.card {c // c ∈ C} = C.card := by
  simp

/-- Q-code / Q-center-cover cardinality duality. -/
theorem finite_q_code_center_cover_cardinality_duality
    {S : Type u} {A : Type v} [Fintype A] [DecidableEq A]
    {Z : Type w} [Fintype Z] [DecidableEq Z]
    (φ : S → Z) (Q : S → A → ℚ) (Qbar : Z → A → ℚ) (η : ℚ)
    (h : QSignatureApproximation φ Q Qbar η) :
    ∃ C : Finset (A → ℚ),
      QCenterCover Q η C ∧
      C.card ≤ Fintype.card Z ∧
      ∃ ψ : S → {c // c ∈ C},
        QSignatureApproximation ψ Q
          (fun z : {c // c ∈ C} => (z : A → ℚ)) η := by
  obtain ⟨C, hcover, hcard⟩ :=
    finite_q_code_gives_center_cover_card_bound φ Q Qbar η h
  obtain ⟨ψ, hψ⟩ := q_center_cover_gives_finite_code Q η C hcover
  exact ⟨C, hcover, hcard, ψ, hψ⟩

/-- A finite Q-center cover with exactly `k` signatures. -/
def HasQCenterCoverCard
    {S : Type u} {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (η : ℚ) (k : ℕ) : Prop :=
  ∃ C : Finset (A → ℚ), QCenterCover Q η C ∧ C.card = k

/-- The finite set of raw Q-signatures covers itself at every nonnegative tolerance. -/
theorem raw_q_image_is_centerCover
    {S : Type u} [Fintype S] {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    QCenterCover Q η (Finset.univ.image Q) := by
  classical
  intro s
  refine ⟨Q s, by simp, ?_⟩
  intro a
  simpa using hη

/-- Every finite Q-signature problem has some finite cover cardinality. -/
theorem exists_qCenterCover_card
    {S : Type u} [Fintype S] {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    ∃ k, HasQCenterCoverCard Q η k := by
  classical
  let C : Finset (A → ℚ) := Finset.univ.image Q
  refine ⟨C.card, C, ?_, rfl⟩
  simpa [C] using raw_q_image_is_centerCover Q η hη

/-- Exact minimum finite context cardinality required to reconstruct every Q
coordinate within tolerance `η`. -/
noncomputable def exactQCodeNumber
    {S : Type u} [Fintype S] {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (η : ℚ) (hη : 0 ≤ η) : ℕ := by
  classical
  exact Nat.find (exists_qCenterCover_card Q η hη)

/-- The minimum Q-center-cover cardinality is attained. -/
theorem exactQCodeNumber_spec
    {S : Type u} [Fintype S] {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    HasQCenterCoverCard Q η (exactQCodeNumber Q η hη) := by
  classical
  simpa [exactQCodeNumber] using
    (Nat.find_spec (exists_qCenterCover_card Q η hη))

/-- The exact Q-code number is no larger than any finite Q-center cover. -/
theorem exactQCodeNumber_le_cover_card
    {S : Type u} [Fintype S] {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (η : ℚ) (hη : 0 ≤ η)
    (C : Finset (A → ℚ)) (hcover : QCenterCover Q η C) :
    exactQCodeNumber Q η hη ≤ C.card := by
  classical
  unfold exactQCodeNumber
  exact Nat.find_min' (exists_qCenterCover_card Q η hη) ⟨C, hcover, rfl⟩

/-- Every finite accurate Q-context has at least the exact Q-rate-distortion
number of available symbols. -/
theorem exactQCodeNumber_le_finite_code_card
    {S : Type u} [Fintype S] {A : Type v} [Fintype A] [DecidableEq A]
    {Z : Type w} [Fintype Z] [DecidableEq Z]
    (φ : S → Z) (Q : S → A → ℚ) (Qbar : Z → A → ℚ)
    (η : ℚ) (hη : 0 ≤ η)
    (h : QSignatureApproximation φ Q Qbar η) :
    exactQCodeNumber Q η hη ≤ Fintype.card Z := by
  obtain ⟨C, hcover, hcard⟩ :=
    finite_q_code_gives_center_cover_card_bound φ Q Qbar η h
  exact (exactQCodeNumber_le_cover_card Q η hη C hcover).trans hcard

/-- The exact Q-code number is attained by a finite context. -/
theorem exactQCodeNumber_attained_by_context
    {S : Type u} [Fintype S] {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    ∃ C : Finset (A → ℚ),
      C.card = exactQCodeNumber Q η hη ∧
      ∃ φ : S → {c // c ∈ C},
        QSignatureApproximation φ Q
          (fun z : {c // c ∈ C} => (z : A → ℚ)) η := by
  obtain ⟨C, hcover, hcard⟩ := exactQCodeNumber_spec Q η hη
  obtain ⟨φ, hφ⟩ := q_center_cover_gives_finite_code Q η C hcover
  exact ⟨C, hcard, φ, hφ⟩

/-- Exact finite Q-signature rate-distortion optimality sandwich. -/
theorem exact_finite_q_rate_distortion_optimality
    {S : Type u} [Fintype S] {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (η : ℚ) (hη : 0 ≤ η) :
    (∀ {Z : Type w} [Fintype Z] [DecidableEq Z]
      (φ : S → Z) (Qbar : Z → A → ℚ),
      QSignatureApproximation φ Q Qbar η →
      exactQCodeNumber Q η hη ≤ Fintype.card Z) ∧
    (∃ C : Finset (A → ℚ),
      C.card = exactQCodeNumber Q η hη ∧
      ∃ φ : S → {c // c ∈ C},
        QSignatureApproximation φ Q
          (fun z : {c // c ∈ C} => (z : A → ℚ)) η) := by
  constructor
  · intro Z instF instD φ Qbar h
    exact exactQCodeNumber_le_finite_code_card φ Q Qbar η hη h
  · exact exactQCodeNumber_attained_by_context Q η hη

end Komorebi.AVOC

namespace Komorebi.AVOC

universe u v

/-- A Q-center cover valid at smaller tolerance remains valid at larger tolerance. -/
theorem qCenterCover_mono_tolerance
    {S : Type u} {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) {η₁ η₂ : ℚ} (hη : η₁ ≤ η₂)
    (C : Finset (A → ℚ)) (hcover : QCenterCover Q η₁ C) :
    QCenterCover Q η₂ C := by
  intro s
  obtain ⟨c, hc, hdist⟩ := hcover s
  exact ⟨c, hc, fun a => (hdist a).trans hη⟩

/-- More tolerated action-value distortion cannot increase exact Q-code number. -/
theorem exactQCodeNumber_antitone_tolerance
    {S : Type u} [Fintype S] {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) {η₁ η₂ : ℚ}
    (hη₁ : 0 ≤ η₁) (hη₂ : 0 ≤ η₂) (h12 : η₁ ≤ η₂) :
    exactQCodeNumber Q η₂ hη₂ ≤ exactQCodeNumber Q η₁ hη₁ := by
  obtain ⟨C, hcover₁, hcard⟩ := exactQCodeNumber_spec Q η₁ hη₁
  have hcover₂ := qCenterCover_mono_tolerance Q h12 C hcover₁
  calc
    exactQCodeNumber Q η₂ hη₂ ≤ C.card :=
      exactQCodeNumber_le_cover_card Q η₂ hη₂ C hcover₂
    _ = exactQCodeNumber Q η₁ hη₁ := hcard

/-- Every exact Q-cover contains every distinct raw Q-signature. -/
theorem raw_q_signatures_subset_zero_centerCover
    {S : Type u} [Fintype S] {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (C : Finset (A → ℚ))
    (hcover : QCenterCover Q 0 C) :
    Finset.univ.image Q ⊆ C := by
  classical
  intro q hq
  obtain ⟨s, -, rfl⟩ := Finset.mem_image.mp hq
  obtain ⟨c, hc, hdist⟩ := hcover s
  have heq : Q s = c := by
    funext a
    have hzero : |Q s a - c a| = 0 :=
      le_antisymm (hdist a) (abs_nonneg _)
    exact sub_eq_zero.mp (abs_eq_zero.mp hzero)
  simpa [heq] using hc

/-- Zero distortion requires exactly one symbol per distinct Q-signature. -/
theorem exactQCodeNumber_zero_eq_distinct_signature_card
    {S : Type u} [Fintype S] {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) :
    exactQCodeNumber Q 0 (by norm_num) = (Finset.univ.image Q).card := by
  classical
  apply le_antisymm
  · exact exactQCodeNumber_le_cover_card Q 0 (by norm_num)
      (Finset.univ.image Q) (raw_q_image_is_centerCover Q 0 (by norm_num))
  · obtain ⟨C, hcover, hcard⟩ := exactQCodeNumber_spec Q 0 (by norm_num)
    have hsub := raw_q_signatures_subset_zero_centerCover Q C hcover
    have hle := Finset.card_le_card hsub
    simpa [hcard] using hle

/-- Earlier pairwise Q-separation lower bounds apply directly to exact optimum. -/
theorem q_separated_card_le_exactQCodeNumber
    {S : Type u} [Fintype S] [DecidableEq S]
    {A : Type v} [Fintype A] [DecidableEq A]
    (Q : S → A → ℚ) (η : ℚ) (hη : 0 ≤ η)
    (K : Finset S) (hsep : PairwiseQSeparated Q η K) :
    K.card ≤ exactQCodeNumber Q η hη := by
  obtain ⟨C, hcard, φ, happrox⟩ :=
    exactQCodeNumber_attained_by_context Q η hη
  have h := q_separated_card_le_code_card φ Q
    (fun z : {c // c ∈ C} => (z : A → ℚ)) η K happrox hsep
  simpa [hcard] using h

end Komorebi.AVOC
