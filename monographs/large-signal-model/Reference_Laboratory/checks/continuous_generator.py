"""Declared exact generating example. Never imported by the standalone learner."""
from pathlib import Path
import json
import sympy as s
from continuous_reference import U,coeffs,encode,integral,moment,embedding
ROOT=Path(__file__).resolve().parents[1]
R=s.Rational
PENCIL=[s.eye(2)/2,s.diag(1,-1)/2,s.Matrix([[0,1],[1,0]])/2]
W=s.Matrix([[2,-1],[1,2]])
ROT=s.Matrix([[1,0,0],[0,R(3,5),-R(4,5)],[0,R(4,5),R(3,5)]])
K=s.diag((1+3*U)/2,(1-3*U)/2)
BASE=s.Matrix([[(1+9*U**2)/4,3*U/2,0],[3*U/2,(1+9*U**2)/4,0],[0,0,(1-9*U**2)/4]])
OPERATORS={'direct':BASE,'rotated':BASE*ROT}
MASS=s.Matrix([[1,0,0]]);INITIAL=s.Matrix([1,0,0])
TESTS=s.Matrix([[1,0,0],[R(1,2),R(3,8),0],[R(1,2),R(9,40),-R(3,10)]])
PLUS=integral(BASE,0,1)
HISTORIES=s.Matrix.hstack(INITIAL,PLUS*INITIAL,PLUS*ROT*PLUS*INITIAL)
MEASURE={'support':['-1','1'],'density_wrt_lebesgue':'1/2'}


def population_tables():
    return {'schema':'komorebi.population-moment-tables.v1','degree':2,
            'reference_measure':MEASURE,'mass':encode(MASS),
            'core':encode(TESTS*HISTORIES),'initial_tests':encode(TESTS*INITIAL),
            'shifted_moment_tables':{a:[encode(TESTS*integral(U**j*B)*HISTORIES) for j in range(3)] for a,B in OPERATORS.items()},
            'declarations':{'rank':3,'degree_is_a_model_class_assumption':True,
               'values':'Exact constructed population moments, not sampled data.',
               'tests':['empty','direct: [0,1]','rotated: [0,1]'],
               'histories':['empty','direct: [0,1]','direct: [0,1] then rotated: [0,1]']}}


def template():
    return {'schema':'komorebi.polynomial-psd-certificate.v1',
         'reference_measure':MEASURE,'embedding':[encode(P) for P in PENCIL],
         'mass':encode(MASS),'initial':encode(INITIAL),'interior':encode(INITIAL),
         'actions':{a:{'operator_coefficients':[encode(M) for M in coeffs(B,2)],
                      'positive_terms':[{'weight':'1' if a=='direct' else '1/5',
                                        'multiplier':'one',
                                        'coefficients':[encode(M) for M in coeffs(K if a=='direct' else K*W,1)]}]} for a,B in OPERATORS.items()},
         'provenance':{'purpose':'A declared fixed structural template, not an inferred universal domain.'}}


def main():
    (ROOT/'examples/continuous_population_tables.json').write_text(json.dumps(population_tables(),indent=2)+'\n')
    (ROOT/'examples/continuous_template.json').write_text(json.dumps(template(),indent=2)+'\n')
    print('Wrote the declared population tables and fixed template.')
if __name__=='__main__':main()
