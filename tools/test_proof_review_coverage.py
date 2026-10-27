"""Negative checks for review-count inflation and stale evidence."""
import copy
import unittest
from proof_review_coverage import build_coverage, extract_pairs


SOURCE = r'''\begin{proposition}[First]\label{prop:first}
A claim.
\end{proposition}
\begin{proof}An argument.\end{proof}
\begin{theorem}[Second]\label{thm:second}
Another claim.
\end{theorem}
\begin{proof}Another argument.\end{proof}
\begin{proposition}[Third]\label{prop:third}
An unreviewed claim.
\end{proposition}
\begin{proof}An unreviewed argument.\end{proof}'''


class CoverageTests(unittest.TestCase):
    def records(self):
        pairs = extract_pairs(SOURCE)
        return [('a.json', {'cards': [{**pairs['prop:first'], 'verdict': 'proved as written'}]}),
                ('b.json', {'cards': [{**pairs['thm:second'], 'verdict': 'correct only after a stated restriction'}]})]

    def test_qualified_and_unreviewed_are_not_passes(self):
        result = build_coverage(SOURCE, self.records())
        self.assertEqual(result['counts'], {'total': 3, 'reviewed': 2, 'proved_as_written': 1, 'qualified': 1, 'unreviewed': 1})
        self.assertEqual(result['entries'][2]['verdict'], 'unreviewed')
        self.assertNotIn('review_record', result['entries'][2])

    def test_repeated_claim_cannot_inflate_coverage(self):
        records = self.records()
        records.append(('c.json', copy.deepcopy(records[0][1])))
        with self.assertRaisesRegex(AssertionError, 'Duplicate reviewed label'):
            build_coverage(SOURCE, records)

    def test_changed_argument_invalidates_old_review(self):
        with self.assertRaisesRegex(AssertionError, 'Changed proof block'):
            build_coverage(SOURCE.replace('An argument.', 'A different argument.'), self.records())

    def test_unknown_claim_is_rejected(self):
        records = self.records(); records[0][1]['cards'][0]['label'] = 'prop:missing'
        with self.assertRaisesRegex(AssertionError, 'Unknown reviewed label'):
            build_coverage(SOURCE, records)

    def test_unknown_verdict_is_not_silently_promoted(self):
        records = self.records(); records[0][1]['cards'][0]['verdict'] = 'probably fine'
        with self.assertRaisesRegex(AssertionError, 'Unclassified verdict'):
            build_coverage(SOURCE, records)

    def test_missing_proof_does_not_borrow_next_proof(self):
        broken = SOURCE.replace(r'\begin{proof}An argument.\end{proof}', '')
        with self.assertRaisesRegex(AssertionError, 'Missing adjacent proof'):
            build_coverage(broken, [])

    def test_unrecognized_declaration_fails_closed(self):
        with self.assertRaisesRegex(AssertionError, 'Unrecognized declaration'):
            build_coverage(SOURCE.replace(r'\label{prop:first}', ''), [])


if __name__ == '__main__':
    unittest.main()
