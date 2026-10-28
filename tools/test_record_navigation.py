"""Guard against stale coverage, omitted review records, and misplaced closed gates."""
import json
from pathlib import Path
import tempfile
import unittest

from record_navigation import render_record_pages, coverage_summary
from update_completion_status import render


class RecordNavigationTests(unittest.TestCase):
    def fixture(self, root):
        data = {'maintained_documents': [], 'assessment_records': [],
                'reader_curation_reviews': [], 'proof_review_coverage': []}
        (root/'docs').mkdir()
        (root/'manifests').mkdir()
        for name in ['earlier', 'later']:
            report = 'docs/'+name+'.md'
            path = 'manifests/'+name+'.json'
            (root/report).write_text('# '+name.title()+' review\n', encoding='utf-8')
            (root/path).write_text(json.dumps({'as_of': '2026-10-27',
                'report': {'path': report}, 'scope': name+' bounded scope'}), encoding='utf-8')
            data['maintained_documents'].append(report)
            data['assessment_records'].append(path)
            data['reader_curation_reviews'].append({'path': path})
        data['assessment_records'].append('verification/other.json')
        return data

    def test_registered_review_order_and_other_evidence_survive(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pages = render_record_pages(root, self.fixture(root), {'docs/history/old.md'})
            records = pages['docs/RECORDS.md']
            self.assertLess(records.index('earlier.json'), records.index('later.json'))
            self.assertEqual(records.count('(../manifests/earlier.json)'), 1)
            self.assertEqual(records.count('(../manifests/later.json)'), 1)
            self.assertIn('(../verification/other.json)', records)
            self.assertIn('(old.md)', pages['docs/history/README.md'])

    def test_coverage_uses_current_index_without_promoting_qualified_claims(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp); data = self.fixture(root)
            path = 'manifests/coverage.json'
            data['proof_review_coverage'] = [{'path': path}]
            index = {'source': {'path': 'monographs/book.tex'},
                     'counts': {'total': 9, 'reviewed': 4, 'proved_as_written': 2,
                                'qualified': 2, 'unreviewed': 5}}
            (root/path).write_text(json.dumps(index), encoding='utf-8')
            self.assertIn('4 of 9 distinct pairs', coverage_summary(root, data))
            self.assertIn('2 recorded passes, 2 requiring restrictions, and 5 unreviewed', coverage_summary(root, data))
            index['counts'].update(reviewed=5, proved_as_written=3, unreviewed=4)
            (root/path).write_text(json.dumps(index), encoding='utf-8')
            self.assertIn('5 of 9 distinct pairs', coverage_summary(root, data))
            self.assertIn('3 recorded passes, 2 requiring restrictions, and 4 unreviewed', coverage_summary(root, data))

    def test_completed_gate_moves_out_of_open_lane_without_disappearing(self):
        root = Path(__file__).resolve().parents[1]
        data = json.loads((root/'manifests/project-status.json').read_bytes())
        task = next(t for t in data['finalization_queue'] if t['lane'] == 'review')
        task['status'] = 'done'
        queue = render(data)['docs/FINALIZATION_QUEUE.md']
        completed = queue.split('## Completed cleanup and bounded qualification', 1)[1].split('## Next finishing work', 1)[0]
        self.assertIn('### '+task['id']+' —', completed)
        for t in data['finalization_queue']:
            self.assertEqual(queue.count('<a id="'+t['id'].lower()+'"></a>'), 1)
            self.assertIn('](#'+t['id'].lower()+')', queue)


if __name__ == '__main__':
    unittest.main()
