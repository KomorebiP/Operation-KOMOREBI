"""Exact wavelet/FIR source and GitHub Pages publication regression checks."""
from __future__ import annotations

from fractions import Fraction as F
import importlib.util
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from wavelet_case import publish, verify_site

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("wavelet_polyphase_example",
                                              ROOT/"examples/wavelet_polyphase.py")
EXAMPLE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXAMPLE)
SNAPSHOTS = ("phase-transfer.csv", "haar-coefficients.csv",
             "weighted-budget.csv", "full-wavelet-transfer.csv",
             "multiscale-energy.csv", "operation-order.csv",
             "results.json", "signal-comparison.svg", "full-wavelet-transfer.svg")


class WaveletPolyphaseArithmetic(unittest.TestCase):
    def test_full_exact_checker(self):
        counts = EXAMPLE.check()
        self.assertEqual(counts, {
            "reference": 28, "obstructions": 5, "basis": 112,
            "exhaustive": 4375, "random": 864, "multiscale": 1525})
        self.assertEqual(sum(counts.values()), 6909)

    def test_filter_transfer_and_haar_conjugacy(self):
        x = EXAMPLE.exact(EXAMPLE.DEFAULT)
        even, odd = EXAMPLE.split_phases(x)
        a, d = EXAMPLE.haar_pair(even, odd)
        actual = EXAMPLE.fir(x)
        self.assertEqual(EXAMPLE.join_phases(EXAMPLE.transfer_polyphase(even, odd)),
                         actual)
        self.assertEqual(EXAMPLE.haar_pair(*EXAMPLE.split_phases(actual)),
                         EXAMPLE.transfer_haar(a, d))
        for i in range(len(x)):
            basis = tuple(F(int(i == j)) for j in range(len(x)))
            even, odd = EXAMPLE.split_phases(basis)
            self.assertEqual(EXAMPLE.join_phases(
                EXAMPLE.transfer_polyphase(even, odd)), EXAMPLE.fir(basis))

    def test_residual_repair_and_obstruction(self):
        case = EXAMPLE.default_case()
        x = case["x"]
        coarse = case["coarse"]
        residual = case["residual"]
        self.assertEqual(case["mean"], 3)
        self.assertEqual(EXAMPLE.energy(x), 416)
        self.assertEqual(EXAMPLE.energy(coarse), 288)
        self.assertEqual(EXAMPLE.energy(residual), 128)
        self.assertEqual(tuple(a+b for a,b in zip(coarse,residual)), x)
        self.assertEqual(EXAMPLE.haar_pair(*EXAMPLE.split_phases(x))[0],
                         EXAMPLE.haar_pair(*EXAMPLE.split_phases(coarse))[0])
        self.assertNotEqual(x, coarse)
        self.assertEqual(EXAMPLE.energy(case["filter_error"]), 624)

    def test_lifting_exactly_matches_the_stated_haar_normalization(self):
        x = EXAMPLE.exact(EXAMPLE.DEFAULT)
        even, odd = EXAMPLE.split_phases(x)
        mean, details = EXAMPLE.haar_pair(even, odd)
        average, difference = EXAMPLE.lifting_decompose(even, odd)
        self.assertEqual(average, mean)
        self.assertEqual(difference, tuple(-2*d for d in details))
        self.assertEqual(EXAMPLE.lifting_synthesize(average, difference), x)
        self.assertEqual(difference[5], -16)

    def test_sharp_periodic_filter_energy_and_missing_transfer_defect(self):
        case = EXAMPLE.default_case()
        original = case["x"]
        diff = EXAMPLE.skew_shift(original)
        self.assertEqual(EXAMPLE.energy(diff), 624)
        self.assertEqual(EXAMPLE.energy(case["filtered"]),
                         4*EXAMPLE.energy(original)+EXAMPLE.energy(diff))
        self.assertEqual(EXAMPLE.energy(case["filter_error"]), EXAMPLE.energy(diff))
        const = (F(1),)*16
        quarter = (F(1),F(0),F(-1),F(0))*4
        self.assertEqual(EXAMPLE.energy(EXAMPLE.fir(const)),4*EXAMPLE.energy(const))
        self.assertEqual(EXAMPLE.energy(EXAMPLE.fir(quarter)),8*EXAMPLE.energy(quarter))

    def test_fixed_basis_budget_and_weighted_selection_counterexample(self):
        case = EXAMPLE.default_case()
        self.assertEqual(
            tuple(int(row[2]) for row in EXAMPLE.best_detail_budget(case["levels"])),
            (272,144,80,48,16,0))
        contrast = (2,)*8 + (-2,-2,1,-5,-2,-2,-2,-2)
        mean, levels = EXAMPLE.analyze(contrast)
        self.assertEqual(mean,0)
        self.assertEqual(EXAMPLE.energy(contrast),82)
        self.assertEqual(EXAMPLE.best_detail_budget(levels)[1],(1,F(64),F(18)))
        self.assertGreater(64,18)

    def test_exact_full_four_level_operator_and_scale_energy(self):
        case = EXAMPLE.default_case()
        original = case["x"]
        filtered = case["filtered"]
        matrix = EXAMPLE.full_wavelet_transfer(16)
        self.assertEqual((len(matrix), len(matrix[0])), (16,16))
        self.assertEqual(sum(int(value!=0) for row in matrix for value in row), 56)
        self.assertEqual(matrix[0], EXAMPLE.exact((2,)+(0,)*15))
        self.assertEqual(matrix[1][11], F(1,4))
        self.assertEqual(matrix[1][15], F(-1,4))
        source_coordinates = EXAMPLE.wavelet_analysis(original)
        target_coordinates = EXAMPLE.wavelet_analysis(filtered)
        self.assertEqual(EXAMPLE.apply_matrix(matrix,source_coordinates),
                         target_coordinates)
        self.assertEqual(EXAMPLE.wavelet_synthesis(source_coordinates), original)
        self.assertEqual(EXAMPLE.wavelet_synthesis(target_coordinates), filtered)
        self.assertEqual(sum(int(x!=0) for x in source_coordinates),6)
        self.assertEqual(sum(int(x!=0) for x in target_coordinates),10)
        self.assertEqual(tuple(int(row[1]) for row in
                               EXAMPLE.wavelet_energy_levels(source_coordinates)),
                         (144,16,64,64,128))
        self.assertEqual(tuple(int(row[1]) for row in
                               EXAMPLE.wavelet_energy_levels(target_coordinates)),
                         (576,64,128,640,880))
        for j in range(16):
            wavelet_basis=tuple(F(int(k==j)) for k in range(16))
            sample_basis=EXAMPLE.wavelet_synthesis(wavelet_basis)
            self.assertEqual(
                EXAMPLE.wavelet_analysis(EXAMPLE.fir(sample_basis)),
                tuple(matrix[k][j] for k in range(16)))

    def test_filter_then_coarsen_does_not_equal_coarsen_then_filter(self):
        case=EXAMPLE.default_case()
        x=case["x"]
        hx=case["filtered"]
        px=EXAMPLE.coarsen_first_level(x)
        phx=EXAMPLE.coarsen_first_level(hx)
        hpx=EXAMPLE.fir(px)
        comm=EXAMPLE.operation_commutator(x)
        self.assertEqual(px,case["coarse"])
        self.assertEqual(EXAMPLE.coarsen_first_level(px),px)
        self.assertEqual(comm,EXAMPLE.exact(
            (-2,2,0,0,4,-4,0,0,-10,10,16,0,-8,-8,0,0)))
        self.assertEqual(EXAMPLE.energy(comm),624)
        self.assertEqual(EXAMPLE.energy(tuple(a-b for a,b in zip(hx,hpx))),768)
        self.assertEqual(EXAMPLE.energy(tuple(a-b for a,b in zip(hx,phx))),880)
        self.assertEqual(EXAMPLE.energy(comm),EXAMPLE.energy(case["filter_error"]))
        self.assertEqual(EXAMPLE.energy(comm),EXAMPLE.energy(EXAMPLE.skew_shift(x)))
        self.assertNotEqual(phx,hpx)

    def test_only_cyclic_boundary_claimed(self):
        x = EXAMPLE.exact(EXAMPLE.DEFAULT)
        self.assertEqual(EXAMPLE.fir(x)[0], 6)
        zero_padded_first = x[0]
        self.assertEqual(zero_padded_first, 2)
        self.assertNotEqual(zero_padded_first, EXAMPLE.fir(x)[0])
        cyclic = EXAMPLE.fir(x)
        zero = EXAMPLE.zero_extended_fir(x)
        self.assertEqual(zero[:2],(F(2),F(6)))
        boundary = tuple(a-b for a,b in zip(cyclic,zero))
        self.assertEqual(boundary,(F(4),F(-4))+(F(0),)*14)
        self.assertEqual(EXAMPLE.energy(boundary),32)
        self.assertEqual(EXAMPLE.default_case()["boundary_residual"],boundary)
        with self.assertRaises(ValueError):
            EXAMPLE.analyze((1, 2, 3))

    def test_snapshots_reproduced_exactly(self):
        with tempfile.TemporaryDirectory() as temp:
            folder = Path(temp)
            EXAMPLE.save(folder, EXAMPLE.check())
            for name in SNAPSHOTS:
                with self.subTest(name=name):
                    self.assertEqual((folder/name).read_bytes(),
                                     (ROOT/"verification/wavelet-polyphase"/name).read_bytes())
            stats = json.loads((folder/"results.json").read_text())
            self.assertEqual(stats["total_assertions"], 6909)
            self.assertEqual(stats["energies"]["missing_transfer_blocks"], 624)
            self.assertEqual(stats["stability"]["boundary_correction_energy"], 32)
            self.assertEqual(stats["weighted_selection_control"]["weighted_selection_error"],18)
            self.assertEqual(stats["budget_residual_energies"],[272,144,80,48,16,0])
            self.assertEqual(stats["multiscale"]["matrix_nonzero"],56)
            self.assertEqual(stats["multiscale"]["commutator_energy"],624)
            self.assertEqual(stats["multiscale"]["error_filter_coarse"],768)
            self.assertEqual(stats["multiscale"]["error_coarse_filtered"],880)
            diagram=(folder/"full-wavelet-transfer.svg").read_text()
            self.assertIn("56 nonzero",diagram)
            self.assertIn("Exact four-level Haar transfer matrix",diagram)
            with (folder/"full-wavelet-transfer.csv").open() as stream:
                self.assertEqual(len(stream.readlines()),57)


