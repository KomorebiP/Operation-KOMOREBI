"""Check the finite examples without extending the source theorems' scope."""
import contextlib
import csv
from decimal import Decimal as D, localcontext
import importlib.util
import io
import json
import math
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

from physics_presets import PHYSICS_PRESETS
from check_hand_examples import quantum_measurement

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('komorebi_browser', ROOT/'website/python/komorebi_browser.py')
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)


def run_preset(name, replacement=None):
    HELPER._reset()
    messages = []
    HELPER._sink = messages.append
    output = io.StringIO()
    namespace = {}
    code = PHYSICS_PRESETS[name]['code']
    if replacement:
        code = code.replace(*replacement)
    with patch.dict(sys.modules, {'komorebi_browser': HELPER}), contextlib.redirect_stdout(output):
        exec(compile(code, name+'.py', 'exec'), namespace)
    return output.getvalue(), [json.loads(m) for m in messages], namespace


def decimal_sin(x):
    # Independent high-precision Taylor evaluation, used only for |x| <= 1.
    total = term = x
    for n in range(1, 60):
        term *= -x*x/D((2*n)*(2*n+1))
        total += term
    return total


class PhysicsPythonTests(unittest.TestCase):
    def test_output_and_plot_payloads(self):
        for name, spec in PHYSICS_PRESETS.items():
            with self.subTest(preset=name):
                output, messages, _ = run_preset(name)
                self.assertEqual(output, spec['expected'])
                plots = [m for m in messages if m['kind'] == 'plot']
                self.assertEqual(len(plots), 2 if name == 'physics-centered' else 1)
                self.assertTrue(all(m['description'] for m in plots))

    def test_packet_rotation_and_receiving_first_sign(self):
        _, messages, namespace = run_preset('physics-current')
        traces = messages[0]['data']
        self.assertEqual(len(traces[0]['x']), 161)
        for t, e0, e1, total in zip(traces[0]['x'], traces[0]['y'], traces[1]['y'], traces[2]['y'], strict=True):
            self.assertAlmostEqual(e0, 1-math.sin(2*t), delta=1e-14)
            self.assertAlmostEqual(e1, 1+math.sin(2*t), delta=1e-14)
            self.assertAlmostEqual(total, 2, delta=1e-14)
        self.assertEqual(namespace['incoming'], (-2, 2))
        # Reversing the generator reverses the actual current.
        reversed_current = (2*1*1, 2*1*(-1))
        self.assertNotEqual(reversed_current, namespace['incoming'])

    def test_quantum_against_existing_exact_density_matrix_calculation(self):
        quantum_measurement()  # Independent matrix products over rational complex pairs.
        _, _, ns = run_preset('physics-phase')
        from fractions import Fraction as Q
        self.assertEqual(ns['phase_i'], (Q(1, 2), Q(1, 2)))
        self.assertEqual(ns['phase_1'], (Q(49, 50), Q(1, 50)))
        self.assertEqual(ns['purity'], Q(337, 625))
        self.assertNotEqual(ns['phase_i'], ns['phase_1'])
        for key in ('coordinate', 'phase_i', 'phase_1'):
            self.assertEqual(sum(ns[key]), 1)

    def test_quantum_rejects_unnormalized_input(self):
        with self.assertRaisesRegex(ValueError, 'a.a.b.b'):
            run_preset('physics-phase', ('Q(3, 5), Q(4, 5)', 'Q(1), Q(1)'))

    def test_centered_csv_against_decimal_evaluation(self):
        _, messages, _ = run_preset('physics-centered')
        exported = [m for m in messages if m['kind'] == 'file']
        self.assertEqual(len(exported), 1)
        rows = list(csv.DictReader(io.StringIO(exported[0]['content'])))
        self.assertEqual(len(rows), 4)
        with localcontext() as ctx:
            ctx.prec = 70
            for row in rows:
                h = D(row['h'])
                error = sum((decimal_sin(h*k)/h-k)**2 for k in (D(1), D(2), D(-1))).sqrt()
                envelope = h*h*D(66).sqrt()/6
                self.assertLessEqual(error, envelope)
                self.assertAlmostEqual(float(row['modal_symbol_error']), float(error), delta=2e-15)
                self.assertAlmostEqual(float(row['quadratic_envelope']), float(envelope), delta=2e-15)

    def test_centered_negative_spacing_symmetry_and_zero_rejection(self):
        _, _, positive = run_preset('physics-centered')
        _, _, negative = run_preset('physics-centered',
            ('[0.5, 0.25, 0.125, 0.0625]', '[-0.5, -0.25, -0.125, -0.0625]'))
        self.assertEqual([r[1:] for r in positive['rows']], [r[1:] for r in negative['rows']])
        with self.assertRaisesRegex(ValueError, 'nonzero spacings'):
            run_preset('physics-centered', ('[0.5, 0.25, 0.125, 0.0625]', '[0]'))


if __name__ == '__main__':
    unittest.main()
