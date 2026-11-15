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
        report=checks();self.assertEqual(report['records'],1783);self.assertEqual(report['terms'],42792)
        self.assertEqual(report['checks']['source_index_maps'],42792)

    def test_unified_records_preserve_old_ids_offsets_and_formula_types(self):
        entries=library_entries(catalogue());self.assertEqual(len(entries),1911);self.assertEqual(len({x['id'] for x in entries}),1911)
        self.assertEqual(sum(len(x['formulas']) for x in entries),5671)
        self.assertTrue(all(len(x['terms'])==24 for x in expanded_catalogue()))
        self.assertTrue(any(x['offset']==2 for x in entries))
        for kind in ['reciprocal','catalan','central-binomial']:
            entry=next(x for x in catalogue() if x['kind']==kind)
            self.assertTrue(any(f['kind']=='hypergeometric' for f in formula_variants(entry)))

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
