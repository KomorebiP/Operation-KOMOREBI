"""Exact, bounded checks of proposed posterior identities. Not a Lean certificate."""
from pathlib import Path
import hashlib, json, random, sys, time
import sympy as s

ROOT = Path(__file__).resolve().parents[1]
SEED = 20260911
rng = random.Random(SEED)

def mat(n, m):
    return s.Matrix(n, m, lambda _i, _j: s.Rational(rng.randint(-3, 3), rng.randint(1, 3)))

def model(n, q, rank):
    L, B = mat(n, rank), mat(q, q)
    P, R, H = L*L.T, B*B.T+s.eye(q), mat(q, n)
    return P, H, R

def update(P, H, R):
    S = H*P*H.T+R
    K = P*H.T*S.inv()
    G = s.eye(P.rows)-K*H
    C = P-K*H*P
    return S, K, G, C

def zero(A):
    return all(x == 0 for x in A)

start = time.perf_counter()
rows=[]
for n,q in [(1,1),(2,1),(2,2),(2,3),(3,2),(3,3)]:
    for rep in range(3):
        rank = rep % (n+1)
        P,H,R = model(n,q,rank)
        P0,H0,R0 = model(n,q,min(n,rank+1))
        S,K,G,C = update(P,H,R)
        S0,K0,G0,C0 = update(P0,H0,R0)
        dP,dH,dR = P-P0,H-H0,R-R0
        mixed = G*dP*G0.T+K*dR*K0.T-C*dH.T*K0.T-K*dH*C0
        assert zero(C-C0-mixed), ('mixed',n,q,rep)
        # Same H and R: the prior discrepancy factorizes into two closed-loop maps.
        _,K1,G1,C1 = update(P0,H,R)
        assert zero(C-C1-G*(P-P0)*G1.T), ('fixed',n,q,rep)
        Kh = mat(n,q)
        F = P*H.T-Kh*S
        J = (s.eye(n)-Kh*H)*P*(s.eye(n)-Kh*H).T+Kh*R*Kh.T
        assert zero(K-Kh-F*S.inv()), ('gainresidual',n,q,rep)
        assert zero(J-C-F*S.inv()*F.T), ('joseph_excess',n,q,rep)
        # Noise contribution to a shared-noise posterior coupling, without square roots.
        D = K-Kh
        assert zero(D*H*P*H.T*D.T+D*R*D.T-F*S.inv()*F.T)
        rows.append({'n':n,'observation_dim':q,'replicate':rep,'prior_factor_rank_bound':rank,
                     'four_term_identity':True,'fixed_observation_identity':True,
                     'inexact_gain_identity':True,'joseph_excess_identity':True,
                     'shared_noise_cost_covariance_identity':True})

P=s.ones(2); P0=s.eye(2); H=R=s.eye(2)
_,K,G,C=update(P,H,R)
_,K0,G0,C0=update(P0,H,R)
E=C-C0
opnorm=lambda A: max(abs(v) for v in A.eigenvals())
refined_bound=opnorm(G)*opnorm(P-P0)*opnorm(G0)
assert refined_bound == s.Rational(1,2) == opnorm(E)

# Residual-certified inexact gain: scalar example.
P=H=R=s.ones(1); S,K,G,C=update(P,H,R); Kh=s.zeros(1)
F=P*H.T-Kh*S; v=s.Matrix([2]); J=s.ones(1)
cost=(F*S.inv()*v).dot(F*S.inv()*v)+s.trace(F*S.inv()*F.T)
assert cost == s.Rational(3,2)
# Exact 1-D W2 formula, independently derived via Cauchy--Schwarz optimality.
w2sq=1+(1-s.sqrt(s.Rational(1,2)))**2
assert s.simplify(cost-w2sq) == -1+s.sqrt(2)

# A factor-gauge false positive: identical standard normal laws, opposite factors.
gauge_cost=(s.Matrix([[1]])-s.Matrix([[-1]])).norm()**2
assert gauge_cost == 4

# Mere parameter closeness is not posterior-error monotonicity at observation y=0.
def scalar_variance(h): return 1/(1+h*h)
assert abs(s.Rational(-1)-1)>abs(s.Rational(1,2)-1)
assert scalar_variance(s.Rational(-1))==s.Rational(1,2)
assert scalar_variance(s.Rational(1,2))==s.Rational(4,5)

script=Path(__file__)
result={'status':'PASS','classification':'bounded exact algebraic checks; not universal Lean verification',
        'seed':SEED,'arithmetic':'SymPy exact rationals','sympy_version':s.__version__,
        'python_version':sys.version.split()[0],'matrix_cases':len(rows),'cases':rows,
        'regression':{'actual_operator_error':str(opnorm(E)), 'archived_general_budget':'6',
                      'new_fixed_H_R_bound':str(refined_bound),'improvement_factor':'12'},
        'inexact_gain_scalar':{'coupling_cost':str(cost),'exact_W2_squared':str(w2sq)},
        'factor_gauge':{'identical_laws':True,'raw_coupling_cost':str(gauge_cost),'actual_W2_squared':'0'},
        'parameter_closeness_example':{'true_h':'1','first_h':'-1','second_h':'1/2',
            'true_posterior_variance':'1/2','first_variance':'1/2','second_variance':'4/5'},
        'runtime_seconds':time.perf_counter()-start,
        'script_sha256':hashlib.sha256(script.read_bytes()).hexdigest(),
        'scope_limits':['18 constructed small-matrix cases, not exhaustive.',
                        'Coupling probability laws and W2 bound have not been run in Lean.',
                        'No literature novelty or general sharpness established.']}
(ROOT/'EXACT_CHECK_RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
