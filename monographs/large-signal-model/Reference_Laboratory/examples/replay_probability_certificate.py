"""Independently replay the exported rational certificate. No fitting or search."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'checks'))
from cone_reference import verify_certificate


def main() -> None:
    report=json.loads((ROOT/'verification/learned_cone_certificate.json').read_text())
    def family(key):
        return {tuple(map(int,k.split(','))):v for k,v in report[key].items()}
    fresh=verify_certificate(family('operators'),report['mass'],report['initial'],
                             report['generators'],family('lifts'),
                             [[x] for x in report['initial_weights']])
    print(fresh['status'])
    print('Exact equality, nonnegativity, initial-state and mass checks replayed.')
    print('No source fit, interval search, hidden generator or statistical assumption was evaluated.')


if __name__=='__main__':main()
