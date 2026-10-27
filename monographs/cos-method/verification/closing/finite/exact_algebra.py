"""Finite exact controls for the proofreading corrections (not general proofs)."""
from pathlib import Path
import json
import sympy as s
out=[]
def record(name, condition, detail):
    assert condition, name
    out.append({'check':name,'passed':True,'detail':detail})
def nz_eigs(M):
    return {str(k):int(v) for k,v in M.eigenvals().items() if k!=0}
I=s.eye(3)
Q=s.Matrix([[1,0],[0,1/s.sqrt(2)],[0,1/s.sqrt(2)]])
B=s.Matrix([[1,0,1],[0,2,0]]);A=Q*B
record('Exact range example',Q.T*Q==s.eye(2) and nz_eigs(A*A.T)==nz_eigs(B*B.T), 'Nonzero eigenvalues are 2 and 4; full Gram has an extra zero.')
A=s.diag(1,0);Q=s.eye(2);B=Q.T*A
record('Oversized captured range',nz_eigs(A*A.T)==nz_eigs(B*B.T) and 0 in (B*B.T).eigenvals(), 'Core Gram retains zero; its entire spectrum is not the nonzero spectrum.')
A=s.Matrix([[1,0],[0,0],[0,0]]);Q=I[:,:2];U=I[:,2:3];R=Q.T*A;C=Q.T*U;F=U-Q*C;Qp=I[:,2:3];Rp=Qp.T*F
core=R.row_join(C).col_join(s.zeros(1,2).row_join(Rp));joined=A.row_join(U)
record('QR update with unused basis direction',joined==Q.row_join(Qp)*core and nz_eigs(joined*joined.T)==nz_eigs(core*core.T) and 0 in (core*core.T).eigenvals(), 'Factor identity is exact; unused old direction produces a zero core eigenvalue.')
A=s.diag(1,0,2);U=I[:,:2];B=U.T*A;F=(I-U*U.T)*A;W=I[:,2:3];D=W.T*F;core=B.col_join(D)
record('Residual completion with unused direction',A==U.row_join(W)*core and A.T*A==core.T*core and 0 in (core*core.T).eigenvals(), 'Nonzero singular values 1 and 2 agree; row Gram contains zero.')
A=s.Matrix([[1,1,0,0,0],[0,1,1,0,0],[0,0,1,1,0],[0,0,0,1,1]])
H=A.T*A;X=s.eye(5)[:,0:1]
for k in range(5):
    J=s.eye(5)[:,:k+1];HF=J.T*H*J;P=J*J.T
    assert HF==(A*J).T*(A*J) and P*H*P==J*HF*J.T
    assert H**k*X==J*HF**k*J.T*X
record('Compressed frontier coordinates',True,'All depths 0 through 4 on a five-phase path satisfy the dimensionally correct embedding identity.')
A=s.Matrix([[1,0],[0,2],[0,0],[0,0]]);U=s.eye(4)[:,:2];B=U.T*A
record('Rectangular zero padding',sorted((A*A.T).eigenvals().items(),key=lambda x:x[0])==[(0,2),(1,1),(4,1)] and (B*B.T).eigenvals()=={1:1,4:1}, 'Both singular-value lists require padding to four entries for the sample Gram.')
M=s.diag(4,9);S=s.diag(1,0);mu=s.Matrix([3,2]);T=s.diag(2,3)*S;b=s.diag(2,3)*mu;P=s.diag(1,0);c=S*M*mu
q0=(mu.T*M*mu)[0]-c[0]**2/4
record('Singular noncentral shift',q0==36 and q0==((s.eye(2)-P)*b).dot((s.eye(2)-P)*b),'The positive deterministic shift is 36 in weighted coordinates.')
H=s.eye(2);X=s.Matrix([1,0]);delta=(H-2*H)*X
record('Adaptive-coefficient negative control',delta!=s.zeros(2,1) and (H-H)*X==s.zeros(2,1),'Identical operators do not control two different polynomial coefficients; the shared-polynomial hypothesis is necessary.')
Path(__file__).with_name('exact_algebra_results.json').write_text(json.dumps({'all_passed':True,'checks':out},indent=2)+'\n')
print(json.dumps({'all_passed':True,'check_count':len(out),'checks':out},indent=2))
