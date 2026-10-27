from __future__ import annotations
import json,sys
from pathlib import Path
from prepare_probe import prepare,disc,v2res,planted_tests
R=Path(__file__).resolve().parent
checks=planted_tests()
for fname in ['fresh_256.json','fresh_256_tail.json','fresh_272.json']:
    doc=json.loads((R/fname).read_text())
    for rec in doc['records']:
        P=rec['local_precision'];W,U=prepare(list(map(int,rec['local_coefficients'])),P)
        assert W==list(map(int,rec['prepared_polynomial']))
        D=disc(W)%(1<<P)
        assert D==int(rec['prepared_discriminant_residue'])
        assert v2res(D,P)==rec['prepared_discriminant_valuation_or_bound']
        checks+=1
s=json.loads((R/'prepared_frontier.json').read_text())
f=json.loads((R/'Komorebi_Euler_Cubic_Unit_v26/evidence/v26_frontier_probe.json').read_text())
W,U=prepare(list(map(int,f['coefficients'])),f['precision'])
assert W==list(map(int,s['prepared_coefficients']));checks+=1
c=json.loads((R/'prepared_cubic_110.json').read_text())
CW,CU=prepare(list(map(int,c['local_coefficients'])),c['local_precision'])
assert CW==list(map(int,c['prepared_coefficients']))
assert CU==list(map(int,c['unit_coefficients']))
assert disc(CW)%(1<<c['local_precision'])==int(c['prepared_discriminant_residue']);checks+=1
assert [int(x)%(1<<62) for x in c['prepared_coefficients']]==W
assert int(c['prepared_discriminant_residue'])%(1<<62)==int(s['discriminant_residue']);checks+=1
lo=json.loads((R/'fresh_256.json').read_text())['records'][0]
hi=json.loads((R/'fresh_272.json').read_text())['records'][0]
assert int(hi['critical_value_residue'])%(1<<78)==int(lo['critical_value_residue'])
assert [int(x)%(1<<78) for x in hi['prepared_polynomial']]==list(map(int,lo['prepared_polynomial']));checks+=1
m=json.loads((R/'fresh_mahler.json').read_text());M=1<<m['precision']
a=json.loads((R/'fresh_256.json').read_text())['records']+json.loads((R/'fresh_256_tail.json').read_text())['records']
a=sorted(a,key=lambda x:x['T']);row=[int(x['critical_value_residue']) for x in a];cs=[]
while row:cs.append(row[0]);row=[(y-x)%M for x,y in zip(row,row[1:])]
assert cs==list(map(int,m['coefficients']))
assert [v2res(x,m['precision']) for x in cs]==m['valuations_or_lower_bounds'];checks+=1
print(json.dumps({'status':'passed','registered_checks':checks,'scope':'exact modular factorization and retained-record consistency; not a universal simplicity proof'},indent=2))
