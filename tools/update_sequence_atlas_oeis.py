"""Compare the curated catalogue against official, locally supplied OEIS exports.

python -B tools/update_sequence_atlas_oeis.py --stripped PATH --names PATH
This scans exported terms only; absence of a match is not a novelty result.
"""
import argparse
from collections import defaultdict
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path

from sequence_atlas import ROOT, catalogue


def compare(stripped, names, entries):
    index = defaultdict(list)
    for entry in entries:
        index[tuple(entry['terms'][:6])].append(entry)
    matches = {entry['id']: [] for entry in entries}
    headers, count = [], 0
    with gzip.open(stripped, 'rt', encoding='utf-8') as source:
        for line in source:
            if line.startswith('#'):
                headers.append(line.strip())
                continue
            if not line.strip():
                continue
            identifier, raw = line.split(None, 1)
            if not identifier.startswith('A') or not identifier[1:].isdigit():
                raise ValueError('Malformed OEIS identifier')
            values = [str(int(v)) for v in raw.strip().strip(',').split(',')]
            count += 1
            for position in range(len(values)-5):
                for entry in index.get(tuple(values[position:position+6]), []):
                    length = 6
                    while length < min(12, len(entry['terms']), len(values)-position) and entry['terms'][length] == values[position+length]:
                        length += 1
                    matches[entry['id']].append(dict(id=identifier, position=position, matched_terms=length))
    wanted = {m['id'] for group in matches.values() for m in group}
    titles = {}
    with gzip.open(names, 'rt', encoding='utf-8') as source:
        for line in source:
            if line.startswith('#') or not line.strip():
                continue
            identifier, name = line.rstrip().split(None, 1)
            if identifier in wanted:
                titles[identifier] = name
    for group in matches.values():
        for match in group:
            match['name'] = titles.get(match['id'], 'Name unavailable in the supplied names export')
        group.sort(key=lambda m: (-m['matched_terms'], m['id'], m['position']))
    signature = hashlib.sha256(json.dumps([(e['id'], e['terms']) for e in entries], separators=(',', ':')).encode()).hexdigest()
    return dict(schema=1, retrieved_at=datetime.now(timezone.utc).isoformat(), sequence_count=count,
        method='Exact contiguous comparison of the first six catalogue terms; extend each hit through at most twelve terms. Every exported position is scanned. Mathematical offsets are not present in stripped.gz.',
        source_urls=['https://oeis.org/stripped.gz', 'https://oeis.org/names.gz'],
        license='CC-BY-SA-4.0', attribution='The Online Encyclopedia of Integer Sequences, OEIS Foundation Inc.',
        headers=headers, stripped_sha256=hashlib.sha256(Path(stripped).read_bytes()).hexdigest(),
        names_sha256=hashlib.sha256(Path(names).read_bytes()).hexdigest(), catalogue_terms_sha256=signature,
        matches=matches,
        non_claims=['No mathematical sequence identity proved', 'No sequence or formula novelty established', 'No full OEIS search service hosted'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stripped', type=Path, required=True)
    parser.add_argument('--names', type=Path, required=True)
    parser.add_argument('--output', type=Path, default=ROOT/'manifests/sequence-atlas-oeis.json')
    args = parser.parse_args()
    previous=json.loads(args.output.read_text(encoding='utf-8')) if args.output.exists() else {}
    report = compare(args.stripped, args.names, catalogue())
    report['compared_at']=report['retrieved_at']
    if all(previous.get(key)==report[key] for key in ('stripped_sha256','names_sha256')):
        report['retrieved_at']=previous['retrieved_at']
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps(dict(sequences_scanned=report['sequence_count'], entries=len(report['matches']), matches=sum(map(len, report['matches'].values())), output=str(args.output))))
