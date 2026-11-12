"""Komorebi P. Portable replay of all inherited and new checkpoint certificates.

Run with python3 -S: numerical search packages are deliberately unnecessary.
"""
import argparse
import hashlib
import json
from pathlib import Path

from composition_certificate import verify_circuit
from replay_new_certificates import replay as replay_inherited

ROOT=Path(__file__).resolve().parents[1]


def replay():
    inherited=replay_inherited()
    entries=json.loads((ROOT/'certificates/COMPOSITION_INDEX.json').read_text())['entries']
    rows=[]
    for entry in entries:
        path=ROOT/entry['file'];cert=json.loads(path.read_text())
        check=verify_circuit(cert,expected_target=entry['target'],expected_budget=entry['budget'])
        if check['status']!='PASS':raise AssertionError((entry['id'],check))
        if entry['required_minimum'] and not check['global_minimum_proved_by_degree']:
            raise AssertionError('Reactive minimum not proved: '+entry['id'])
        rows.append({'id':entry['id'],'file':entry['file'],'source':entry['source'],
                     'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                     'format':cert['format'],'status':check['status'],
                     'actual_storage':check['actual_storage'],'resistors':check['resistors'],
                     'reduced_target_degree':check['reduced_target_degree'],
                     'minimum_proved':check['global_minimum_proved_by_degree']})
    return {'status':'PASS','arithmetic':'Python standard library only',
            'inherited_entries':inherited['replayed'],'new_checkpoint_entries':len(rows),
            'total_entries':inherited['replayed']+len(rows),
            'inherited':inherited,'new_checkpoint':rows}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path);args=p.parse_args()
    data=replay();content=json.dumps(data,indent=2)+'\n'
    if args.output:args.output.write_text(content)
    print(content)
