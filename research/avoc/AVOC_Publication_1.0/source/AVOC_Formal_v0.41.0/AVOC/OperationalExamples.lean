import AVOC.CertifiedOperationalCatalogue

namespace Komorebi.AVOC.Affine.OperationalExamples

open Komorebi.AVOC.MultiLevel
open Komorebi.AVOC.Affine
open Komorebi.AVOC.Affine.Terminal
open Komorebi.AVOC.Affine.MultiLevelRank
open Komorebi.AVOC.Affine.MultiLevelOperational
open Komorebi.AVOC.Affine.CertifiedOperational

local instance : Fact (Nat.Prime 5) := ⟨by decide⟩
abbrev F := ZMod 5
abbrev World := Unit
abbrev ProbeId := Unit


def source : DenseProgram F 1 1 := .ident


def warmDeployment : Deployment 1 1 where
  kind := .warm
  source := source
  selected := source
  setup := 0
  correct := by intro x; rfl
  noWorse := by rfl


def coldDeployment : Deployment 1 1 where
  kind := .cold
  source := source
  selected := source
  setup := 1
  correct := by intro x; rfl
  noWorse := by rfl


def worldPlan : WorldPlan 1 1 where
  source := source
  calls := 10
  warm := warmDeployment
  cold := coldDeployment
  warm_source := rfl
  cold_source := rfl
  warm_kind := rfl
  cold_kind := rfl


def catalogue : CertifiedOperational.Catalogue World ProbeId 1 1 where
  world _ := worldPlan
  probe _ := .entry 0 0
  fee _ := 1
  fee_nonneg _ := by norm_num


def initial : State (CertifiedOperational.model catalogue) where
  worlds := Finset.univ
  worlds_nonempty := ⟨(),Finset.mem_univ _⟩
  remaining := [()]
  remaining_nodup := by decide
  lower := 0
  done := false


theorem warm_payoff_zero : warmDeployment.payoff 10 = 0 := by
  norm_num [Deployment.payoff, MultiLevelEconomics.netGain, warmDeployment,
    source, executionCost, cost]


theorem cold_payoff_negative_one : coldDeployment.payoff 10 = -1 := by
  norm_num [Deployment.payoff, MultiLevelEconomics.netGain, coldDeployment,
    source, executionCost, cost]


theorem exact_probe_match :
    ProbeMatches (rankCatalogue catalogue) initial () () true := by
  constructor
  · exact Finset.mem_univ _
  constructor
  · simp [initial]
  · rfl


theorem exact_probe_acknowledged :
    acknowledgeProbe (rankCatalogue catalogue) initial () () (.report true) =
      some (step (CertifiedOperational.model catalogue) initial (.probe ()) true) :=
  matching_probe_accepted _ _ _ _ _ exact_probe_match


theorem false_probe_report_rejected :
    acknowledgeProbe (rankCatalogue catalogue) initial () () (.report false) = none := by
  apply mismatching_probe_rejected
  intro h
  exact Bool.noConfusion h.2.2


@[simp] theorem operational_fault_rejected :
    acknowledgeProbe (rankCatalogue catalogue) initial () () .fault = none := rfl


theorem exact_probe_positive_probability :
    0 < probability (CertifiedOperational.model catalogue) initial (.probe ()) true :=
  actual_report_positive_probability _ _ _ _ _ exact_probe_match


theorem exact_probe_certifies_rank_one :
    1 ≤ (coefficients source).linear.rank := by
  exact detects_rank_lower (coefficients source).linear (.entry 0 0) (by decide)


theorem successful_probe_preserves_rank :
    RankSound (rankCatalogue catalogue)
      (step (CertifiedOperational.model catalogue) initial (.probe ()) true) := by
  apply acknowledged_probe_preserves_rank (rankCatalogue catalogue) initial
    (rankSound_zero _ initial rfl) () () true
  exact exact_probe_acknowledged


theorem warm_terminal_accepted :
    acknowledgeTerminal (CertifiedOperational.model catalogue) initial .reuse
      (.success warmDeployment) = some (terminal initial) := by
  apply matching_terminal_accepted
  · exact (reuse_mem_actions_iff _ _).2 ⟨rfl,rfl⟩
  · exact Or.inl ⟨rfl,rfl⟩


theorem cold_terminal_accepted :
    acknowledgeTerminal (CertifiedOperational.model catalogue) initial .cold
      (.success coldDeployment) = some (terminal initial) := by
  apply matching_terminal_accepted
  · exact (cold_mem_actions_iff _ _).2 rfl
  · exact Or.inr ⟨rfl,rfl⟩


theorem wrong_terminal_kind_rejected :
    acknowledgeTerminal (CertifiedOperational.model catalogue) initial .reuse
      (.success coldDeployment) = none := by
  cases h : acknowledgeTerminal (CertifiedOperational.model catalogue) initial .reuse
      (.success coldDeployment) with
  | none => rfl
  | some t =>
      have hx := accepted_terminal_exact (CertifiedOperational.model catalogue)
        initial .reuse coldDeployment t h
      rcases hx.2.1 with hgood | hcold
      · have hk : Kind.cold = Kind.warm := by
          simpa [coldDeployment] using hgood.2
        cases hk
      · cases hcold.1


theorem one_world_reuse_discrepancy_zero :
    terminalDiscrepancy (CertifiedOperational.model catalogue) initial .reuse
      warmDeployment 10 = 0 := by
  apply actual_reuse_discrepancy_zero catalogue initial ()
  intro u hu
  cases u
  rfl


theorem one_world_cold_discrepancy_zero :
    terminalDiscrepancy (CertifiedOperational.model catalogue) initial .cold
      coldDeployment 10 = 0 := by
  apply actual_cold_discrepancy_zero catalogue initial ()
  intro u hu
  cases u
  rfl

end Komorebi.AVOC.Affine.OperationalExamples
