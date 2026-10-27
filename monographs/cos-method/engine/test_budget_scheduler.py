import unittest
import numpy as np

from budget_scheduler import (
    additive_scalar_bound,
    brute_force_unit_optimum,
    depth_edge_risk_vector,
    double_buffer_pipeline_estimate,
    edge_risks_depth,
    exact_depth_transfer_envelope,
    exact_envelope_refinement,
    prune_pairs,
    symmetric_offdiag_pairs,
    unit_cost_optimal_additive_schedule,
)


class BudgetSchedulerTests(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(123)
        q = 6
        B = np.zeros((q, q))
        for i in range(q):
            B[i, i] = 0.70 + 0.10 * rng.random()
        for i in range(q):
            for j in range(i + 1, q):
                d = j - i
                scale = 0.12 if d == 1 else 0.02 / d
                B[i, j] = B[j, i] = scale * (0.7 + 0.6 * rng.random())
        self.B = B
        self.rho = np.array([1.2, 0, 0, 0, 0, 0], dtype=float)
        self.depth = 4
        self.pairs = symmetric_offdiag_pairs(q)

    def test_edge_additive_vector_bound(self):
        risks = edge_risks_depth(self.B, self.rho, self.depth)
        rng = np.random.default_rng(4)
        for _ in range(30):
            omitted = [p for p in self.pairs if rng.random() < 0.35]
            B0 = prune_pairs(self.B, omitted)
            exact_vec = (
                np.linalg.matrix_power(self.B, self.depth)
                - np.linalg.matrix_power(B0, self.depth)
            ) @ self.rho
            add_vec = np.sum(
                [r.vector for r in risks if r.pair in set(omitted)],
                axis=0,
            ) if omitted else np.zeros_like(self.rho)
            self.assertTrue(np.all(exact_vec <= add_vec + 1e-12))

    def test_unit_cost_optimum_matches_bruteforce_additive(self):
        budget = 0.012
        sched = unit_cost_optimal_additive_schedule(
            self.B, self.rho, self.depth, budget
        )
        brute = brute_force_unit_optimum(
            self.B, self.rho, self.depth, budget,
            use_exact_envelope=False,
        )
        self.assertEqual(len(sched.omitted_pairs), len(brute.omitted_pairs))
        self.assertLessEqual(sched.additive_risk_bound, budget + 1e-15)

    def test_exact_refinement_remains_certified(self):
        budget = 0.012
        sched = unit_cost_optimal_additive_schedule(
            self.B, self.rho, self.depth, budget
        )
        refined = exact_envelope_refinement(
            self.B, self.rho, self.depth, budget, sched.omitted_pairs
        )
        self.assertTrue(refined.certificate_valid)
        self.assertGreaterEqual(len(refined.omitted_pairs), len(sched.omitted_pairs))

    def test_double_buffer_formula(self):
        io = [2.0, 2.0, 2.0, 2.0]
        comp = [3.0, 3.0, 3.0, 3.0]
        r = double_buffer_pipeline_estimate(
            io, comp, resident_block_bytes=100, fixed_working_bytes=50
        )
        self.assertAlmostEqual(r.single_buffer_time, 20.0)
        self.assertAlmostEqual(r.double_buffer_time, 14.0)
        self.assertEqual(r.resident_bytes_single, 150)
        self.assertEqual(r.resident_bytes_double, 250)


if __name__ == "__main__":
    unittest.main(verbosity=2)
