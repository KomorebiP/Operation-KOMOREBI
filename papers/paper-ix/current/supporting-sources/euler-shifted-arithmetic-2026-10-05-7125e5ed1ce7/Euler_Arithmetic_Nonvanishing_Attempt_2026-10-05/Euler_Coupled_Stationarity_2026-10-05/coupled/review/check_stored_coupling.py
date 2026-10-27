#!/usr/bin/env python3
"""Independent bounded algebra on frozen coefficient records; no Euler rebuild."""
import hashlib,json,math,platform,sys
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OLD=ROOT/'recovered/Komorebi_Euler_Parameter_Nonintersection_2026-10-04/Euler_Nonintersection_Certificate/fast_certificate_629.json'
MODEL=ROOT/'coupled/parameter_geometry/model_coefficients.json'
PACKETS=ROOT/'coupled/packet_balance/packet_ledger.json'

def ev(p,x,m):
    return sum(int(a)*pow(x,i,m) for i,a in enumerate(p))%m
def der(p):return [i*int(a) for i,a in enumerate(p) if i]
def v(a,cap):
    a%=1<<cap
    return cap if not a else (a&-a).bit_length()-1
def fm(a,m):return a.numerator*pow(a.denominator,-1,m)%m
def mul(a,b):
    c=[Fraction(0)]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):c[i+j]+=x*y
    return c

def run():
    old=json.loads(OLD.read_text()); model=json.loads(MODEL.read_text())
    assert model['origin_sha256']==hashlib.sha256(OLD.read_bytes()).hexdigest()
    H0=list(map(int,old['H0']));H1=list(map(int,old['H1']))
    assert H0==list(map(int,model['H0'])) and H1==list(map(int,model['H1']))
    assert [a%256 for a in H0]==[215,72,107]+[0]*(len(H0)-3)
    assert [a%256 for a in H1]==[189]+[0]*(len(H1)-1)
    assert [pow(251,-1,256)*a%256 for a in [215,72,107,189]]==[213,88,81,167]
    assert (44+81*20)%128==0
    assert (213+88*20+81*400)%256==69
    assert all(a%256==0 for a in H0[3:]) and all(a%(1<<25)==0 for a in H1[2:])
    assert [v(a,451) for a in H0[:7]]==[0,3,0,8,19,28,39]
    assert [v(a,451) for a in H1[:7]]==[0,8,25,42,58,74,90]

    # Newton source numerator built with exact rationals from its defining sum.
    num=[Fraction(0)]*4;fall=[Fraction(1)]
    for q in range(4):
        for i,a in enumerate(fall):num[i]+=Fraction(8**q,math.factorial(q+1))*a
        fall=mul(fall,[-q,1])
    source=mul(num,[(-2)**i for i in range(7)])[:7]
    source=[fm(a,128) for a in source]
    assert source==[1,34,92,8,112,32,64]
    r=(17659<<640)-161
    def depletion_residue(m):
        n=2*m
        return fm(Fraction(1-n)+Fraction(2,3)*math.comb(n,2)-Fraction(8,15)*math.comb(n,4)+Fraction(32,21)*math.comb(n,6),64)
    D0,D1=map(depletion_residue,[r,r+1]);assert [D0,D1]==[13,1]
    u=D1*pow(D0*(2*r-1)*((r+1)//32),-1,64)%64
    assert u==43
    logquarter=fm(sum((Fraction((-1)**(j+1)*8**j,4*j) for j in range(1,7)),Fraction(0)),128)
    ap=ev(der(source),10202,128);other=u*logquarter*pow(9,10202,128)%128
    assert [ap,other,(ap+other)%128]==[50,94,16]
    assert (ev(source,10202,32)+u*((pow(9,10202,128)-1)//4))%32==17
    assert (pow(9,10202,128)-1)//16%8==1

    packet=json.loads(PACKETS.read_text());M=1<<320;A=1<<178;checks=[]
    sums=[]
    for case in packet['cases']:
        z=int(case['stationary_Z']);T=int(case['T']);B=int(case['B'])
        total=[0]*22
        for row in case['packets']:
            p=list(map(int,row['coefficients']))
            for i,a in enumerate(p):total[i]=(total[i]+a)%M
            for ch,pp in [('value',p),('half_derivative',der(p)),('second_derivative',der(der(p)))]:
                assert ev(pp,z,M)==int(row[ch]['raw_residue'])
        assert all(a%A==0 for a in total)
        K=[a//A for a in total]
        assert [(B*a)% (1<<142) for a in K]==[(a+T*b)%(1<<142) for a,b in zip(H0,H1)][:22]
        assert all((a+T*b)%(1<<142)==0 for a,b in list(zip(H0,H1))[22:])
        assert ev(der(total),z,M)==0
        value=v(ev(total,z,M),320)-178
        assert value==case['groups']['total']['value']['normalized_valuation']
        assert v(ev(der(der(total)),z,M),320)-178==1
        bal=case['unit_balance']; assert bal['individual_value_unit_stable_bits']==149
        assert bal['individual_derivative_unit_stable_bits']==152
        assert bal['certified_obstruction_bits']==152
        m=1<<152
        L,U,D,E=[int(bal[k]) for k in ['lower_value_unit','upper_value_unit','lower_derivative_unit','upper_derivative_unit']]
        assert (D+E)%m==0
        assert (L*E-U*D)%m==(-(L+U)*D)%m==int(bal['cross_obstruction'])
        assert (1+U*pow(L,-1,m))%m==int(bal['relative_value_imbalance'])
        assert v(int(bal['relative_value_imbalance']),152)==18+value
        checks.append({'T':str(T),'critical_value_valuation':value,'stationary_residue_bits':141,'obstruction_valuation':18+value})
        sums.append(total)
    motions=[]
    for a,b in [(0,1),(1,2),(0,2)]:
        ca,cb=packet['cases'][a],packet['cases'][b]
        za,zb=int(ca['stationary_Z']),int(cb['stationary_Z'])
        n=v(int(ca['T'])-int(cb['T']),320);motion=v(za-zb,320)
        error=v(ev(sums[b],za,M)-ev(sums[b],zb,M),320)-178
        assert motion==n+7 and error==2*motion
        motions.append({'parameter_valuation':n,'center_valuation':motion,'frozen_error_valuation':error})
    return {'status':'PASS','python':platform.python_version(),'arithmetic':'exact integers and rational coefficients, finite stored-record audit',
            'actual_K_mod256':[213,88,81],'T_slope_mod256':167,'critical_point_mod128':20,'critical_value_mod256_constant':69,
            'source_and_q1_derivative_mod128':[ap,other,(ap+other)%128],'depleted_q1_unit_mod64':u,
            'packet_cases':checks,'motion_checks':motions,
            'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [OLD,MODEL,PACKETS]},
            'nonclaims':['No fresh high-index Euler reconstruction','No new singular parameter lift','No all-precision interpolation in T','No universal Euler simplicity']}

if __name__=='__main__':
    result=run();out=Path(sys.argv[1]);out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
