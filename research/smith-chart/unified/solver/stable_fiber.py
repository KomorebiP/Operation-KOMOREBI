"""Physical stable-factor cut of the coefficient fiber. Author: Komorebi P.

Universal graph accretivity and real factorization are written separately.
This producer checks the exact polynomial identities and quantitative repair.
"""
from fractions import Fraction as F
import json
from kernel import exact_polynomials as p
from coefficient_fiber import fiber,certificate as fiber_certificate


def delta3(coefficients):
    if len(coefficients)>5:raise ValueError('Degree at most four required')
    a=list(coefficients)+[F(0)]*(5-len(coefficients))
    return a[3]*a[2]*a[1]-a[4]*a[1]**2-a[3]**2*a[0]


def poly_delta3(a):
    return p.sub(p.sub(p.mul(p.mul(a[3],a[2]),a[1]),p.mul(a[4],p.square(a[1]))),p.mul(p.square(a[3]),a[0]))


def identities():
    a,b,c,d,e,f=map(p.var,('a','b','c','d','e','f'))
    # Ascending quadratic factors (c+b*s+a*s^2)*(f+e*s+d*s^2).
    product=[p.mul(c,f),p.add(p.mul(b,f),p.mul(c,e)),
      p.add(p.mul(a,f),p.mul(b,e),p.mul(c,d)),p.add(p.mul(a,e),p.mul(b,d)),p.mul(a,d)]
    expected=p.mul(p.mul(b,e),p.add(p.square(p.sub(p.mul(a,f),p.mul(c,d))),p.mul(product[3],product[1])))
    assert poly_delta3(product)==expected
    A,B,C=map(p.var,('A','B','C'))
    PH=[p.scale(A,4),p.add(p.scale(A,3),p.scale(B,4)),p.add(p.scale(A,6),p.scale(B,3),p.scale(C,4)),p.add(p.scale(B,6),p.scale(C,3)),p.scale(C,6)]
    G=p.add(p.square(p.sub(p.scale(A,6),p.scale(C,4))),p.mul(PH[3],PH[1]))
    assert poly_delta3(PH)==p.scale(p.mul(B,G),3)
    lower=p.sub(p.add(p.square(p.sub(p.scale(A,6),p.scale(C,4))),p.scale(p.mul(A,C),F(19,9))),p.scale(p.square(p.add(A,C)),F(1,2)))
    sos=p.add(p.scale(p.square(p.sub(A,p.scale(C,F(422,639)))),F(71,2)),p.scale(p.square(C),F(197,11502)))
    assert lower==sos
    U,K=map(p.var,('U','K'));t=p.add(p.const(F(1,30)),K)
    before=[p.mul(t,U),p.scale(K,-1),p.mul(t,p.sub(p.const(1),U))]
    after=[p.scale(U,F(1,30)),p.const(0),p.scale(p.sub(p.const(1),U),F(1,30))]
    weights=[p.scale(U,-4),p.sub(p.const(4),p.scale(U,3)),p.sub(p.const(-1),p.scale(U,2)),
             p.add(p.const(3),p.scale(U,3)),p.add(p.const(-6),p.scale(U,6)),p.scale(U,-9),
             p.sub(p.const(9),p.scale(U,2)),p.add(p.const(-7),p.scale(U,3)),
             p.add(p.const(4),p.scale(U,2)),p.add(p.const(-6),p.scale(U,6))]
    changes=[]
    for base in ((4,3,6),(9,2,6)):
        left=[{} for _ in range(5)];right=[{} for _ in range(5)]
        for i,a0 in enumerate(base):
            for j in range(3):
                left[i+j]=p.add(left[i+j],p.scale(before[j],a0))
                right[i+j]=p.add(right[i+j],p.scale(after[j],a0))
        changes.extend(p.sub(a0,b0) for a0,b0 in zip(right,left))
    assert changes==[p.mul(K,w) for w in weights]
    return {'quadratic_product_identity':p.dump(expected),'target_fiber_identity':p.dump(poly_delta3(PH)),
            'positive_lower_bound_identity':p.dump(sos),'repair_identity':[p.dump(v) for v in changes]}


def triangle_repair(m):
    a,b,c=map(F,m)
    if a<0 or c<0 or b<-2*a/9 or b<-c/3 or a+b+c!=F(1,30):
        raise ValueError('Exact nonnegative coefficient fiber required')
    if b>=0:return (a,b,c)
    total=a+c
    return (a/(30*total),F(0),c/(30*total))


def certificate():
    data=identities();old=fiber_certificate(4)
    for m in old['exact_nonnegative_fiber']['multiplier_vertices']:
        x=fiber(4,list(map(F,m)));assert max(x[:5])<=F(1,5)
    assert (1+9*F(675,2))<3039
    vertices=[(F(1,30),0,0),(0,F(1,30),0),(0,0,F(1,30))]
    for m in vertices:
        x=fiber(4,m);assert min(x)>=0 and sum(x)==1 and delta3(x[:5])>=0
    bad=(F(3,130),F(-1,195),F(1,65));x=fiber(4,bad)
    assert delta3(x[:5])<0 and delta3(x[5:])==0
    return {'status':'PASS','physical_limiting_multiplier':'a+b*s+c*s^2; a,b,c>=0; a+b+c=1/30',
      'stable_triangle_vertices':[list(map(str,m)) for m in vertices],
      'quadrilateral_negative_vertex_control':{'multiplier':list(map(str,bad)),
          'P_delta3':str(delta3(x[:5])),'Q_delta3':str(delta3(x[5:])),
          'meaning':'Nonnegative coefficients and passivity of the cancelled ratio do not give graph-polynomial stability; the numerator condition is essential to this cut.'},
      'quantitative_triangle_factor':3039,'small_eta_threshold':'1/20',
      'negative_b_G_lower':'1/1800','negative_b_error_factor':'675/2',
      'fiber_coordinate_bound':'1/5','delta3_lipschitz_on_quarter_box':'9/16',
      'multiplier_repair_coefficient_factor':9,
      'old_fiber_error_factor':old['coefficient_error_factor'],
      'old_fiber_interior_rho':old['interior_minimum_coefficient'],
      'distance_statement':'For a normalized physical degree<=4 graph pair with seven-sample error delta, epsilon=C4*delta and eta=epsilon/(rho+epsilon), distance to the stable target triangle is at most min(1,3039*eta).',
      'identities':data,
      'proof_scope':'Written physical accretivity and real quadratic factorization plus exact arithmetic; no all-topology margin, independent review, new Lean or priority claim.'}


def verify(record):
    if record!=certificate():raise ValueError('Stable-fiber certificate binding differs')
    return {'status':'PASS'}


if __name__=='__main__':
    if not __debug__:raise RuntimeError('Assertions must remain enabled')
    print(json.dumps(certificate(),indent=2))
