"""Standard-library exact replay for the interior order classification."""
import argparse,itertools,json,sys,time
from fractions import Fraction as F
from math import comb,factorial,isqrt,prod
from pathlib import Path
import sequence_hankel_orders as orders
import verify_sequence_exceptional_hankel as sparse
from sequence_differential_hankel import structured_differential_hankel
from test_sequence_differential_hankel import direct_determinant
from verify_sequence_uniform_mixed import base_polynomial,nu,power

def add(*items):
    return orders.trim([sum((p[i] if i<len(p) else 0) for p in items)
        for i in range(max((len(p) for p in items),default=0))])
def scale(p,c):return orders.trim([c*x for x in p])
def mul(a,b):
    if not a or not b:return []
    out=[F(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]+=x*y
    return orders.trim(out)
def ppow(a,n):
    out=[F(1)]
    for _ in range(n):out=mul(out,a)
    return out
def evaluate(p,x):
    out=F(0)
    for c in reversed(p):out=out*x+c
    return out
def determinant(matrix):
    size=len(matrix);out=[]
    for permutation in itertools.permutations(range(size)):
        sign=(-1)**sum(permutation[i]>permutation[j] for i in range(size) for j in range(i+1,size))
        term=[F(1)]
        for i,j in enumerate(permutation):term=mul(term,matrix[i][j])
        out=add(out,scale(term,sign))
    return out

def taylor_multiply(a,b,H):
    return [add(*(mul(a[j],b[k-j]) for j in range(k+1))) for k in range(H+1)]
def scalar_multiply(a,b,H):
    return [sum(a[j]*b[k-j] for j in range(k+1)) for k in range(H+1)]
def scalar_power(a,n,H):
    if n<0:
        inverse=[1/a[0]]
        for k in range(1,H+1):inverse.append(-sum(a[j]*inverse[k-j] for j in range(1,k+1))/a[0])
        return scalar_power(inverse,-n,H)
    out=[F(1)]+[F(0)]*H
    for _ in range(n):out=scalar_multiply(out,a,H)
    return out

def branch_rows(u,H):
    # Coefficients of u(x+h), with x=u+1/u. Taylor coefficients include 1/h!.
    us=[u]
    if H>=1:us.append(u*u/(u*u-1))
    if H>=2:us.append(-u**3/(u*u-1)**3)
    assert H<=2
    inv=scalar_power(us,-1,H)
    assert us[0]+inv[0]==u+1/u
    if H:assert us[1]+inv[1]==1
    if H>=2:assert us[2]+inv[2]==0
    v=[F(0)]+[x/u for x in us[1:]]
    power_n=[[] for _ in range(H+1)];choose=[F(1)]
    for k in range(H+1):
        if k:choose=scale(mul(choose,[F(1-k),F(1)]),F(1,k))
        term=scalar_power(v,k,H)
        for h,c in enumerate(term):power_n[h]=add(power_n[h],scale(choose,c))
    inverse2=scalar_power(us,-2,H);inverse4=scalar_multiply(inverse2,inverse2,H)
    A=[(1 if h==0 else 0)-2*inverse2[h]+inverse4[h] for h in range(H+1)]
    B=[(-7 if h==0 else 0)+8*inverse2[h]-inverse4[h] for h in range(H+1)]
    columns=[]
    for j in range(4):
        shift=[F(j),F(1)]
        ell=[add(scale(ppow(shift,2),A[h]),scale(shift,B[h]),[F(12)] if not h else []) for h in range(H+1)]
        uj=[[value] if value else [] for value in scalar_power(us,j,H)]
        columns.append(taylor_multiply(taylor_multiply(power_n,uj,H),ell,H))
    return [[columns[j][h] for j in range(4)] for h in range(H+1)]

def jet_case(groups):
    roots=[u+1/u for u,m in groups]
    vandermonde=prod((roots[j]-roots[i])**(groups[i][1]*groups[j][1])
        for i in range(len(groups)) for j in range(i+1,len(groups)))
    assert vandermonde and all(u*u!=1 for u,m in groups)
    row_data=[]
    for u,m in groups:
        branches=[branch_rows(u,m-1),branch_rows(1/u,m-1)]
        row_data.extend([(u,1/u,[branches[0][h],branches[1][h]]) for h in range(m)])
    modes={};leading_checks=0
    for signs in itertools.product(range(2),repeat=4):
        matrix=[row[2][sign] for row,sign in zip(row_data,signs)]
        raw=determinant(matrix);quotient,remainder=orders.divide(raw,[F(0),F(-1),F(1)])
        assert not remainder
        polynomial=scale(quotient,F(1,4608)/vandermonde)
        us=[row[sign] for row,sign in zip(row_data,signs)];frequency=2*prod(us)
        modes[frequency]=add(modes.get(frequency,[]),polynomial)
        consistent=True;position=0
        for u,m in groups:
            consistent &= len(set(signs[position:position+m]))==1;position+=m
        if consistent:
            A=prod((1-u**-2)**2 for u in us)/prod(1-1/(us[i]*us[j]) for i in range(4) for j in range(i+1,4))
            assert len(polynomial)==7 and polynomial[6]==A/4608
            assert polynomial[5]==A*F(-15-6*sum(1/(u*u-1) for u in us),4608)
            leading_checks+=1
    modes={key:value for key,value in modes.items() if value}
    R=[F(1)]
    for root,(u,m) in zip(roots,groups):
        for _ in range(m):R=mul(R,[-root,F(1)])
    direct=0
    for N in range(1,17):
        actual=direct_determinant([[sum(c*nu(i+j+k) for k,c in enumerate(R)) for j in range(N)] for i in range(N)])
        predicted=sum(frequency**N*evaluate(polynomial,N) for frequency,polynomial in modes.items())
        assert actual==predicted,(groups,N);direct+=1
    assert sum(evaluate(polynomial,0) for polynomial in modes.values())==F(1,2)
    return modes,direct,leading_checks

def jet_audit():
    cases=[('simple',[(2,1),(3,1),(5,1),(7,1)],112),
        ('triple_product',[(2,1),(3,1),(F(1,6),1),(5,1)],98),
        ('positive_full',[(2,1),(3,1),(5,1),(F(1,30),1)],105),
        ('negative_full',[(2,1),(3,1),(5,1),(F(-1,30),1)],104),
        ('one_double',[(2,2),(3,1),(5,1)],88),
        ('double_AA_collision',[(2,2),(F(1,4),1),(3,1)],74),
        ('double_AB_collision',[(2,2),(3,1),(F(1,6),1)],74),
        ('double_positive_full',[(2,2),(3,1),(F(1,12),1)],81),
        ('double_negative_full',[(2,2),(3,1),(F(-1,12),1)],80),
        ('two_double',[(2,2),(3,2)],69),('triple_root',[(2,3),(3,1)],64)]
    total_direct=total_leading=0;results=[];saved={}
    for label,groups,expected in cases:
        groups=[(F(u),m) for u,m in groups];modes,direct,leading=jet_case(groups)
        order=sum(len(p) for p in modes.values());assert order==expected,(label,order,expected)
        results.append({'label':label,'order':order,'frequencies':len(modes),
            'coefficient_degrees':sorted(len(p)-1 for p in modes.values())})
        total_direct+=direct;total_leading+=leading;saved[label]=modes
    for groups,label in [([(5,1),(2,1),(7,1),(3,1)],'simple'),
                         ([(F(1,2),2),(3,1),(5,1)],'one_double')]:
        actual,direct,leading=jet_case([(F(u),m) for u,m in groups]);assert actual==saved[label]
        total_direct+=direct;total_leading+=leading
    return {'cases':results,'direct_determinants':total_direct,'leading_identities':total_leading,
        'root_order_and_inverse_choice_invariance':True}

def polynomial_leaves(coefficients,certificate):
    first=[sparse.decode(row) for row in coefficients]
    for j,p in enumerate(first):
        assert all(i<=j and k<=j//2 for i,k in p)
    all_coefficients=first+list(reversed(first[:-1]))
    t,q=sparse.atom(1),sparse.atom(0,1);one=sparse.ONE
    plus=sparse.add(*all_coefficients)
    expected=sparse.mul(sparse.power(q,2),sparse.power(sparse.add(q,sparse.scale(sparse.power(t,2),36)),2))
    assert plus==expected
    B=sparse.add(sparse.power(q,2),sparse.mul(q,sparse.add(sparse.scale(sparse.power(t,2),36),sparse.scale(t,-16),sparse.scale(one,32))),
        sparse.scale(sparse.power(sparse.add(t,sparse.scale(one,-2)),2),64))
    minus=sparse.add(*(sparse.scale(p,(-1)**j) for j,p in enumerate(all_coefficients)))
    assert minus==sparse.power(B,2)
    substitution=sparse.scale(sparse.add(t,one),-16)
    substituted=sparse.add(*(sparse.scale(sparse.mul(sparse.power(t,i),sparse.power(substitution,j)),c) for (i,j),c in B.items()))
    assert substituted==sparse.atom(3,0,-576)
    node_checks=0
    for T in map(F,range(9)):
        for W in map(F,range(5)):
            actual=base_polynomial([16-8*T,W*(6*T-4),2*T-8,W,F(1)])
            candidate=orders.characteristic(T,W*W,coefficients)
            assert all(value==candidate[j]*2**j for j,value in enumerate(actual))
            node_checks+=1
    P=list(map(F,certificate['triple_y_polynomial']));assert P==[F(-768),F(1280),F(480),F(144),F(13)]
    Y=[F(0),F(1)];D=mul(Y,ppow([F(12),F(1)],2));numerator=scale(ppow([F(4),F(3)],2),16)
    tests={'within_triple':mul(mul(Y,[F(-1),F(1)]),[F(-4),F(1)]),
        'distinct_or_opposite':add(numerator,scale(mul(Y,D),-1)),
        'endpoint_simple':add(numerator,scale(D,-4)),
        'cross_k2':add(numerator,scale(mul(ppow([F(-2),F(1)],2),D),-1)),
        'cross_k3':add(numerator,scale(mul(mul(Y,ppow([F(-3),F(1)],2)),D),-1)),
        'denominators':mul(Y,[F(12),F(1)]),'t_nonzero':[F(48),F(8),F(3)],
        'w_nonzero':[F(-16),F(24),F(3)]}
    assert [item['label'] for item in certificate['triple_noncollision_bezout']]==list(tests)
    for item in certificate['triple_noncollision_bezout']:
        Q=list(map(F,item['polynomial']));assert Q==tests[item['label']],item['label']
        assert add(mul(list(map(F,item['u'])),P),mul(list(map(F,item['v'])),Q))==[F(1)]
    yp12=[F(12),F(1)];three_y_p4=[F(4),F(3)]
    elimination=add(scale(mul(ppow(Y,2),ppow(yp12,2)),26),
        scale(mul(mul(Y,three_y_p4),yp12),-132),scale(ppow(three_y_p4,2),144),
        scale(mul(Y,ppow(yp12,2)),60),scale(mul(three_y_p4,yp12),-80))
    assert elimination==scale(P,2)
    assert orders.divide([F(16),F(24),F(1)],[F(20),F(17)])[1]==[F(-3136,289)]
    two_double=orders.classify(F(10,9),F(-400,9),coefficients)
    assert two_double['root_type']=='2+2' and two_double['distinct_bases']==9 and two_double['order']==69
    return {'characteristic_complete_nodes':node_checks,'characteristic_coefficient_checks':17*node_checks,
        'triple_noncollision_bezout_identities':len(tests),'triple_elimination_identity':True,
        'negative_full_nonvanishing_identity':True,'two_double_support_has_nine_distinct_bases':True}

def modular_multiply(a,b,p):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):out[i+j]=(out[i+j]+x*y)%p
    return out

def sample_replay(coefficients,certificate):
    nodes=[F(i*i) for i in range(57)]
    denominators=[prod(node-other for j,other in enumerate(nodes) if j!=i) for i,node in enumerate(nodes)]
    cache={};direct=0;rows=[]
    for item in certificate['samples']:
        t,q=F(item['t']),F(item['q'])
        if t not in cache:
            evaluations=[]
            for index in range(57):
                values=structured_differential_hankel([F(1),t],[F(1),F(index)],112)
                def moment(k):
                    m=k//2;value=(1+t*m)*comb(2*m,m)
                    return value if not k%2 else index*(2*m+1)*value
                for N in range(7):
                    assert values[N]==direct_determinant([[moment(i+j) for j in range(N)] for i in range(N)])
                    direct+=1
                evaluations.append(values)
            cache[t]=evaluations
            print(json.dumps({'replayed_t':str(t),'complete_q_nodes':57}),flush=True)
        if q in nodes:values=cache[t][nodes.index(q)]
        else:
            whole=prod(q-node for node in nodes)
            weights=[whole/((q-node)*denominators[i]) for i,node in enumerate(nodes)]
            values=[sum(weight*row[N] for weight,row in zip(weights,cache[t])) for N in range(113)]
        independent=orders.normalized_terms(t,q,13)
        assert values[:13]==independent,(item['label'],'rational moment basis')
        direct+=13
        c=orders.characteristic(t,q,coefficients)
        D=power([value*2**j for j,value in enumerate(c)],7)
        N=[sum(D[j]*values[k-j] for j in range(k+1)) for k in range(113)]
        Nr,Dr=list(map(F,item['reduced_numerator'])),list(map(F,item['reduced_denominator']))
        assert Dr[0]==1 and len(Nr)==len(Dr) and Nr[-1]==Dr[-1]/2
        assert mul(Nr,D)==mul(N,Dr),item['label']
        witness=item['modular_bezout'];prime=witness['prime']
        assert prime==1000003 and all(prime%j for j in range(2,isqrt(prime)+1))
        residue=lambda value:value.numerator*pow(value.denominator,-1,prime)%prime
        Nm,Dm=list(map(residue,Nr)),list(map(residue,Dr));assert Nm[-1] and Dm[-1]
        U,V=witness['u'],witness['v']
        left,right=modular_multiply(U,Nm,prime),modular_multiply(V,Dm,prime)
        length=max(len(left),len(right))
        identity=[((left[i] if i<len(left) else 0)+(right[i] if i<len(right) else 0))%prime for i in range(length)]
        assert identity==[1]+[0]*(length-1)
        prediction=orders.classify(t,q,coefficients)
        actual=len(Dr)-1
        assert prediction['order']==item['actual_order']==actual
        assert prediction['root_type']==item['root_type']
        assert prediction['distinct_bases']==item['distinct_bases']
        assert prediction['negative_full_collision']==bool(item['negative_full'])
        rows.append({'label':item['label'],'t':str(t),'q':str(q),'order':actual,
            'root_type':prediction['root_type'],'first_eight':[str(x) for x in values[:8]]})
    assert len(rows)==10 and len(cache)==6
    return {'cases':rows,'complete_parameter_nodes':57*len(cache),
        'defining_prefix_values':57*113*len(cache),'direct_monomial_determinants':direct,
        'exact_cross_multiplications':len(rows),'degree_preserving_modular_bezout_identities':len(rows)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--coefficients',required=True)
    p.add_argument('--certificate',required=True);p.add_argument('--output',required=True);a=p.parse_args()
    start=time.perf_counter();coefficients=json.loads(Path(a.coefficients).read_text())['first_eight_with_unit']
    certificate=json.loads(Path(a.certificate).read_text())
    leaves=polynomial_leaves(coefficients,certificate)
    jets=jet_audit();samples=sample_replay(coefficients,certificate)
    report={'outcome':'Interior polynomial leaves, confluence regressions and exact GF samples passed',
        'review':'project self-review, not independent review','polynomial_leaves':leaves,'jets':jets,'samples':samples,
        'jet_scope':'The rational-lift regression quartics need not lie in the mixed family; their numerical orders are checks of the confluence mechanism, not claims that all those orders occur in that family.',
        'scope':'The universal classification requires the written root-collision, confluence, coefficient-degree and specialization proofs. The finite samples alone do not prove it.',
        'elapsed_seconds':time.perf_counter()-start}
    Path(a.output).write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'outcome':report['outcome'],'coefficient_nodes':leaves['characteristic_complete_nodes'],
        'sample_nodes':samples['complete_parameter_nodes'],'direct_checks':jets['direct_determinants']+samples['direct_monomial_determinants'],
        'elapsed_seconds':report['elapsed_seconds']}))

if __name__=='__main__':main()
