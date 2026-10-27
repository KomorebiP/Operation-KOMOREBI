from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from integer_echelon import discover_echelon

def vec(a):
    if not a:return '(fun i => Fin.elim0 i)'
    return '!['+', '.join(vec(x) if isinstance(x,list) else str(x) for x in a)+']'
def tests(a):
    return '['+', '.join('(['+','.join(map(str,x['word']))+'], '+str(x['observation'])+')' for x in a)+']'

def main():
    sources=sorted((ROOT/'certificates').glob('*.source.json'))+[ROOT/'certified_data/descending_torsion.source.json']
    records=[]
    for idx,p in enumerate(sources):
        source=json.loads(p.read_text()); answer,stats=discover_echelon(source)
        prior=json.loads((ROOT/'certified_data'/p.name.replace('.source.json','.trace.json')).read_text())
        assert answer==prior['result'],p.name
        records.append({'index':idx,'source':str(p.relative_to(ROOT)),'stats':stats,'result':answer})
    (ROOT/'results_v06/DISCOVERY_REGRESSION.json').write_text(json.dumps(records,indent=2)+'\n')
    # Keep individual files to bound each kernel-reduction obligation.
    out=ROOT/'formalization/EchelonCases';out.mkdir(exist_ok=True)
    for rec in records:
        src=json.loads((ROOT/rec['source']).read_text()); i=rec['index']
        n=f'Case{i:03}'; ns=f'Komorebi.EchelonRegression.{n}'
        code=f'''module
public import EchelonDiscovery
@[expose] public section
namespace {ns}
open Komorebi.Discovery Komorebi.Discovery.EchelonBackend
open Komorebi.Representation Komorebi.Representation.Matrix
set_option maxRecDepth 100000
set_option maxHeartbeats 8000000
abbrev R := ZMod ({src['p']}^{src['r']})
def A : Fin {len(src['actions'])} → Mat R {src['dimension']} {src['dimension']} := {vec(src['actions'])}
def O : Mat R {len(src['observations'])} {src['dimension']} := {vec(src['observations'])}
def result : List (Test {len(src['actions'])} {len(src['observations'])}) := {tests(rec['result'])}
theorem computed : fastPrimeDiscover {src['p']} {src['r']} {src['dimension']}
    (fun a => rowRight (A a)) O = some result := by decide +kernel
end {ns}
'''
        (out/(n+'.lean')).write_text(code)
    print(json.dumps({'cases':len(records),'accepted':sum(x['stats']['accepted'] for x in records),
       'decisions':sum(x['stats']['decisions'] for x in records),
       'max_integer_bits':max(x['stats']['max_integer_bits'] for x in records),
       'large':records[-2], 'stress':records[-1]},indent=2))
if __name__=='__main__':main()
