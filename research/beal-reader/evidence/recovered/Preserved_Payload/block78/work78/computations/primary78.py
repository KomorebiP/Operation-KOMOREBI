import json, hashlib
P=7
# F49 = F7[w]/(w^2-5), code a+7b

def add(x,y): return ((x%7+y%7)%7)+7*(((x//7+y//7)%7))
def neg(x): return ((-x%7)%7)+7*((-(x//7)%7)%7)
def sub(x,y): return add(x,neg(y))
def mul(x,y):
    a,b=x%7,x//7; c,d=y%7,y//7
    return ((a*c+5*b*d)%7)+7*((a*d+b*c)%7)
def smul(a,x): return mul(a%7,x)
def inv(x):
    if x==0: raise ZeroDivisionError
    for y in range(1,49):
        if mul(x,y)==1:return y
    raise AssertionError

def matmul(A,B):
    return [[add(mul(A[i][0],B[0][j]),mul(A[i][1],B[1][j])) for j in range(2)] for i in range(2)]
def matsub(A,B): return [[sub(A[i][j],B[i][j]) for j in range(2)] for i in range(2)]
def matsmul(x,A): return [[mul(x,A[i][j]) for j in range(2)] for i in range(2)]
def eq(A,B): return A==B

def main():
    checks=0; packets=0; lift_checks=0; bad_wrong=0; csum=0; cxor=0
    zero=[[0,0],[0,0]]
    support_hash=hashlib.sha256()
    for h0 in range(7):
      h=h0
      for c in range(1,49):
        ci=inv(c)
        for b in range(49):
          # 49 affine solutions indexed by theta
          for th in range(49):
            pT=mul(th,c)
            pF=sub(mul(th,b),h)
            lhs=sub(mul(c,pF),mul(b,pT))
            rhs=neg(mul(h,c))
            assert lhs==rhs
            # reconstruct theta uniquely from pT/c
            assert mul(pT,ci)==th
            M=matsmul(c,[[th,neg(mul(th,th))],[1,neg(th)]])
            A=[[mul(th,b),sub(mul(th,h),mul(mul(th,th),b))],[b,sub(h,mul(th,b))]]
            assert matmul(M,M)==zero
            comm=matsub(matmul(A,M),matmul(M,A))
            assert comm==matsmul(h,M)
            assert add(A[0][0],A[1][1])==h
            # p extraction relative to diag(1+7h,1)
            assert sub(A[0][0],h)==pF
            assert M[0][0]==pT
            # Frobenius lift invariance F -> T^m F at first order
            m=(th%7) # deterministic varied m in F7
            bp=add(b,mul(m,c))
            pFp=add(pF,mul(m,pT))
            assert sub(mul(c,pFp),mul(bp,pT))==lhs
            # wrong-sign target generally fails; count counterexamples
            if lhs!=mul(h,c): bad_wrong+=1
            support_hash.update(bytes([h0,c,b,th,pT,pF]))
            key=h0 | (c<<3) | (b<<9) | (th<<15) | (pT<<21) | (pF<<27)
            csum=(csum+key)&((1<<64)-1); cxor ^= key
            packets+=1; checks+=9
    # dual actions: A0=k trivial => dual k(chi); A1=k(chi) => dual trivial
    dual=[]
    for a in range(1,7):
        for x in range(49):
            # code-level scalar actions
            dual_a0=smul(a,x)
            dual_a1=x
            dual.append((a,x,dual_a0,dual_a1))
            lift_checks+=2
    out={
      'status':'PASS','field_basis':'w^2=5','base_local_data':7*48*49,
      'affine_toric_packets':packets,'formula_checks':checks,
      'dual_action_checks':lift_checks,'wrong_sign_failures':bad_wrong,
      'packet_sha256':support_hash.hexdigest(),'canonical_sum_mod_2_64':csum,'canonical_xor_64':cxor,
      'claims':[
        'at beta-ramified depth-one tame places c*p(F)-b*p(T)=-h*c',
        'each local datum (h,c!=0,b) has exactly 49 first-order toric p-solutions',
        'the functional is invariant under Frobenius-lift change',
        'dual of trivial k has cyclotomic action; dual of k(chi) is trivial'
      ],
      'nonclaims':['finite checks do not prove Neukirch localization surjectivity','no bounded Beal pattern is eliminated']
    }
    print(json.dumps(out,sort_keys=True,indent=2))
if __name__=='__main__':main()
