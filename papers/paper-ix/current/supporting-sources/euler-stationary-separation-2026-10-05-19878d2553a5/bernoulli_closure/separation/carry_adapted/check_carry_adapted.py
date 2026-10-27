#!/usr/bin/env python3
"""Actual lower packets with rational Padé tail at the terminal carry reset.

Only the existing T=0 and T=718787533 are used. Complete local coefficients,
ordinary derivatives, stationary points where present, and errors are checked.
"""
from pathlib import Path
from fractions import Fraction as F
from functools import lru_cache
import hashlib,json,sys,time

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'vendor'))
import euler_packet_engine as base

P=256;MOD=1<<P;CONTENT=178;CENTER=10202;DEPTH=15
MAX_RANK=10
MOMENT_BITS=P+128


@lru_cache(None)
def fast_twoB(n,p):
    mod=1<<p;unit=1;valuation=0;out=0
    for k in range(min(n,p)+1):
        if k:
            num=n-k+1;vn=base.v2(num);vd=base.v2(k)
            unit=unit*((num>>vn)%mod)*pow(k>>vd,-1,mod)%mod
            valuation+=vn-vd
        if base.B[k] and valuation<p:
            out=(out+(unit<<valuation)*base.fmod((1<<k)*base.B[k],p))%mod
    return out*pow((1-pow(2,n-1,mod))%mod,-1,mod)%mod


def linmul(a,c,s,d,mod):
    out=[0]*min(len(a)+1,d+1)
    for i in range(len(out)):
        out[i]=(c*(a[i] if i<len(a) else 0)+(s*a[i-1] if i else 0))%mod
    return out


def local_source(src,c,prec,d):
    mod=1<<prec;out=[0]*(d+1)
    for t in reversed(src[:prec]):
        for i in range(d,0,-1):out[i]=(c*out[i]+(1<<DEPTH)*out[i-1])%mod
        out[0]=(c*out[0]+t)%mod
    return out


def conv(a,b,d,mod):
    out=[0]*(min(d,len(a)+len(b)-2)+1)
    for i,x in enumerate(a):
        for j in range(min(len(b),len(out)-i)):out[i+j]=(out[i+j]+x*b[j])%mod
    return out


