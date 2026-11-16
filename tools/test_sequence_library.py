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
        report=checks();self.assertEqual(report['records'],2034);self.assertEqual(report['terms'],52579)
        self.assertEqual(report['checks']['source_index_maps'],52579)

    def test_unified_records_preserve_old_ids_offsets_and_formula_types(self):
        entries=library_entries(catalogue());self.assertEqual(len(entries),2162);self.assertEqual(len({x['id'] for x in entries}),2162)
        self.assertEqual(sum(len(x['formulas']) for x in entries),6501)
        self.assertTrue(all(len(x['terms'])==(sum(x['triangle']['row_lengths']) if x.get('triangle') else 24) for x in expanded_catalogue()))
        self.assertTrue(any(x['offset']==2 for x in entries))
        for kind in ['reciprocal','catalan','central-binomial']:
            entry=next(x for x in catalogue() if x['kind']==kind)
            self.assertTrue(any(f['kind']=='hypergeometric' for f in formula_variants(entry)))

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
