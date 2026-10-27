#!/usr/bin/env python3
"""Check or regenerate the exact-rational translations of the retained tilted intervals.

This is a transparent Python translation, not a verified JSON parser. The emitted
Lean proof checks the stated rational inequalities, not the source intervals.
"""
from pathlib import Path
from fractions import Fraction
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parent

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true',help='Overwrite generated source in a working copy')
    args=ap.parse_args()
    source=ROOT/'provenance/official_worked_example.json'
    d=json.loads(source.read_text())
    rows=[]
    lines=['import KomorebiQCOS.Acceptance','', 'open KomorebiQCOS', 'namespace RecordedTiltedControls', '',
           '-- These are exact arithmetic checks on the recorded tilted-functional interval.',
           '-- They do not prove the transform, analytic remainder, interval library, or log endpoints.',
           'set_option maxRecDepth 10000', 'set_option maxHeartbeats 2000000', '']
    def term(x):return f'({x.numerator} / {x.denominator} : ℚ)'
    for item in d['refinements']:
        n=item['modes'];r=item['result']
        flo,fhi=map(Fraction,r['finite_sum_interval'].strip('[]').split(','))
        _,ehi=map(Fraction,r['total_tilted_error_interval'].strip('[]').split(','))
        lo,hi=flo-ehi,fhi+ehi
        for tol,name in [(Fraction(1,50),'two_percent'),(Fraction(1,1000),'one_per_mille')]:
            ok=0<lo and lo<=hi and 0<=tol and hi<=(1+tol)*lo
            lines += [f'theorem modes_{n}_{name} :',f'    acceptsRational {term(lo)} {term(hi)} {term(tol)} = {str(ok).lower()} := by norm_num [acceptsRational]','']
            rows.append(dict(modes=n,tolerance=str(tol),lower=str(lo),upper=str(hi),accepted=ok,source='official_worked_example.json',source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),scope='tilted-functional interval only'))
    lines+=['end RecordedTiltedControls','']
    outputs={ROOT/'lean/Controls/RecordedTilted.lean':'\n'.join(lines),ROOT/'verification/recorded_tilted_cases.json':json.dumps(rows,indent=2)+'\n'}
    for path,text in outputs.items():
        if args.write:path.write_text(text)
        elif path.read_text()!=text:raise SystemExit('Mismatch: '+str(path))
    print('PASS: exact rational translations and four expected decisions match retained records.')
if __name__=='__main__':main()
