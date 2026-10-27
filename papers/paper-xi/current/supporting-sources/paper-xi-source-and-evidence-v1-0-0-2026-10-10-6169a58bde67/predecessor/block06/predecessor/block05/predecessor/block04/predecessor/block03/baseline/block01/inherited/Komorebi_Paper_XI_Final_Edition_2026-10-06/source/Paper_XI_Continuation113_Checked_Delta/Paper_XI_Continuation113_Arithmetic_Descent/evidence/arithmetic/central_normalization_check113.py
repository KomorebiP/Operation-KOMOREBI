#!/usr/bin/env python3
"""Direct group-character checks and exact central normalization of wild correction."""
import importlib.util,contextlib,io,pathlib,json,sys
p=pathlib.Path(__file__).with_name('central_twist113.py')
spec=importlib.util.spec_from_file_location('ct',p);m=importlib.util.module_from_spec(spec)
with contextlib.redirect_stdout(io.StringIO()):spec.loader.exec_module(m)
c=m.c
comm0=m.mm(m.mm(m.mm(m.gi,m.u0),m.g),m.mi(m.u0))
comm1=m.mm(m.mm(m.mm(m.gi,m.u1),m.g),m.mi(m.u1))
e0=m.htheta(comm0);e1=m.htheta(comm1);eh=m.htheta(m.h)
assert e0==0 and e1==0
assert eh==m.Q(1,3)  # This script imports correction coefficient zero.
gamma=c.power(c.x,-8)
v=c.mul(c.piF,c.power(c.x,-3))
phase=c.fractional_part_3(c.trace(c.mul(gamma,m.padic_log_mod7(v)))/3)
assert c.valuation(c.sub(v,c.one))==4 and phase==m.Q(2,3)
assert c.fractional_part_3(phase+m.Q(1,3))==0
result={'eta_generator_commutator_phases':[str(e0),str(e1)],'uniformizer_commutator_phase':str(eh),'uniformizer_ratio_valuation':4,'nu_piF_if_nu_piL_is_one':str(phase),'normalized_nu_piL':'zeta9','normalized_nu_piF_exponent':'0','central_unit_proof':'UF1=mu3*UF2; log kills mu3, and piL^-8 log(UF2) lies pL^-2 inside ker psiL=pL^-3.','all_assertions_pass':True,'scope':'Direct group phases for the original theta and central-character normalization for the distinct corrected theta. Not AI occurrence.'}
print(json.dumps(result,indent=2))
