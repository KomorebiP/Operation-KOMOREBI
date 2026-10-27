"""Check review coverage for this manuscript's explicit theorem/proposition format.

This checks provenance and counting, never mathematical truth. Verdicts come
from the bound review records. This is deliberately not a general LaTeX parser.
"""
import hashlib
import json
import re
import subprocess


VERDICTS = {'proved as written': 'proved_as_written',
            'correct only after a stated restriction': 'qualified'}
START = re.compile(r'\\begin\{(theorem|proposition)\}(?:\[[^\n]*\])?\s*\\label\{([^}]+)\}')


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def extract_pairs(text):
    starts = list(START.finditer(text))
    assert len(starts) == len(re.findall(r'\\begin\{(?:theorem|proposition)\}', text)), 'Unrecognized declaration'
    pairs = {}
    for i, match in enumerate(starts):
        label = match.group(2)
        assert label not in pairs, 'Duplicate source label: '+label
        stop = starts[i+1].start() if i+1 < len(starts) else len(text)
        proof = text.find('\\begin{proof}', match.end(), stop)
        end = text.find('\\end{proof}', proof, stop) if proof >= 0 else -1
        assert end >= 0, 'Missing adjacent proof: '+label
        block = text[match.start():end+len('\\end{proof}')]
        pairs[label] = {'label': label, 'source_line': text.count('\n', 0, match.start())+1,
                        'statement_and_proof_sha256': digest(block.encode('utf-8'))}
    return pairs


def build_coverage(text, records):
    pairs = extract_pairs(text)
    reviewed = {}
    for path, record in records:
        for card in record['cards']:
            label = card['label']
            assert label in pairs, 'Unknown reviewed label: '+label
            assert label not in reviewed, 'Duplicate reviewed label: '+label
            assert card['statement_and_proof_sha256'] == pairs[label]['statement_and_proof_sha256'], 'Changed proof block: '+label
            assert card['source_line'] == pairs[label]['source_line'], 'Changed source line: '+label
            assert card['verdict'] in VERDICTS, 'Unclassified verdict: '+label
            reviewed[label] = {'review_record': path, 'verdict': card['verdict']}
    entries = [{**pair, **reviewed.get(label, {'verdict': 'unreviewed'})} for label, pair in pairs.items()]
    counts = {'total': len(pairs), 'reviewed': len(reviewed), 'proved_as_written': 0,
              'qualified': 0, 'unreviewed': len(pairs)-len(reviewed)}
    for card in reviewed.values():
        counts[VERDICTS[card['verdict']]] += 1
    return {'counts': counts, 'entries': entries}


def validate_coverage(root, binding, git, current):
    raw = (root/binding['path']).read_bytes()
    assert digest(raw) == binding['sha256'], 'Coverage index binding changed'
    index = json.loads(raw)
    source = index['source']
    assert current.get(source['path']) == source['git_blob_sha1'], 'Coverage source changed'
    # Git blobs avoid sparse-checkout absence and checkout newline conversion.
    source_raw = subprocess.check_output([git, 'cat-file', 'blob', source['git_blob_sha1']], cwd=root)
    assert digest(source_raw) == source['sha256'], 'Coverage source digest mismatch'
    records = []
    seen = set()
    for item in index['review_records']:
        path = item['path']
        assert path not in seen, 'Duplicate coverage record'
        seen.add(path)
        if 'git_blob_sha1' in item:
            assert current.get(path) == item['git_blob_sha1'], 'Imported review changed'
            record_raw = subprocess.check_output([git, 'cat-file', 'blob', item['git_blob_sha1']], cwd=root)
        else:
            record_raw = (root/path).read_bytes()
        assert digest(record_raw) == item['sha256'], 'Coverage record digest mismatch: '+path
        record = json.loads(record_raw)
        if 'source_sha256' in record:
            assert record['source_sha256'] == source['sha256'], 'Review covers another source'
        else:
            sources = {s['path']: s for s in record['reviewed_sources']}
            assert sources[source['path']]['sha256'] == source['sha256'], 'Review covers another source'
        records.append((path, record))
    computed = build_coverage(source_raw.decode('utf-8'), records)
    assert index['counts'] == computed['counts'], 'Coverage counts differ from bound cards'
    assert index['entries'] == computed['entries'], 'Coverage entries differ from bound cards'
    return computed['counts']
