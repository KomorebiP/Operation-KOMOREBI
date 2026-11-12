"""Forward construction of a fixed exact member regression, without the decoder.
Author: Komorebi P. This is a known-family regression, not a discovery holdout.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def plus(p, q):
    return [(p[i] if i < len(p) else F(0))+(q[i] if i < len(q) else F(0)) for i in range(max(len(p),len(q)))]


def lift(P, Q, g, L):
    N = plus(P, [F(0)]+[L*x for x in Q])
    D = plus(Q, [g*x for x in N])
    return [x/D[-1] for x in N], [x/D[-1] for x in D]


def main():
    family = json.loads((ROOT/'family.json').read_bytes())
    a = list(map(F, family['target_box']['center']))
    r = list(map(F, family['target_box']['radii']))
    offsets = [[F(0)]*7, [F(1,2)]*7, [F(-1,2)]*7, [F((-1)**j,3) for j in range(7)]]
    for j in range(7):
        for sign in (-1,1):
            z = [F(0)]*7
            z[j] = F(sign)
            offsets.append(z)
    targets = []
    for index, offset in enumerate(offsets):
        y = [x+t*b for x,t,b in zip(a,offset,r)]
        P,Q = y[:4], y[4:]+[F(1)]
        depths = {0,1,3,5,9,13} if index < 4 else {0}
        for depth in range(max(depths)+1):
            if depth:
                P,Q = lift(P,Q,F(depth+2,depth+5),F(2*depth+3,depth+2))
            if depth in depths:
                targets.append({'id':f'core-{index:02d}-depth-{depth}', 'degree':3+depth,
                    'target':{'P':list(map(str,P)),'Q':list(map(str,Q))}, 'core_offset':list(map(str,offset))})
    record = {'schema':'komorebi-deterministic-family-regression-v2',
        'scope':'Fixed exact members of a known certified family; not an independent discovery holdout',
        'generator_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'family_sha256':hashlib.sha256((ROOT/'family.json').read_bytes()).hexdigest(), 'targets':targets}
    dest = ROOT/'frozen_targets.json'
    dest.write_text(json.dumps(record,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({'members':len(targets),'degrees':sorted({r['degree'] for r in targets}),
        'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()}))


if __name__ == '__main__':
    main()
