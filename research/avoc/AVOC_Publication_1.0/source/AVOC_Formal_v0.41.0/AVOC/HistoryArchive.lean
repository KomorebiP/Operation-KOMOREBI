import AVOC.ArchiveReplay
import AVOC.HistoryState

namespace Komorebi.AVOC

universe u v w z

/-- The likelihood contribution recorded by one action-observation pair. -/
def historyLikelihoodFactor
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (a : A) (o : O) : LikelihoodFactor Ω where
  weight ω := (sys.experiment a).prob ω o
  nonneg ω := (sys.experiment a).nonneg ω o

/-- Durable likelihood archive extracted from a raw research history. -/
def archiveOfHistory
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert) :
    ResearchHistory A O → List (LikelihoodFactor Ω)
  | .root => []
  | .snoc h a o => archiveOfHistory sys h ++ [historyLikelihoodFactor sys a o]

@[simp] theorem archiveOfHistory_root
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert) :
    archiveOfHistory sys (.root : ResearchHistory A O) = [] := by
  rfl

@[simp] theorem archiveOfHistory_snoc
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (h : ResearchHistory A O) (a : A) (o : O) :
    archiveOfHistory sys (.snoc h a o) =
      archiveOfHistory sys h ++ [historyLikelihoodFactor sys a o] := by
  rfl

/-- Every actually observed event in a positive history had positive predictive
mass at the belief state immediately before observing it. -/
def PositiveResearchHistory
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (init : CertifiedResearchState Ω Cert) : ResearchHistory A O → Prop
  | .root => True
  | .snoc h a o =>
      PositiveResearchHistory sys init h ∧
        0 < predictiveProb (compileHistory sys init h).belief (sys.experiment a) o

@[simp] theorem positiveResearchHistory_root
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (init : CertifiedResearchState Ω Cert) :
    PositiveResearchHistory sys init (.root : ResearchHistory A O) := by
  trivial

/-- The one-step archival likelihood is exactly the observation likelihood. -/
theorem archiveLikelihood_single_historyFactor
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (a : A) (o : O) (ω : Ω) :
    archiveLikelihood [historyLikelihoodFactor sys a o] ω =
      (sys.experiment a).prob ω o := by
  simp [archiveLikelihood, historyLikelihoodFactor]

/-- Evidence mass of a single archived history factor is the usual Bayesian
predictive probability. -/
theorem evidenceMass_single_historyFactor
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (b : RationalBelief Ω) (a : A) (o : O) :
    evidenceMass b (archiveLikelihood [historyLikelihoodFactor sys a o]) =
      predictiveProb b (sys.experiment a) o := by
  unfold evidenceMass predictiveProb
  apply Finset.sum_congr rfl
  intro ω hω
  rw [archiveLikelihood_single_historyFactor]

