"""Conservative binary64 normwise residual certificates for cached real actions.

Assumes correctly rounded binary64 elementary operations/dot products. Guards
exclude overflow and underflow in the stated operations. No orthogonality or
exact projected solve is assumed in the final response-error identity.
"""
from fractions import Fraction as F
import numpy as np
from full_model import sqrt_upper

UNIT=F(1,2**53)
def gamma(k):
    if k*UNIT>=1:raise ValueError('Invalid rounding count')
    return k*UNIT/(1-k*UNIT)
def exponent_bound(values):
    return max((F(float(x)).denominator.bit_length()-1 for x in np.asarray(values).ravel()),default=0)
def norm_upper(values,exponent):
    values=np.asarray(values)
    if 2*exponent>=1000:raise ValueError('Cannot exclude squared-norm underflow')
    if not np.isfinite(values).all() or np.max(np.abs(values),initial=0)>2**100:raise ValueError('Norm range exceeded')
    real=np.asarray(values.real,dtype=float);imag=np.asarray(values.imag,dtype=float)
    observed=float(np.sum(real*real)+np.sum(imag*imag))
    upper2=F(observed)/(1-gamma(2*values.size+2))
    return sqrt_upper(upper2),upper2
def abs_upper(z):return sqrt_upper(F(float(z.real))**2+F(float(z.imag))**2)


def prepare_basis(model,Q,Y,source):
    Q=np.asarray(Q,dtype=float);Y=np.asarray(Y,dtype=float);source=np.asarray(source,dtype=float)
    if Q.shape!=Y.shape or len(source)!=Q.shape[0]:raise ValueError('Basis/image dimensions differ')
    qe=exponent_bound(Q);ye=exponent_bound(Y);be=exponent_bound(source)
    if qe+model.coefficient_denominator_exponent+1>=1000:raise ValueError('Action range guard failed')
    qnorms=[];q2=[];y2=[];errors=[]
    for j in range(Q.shape[1]):
        q,n2=norm_upper(Q[:,j],qe);qnorms.append(q);q2.append(n2)
        _,n2=norm_upper(Y[:,j],ye);y2.append(n2)
        errors.append(model.action_error_per_norm*q)
    b,b2=norm_upper(source,be)
    return dict(q_exponent=qe,y_exponent=ye,b_exponent=be,q_norms=qnorms,
        q_frobenius_upper=sqrt_upper(sum(q2)),y_frobenius_upper=sqrt_upper(sum(y2)),
        image_errors=errors,b_norm_upper=b,b_norm_squared_upper=b2)


def certify_grid(model,Q,Y,source,energies,etas,metadata,chunk=8):
    """Reuse the same Q and HQ cache at every energy, with zero new H actions."""
    k=Q.shape[1];N=Q.shape[0];G=Q.T@Q;K=Q.T@Y;K=(K+K.T)/2;rhs=Q.T@source
    prepared=prepare_basis(model,Q,Y,source);result=[]
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
