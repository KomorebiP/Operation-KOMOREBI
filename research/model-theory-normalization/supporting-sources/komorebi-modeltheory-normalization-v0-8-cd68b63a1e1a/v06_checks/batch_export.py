from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[1]
records=json.loads((ROOT/'results_v06/DISCOVERY_REGRESSION.json').read_text())
for b in range((len(records)+11)//12):
    name=f'EchelonComputed{b:02}'
    code=['module','public import EchelonDiscovery','@[expose] public section',
      'namespace Komorebi.EchelonRegression.'+name,
      'open Komorebi.Discovery Komorebi.Discovery.EchelonBackend',
      'open Komorebi.Representation Komorebi.Representation.Matrix',
      'open Komorebi.ModelTheory Komorebi.ModelTheory.Standard',
      'set_option maxRecDepth 100000','set_option maxHeartbeats 16000000']
    for r in records[b*12:(b+1)*12]:
        i=r['index'];src=json.loads((ROOT/r['source']).read_text())
        lines=(ROOT/f'formalization/EchelonCases/Case{i:03}.lean').read_text().splitlines()
        start=next(j for j,l in enumerate(lines) if l.startswith('abbrev R'))
        end=next(j for j,l in enumerate(lines) if l.startswith('end '))
        body='\n'.join(lines[start:end])
        body=re.sub(r'\b(R|A|O|result|computed)\b',lambda m:f'c{i:03}_'+m[0],body)
        prefix=f'c{i:03}_'
        body+=f'''\ntheorem {prefix}code : FiniteCodeCertificate (linearSystem {prefix}A {prefix}O) {prefix}result :=
  fastPrimeDiscover_code {src['p']} {src['r']} {src['dimension']} {prefix}A {prefix}O {prefix}result {prefix}computed
'''
        code.append(body)
    code+=['end Komorebi.EchelonRegression.'+name,'']
    (ROOT/'formalization'/(name+'.lean')).write_text('\n'.join(code))
print('17 batches emitted')
