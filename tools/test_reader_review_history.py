"""Review-history regressions: earlier decisions and evidence must survive."""
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from update_completion_status import validate_reader_reviews


class ReviewHistoryTests(unittest.TestCase):
    def fixture(self, root):
        data = {'components': [], 'assessment_records': [], 'maintained_documents': [],
                'reader_curation_reviews': []}
        def write(path, content):
            (root/path).write_bytes(content)
            return {'path': path, 'sha256': hashlib.sha256(content).hexdigest()}
        for name in ['earlier', 'later']:
            report = write(name+'.md', b'Review')
            computation = write(name+'-run.json', b'{}')
            review = {'source_revision': name, 'report': report, 'computation': computation,
                      'reviewed_sources': [{'path': name+'.py', 'sha': name+'-source'}],
                      'decisions': [{'id': name, 'placement': 'incubator'}]}
            binding = write(name+'.json', json.dumps(review).encode())
            data['maintained_documents'].append(report['path'])
            data['assessment_records'] += [binding['path'], computation['path']]
            data['reader_curation_reviews'].append(binding)
            data['components'].append({'id': name, 'reader_listing': {'placement': 'incubator', 'review': report['path']}})
        return data

    def validate(self, root, data, current=None):
        sources = {'earlier.py': 'earlier-source', 'later.py': 'later-source'}
        with patch('update_completion_status.git_tree', return_value=sources):
            validate_reader_reviews(root, data, {'earlier', 'later'}, sources if current is None else current, 'git')

    def test_two_reviews_preserve_both_incubator_decisions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.validate(root, self.fixture(root))

    def test_written_review_does_not_require_a_computation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=self.fixture(root)
            path=root/'later.json';review=json.loads(path.read_text())
            review.pop('computation');path.write_text(json.dumps(review))
            data['reader_curation_reviews'][1]['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
            self.validate(root,data)

    def test_later_review_can_return_an_entry_to_reading_list(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);data=self.fixture(root)
            path=root/'later.json';review=json.loads(path.read_text())
            review['decisions'].append({'id':'earlier','placement':'retain'})
            path.write_text(json.dumps(review))
            data['reader_curation_reviews'][1]['sha256']=hashlib.sha256(path.read_bytes()).hexdigest()
            data['components'][0].pop('reader_listing')
            self.validate(root,data)

    def test_dropped_earlier_review_cannot_silently_erase_binding(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); data=self.fixture(root)
            data['reader_curation_reviews'].pop(0)
            with self.assertRaisesRegex(AssertionError, 'review history'):
                self.validate(root,data)

    def test_changed_report_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); data=self.fixture(root)
            (root/'earlier.md').write_text('Changed')
            with self.assertRaisesRegex(AssertionError, 'earlier.md'):
                self.validate(root,data)

    def test_changed_reviewed_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); data=self.fixture(root)
            with self.assertRaisesRegex(AssertionError, 'Reassess changed reviewed source'):
                self.validate(root,data,{'earlier.py': 'changed', 'later.py': 'later-source'})

    def test_listing_must_link_the_deciding_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); data=self.fixture(root)
            data['components'][0]['reader_listing']['review']='later.md'
            with self.assertRaises(AssertionError):self.validate(root,data)


if __name__ == '__main__':
    unittest.main()
