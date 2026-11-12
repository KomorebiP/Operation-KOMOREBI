"""Author: Komorebi P. Portable standard-library-only certificate replay."""
import argparse
import hashlib
import json
from pathlib import Path
from algebraic_witness import verify_algebraic_circuit
from interval_certificate import verify_interval_circuit
from interval_family import verify_coefficient_family

ROOT=Path(__file__).resolve().parents[1]


def replay():
    entries=json.loads((ROOT/'certificates/INDEX.json').read_text())['entries']
    rows=[]
    for entry in entries:
        path=ROOT/entry['file'];cert=json.loads(path.read_text())
        if entry['kind']=='family':
            check=verify_coefficient_family(cert)
        elif entry['kind']=='interval':
            check=verify_interval_circuit(cert,entry['target'],entry['budget'])
        elif entry['kind']=='rational':
            check=verify_algebraic_circuit(cert,entry['target'],entry['budget'])
        else:raise ValueError('Unknown index kind')
        if check['status']!='PASS':raise AssertionError(check)
        rows.append({'file':entry['file'],'kind':entry['kind'],'status':check['status'],
                     'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'actual_storage':check.get('actual_storage',check.get('storage_count')),
                     'minimum_proved':check.get('global_minimum_proved_by_degree',check.get('minimum_reactive_count')==3)})
    return {'status':'PASS','replayed':len(rows),'arithmetic':'standard-library only','cases':rows}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);args=p.parse_args()
    data=replay();content=json.dumps(data,indent=2)+'\n'
    if args.output:args.output.write_text(content)
    print(content)
