"""Author: Komorebi P. Uniform exact coefficient neighborhoods for q=3.

Every target in a seven-dimensional rational coefficient box receives an
exact positive realization in the same component box. The checker rebuilds
all joint polynomials and checks uniform contraction and coprimality. This
certifies a local family; it does not assert global coverage of degree three.
"""
from fractions import Fraction as F
from copy import deepcopy
import argparse
import json
from pathlib import Path

from exact_polynomials import rational
from interval_certificate import (build_coefficient_system, graph_polynomials,
    invert_matrix, differentiate, interval_evaluate_polynomial, reduce_target)

FORMAT='komorebi-rlc-coefficient-family-v1'


def add_scaled(out, poly, coefficient):
    for monomial,value in poly.items():
        new=out.get(monomial,F(0))+coefficient*value
        if new:out[monomial]=new
        else:out.pop(monomial,None)


def joint_system(branches):
    """F coefficients for P=sum(y_i*s^i), Q=s^3+sum(y_(4+i)*s^i)."""
    graph=graph_polynomials(branches)
    if graph['storage_count']!=3 or graph['variables']!=7:
        raise ValueError('Family certificate requires seven branches and three reactives')
    equations=[{} for _ in range(7)]
    for k,poly in enumerate(graph['numerator']):
        for monomial,c in poly.items():
            key=monomial+(0,)*7
            add_scaled(equations[k+3],{key:c},F(1))
            for j in range(3):
                yy=[0]*7;yy[4+j]=1
                add_scaled(equations[k+j],{monomial+tuple(yy):c},F(1))
    for k,poly in enumerate(graph['denominator']):
        for monomial,c in poly.items():
            for j in range(4):
                yy=[0]*7;yy[j]=1
                add_scaled(equations[k+j],{monomial+tuple(yy):c},F(-1))
    return graph,equations


def sylvester_matrix(coefficients):
    """Matrix of (U,V) -> U*P+V*Q for deg U,V <= 2, asc conventions."""
    P=list(coefficients[:4]);Q=list(coefficients[4:])+[F(1)]
    return [[(P[i-j] if 0<=i-j<=3 else F(0)) if j<3
             else (Q[i-(j-3)] if 0<=i-(j-3)<=3 else F(0))
             for j in range(6)] for i in range(6)]


def coprimality_box(center,radii):
    """Prove every Sylvester matrix in the box nonsingular by a norm bound."""
    M=sylvester_matrix(center);Y=invert_matrix(M)
    # Matrix dependence on y is linear. Bound |I-YM(y)| by summing each
    # target coordinate's exact derivative times its radius.
    zero=[F(0)]*7
    const=sylvester_matrix(zero)
    derivatives=[]
    for k in range(7):
        unit=zero.copy();unit[k]=F(1);A=sylvester_matrix(unit)
        derivatives.append([[A[i][j]-const[i][j] for j in range(6)] for i in range(6)])
    bound=[[sum((abs(sum((Y[i][a]*derivatives[k][a][j] for a in range(6)),F(0)))*radii[k]
                   for k in range(7)),F(0)) for j in range(6)] for i in range(6)]
    norm=max(sum(row,F(0)) for row in bound)
    if norm>=1:raise ValueError('Uniform Sylvester nonsingularity not certified')
    return norm


