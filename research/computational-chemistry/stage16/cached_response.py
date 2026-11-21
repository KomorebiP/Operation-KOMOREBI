"""Prepared immutable cache; the Stage 15 arithmetic enclosure is retained."""
from pathlib import Path
import sys
import numpy as np
from fractions import Fraction as F
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'stage15'))
from full_model import sqrt_upper
from float_certificate import norm_upper,exponent_bound,gamma,abs_upper

def prepare_basis(model,Q,Y,source):
    # flat iterates strided/mapped arrays without ravel's potentially large copy.
    exp=lambda a:max((F(float(x)).denominator.bit_length()-1 for x in np.asarray(a).flat),default=0)
    if Q.shape!=Y.shape or len(source)!=Q.shape[0]:raise ValueError('Basis/image dimensions differ')
    qe,ye,be=exp(Q),exp(Y),exp(source)
    if qe+model.coefficient_denominator_exponent+1>=1000:raise ValueError('Action range guard failed')
    qnorms=[];q2=[];y2=[];errors=[]
    for j in range(Q.shape[1]):
        q,n2=norm_upper(Q[:,j],qe);qnorms.append(q);q2.append(n2)
        _,n2=norm_upper(Y[:,j],ye);y2.append(n2);errors.append(model.action_error_per_norm*q)
    b,b2=norm_upper(source,be)
    return dict(q_exponent=qe,y_exponent=ye,b_exponent=be,q_norms=qnorms,q_frobenius_upper=sqrt_upper(sum(q2)),y_frobenius_upper=sqrt_upper(sum(y2)),image_errors=errors,b_norm_upper=b,b_norm_squared_upper=b2)

class ResponseCache:
    def __init__(self,model,Q,Y,source,copy=True):
        if np.iscomplexobj(Q) or np.iscomplexobj(Y) or np.iscomplexobj(source):raise ValueError('This endpoint implementation requires real data')
        if not copy and (Q.dtype!=np.dtype(float) or Y.dtype!=np.dtype(float) or Q.flags.writeable or Y.flags.writeable):raise ValueError('Borrowed caches must be read-only binary64 arrays')
        self.model=model;self.Q=np.array(Q,dtype=float,copy=True) if copy else np.asarray(Q);self.Y=np.array(Y,dtype=float,copy=True) if copy else np.asarray(Y);self.source=np.array(source,dtype=float,copy=True)
        Q,Y,source=self.Q,self.Y,self.source
        self.k=Q.shape[1];self.N=Q.shape[0];self.G=Q.T@Q;K=Q.T@Y;self.K=(K+K.T)/2;self.rhs=Q.T@source
        self.prepared=prepare_basis(model,Q,Y,source)
        for value in [Q,Y,source]:value.flags.writeable=False

    def evaluate(self,energies,etas,metadata,chunk=8):
        model,Q,Y,source=self.model,self.Q,self.Y,self.source
        k,N,G,K,rhs,prepared=self.k,self.N,self.G,self.K,self.rhs,self.prepared
        result=[]
        targets=[(E,eta) for eta in etas for E in energies]
        for start in range(0,len(targets),chunk):
            current=targets[start:start+chunk]
            coefficients=np.column_stack([np.linalg.solve(complex(float(E),float(eta))*G-K,rhs) for E,eta in current])
            X=np.empty((N,len(current)),dtype=complex);W=np.empty_like(X)
            X.real=Q@coefficients.real;X.imag=Q@coefficients.imag
            W.real=Y@coefficients.real;W.imag=Y@coefficients.imag
            for col,(E,eta) in enumerate(current):
                a=coefficients[:,col];x=X[:,col];w=W[:,col];z=complex(float(E),float(eta))
                ae=max(exponent_bound(a.real),exponent_bound(a.imag));ze=max(exponent_bound([z.real]),exponent_bound([z.imag]))
                xe=prepared['q_exponent']+ae;we=prepared['y_exponent']+ae
                re=max(prepared['b_exponent'],ze+xe,we)
                if max(2*re,xe+re,prepared['b_exponent']+xe)>=1000:raise ValueError('Certificate range guard failed')
                r=source-z*x+w;center=source@x;cross=x@r
                nx,_=norm_upper(x,xe);nw,_=norm_upper(w,we);nr,_=norm_upper(r,re)
                ar,_=norm_upper(a.real,ae);ai,_=norm_upper(a.imag,ae)
                ex=gamma(2*k)*prepared['q_frobenius_upper']*(ar+ai)
                ey=gamma(2*k)*prepared['y_frobenius_upper']*(ar+ai)
                image_error=sum(error*abs_upper(value) for error,value in zip(prepared['image_errors'],a))
                z1=abs(F(float(z.real)))+abs(F(float(z.imag)))
                product_error=2*gamma(3)*z1*nx
                addition_error=2*gamma(2)*(prepared['b_norm_upper']+(1+2*gamma(3))*z1*nx+nw)
                z_error=sqrt_upper((F(float(z.real))-E)**2+(F(float(z.imag))-eta)**2)*nx
                residual_error=ey+image_error+model.norm_upper*ex+product_error+addition_error+z_error
                cross_error=4*gamma(8*N)*nx*nr
                center_error=2*gamma(2*N)*prepared['b_norm_upper']*nx
                radius=abs_upper(cross)+cross_error+nx*residual_error+(nr+residual_error)**2/eta+center_error
                result.append(dict(**metadata,ionic_energy=str(E),eta=str(eta),response_center=dict(real=str(F(float(center.real))),imaginary=str(F(float(center.imag)))),
                    radius_rational_upper=str(radius),radius_decimal=float(radius),
                    residual_norm_upper=str(nr),residual_formation_error_upper=str(residual_error),
                    observed_galerkin_defect_upper=str(abs_upper(cross)),cross_dot_roundoff_upper=str(cross_error),
                    center_dot_roundoff_upper=str(center_error),
                    response_real=float(center.real),response_imaginary=float(center.imag)))
        return result
