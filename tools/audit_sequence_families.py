"""Independent finite constructions and source-binding checks for the family studio."""
import argparse
from collections import Counter
from fractions import Fraction as Q
from functools import lru_cache
import hashlib
import json
from math import comb,factorial
from pathlib import Path
import subprocess
from sequence_formula_catalogue import secancy_polynomials,theta_polynomial_rows,tangent
from sequence_atlas import catalogue,terms as classical_terms
from sequence_generalized import catalogue as generalized_catalogue,membership
from sequence_library import library_entries

ROOT=Path(__file__).resolve().parents[1]

def product(a,b,n):return [sum(a[k]*b[i-k] for k in range(i+1)) for i in range(n)]

@lru_cache(maxsize=None)
def linear(k,r,c,n):
    base=[1]
    for i in range(1,n):base.append(c*sum(base[max(0,i-k):i]))
    answer=[1]+[0]*(n-1)
    for _ in range(r):answer=product(answer,base,n)
    return tuple(answer)

@lru_cache(maxsize=None)
def inverse(N,j,r,n,alternating=False):
    d=[Q(((-1)**i if alternating else 1)*factorial(j),factorial(N*i+j)) for i in range(n)]
    u=[Q(0)]+[-value for value in d[1:]];power=[Q(1)]+[Q(0)]*(n-1);base=power.copy()
    for _ in range(1,n):power=product(power,u,n);base=[a+b for a,b in zip(base,power)]
    answer=[Q(1)]+[Q(0)]*(n-1)
    for _ in range(r):answer=product(answer,base,n)
    return tuple(answer)

def theta(x,n):
    first=inverse(2,0,1,n)
    # sech(xz) is obtained by scaling each even coefficient by x^(2i).
    first=[v*x**(2*i) for i,v in enumerate(first)]
    if x>=0:second=inverse(2,0,x,n)
    else:
        base=[Q(1,factorial(2*i)) for i in range(n)];second=[Q(1)]+[Q(0)]*(n-1)
        for _ in range(-x):second=product(second,base,n)
    return [v*factorial(2*i) for i,v in enumerate(product(first,second,n))]

def denominator(k,r,c):
    d=[1]
    for _ in range(r):
        out=[0]*(len(d)+k)
        for i,a in enumerate(d):
            out[i]+=a
            for j in range(1,k+1):out[i+j]-=c*a
        d=out
    return d

