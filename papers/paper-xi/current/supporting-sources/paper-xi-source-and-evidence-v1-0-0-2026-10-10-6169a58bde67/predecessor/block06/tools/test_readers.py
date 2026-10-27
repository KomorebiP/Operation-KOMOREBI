#!/usr/bin/env python3
"""Bounded publication regressions, not a Lean build or universal arithmetic proof."""
from __future__ import annotations
import argparse,hashlib,json,re,unittest,sys
from pathlib import Path
import fitz
ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'publication/source'
BASE=ROOT/'predecessor/block05/baseline/core_readers_editable'
PDF=ROOT/'publication/pdfs'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
class ReaderTests(unittest.TestCase):
    def test_01_all_68_main_proof_bodies_preserved(self):
        a=(BASE/'traditional/Paper_XI_Traditional_Final.tex').read_text();b=(SRC/'traditional/Paper_XI_Traditional_Final.tex').read_text()
        pat=r'\\begin\{proof\}.*?\\end\{proof\}';old=re.findall(pat,a,re.S)
        self.assertEqual(len(old),68);self.assertEqual(old,re.findall(pat,b,re.S))
    def test_02_all_numbered_statement_bodies_preserved(self):
        a=(BASE/'traditional/Paper_XI_Traditional_Final.tex').read_text();b=(SRC/'traditional/Paper_XI_Traditional_Final.tex').read_text()
        for kind in ['theorem','proposition','lemma','corollary','definition','example','standardfact','remark','conjecture']:
            pat=rf'\\begin\{{{kind}\}}.*?\\end\{{{kind}\}}';self.assertEqual(re.findall(pat,a,re.S),re.findall(pat,b,re.S),kind)
    def test_03_appendix_change_is_exactly_the_documented_repair(self):
        count=0
        for old in (BASE/'traditional/appendices').glob('*.tex'):
            new=SRC/'traditional/appendices'/old.name;expected=old.read_text()
            if old.name=='odd_capacity.tex':
                expected=expected.replace(r'dimension \href{n−n/p}{k:F\_p}. For k=F\_p, it has dimension n−n/p.~This',r'dimension \([k:\FF_p](n-n/p)\). For \(k=\FF_p\), it has dimension \(n-n/p\). This')
            self.assertEqual(expected,new.read_text(),old.name);count+=1
        self.assertEqual(count,15)
    def test_04_raw_capacity_note_authenticates_the_missing_factor(self):
        p=ROOT/'evidence/block06/raw_sources/LEADING_LAYER_CAPACITY166.md'
        self.assertEqual(sha(p),'b1e8b64c032e43c4c8e2343493935b4f151dc7e7b2318602b593cf2501d0f5b4')
        self.assertIn('dimension [k:F_p](n−n/p)',p.read_text())
    def test_05_residue_degree_dimension_and_negative_control(self):
        for p in (3,5,7):
            for r in (1,2,3):
                n=p**r
                for f in (1,2,3,4):
                    dimension=f*(n-n//p)
                    self.assertEqual((p**f)**(n-n//p),p**dimension)
        # Dropping the grade-dimension factor fails already over F_9 at rank 3.
        self.assertNotEqual(2,2*(3-1))
    def test_06_all_423_selected_lean_sources_match_catalog(self):
        c=json.loads((SRC/'lean_guide/SOURCE_CATALOG.json').read_text())['modules'];self.assertEqual(len(c),423)
        for e in c.values():self.assertEqual(sha(SRC/'lean_guide'/e['local_source_path']),e['sha256'])
    def test_07_all_40_raw_and_displayed_excerpts_match(self):
        c=json.loads((SRC/'lean_guide/EXCERPTS.json').read_text());self.assertEqual(len(c),40)
        for e in c:
            root=SRC/'lean_guide';raw=root/'excerpts'/f"{e['id']}.raw.txt";disp=root/'excerpts'/f"{e['id']}.render.txt"
            self.assertEqual(sha(raw),e['raw_sha256']);self.assertEqual(sha(disp),e['render_sha256'])
            text=disp.read_text()
            for token,char in e['display_escape_map'].items():text=text.replace(token,char)
            self.assertEqual(text,raw.read_text())
            source=''.join((root/e['source_path']).read_text().splitlines(keepends=True)[e['first_line']-1:e['last_line']])
            self.assertTrue(source.startswith(raw.read_text().rstrip('\n')),e['id'])
    def test_08_catalogs_and_figures_are_byte_preserved(self):
        for p in BASE.rglob('*'):
            if p.is_file() and (p.suffix in ['.json','.lean'] or ('figures' in p.parts and p.suffix=='.pdf')):
                self.assertEqual(p.read_bytes(),(SRC/p.relative_to(BASE)).read_bytes(),str(p))
    def test_09_every_declared_name_is_printed(self):
        c=json.loads((SRC/'lean_guide/SOURCE_CATALOG.json').read_text())['modules'];names=[x['name'] for e in c.values() for x in e['declarations']]
        self.assertEqual(len(names),4342)
        with fitz.open(PDF/'Paper_XI_Lean_Guide_Synchronized_v0.6.0.pdf') as d:txt=re.sub(r'\s+','',''.join(p.get_text() for p in d))
        for n in names:self.assertIn(re.sub(r'\s+','',n),txt)
    def test_10_research_companions_unchanged(self):
        for name in ['Paper_XI_Conjecture66_Progress_v0.4.0.pdf','Paper_XI_Conjecture66_Visual_Atlas_v0.5.0.pdf']:
            self.assertEqual(sha(PDF/name),sha(ROOT/'predecessor/block05/publication/pdfs'/name))
    def test_11_all_pdf_links_resolve_and_no_placeholder_survives(self):
        for f in PDF.glob('*.pdf'):
            with fitz.open(f) as d:
                dests=d.resolve_names()
                for page in d:
                    for link in page.get_links():
                        if link['kind']==fitz.LINK_GOTO:self.assertTrue(0<=link['page']<len(d))
                        elif link['kind']==fitz.LINK_NAMED:self.assertIn(link['nameddest'],dests)
                        elif link['kind']==fitz.LINK_GOTOR:
                            target=PDF/link['file'];self.assertTrue(target.is_file(),str(target))
                            with fitz.open(target) as t:self.assertTrue(0<=link['page']<len(t))
                        else:self.fail(f'Unexpected or unresolved link: {f.name}: {link}')
    def test_12_historical_66_row95_is_not_register_row66(self):
        cw=json.loads((SRC/'lean_guide/HISTORICAL_CLAIM_CROSSWALK.json').read_text())['rows'];self.assertEqual(len(cw),66)
        e=[r for r in cw if r['original_obligation']==66][0]
        self.assertEqual((e['all_records_row'],e['printed_number']),(95,'16.2'))
        b=json.loads((ROOT/'verification/block06/BUILD_RECORD.json').read_text())['reading_routes']
        self.assertEqual(b['obligation_66']['number'],'66')
        self.assertNotEqual(b['current_comparison']['destination'],b['obligation_66']['destination'])
    def test_13_pdf_page_bounds_and_glyphs(self):
        for f in PDF.glob('*Synchronized*.pdf'):
            with fitz.open(f) as d:
                for i,page in enumerate(d):
                    for block in page.get_text('dict')['blocks']:
                        for line in block.get('lines',[]):
                            for s in line['spans']:
                                self.assertNotIn('\ufffd',s['text'],(f.name,i))
                                x0,y0,x1,y1=s['bbox'];self.assertGreaterEqual(x0,-.5);self.assertGreaterEqual(y0,-.5);self.assertLessEqual(x1,page.rect.width+.5);self.assertLessEqual(y1,page.rect.height+.5)
    def test_14_builds_do_not_hide_overflow_or_missing_references(self):
        b=json.loads((ROOT/'verification/block06/BUILD_RECORD.json').read_text())
        for e in b['records'].values():
            for s in e['diagnostics']:
                self.assertFalse(any(t in s for t in ['Overfull','Missing character','undefined','Rerun to get']),s)
    def test_15_editorial_history_retains_all_ids_and_open_tasks(self):
        old=json.loads((ROOT/'predecessor/block05/PROGRESS_LEDGER.json').read_text());new=json.loads((ROOT/'PROGRESS_LEDGER.json').read_text())
        self.assertEqual([x['id'] for x in old['tasks']],[x['id'] for x in new['tasks']]);self.assertEqual(len(new['tasks']),23)
        self.assertEqual(new['history'][:len(old['history'])],old['history'])
        for task in new['tasks']:
            if task['id'] in ['P11-OPEN-016','P11-OPEN-017','P11-OPEN-021','P11-OPEN-022']:self.assertEqual(task['status'],'open')
        self.assertEqual(new['checkpoint_id'],'P11-PUB-B06')

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--result',type=Path,required=True);a=ap.parse_args()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(ReaderTests);res=unittest.TextTestRunner(verbosity=2).run(suite)
    report={'status':'passed' if res.wasSuccessful() else 'failed','methods':res.testsRun,'failures':len(res.failures),'errors':len(res.errors),'script_sha256':sha(Path(__file__)),'scope':'Publication and bounded dimension regressions only. No new Lean certification or general arithmetic proof.'}
    a.result.parent.mkdir(parents=True,exist_ok=True);a.result.write_text(json.dumps(report,indent=2)+'\n');raise SystemExit(0 if res.wasSuccessful() else 1)
if __name__=='__main__':main()
