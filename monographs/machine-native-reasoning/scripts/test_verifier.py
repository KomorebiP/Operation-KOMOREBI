"""Small exact regression tests for the project-authored receipt parser and source scanner."""
import unittest
from verify import parse_axioms,masked_lean,source_inventory,invalid_control_diagnostic
class VerifierTests(unittest.TestCase):
    def test_multiline_axioms(self):
        text="'A' depends on axioms: [propext,\n Classical.choice,\n Quot.sound]\n'B' does not depend on any axioms\n"
        self.assertEqual(parse_axioms(text),{'A':['propext','Classical.choice','Quot.sound'],'B':[]})
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):parse_axioms("'A' does not depend on any axioms\n'A' does not depend on any axioms")
    def test_comments_and_strings(self):
        self.assertNotIn('sorry',masked_lean('/- nested /- sorry -/ end -/\n-- sorry\n"sorry"'))
        self.assertIn('sorry',masked_lean('example : True := by sorry'))
    def test_live_inventory(self):
        inv=source_inventory()
        self.assertGreater(len(inv),390)
        self.assertGreater(sum(r['kind']=='theorem' for r in inv),237)
        names={r['name'] for r in inv}
        self.assertIn('Komorebi.MachineTheory.Instrument.quotient_feedback_law',names)
        self.assertIn('Komorebi.MachineTheory.Bayes.ReportingModel.all_iff_reconstruction',names)
        self.assertIn('Komorebi.MachineTheory.Refinement.least_prediction_correction_refinement',names)
    def test_planning_endpoints(self):
        names={r['name'] for r in source_inventory()}
        self.assertIn('Komorebi.MachineTheory.BeliefPlanning.compressed_belief_planning',names)
        self.assertIn('Komorebi.MachineTheory.Planning.Tree',names)
        self.assertIn('Komorebi.MachineTheory.PlanningSensor.source_sensor_optimum',names)
    def test_approximation_endpoints(self):
        names={r['name'] for r in source_inventory()}
        self.assertIn('Komorebi.MachineTheory.ApproximateHistory.whole_history_bound',names)
        self.assertIn('Komorebi.MachineTheory.Variation.condition_bound',names)
        self.assertIn('Komorebi.MachineTheory.ApproximateDecision.history_selected_policy_regret',names)
    def test_response_endpoints(self):
        names={r['name'] for r in source_inventory()}
        for n in ['ResponseDecision.decision_error_global','ResponseDecision.metric_minimizers_exist',
                  'ResponseDecision.regret_to_minimum','ResponseDecision.unique_minimizer_transfer',
                  'DecisionHistory.history_conditioned_response_error',
                  'ResponseExamples.sensor_true_unique_from_certificate']:
            self.assertIn('Komorebi.MachineTheory.'+n,names)
    def test_recipient_endpoints(self):
        names={r['name'] for r in source_inventory()}
        for n in ['Recipient.encoder_exists_iff','Recipient.cardinality_budget_iff',
                  'Recipient.minimum_image_eq_cover','Recipient.minimum_common_artifact',
                  'RecipientExecution.Audience.common_artifact_iff',
                  'RecipientExamples.xor_minimum_codebook','RecipientExamples.triple_minimum_codebook']:
            self.assertIn('Komorebi.MachineTheory.'+n,names)
    def test_hard_inquiry_endpoints(self):
        names={r['name'] for r in source_inventory()}
        for n in ['HardInquiry.Model.exact_frontier','HardInquiry.Model.joint_budget_iff',
                  'HardInquiry.Model.execution_sound','HardInquiry.Model.worst_coordinate_attained',
                  'HardExamples.four_frontier_all','HardControls.sensor_recipient_execution']:
            self.assertIn('Komorebi.MachineTheory.'+n,names)
    def test_binary_endpoints(self):
        names={r['name'] for r in source_inventory()}
        for n in ['BinaryDiagnosis.binary_lower_bounds','BinaryDiagnosis.records_exact',
                  'BinaryDiagnosis.actual_run_lower_bound','BinaryDiagnosis.admitted_frontier',
                  'BinaryDiagnosis.admitted_budget','BinaryExamples.eight_frontier_all']:
            self.assertIn('Komorebi.MachineTheory.'+n,names)
    def test_synthesis_endpoints(self):
        names={r['name'] for r in source_inventory()}
        for n in ['Synthesis.truthful_call_bound','Synthesis.truthful_outcome',
                  'Synthesis.scan_protocol','Synthesis.accepted_first',
                  'Synthesis.ordered_compression','Synthesis.resume_bounded',
                  'SynthesisExamples.arithmetic_key_sound']:
            self.assertIn('Komorebi.MachineTheory.'+n,names)
    def test_prefix_endpoints(self):
        names={r['name'] for r in source_inventory()}
        for n in ['PrefixScan.integer_completion_iff','PrefixScan.stream_branches',
                  'OrderedCompiler.source_prefix_certificate','OrderedCompiler.admitted_failure_iff_empty_frontier',
                  'PrefixExamples.eight_measured_reads']:
            self.assertIn('Komorebi.MachineTheory.'+n,names)
    def test_revision_endpoints(self):
        names={r['name'] for r in source_inventory()}
        for n in ['Dependency.closure_iff_reach','Dependency.System.selective_reuse',
                  'Dependency.System.restoration','Dependency.System.admitted_reuse_and_restoration',
                  'RevisionExamples.meanings_complete','RevisionExamples.replacement_actual_controller']:
            self.assertIn('Komorebi.MachineTheory.'+n,names)
    def test_prices_endpoints(self):
        names={r['name'] for r in source_inventory()}
        for n in ['ResourcePrices.all_nonnegative_prices_iff','ResourcePrices.finite_price_minimum',
                  'ResourcePrices.Ledger.delta_eq_total_difference','ResourcePrices.amortization_iff',
                  'PriceExamples.actual_workload_delta','PriceExamples.paid_hull_minimum',
                  'PriceRevision.meanings_complete','PriceRevision.restored_calculation']:
            self.assertIn('Komorebi.MachineTheory.'+n,names)
    def test_lineage_endpoints(self):
        names={r['name'] for r in source_inventory()}
        for n in ['Lineage.conditional_marginal_bound','Lineage.lineage_bound',
                  'Lineage.lineage_ennreal_bound','Lineage.stopped_selected_lineage_bound',
                  'Lineage.divergent_real_total_not_union_bound',
                  'LineageExamples.selection_invalidates_nominal_bound']:
            self.assertIn('Komorebi.MachineTheory.'+n,names)
    def test_ending_endpoints(self):
        names={r['name'] for r in source_inventory()}
        for n in ['SafeEnding.safe_continuation_iff','SafeEnding.source_core83',
                  'SafeEnding.command_rank_arrival','SafeEnding.guarantee_mem_ending',
                  'SafeEnding.running_has_infinite_path','SafeEnding.ending_prefix_extends']:
            self.assertIn('Komorebi.MachineTheory.'+n,names)
    def test_common_quotient_endpoints(self):
        names={r['name'] for r in source_inventory()}
        for n in ['source_core24','source_core24_reference','agreement_of_function_factor',
                  'agreement_iff_invisible','agreement_iff_commonModel','switching_output',
                  'stage_finrank_eq','comparisonMap_unique','discrepancy_reference_independent']:
            self.assertIn('Komorebi.MachineTheory.CommonQuotient.'+n,names)
    def test_unknown_identifier_not_math_rejection(self):
        self.assertTrue(invalid_control_diagnostic('error(lean.unknownIdentifier): Unknown identifier x\nunsolved goals\n⊢ False'))
    def test_implicit_unknown_not_math_rejection(self):
        self.assertTrue(invalid_control_diagnostic('Hint: The identifier X is unknown, and autoImplicit ...'))
    def test_actual_false_goal_is_allowed(self):
        self.assertFalse(invalid_control_diagnostic('error: unsolved goals\n⊢ False'))
if __name__=='__main__':unittest.main()
