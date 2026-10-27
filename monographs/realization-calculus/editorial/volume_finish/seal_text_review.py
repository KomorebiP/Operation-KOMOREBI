"""Combine exact-line editorial decisions for the actual finished volume."""
from pathlib import Path
from collections import Counter
import hashlib
import json
import fitz

ROOT = Path(__file__).resolve().parents[2]
D = ROOT / 'editorial/volume_finish'


def load(name):
    return json.loads((D / name).read_text())


def key(row):
    return tuple(row.get(k) for k in
                 ('book_page', 'component_id', 'source_page', 'reference', 'text'))


def main():
    candidate = load('final_text_candidates.json')
    with (ROOT / 'output/Realization_Calculus.pdf').open('rb') as stream:
        digest = hashlib.file_digest(stream, 'sha256').hexdigest()
    assert candidate['pdf_sha256'] == digest
    assert not candidate['bookmark_matches']
    decisions = []
    reports = []
    for name, field in [('final_candidate_review_i_viii.json', 'text_decisions'),
                        ('final_candidate_review_ix_xii.json', 'decisions')]:
        report = load(name)
        assert report['status'] == 'PASS' and report['pdf_sha256'] == digest, name
        for row in report[field]:
            assert row['decision'].lower() == 'retain', row
            decisions.append(row)
        reports.append({'path': str((D / name).relative_to(ROOT)),
                        'sha256': hashlib.sha256((D / name).read_bytes()).hexdigest()})
    with fitz.open(ROOT / 'output/Realization_Calculus.pdf') as document:
        for row in candidate['matches']:
            if row['component_id'] != 'outer':
                continue
            text = document[row['book_page'] - 1].get_text()
            assert row['text'] in text
            if 'Infinite versions require a specified convergence mode' in row['text']:
                reason = ('The glossary distinguishes infinite packet analysis and synthesis '
                          'from finite inverse isomorphisms, retaining the convergence and bound hypotheses.')
            elif 'version, generation is replaced by dense generation.' in row['text']:
                reason = ('The glossary distinguishes topological seed rank, defined by dense '
                          'generation, from algebraic generation. This is mathematical terminology.')
            else:
                raise AssertionError(('Unreviewed outer candidate', row))
            decisions.append({**row, 'decision': 'retain', 'category': 'mathematical_variant',
                              'reason': reason, 'context_sha256': hashlib.sha256(text.encode()).hexdigest()})
    expected = Counter(key(row) for row in candidate['matches'])
    actual = Counter(key(row) for row in decisions)
    assert expected == actual, {'missing': list((expected - actual).elements()),
                                'extra': list((actual - expected).elements())}
    record = {'schema': 'realization-calculus.final-text-review/1', 'status': 'PASS',
              'pdf_sha256': digest, 'pages': candidate['pages'],
              'scope': 'Every publication-history scan candidate in the actual finished book '
                       'has an exact-line editorial decision. Mathematical variants, valuations, '
                       'folio numbers, precise back-reference identities, scope qualifications '
                       'and a protected literal source contract are retained. This is not a proof audit.',
              'candidate_count': sum(expected.values()), 'classified_count': len(decisions),
              'bookmark_candidates': 0, 'actionable_publication_history_findings': [],
              'decision_sources': reports, 'decisions': decisions}
    (D / 'final_text_review.json').write_text(json.dumps(record, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({k: v for k, v in record.items() if k != 'decisions'}, indent=2))


if __name__ == '__main__':
    main()
