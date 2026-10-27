from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'checks'))
from data_certificate_reference import replay_certificate, MEASURE
if __name__=='__main__':
    d=json.loads((ROOT/'examples/dependent_observations.json').read_text())
    if d['reference_measure'] != MEASURE: raise ValueError('Wrong observation measure.')
    c=json.loads((ROOT/'certificates/dependent_data_certificate.json').read_text())
    print(json.dumps(replay_certificate(c,d['node_indices']),indent=2))
