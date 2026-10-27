"""Verify the preserved source and the one declared proposition clarification.

The separately delivered predecessor ZIP is identified, not redistributed here.
This checks preservation and declared edits, not mathematical proof validity.
"""
from pathlib import Path
import hashlib
import json
import re
ROOT = Path(__file__).resolve().parents[1]
PATTERN = r'\*\*Proposition (\d+)\..*?\\square\$'

def spans(text: str) -> dict[int, str]:
    matches = list(re.finditer(PATTERN, text, re.S))
    result = {int(m.group(1)): m.group(0) for m in matches}
    if len(matches) != len(result): raise ValueError('Duplicate proposition number.')
    return result

def main() -> None:
    lineage = json.loads((ROOT/'SOURCE_LINEAGE.json').read_text())
    before_file = ROOT/lineage['preserved_prose']
    digest = hashlib.sha256(before_file.read_bytes()).hexdigest()
    if digest != lineage['preserved_prose_sha256']:
        raise ValueError('Preserved predecessor prose changed.')
    before = spans(before_file.read_text(encoding='utf-8'))
    after = spans((ROOT/'theory/FOUNDATIONS.md').read_text(encoding='utf-8'))
    expected = set(range(1,88))
    if set(before) != expected or set(after) != expected:
        raise ValueError('Expected exactly propositions 1 through 87 in both sources.')
    changed = [i for i in sorted(expected) if before[i] != after[i]]
    if changed != [72]: raise ValueError(f'Unexpected changed proposition spans: {changed}')
    marker = '** '
    corrected = before[72].replace(marker, marker + r'Assume $d\geq1$. ', 1)
    if after[72] != corrected:
        raise ValueError('Proposition 72 has edits beyond its declared dimension hypothesis.')
    result = {'passed':True, 'propositions':87, 'byte_identical_statement_proof_spans':86,
              'changed_ids':[72], 'change':'Explicit spatial dimension d >= 1',
              'preserved_prose_sha256':digest, 'predecessor_archive_embedded':False,
              'proof_kernel_verification':False}
    (ROOT/'verification/source_lineage_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__ == '__main__': main()
