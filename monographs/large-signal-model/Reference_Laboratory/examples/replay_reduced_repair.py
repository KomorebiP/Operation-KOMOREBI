from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'checks'))
from robust_reference import replay_certificate
if __name__=='__main__':
    for name in ['reduced_repair_certificate','reduced_repair_comparison']:
        print(name,json.dumps(replay_certificate(json.loads((ROOT/f'certificates/{name}.json').read_text())),indent=2))
