"""Independent values, failure controls, and guide bindings for six compositions."""
from fractions import Fraction as Q
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROGRAM = ROOT / 'examples/operator_compositions.py'
spec = importlib.util.spec_from_file_location('operator_composition_examples', PROGRAM)
examples = importlib.util.module_from_spec(spec)
spec.loader.exec_module(examples)


def compact_math(text):
    """Ignore whitespace and the two fraction spellings used by the guide."""
    text = re.sub(r'\\(?:tfrac|frac)\{(-?\d+)\}\{(\d+)\}', r'\1/\2', text)
    text = re.sub(r'\\(?:tfrac|frac)(\d)(\d)', r'\1/\2', text)
    return re.sub(r'\s+', '', text)


def tex_matrix(value):
    return r'\begin{pmatrix}' + r'\\'.join('&'.join(map(str, row)) for row in value) + r'\end{pmatrix}'


def tex_tuple(value):
    return '(' + ','.join(map(str, value)) + ')'


def tex_diagonal(value):
    return r'\operatorname{diag}' + tex_tuple(tuple(row[i] for i, row in enumerate(value)))


def table_row(values):
    return '|' + '|'.join('$' + str(value) + '$' for value in values) + '|'


class OperatorCompositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results = examples.run_recipes()

    def test_middle_chart_bridge_and_wrong_coordinate_control(self):
        row = self.results['middle-chart-bridge']
        # Direct coordinate formulas are T(a,b)=(a+2b,b), U(a,b)=(a,a+b).
        self.assertEqual(row['physical_composite'], ((1, 2), (1, 3)))
        self.assertEqual(row['bridged_composite'], ((1, 2), (1, 3)))
        self.assertEqual(row['stored_T'], ((2, 4), (0, 1)))
        self.assertEqual(row['stored_U'], ((1, -1), (1, 0)))
        self.assertEqual(row['bridge'], ((Q(1, 2), 1), (0, 1)))
        self.assertEqual(row['physical_intermediate'], (5, 2))
        self.assertEqual(row['first_coordinates'], (10, 2))
        self.assertEqual(row['second_coordinates'], (7, 2))
        self.assertEqual(row['output'], (5, 7))
        self.assertEqual(row['without_bridge_output'], (8, 10))

    def test_coarse_cancellation_independent_candidate_and_plain_addition_control(self):
        row = self.results['coarse-defect']
        self.assertEqual(row['E_T'], ((0, 1),))
        self.assertEqual(row['E_U'], ((0, -1),))
        self.assertEqual(row['transported_E_U'], ((0, -3),))
        self.assertEqual(row['propagated_E_T'], ((0, 3),))
        self.assertEqual(row['E_UT'], ((0, 0),))
        self.assertEqual(row['composite'], ((6, 0), (0, 6)))
        self.assertEqual(row['observed_summaries'], (3, 8, 18))
        self.assertEqual(row['coarse_summaries'], (3, 6, 18))
        self.assertEqual(row['kernel_vector'], (1, -1))
        self.assertEqual(row['kernel_image_summaries'], {'T': -1, 'U': 1})
        separate = row['independent_composite']
        self.assertEqual(separate['candidate'], 5)
        self.assertEqual(separate['extra_term'], ((1, 1),))
        self.assertEqual(separate['defect_row'], ((1, 1),))
        self.assertEqual(separate['defect_at_x'], 3)
        variant = row['variant']
        self.assertEqual(variant['E_U'], ((0, 1),))
        self.assertEqual(variant['transported_E_U'], ((0, 3),))
        self.assertEqual(variant['E_UT'], ((0, 6),))
        self.assertEqual(variant['naive_E_UT'], ((0, 2),))
        self.assertEqual((variant['defect_at_x'], variant['naive_defect_at_x']), (12, 4))

    def test_metric_defects_and_independent_squared_norms(self):
        row = self.results['metric-defect']
        self.assertEqual(row['E_T'], ((3, 0), (0, 0)))
        self.assertEqual(row['E_U'], ((Q(-3, 4), 0), (0, 8)))
        self.assertEqual(row['pulled_back_E_U'], ((-3, 0), (0, 8)))
        self.assertEqual(row['E_UT'], ((0, 0), (0, 8)))
        self.assertEqual(row['naive_E_UT'], ((Q(9, 4), 0), (0, 8)))
        self.assertEqual(row['states'], ((1, 1), (2, 1), (1, 3)))
        norms = (1 ** 2 + 1 ** 2, 2 ** 2 + 1 ** 2, 1 ** 2 + 3 ** 2)
        self.assertEqual(row['squared_norms'], norms)
        self.assertEqual(row['stage_changes'], (norms[1] - norms[0], norms[2] - norms[1]))
        self.assertEqual(row['evaluated_stage_changes'], (3, 5))
        self.assertEqual(row['total_change'], 8)
        self.assertEqual(row['naive_change'], Q(41, 4))

    def test_each_basis_moment_and_wrong_covector_control(self):
        row = self.results['moment-covector']
        self.assertEqual(row['basis_polynomials'], ((1,), (0, 1), (0, -1, 1), (0, 2, -3, 1)))
        # Integrals of 1, x, x^2-x, x^3-3x^2+2x, independently expanded.
        moments = (Q(1), Q(1, 2), Q(1, 3) - Q(1, 2), Q(1, 4) - 1 + 1)
        self.assertEqual(row['independent_basis_integrals'], moments)
        self.assertEqual(row['falling_moments'], moments)
        self.assertEqual(row['falling_coefficients'], (0, 1, 3, 1))
        self.assertEqual(row['ordinary_coefficients'], (0, 0, 0, 1))
        self.assertEqual(row['integral'], Q(1, 4))
        self.assertEqual(row['unchanged_row_integral'], Q(7, 4))

    def test_pushforward_product_atoms_and_correlation_control(self):
        row = self.results['finite-pushforward']
        nu = ((Q(1), Q(1, 2)), (Q(3), Q(1, 2)))
        self.assertEqual(row['source_atoms'], ((0, Q(1, 2)), (1, Q(1, 2))))
        self.assertEqual(row['pushforward_atoms'], nu)
        self.assertEqual(row['product_atoms'], (((1, 1), Q(1, 4)), ((1, 3), Q(1, 4)),
                                                ((3, 1), Q(1, 4)), ((3, 3), Q(1, 4))))
        self.assertEqual(row['product_contributions'], (Q(1, 4), Q(3, 4), Q(3, 4), Q(9, 4)))
        self.assertEqual(row['partial_integral_slope'], 2)
        self.assertEqual(row['partial_integrals'], ((1, 2), (3, 6)))
        self.assertEqual(row['pushforward_integral'], Q(1 + 9, 2))
        self.assertEqual(row['pullback_integral'], Q(1 + 9, 2))
        self.assertEqual(row['product_integral'], Q(1 + 3 + 3 + 9, 4))
        self.assertEqual(row['iterated_integral'], Q(2 + 6, 2))
        self.assertEqual(row['correlated_atoms'], (((1, 1), Q(1, 2)), ((3, 3), Q(1, 2))))
        self.assertEqual(row['correlated_marginals'], (nu, nu))
        self.assertEqual(row['correlated_integral'], Q(1 + 9, 2))

    def test_filter_all_five_cuts_full_state_and_missing_history_controls(self):
        row = self.results['filter-state']
        samples = (Q(2), Q(1), Q(0), Q(0))
        expected = (Q(2), Q(8, 3), Q(25, 18), Q(25, 54))
        for n, actual in enumerate(expected):
            previous_input = samples[n - 1] if n else Q(0)
            previous_output = expected[n - 1] if n else Q(0)
            self.assertEqual(actual, samples[n] + previous_input / 2 + previous_output / 3)
        self.assertEqual(row['input'], samples)
        self.assertEqual(row['output'], expected)
        final_state = {'previous_input': Q(0), 'previous_output': expected[-1]}
        self.assertEqual(row['final_state'], final_state)
        self.assertEqual([run['cut'] for run in row['split_runs']], list(range(5)))
        for run in row['split_runs']:
            cut = run['cut']
            with self.subTest(cut=cut):
                self.assertEqual(run['left_output'], expected[:cut])
                self.assertEqual(run['right_output'], expected[cut:])
                self.assertEqual(run['saved_state'], {
                    'previous_input': samples[cut - 1] if cut else Q(0),
                    'previous_output': expected[cut - 1] if cut else Q(0),
                })
                self.assertEqual(run['final_state'], final_state)
        self.assertEqual(row['continuation_state'], {'previous_input': 1, 'previous_output': Q(8, 3)})
        self.assertEqual(row['continued_output'], (Q(25, 18), Q(25, 54)))
        self.assertEqual(row['reset_output'], (0, 0))
        self.assertEqual(row['output_history_only'], (Q(8, 9), Q(8, 27)))
        self.assertEqual(row['input_history_only'], (Q(1, 2), Q(1, 6)))
        supplied = examples.FilterState(Q(7, 5), Q(-2, 7))
        self.assertEqual(examples.filter_chunk((), supplied), ((), supplied))
        self.assertEqual(row['empty_chunk']['returned_state'], row['empty_chunk']['supplied_state'])

    def test_guide_displays_are_bound_to_computed_values(self):
        guide = (ROOT / 'docs/operators/COMPOSITION.md').read_text(encoding='utf-8')
        markers = list(re.finditer(r'<a id="([^"]+)"></a>', guide))
        sections = {match[1]: guide[match.end():markers[i + 1].start() if i + 1 < len(markers) else len(guide)]
                    for i, match in enumerate(markers)}

        def contains(name, *fragments):
            self.assertIn(name, sections)
            text = compact_math(sections[name])
            for fragment in fragments:
                with self.subTest(recipe=name, display=fragment):
                    self.assertIn(compact_math(fragment), text)

        row = self.results['middle-chart-bridge']
        contains('middle-chart-bridge',
                 r'\widehat T=CT=' + tex_matrix(row['stored_T']),
                 r'\widehat U=UD^{-1}=' + tex_matrix(row['stored_U']),
                 r'R=DC^{-1}=' + tex_matrix(row['bridge']),
                 r'=UT=' + tex_matrix(row['physical_composite']),
                 r'UTx=' + tex_tuple(row['output']),
                 r'\widehat U\widehat T x=' + tex_tuple(row['without_bridge_output']))

        row = self.results['coarse-defect']
        contains('coarse-defect',
                 r'E_T=qT-\overline Tq=' + tex_matrix(row['E_T']),
                 r'E_U=qU-\overline Uq=' + tex_matrix(row['E_U']),
                 tex_matrix(row['variant']['E_UT']),
                 'The actual composite defect at $x$ is $' + str(row['variant']['defect_at_x']) + '$',
                 'would give $' + str(row['variant']['naive_defect_at_x']) + '$ at that input',
                 'Its defect at $x$ is $' + str(row['independent_composite']['defect_at_x']) + '$')
        for label, state, observed, candidate in zip(('Initial', 'After $T$', 'After $UT$'), row['states'],
                                                      row['observed_summaries'], row['coarse_summaries']):
            contains('coarse-defect', '|' + label + '|$' + tex_tuple(state) + r'^{\mathsf T}$|' +
                     '|'.join('$' + str(value) + '$' for value in (observed, candidate, observed - candidate)) + '|')

        row = self.results['metric-defect']
        contains('metric-defect',
                 r'\mathcal E(T)&=' + tex_diagonal(row['E_T']),
                 r'\mathcal E(U)&=' + tex_diagonal(row['E_U']),
                 r'T^{\mathsf T}\mathcal E(U)T&=' + tex_diagonal(row['pulled_back_E_U']),
                 r'\mathcal E(UT)&=' + tex_diagonal(row['E_UT']),
                 r'\mathcal E(T)+\mathcal E(U)=' + tex_diagonal(row['naive_E_UT']),
                 'At $v$ this predicts $' + str(row['naive_change']) + '$, rather than $' + str(row['total_change']) + '$')

        row = self.results['moment-covector']
        contains('moment-covector',
                 'B=' + tex_matrix(row['basis_matrix']),
                 'mB=' + tex_matrix((row['falling_moments'],)),
                 'a=' + tex_matrix(tuple((value,) for value in row['falling_coefficients'])),
                 'Ba=' + tex_matrix(tuple((value,) for value in row['ordinary_coefficients'])),
                 r'(mB)a=\frac12-\frac12+\frac14=' + str(row['integral']),
                 'ma=1/2+1+1/4=' + str(row['unchanged_row_integral']))

        row = self.results['finite-pushforward']
        contains('finite-pushforward',
                 r'I_\nu p=\frac12(1^2+3^2)=' + str(row['pushforward_integral']),
                 r'I_{\nu\otimes\nu}(yz)=' + str(row['product_integral']),
                 r'(I_\nu^{(z)}(yz))(y)=\frac12(y+3y)=' + str(row['partial_integral_slope']) + 'y',
                 r'I_\gamma(yz)=\frac12(1+9)=' + str(row['correlated_integral']))
        for (point, weight), contribution in zip(row['product_atoms'], row['product_contributions']):
            contains('finite-pushforward', table_row((tex_tuple(point), point[0] * point[1], contribution)))

        row = self.results['filter-state']
        for n, current_output in enumerate(row['output']):
            values = (n, row['input'][n], row['input'][n - 1] if n else 0,
                      row['output'][n - 1] if n else 0, current_output)
            contains('filter-state', table_row(values))
        state = row['continuation_state']
        controls = (
            ('Complete', (state['previous_input'], state['previous_output']), row['continued_output']),
            ('Output history only', (Q(0), state['previous_output']), row['output_history_only']),
            ('Input history only', (state['previous_input'], Q(0)), row['input_history_only']),
            ('Reset', (Q(0), Q(0)), row['reset_output']),
        )
        for label, supplied, output in controls:
            contains('filter-state', '|' + label + ': $' + tex_tuple(supplied) + r'^{\mathsf T}$|$' + tex_tuple(output) + '$|')

    def test_cli_no_default_write_and_exact_optional_receipt(self):
        with tempfile.TemporaryDirectory() as directory:
            command = [sys.executable, '-B', str(PROGRAM)]
            result = subprocess.run(command, cwd=directory, capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(list(Path(directory).iterdir()), [])
            lines = result.stdout.splitlines()
            self.assertEqual(lines[:-1], ['PASS ' + name for name in examples.RECIPES])
            self.assertEqual(lines[-1], 'RESULT 6/6 finite composition recipes passed')
            receipt_path = Path(directory) / 'receipt.json'
            result = subprocess.run(command + ['--json', str(receipt_path)], cwd=directory,
                                    capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            receipt = json.loads(receipt_path.read_text(encoding='utf-8'))
            self.assertEqual(list(Path(directory).iterdir()), [receipt_path])
        self.assertEqual(receipt['recipe_count'], 6)
        self.assertEqual(list(receipt['recipes']), list(examples.RECIPES))
        self.assertEqual(receipt['recipes']['moment-covector']['integral'], '1/4')
        self.assertEqual(receipt['recipes']['filter-state']['output'], ['2', '8/3', '25/18', '25/54'])

        def reject_float(value):
            self.assertNotIsInstance(value, float)
            if isinstance(value, dict):
                for item in value.values():
                    reject_float(item)
            elif isinstance(value, (tuple, list)):
                for item in value:
                    reject_float(item)

        reject_float(self.results)
        reject_float(receipt)


if __name__ == '__main__':
    unittest.main()
