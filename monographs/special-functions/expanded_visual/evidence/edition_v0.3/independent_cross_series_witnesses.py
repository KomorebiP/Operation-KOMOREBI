"""Independent finite witnesses for new VI, synthesis and q-recoupling lessons.

The q matrices are rebuilt on the full excitation space from the coproduct,
without importing any author figure script or finite recoupling module.
"""
from fractions import Fraction as F
from pathlib import Path
import json
import math
import numpy as np
from scipy.linalg import null_space
from scipy.special import gamma, polygamma

ROOT = Path(__file__).resolve().parents[1]


def rising(shape, degree):
    return math.prod((shape+j for j in range(degree)), start=F(1))


def allocation_weight(shapes, degrees):
    degree = sum(degrees)
    result = F(math.factorial(degree), math.prod(math.factorial(r) for r in degrees))
    return result * math.prod((rising(a,r) for a,r in zip(shapes,degrees)), start=F(1)) / rising(sum(shapes),degree)


def compositions(degree):
    return [(a,b,degree-a-b) for a in range(degree+1) for b in range(degree-a+1)]


def q_number(value, q):
    return value if q == 1 else math.sinh(-value*math.log(q)) / math.sinh(-math.log(q))


def lowering(degree, q, factors):
    source, target = compositions(degree), compositions(degree-1)
    indices = {value:index for index,value in enumerate(target)}
    result = np.zeros((len(target),len(source)))
    for column, state in enumerate(source):
        for factor in factors:
            if not state[factor]:
                continue
            changed = list(state)
            changed[factor] -= 1
            exponent = (sum(state[j]+.5 for j in factors if j > factor)
                        - sum(state[j]+.5 for j in factors if j < factor))
            # For kappa=1/2, sqrt([n]_q[2*kappa+n-1]_q)=[n]_q.
            result[indices[tuple(changed)],column] = q_number(state[factor],q) * q**exponent
    return result


def q_overlap(degree, q):
    full_lower = lowering(degree,q,(0,1,2))
    frame = null_space(full_lower)
    assert frame.shape[1] == degree+1
    eigenvectors = []
    spectrum_errors = []
    for pair in ((0,1),(1,2)):
        diagonal = [q_number(sum(state[j]+.5 for j in pair),q)
                    * q_number(sum(state[j]+.5 for j in pair)-1,q)
                    for state in compositions(degree)]
        pair_lower = lowering(degree,q,pair)
        casimir = np.diag(diagonal) - pair_lower.T @ pair_lower
        spectrum, vectors = np.linalg.eigh(frame.T @ casimir @ frame)
        expected = np.array([q_number(1+j,q)*q_number(j,q) for j in range(degree+1)])
        spectrum_errors.append(float(np.max(np.abs(spectrum-expected))/max(1,float(np.max(np.abs(expected))))))
        eigenvectors.append(vectors)
    overlap = eigenvectors[0].T @ eigenvectors[1]
    return overlap, {'lowering_relative_residual':float(np.linalg.norm(full_lower@frame)/max(1,np.linalg.norm(full_lower))),
                     'orthogonality_residual':float(np.max(np.abs(overlap.T@overlap-np.eye(degree+1)))),
                     'pair_spectrum_max_relative_error':max(spectrum_errors)}


