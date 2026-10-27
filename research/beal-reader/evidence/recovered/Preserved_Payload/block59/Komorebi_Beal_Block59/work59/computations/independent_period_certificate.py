#!/usr/bin/env python3
"""Independent sqrt(5)-basis audit. Imports no primary arithmetic module."""
import argparse, hashlib, json
from pathlib import Path
from math import isqrt


def sieve(n):
    a=bytearray(b'\1')*(n+1);a[0:2]=b'\0\0'
    for p in range(2,isqrt(n)+1):
        if a[p]:a[p*p:n+1:p]=b'\0'*len(range(p*p,n+1,p))
    return [p for p in range(11,n+1) if a[p]]

class Residue:
    def __init__(self,p,phi_root):
        self.p=p;self.phi_root=phi_root;self.sroot=None if phi_root is None else (2*phi_root-1)%p
        self.order=p*p if self.sroot is None else p
        self.one=(1,0);self.zero=(0,0)
        self.s=(0,1) if self.sroot is None else (self.sroot,0)
        self.phi=self.scale(self.add(self.one,self.s),pow(2,-1,p))
    def add(self,x,y):return ((x[0]+y[0])%self.p,(x[1]+y[1])%self.p)
    def scale(self,x,k):return (x[0]*k%self.p,x[1]*k%self.p)
    def sub(self,x,y):return self.add(x,self.scale(y,-1))
    def mul(self,x,y):return ((x[0]*y[0]+5*x[1]*y[1])%self.p,(x[0]*y[1]+x[1]*y[0])%self.p)
    def pow(self,x,n):
        # Left-to-right exponentiation, separate from primary's implementation.
        ans=self.one
        for bit in bin(n)[2:]:
            ans=self.mul(ans,ans)
            if bit=='1':ans=self.mul(ans,x)
        return ans
    def inv(self,x):
        if x==self.zero:raise ZeroDivisionError
        norm=(x[0]*x[0]-5*x[1]*x[1])%self.p
        return (x[0]*pow(norm,-1,self.p)%self.p,-x[1]*pow(norm,-1,self.p)%self.p)
    def div(self,x,y):return self.mul(x,self.inv(y))
    def c(self,n):return(n%self.p,0)
    def phicoord(self,x):
        return [x[0],0] if self.sroot is not None else [(x[0]-x[1])%self.p,2*x[1]%self.p]
    def phiword(self,a,b):return self.add(self.c(a),self.scale(self.phi,b))

def allfields(p):
    roots=[x for x in range(p) if (x*x-5)%p==0]
    proots=sorted({(1+x)*pow(2,-1,p)%p for x in roots})
    return [Residue(p,r) for r in proots] if roots else [Residue(p,None)]

def val7(n):
    assert n
    z=0
    while n%7==0:z+=1;n//=7
    return z

