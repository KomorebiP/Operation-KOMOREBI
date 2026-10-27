import AVOC.HistoryState
import AVOC.OpenWorld
import AVOC.BayesianEvidence
import Mathlib.Tactic.Ring
import Mathlib.Tactic.Linarith

namespace Komorebi.AVOC

universe u v

/-- A durable likelihood contribution stored in archival memory. -/
structure LikelihoodFactor (Ω : Type u) where
  weight : Ω → ℚ
  nonneg : ∀ ω, 0 ≤ weight ω

/-- The cumulative likelihood carried by an archive of evidence factors. -/
def archiveLikelihood {Ω : Type u} : List (LikelihoodFactor Ω) → Ω → ℚ
  | [], _ => 1
  | f :: fs, ω => f.weight ω * archiveLikelihood fs ω

/-- Archived likelihood products remain nonnegative. -/
theorem archiveLikelihood_nonneg
    {Ω : Type u} (fs : List (LikelihoodFactor Ω)) :
    ∀ ω, 0 ≤ archiveLikelihood fs ω := by
  induction fs with
  | nil =>
      intro ω
      simp [archiveLikelihood]
  | cons f fs ih =>
      intro ω
      simp only [archiveLikelihood]
      exact mul_nonneg (f.nonneg ω) (ih ω)

@[simp] theorem archiveLikelihood_nil
    {Ω : Type u} (ω : Ω) : archiveLikelihood ([] : List (LikelihoodFactor Ω)) ω = 1 := by
  rfl

/-- Concatenating two evidence archives multiplies their cumulative likelihoods. -/
theorem archiveLikelihood_append
    {Ω : Type u} (xs ys : List (LikelihoodFactor Ω)) (ω : Ω) :
    archiveLikelihood (xs ++ ys) ω =
      archiveLikelihood xs ω * archiveLikelihood ys ω := by
  induction xs with
  | nil => simp [archiveLikelihood]
  | cons f xs ih =>
      simp [archiveLikelihood, ih, mul_assoc]

/-- Evidence mass of a durable likelihood archive under an initial belief. -/
def archiveEvidenceMass
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω) (fs : List (LikelihoodFactor Ω)) : ℚ :=
  evidenceMass b (archiveLikelihood fs)

/-- Empty archival evidence has unit mass. -/
theorem archiveEvidenceMass_nil
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω) :
    archiveEvidenceMass b [] = 1 := by
  unfold archiveEvidenceMass evidenceMass
  simpa [archiveLikelihood] using b.sum_one

/-- Replay all archived likelihood contributions against the fine initial belief. -/
def replayArchive
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω) (fs : List (LikelihoodFactor Ω))
    (hpos : 0 < archiveEvidenceMass b fs) : RationalBelief Ω :=
  conditionByWeight b (archiveLikelihood fs)
    (archiveLikelihood_nonneg fs) hpos

/-- Empty replay returns the initial belief exactly. -/
theorem replayArchive_nil
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω) :
    replayArchive b [] (by rw [archiveEvidenceMass_nil]; norm_num) = b := by
  apply RationalBelief.ext
  intro ω
  unfold replayArchive conditionByWeight archiveEvidenceMass evidenceMass
  simp [archiveLikelihood, b.sum_one]

/-- The combined evidence mass factors into the first archive mass times the
conditional mass of the second archive. -/
theorem archiveEvidenceMass_append_factor
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω)
    (xs ys : List (LikelihoodFactor Ω))
    (hx : 0 < archiveEvidenceMass b xs) :
    archiveEvidenceMass b (xs ++ ys) =
      archiveEvidenceMass b xs *
        evidenceMass (replayArchive b xs hx) (archiveLikelihood ys) := by
  unfold archiveEvidenceMass replayArchive
  rw [show archiveLikelihood (xs ++ ys) =
      fun ω => archiveLikelihood xs ω * archiveLikelihood ys ω by
        funext ω
        exact archiveLikelihood_append xs ys ω]
  exact (evidenceMass_condition_compose b
    (archiveLikelihood xs) (archiveLikelihood ys)
    (archiveLikelihood_nonneg xs) (archiveLikelihood_nonneg ys) hx).symm

