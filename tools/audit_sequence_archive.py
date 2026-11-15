"""Reproduce every recovered record and audit its indexed serialization."""
import argparse
import csv
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

from sequence_archive import SOURCE, records, bfile
from sequence_atlas import catalogue


def audit():
    sys.path.insert(0,str(SOURCE))
    import generate_candidates as generator
    generated=generator.create_catalog()
    controls=generator.independent_tests(generated)
    recovered=json.loads((SOURCE/'candidate_registry.json').read_bytes())
    assert [asdict(x) for x in generated.items]==recovered
    entries=records(catalogue()); hashes=json.loads((SOURCE/'BFILE_SHA256.json').read_bytes())
    for entry in entries:
        assert hashlib.sha256(bfile(entry).encode()).hexdigest()==hashes[entry['id']+'_candidate_bfile.txt']
    historical=0
    with (SOURCE/'v10_sequence_catalog.csv').open(newline='',encoding='utf-8') as file:
        for row in csv.DictReader(file):
            if row['key'].startswith('A_N_block_N'):
                N=int(row['key'].split('_N')[-1]);expected=[int(v) for v in row['values'].split(',')]
                assert generator.block_base(N,len(expected))==expected
                historical+=len(expected)
    assert len(entries)==90 and sum(len(x['terms']) for x in entries)==5487
    return dict(status='passed',assertion_tested='All 90 recovered records and all 5487 exact integer terms reproduce from the preserved generator; all indexed b-file bytes reproduce their archived SHA-256 hashes.',
        records=90,terms=5487,bfile_hashes=90,historical_control_terms=historical,
        overlaps=sum(bool(x['overlap']) for x in entries),controls=controls,
        non_claims=['No new OEIS allocation or novelty finding','No infinite identity from a finite overlap','No global Collatz or Carmichael theorem','No physical circuit realization theorem'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=audit();args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8');print(json.dumps(result,indent=2))