def onefield(f):
    a=f.scale(f.sub(f.s,f.one),pow(2,-1,f.p));b=f.scale(f.add(f.one,f.s),-pow(2,-1,f.p))
    delta=f.scale(f.sub(f.c(5),f.s),3*pow(2,-1,f.p))
    # Geometric tangent and secant parameter values, not hard-coded lambdas.
    lambda_a=f.sub(a,f.one)
    lambda_bplus=f.div(f.sub(f.mul(f.phi,delta),delta),f.sub(b,a))
    lambda_bminus=f.div(f.sub(f.scale(f.mul(f.phi,delta),-1),delta),f.sub(b,a))
    for X,Y in ((a,delta),(a,f.scale(delta,-1)),(b,f.mul(f.phi,delta)),(b,f.scale(f.mul(f.phi,delta),-1))):
        assert f.mul(Y,Y)==f.mul(delta,f.add(f.mul(f.sub(X,f.one),f.sub(X,f.one)),f.c(4)))
    assert len({lambda_a,lambda_bplus,lambda_bminus})==3
    c=f.div(f.sub(lambda_a,lambda_bplus),f.sub(lambda_a,lambda_bminus))
    assert c==f.scale(f.pow(f.inv(f.phi),4),-1)
    h=val7(f.order-1)
    flags=[]
    for r in (1,2,3):
        power=7**min(h,r)
        p=f.pow(f.phi,(f.order-1)//power)==f.one
        assert p==(f.pow(c,(f.order-1)//power)==f.one)
        flags.append(p)
    return {'q':f.p,'phi_root':f.phi_root,'norm':f.order,'h':h,'cross_ratio':f.phicoord(c),
            'phi_is_7_power':flags[0],'phi_is_49_power':flags[1],'phi_is_343_power':flags[2]}

def determinant_subset(A):
    # Leibniz expansion via subsets, no elimination/Bareiss.
    n=len(A);dp={0:1}
    for i in range(n):
        new={}
        for mask,z in dp.items():
            for j in range(n):
                if mask>>j&1:continue
                sgn=-1 if (mask>>(j+1)).bit_count()%2 else 1
                m=mask|(1<<j);new[m]=new.get(m,0)+sgn*z*A[i][j]
        dp=new
    return dp[(1<<n)-1]

def verify_frozen(root,primary):
    frozen=json.loads((root/'work59/source_records/frozen_block58_reciprocity.json').read_text())
    M=frozen['matrix_mod7'];count=0
    for j,row in enumerate(frozen['places']):
        f=Residue(row['q'],row['phi_root']);symbols=[]
        for elem in frozen['row_elements']:
            z=f.phiword(*elem['phi_coefficients']);assert z!=f.zero
            symbols.append(f.pow(z,(f.order-1)//7))
        k=next(i for i in range(15) if M[i][j]%7)
        base=f.pow(symbols[k],pow(M[k][j],-1,7));assert base!=f.one
        for i,z in enumerate(symbols):assert z==f.pow(base,M[i][j]);count+=1
    idx=primary['correction_test']['selected_row_indices'];square=[M[i] for i in idx]
    d=determinant_subset(square)
    assert d==primary['correction_test']['integer_determinant'] and d%7
    for i,x in enumerate(primary['correction_test']['transpose_basis_preimages']):
        assert [sum(square[k][j]*x[k] for k in range(12))%7 for j in range(12)]==[int(j==i) for j in range(12)]
    # Exhaust all normalized F49 coefficients, explicitly in sqrt(5) basis mod7.
    surviving_records=[]
    for ua in range(7):
      for ub in range(7):
       for ra in range(7):
        for rb in range(7):
         if not (ra or rb):continue
         possible=[]
         for q in (197,883,1373,1667):
            j=next(j for j,x in enumerate(frozen['places']) if x['q']==q)
            f0,f3,f5=M[0][j],M[2][j],M[3][j]
            if ((f0*ua+f3*ra+f5)%7,(f0*ub+f3*rb)%7)==(0,0):possible.append(q)
         expect=[883]
         if (ra,rb)==(6,0):expect=[197,883]
         if (ra,rb)==(1,0):expect=[883,1373,1667]
         assert possible==expect
         surviving_records.append(possible)
    return {'residue_symbols_checked':count,'determinant':d,'F49_directions':len(surviving_records),
            'all_directions_retain_883':all(883 in x for x in surviving_records)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--primary',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    root=Path(__file__).resolve().parents[2];target=json.loads(a.primary.read_text())
    U=[97,197,293,491,587,883,1373,1471,1567,1667]
    got=[onefield(f) for q in U for f in allfields(q)];assert got==target['universe']
    allp=sieve(20000)
    grid=[onefield(f) for q in allp if q<=2000 for f in allfields(q)]
    assert len(grid)==target['cross_grid_count']
    assert hashlib.sha256(json.dumps(grid,sort_keys=True).encode()).hexdigest()==target['cross_grid_digest']
    high=[]
    for q in allp:
        # Legendre test independently computed by finding square roots of 5.
        deg=1 if pow(5,(q-1)//2,q)==1 else 2
        if (q**deg-1)%49==0:high.extend(onefield(f) for f in allfields(q))
    controls=[x for x in high if x['phi_is_7_power'] and not x['phi_is_49_power']]
    assert len(high)==target['high_scan_places'] and controls==target['seventh_but_not_49th_controls']
    f13=allfields(13)[0]
    sym13=[f13.phicoord(f13.pow(z,24)) for z in (f13.phi,f13.c(3),f13.s)]
    assert sym13==target['bad13_symbols_phi_basis']==[[5,10],[1,0],[1,0]]
    out={'bad13_symbols_phi_basis':sym13,'status':'PASS_INDEPENDENT_FINITE_ASSERTIONS','universe_places':len(got),'cross_grid':len(grid),
         'high_scan_places':len(high),'power_strength_controls':controls,**verify_frozen(root,target)}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps(out,sort_keys=True))
if __name__=='__main__':
    if not __debug__: raise RuntimeError('Run without Python optimization; assertions are required')
    main()
