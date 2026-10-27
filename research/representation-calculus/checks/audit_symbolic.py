"""Independent emission/transcription checks and exact finite regressions.

This script does not certify Lean outcomes; tools/verify_lean.py records those.
No enumeration of any large source or observable state space is performed.
"""
from pathlib import Path
from collections import Counter
from copy import deepcopy
from hashlib import sha256
import ast,json,random,re,sys,time
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'tools'))
from discover import discover, matvec, encode, compressed_output
from checks.check_certificate import check, InvalidCertificate
from export_symbolic_lean import emit, canonical
C=Counter()
def need(ok,label):
    C[label]+=1
    if not ok:raise AssertionError(label)
def payload(line):
    """Read only the first balanced literal list, independent of the exporter."""
    a=line.index('[');depth=0
    for b in range(a,len(line)):
        if line[b]=='[':depth+=1
        elif line[b]==']':
            depth-=1
            if depth==0:return ast.literal_eval(line[a:b+1])
    raise ValueError('unclosed payload')
def row_eval(spec,word,j):
    m=spec['p']**spec['r'];d=spec['dimension'];out=[]
    for col in range(d):
        state=[int(i==col) for i in range(d)]
        for digit in word:
            state=[sum(a*b for a,b in zip(row,state))%m for row in spec['actions'][digit]]
        out.append(sum(a*b for a,b in zip(spec['observations'][j],state))%m)
    return out

def main():
    tick=time.monotonic();rng=random.Random(2026092003)
    exports=json.loads((ROOT/'evidence/SYMBOLIC_EXPORTS.json').read_text());trace_nodes=0;witnesses=0;zero=0
    for item in exports:
        spec=json.loads((ROOT/item['source']).read_text());cert=json.loads((ROOT/item['certificate']).read_text())
        m=spec['p']**spec['r'];d=spec['dimension'];text=(ROOT/item['generated']).read_text();lines=text.splitlines()
        need(check(spec,cert)['status']=='PASS','independent_matrix_certificate')
        fresh=discover(spec)['certificate']
        need(canonical(fresh)==canonical(cert),'rediscovery_matches_frozen_certificate')
        need(emit(spec,cert,item['namespace'].split('.')[-1])==text,'deterministic_export_bytes')
        need(payload(next(z for z in lines if z.startswith('  fun a i j')))==spec['actions'],'source_actions_transcribed')
        need(payload(next(z for z in lines if z.startswith('def observations')))==spec['observations'],'source_observations_transcribed')
        need(int(re.search(r'abbrev R := Fin (\d+)',text).group(1))==m,'modulus_transcribed')
        declared=[int(n) for n in re.search(r'def data : CertificateData R (\d+) (\d+) (\d+) (\d+) (\d+)',text).groups()]
        need(declared==[d,cert['dimension'],len(spec['actions']),len(spec['observations']),len(cert['raw_tests'])],'dimensions_transcribed')
        for marker,field in [('  encoding :=','basis'),('  transitions :=','transitions'),('  decoder :=','observation_decoder'),('  combinations :=','basis_combinations'),('  change :=','V'),('  inverse :=','V_inverse')]:
            need(payload(next(z for z in lines if z.startswith(marker)))==cert[field],'certificate_matrix_transcribed')
        raw=payload(next(z for z in lines if z.startswith('def witnessedRows')))
        for i,test in enumerate(cert['raw_tests']):
            need(raw[i]==row_eval(spec,test['word'],test['observation']),'witness_rows_independent_basis_evaluation')
            delta=cert['strict_growth_witnesses'][i]['delta'];witnesses+=1
            need(all(sum(a*b for a,b in zip(row,delta))%m==0 for row in raw[:i]) and sum(a*b for a,b in zip(raw[i],delta))%m!=0,'growth_witness_equations')
        nodes=len(re.findall(r'^def row\d+ :',text,re.M));trace_nodes+=nodes
        need(nodes<=sum(len(t['word'])+1 for t in cert['raw_tests']),'trace_dag_within_unshared_bound')
        if cert['dimension']==0:zero+=1
        for _ in range(8):
            x=[rng.randrange(m) for _ in range(d)];w=[rng.randrange(len(spec['actions'])) for _ in range(rng.randrange(13))];z=x[:]
            for a in w:z=matvec(spec['actions'][a],z,m)
            for j,row in enumerate(spec['observations']):
                need(compressed_output(cert,encode(cert,x,m),w,j,m)==sum(a*b for a,b in zip(row,z))%m,'sample_all_state_transport')
    # Actual large-image code and inverse: test arbitrary codes, not enumeration.
    s=json.loads((ROOT/'certificates/scrambled_128bit.source.json').read_text());b=json.loads((ROOT/'certificates/scrambled_128bit.certificate.json').read_text())
    for _ in range(4096):
        q=rng.randrange(2**30);lo=q%65536;hi=q//65536;y=[lo,4*hi]
        need(y[0]+65536*(y[1]//4)==q,'large_image_code_roundtrip')
        z=[lo,hi]+[0]*6;x=matvec(b['V'],z,65536)
        need(encode(b,x,65536)==y,'large_code_has_source_representative')
    for _ in range(512):
        x=[rng.randrange(65536) for _ in range(8)];y=encode(b,x,65536)
        need(y[1]%4==0,'large_arbitrary_image_divisibility')
        q=y[0]+65536*(y[1]//4)
        need([q%65536,4*(q//65536)]==y,'large_image_decode_roundtrip')
    mutations=[]
    c=deepcopy(b);c['basis'][0][0]^=1;mutations.append(('encoding',s,c))
    c=deepcopy(b);c['smith_valuations'][1]=1;mutations.append(('torsion',s,c))
    c=deepcopy(b);c['strict_growth_witnesses'][1]['delta']=[0]*8;mutations.append(('witness',s,c))
    s2=deepcopy(s);s2['actions'][0][0][0]^=1;c=deepcopy(b);c['source_sha256']=sha256(canonical(s2)).hexdigest();mutations.append(('rebound_source',s2,c))
    for name,src,c in mutations:
        try:emit(src,c,'Rejected')
        except InvalidCertificate:C['corrupt_export_inputs_rejected']+=1
        else:raise AssertionError(name+' accepted by exporter')
    try:emit(s,b,'Bad.Name; axiom X : False')
    except ValueError:C['namespace_injection_rejected']+=1
    else:raise AssertionError('namespace accepted')
    result={'status':'PASS','seed':2026092003,'instances':len(exports),'trace_nodes':trace_nodes,'growth_witnesses':witnesses,'zero_coordinate_instances':zero,
       'counts':dict(C),'runtime_seconds':time.monotonic()-tick,
       'ranges':{'source_cases':'all 202 frozen v0.2 certificates; no changed source semantics','sample_words_per_profile':8,'maximum_sample_word_length':12,'large_image_codes_sampled':4096,'large_arbitrary_states_sampled':512},
       'boundaries':['Finite sample checks do not prove universal claims; the separately recorded Lean proofs do.',
       'Exporter and source JSON parser are not verified programs. Independent literal-data extraction checks transcription.',
       'All fixtures are synthetic, inherited, and not a held-out AI discovery benchmark.']}
    (ROOT/'results/SYMBOLIC_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