def checks(node):
    cases=[];counts=Counter()
    def add(engine,params,values,offset=0,degrees=None,rationals=None):
        values=list(values);assert all(Q(v).denominator==1 for v in values)
        case=dict(name=engine+':'+json.dumps(params,sort_keys=True),engine=engine,params=params,terms=[str(int(v)) for v in values],offset=offset,degrees=degrees if degrees is not None else list(range(offset,offset+len(values))))
        if rationals is not None:case['rationals']=[str(v) for v in rationals]
        cases.append(case);counts[engine+'_cases']+=1
    for k in range(2,17):
        for r in range(1,9):
            for c in range(1,6):add('linear',dict(k=k,r=r,c=c,count=32),linear(k,r,c,32))
        add('kbonacci',dict(k=k,count=48),[0]*(k-1)+list(linear(k,1,1,49-k)))
    for k in range(2,9):
        for c in (1,2,5):
            for seeds in ([0]*k,[(-1)**i*(i+1) for i in range(k)],[2,1]+[0]*(k-2)):
                n=32;d=denominator(k,1,c);numerator=[s-c*sum(seeds[:i]) for i,s in enumerate(seeds)];base=linear(k,1,c,n);values=[sum(numerator[j]*base[i-j] for j in range(min(i,k-1)+1)) for i in range(n)]
                add('linear',dict(k=k,c=c,r=1,seedMode='custom',seeds=','.join(map(str,seeds)),count=n),values)
    for N in range(2,17):
        for r in range(1,9):
            n=16;values=inverse(N,0,r,n,True);add('reciprocal',dict(N=N,r=r,count=n),[q*factorial(N*i) for i,q in enumerate(values)],degrees=[N*i for i in range(n)])
        for column in (1,4,8):
            n=12;rows=secancy_polynomials(N,n+column);add('secancy',dict(N=N,column=column,count=n),[row[column] for row in rows[column:]],offset=column,degrees=[N*i for i in range(column,column+n)])
        add('tangent',dict(N=N,count=16),tangent(N,16),degrees=[N*(i+1)-1 for i in range(16)])
    for engine,params in [('reciprocal',dict(N=16,r=8,count=32)),('secancy',dict(N=16,column=8,count=32))]:
        N=params['N'];n=params['count']
        if engine=='reciprocal':add(engine,params,[v*factorial(N*i) for i,v in enumerate(inverse(N,0,params['r'],n,True))],degrees=[N*i for i in range(n)])
        else:
            k=params['column'];add(engine,params,[row[k] for row in secancy_polynomials(N,n+k)[k:]],offset=k,degrees=[N*i for i in range(k,k+n)])
    for N in range(2,9):
        for j in range(N):
            for r in range(1,5):
                n=12;raw=[q*factorial(N*i) for i,q in enumerate(inverse(N,j,r,n))]
                for component in ('numerator','denominator'):add('congruential',dict(N=N,j=j,r=r,count=n,component=component),[getattr(q,component) for q in raw],degrees=[N*i for i in range(n)],rationals=raw)
    for N in range(2,7):
        for j in range(N):
            for r in (1,2):
                for x in (-2,0,2):
                    n=12;h=inverse(N,j,r,n);sparse=[h[i//N] if i%N==0 else Q(0) for i in range(n)];exp=[Q(x**i,factorial(i)) for i in range(n)];raw=[v*factorial(i) for i,v in enumerate(product(sparse,exp,n))]
                    for component in ('numerator','denominator'):add('appell',dict(N=N,j=j,r=r,x=x,count=n,component=component),[getattr(q,component) for q in raw],rationals=raw)
    for x in (-8,-3,-1,0,1,2,8):add('theta',dict(x=x,count=16),theta(x,16),degrees=[2*i for i in range(16)])
    rows=theta_polynomial_rows(16)
    for k in range(1,9):
        offset=(k+1)//2;add('theta-column',dict(column=k,count=12),[row[k] for row in rows[offset:offset+12]],offset=offset,degrees=[2*i for i in range(offset,offset+12)])
    seeds=catalogue()
    for kind in ('fibonacci','lucas','pell','factorial','catalan','central-binomial','triangular','square','cube','power-two','power-three','bell','fubini'):
        source=next(e for e in seeds if e['kind']==kind)
        for N in (1,2,3,5):
            for j in sorted({0,N-1}):
                n=8;all_values=classical_terms(dict(source,cap=1000),N*(n-1)+j+1);add('section',dict(N=N,j=j,parent=kind,count=n),[all_values[N*i+j] for i in range(n)],degrees=[N*i+j for i in range(n)])
    cycles=[dict(params=dict(k=k,r=r,c=c),modulus=m,maximum=256) for k in range(2,5) for r in range(1,4) for c in (1,2,3) for m in range(2,12)]
    cycles+=[dict(params=dict(k=2,c=2),modulus=2,maximum=10),dict(params=dict(k=2),modulus=7,maximum=1),dict(params=dict(k=2,seedMode='custom',seeds='0, 0'),modulus=9,maximum=10),dict(params=dict(k=16,r=8,c=5),modulus=256,maximum=256)]
    streams=[]
    for i,(prefix,scale,offset) in enumerate([(0,1,0),(1,1,0),(2,-2,-4),(0,3,10),(4,10**30+1,7),(5,-7,-3)]):
        tail=[scale*v for v in linear(2+i%3,1,1+i%2,20)]
        if i==5:tail=[v if n==0 or n%3 else 0 for n,v in enumerate(tail)]
        values=[0]*prefix+tail
        streams.append(dict(id='STREAM-'+str(i),title='Audit stream '+str(i),offset=offset,terms=list(map(str,values))))
    @lru_cache(maxsize=None)
    def quotient(i,j):
        source=streams[i]['terms'];target=streams[j]['terms']
        a=list(map(Q,source[next(k for k,x in enumerate(source) if int(x)):]))
        b=list(map(Q,target[next(k for k,x in enumerate(target) if int(x)):]))
        n=12;u=[Q(0)]+[-v/a[0] for v in a[1:n]];power=[Q(1)]+[Q(0)]*(n-1);inv=power.copy()
        for _ in range(1,n):power=product(power,u,n);inv=[v+w for v,w in zip(inv,power)]
        return tuple(product(b[:n],[v/a[0] for v in inv],n))
    compositions=[]
    for i,a in enumerate(streams):
        for b in streams:
            for j,c in enumerate(streams):
                v=next(k for k,x in enumerate(a['terms']) if int(x));w=next(k for k,x in enumerate(c['terms']) if int(x))
                compositions.append(dict(a=a,b=b,c=c,expected=list(map(str,quotient(i,j))),inverse=list(map(str,quotient(j,i))),positionShift=w-v,indexShift=c['offset']+w-a['offset']-v))
    entries=library_entries(seeds);scalar_count=sum(not e.get('triangle') and e['id']!='KOM084' and e.get('index_symbol')!='j' for e in entries)
    fib=next(e['id'] for e in entries if e['kind']=='fibonacci' and e['collection']=='atlas');square=next(e['id'] for e in entries if e['kind']=='square' and e['collection']=='atlas')
    identifications=[dict(text='0,1,1,2,3,5,8,13',both=False,expected=fib),dict(text='0,2,2,4,6,10,16,26',both=False,expected=fib),dict(text='0,0,1,0,1,0,2,0,3,0,5,0,8,0,13,0',both=False,expected=fib),dict(text='0,1,4,9,16,25,36,49',both=True,expected=square)]
    dto=[{k:e[k] for k in ('id','title','url','offset','terms','index_symbol') if k in e}|dict(triangle=bool(e.get('triangle'))) for e in entries]
    payload=json.dumps(dict(cases=cases,cycles=cycles,compositions=compositions,entries=dto,scalarCount=scalar_count,identifications=identifications),separators=(',',':'))
    result=subprocess.run([node,str(ROOT/'tools/audit_sequence_families.mjs')],input=payload,text=True,encoding='utf-8',capture_output=True,check=True,timeout=300);observed=json.loads(result.stdout)
    assert observed['cases']==len(cases) and observed['values']==sum(len(c['terms']) for c in cases)
    states=0;certificates=0
    for example,actual in zip(cycles,observed['cycles'],strict=True):
        p=example['params'];k,r,c=p['k'],p.get('r',1),p.get('c',1);d=denominator(k,r,c);order=len(d)-1;n=example['maximum']+order+1
        if p.get('seedMode')=='custom':a=[int(v) for v in p['seeds'].split(',')]
        else:
            a=[1]
            for i in range(1,order):a.append(-sum(d[j]*a[i-j] for j in range(1,i+1)))
        for i in range(order,n):a.append(-sum(d[j]*a[i-j] for j in range(1,order+1)))
        m=example['modulus'];a=[v%m for v in a];assert actual['initialState']==a[:order];assert actual['model']['coefficients']==list(map(str,[-v for v in d[1:]]));assert actual['values']==a[:len(actual['values'])]
        seen={};first=repeat=None
        for i in range(example['maximum']+1):
            state=tuple(a[i:i+order])
            if state in seen:first,repeat=seen[state],i;break
            if i==example['maximum']:break
            seen[state]=i
        assert actual['certified']==(repeat is not None)
        if repeat is not None:assert (actual['preperiod'],actual['period'],actual['repeatedState'])==(first,repeat-first,a[repeat:repeat+order]);certificates+=1
        states+=actual['scanned']
    data=generalized_catalogue(entries);assert len(data['families'])==36 and len(data['relations'])==1231
    assert data['archive_coverage']==dict(records=90,assigned=90)
    assert data['record_coverage']==dict(records=2292,assigned=2292)
    for source in data['sources']:
        text=(ROOT/source['path']).read_text(encoding='utf-8');assert hashlib.sha256(text.encode()).hexdigest()==source['normalized_sha256'],source['id']
    ids={e['id'] for e in entries}
    for family in data['families']:assert set(family['record_ids'])<=ids
    assert membership(next(e for e in entries if e['kind']=='euler'))==['GF-CONGRUENTIAL']
    return dict(status='passed',family_cases=observed['cases'],exact_values=observed['values'],finite_hypergeometric_values=observed['hypergeometric_values'],worked_alternatives=observed['worked_alternatives'],cases_by_engine=dict(counts),modular_cases=len(cycles),states_checked=states,cycle_certificates=certificates,composition_cases=observed['composition_cases'],composition_coefficients=observed['composition_coefficients'],identification_cases=observed['identifications'],generalized_families=len(data['families']),family_modes=dict(Counter(f['mode'] for f in data['families'])),archive_coverage=data['archive_coverage'],record_coverage=data['record_coverage'],source_documents=len(data['sources']),source_headings=sum(len(s['headings']) for s in data['sources']),relations=len(data['relations']),case_payload_sha256=hashlib.sha256(payload.encode()).hexdigest(),scope='Exact independent finite coefficient constructions, differential browser execution, source bindings and complete-state certificate replay within the enumerated contract.',non_claims=['No whole-manuscript independent proof review','Source-indexed analytic families are not numerically evaluated here','Finite identification matches do not prove infinite identity','No historical novelty claim'])

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--node',required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args();report=checks(args.node);args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n');print(json.dumps(report))
