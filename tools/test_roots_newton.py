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

    def test_both_projectors_are_valid_but_not_identical(self):
        f=M.power(5)
        ordinary=[M.naive_power_project(f,3,r) for r in range(3)]
        transported=[M.project_newton(f,3,r) for r in range(3)]
        self.assertEqual(ordinary,[(Fraction(0),),(Fraction(0),),f])
        self.assertEqual([M.evaluate(p,4) for p in ordinary],[0,0,1024])
        self.assertEqual([M.evaluate(p,4) for p in transported],[600,244,180])
        self.assertEqual(
            M.add(ordinary[0],M.add(ordinary[1],ordinary[2])),f)
        for r in range(3):
            for target in range(3):
                self.assertEqual(
                    M.naive_power_project(ordinary[r],3,target),
                    ordinary[r] if target==r else (Fraction(0),))
        with self.assertRaises(ValueError):
            M.naive_power_project(f,0,0)
        with self.assertRaises(ValueError):
            M.naive_power_project(f,3,3)
        with self.assertRaises(ValueError):
            M.naive_power_project(f,True,0)

    def test_integral_stirling_inverse_and_mod_three_polynomial_scope(self):
        first=M.signed_stirling_first(8)
        second=M.stirling_second(8)
        for p in (2,3,5):
            for n in range(9):
                for k in range(n+1):
                    self.assertEqual(
                        sum(first[n][j]*second[j][k]
                            for j in range(k,n+1)) % p, int(n==k))
                    self.assertEqual(
                        sum(second[n][j]*first[j][k]
                            for j in range(k,n+1)) % p, int(n==k))
        for degree in range(9):
            f=M.power(degree)
            self.assertEqual(
                M.mod_polynomial(M.delta(M.delta(M.delta(f))),3),(0,))
            self.assertEqual(
                M.mod_polynomial(M.translate(f,3),3),
                M.mod_polynomial(f,3))
        v=M.falling(3)
        self.assertNotEqual(M.mod_polynomial(v,3),(0,))
        self.assertTrue(all(M.evaluate(v,a).numerator%3==0
                            for a in range(3)))

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

    def test_independent_function_image_histograms(self):
        self.assertEqual(M.image_count_histogram(5,4),(0,4,180,600,240,0))
        self.assertEqual(sum(M.image_count_histogram(5,4)),4**5)
        self.assertEqual(M.image_count_histogram(0,0),(1,))
        self.assertEqual(M.image_count_histogram(3,0),(0,0,0,0))
        for codomain in range(5):
            for n in range(7):
                counts=M.image_count_histogram(n,codomain)
                expected=M.stirling_second(n)[n]
                self.assertEqual(
                    counts,tuple(expected[k]*M.evaluate(M.falling(k),codomain)
                                 for k in range(n+1)))
                self.assertEqual(sum(counts),codomain**n)
        for bad in ((-1,2),(1,-1),(2.2,3)):
            with self.assertRaises(ValueError):
                M.image_count_histogram(*bad)

    def test_number_operator_and_rational_spectral_projectors(self):
        for k in range(10):
            self.assertEqual(M.newton_degree_operator(M.falling(k)),
                             M.scale(M.falling(k),k))
        self.assertEqual(M.newton_degree_operator(M.power(2)),
                         (Fraction(0),Fraction(-1),Fraction(2)))
        self.assertNotEqual(M.newton_degree_operator(M.power(2)),
                            (Fraction(0),Fraction(0),Fraction(2)))
        for degree in range(7):
            f=M.power(degree)
            self.assertEqual(
                M.add(M.newton_degree_operator(M.delta(f)),
                      M.scale(M.delta(M.newton_degree_operator(f)),-1)),
                M.scale(M.delta(f),-1))
            for modulus in (2,3,4,5):
                for r in range(modulus):
                    self.assertEqual(M.spectral_project_newton(f,modulus,r),
                                     M.project_newton(f,modulus,r))

    def test_formal_image_packet_egfs(self):
        degree=8
        for x in (Fraction(0),Fraction(1),Fraction(4),
                  Fraction(1,2),Fraction(-3,2)):
            for modulus in (2,3,4):
                packets=[
                    M.packet_egf_coefficients(x,modulus,r,degree)
                    for r in range(modulus)]
                for n in range(degree+1):
                    self.assertEqual(sum(packet[n] for packet in packets),
                                     x**n/M.factorial(n))
                    for r in range(modulus):
                        self.assertEqual(
                            packets[r][n],
                            M.evaluate(
                                M.project_newton(M.power(n),modulus,r),x
                            ) / M.factorial(n))
        self.assertEqual(tuple(
            M.packet_egf_coefficients(4,3,r,5)[5]*M.factorial(5)
            for r in range(3)),(600,244,180))
        with self.assertRaises(ValueError):
            M.packet_egf_coefficients(4,1,0,5)
        with self.assertRaises(ValueError):
            M.packet_egf_coefficients(4,3,3,5)
        with self.assertRaises(ValueError):
            M.packet_egf_coefficients(4,3,2,-1)

    def test_translation_carry_noncommutation_exact_row(self):
        f=M.power(5)
        source=[M.project_newton(f,3,r) for r in range(3)]
        target=[M.project_newton(M.translate(f,1),3,r) for r in range(3)]
        self.assertEqual([M.evaluate(q,4) for q in source],[600,244,180])
        self.assertEqual([M.evaluate(M.delta(q),4) for q in source],
                         [900,961,240])
        self.assertEqual([M.evaluate(q,4) for q in target],[1561,484,1080])
        self.assertEqual([M.evaluate(M.translate(q,1),4) for q in source],
                         [1500,1205,420])
        self.assertEqual([M.evaluate(q,4)-M.evaluate(M.translate(source[r],1),4)
                          for r,q in enumerate(target)],[61,-721,660])
        self.assertEqual(sum(M.evaluate(q,4) for q in target),5**5)
        for r in range(3):
            self.assertEqual(target[r],
                M.add(source[r],M.delta(source[(r+1)%3])))
            self.assertNotEqual(target[r],M.translate(source[r],1))
        self.assertIn("1561 + 484 + 1080 = 3125",
                      M.svg_translation_carry())

    def test_general_translation_and_cyclic_transfer_blocks(self):
        examples=[M.power(k) for k in range(7)]
        examples.extend([(Fraction(2,3),Fraction(-1),Fraction(0),Fraction(5)),
                         (Fraction(0),Fraction(1,2),Fraction(0),Fraction(-2))])
        for poly in examples:
            for h in (Fraction(-1),Fraction(0),Fraction(1),
                      Fraction(2),Fraction(3),Fraction(1,2)):
                self.assertEqual(M.translate(poly,h),
                                 M.translate_via_newton(poly,h))
                for m in (2,3,4,5):
                    destinations=[M.project_newton(M.translate(poly,h),m,r)
                                  for r in range(m)]
                    for r in range(m):
                        total=(Fraction(0),)
                        for source in range(m):
                            result=M.translate_packet_block(poly,m,source,r,h)
                            self.assertEqual(result,
                                M.project_newton(
                                    M.translate(M.project_newton(poly,m,source),h),
                                    m,r))
                            total=M.add(total,result)
                            if h==1:
                                original=M.project_newton(poly,m,source)
                                expected=(Fraction(0),)
                                if r==source:
                                    expected=M.add(expected,original)
                                if r==(source-1)%m:
                                    expected=M.add(expected,M.delta(original))
                                self.assertEqual(result,expected)
                        self.assertEqual(total,destinations[r])
        with self.assertRaises(ValueError):
            M.translate_packet_block(M.power(2),1,0,0,1)
        with self.assertRaises(ValueError):
            M.translate_packet_block(M.power(2),3,3,0,1)
        with self.assertRaises(ValueError):
            M.translate_packet_block(M.power(2),3,0,-1,1)

    def test_filtered_egf_carry_under_one_extra_label(self):
        degree=8
        u=(Fraction(0),)+tuple(
            Fraction(1,M.factorial(j)) for j in range(1,degree+1))
        for x in (Fraction(0),Fraction(1),Fraction(4),
                  Fraction(1,2),Fraction(-3,2)):
            for m in (2,3,4):
                for r in range(m):
                    current=M.packet_egf_coefficients(x,m,r,degree)
                    next_row=M.packet_egf_coefficients(x+1,m,r,degree)
                    prior=M.packet_egf_coefficients(x,m,(r-1)%m,degree)
                    carry=M.series_product_truncated(u,prior,degree)
                    self.assertEqual(next_row,tuple(
                        current[n]+carry[n] for n in range(degree+1)))
        self.assertEqual([M.packet_egf_coefficients(5,3,r,5)[5]*120
                          for r in range(3)],[1500,1205,420])

    def test_integral_basis_but_colliding_spectral_eigenvalues_in_f3(self):
        one=M.falling(0)
        triple=M.falling(3)
        self.assertEqual(M.mod_polynomial(triple,3),(0,2,0,1))
        self.assertEqual(M.mod_polynomial(M.newton_degree_operator(one),3),(0,))
        self.assertEqual(M.mod_polynomial(M.newton_degree_operator(triple),3),(0,))
        self.assertEqual(M.mod_polynomial(M.project_newton(one,2,0),3),(1,))
        self.assertEqual(M.mod_polynomial(M.project_newton(triple,2,0),3),(0,))
        self.assertEqual(M.mod_polynomial(M.project_newton(triple,2,1),3),
                         (0,2,0,1))
        self.assertNotEqual(M.mod_polynomial(one,3),
                            M.mod_polynomial(triple,3))
        self.assertEqual(M.mod_polynomial(M.translate(triple,3),3),
                         M.mod_polynomial(triple,3))
        with self.assertRaises(ValueError):
            M.mod_polynomial((Fraction(1,2),),3)
        with self.assertRaises(ValueError):
            M.mod_polynomial(M.falling(3),1)

    def test_exact_suite_and_invalid_controls(self):
        checks = M.check()
        self.assertEqual(checks["anchor"],12)
        self.assertGreater(sum(checks.values()),6800)
        self.assertEqual(set(checks),{
            "anchor","stirling","roundtrip","projection","difference",
            "fourier","refinement","matrix","star","boundaries",
            "enumeration","spectral","packet_egf",
            "translation_anchor","translation","translation_blocks",
            "egf_carry","characteristic","power_projector","modular_basis",
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
            self.assertEqual(len(FILES),15)
            for file in FILES:
                with self.subTest(file=file):
                    self.assertEqual((a/file).read_bytes(),(b/file).read_bytes())
            result=json.loads((a/"results.json").read_bytes())
            self.assertEqual(result["total_assertions"],sum(c.values()))
            self.assertEqual(result["packet_values_at_x4"],["600","244","180"])
            self.assertEqual(result["image_count_histogram_n5_x4"],[0,4,180,600,240,0])
            self.assertEqual(result["number_operator_on_x_squared"],["0","-1","2"])
            self.assertEqual(result["packet_egf_n5_x4"],["600","244","180"])
            self.assertEqual(result["shift_one_project_after_translate_at_4"],
                             ["1561","484","1080"])
            self.assertEqual(result["shift_one_translate_existing_packet_at_4"],
                             ["1500","1205","420"])
            self.assertEqual(result["shift_one_cross_packet_carries_at_4"],
                             ["961","240","900"])
            self.assertEqual(result["finite_characteristic_obstruction"]["falling_degree_3_mod_3"],
                             [0,2,0,1])
            self.assertIn("0,600,1500,900,961,1561",
                          (a/"shifted-packet-ledger.csv").read_text())
            self.assertIn("F3,0,0,1,1,0",
                          (a/"finite-characteristic-obstruction.csv").read_text())
            self.assertIn("1561 + 484 + 1080 = 3125",
                          (a/"translation-carry.svg").read_text())
            self.assertIn("5,4,3,600,600",(a/"image-histograms.csv").read_text())
            self.assertIn("600 + 244 + 180 = 1024 functions",
                          (a/"function-image-histogram.svg").read_text())
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
            self.assertGreaterEqual(record["case_assertions"],6800)
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
