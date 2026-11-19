"""Independent arithmetic oracles, snapshot coverage, and generated-page checks."""
from fractions import Fraction
import gzip
import hashlib
import json
from math import comb, factorial
from pathlib import Path
import tempfile
import unittest
import ast
import io
import posixpath
from urllib.parse import urlsplit, unquote
from contextlib import redirect_stdout

from build_reader_site import Site
from check_reader_site import Page, check_search_targets
from sequence_atlas import ROOT, build, catalogue, reciprocal, terms
from sequence_atlas_index import connection_graph, connection_counts
from update_sequence_atlas_oeis import compare


class SequenceAtlasTests(unittest.TestCase):
    def test_connection_graph_preserves_directed_offsets_and_rejects_invalid_records(self):
        entries=catalogue();graph=connection_graph(entries)
        self.assertEqual(len(graph['edges']),7)
        self.assertEqual(sum(len(edge['rows']) for edge in graph['edges']),84)
        self.assertEqual(connection_counts(graph,'KSEQ-000001'),(1,2))
        self.assertEqual(connection_counts(graph,'KSEQ-000024'),(0,0))
        self.assertEqual(sum(sum(connection_counts(graph,entry['id'])) for entry in entries),14)
        edge=next(edge for edge in graph['edges'] if edge['source_id']=='KSEQ-000030')
        self.assertEqual((edge['source_start'],edge['target_start']),(1,0))
        self.assertEqual([row['transformed_value'] for row in edge['rows'][:3]],['1','3','5'])
        entries[0]['connections'][0]['matched_terms']=11
        with self.assertRaises(ValueError):connection_graph(entries)

    def test_reading_index_maps_preserve_the_value_and_basis_conventions(self):
        for entry in catalogue():
            reading=entry['reading']
            self.assertEqual(reading['offset'],0)
            self.assertEqual(reading['stored_range'],[0,63])
            self.assertEqual(len(reading['samples']),6)
            for n,row in enumerate(reading['samples']):
                self.assertEqual((row['n'],row['value']),(n,entry['terms'][n]))
                if entry['kind']=='reciprocal':
                    self.assertEqual(row['source_index'],entry['N']*n)
                    self.assertEqual(Fraction(row['ordinary_coefficient']),Fraction(int(entry['terms'][n]),factorial(entry['N']*n)))
                elif entry['kind']=='euler':
                    self.assertEqual(row['source_index'],2*n)
                    self.assertNotIn('ordinary_coefficient',row)
                else:
                    self.assertEqual(row['source_index'],n)
                    self.assertNotIn('ordinary_coefficient',row)
            self.assertTrue(reading['definition'] and reading['index_meaning'] and reading['tex'])
        reciprocal_entry=next(e for e in catalogue() if e['id']=='KSEQ-000007')
        self.assertEqual(reciprocal_entry['reading']['samples'][2]['ordinary_coefficient'],'23/13440')

    def test_original_ids_and_terms_are_preserved(self):
        entries=catalogue()
        signature=hashlib.sha256(json.dumps([(e['id'],e['terms']) for e in entries[:26]],separators=(',',':')).encode()).hexdigest()
        self.assertEqual(signature,'e6d9a62e849de548d3226c1fb657b7b0a91b92b3bb383dcd9bd6326dadb48ff3')
        self.assertEqual([e['id'] for e in entries],[f'KSEQ-{n:06d}' for n in range(1,39)])

    def test_copyable_programs_and_computed_connections(self):
        entries=catalogue();lookup={e['id']:e for e in entries}
        for entry in entries:
            output=io.StringIO()
            with redirect_stdout(output):exec(compile(entry['python'],'<atlas program>','exec'),{})
            self.assertEqual(list(map(str,ast.literal_eval(output.getvalue()))),entry['terms'][:16],entry['id'])
            raw=list(map(int,entry['terms']))
            for link in entry['connections']:
                values={'absolute values':list(map(abs,raw)),'alternating signs':[(-1)**n*v for n,v in enumerate(raw)],'first differences':[raw[n]-raw[n-1] for n in range(1,64)],'partial sums':[sum(raw[:n+1]) for n in range(64)]}[link['transform']]
                self.assertEqual(list(map(str,values[:12])),lookup[link['id']]['terms'][link['target_start']:link['target_start']+12])
        self.assertTrue(any(x['id']=='KSEQ-000029' for x in lookup['KSEQ-000027']['connections']))

    def test_reference_definitions_against_distinct_counting_oracles(self):
        catalan=[1]
        for n in range(1,32):catalan.append(sum(catalan[k]*catalan[n-1-k] for k in range(n)))
        self.assertEqual(terms({'kind':'catalan'},32),catalan)
        self.assertEqual(terms({'kind':'central-binomial'},32),[sum(comb(n,k)**2 for k in range(n+1)) for n in range(32)])
        self.assertEqual(terms({'kind':'square'},64),[sum(2*k+1 for k in range(n)) for n in range(64)])
        self.assertEqual(terms({'kind':'triangular'},64),[sum(range(n+1)) for n in range(64)])
        self.assertEqual(terms({'kind':'partition'},11),[1,1,2,3,5,7,11,15,22,30,42])

    def test_reciprocals_against_ordinary_rational_series(self):
        count = 16
        for N in range(2, 9):
            denominator = [Fraction((-1)**k, factorial(N*k)) for k in range(count)]
            inverse = [Fraction(1)]
            for n in range(1, count):
                inverse.append(-sum(denominator[k]*inverse[n-k] for k in range(1, n+1)))
            power = [Fraction(1)]+[Fraction(0)]*(count-1)
            for r in range(1, 4):
                power = [sum(power[k]*inverse[n-k] for k in range(n+1)) for n in range(count)]
                self.assertEqual([x*factorial(N*n) for n, x in enumerate(power)], list(reciprocal(N, r, count)), (N,r))
        self.assertEqual(reciprocal(2,1,6), (1,1,5,61,1385,50521))
        self.assertEqual(reciprocal(4,1,5), (1,1,69,33661,60376809))

    def test_counting_families_against_binomial_recurrences(self):
        bell, fubini = [1], [1]
        for n in range(1, 32):
            bell.append(sum(comb(n-1,k)*bell[k] for k in range(n)))
            fubini.append(sum(comb(n,k)*fubini[n-k] for k in range(1,n+1)))
        self.assertEqual(terms({'kind':'bell'},32), bell)
        self.assertEqual(terms({'kind':'fubini'},32), fubini)
        self.assertEqual(bell[:6], [1,1,2,5,15,52])
        self.assertEqual(fubini[:6], [1,1,3,13,75,541])

    def test_snapshot_scans_all_positions_and_records_finite_scope(self):
        with tempfile.TemporaryDirectory() as folder:
            base=Path(folder)
            with gzip.open(base/'stripped.gz','wt') as f:
                f.write('# fixture\nA000001 ,99,1,2,3,4,5,6,7,8,9,\nA000002 ,1,2,3,4,5,6,99,\nA000003 ,1,2,3,4,5,\n')
            with gzip.open(base/'names.gz','wt') as f:
                f.write('A000001 Fixture one\nA000002 Fixture two\n')
            report=compare(base/'stripped.gz',base/'names.gz',[{'id':'fixture','terms':list(map(str,range(1,10)))}])
            self.assertEqual(report['sequence_count'],3)
            self.assertEqual([(m['id'],m['position'],m['matched_terms']) for m in report['matches']['fixture']], [('A000001',1,9),('A000002',0,6)])
            self.assertEqual(report['matches']['fixture'][0]['name'],'Fixture one')

    def test_retained_snapshot_matches_current_catalogue(self):
        path=ROOT/'manifests/sequence-atlas-oeis.json'
        if not path.exists():
            self.skipTest('Bulk snapshot not supplied; UI labels it unavailable')
        report=json.loads(path.read_text(encoding='utf-8'))
        signature=hashlib.sha256(json.dumps([(e['id'],e['terms']) for e in catalogue()],separators=(',',':')).encode()).hexdigest()
        self.assertEqual(report['catalogue_terms_sha256'],signature)
        self.assertGreater(report['sequence_count'],100000)
        self.assertEqual(report['license'],'CC-BY-SA-4.0')
        for entry in catalogue()[26:]:
            self.assertTrue(any(m['id']==entry['oeis'] and m['position']==0 and m['matched_terms']==12 for m in report['matches'][entry['id']]),entry['id'])

    def test_generated_catalogue_pages_and_exact_exports(self):
        with tempfile.TemporaryDirectory() as folder:
            site=Site.__new__(Site);site.root=ROOT;site.output=Path(folder);site.search=[]
            result=build(site)
            self.assertEqual(result['entries'],38)
            main=(site.output/'sequence-explorer.html').read_text(encoding='utf-8')
            self.assertIn('<h1>Curated sequence generators</h1>',main)
            handoff=(site.output/'sequences.html').read_text(encoding='utf-8')
            self.assertIn('sequence-redirect.mjs',handoff)
            for anchor in ('find','catalogue','saved','explorer','discover','connections','reference'):
                self.assertIn('id="'+anchor+'"',handoff)
            self.assertEqual(result['library']['entries'],2327)
            # One research entry point, without duplicating the exact catalogue.
            research_desk=(site.output/'sequence-library.html').read_text(encoding='utf-8')
            self.assertIn('id="sequence-research-desk"',research_desk)
            self.assertIn('id="closed-calculator-panel"',research_desk)
            self.assertIn('id="sequence-research-hub"',research_desk)
            self.assertIn('id="sequence-proof-path"',research_desk)
            self.assertIn('id="sl-theorem-disclosure"',research_desk)
            self.assertIn('sequence-closed-forms.css',research_desk)
            self.assertEqual(research_desk.count('id="closed-calculator-panel"'),1)
            focused=(site.output/'sequence-closed-forms.html').read_text(encoding='utf-8')
            self.assertEqual(focused.count('id="closed-calculator-panel"'),1)
            mathematical=(site.output/'sequence-differential-hankel.html').read_text(encoding='utf-8')
            self.assertIn('id="differential-hankel-reading"',mathematical)
            self.assertIn('id="math-proof-1-moments-and-operator"',mathematical)
            self.assertIn('class="arithmatex sl-math-display"',mathematical)
            self.assertIn('Full differential Hankel mathematical derivation',mathematical)
            self.assertIn('cf-mode=differential_hankel',mathematical)
            self.assertIn('cf-mode=differential_moments',mathematical)
            self.assertIn('id="math-proof-algebraic-ordinary-generating-function-for-every-finite-differential-operator"',mathematical)
            self.assertIn('1+2z-8z^2-4z^3+52z^4',mathematical)
            self.assertIn('math-proof',mathematical)
            self.assertIn('sequence-closed-forms.css',mathematical)
            self.assertIn('sequence-differential-hankel.html',focused)
            self.assertIn('class="sl-proof-outline"',mathematical)
            self.assertIn('<span class="arithmatex">',mathematical)
            self.assertIn('aria-label="Scrollable code example"',mathematical)
            self.assertIn('sizes 0 through 64',mathematical)
            for asset,dependency in [
                ('sequence-closed-forms-core.mjs','sequence-differential-hankel.mjs'),
                ('sequence-closed-forms-worker.mjs','sequence-closed-forms-core.mjs'),
                ('sequence-closed-forms-ui.mjs','sequence-closed-forms-worker.mjs'),
            ]:
                self.assertIn('./'+dependency+'?v=',(site.output/'assets'/asset).read_text())
            from zipfile import ZipFile
            with ZipFile(site.output/'assets/sequence-formula-source.zip') as bundle:
                for asset in ('sequence-closed-forms-core.mjs','sequence-differential-hankel.mjs'):
                    name='website/assets/'+asset
                    self.assertEqual(bundle.read(name),(ROOT/name).read_bytes())

            direct=(site.output/'sequence-families/KFOR-CF-JET-01.html').read_text(encoding='utf-8')
            self.assertIn('cf-mode=jet',direct)
            self.assertIn('cf-lambda=1',direct)
            self.assertIn('Recalculate this sequence in the unified exact workspace',direct)

            self.assertIn('<noscript>',main)
            self.assertIn('CC BY-SA 4.0',main)
            self.assertEqual(main.count('data-index-entry='),38)
            self.assertIn('aria-label="Alphabetical sequence index"',main)
            graph=json.loads((site.output/'assets/sequence-atlas-connections.json').read_text(encoding='utf-8'))
            self.assertEqual(len(graph['edges']),7)
            import csv
            index=list(csv.DictReader((site.output/'assets/sequence-atlas-index.csv').read_text(encoding='utf-8').splitlines()))
            self.assertEqual([row['id'] for row in index],[entry['id'] for entry in catalogue()])
            self.assertEqual(index[0]['connections_in'],'2')
            self.assertNotIn('data-side-reader-link',main)
            for identifier in ('sa-query','sa-search-form','sa-results','sa-search-error','sa-previous-point','sa-next-window','sa-table-detail'):
                self.assertIn('id="'+identifier+'"',main)
            self.assertIn('role="search"',main)
            self.assertIn('value="mod-pairs"',main)
            pages={}
            for path in site.output.rglob('*.html'):
                source=path.read_text(encoding='utf-8');page=Page(source)
                self.assertEqual((page.h1,page.main),(1,1),str(path))
                self.assertEqual(len(page.ids),len(set(page.ids)))
                self.assertTrue(page.skip)
                for control in page.inputs:
                    self.assertTrue(control.get('id') in page.labels or control.get('aria-label'),control)
                pages[path.relative_to(site.output).as_posix()]=page
            for name,page in pages.items():
                for href in page.links:
                    parts=urlsplit(href)
                    if parts.scheme or parts.netloc:continue
                    target=posixpath.normpath(posixpath.join(posixpath.dirname(name),parts.path)) if parts.path else name
                    if target in pages and parts.fragment:
                        self.assertIn(unquote(parts.fragment),pages[target].ids,(name,href))
            check_search_targets(site.search,pages)
            data=json.loads((site.output/'assets/sequence-atlas-data.json').read_text(encoding='utf-8'))
            for entry in data['entries']:
                self.assertEqual(entry['terms'],list(map(str,terms(entry))))
                if entry['kind']=='euler':
                    self.assertEqual(entry['work_ids'],['paper-iv'])
                lines=(site.output/'sequences'/f"{entry['id']}.csv").read_text().splitlines()
                self.assertEqual(len(lines),65)
                self.assertEqual(lines[-1],f"63,{entry['terms'][63]}")
                indexed=(site.output/'sequences'/f"{entry['id']}.txt").read_text().splitlines()
                self.assertEqual(indexed[-1],f"63 {entry['terms'][63]}")
                self.assertEqual(len([line for line in indexed if not line.startswith('#')]),64)
                exported=json.loads((site.output/'sequences'/f"{entry['id']}.json").read_text(encoding='utf-8'))
                self.assertEqual(exported['terms'],entry['terms'])
                self.assertEqual(exported['oeis_reference']['license'],'CC-BY-SA-4.0')
                source=(site.output/'sequences'/f"{entry['id']}.html").read_text(encoding='utf-8')
                self.assertIn('Related entries',source)
                self.assertIn('data-save-sequence="'+entry['id']+'"',source)
                self.assertEqual('rel="prev"' in source,entry['id']!='KSEQ-000001')
                self.assertEqual('rel="next"' in source,entry['id']!='KSEQ-000038')
                self.assertIn('id="programs"',source)
                self.assertIn('id="connections"',source)
                expected=sum(connection_counts(graph,entry['id']))
                self.assertEqual(source.count('data-connection-key='),expected)
                self.assertIn('id="analysis"',source)
                self.assertIn('aria-label="Backward difference table"',source)
                self.assertIn('n=0–11',source)
                self.assertIn('A constant difference row or a transform match does not establish an infinite identity.',source)
                if entry['source'].startswith('collection/'):
                    target=entry['source'].split('#')[0].replace('collection/','docs/').replace('.html','.md')
                    self.assertTrue((ROOT/target).is_file(),target)
            script=(site.output/'assets/sequence-atlas.js').read_text(encoding='utf-8')
            self.assertIn('./sequence-atlas-search.mjs?v=',script)
            self.assertIn('./sequence-atlas-directory.mjs?v=',script)
            self.assertIn('./sequence-atlas-saved.mjs?v=',script)
            self.assertIn('./sequence-atlas-saved.mjs?v=',(site.output/'assets/sequence-atlas-entry.js').read_text(encoding='utf-8'))
            self.assertIn('./sequence-atlas-study.js?v=',(site.output/'assets/sequence-atlas-entry.js').read_text(encoding='utf-8'))
            self.assertIn('./sequence-atlas-study.mjs?v=',(site.output/'assets/sequence-atlas-study.js').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
