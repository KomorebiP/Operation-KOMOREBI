from __future__ import annotations
import sys,json,hashlib,time
from pathlib import Path
ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'Komorebi_Euler_Cubic_Unit_v26/checks'))
import check_critical_value as b
from prepare_probe import prepare,disc,v2res
P=272;b.B=b.bernoullis(P);started=time.monotonic()
r0=17659*(1<<640)-161
G,mu,j=b.residual(r0,P)
assert (mu,j)==(-154,161)
loc=b.local(G,90,7,P);content=min(b.v2(z,P) for z in loc);assert content==162
f=[z>>content for z in loc];bits=P-content
W,U=prepare(f,bits);D=disc(W)%(1<<bits)
previous=json.loads((ROOT/'prepared_frontier.json').read_text())
assert [w%(1<<62) for w in W]==list(map(int,previous['prepared_coefficients']))
assert D%(1<<62)==int(previous['discriminant_residue'])
res={'global_precision':P,'local_precision':bits,'prepared_degree':3,
     'local_coefficients':[str(x) for x in f], 'unit_coefficients':[str(x) for x in U],
     'prepared_coefficients':[str(x) for x in W], 'prepared_discriminant_residue':str(D),
     'valuation':v2res(D,bits),'agrees_with_62_bit_saved_core':True,
     'full_factorization_modulus_verified':True,'seconds':time.monotonic()-started,
     'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(ROOT/'prepared_cubic_110.json').write_text(json.dumps(res,indent=2)+'\n')
print(json.dumps({k:v for k,v in res.items() if not k.endswith('coefficients')},indent=2))
