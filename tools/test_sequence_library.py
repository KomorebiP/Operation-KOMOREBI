import gzip
import json
from pathlib import Path
import tempfile
import unittest
from audit_sequence_library import checks
from sequence_atlas import catalogue
from sequence_library import library_entries
from sequence_formula_catalogue import formula_variants,expanded_catalogue
from update_sequence_library_oeis import compare


class SequenceLibraryTests(unittest.TestCase):
    def test_complete_parameter_windows_and_independent_formulas(self):
        report=checks();self.assertEqual(report['records'],2164);self.assertEqual(report['terms'],55939)
        self.assertEqual(report['checks']['source_index_maps'],55939)

    def test_unified_records_preserve_old_ids_offsets_and_formula_types(self):
        entries=library_entries(catalogue());self.assertEqual(len(entries),2292);self.assertEqual(len({x['id'] for x in entries}),2292)
        self.assertEqual(sum(len(x['formulas']) for x in entries),7033)
        self.assertTrue(all(len(x['terms'])==(sum(x['triangle']['row_lengths']) if x.get('triangle') else 48 if x['id'].startswith('KFOR-KB-') else 24) for x in expanded_catalogue()))
        self.assertTrue(any(x['offset']==2 for x in entries))
        for kind in ['reciprocal','catalan','central-binomial']:
            entry=next(x for x in catalogue() if x['kind']==kind)
            self.assertTrue(any(f['kind']=='hypergeometric' for f in formula_variants(entry)))

    def test_formula_source_degrees_follow_the_existing_exact_index_map(self):
        from sequence_library import source_degree
        entries=library_entries(catalogue())
        formulas=[item for item in entries if item['collection']=='formulas']
        self.assertEqual(len(formulas),2164)
        self.assertEqual(sum(len(item['terms']) for item in formulas),55939)
        by_id={item['id']:item for item in formulas}
        for item in formulas:
            degrees=[source_degree(item,item['offset']+i) for i in range(len(item['terms']))]
            self.assertEqual(len(degrees),len(item['terms']))
            self.assertTrue(all(isinstance(degree,int) and degree>=0 for degree in degrees))
        self.assertEqual(source_degree(by_id['KFOR-P-03-02'],2),6)
        self.assertEqual(source_degree(by_id['KFOR-P-03-02'],3),9)
        self.assertEqual(source_degree(by_id['KFOR-TRI-P-03'],5),6)
        self.assertEqual(source_degree(by_id['KFOR-HC-04'],2),4)
        self.assertNotIn('source_degrees',next(item for item in entries if item['collection']=='atlas'))

    def test_research_tools_have_disjoint_reading_sections(self):
        from sequence_generalized import sections
        ids=('generalized','research-graph','identify','modular-dynamics','research-notebooks')
        complete=sections()
        for identifier in ids:
            part=sections(only=[identifier])
            self.assertIn('id="'+identifier+'"',part)
            self.assertEqual(part.count('<section id='),1)
            self.assertIn(part,complete)
            self.assertTrue(part.endswith('</section>'))
        self.assertEqual(sections(only=['generalized','research-graph']).count('<section id='),2)
        with self.assertRaises(ValueError):
            sections(only=['missing-tool'])

    def test_research_family_directory_covers_all_indexed_records(self):
        from collections import Counter
        entries=library_entries(catalogue())
        research=[item for item in entries if 'research-derived' in item['tags']]
        counts=Counter(item['kind'] for item in research)
        expected={
            'secancy parameter column':88,
            'secancy coefficient triangle':11,
            'Euler-transfer theta':12,
            'theta polynomial column':12,
            'theta coefficient triangle':1,
            'block-Appell coefficient triangle':21,
            'block-Appell coefficient column':84,
            'k-step reciprocal power':120,
            'k-bonacci':10,
        }
        self.assertEqual(counts,expected)
        self.assertEqual(sum(counts.values()),359)
        self.assertEqual(len({item['id'] for item in research}),359)

    def test_research_windows_keep_real_indices_and_ordinary_polynomial_coefficients(self):
        from sequence_formula_catalogue import secancy_polynomials,theta_polynomial_rows
        from sequence_library import source_degree
        self.assertEqual(secancy_polynomials(3,3)[2],(0,9,10))
        self.assertEqual(theta_polynomial_rows(4)[3],(0,-16,-30,-45,-45,-75,-61))
        entries={e['id']:e for e in expanded_catalogue()}
        for key,offset,degree,first in [('KFOR-P-03-02',2,6,'10'),('KFOR-H-02',0,0,'1'),('KFOR-HC-04',2,4,'5')]:
            e=entries[key];self.assertEqual(e['offset'],offset);self.assertEqual(e['terms'][0],first);self.assertEqual(source_degree(e,offset),degree);self.assertIn('research-derived',e['tags']);self.assertIn('novelty unassessed',e['status'])
        self.assertEqual(entries['KFOR-H-02']['terms'][:4],['1','-6','144','-7536'])

    def test_full_triangles_retain_zeros_coordinates_and_source_degrees(self):
        from sequence_research_tables import research_additions,cell_coordinates,exact_integer
        from fractions import Fraction
        from sequence_library import source_degree
        with self.assertRaises(ValueError):exact_integer(Fraction(3,2))
        self.assertEqual(exact_integer(Fraction(4,2)),2)
        entries={item['id']:item for item in research_additions()}
        self.assertEqual(len(entries),139)
        self.assertEqual(sum('triangle' in item for item in entries.values()),55)
        p=entries['KFOR-TRI-P-03'];self.assertEqual(p['terms'][:6],['1','0','1','0','9','10'])
        self.assertEqual(cell_coordinates(p,5),(2,2));self.assertEqual(source_degree(p,5),6)
        theta=entries['KFOR-TRI-H'];self.assertEqual(theta['terms'][:9],['1','0','-1','-1','0','2','3','6','5'])
        self.assertEqual(cell_coordinates(theta,8),(2,4));self.assertEqual(source_degree(theta,8),4)
        column=entries['KFOR-AC-03-01-02'];self.assertEqual(column['terms'][:2],['1','-10']);self.assertEqual(source_degree(column,1),5)

    def test_connection_equations_retain_exact_indices_and_static_readability(self):
        from sequence_research_notes import research_connections
        from sequence_research_tables import research_additions,triangle_section
        edges=research_connections()['edges']
        def edge(kind,target):
            return next(e for e in edges if e['kind']==kind and e['target']==target)
        self.assertTrue(next(e['math_plain'] for e in edges if e['kind']=='subsequence').startswith('b(n)=a('))
        self.assertIn(r'\Theta_{2n}',edge('coefficient extraction','KFOR-HC-04')['math_tex'])
        self.assertIn(r'E_{3n+2}',edge('coefficient extraction','KFOR-AC-03-01-02')['math_tex'])
        self.assertIn(r'\Theta_{2n}(2)',edge('polynomial evaluation','KFOR-H-02')['math_tex'])
        self.assertIn(r'\delta_{n,k}',edge('inverse matrices','KFOR-TRI-BI-03')['math_tex'])
        self.assertTrue(all(e['math_plain'] and e['math_tex'] for e in edges if e['kind'] in
            ('subsequence','seed shift','coefficient extraction','polynomial evaluation','inverse matrices','ordinary convolution')))
        entries={entry['id']:entry for entry in research_additions()}
        self.assertIn('j=n^2+k',triangle_section(entries['KFOR-TRI-H']))
        self.assertIn(r'\frac{n(n+1)}{2}',triangle_section(entries['KFOR-TRI-P-03']))
        self.assertIn('data-math-latex=',triangle_section(entries['KFOR-TRI-B-03']))

    def test_snapshot_contiguous_matching_extends_and_caps_with_exact_totals(self):
        entry=dict(id='LOCAL',terms=[str(x) for x in range(1,13)])
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)
            with gzip.open(p/'terms.gz','wt',encoding='utf-8') as stream:stream.write('# OEIS fixture\n'+''.join(f'A{i:06d} ,99,1,2,3,4,5,6,7,8,9,10,11,12,\n' for i in range(1,6)))
            with gzip.open(p/'names.gz','wt',encoding='utf-8') as stream:stream.write(''.join(f'A{i:06d} Fixture {i}\n' for i in range(1,6)))
            report=compare(p/'terms.gz',p/'names.gz',[entry],limit=2)
            self.assertEqual(report['sequence_count'],5);self.assertEqual(report['total_matches']['LOCAL'],5);self.assertEqual(len(report['matches']['LOCAL']),2)
            self.assertTrue(all(x['position']==1 and x['matched_terms']==12 for x in report['matches']['LOCAL']))


if __name__=='__main__':unittest.main()