/-- **History/archive replay theorem.**  For a positive raw history, the durable
likelihood archive reconstructed from that history reproduces exactly the
Bayesian belief component of the compiled research state. -/
theorem positive_history_has_exact_archive_replay
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (init : CertifiedResearchState Ω Cert) :
    ∀ h : ResearchHistory A O,
      PositiveResearchHistory sys init h →
      ∃ hpos : 0 < archiveEvidenceMass init.belief (archiveOfHistory sys h),
        replayArchive init.belief (archiveOfHistory sys h) hpos =
          (compileHistory sys init h).belief := by
  intro h
  induction h with
  | root =>
      intro hp
      let hpos : 0 < archiveEvidenceMass init.belief [] := by
        rw [archiveEvidenceMass_nil]
        norm_num
      refine ⟨hpos, ?_⟩
      simpa using replayArchive_nil init.belief
  | snoc h a o ih =>
      intro hp
      rcases hp with ⟨hpref, hobs⟩
      obtain ⟨hx, hreplay⟩ := ih hpref
      let f := historyLikelihoodFactor sys a o
      have hyCompiled : 0 < evidenceMass
          (compileHistory sys init h).belief (archiveLikelihood [f]) := by
        change 0 < evidenceMass (compileHistory sys init h).belief
          (archiveLikelihood [historyLikelihoodFactor sys a o])
        rw [evidenceMass_single_historyFactor sys (compileHistory sys init h).belief a o]
        exact hobs
      have hy : 0 < evidenceMass
          (replayArchive init.belief (archiveOfHistory sys h) hx)
          (archiveLikelihood [f]) := by
        have hm := congrArg
          (fun q : RationalBelief Ω => evidenceMass q (archiveLikelihood [f])) hreplay
        rw [hm]
        exact hyCompiled
      let hwhole := archiveEvidenceMass_append_pos init.belief
        (archiveOfHistory sys h) [f] hx hy
      refine ⟨hwhole, ?_⟩
      have happ := replayArchive_append init.belief
        (archiveOfHistory sys h) [f] hx hy
      have hcond :
          conditionByWeight
              (replayArchive init.belief (archiveOfHistory sys h) hx)
              (archiveLikelihood [f]) (archiveLikelihood_nonneg [f]) hy =
            bayesUpdate (compileHistory sys init h).belief (sys.experiment a) o hobs := by
        have hb := conditionByWeight_congr_belief
          (replayArchive init.belief (archiveOfHistory sys h) hx)
          (compileHistory sys init h).belief (archiveLikelihood [f])
          (archiveLikelihood_nonneg [f]) hreplay hy hyCompiled
        have hL : archiveLikelihood [f] = fun ω => (sys.experiment a).prob ω o := by
          funext ω
          exact archiveLikelihood_single_historyFactor sys a o ω
        have hl := conditionByWeight_congr_likelihood
          (compileHistory sys init h).belief
          (archiveLikelihood [f]) (fun ω => (sys.experiment a).prob ω o)
          (archiveLikelihood_nonneg [f]) (fun ω => (sys.experiment a).nonneg ω o)
          hL hyCompiled hobs
        calc
          conditionByWeight
              (replayArchive init.belief (archiveOfHistory sys h) hx)
              (archiveLikelihood [f]) (archiveLikelihood_nonneg [f]) hy
              = conditionByWeight (compileHistory sys init h).belief
                  (archiveLikelihood [f]) (archiveLikelihood_nonneg [f]) hyCompiled := hb
          _ = conditionByWeight (compileHistory sys init h).belief
                (fun ω => (sys.experiment a).prob ω o)
                (fun ω => (sys.experiment a).nonneg ω o) hobs := hl
          _ = bayesUpdate (compileHistory sys init h).belief (sys.experiment a) o hobs :=
                (bayesUpdate_eq_conditionByWeight
                  (compileHistory sys init h).belief (sys.experiment a) o hobs).symm
      have htotal := bayesUpdateTotal_eq_of_pos
        (compileHistory sys init h).belief (sys.experiment a) o hobs
      calc
        replayArchive init.belief (archiveOfHistory sys (.snoc h a o)) hwhole
            = replayArchive init.belief (archiveOfHistory sys h ++ [f]) hwhole := by rfl
        _ = conditionByWeight
              (replayArchive init.belief (archiveOfHistory sys h) hx)
              (archiveLikelihood [f]) (archiveLikelihood_nonneg [f]) hy := by
              exact happ
        _ = bayesUpdate (compileHistory sys init h).belief (sys.experiment a) o hobs := hcond
        _ = bayesUpdateTotal (compileHistory sys init h).belief (sys.experiment a) o := by
              exact htotal.symm
        _ = (compileHistory sys init (.snoc h a o)).belief := by rfl

/-- Any later deterministic hypothesis resolution can be reconstructed from a
positive raw history by replaying the fine archive and then pushing forward. -/
theorem positive_history_replay_at_resolution
    {Ω : Type u} {A : Type v} {O : Type w} {Cert : Type z} {Z : Type*}
    [Fintype Ω] [Fintype O] [DecidableEq A]
    [Fintype Z] [DecidableEq Z]
    (sys : CertifiedBayesianResearchSystem Ω A O Cert)
    (init : CertifiedResearchState Ω Cert)
    (φ : Ω → Z) (h : ResearchHistory A O)
    (hp : PositiveResearchHistory sys init h) :
    ∃ hpos : 0 < archiveEvidenceMass init.belief (archiveOfHistory sys h),
      replayAtResolution φ init.belief (archiveOfHistory sys h) hpos =
        pushforwardBelief φ (compileHistory sys init h).belief := by
  obtain ⟨hpos, hreplay⟩ := positive_history_has_exact_archive_replay sys init h hp
  refine ⟨hpos, ?_⟩
  unfold replayAtResolution
  rw [hreplay]

end Komorebi.AVOC
