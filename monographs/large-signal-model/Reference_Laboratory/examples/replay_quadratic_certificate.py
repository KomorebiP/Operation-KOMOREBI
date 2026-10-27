"""Independently replay the exported witness. No fitting, template, or generator."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'checks'))
from continuous_reference import load_json
from quadratic_reference import verify_quadratic
if __name__=='__main__':
    obj=verify_quadratic(load_json(ROOT/'certificates/discovered_quadratic_certificate.json'))
    print(json.dumps(obj.report,indent=2))
