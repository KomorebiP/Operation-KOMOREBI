"""Independent all-extension obstruction inputs, original theta only.

Uses the inspected rational cyclotomic arithmetic but no Weyl intertwiner
search and no chosen central-type matrix S. The decisive scalar is evaluated
directly on h=g^-1 Pi g Pi^-1 in the actual H1.
"""
from pathlib import Path
from fractions import Fraction
import contextlib,io,importlib.util,json,hashlib,subprocess,sys

here=Path(__file__).resolve().parent
project=here.parents[1]
arith=project/'evidence/arithmetic'
spec=importlib.util.spec_from_file_location('self_twist_raw',arith/'self_twist113.py')
st=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):spec.loader.exec_module(st)
c=st.c

def theta(h):
    # Independent decomposition modulo U_a^6 into an L-unit and a deep unit.
    remainder=st.ms(h,st.I)
    ell=c.one
    ell_matrix=st.I
    digits=[]
    for depth in range(1,6):
        good=[]
        for a in range(3):
            res=st.ms(remainder,st.sm(st.mp(st.Pi,depth),c.scale(c.one,a)))
            if st.va(res)>=depth+1:good.append((a,res))
        assert len(good)==1,(depth,len(good))
        a,remainder=good[0]
        digits.append(a)
        ell=c.add(ell,c.scale(c.power(c.x,depth),a))
        ell_matrix=st.ma(ell_matrix,st.sm(st.mp(st.Pi,depth),c.scale(c.one,a)))
    y=st.mm(st.mi(ell_matrix),h)
    deep=st.va(st.ms(y,st.I))
    assert deep>=6
    el=c.trace(c.mul(c.beta,st.padic_log_mod7(ell)))/3
    ey=c.trace(st.mt(st.mm(st.B,st.ms(y,st.I))))/9
    return {'L_digits':digits,'deep_remainder_order':deep,
            'L_exponent':str(c.fractional_part_3(el)),
            'deep_exponent':str(c.fractional_part_3(ey)),
            'theta_exponent':str(c.fractional_part_3(el+ey))}

h=st.mm(st.mm(st.mm(st.gi,st.Pi),st.g),st.mi(st.Pi))
h_result=theta(h)
assert h_result['theta_exponent']=='1/3'
generator_rows=[]
for pos in (0,1):
    D=tuple(tuple(c.one if i==j==pos else c.zero for j in range(3)) for i in range(3))
    u=st.ma(st.I,st.mm(D,st.mp(st.Pi,5)))
    comm=st.mm(st.mm(st.mm(st.gi,u),st.g),st.mi(u))
    level=st.va(st.ms(comm,st.I))
    assert level>=6
    phase=c.fractional_part_3(c.trace(st.mt(st.mm(st.B,st.ms(comm,st.I))))/9)
    omega=c.fractional_part_3(c.trace(st.mt(st.sm(st.ms(u,st.I),c.scale(c.one,Fraction(1,3)))))/9)
    assert phase==omega==0
    generator_rows.append({'label':pos,'commutator_order':level,
                           'theta_commutator_exponent':str(phase),'omega_exponent':str(omega)})
assert all(c.sigma(v)==v for row in st.g for v in row)
assert all(c.sigma(v)==v for row in h for v in row)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
pins=[arith/s for s in ['cyclotomic_check113.py','self_twist113.py','central_twist113.py','central_twist_result113.json']]
result={'status':'PASS','input_sha256':{str(p.relative_to(project)):sha(p) for p in pins},
        'g_minus_one_order':st.va(st.ms(st.g,st.I)),
        'uniformizer_commutator':h_result,'eta_generator_conjugation':generator_rows,
        'matrix_entries_fixed_by_sigma':True,
        'obstruction':'zeta3, independent of every nonzero scalar rescaling of the intertwiner or of the extension action at Pi',
        'scope':'Original theta only. Group-generation, Schur, and primary compact-induction theorems provide the all-extension consequence in SELF_TWIST_AUDIT113.md.'}
out=subprocess.run([sys.executable,str(arith/'central_twist113.py'),'0'],capture_output=True,text=True,timeout=90)
(here/'central_twist_original_replay.log').write_text(out.stdout+out.stderr)
assert out.returncode==0,out.stderr
replay=json.loads(out.stdout)
stored=json.loads((arith/'central_twist_result113.json').read_text())
assert replay==stored
result['central_replay_identical']=True
(here/'SELF_TWIST_RESULT113.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
