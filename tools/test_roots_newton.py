"""Exact arithmetic, transfer-law and source-bound reader publication tests."""
from __future__ import annotations

import json
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace

from roots_newton_case import (
    FILES, PREFIX, READER, load_program, publish, verify_site,
)

ROOT = Path(__file__).resolve().parents[1]
M = load_program(ROOT)


class RootsUnityExactTests(unittest.TestCase):
    def test_fifth_power_three_packets(self):
        row, poly, packets = M.example_row()
        self.assertEqual(row, (0,1,15,25,10,1))
        self.assertEqual(
            [int(M.evaluate(packet,4)) for packet in packets],
            [600,244,180])
        self.assertEqual(M.add(M.add(packets[0],packets[1]),packets[2]),poly)
        self.assertEqual([int(M.evaluate(M.delta(p),4)) for p in packets],
                         [900,961,240])
        self.assertEqual(M.evaluate(M.delta(poly),4),2101)

    def test_true_transported_operator_not_original_power_filter(self):
        p = M.power(5)
        self.assertEqual(M.evaluate(M.naive_power_project(p,3,2),4),1024)
        self.assertEqual(M.evaluate(M.project_newton(p,3,2),4),180)
        self.assertEqual(M.project_newton(p,3,0),
                         (Fraction(0),Fraction(50),Fraction(-75),Fraction(25)))
        self.assertEqual(M.project_newton(p,3,1),
                         (Fraction(0),Fraction(-59),Fraction(110),Fraction(-60),Fraction(10)))
        self.assertEqual(M.project_newton(p,3,2),
                         (Fraction(0),Fraction(9),Fraction(-35),Fraction(35),
                          Fraction(-10),Fraction(1)))

    def test_exact_fourier_trace_and_general_polynomial_projections(self):
        for modulus in range(2,8):
            for k in range(11):
                for r in range(modulus):
                    self.assertEqual(
                        M.trace_character_selector(modulus,k,r),
                        int(k%modulus==r))
        f = (Fraction(2,3),Fraction(-5),Fraction(0),Fraction(2),Fraction(1,5))
        pieces = [M.project_newton(f,4,r) for r in range(4)]
        self.assertEqual(M.to_newton(f),
                         tuple(M.to_newton(M.add(M.add(pieces[0],pieces[1]),
                                              M.add(pieces[2],pieces[3])))))
        for r in range(4):
            for s in range(4):
                self.assertEqual(M.project_newton(pieces[r],4,s),
                                 pieces[r] if r==s else (Fraction(0),))
            self.assertEqual(M.delta(pieces[r]),
                             M.project_newton(M.delta(f),4,(r-1)%4))

    def test_transport_of_product_and_difference(self):
        x = M.power(1)
        self.assertEqual(M.star(x,x),M.falling(2))
        self.assertEqual(M.multiply(x,x),M.power(2))
        self.assertNotEqual(M.star(x,x),M.multiply(x,x))
        f = (Fraction(1),Fraction(2),Fraction(3))
        g = (Fraction(2),Fraction(-1),Fraction(1))
        self.assertEqual(M.delta(M.star(f,g)),
                         M.add(M.star(M.delta(f),g),M.star(f,M.delta(g))))
        self.assertEqual(M.delta(M.multiply(f,g)),
                         M.add(M.multiply(M.delta(f),g),
                               M.multiply(M.shift(f),M.delta(g))))

    def test_exact_suite_and_invalid_controls(self):
        checks = M.check()
        self.assertEqual(checks["anchor"],12)
        self.assertGreater(sum(checks.values()),400)
        self.assertEqual(set(checks),{
            "anchor","stirling","roundtrip","projection","difference",
            "fourier","refinement","matrix","star","boundaries",
        })
        with self.assertRaises(ValueError):
            M.project_newton(M.power(2),0,0)
        with self.assertRaises(ValueError):
            M.project_newton(M.power(2),3,3)
        with self.assertRaises(ValueError):
            M.trace_character_selector(3,0,3)

    def test_deterministic_artifacts_and_no_overwrite(self):
        with tempfile.TemporaryDirectory() as left, tempfile.TemporaryDirectory() as right:
            a,b=Path(left),Path(right)
            c=M.check()
            M.save(a,c)
            M.save(b,c)
            self.assertEqual(len(FILES),7)
            for file in FILES:
                with self.subTest(file=file):
                    self.assertEqual((a/file).read_bytes(),(b/file).read_bytes())
            result=json.loads((a/"results.json").read_bytes())
            self.assertEqual(result["total_assertions"],sum(c.values()))
            self.assertEqual(result["packet_values_at_x4"],["600","244","180"])
            self.assertIn("2,2,15,12,180,1",
                          (a/"packet-contributions.csv").read_text())
            self.assertIn("600 + 244 + 180 = 1024",
                          (a/"projection-diagram.svg").read_text())
            with self.assertRaises(FileExistsError):
                M.save(a,c)


class RootsUnityReaderTests(unittest.TestCase):
    def make_site(self, root):
        pages={}
        def write(path,data):
            destination=root/path
            destination.parent.mkdir(parents=True,exist_ok=True)
            destination.write_text(data,encoding="utf-8",newline="\n")
        def page(path,title,body,source):
            write(path,body)
            pages[path]=body
        return SimpleNamespace(
            root=ROOT,output=root,revision="b"*40,
            write=write,page=page,search=[]),pages

    def test_reader_hashes_and_mutation_rejection(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            site,pages=self.make_site(root)
            record=publish(site)
            pages[record["manuscript_url"]]="<h1>Roots of unity</h1>"
            self.assertEqual(record["reader_url"],READER)
            self.assertEqual(len(record["tables"]),len(FILES))
            self.assertEqual(len(site.search),1)
            from check_reader_site import Page
            parsed={path:Page(body) for path,body in pages.items()}
            self.assertEqual(verify_site(root,parsed),1)
            file=root/PREFIX/"newton-stirling.csv"
            file.write_bytes(file.read_bytes()+b"corrupted")
            with self.assertRaises(AssertionError):
                verify_site(root,parsed)

    def test_archive_contains_exact_program_and_manuscript(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            site,_=self.make_site(root)
            record=publish(site)
            import zipfile
            with zipfile.ZipFile(root/record["archive_url"]) as archive:
                self.assertIn(record["manuscript_source"],archive.namelist())
                self.assertIn(record["program_source"],archive.namelist())
                self.assertEqual(
                    archive.read(record["program_source"]),
                    (ROOT/record["program_source"]).read_bytes())
                self.assertEqual(
                    archive.read(record["manuscript_source"]),
                    (ROOT/record["manuscript_source"]).read_bytes())


if __name__=="__main__":
    unittest.main()
