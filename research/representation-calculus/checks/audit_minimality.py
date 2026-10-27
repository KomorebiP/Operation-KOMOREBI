"""Finite implementation and provenance audit, separate from universal Lean claims."""
from pathlib import Path
from collections import Counter
from itertools import product
from copy import deepcopy
import ast,hashlib,json,math,random,re,sys,time,zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools'))
from checks.check_certificate import check,InvalidCertificate
from discover import discover,canonical
from export_symbolic_lean import emit
from export_minimum_lean import emit_minimum
C=Counter()
def need(value,label):
    C[label]+=1
    if not value:raise AssertionError(label)
def modern(text):
    lines=text.splitlines(keepends=True);last=max(i for i,s in enumerate(lines) if s.startswith('import '));out=['module\n']
    for i,s in enumerate(lines):
        out.append('public '+s if s.startswith('import ') else s)
        if i==last:out.append('\n@[expose] public section\n')
    return ''.join(out)
def main():
    start=time.monotonic();records=json.loads((ROOT/'source_records/SYMBOLIC_EXPORTS_v03.json').read_text())
    gaps=[];empty=0;torsion=0;exports=[]
    for rec in records:
        source=json.loads((ROOT/rec['source']).read_text());cert=json.loads((ROOT/rec['certificate']).read_text())
        p,r,t=source['p'],source['r'],cert['dimension'];ss=cert['smith_valuations'];m=p**r
        need(check(source,cert)['status']=='PASS','independent_matrix_certificate')
        need(canonical(discover(source)['certificate'])==canonical(cert),'exact_frozen_rediscovery')
        text=(ROOT/rec['generated']).read_text()
        need(text==modern(emit(source,cert,rec['namespace'].split('.')[-1])),'unchanged_matrix_bodies_module_headers_only')
        need(len(ss)==t and all(0<=s<r for s in ss),'all_factors_nonzero')
        length=sum(r-s for s in ss);lower=(length+r-1)//r
        if lower<t:gaps.append({'tag':rec['tag'],'linear_minimum':t,'cardinality_bound':lower,'p_digits':length})
        empty+=t==0;torsion+=any(s>0 for s in ss)
        generated=emit_minimum(source,cert,rec['namespace'].split('.')[-1]+'WithMinimum')
        need('fin_certificate_minimum_iff' in generated,'minimum_export_contains_universal_application')
        need(f'(p:={p}) (r:={r})' in generated,'minimum_export_prime_precision_binding')
    # Exhaustive check: every one-row linear code fails for the two order-two factors.
    states=list(product(range(16),repeat=2));obs=lambda x:(8*x[0]%16,8*x[1]%16)
    witnesses=[]
    for a,b in product(range(16),repeat=2):
        delta=next(x for x in states if (a*x[0]+b*x[1])%16==0 and obs(x)!=(0,0))
        need((a*delta[0]+b*delta[1])%16==0 and obs(delta)!=(0,0),'every_one_row_linear_encoder_excluded')
        witnesses.append({'row':[a,b],'delta':list(delta)})
    images=set()
    for x in states:
        packed=x[0]%2+2*(x[1]%2);images.add(packed)
        need((8*(packed%2),8*((packed//2)%2))==obs(x),'nonlinear_one_residue_exact_observations')
    need(len(images)==4,'nonlinear_quotient_has_four_states')
    need((2%2)!=2*(1%2),'nonlinear_pack_not_additive')
    # Model minima on bounded diagonal examples; cardinality alone can be arbitrarily weak.
    for p in (2,3,5):
        for r in range(1,6):
            for t in range(0,6):
                ss=[max(0,r-1-i%2) for i in range(t)]
                length=sum(r-s for s in ss)
                need((length+r-1)//r<=t,'cardinality_lower_never_exceeds_generator_count')
    source=json.loads((ROOT/'certificates/scrambled_128bit.source.json').read_text());cert=json.loads((ROOT/'certificates/scrambled_128bit.certificate.json').read_text())
    cases=[]
    for key in ['encoding','weight_zero','wrong_prime','wrong_precision','single_seed','wrong_actions_rebound']:
        s=deepcopy(source);c=deepcopy(cert)
        if key=='encoding':c['basis'][0][0]^=1
        elif key=='weight_zero':c['smith_valuations'][0]=s['r']
        elif key=='wrong_prime':s['p']=4;c['source_sha256']=hashlib.sha256(canonical(s)).hexdigest()
        elif key=='wrong_precision':s['r']+=1;c['source_sha256']=hashlib.sha256(canonical(s)).hexdigest()
        elif key=='single_seed':s['initial_interface']='single_seed';c['source_sha256']=hashlib.sha256(canonical(s)).hexdigest()
        else:s['actions'][0][0][0]^=1;c['source_sha256']=hashlib.sha256(canonical(s)).hexdigest()
        try:emit_minimum(s,c,'Rejected')
        except (InvalidCertificate,ValueError):C['corrupted_minimum_exports_rejected']+=1
        else:raise AssertionError(key+' erroneously accepted')
    # Exactly frozen predecessor and three directly reused module bodies.
    par=zipfile.ZipFile(ROOT/'history/Komorebi_Representation_Calculus_v0.3.zip')
    for n in ['discover.py','chainring.py','checks/check_certificate.py','tools/export_symbolic_lean.py']:
        need((ROOT/n).read_bytes()==par.read('Komorebi_Representation_Calculus_v0.3/'+n),'unchanged_discovery_and_checker_source')
    result={'status':'PASS','counts':dict(C),'instances':len(records),'zero_coordinate_instances':empty,'torsion_instances':torsion,
            'cardinality_bound_strictly_weaker_instances':len(gaps),'cardinality_gaps':gaps,'seconds':time.monotonic()-start,
            'ranges':{'one_row_encoders':256,'source_states_for_boundary':256,'diagonal_formula_cases':90},
            'boundaries':['Finite tests do not prove the universal minimum; separately compiled Lean proves it.',
                          'All data are inherited synthetic fixtures, not a held-out discovery benchmark.',
                          'Exporter, discoverer, and Python checker are not verified executable programs.']}
    (ROOT/'results/PYTHON_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    (ROOT/'results/ONE_ROW_COUNTEREXAMPLES.json').write_text(json.dumps(witnesses,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cardinality_gaps'},indent=2))
if __name__=='__main__':main()
