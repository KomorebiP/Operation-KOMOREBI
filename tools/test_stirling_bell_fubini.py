"""Exact partition-transform research preview and source-bound website checks."""
from __future__ import annotations

import json
from fractions import Fraction
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from stirling_case import FILES, PREFIX, program_module, publish, verify_site

ROOT=Path(__file__).resolve().parents[1]
M=program_module(ROOT)


class PartitionTransformExactTests(unittest.TestCase):
    def test_all_exact_contracts(self):
        counts=M.test_cases()
        self.assertEqual(counts,{
            "reference":17,
            "partitions":45,
            "surjections":36,
            "triangular":165,
            "generating":110,
            "packets":44
        })
        self.assertEqual(sum(counts.values()),417)

    def test_reference_row_and_signed_inverse(self):
        second=M.stirling_second(5)
        first=M.signed_stirling_first(5)
        bell,ordered=M.bell_fubini(second)
        self.assertEqual(second[5],(0,1,15,25,10,1))
        self.assertEqual((bell[5],ordered[5]),(52,541))
        self.assertEqual(first[5],(0,24,-50,35,-10,1))
        self.assertEqual(sum(first[5][j]*ordered[j] for j in range(6)),120)
        self.assertEqual(sum(first[5][j]*bell[j] for j in range(6)),1)

    def test_two_summary_obstruction_uses_only_a_candidate_not_another_partition_row(self):
        original=M.stirling_second(4)[4]
        alternate=M.ALTERNATIVE_ROW_4
        self.assertEqual(original,(0,1,7,6,1))
        self.assertEqual(alternate,(0,5,2,7,1))
        self.assertNotEqual(original,alternate)
        self.assertEqual((sum(original),M.weighted_sum(original)),(15,75))
        self.assertEqual((sum(alternate),M.weighted_sum(alternate)),(15,75))
        self.assertEqual(tuple(y-x for x,y in zip(original,alternate)),
                         (0,4,-5,1,0))

    def test_formal_series_and_residue_packets(self):
        rows=M.stirling_second(10)
        bell,ordered=M.bell_fubini(rows)
        self.assertEqual(
            M.ordered_reciprocal_series(10),
            M.egf_coefficients(ordered))
        self.assertEqual(
            M.exponential_series_of_expm1(10),
            M.egf_coefficients(bell))
        f=M.egf_coefficients(ordered)
        even=M.packet(f,2,0)
        odd=M.packet(f,2,1)
        self.assertEqual(even[5],Fraction(0))
        self.assertEqual(odd[5],Fraction(541,120))
        self.assertEqual(sum(M.packet(f,3,r)[5] for r in range(3)),f[5])
        self.assertEqual(f[5],Fraction(541,120))
        with self.assertRaises(ValueError):
            M.packet(f,0,0)

    def test_program_emits_reproducible_exact_results(self):
        with tempfile.TemporaryDirectory() as one,tempfile.TemporaryDirectory() as two:
            a,b=Path(one),Path(two)
            counts=M.test_cases()
            M.save(a,counts)
            M.save(b,counts)
            self.assertEqual(len(FILES),7)
            for name in FILES:
                with self.subTest(name=name):
                    self.assertEqual((a/name).read_bytes(),(b/name).read_bytes())
            summary=json.loads((a/"results.json").read_bytes())
            self.assertEqual(summary["total_assertions"],417)
            self.assertEqual(summary["bell5"],52)
            self.assertEqual(summary["fubini5"],541)
            self.assertEqual(summary["packet_split_n5"],{
                "even_degree_tap_contribution":135,
                "odd_degree_tap_contribution":406
            })
            image=(a/"stirling-transform.svg").read_text()
            self.assertIn("Stirling partitions and factorial-weighted ordered partitions",image)
            self.assertIn("541",image)


class PartitionTransformWebsiteTests(unittest.TestCase):
    def test_generated_reader_archive_and_rejected_modified_download(self):
        with tempfile.TemporaryDirectory() as work:
            site_root=Path(work)
            pages={}
            def write(path,text):
                target=site_root/path
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text(text,encoding="utf-8",newline="\n")
            def page(path,title,body,source):
                write(path,body)
                pages[path]=body
            site=SimpleNamespace(root=ROOT,output=site_root,revision="a"*40,
                                 write=write,page=page,search=[])
            record=publish(site)
            self.assertEqual(len(site.search),1)
            self.assertEqual(record["case_assertions"],417)
            self.assertEqual(len(record["tables"]),7)
            pages[record["manuscript_url"]]="<h1>Stirling partitions</h1>"
            from check_reader_site import Page
            parsed={name:Page(content) for name,content in pages.items()}
            self.assertEqual(verify_site(site_root,parsed),1)
            (site_root/record["download_url"]).write_bytes(b"tampered")
            with self.assertRaises(AssertionError):
                verify_site(site_root,parsed)

    def test_export_hashes_bound_to_exact_source(self):
        with tempfile.TemporaryDirectory() as work:
            root=Path(work)
            def write(path,text):
                target=root/path
                target.parent.mkdir(parents=True,exist_ok=True)
                target.write_text(text,encoding="utf-8",newline="\n")
            site=SimpleNamespace(root=ROOT,output=root,revision="b"*40,
                                 write=write,page=lambda *args:None,search=[])
            record=publish(site)
            self.assertEqual(
                set(x["name"] for x in record["tables"]),set(FILES))
            self.assertTrue(all(entry["size"]>0 for entry in record["tables"]))
            self.assertTrue((root/PREFIX/"results.json").is_file())
            self.assertTrue((root/PREFIX/"stirling-transform.svg").is_file())


if __name__=="__main__":
    unittest.main()