/-- Positive evidence for an archive prefix and then a suffix implies positive
mass for the concatenated archive. -/
theorem archiveEvidenceMass_append_pos
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω)
    (xs ys : List (LikelihoodFactor Ω))
    (hx : 0 < archiveEvidenceMass b xs)
    (hy : 0 < evidenceMass (replayArchive b xs hx) (archiveLikelihood ys)) :
    0 < archiveEvidenceMass b (xs ++ ys) := by
  rw [archiveEvidenceMass_append_factor b xs ys hx]
  exact mul_pos hx hy

/-- **Archive replay composition.** Replaying a concatenated archive is exactly
sequential conditioning by its two cumulative likelihood blocks. -/
theorem replayArchive_append
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω)
    (xs ys : List (LikelihoodFactor Ω))
    (hx : 0 < archiveEvidenceMass b xs)
    (hy : 0 < evidenceMass (replayArchive b xs hx) (archiveLikelihood ys)) :
    replayArchive b (xs ++ ys) (archiveEvidenceMass_append_pos b xs ys hx hy) =
      conditionByWeight (replayArchive b xs hx) (archiveLikelihood ys)
        (archiveLikelihood_nonneg ys) hy := by
  let hxy := archiveEvidenceMass_append_pos b xs ys hx hy
  let left := replayArchive b (xs ++ ys) hxy
  let right := conditionByWeight (replayArchive b xs hx) (archiveLikelihood ys)
    (archiveLikelihood_nonneg ys) hy
  apply RationalBelief.ext
  intro ω
  apply mul_right_cancel₀ (ne_of_gt hxy)
  change left.prob ω * archiveEvidenceMass b (xs ++ ys) =
    right.prob ω * archiveEvidenceMass b (xs ++ ys)
  have hleft := conditionByWeight_mul_evidence b (archiveLikelihood (xs ++ ys))
    (archiveLikelihood_nonneg (xs ++ ys)) hxy ω
  have hright := conditionByWeight_mul_evidence (replayArchive b xs hx)
    (archiveLikelihood ys) (archiveLikelihood_nonneg ys) hy ω
  have hprefix := conditionByWeight_mul_evidence b (archiveLikelihood xs)
    (archiveLikelihood_nonneg xs) hx ω
  have hmass := archiveEvidenceMass_append_factor b xs ys hx
  have hL := archiveLikelihood_append xs ys ω
  change
    (replayArchive b (xs ++ ys) hxy).prob ω * archiveEvidenceMass b (xs ++ ys) =
      (conditionByWeight (replayArchive b xs hx) (archiveLikelihood ys)
        (archiveLikelihood_nonneg ys) hy).prob ω * archiveEvidenceMass b (xs ++ ys)
  calc
    (replayArchive b (xs ++ ys) hxy).prob ω * archiveEvidenceMass b (xs ++ ys)
        = b.prob ω * archiveLikelihood (xs ++ ys) ω := by
            simpa [replayArchive, archiveEvidenceMass] using hleft
    _ = (b.prob ω * archiveLikelihood xs ω) * archiveLikelihood ys ω := by
          rw [hL, mul_assoc]
    _ = ((replayArchive b xs hx).prob ω * archiveEvidenceMass b xs) *
          archiveLikelihood ys ω := by
          rw [show (replayArchive b xs hx).prob ω * archiveEvidenceMass b xs =
            b.prob ω * archiveLikelihood xs ω by
              simpa [replayArchive, archiveEvidenceMass] using hprefix]
    _ = ((replayArchive b xs hx).prob ω * archiveLikelihood ys ω) *
          archiveEvidenceMass b xs := by ring
    _ = ((conditionByWeight (replayArchive b xs hx) (archiveLikelihood ys)
          (archiveLikelihood_nonneg ys) hy).prob ω *
            evidenceMass (replayArchive b xs hx) (archiveLikelihood ys)) *
          archiveEvidenceMass b xs := by
          rw [hright]
    _ = (conditionByWeight (replayArchive b xs hx) (archiveLikelihood ys)
          (archiveLikelihood_nonneg ys) hy).prob ω *
          (archiveEvidenceMass b xs *
            evidenceMass (replayArchive b xs hx) (archiveLikelihood ys)) := by ring
    _ = (conditionByWeight (replayArchive b xs hx) (archiveLikelihood ys)
          (archiveLikelihood_nonneg ys) hy).prob ω * archiveEvidenceMass b (xs ++ ys) := by
          rw [hmass]


