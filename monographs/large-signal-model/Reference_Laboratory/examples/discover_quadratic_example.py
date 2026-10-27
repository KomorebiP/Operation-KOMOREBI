"""Fit observable moment tables, then discover a curved domain without a template."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'checks'))
from continuous_reference import fit_population_moments, load_json
from quadratic_reference import discover_quadratic,verify_quadratic

def main():
    fitted=fit_population_moments(load_json(ROOT/'examples/continuous_population_tables.json'))
    cert=discover_quadratic(fitted)
    out=ROOT/'certificates/discovered_quadratic_certificate.json'
    out.write_text(json.dumps(cert,indent=2)+'\n')
    obj=verify_quadratic(cert)
    print(json.dumps({'passed':True,'center':cert['center'],'metric':cert['metric'],
                      'template_supplied':False,'certificate':str(out.relative_to(ROOT)),
                      'identities':obj.report['identities']},indent=2))
if __name__=='__main__':main()
