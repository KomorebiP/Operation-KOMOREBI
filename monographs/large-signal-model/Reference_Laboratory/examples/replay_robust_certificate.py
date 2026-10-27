"""Independently replay the supplied exact robust certificate."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'checks'))
from robust_reference import replay_certificate
path=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'certificates/robust_curved_certificate.json'
print(json.dumps(replay_certificate(json.loads(path.read_text())),indent=2))