def localize(gamma,src):
    degree=(P-1)//DEPTH;out=[0]*(degree+1);pq=[1]
    for q,g in enumerate(gamma):
        if q:
            j=q-1
            pq=linmul(pq,CENTER-j,1<<DEPTH,degree,MOD)
            pq=linmul(pq,2*CENTER-2*j-1,1<<(DEPTH+1),degree,MOD)
        if not g or not any(pq):continue
        vg=base.v2(g,P);vp=min(base.v2(c,P) for c in pq);prec=P-vg-vp
        if prec<=0:continue
        mod=1<<prec;d=min(degree,(prec-1)//DEPTH)
        ss=local_source(src,CENTER-q,prec,d)
        term=conv([(c>>vp)%mod for c in pq],ss,degree,mod)
        for i,x in enumerate(term):out[i]=(out[i]+((g>>vg)*x<<(vg+vp)))%MOD
    return out


def shift_moments(m,bits,count):
    mod=1<<bits;d0=fast_twoB(2*m,bits);inv=pow(d0,-1,mod)
    out=[1];odd=1;val=0
    for q in range(1,count):
        for j in (2*m+2*q-1,2*m+2*q):
            v=base.v2(j);val+=v;odd=odd*(j>>v)%mod
        exponent=2*q-val
        assert exponent==q.bit_count() and exponent>=1
        out.append((fast_twoB(2*m+2*q,bits)*inv*pow(odd,-1,mod)<<exponent)%mod)
    return out


def determinant(matrix):
    """Exact Bareiss determinant over Z, with row pivoting."""
    a=[row[:] for row in matrix];n=len(a);sign=1;previous=1
    if n==0:return 1
    for k in range(n-1):
        if not a[k][k]:
            j=next((j for j in range(k+1,n) if a[j][k]),None)
            if j is None:return 0
            a[k],a[j]=a[j],a[k];sign=-sign
        pivot=a[k][k]
        for i in range(k+1,n):
            for j in range(k+1,n):
                value=a[i][j]*pivot-a[i][k]*a[k][j]
                assert value%previous==0
                a[i][j]=value//previous
        for i in range(k+1,n):a[i][k]=0
        previous=pivot
    return sign*a[-1][-1]


def pade_denominator(moments,rank):
    matrix=[[moments[k-j] for j in range(1,rank+1)]
            for k in range(rank,2*rank)]
    rhs=[-moments[k] for k in range(rank,2*rank)]
    det=determinant(matrix);loss=base.v2(det,MOMENT_BITS)
    assert loss<MOMENT_BITS-P
    den=[]
    for j in range(rank):
        column=[row[:] for row in matrix]
        for i in range(rank):column[i][j]=rhs[i]
        numerator=determinant(column)
        assert base.v2(numerator,MOMENT_BITS)>=loss
        den.append(base.fmod(F(numerator,det),P))
    return den,loss


def characteristics(poly):
    coefficient_valuations=[base.v2(a,P)-CONTENT if a else P-CONTENT for a in poly]
    derivative=[i*poly[i]%MOD for i in range(1,len(poly))]
    answer={'coefficient_valuations_or_bounds':coefficient_valuations,
            'value_at_Z0_valuation':base.v2(poly[0],P)-CONTENT,
            'derivative_coefficient_valuations_or_bounds':[
                base.v2(a,P)-CONTENT if a else P-CONTENT for a in derivative]}
    critical_bits=P-CONTENT-1
    if not all(a%(1<<(CONTENT+1))==0 for a in derivative):
        assert base.v2(derivative[0],P)==CONTENT
        assert all(base.v2(a,P)>=CONTENT+1 for a in derivative[1:])
        answer['stationary_point']='none on Z2; derivative is an odd unit after normalization'
        return answer
    h=[(a>>(CONTENT+1))%(1<<critical_bits) for a in derivative]
    assert h[1]%2 and all(a%2==0 for a in h[2:])
    c=0
    for k in range(critical_bits):
        if base.ev(h,c,1<<(k+1)):c+=1<<k
    value=base.ev(poly,c,MOD)
    answer.update({'stationary_point':'unique','critical_center_residue':str(c),
        'critical_center_bits':critical_bits,'critical_raw_value':str(value),
        'critical_value_valuation':base.v2(value,P)-CONTENT})
    return answer


def main(output):
    started=time.monotonic()
    base.B=base.bernoullis(MOMENT_BITS);base.twoB=fast_twoB
    source=list(base.source(P))
    assert all(base.v2(a,P)>=i for i,a in enumerate(source))
    inherited=json.loads((ROOT/'inherited_actual.json').read_text())
    records=[]
    for inp in inherited['records']:
        T=int(inp['T']);r=(17659+(1<<18)*T)*(1<<640)-161;m=r+161
        assert base.v2(m)==640 and 2*r-1>P+8
        costs=[3*q+(r+q).bit_count()-r.bit_count() for q in range((r.bit_count()-1)//3+1)]
        assert min(costs)==-154 and max(q for q,v in enumerate(costs) if v==-154)==161
        cutoff=(P+r.bit_count()-154-2)//3
        assert 3*(cutoff+1)+1-r.bit_count()+154>=P
        actual_gamma=base.gamma(r,-154,P,cutoff)
        assert actual_gamma[161]%2
        actual_poly=localize(actual_gamma,source)
        assert all(x%(1<<CONTENT)==0 for x in actual_poly)
        actual_K=[x>>CONTENT for x in actual_poly]
        for i,x in enumerate(actual_K):
            assert x==inp['K'][i]%(1<<(P-CONTENT))
        actual_info=characteristics(actual_poly)
        assert actual_info['critical_value_valuation']==inp['expected_phi_valuation']
        moments=shift_moments(m,MOMENT_BITS,2*MAX_RANK+1)
        row={'T':str(T),'global_precision':P,'packet_cutoff':cutoff,
             'actual':actual_info,'actual_K_coefficients':list(map(str,actual_K)),
             'terminal_moment_valuations':[base.v2(a,MOMENT_BITS) for a in moments],
             'models':[]}
        for rank in range(1,MAX_RANK+1):
            den,loss=pade_denominator(moments,rank)
            assert loss==rank-1 and base.v2(den[-1],P)==1
            next_hankel=determinant([[moments[i+j] for j in range(rank+1)]
                                     for i in range(rank+1)])
            assert base.v2(next_hankel,MOMENT_BITS)==rank
            coefficients=[a%MOD for a in moments[:rank]]
            for t in range(rank,cutoff-160):
                coefficients.append(-sum(den[j-1]*coefficients[t-j]
                                         for j in range(1,rank+1))%MOD)
            assert coefficients[:2*rank]==[a%MOD for a in moments[:2*rank]]
            assert all(a%2==0 for a in coefficients[1:])
            first_error=(moments[2*rank]-coefficients[2*rank])%MOD
            assert base.v2(first_error,P)==1
            assert 3*(cutoff-160)>=P
            gamma=actual_gamma[:161]+[0]*(cutoff-160)
            inverse=pow(2*m-1,-1,MOD)
            for t,a in enumerate(coefficients):
                gamma[161+t]=(actual_gamma[161]*pow(8,t,MOD)*a*
                    (2*m+2*t-1)*inverse)%MOD
            match_count=2*rank
            assert gamma[161:161+match_count]==actual_gamma[161:161+match_count]
            poly=localize(gamma,source)
            info=characteristics(poly)
            delta=[(x-y)%MOD for x,y in zip(poly,actual_poly)]
            q0=161+2*rank
            expected_error=6*rank+1+sum(base.v2(CENTER-i) for i in range(q0))-CONTENT
            assert min(base.v2(a,P) for a in delta)-CONTENT==expected_error
            delta_derivative=[i*delta[i]%MOD for i in range(1,len(delta))]
            assert base.v2(delta_derivative[0],P)-CONTENT==expected_error+8
            assert all(base.v2(a,P)-CONTENT>=expected_error+8 for a in delta_derivative)
            info.update({'rank':rank,'matched_terminal_packets':match_count,
                'hankel_determinant_valuation':loss,
                'next_hankel_determinant_valuation':rank,
                'first_unmatched_moment_error_valuation':1,
                'proved_uniform_error_valuation':expected_error,
                'derivative_error_Gauss_valuation':expected_error+8,
                'denominator_coefficient_valuations_or_bounds':[base.v2(a,P) for a in den],
                'model_raw_coefficients':list(map(str,poly)),
                'error_coefficient_valuations_or_bounds':[
                    base.v2(a,P)-CONTENT if a else P-CONTENT for a in delta],
                'error_Gauss_valuation':min(base.v2(a,P) for a in delta)-CONTENT})
            if info['stationary_point']=='unique':
                cm=int(info['critical_center_residue']);ca=int(actual_info['critical_center_residue'])
                info['center_difference_valuation_or_bound']=base.v2(cm-ca,P-CONTENT-1)
                vm=int(info['critical_raw_value']);va=int(actual_info['critical_raw_value'])
                info['critical_value_difference_valuation']=base.v2((vm-va)%MOD,P)-CONTENT
                info['frozen_model_at_actual_center_valuation']=base.v2(base.ev(poly,ca,MOD),P)-CONTENT
                assert info['center_difference_valuation_or_bound']==expected_error+7
                assert info['critical_value_difference_valuation']==expected_error
            if (T,rank) in ((0,3),(718787533,6)):
                assert info['critical_value_valuation']==(0 if T==0 else 30)
                assert info['critical_value_valuation']<expected_error
                info['named_strict_transfer']='passed'
            row['models'].append(info)
        records.append(row)
    result={'status':'passed','arithmetic':'exact modular integer Bernoulli reconstruction and complete local polynomials',
        'records':records,'seconds':time.monotonic()-started,
        'nonclaims':['No new multiplier digits.','No universal critical nonvanishing.',
            'No source transform rationality claim.','Rank1/rank2 models are rational Bernoulli-derived tail replacements.']}
    Path(output).write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'seconds':result['seconds'],'records':[
        {'T':r['T'],'actual_critical_value_valuation':r['actual']['critical_value_valuation'],
         'models':[{k:v for k,v in z.items() if k not in ('model_raw_coefficients',
           'coefficient_valuations_or_bounds','derivative_coefficient_valuations_or_bounds',
           'error_coefficient_valuations_or_bounds','critical_raw_value','critical_center_residue')}
          for z in r['models']]} for r in records]},indent=2))


if __name__=='__main__':main(sys.argv[1] if len(sys.argv)>1 else 'CARRY_ADAPTED_CHECKS.json')
