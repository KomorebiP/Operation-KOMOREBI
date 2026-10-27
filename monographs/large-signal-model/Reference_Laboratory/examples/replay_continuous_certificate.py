"""Check a supplied witness without the tables, template, learner or generator."""
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'checks'))
from continuous_reference import load_json,verify_certificate
if __name__=='__main__':
    target=Path(sys.argv[1]) if len(sys.argv)>1 else ROOT/'certificates/continuous_psd_certificate.json'
    model=verify_certificate(load_json(target))
    print(json.dumps(model.verification,indent=2))
