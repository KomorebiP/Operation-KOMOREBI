"""Replay the six preserved mathematical certificates for final edition 1.0."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

PREFIX = 'verification/sequence-library/hankel-compression/'
CHECKS = [
 ('quadratic-sample', 'verify_sequence_quadratic_certificate.py',
  ['--input', PREFIX+'quadratic-certificate.json'], {'minimal_eventual_order': 63, 'recurrence_start': 1}),
 ('mixed-sample', 'verify_sequence_mixed_hankel.py',
  ['--input', PREFIX+'mixed-certificate.json'], {'minimal_eventual_order': 112, 'recurrence_start': 1}),
 ('sharp-quadratic', 'verify_sequence_sharp_quadratic.py', [], {'maximum_coefficient_degree': 6}),
 ('uniform-mixed', 'verify_sequence_uniform_mixed.py',
  ['--sample-certificate', PREFIX+'mixed-certificate.json'], {'sample_minimal_eventual_order': 112}),
 ('boundary', 'verify_sequence_exceptional_hankel.py',
  ['--certificate', PREFIX+'exceptional-certificate.json'], {'parameter_polynomial_families': 4}),
 ('interior', 'verify_sequence_interior_hankel.py',
  ['--coefficients', PREFIX+'interior-coefficients.json', '--certificate', PREFIX+'interior-certificate.json'], {}),
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error('Use a new empty output directory')
    output.mkdir(parents=True, exist_ok=True)
    parent = json.loads((root/(PREFIX+'interior-source-bundle.json')).read_text(encoding='utf-8'))
    assert parent['sha256'] == 'e7a43e634553bf7d814518cd65a14769a2d2094afd8db85e5641675afca52ccd'
    rows = []
    start = time.monotonic()
    for label, name, arguments, expected in CHECKS:
        path = 'tools/'+name
        raw = (root/path).read_text(encoding='utf-8').encode('utf-8')
        digest = hashlib.sha256(raw).hexdigest()
        assert digest == parent['files'][path], 'Preserved replayer changed: '+path
        report = output/(label+'.json')
        command = [sys.executable, '-B', path, *arguments, '--output', str(report)]
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=180)
        (output/(label+'.log')).write_text(result.stdout+result.stderr, encoding='utf-8', newline='\n')
        result.check_returncode()
        data = json.loads(report.read_text(encoding='utf-8'))
        for key, value in expected.items():
            assert data[key] == value, (label, key)
        if label == 'interior':
            assert data['polynomial_leaves']['characteristic_complete_nodes'] == 45
        rows.append({'name': label, 'status': 'passed', 'replayer_sha256': digest,
                     'report_sha256': hashlib.sha256(report.read_bytes()).hexdigest()})
        print(label+': passed', flush=True)
    receipt = {'edition': '1.0', 'status': 'passed', 'checks': rows,
               'source_revision': 'af2d91ead77d06f7903239f1da293e26bb00f240',
               'review_provenance': 'project self-review',
               'scope': 'Replays the retained finite certificate leaves; universal conclusions use the written proofs.',
               'elapsed_seconds': time.monotonic()-start}
    (output/'result.json').write_text(json.dumps(receipt, indent=2)+'\n', encoding='utf-8', newline='\n')
    print(json.dumps({'status': 'passed', 'checks': len(rows), 'elapsed_seconds': receipt['elapsed_seconds']}))

if __name__ == '__main__':
    main()
