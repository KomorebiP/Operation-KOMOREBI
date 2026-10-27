"""Seeded rational five-node Markov analogue, not real-sensor measurements.

Sampling probabilities are exact fractions. randrange implements integer sampling;
the saved pseudo-random realization is an illustration, not a coverage experiment.
The learner receives only node indices and the declared observation measure.
"""
from pathlib import Path
import random,json,sys,math
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'checks'))
from data_certificate_reference import NODES,MEASURE,probability_row

def main():
    a,b=F(2,5),F(1,5);seed=20261009;steps=262144
    r=random.Random(seed);samplers=[]
    for s in NODES:
        ps=probability_row(s,a,b);d=math.lcm(*(x.denominator for x in ps));acc=0;cs=[]
        for p in ps:acc+=int(p*d);cs.append(acc)
        samplers.append((d,cs))
    path=[2]
    for _ in range(steps):
        d,cs=samplers[path[-1]];v=r.randrange(d);path.append(next(i for i,c in enumerate(cs) if v<c))
    (ROOT/'examples/dependent_observations.json').write_text(json.dumps({'reference_measure':MEASURE,'node_indices':path},separators=(',',':'))+'\n')
    (ROOT/'verification/dependent_generator.json').write_text(json.dumps({'seed':seed,'steps':steps,'parameter_a':str(a),'parameter_b':str(b),
       'sampling':'integer draws with exact rational transition probabilities','empirical_data':False,
       'continuous_measure_sample':False,'reference_measure':MEASURE},indent=2)+'\n')
    print(f'Generated {steps} dependent transitions; exact five-node reference measure.')
if __name__=='__main__':main()