class WaveletPolyphasePublication(unittest.TestCase):
    def test_source_reader_and_detect_modified_download(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            pages = {}
            def write(path, data):
                target = out/path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(data, encoding="utf-8")
            def page(path, title, body, source):
                pages[path] = body
                write(path, body)
            site = SimpleNamespace(root=ROOT, output=out, revision="a"*40,
                                   write=write, page=page, search=[])
            record = publish(site)
            pages[record["manuscript_url"]] = "<h1>Wavelets and polyphase</h1>"
            from check_reader_site import Page
            parsed = {name: Page(body) for name,body in pages.items()}
            self.assertEqual(verify_site(out, parsed), 1)
            self.assertEqual(len(site.search), 1)
            (out/record["download_url"]).write_bytes(b"altered")
            with self.assertRaises(AssertionError):
                verify_site(out, parsed)

    def test_source_record_checks_all_svg_and_csv_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            out = Path(temp)
            site = SimpleNamespace(
                root=ROOT, output=out, revision="a"*40,
                write=lambda path, data: (out/path).write_text(data, encoding="utf-8"),
                page=lambda *args: None, search=[])
            record = publish(site)
            self.assertEqual(len(record["tables"]), 9)
            self.assertTrue(all(t["sha256"] and t["size"] for t in record["tables"]))
            self.assertIn("signal-comparison.svg", [t["source"].split("/")[-1]
                                                    for t in record["tables"]])


if __name__ == "__main__":
    unittest.main()