/-- Conditioning is insensitive to proof transport along equality of the prior
belief.  This lemma is useful when replay equality appears inside the type of a
positive-evidence certificate. -/
theorem conditionByWeight_congr_belief
    {Ω : Type u} [Fintype Ω]
    (b c : RationalBelief Ω) (L : Ω → ℚ)
    (hL : ∀ ω, 0 ≤ L ω)
    (hb : b = c)
    (hpb : 0 < evidenceMass b L)
    (hpc : 0 < evidenceMass c L) :
    conditionByWeight b L hL hpb = conditionByWeight c L hL hpc := by
  subst c
  rfl

/-- Conditioning is insensitive to proof transport along pointwise equality of
likelihood functions. -/
theorem conditionByWeight_congr_likelihood
    {Ω : Type u} [Fintype Ω]
    (b : RationalBelief Ω) (L M : Ω → ℚ)
    (hL : ∀ ω, 0 ≤ L ω) (hM : ∀ ω, 0 ≤ M ω)
    (hLM : L = M)
    (hpL : 0 < evidenceMass b L)
    (hpM : 0 < evidenceMass b M) :
    conditionByWeight b L hL hpL = conditionByWeight b M hM hpM := by
  subst M
  rfl

/-- Replay at an arbitrary later hypothesis resolution is simply deterministic
pushforward of the fine replayed posterior.  The archive itself remains at the
fine resolution. -/
def replayAtResolution
    {Ω : Type u} {Z : Type v}
    [Fintype Ω] [Fintype Z] [DecidableEq Z]
    (φ : Ω → Z)
    (b : RationalBelief Ω) (fs : List (LikelihoodFactor Ω))
    (hpos : 0 < archiveEvidenceMass b fs) : RationalBelief Z :=
  pushforwardBelief φ (replayArchive b fs hpos)

/-- Replaying at two nested resolutions commutes with deterministic decoding. -/
theorem replayAtResolution_comp
    {Ω : Type u} {Y : Type v} {Z : Type*}
    [Fintype Ω] [Fintype Y] [Fintype Z]
    [DecidableEq Y] [DecidableEq Z]
    (φ : Ω → Y) (ψ : Y → Z)
    (b : RationalBelief Ω) (fs : List (LikelihoodFactor Ω))
    (hpos : 0 < archiveEvidenceMass b fs) :
    pushforwardBelief ψ (replayAtResolution φ b fs hpos) =
      replayAtResolution (ψ ∘ φ) b fs hpos := by
  unfold replayAtResolution
  exact pushforwardBelief_comp φ ψ (replayArchive b fs hpos)

/-- A replay-complete fine archive can answer any later deterministic resolution
without changing the stored evidence factors. -/
theorem replay_resolution_is_pushforward
    {Ω : Type u} {Z : Type v}
    [Fintype Ω] [Fintype Z] [DecidableEq Z]
    (φ : Ω → Z)
    (b : RationalBelief Ω) (fs : List (LikelihoodFactor Ω))
    (hpos : 0 < archiveEvidenceMass b fs) :
    replayAtResolution φ b fs hpos =
      pushforwardBelief φ (replayArchive b fs hpos) := by
  rfl

end Komorebi.AVOC
