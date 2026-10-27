#!/usr/bin/env python3
"""Reading-release regressions. No Lean compilation or universal arithmetic proof."""
from __future__ import annotations
import argparse,json,re,sys,unittest
from pathlib import Path
import fitz
import audit_release as A
ROOT=A.ROOT;SRC=A.SOURCE;BASE=A.BASE;PDF=A.PDF
class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src=A.source_audit();cls.refs=A.citation_audit();cls.pdf=A.pdf_audit()
        cls.oldmain=(BASE/'traditional/Paper_XI_Traditional_Final.tex').read_text()
        cls.main=(SRC/'traditional/Paper_XI_Traditional_Final.tex').read_text()
    def test_01_main_proof_bodies(self):
        self.assertEqual(len(A.blocks(self.oldmain,'proof')),68)
        self.assertEqual(A.blocks(self.oldmain,'proof'),A.blocks(self.main,'proof'))
    def test_02_main_statement_bodies(self):
        self.assertEqual(sum(len(A.blocks(self.oldmain,k)) for k in A.STATEMENTS),105)
        for kind in A.STATEMENTS:self.assertEqual(A.blocks(self.oldmain,kind),A.blocks(self.main,kind))
    def test_03_exact_appendix_patch(self):
        self.assertEqual(self.src['status'],'passed',self.src['errors'])
        self.assertEqual((self.src['superscript_repairs'],self.src['appendices_with_repairs']),(44,9))
    def test_04_all_fifteen_raw_notes(self):
        rows=A.read_json(ROOT/'evidence/block07/APPENDIX_SOURCE_MAP.json')['sources'];self.assertEqual(len(rows),15)
        for row in rows:self.assertEqual(A.digest(ROOT/row['local_path']),row['sha256'])
    def test_05_conversion_detector_and_negative_controls(self):
        self.assertTrue(A.converted_superscripts(r'J\textsuperscript{1/H}1'))
        self.assertTrue(A.converted_superscripts(r's(P\textsuperscript{r)=Q}r'))
        self.assertFalse(A.converted_superscripts(r'\(J^1/H^1\)'))
        for p in (SRC/'traditional/appendices').glob('*.tex'):self.assertFalse(A.converted_superscripts(p.read_text()))
    def test_06_parser_receipt_accounts_for_hazards(self):
        report=A.read_json(ROOT/'evidence/block07/MARKDOWN_AST.json')
        self.assertEqual(len(report['sources']),15)
        self.assertEqual(report['totals'],{'Superscript':44,'Link':1,'Emph':2})
    def test_07_literal_appendix_blocks_preserved(self):
        for old in (BASE/'traditional/appendices').glob('*.tex'):
            self.assertEqual(A.blocks(old.read_text(),'Verbatim'),A.blocks((SRC/'traditional/appendices'/old.name).read_text(),'Verbatim'))
    def test_08_source_carrier_header_clarified_without_new_numbers(self):
        old=(BASE/'traditional/appendices/dyadic_capacity.tex').read_text()
        new=(SRC/'traditional/appendices/dyadic_capacity.tex').read_text()
        self.assertIn('Source carrier dimension',new)
        for row in ['1 & 2 & 0 & 1 & 2 & Fails','2 & 4 & 2 & 2 & 4 & Fails','3 & 8 & 6 & 8 & 8 & Exact','4 & 16 & 14 & 128 & 16 & Sufficient']:
            self.assertIn(row,old);self.assertIn(row,new)
    def test_09_previous_factor_repair_and_double_exponent_controls(self):
        text=(SRC/'traditional/appendices/odd_capacity.tex').read_text()
        self.assertIn(r'\([k:\FF_p](n-n/p)\)',text)
        self.assertNotEqual(2,2*(3-1))
        for d in range(1,9):
            self.assertEqual(2**((2**d-2)//2),2**(2**(d-1)-1))
        self.assertNotEqual(2**(2**(3-1)-1),2**(3-1)-1)
    def test_10_all_selected_lean_source_hashes(self):
        modules=A.read_json(SRC/'lean_guide/SOURCE_CATALOG.json')['modules'];self.assertEqual(len(modules),423)
        for row in modules.values():self.assertEqual(A.digest(SRC/'lean_guide'/row['local_source_path']),row['sha256'])
    def test_11_all_excerpts_reversible(self):
        rows=A.read_json(SRC/'lean_guide/EXCERPTS.json');self.assertEqual(len(rows),40)
        for row in rows:
            raw=SRC/'lean_guide/excerpts'/f"{row['id']}.raw.txt";display=raw.with_name(f"{row['id']}.render.txt")
            self.assertEqual(A.digest(raw),row['raw_sha256']);self.assertEqual(A.digest(display),row['render_sha256'])
            text=display.read_text()
            for token,char in row['display_escape_map'].items():text=text.replace(token,char)
            self.assertEqual(text,raw.read_text())
    def test_12_catalogs_formal_sources_and_figures_preserved(self):
        for old in BASE.rglob('*'):
            if old.is_file() and (old.suffix in ['.lean','.json'] or 'figures' in old.parts):
                self.assertEqual(old.read_bytes(),(SRC/old.relative_to(BASE)).read_bytes())
    def test_13_all_4342_declaration_names_printed(self):
        rows=A.read_json(SRC/'lean_guide/SOURCE_CATALOG.json')['modules']
        names=[decl['name'] for row in rows.values() for decl in row['declarations']];self.assertEqual(len(names),4342)
        with fitz.open(PDF/'Paper_XI_Lean_Guide_v1.0.0.pdf') as d:text=re.sub(r'\s+','',''.join(p.get_text() for p in d))
        for name in names:self.assertIn(re.sub(r'\s+','',name),text)
    def test_14_research_readers_unchanged(self):
        for name in ['Paper_XI_Conjecture66_Progress_v0.4.0.pdf','Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf']:
            self.assertEqual(A.digest(PDF/name),A.digest(ROOT/'predecessor/block06/publication/pdfs'/name))
    def test_15_five_reader_link_graph(self):
        self.assertEqual(self.pdf['status'],'passed',self.pdf['errors'])
        self.assertEqual((self.pdf['internal_links'],self.pdf['companion_links']),(504,140))
    def test_16_page_counts_bounds_and_glyphs(self):
        self.assertEqual(self.pdf['total_pages'],510);self.assertEqual(self.pdf['errors'],[])
        self.assertEqual({x['filename']:x['pages'] for x in self.pdf['readers']},A.READERS)
    def test_17_historical_identifier_and_same_candidate_contract(self):
        rows=A.read_json(SRC/'lean_guide/HISTORICAL_CLAIM_CROSSWALK.json')['rows'];self.assertEqual(len(rows),66)
        last=[x for x in rows if x['original_obligation']==66][0]
        self.assertEqual((last['all_records_row'],last['printed_number']),(95,'16.2'))
        self.assertIn('No proof of the unrestricted statement is claimed.',self.main)
        self.assertIn('Suppose H5 holds for this same',self.main)
    def test_18_all_bibliography_keys_and_local_references(self):
        self.assertEqual(self.refs['status'],'passed',self.refs)
        self.assertEqual(self.refs['bibliography_entries'],28);self.assertEqual(self.refs['distinct_cited_keys'],28)
        self.assertEqual((self.refs['local_labels'],self.refs['local_reference_occurrences']),(286,72))
    def test_19_build_diagnostics_not_suppressed(self):
        d=A.read_json(ROOT/'verification/block07/BUILD_RECORD.json')
        for row in d['records'].values():
            for line in row['diagnostics']:
                self.assertFalse(any(x in line for x in ['Overfull','Missing character','undefined','Rerun to get']),line)
    def test_20_ledger_ids_and_history_preserved(self):
        old=A.read_json(ROOT/'predecessor/block06/PROGRESS_LEDGER.json');new=A.read_json(ROOT/'PROGRESS_LEDGER.json')
        self.assertEqual([t['id'] for t in old['tasks']],[t['id'] for t in new['tasks']]);self.assertEqual(len(new['tasks']),23)
        self.assertEqual(new['history'][:len(old['history'])],old['history']);self.assertEqual(new['checkpoint_id'],'P11-PUB-B07')
    def test_21_open_and_unexecuted_tasks_remain_explicit(self):
        rows={t['id']:t for t in A.read_json(ROOT/'PROGRESS_LEDGER.json')['tasks']}
        for tid in ['P11-OPEN-016','P11-OPEN-017','P11-OPEN-021','P11-OPEN-022']:self.assertEqual(rows[tid]['status'],'open')
        self.assertEqual(rows['P11-VERIFY-015']['status'],'not_run')
        self.assertEqual(rows['P11-PUB-019']['status'],'blocked_source_recovery')
        self.assertEqual(rows['P11-VERIFY-020']['status'],'receipt_not_recovered')
    def test_22_current_editions_and_filenames(self):
        self.assertEqual({p.name for p in PDF.glob('*.pdf')},set(A.READERS))
        for name in ['Traditional','Visual_Guide','Lean_Guide']:
            with fitz.open(PDF/f'Paper_XI_{name}_v1.0.0.pdf') as d:self.assertIn('1.0.0',d[0].get_text())
        self.assertEqual(A.read_json(ROOT/'evidence/block07/READING_ROUTES.json')['version'],'1.0.0')
        renderer=(ROOT/'tools/render_readers.py').read_text()
        self.assertIn("glob('*_v1.0.0.pdf')",renderer)
        self.assertNotIn("glob('*Synchronized*.pdf')",renderer)
    def test_23_appendix_square_bits_not_invented(self):
        # Preserve the actual earlier atlas data, including its explicit null native data.
        atlas_root=ROOT/'predecessor/block06/predecessor/block05'
        catalog=A.read_json(atlas_root/'evidence/block05/PLATE_CATALOG.json')
        self.assertTrue(catalog)
        ledger=A.read_json(ROOT/'PROGRESS_LEDGER.json')
        row=[t for t in ledger['tasks'] if t['id']=='P11-OPEN-022'][0]
        self.assertIn('actual',str(row).lower());self.assertIn('native',str(row).lower())
    def test_24_registered_route_count_and_distinct_comparison(self):
        routes=A.read_json(ROOT/'evidence/block07/READING_ROUTES.json')['routes'];self.assertEqual(len(routes),107)
        built=A.read_json(ROOT/'verification/block07/BUILD_RECORD.json')['reading_routes']
        self.assertEqual(set(routes),set(built))
        concordance=(ROOT/'READING_CONCORDANCE.md').read_text()
        for key,row in built.items():
            self.assertIn(f"| `{key}` | `{row['file']}` | {row['page']} |",concordance)
        self.assertNotEqual(built['obligation_66']['destination'],built['current_comparison']['destination'])
def main()->int:
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--result',type=Path,required=True);a=ap.parse_args();out=a.result.resolve()
    if out.is_relative_to(ROOT):raise SystemExit('Test report must be outside the package.')
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ReleaseTests);res=unittest.TextTestRunner(verbosity=2).run(suite)
    data={'status':'passed' if res.wasSuccessful() else 'failed','methods':res.testsRun,'failures':len(res.failures),'errors':len(res.errors),'script_sha256':A.digest(Path(__file__)),'scope':__doc__}
    out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(data,indent=2)+'\n');return int(not res.wasSuccessful())
if __name__=='__main__':raise SystemExit(main())
