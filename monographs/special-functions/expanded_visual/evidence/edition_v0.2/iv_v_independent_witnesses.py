"""Independent bounded IV--V examples; no author numerical implementation imported."""
from pathlib import Path
import json
import mpmath as mp
import sympy as sy

mp.mp.dps = 80
ROOT = Path(__file__).resolve().parents[1]


def decimal(z, digits=45):
    return mp.nstr(z, digits)


def moments(positive):
    vals = []
    for j in range(12):
        summands = []
        for r in range(j + 1):
            seed = (mp.zeta(4 + 2*r) / mp.zeta(8 + 4*r)
                    if positive else 1/mp.zeta(2 + 2*r))
            summands.append((-1)**r * mp.binomial(j, r) * seed)
        vals.append(mp.fsum(summands))
    return vals


def model(positive):
    data = moments(positive)
    # Solve q1..q4 against coefficient equations j=4..7.
    equations = mp.matrix([[data[j-k] for k in range(1, 5)] for j in range(4, 8)])
    q = [mp.mpf(1)] + list(mp.lu_solve(equations, mp.matrix([-data[j] for j in range(4, 8)])))
    roots = sorted(mp.polyroots(q, maxsteps=1000, extraprec=180), key=lambda x: mp.re(x))
    assert all(abs(mp.im(x)) < mp.mpf('1e-60') for x in roots)
    roots = [mp.re(x) for x in roots]
    vandermonde = mp.matrix([[x**j for x in roots] for j in range(4)])
    weights = list(mp.lu_solve(vandermonde, mp.matrix(data[:4])))
    reconstructed = [mp.fsum(w*x**j for w, x in zip(weights, roots)) for j in range(12)]
    contracted = max(abs(x-y) for x, y in zip(data[:8], reconstructed[:8]))
    later = max(abs(x-y) for x, y in zip(data[8:], reconstructed[8:]))
    determinant = mp.det(mp.matrix([[data[i+j] for j in range(4)] for i in range(4)]))
    separation = min(abs(x-y) for i,x in enumerate(roots) for y in roots[i+1:])
    assert abs(q[-1]) > mp.mpf('1e-12')
    assert separation > mp.mpf('.07')
    assert contracted < mp.mpf('1e-65')
    assert later > mp.mpf('1e-10')
    assert all(w > 0 for w in weights) if positive else any(w < 0 for w in weights)
    assert all(0 < x < 1 for x in roots) if positive else roots[0] < 0
    return {'hankel_determinant': decimal(determinant), 'q4': decimal(q[-1]),
            'effective_nodes': [decimal(x) for x in roots],
            'weights': [decimal(w) for w in weights],
            'minimum_node_separation': decimal(separation),
            'first_eight_max_residual': decimal(contracted),
            'later_four_max_difference': decimal(later)}


# Exact symbolic Fourier phase witnesses from the Gamma integral, degree 0..4.
# Laguerre coefficient integral u^j -> 2^j(s)_j, s=alpha/2-i*w.
alpha = sy.Rational(3, 2)
w = sy.symbols('w', real=True)
s = alpha/2 - sy.I*w
pollaczek = [sy.Integer(1), 2*w]
for n in range(1, 4):
    pollaczek.append(sy.expand((2*w*pollaczek[n] - (n+alpha-1)*pollaczek[n-1])/(n+1)))
phase_results = []
for n in range(5):
    transformed = sy.expand(sum((-1)**j * sy.binomial(n+alpha-1, n-j)
                               * 2**j * sy.rf(s, j)/sy.factorial(j)
                               for j in range(n+1)))
    residual = sy.simplify(transformed - sy.I**n * pollaczek[n])
    assert residual == 0
    phase_results.append({'degree': n, 'unnormalized_P': str(pollaczek[n]),
                          'exact_residual': str(residual)})

# C08's generic counterexample is exact and is separate from arithmetic data.
c = [sy.Integer(0), sy.Integer(1), sy.Integer(0), sy.Integer(0)]
H2 = sy.Matrix([[c[0], c[1]], [c[1], c[2]]])
eq2 = sy.Matrix([[c[1], c[0]], [c[2], c[1]]])
q2 = list(eq2.inv() * sy.Matrix([-c[2], -c[3]]))
assert H2.det() == -1 and q2 == [0, 0]

# Selected closed-form numerical values and analytic tail constants.
a = mp.mpf('1.5'); h = mp.mpf('1.4'); eta = mp.mpf('.8')
A = mp.gamma(a+1j*eta)/mp.gamma(a) / mp.cosh(h/2)**(a+1j*eta)
W = 2*mp.re(mp.besselk(4j, 1))/(mp.pi*mp.gamma(a))
assert W < 0
left_ambiguity_tail = mp.exp(a*(-30))/(a*mp.gamma(a))
left_fourier_tail = 2*mp.exp(a*(-30)/2)/(a*mp.sqrt(2*mp.pi*mp.gamma(a)))
results = {
    'scope': 'Independent finite numerical examples and exact symbolic degree-0..4 phase checks. No interval certificate or universal Padé nonbreakdown claim.',
    'coefficient_arithmetic': {'mpmath_working_decimal_digits': 80,
                             'symbolic_field': 'Q(i)[w], alpha=3/2'},
    'signed_pade_m4': model(False),
    'positive_pade_m4': model(True),
    'generic_C08_degree_drop': {'moments': [0,1,0,0], 'H2_determinant': -1,
                               'denominator_coefficients': [1,0,0], 'matching_rational_function': 'z'},
    'V_Fourier_phase_exact_checks': phase_results,
    'selected_closed_values': {
        'signed_c1_over_c0': decimal(moments(False)[1]/moments(False)[0]),
        'V02_A_real': decimal(mp.re(A)), 'V02_A_imaginary': decimal(mp.im(A)),
        'V07_W_y0_omega2': decimal(W),
        'V09_mean_y_alpha_1_5': decimal(mp.digamma(a)),
        'V09_variance_y_alpha_1_5': decimal(mp.polygamma(1,a)),
        'V09_uncertainty_product': decimal(mp.sqrt(a*mp.polygamma(1,a))/2),
        'V02_left_tail_bound': decimal(left_ambiguity_tail),
        'V05_left_tail_bound': decimal(left_fourier_tail),
        'IV11_normalized_EGF_tail_bound': decimal(mp.zeta(2)*mp.gammainc(41,0,8)/mp.gamma(41))
    },
    'status': 'PASS'
}
out = ROOT/'evidence'/'iv_v_independent_run'/'results.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(results, indent=2)+'\n')
print(json.dumps({'status': 'PASS', 'exact_phase_checks': 5, 'pade_models': 2}))
