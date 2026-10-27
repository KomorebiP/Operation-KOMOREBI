#!/usr/bin/env python3
"""Paper XII reading-release regression tests. Does not invoke Lean or Lake.

The finite controls test the limits of illustrations. Source/catalog checks are
not a replacement for elaboration or for an arithmetic existence theorem.
"""
from __future__ import annotations
import argparse, collections, hashlib, io, json, re, sys, unittest, zipfile
from pathlib import Path
import fitz
sys.dont_write_bytecode = True
from audit_publication import check
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'publication/source'
OLD = ROOT / 'predecessor/editable'
DATA = SRC / 'lean_guide/data'
FIGURES_CHANGED = {'09_hecke_artin_packets.pdf', '14_companion_spine.pdf',
                   '16_pointwise_automorphy.pdf', '17_final_completion.pdf'}
FONTS = {'.ttf', '.otf', '.woff', '.woff2', '.pfb', '.pfa', '.ttc'}
def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p: Path):
    return json.loads(p.read_text())
def mm(a, b, p=2):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(len(b))) % p
                       for j in range(len(b[0]))) for i in range(len(a)))
class ReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = check(ROOT)
        cls.cat = load(DATA/'source_catalog.json')
        cls.dec = load(DATA/'declarations.json')
        cls.claims = load(DATA/'claim_crosswalk.json')['claims']
        cls.main = (SRC/'traditional/Paper_XII_Traditional_Final.tex').read_text()

    def test_01_publication_check_passes(self):
        self.assertEqual(self.audit['errors'], [])

    def test_02_all_main_proof_bodies_preserved(self):
        self.assertEqual(self.audit['proof_bodies'], {'count':52,'byte_identical':True})

    def test_03_all_main_statement_bodies_preserved(self):
        self.assertEqual(self.audit['statement_bodies'], {'count':82,'byte_identical':True})

    def test_04_complete_module_census_and_hashes(self):
        self.assertEqual(len(self.cat),96)
        self.assertEqual(len({r['module'] for r in self.cat}),96)
        for row in self.cat:
            self.assertEqual(sha(SRC/'lean_guide/formal_release/lean'/row['source']),row['sha256'])

    def test_05_declaration_census_and_literal_locations(self):
        self.assertEqual(len(self.dec),1229)
        self.assertEqual(len({r['name'] for r in self.dec}),1229)
        self.assertEqual(collections.Counter(r['kind'] for r in self.dec),
                         {'theorem':829,'def':319,'abbrev':47,'structure':17,'instance':17})
        for r in self.dec:
            lines=(SRC/'lean_guide/formal_release/lean'/r['source']).read_text().splitlines()
            i=r['line']-1
            # This catalog records an attribute line as the start of one declaration.
            while re.fullmatch(r'@\[[^\]]*\]', lines[i].strip()): i+=1
            self.assertIn(r['name'].split('.')[-1],lines[i])

    def test_06_own_and_reused_theorems_separate(self):
        self.assertEqual(sum(r['kind']=='theorem' and not r['reused_from_paper_x'] for r in self.dec),748)
        self.assertEqual(sum(r['kind']=='theorem' and r['reused_from_paper_x'] for r in self.dec),81)
        self.assertNotIn('PaperXII.DeterminantalIdeals.option_factor',{r['name'] for r in self.dec})

    def test_07_every_claim_target_has_actual_source(self):
        targets={t for r in self.claims for t in r['checked_targets']}
        self.assertEqual(len(targets),291)
        self.assertTrue(targets <= {r['name'] for r in self.dec})
        self.assertEqual(len(self.claims),49)

    def test_08_revised_and_original_ledgers_are_different(self):
        self.assertEqual(collections.Counter(r['status'] for r in self.claims),{'complete':49})
        originals=collections.Counter(r['original_status'] for r in self.claims)
        self.assertEqual(originals['complete'],41)
        self.assertEqual(originals['partial'],7)
        self.assertEqual(sum(originals.values())-originals['complete']-originals['partial'],1)
        expected={'6.12','9.4','9.5','9.6','10.5','12.2','12.4','12.6'}
        self.assertEqual({r['number'] for r in self.claims if r['amendment']},expected)

    def test_09_import_order_and_literal_imports(self):
        rows=load(DATA/'import_audit.json');order={r['module']:i for i,r in enumerate(self.cat)}
        self.assertEqual(sum(r['internal'] for r in rows),113)
        for r in rows:
            p=SRC/'lean_guide/formal_release/lean'/(r['module'].replace('.','/')+'.lean')
            self.assertIn('import '+r['import'],p.read_text())
            if r['internal']: self.assertLess(order[r['import']],order[r['module']])

    def test_10_exact_teaching_excerpts_unchanged(self):
        self.assertTrue(self.audit['excerpt_files']['byte_identical'])
        self.assertEqual(len(list((SRC/'lean_guide/excerpts').glob('*.lean'))),24)

    def test_11_source_data_catalogs_unchanged(self):
        for p in (OLD/'lean_guide/data').glob('*'):
            if not p.is_file(): continue
            q=SRC/'lean_guide/data'/p.name
            if p.name=='crosswalk.tex':
                # Display-only link wrappers are new; the complete underlying table is identical.
                t=re.sub(r'\\href\{p12-route:[^}]+\}\{([^}]+)\}',r'\1',q.read_text())
                self.assertEqual(t,p.read_text())
            else: self.assertEqual(sha(p),sha(q))

    def test_12_all_cited_bibliography_keys_resolve(self):
        self.assertEqual(self.audit['bibliography'],{'cited_keys':27,'bibitems':27,'missing':[]})
        self.assertIn('appendix',(SRC/'traditional/Paper_XII_Traditional_Final.bib').read_text().lower())

    def test_13_all_registered_remote_targets_resolve(self):
        self.assertEqual(self.audit['registered_routes'],94)
        self.assertEqual(self.audit['companion_links'],95)
        self.assertEqual(self.audit['internal_links'],211)

    def test_14_visual_lessons_do_not_spill(self):
        self.assertEqual(self.audit['visual_lesson_pages'],list(range(1,28)))
        self.assertEqual(next(r['pages'] for r in self.audit['pdfs'] if 'Visual_Guide' in r['file']),28)

    def test_15_lean_contents_fits_one_page(self):
        with fitz.open(ROOT/'publication/pdfs/Paper_XII_Lean_Guide_v1.0.0.pdf') as d:
            self.assertEqual(len(d),31)
            self.assertIn('Contents',d[2].get_text())
            self.assertIn('A practical reading and inspection sequence',d[2].get_text())
            self.assertIn('1 What this guide certifies',d[3].get_text())

    def test_16_all_pages_within_bounds_and_no_replacement_glyphs(self):
        self.assertEqual(self.audit['total_pages'],99)
        for r in self.audit['pdfs']:
            self.assertEqual(r['out_of_page_spans'],[])
            self.assertEqual(r['replacement_glyph_pages'],[])

    def test_17_four_figures_repaired_fourteen_preserved(self):
        fs=list((OLD/'traditional/figures').glob('*.pdf'))
        self.assertEqual(len(fs),18)
        changed={p.name for p in fs if sha(p)!=sha(SRC/'traditional/figures'/p.name)}
        self.assertEqual(changed,FIGURES_CHANGED)
        for name in FIGURES_CHANGED:
            with fitz.open(SRC/'traditional/figures'/name) as d:
                self.assertEqual(len(d),1)
                self.assertEqual(d[0].get_images(),[]) # vector output, not raster replacement

    def test_18_final_gate_diagram_uses_actual_five_gates(self):
        with fitz.open(SRC/'traditional/figures/17_final_completion.pdf') as d:
            t=d[0].get_text().lower()
        for word in ['residual','patching','comparison','fiber','realization']:
            self.assertIn(word,t)
        self.assertIn('existing',t)

    def test_19_frozen_predecessor_current_manifest_authenticated(self):
        r=load(ROOT/'evidence/block01/PREDECESSOR_AUDIT.json')
        self.assertEqual(r['current_manifest_entries'],2252)
        self.assertEqual(r['current_manifest_mismatches'],[])
        self.assertEqual(len(r['font_distribution_exclusions']),9)
        self.assertEqual(r['archive_sha256'],'e703c29076015a3de280e5529d9339ac209bdd8198bf4217108109f78262fe86')

    def test_20_no_distributed_font_files_including_nested_archives(self):
        found=[]
        def scan(z, prefix):
            for i in z.infolist():
                if i.is_dir():continue
                if Path(i.filename).suffix.lower() in FONTS:found.append(prefix+'!'+i.filename)
                if i.filename.lower().endswith('.zip'):
                    with zipfile.ZipFile(io.BytesIO(z.read(i))) as child:scan(child,prefix+'!'+i.filename)
        for p in ROOT.rglob('*'):
            if not p.is_file():continue
            if p.suffix.lower() in FONTS:found.append(str(p.relative_to(ROOT)))
            elif p.suffix.lower()=='.zip':
                with zipfile.ZipFile(p) as z:scan(z,str(p.relative_to(ROOT)))
        self.assertEqual(found,[])

    def test_21_characteristic_two_trace_is_not_occupancy(self):
        identity=((1,0),(0,1));self.assertEqual(mm(identity,identity),identity)
        self.assertEqual(sum(identity[i][i] for i in range(2))%2,0)
        self.assertNotEqual(identity,((0,0),(0,0)))

    def test_22_nilpotent_transitions_destroy_stable_core(self):
        n=((0,1,0),(0,0,1),(0,0,0));n2=mm(n,n);n3=mm(n2,n)
        self.assertNotEqual(n2,((0,0,0),)*3)
        self.assertEqual(n3,((0,0,0),)*3)
        # All ambient levels have dimension 3; every compatible coordinate is in im(N^3)=0.

    def test_23_one_plateau_is_not_permanent_stabilization(self):
        ranges=[{0,1,2},{0,1,2},{0,1},{0}]
        self.assertTrue(all(b<=a for a,b in zip(ranges,ranges[1:])))
        self.assertEqual(ranges[0],ranges[1]);self.assertNotEqual(ranges[1],ranges[-1])

    def test_24_quotient_geometry_is_not_a_local_idempotent(self):
        # F_2[e]/(e^2): sole idempotents 0 and 1 despite a nilpotent direction.
        mul=lambda a,b:(a[0]*b[0]%2,(a[0]*b[1]+a[1]*b[0])%2)
        vals=[(a,b) for a in range(2) for b in range(2)]
        self.assertEqual([v for v in vals if mul(v,v)==v],[(0,0),(1,0)])
        self.assertEqual(mul((0,1),(0,1)),(0,0))

    def test_25_support_does_not_supply_same_field_point(self):
        # Finite-field analogue: F_3 -> F_9=F_3[t]/(t^2+1) has no F_3-valued extension.
        self.assertEqual([x for x in range(3) if (x*x+1)%3==0],[])
        self.assertEqual(3**2,9) # nonzero extension algebra, not an empty carrier

    def test_26_a_single_frame_relation_is_not_all_frames(self):
        a=((1,1),(0,1));s=((0,1),(1,0));b=mm(mm(s,a),s)
        self.assertEqual(a[1][0],0);self.assertEqual(b[1][0],1)
        self.assertEqual(mm(s,s),((1,0),(0,1)))
        # Conjugation preserves the representation class, not a prescribed entry-zero relation.

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    stream=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromTestCase(ReleaseTests)
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    report={'status':'PASS' if result.wasSuccessful() else 'FAIL','unittest_methods':result.testsRun,
            'failures':[(str(t),s) for t,s in result.failures], 'errors':[(str(t),s) for t,s in result.errors],
            'fresh_lean':False,'scope':'Reading-release consistency, immutable source checks and six finite cautionary models',
            'log':stream.getvalue()}
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n')
    print(stream.getvalue());raise SystemExit(not result.wasSuccessful())
