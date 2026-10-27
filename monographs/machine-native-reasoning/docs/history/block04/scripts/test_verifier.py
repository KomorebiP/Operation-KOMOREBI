"""Small exact regression tests for the project-authored receipt parser and source scanner."""
import unittest
from verify import parse_axioms,masked_lean,source_inventory
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
if __name__=='__main__':unittest.main()