def main():
    result = {}
    z = F(1,3)
    direct = sum(F(n+1)*z**n for n in range(6))
    interleaved = sum(z**r*sum(F(2*m+r+1)*(z*z)**m for m in range(3)) for r in range(2))
    assert direct == interleaved == F(181,81)
    result['synthesis_reconstruction'] = {'exact':True,'coefficient_count':6,'z':'1/3','value':'181/81'}

    synthesis_weights = [allocation_weight((F(1),F(2),F(3)),r) for r in compositions(3)]
    assert sum(synthesis_weights)==1 and allocation_weight((F(1),F(2),F(3)),(1,1,1))==F(3,28)
    vi_weights = [allocation_weight((F(2),F(3)),(r,4-r)) for r in range(5)]
    assert vi_weights == [F(value,70) for value in (15,20,18,12,5)]
    vi_many = [allocation_weight((F(2),F(3),F(1)),r) for r in compositions(4)]
    assert len(vi_many)==15 and sum(vi_many)==1
    assert allocation_weight((F(2),F(3),F(1)),(1,2,1))==F(2,21)
    result['shape_refinement_examples'] = {'exact':True,'synthesis_degree_3_compositions':10,
        'synthesis_example':'3/28','VI_binary_weights':list(map(str,vi_weights)),
        'VI_degree_4_compositions':15,'VI_multinomial_example':'2/21','both_total_energies':'1'}

    # The Beta(2,2) CDF is an elementary polynomial.
    beta_cdf = lambda v: 3*v*v-2*v*v*v
    assert beta_cdf(F(3,4))-beta_cdf(F(1,4))==F(11,16)
    sigma61_squared = F(24,63*64*65)
    result['VI_exact_strip_and_spectral_tail'] = {'frame_strip_energy':'11/16',
        'initial_shape':2,'increment':3,'retained_degrees':[0,60],
        'next_singular_value_squared':str(sigma61_squared),'next_singular_value':math.sqrt(float(sigma61_squared))}

    convolution_bound = 4/math.pi*math.atan(math.exp(-8*math.pi))
    levy_bound = 4*math.exp(-10*math.pi)/(10*math.pi*(1-math.exp(-20*math.pi)))
    assert convolution_bound < 1.55e-11 and levy_bound < 2.90e-15
    result['VI_tail_bound_constants'] = {'convolution_bound':convolution_bound,'levy_bound':levy_bound,
        'derivations':['rho_1(x)=sech(pi*x)<=1, so omitted convolution <= omitted rho_1 mass = 4/pi*atan(exp(-8*pi)).',
                       'For x>=10, |cos(xi*x)-1|<=2 and 1/sinh(pi*x)<=2*exp(-pi*x)/(1-exp(-20*pi)); integrate with 1/x<=1/10.'],
        'Chernoff_derivation':'For |t|<pi, E exp(t X_s)=sec(t/2)^s. Applying each side with t=pi/2 gives P(|X_s|>L)<=min(1,2*2^(s/2)*exp(-pi*L/2)).'}

    affinity = gamma(2.1)/math.sqrt(gamma(2)*gamma(2.2))
    maximum = math.sqrt(2/3)*math.exp(math.log(2)/2)/math.cosh(math.log(2)/2)**3
    assert abs(affinity-.996969)<5e-7 and abs(maximum-.967700)<5e-7
    result['VI_caption_values'] = {'affinity_F_2_2p2':float(affinity),'cross_shape_peak_2_4':maximum,
        'cross_ambiguity_squared_at_h0_eta1':5*math.pi/(3*math.sinh(math.pi)),
        'rho2_at_1':2/math.sinh(math.pi),'variance_Z_shape32':float(32*polygamma(1,32))}

    benchmark, benchmark_audit = q_overlap(1,.5)
    expected_probability = np.array([[.16,.84],[.84,.16]])
    assert np.max(np.abs(benchmark**2-expected_probability)) < 1e-12
    grid = np.linspace(.2,1,41)
    entropies, audits = [], []
    for q in grid:
        overlap,audit = q_overlap(3,float(q))
        probability = overlap[1]**2
        entropies.append(-sum(value*math.log(value) for value in probability if value>0))
        audits.append(audit)
    increments = np.diff(entropies)
    index = int(np.argmin(increments))
    assert increments[index] < -.01
    assert max(item['orthogonality_residual'] for item in audits) < 1e-12
    assert max(item['lowering_relative_residual'] for item in audits) < 1e-12
    assert max(item['pair_spectrum_max_relative_error'] for item in audits) < 1e-10
    result['independent_q_negative_control'] = {
        'construction':'full weak-composition excitation basis, coproduct lowering, SVD nullspace and pair-Casimir eigenspaces; no author-module import',
        'arithmetic':'IEEE-754 double precision using NumPy/SciPy','kappas':['1/2']*3,
        'benchmark':{'N':1,'q':.5,'squared_overlap':(benchmark**2).tolist(),'audit':benchmark_audit},
        'N':3,'row_index':1,'q_grid':grid.tolist(),'row_entropies':entropies,
        'negative_increment':{'q_left':float(grid[index]),'q_right':float(grid[index+1]),
            'H_left':entropies[index],'H_right':entropies[index+1],'change':float(increments[index])},
        'max_orthogonality_residual':max(item['orthogonality_residual'] for item in audits),
        'max_lowering_relative_residual':max(item['lowering_relative_residual'] for item in audits),
        'max_pair_spectrum_relative_error':max(item['pair_spectrum_max_relative_error'] for item in audits),
        'scope':'A bounded numerical negative control refutes universal q-monotonicity for this family; fixed-kernel entropy nondecrease is a different theorem.'}
    result['all_passed']=True
    path=ROOT/'evidence'/'independent_cross_series_run'/'results.json'
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'independent_cross_series_witnesses':'passed','negative_q_entropy_increment':float(increments[index])}))


if __name__=='__main__':
    main()
