import AVOC.ArchiveReplay
import AVOC.Retrospective

namespace Komorebi.AVOC

/-- Durable one-factor archive for evidence favoring `true`. -/
def retrospectiveTrueFactor : LikelihoodFactor Bool where
  weight := retrospectiveLikelihoodTrue
  nonneg := retrospectiveLikelihoodTrue_nonneg

/-- Durable one-factor archive for evidence favoring `false`. -/
def retrospectiveFalseFactor : LikelihoodFactor Bool where
  weight := retrospectiveLikelihoodFalse
  nonneg := retrospectiveLikelihoodFalse_nonneg

abbrev retrospectiveTrueArchive : List (LikelihoodFactor Bool) := [retrospectiveTrueFactor]
abbrev retrospectiveFalseArchive : List (LikelihoodFactor Bool) := [retrospectiveFalseFactor]


theorem retrospectiveTrueArchive_likelihood :
    archiveLikelihood retrospectiveTrueArchive = retrospectiveLikelihoodTrue := by
  funext ω
  simp [retrospectiveTrueFactor, archiveLikelihood]

theorem retrospectiveFalseArchive_likelihood :
    archiveLikelihood retrospectiveFalseArchive = retrospectiveLikelihoodFalse := by
  funext ω
  simp [retrospectiveFalseFactor, archiveLikelihood]

theorem retrospectiveTrueArchive_mass :
    archiveEvidenceMass uniformBoolBelief retrospectiveTrueArchive = 5 := by
  unfold archiveEvidenceMass
  rw [retrospectiveTrueArchive_likelihood]
  exact retrospectiveLikelihoodTrue_mass

theorem retrospectiveFalseArchive_mass :
    archiveEvidenceMass uniformBoolBelief retrospectiveFalseArchive = 5 := by
  unfold archiveEvidenceMass
  rw [retrospectiveFalseArchive_likelihood]
  exact retrospectiveLikelihoodFalse_mass

theorem retrospectiveTrueArchive_positive :
    0 < archiveEvidenceMass uniformBoolBelief retrospectiveTrueArchive := by
  rw [retrospectiveTrueArchive_mass]
  norm_num

theorem retrospectiveFalseArchive_positive :
    0 < archiveEvidenceMass uniformBoolBelief retrospectiveFalseArchive := by
  rw [retrospectiveFalseArchive_mass]
  norm_num

/-- Replay of the durable true-favoring archive recovers the same fine posterior
as direct conditioning. -/
theorem replay_retrospectiveTrueArchive :
    replayArchive uniformBoolBelief retrospectiveTrueArchive
        retrospectiveTrueArchive_positive =
      conditionByWeight uniformBoolBelief retrospectiveLikelihoodTrue
        retrospectiveLikelihoodTrue_nonneg retrospectiveLikelihoodTrue_positive := by
  unfold replayArchive
  exact conditionByWeight_congr_likelihood uniformBoolBelief
    (archiveLikelihood retrospectiveTrueArchive) retrospectiveLikelihoodTrue
    (archiveLikelihood_nonneg retrospectiveTrueArchive) retrospectiveLikelihoodTrue_nonneg
    retrospectiveTrueArchive_likelihood retrospectiveTrueArchive_positive
    retrospectiveLikelihoodTrue_positive

/-- Replay of the durable false-favoring archive recovers the direct fine posterior. -/
theorem replay_retrospectiveFalseArchive :
    replayArchive uniformBoolBelief retrospectiveFalseArchive
        retrospectiveFalseArchive_positive =
      conditionByWeight uniformBoolBelief retrospectiveLikelihoodFalse
        retrospectiveLikelihoodFalse_nonneg retrospectiveLikelihoodFalse_positive := by
  unfold replayArchive
  exact conditionByWeight_congr_likelihood uniformBoolBelief
    (archiveLikelihood retrospectiveFalseArchive) retrospectiveLikelihoodFalse
    (archiveLikelihood_nonneg retrospectiveFalseArchive) retrospectiveLikelihoodFalse_nonneg
    retrospectiveFalseArchive_likelihood retrospectiveFalseArchive_positive
    retrospectiveLikelihoodFalse_positive

/-- The two replayed fine posteriors remain distinguishable. -/
theorem retrospectiveArchiveFineReplay_ne :
    replayArchive uniformBoolBelief retrospectiveTrueArchive
        retrospectiveTrueArchive_positive ≠
      replayArchive uniformBoolBelief retrospectiveFalseArchive
        retrospectiveFalseArchive_positive := by
  rw [replay_retrospectiveTrueArchive, replay_retrospectiveFalseArchive]
  exact retrospectiveFinePosteriors_ne

/-- At the old one-cell working resolution, both archive replays collapse to the
same posterior. -/
theorem retrospectiveArchiveCoarseReplay_eq :
    replayAtResolution (fun _ : Bool => ()) uniformBoolBelief retrospectiveTrueArchive
        retrospectiveTrueArchive_positive =
      replayAtResolution (fun _ : Bool => ()) uniformBoolBelief retrospectiveFalseArchive
        retrospectiveFalseArchive_positive := by
  unfold replayAtResolution
  rw [replay_retrospectiveTrueArchive, replay_retrospectiveFalseArchive]
  exact retrospectiveCoarsePosteriors_eq

/-- Replaying the richer archive after refinement recovers 9/10 mass on `true`. -/
theorem retrospectiveTrueArchive_recovers_refined_true :
    (replayArchive uniformBoolBelief retrospectiveTrueArchive
      retrospectiveTrueArchive_positive).prob true = 9 / 10 := by
  rw [replay_retrospectiveTrueArchive]
  exact retrospectivePosteriorTrue_true

/-- The alternate archive recovers 1/10 mass on `true`, despite having had the
same old one-cell working posterior. -/
theorem retrospectiveFalseArchive_recovers_refined_true :
    (replayArchive uniformBoolBelief retrospectiveFalseArchive
      retrospectiveFalseArchive_positive).prob true = 1 / 10 := by
  rw [replay_retrospectiveFalseArchive]
  exact retrospectivePosteriorFalse_true


/-- The archival/working-memory separation in one statement: the old coarse
working posterior is identical, while the durable archives replay to distinct
fine posteriors. -/
theorem retrospective_archive_preserves_lost_distinction :
    replayAtResolution (fun _ : Bool => ()) uniformBoolBelief retrospectiveTrueArchive
        retrospectiveTrueArchive_positive =
      replayAtResolution (fun _ : Bool => ()) uniformBoolBelief retrospectiveFalseArchive
        retrospectiveFalseArchive_positive ∧
    replayArchive uniformBoolBelief retrospectiveTrueArchive
        retrospectiveTrueArchive_positive ≠
      replayArchive uniformBoolBelief retrospectiveFalseArchive
        retrospectiveFalseArchive_positive := by
  exact ⟨retrospectiveArchiveCoarseReplay_eq, retrospectiveArchiveFineReplay_ne⟩

end Komorebi.AVOC
