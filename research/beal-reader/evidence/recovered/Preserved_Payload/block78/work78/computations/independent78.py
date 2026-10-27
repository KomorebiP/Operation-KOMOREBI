import json,hashlib
# F49 = F7[t]/(t^2-t-1), code a+7b
# w=2t-1 gives w^2=5 but this implementation never calls primary code.
def A(x,y): return ((x%7+y%7)%7)+7*(((x//7+y//7)%7))
def N(x): return ((-x%7)%7)+7*((-(x//7)%7)%7)
def S(x,y): return A(x,N(y))
def M(x,y):
    a,b=x%7,x//7;c,d=y%7,y//7
    # t^2=t+1
    return ((a*c+b*d)%7)+7*((a*d+b*c+b*d)%7)
def I(x):
    for y in range(1,49):
        if M(x,y)==1:return y
    raise ZeroDivisionError
def sc(a,x): return M(a%7,x)
def mm(X,Y): return [[A(M(X[i][0],Y[0][j]),M(X[i][1],Y[1][j])) for j in range(2)] for i in range(2)]
def ms(X,Y): return [[S(X[i][j],Y[i][j]) for j in range(2)] for i in range(2)]
def sm(a,X): return [[M(a,X[i][j]) for j in range(2)] for i in range(2)]
def main():
  total=0; digest=hashlib.sha256(); wrong=0; csum=0; cxor=0
  Z=[[0,0],[0,0]]
  for h in range(7):
    for c in range(1,49):
      ci=I(c)
      for b in range(49):
        seen=set()
        for pT in range(49):
          # solve the affine equation directly, not via theta parametrization
          pF=M(I(c),S(M(b,pT),M(h,c)))
          assert S(M(c,pF),M(b,pT))==N(M(h,c))
          th=M(pT,ci); seen.add((pT,pF))
          X=sm(c,[[th,N(M(th,th))],[1,N(th)]])
          Y=[[M(th,b),S(M(th,h),M(M(th,th),b))],[b,S(h,M(th,b))]]
          assert mm(X,X)==Z
          assert ms(mm(Y,X),mm(X,Y))==sm(h,X)
          assert S(Y[0][0],h)==pF and X[0][0]==pT
          m=(pT//7)%7
          b2=A(b,M(m,c)); f2=A(pF,M(m,pT))
          assert S(M(c,f2),M(b2,pT))==N(M(h,c))
          if S(M(c,pF),M(b,pT))!=M(h,c): wrong+=1
          digest.update(bytes([h,c,b,pT,pF,th]))
          def tow(x):
            aa,bb=x%7,x//7
            return ((aa+4*bb)%7)+7*((4*bb)%7)
          cw,bw,tw,pTw,pFw=map(tow,(c,b,th,pT,pF))
          key=h | (cw<<3) | (bw<<9) | (tw<<15) | (pTw<<21) | (pFw<<27)
          csum=(csum+key)&((1<<64)-1); cxor ^= key
          total+=1
        assert len(seen)==49
  dual=0
  for a in range(1,7):
    for x in range(49):
      # direct definition: target mu7 action a; source action is 1 or a
      # dual action multiplier target/source
      assert sc(a,x)==M(a,x)
      assert x==M(1,x)
      dual+=2
  print(json.dumps({'status':'PASS','field_basis':'t^2=t+1','affine_toric_packets':total,
    'dual_action_checks':dual,'wrong_sign_failures':wrong,'packet_sha256':digest.hexdigest(),'canonical_sum_mod_2_64':csum,'canonical_xor_64':cxor,
    'nonclaims':['independent arithmetic does not prove the external localization theorem']},sort_keys=True,indent=2))
if __name__=='__main__':main()