def verify_coefficient_family(cert):
    if not isinstance(cert,dict) or cert.get('format')!=FORMAT:
        raise ValueError('Unknown coefficient-family certificate format')
    target=cert['target_box']
    if target.get('coordinates')!='P0,P1,P2,P3,Q0,Q1,Q2;Q3=1':
        raise ValueError('Coefficient coordinate convention mismatch')
    def vector(value):
        if not isinstance(value,list) or len(value)!=7:raise ValueError('Seven exact entries required')
        return list(map(rational,value))
    a=vector(target['center']);rho=vector(target['radii'])
    c=vector(cert['center']);r=vector(cert['radii'])
    if any(z<=0 for z in r+rho):raise ValueError('All box radii must be positive')
    if any(x-y<=0 for x,y in zip(c,r)):raise ValueError('Component box is not positive')
    if a[3]-rho[3]<=0:raise ValueError('P3 must remain strictly positive')
    Y=cert['preconditioner']
    if not isinstance(Y,list) or len(Y)!=7 or any(not isinstance(row,list) or len(row)!=7 for row in Y):
        raise ValueError('A seven-by-seven preconditioner is required')
    Y=[list(map(rational,row)) for row in Y];invert_matrix(Y)
    graph,eq=joint_system(cert['branches'])
    combined=[]
    for row in Y:
        poly={}
        for scale,equation in zip(row,eq):add_scaled(poly,equation,scale)
        combined.append(poly)
    box=[(x-y,x+y) for x,y in zip(c,r)]+[(x-y,x+y) for x,y in zip(a,rho)]
    center_x_box=[(x,x) for x in c]+box[7:]
    corrections=[];bounds=[]
    for i,poly in enumerate(combined):
        lo,hi=interval_evaluate_polynomial(poly,center_x_box)
        corrections.append(max(abs(lo),abs(hi)))
        row=[]
        for j in range(7):
            dp={}
            if i==j:dp[(0,)*14]=F(1)
            add_scaled(dp,differentiate(poly,j),F(-1))
            lo,hi=interval_evaluate_polynomial(dp,box)
            row.append(max(abs(lo),abs(hi)))
        bounds.append(row)
    weighted=[sum((b*rr for b,rr in zip(row,r)),F(0))/r[i] for i,row in enumerate(bounds)]
    contraction=max(weighted)
    if contraction>=1:raise ValueError('Uniform component contraction failed')
    margins=[r[i]-corrections[i]-weighted[i]*r[i] for i in range(7)]
    if any(v<=0 for v in margins):raise ValueError('Uniform self-mapping failed')
    sylvester=coprimality_box(a,rho)
    return {'status':'PASS','family_dimension':7,'coefficient_domain':'all real coefficients in the closed target box',
            'quantifier':'For every target vector in target_box, exactly one root lies in the component box',
            'minimum_reactive_count':3,'storage_count':graph['storage_count'],
            'resistor_count':sum(row['type']=='g' for row in graph['branches']),
            'uniform_contraction_bound':str(contraction),'self_map_margins':list(map(str,margins)),
            'uniform_center_correction_bounds':list(map(str,corrections)),
            'sylvester_nonsingularity_bound':str(sylvester),
            'arithmetic':'standard-library integer and Fraction only',
            'scope':'explicit local family in one topology; no global synthesis claim'}


def build_family(root_certificate,component_exponents=(5,6,7),target_exponents=(10,12,14,16)):
    P,Q=reduce_target(root_certificate['target']['P'],root_certificate['target']['Q'])
    if len(P)!=4 or len(Q)!=4:raise ValueError('Degree-(3,3) central target required')
    a=P+Q[:3];c=list(map(F,root_certificate['center']))
    errors=[]
    for component_exp in component_exponents:
        for target_exp in target_exponents:
            cert={'format':FORMAT,'branches':deepcopy(root_certificate['branches']),
                  'center':list(map(str,c)),
                  'radii':[str(max(F(1),abs(x))/(10**component_exp)) for x in c],
                  'preconditioner':deepcopy(root_certificate['preconditioner']),
                  'target_box':{'coordinates':'P0,P1,P2,P3,Q0,Q1,Q2;Q3=1',
                                'center':list(map(str,a)),
                                'radii':[str(max(F(1),abs(x))/(10**target_exp)) for x in a]}}
            try:check=verify_coefficient_family(cert)
            except ValueError as exc:
                errors.append({'component_exponent':component_exp,'target_exponent':target_exp,'reason':str(exc)})
                continue
            return {'status':'CERTIFIED_LOCAL_FAMILY','certificate':cert,'verification':check,
                    'component_relative_scale_exponent':component_exp,'target_relative_scale_exponent':target_exp,
                    'prior_attempts':errors}
    return {'status':'UNKNOWN','attempts':errors}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('certificate',type=Path);p.add_argument('--build',action='store_true');p.add_argument('--output',type=Path)
    args=p.parse_args();data=json.loads(args.certificate.read_text())
    result=build_family(data) if args.build else verify_coefficient_family(data)
    content=json.dumps(result,indent=2)+'\n'
    if args.output:args.output.write_text(content)
    else:print(content)
