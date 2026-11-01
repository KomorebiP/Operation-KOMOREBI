"""Finite arithmetic, information-loss controls, and published-byte safeguards."""
import contextlib
import csv
import io
import json
from pathlib import Path
import re
from fractions import Fraction as Q
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest

from quantum_case import FILES, MANUSCRIPT, MANUSCRIPT_URL, PREFIX, PROGRAM, load_program, publish, verify_site
from test_physics_python import run_preset

ROOT = Path(__file__).resolve().parents[1]
M = load_program(ROOT)


class QuantumArithmeticTests(unittest.TestCase):
    def test_full_exact_suite_and_documented_stdout(self):
        self.assertEqual(M.check(), dict(states=182, partial_channels=910, records=182, controls=10))
        output = subprocess.check_output([sys.executable, '-B', str(ROOT/PROGRAM)], text=True)
        document = (ROOT/MANUSCRIPT).read_text(encoding='utf-8')
        expected = re.search(r'<!-- expected-output -->\s*```text\n(.*?)\n```', document, re.S)[1]+'\n'
        self.assertEqual(output, expected)

    def test_imaginary_sign_against_direct_vector_projector(self):
        # |y+> = (1,i)/sqrt(2): the conjugation fixes this sensitive sign.
        rho = M.state(phase=M.C(0, 1))
        self.assertEqual(rho[0][1], M.C(0, Q(-12, 25)))
        self.assertEqual(M.probabilities(rho), (Q(1, 2), Q(49, 50), Q(9, 25)))
        self.assertEqual(M.probabilities(M.state(phase=M.C(0, -1)))[1], Q(1, 50))

    def test_same_summary_cannot_recover_x_measurement(self):
        a, b = M.state(), M.state(phase=M.C(0, 1))
        self.assertNotEqual(a, b)
        self.assertEqual(M.dephase(a), M.dephase(b))
        self.assertEqual(M.probabilities(a)[0]-M.probabilities(b)[0], Q(12, 25))
        self.assertEqual(M.probabilities(M.dephase(a))[:2], (Q(1, 2), Q(1, 2)))

    def test_channel_composition_and_nonphysical_inverse(self):
        rho = M.state(phase=M.C(Q(3, 5), Q(4, 5)))
        for s in (Q(0), Q(1, 3), Q(1)):
            for t in (Q(0), Q(1, 2), Q(1)):
                self.assertEqual(M.partial_dephase(M.partial_dephase(rho, t), s),
                                 M.partial_dephase(rho, s*t))
        self.assertEqual(M.purity(M.partial_dephase(rho, Q(1, 2))), Q(409, 625))
        invalid = M.matrix(((Q(1, 2), 1), (1, Q(1, 2))))
        self.assertEqual(invalid[0][0]*invalid[1][1]-invalid[0][1]*invalid[1][0], M.C(Q(-3, 4)))
        for invalid_t in (Q(-1, 2), Q(3, 2)):
            with self.assertRaises(ValueError):
                M.partial_dephase(rho, invalid_t)

    def test_coherent_and_classical_record_have_different_reversibility(self):
        rho = M.state(phase=M.C(0, 1))
        joint = M.coherent_record(rho)
        self.assertEqual(joint[0][3], M.C(0, Q(-12, 25)))
        self.assertEqual(M.forget_record(joint), M.dephase(rho))
        self.assertEqual(M.forget_record(M.uncompute_record(joint)), rho)
        self.assertEqual(M.forget_record(M.uncompute_record(M.dephase(joint))), M.dephase(rho))

    def test_refined_measurement_removes_within_parity_coherence(self):
        bell = M.matrix(((Q(1, 2), 0, 0, Q(1, 2)), (0, 0, 0, 0),
                         (0, 0, 0, 0), (Q(1, 2), 0, 0, Q(1, 2))))
        self.assertEqual(M.dephase(bell, ((0, 3), (1, 2))), bell)
        self.assertEqual(M.purity(M.dephase(bell)), Q(1, 2))
        self.assertEqual(M.dephase(M.dephase(bell, ((0, 3), (1, 2)))), M.dephase(bell))
        for groups in (((0, 3), (1,)), ((0, 3), (1, 2, 3))):
            with self.assertRaises(ValueError):
                M.dephase(bell, groups)

    def test_snapshot_bytes_reproduce_on_every_platform(self):
        with tempfile.TemporaryDirectory() as temp:
            M.save(Path(temp), M.check())
            for name in FILES:
                self.assertEqual((Path(temp)/name).read_bytes(),
                                 (ROOT/'verification/quantum-phase-measurement'/name).read_bytes())


class QuantumPublicationTests(unittest.TestCase):
    def test_published_program_records_and_bundle_detect_corruption(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            pages = {}
            def write(path, content):
                target = root/path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding='utf-8')
            def page(path, title, body, source):
                pages[path] = body
                write(path, body)
            site = SimpleNamespace(root=ROOT, output=root, revision='a'*40,
                                   write=write, page=page, search=[])
            record = publish(site)
            pages[MANUSCRIPT_URL] = 'walkthrough'
            self.assertEqual(verify_site(root, pages), 1)
            archive_bytes = (root/record['archive_url']).read_bytes()
            self.assertEqual(publish(site), record)
            self.assertEqual((root/record['archive_url']).read_bytes(), archive_bytes)
            for path in [record['download_url'], PREFIX+FILES[0], record['archive_url']]:
                target = root/path
                original = target.read_bytes()
                target.write_bytes(b'corrupted')
                with self.assertRaises(AssertionError):
                    verify_site(root, pages)
                target.write_bytes(original)

    def test_browser_exact_data_agrees_with_independent_matrix_program(self):
        _, messages, ns = run_preset('physics-dephasing')
        file = next(m for m in messages if m['kind'] == 'file')
        rows = list(csv.DictReader(io.StringIO(file['content'])))
        self.assertEqual(len(rows), 9)
        rho = M.state(phase=M.C(Q(3, 5), Q(4, 5)))
        for row in rows:
            mixed = M.partial_dephase(rho, Q(row['retained_coherence']))
            self.assertEqual(tuple(Q(row[k]) for k in ('p_X_plus', 'p_Y_plus', 'p_Z_plus')),
                             M.probabilities(mixed))
            self.assertEqual(Q(row['purity']), M.purity(mixed))
            error = M.add(rho, M.scale(-1, mixed))
            self.assertEqual(Q(row['squared_HS_error']), M.trace(M.multiply(M.adjoint(error), error)).re)
        self.assertEqual((ns['recovered_re'], ns['recovered_im']), (Q(36, 125), Q(-48, 125)))

    def test_browser_full_dephasing_and_invalid_inputs(self):
        output, _, ns = run_preset('physics-dephasing', ('t = Q(1, 2)', 't = Q(0)'))
        self.assertIn('cannot be recovered', output)
        self.assertNotIn('recovered_re', ns)
        for replacement in (('t = Q(1, 2)', 't = Q(2)'),
                            ('Q(3, 5), Q(4, 5)', 'Q(1), Q(1)')):
            with self.assertRaises(ValueError):
                run_preset('physics-dephasing', replacement)


if __name__ == '__main__':
    unittest.main()
