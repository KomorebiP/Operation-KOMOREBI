#!/usr/bin/env python3
"""Independent exhaustive S3 checks of gauge groupoids and relative extension.

Exact arithmetic: permutations of {0,1,2}, composed right to left.
No floating point, random sampling, external services, or numerical tolerance.
These finite checks do not replace the universal Lean proofs.
"""
from __future__ import annotations
import argparse, datetime as dt, hashlib, itertools, json, time
from collections import Counter
from pathlib import Path

Perm = tuple[int, int, int]
H: tuple[Perm, ...] = tuple(itertools.permutations(range(3)))
ONE: Perm = (0,1,2)
SWAP: Perm = (1,0,2)
CYCLE: Perm = (1,2,0)
MUL = {(a,b): tuple(a[b[i]] for i in range(3)) for a in H for b in H}
INV = {a: next(b for b in H if MUL[a,b] == ONE) for a in H}

def mul(a: Perm,b: Perm) -> Perm: return MUL[a,b]
def conj(a: Perm,b: Perm) -> Perm: return mul(mul(a,b),INV[a])
def sign(a: Perm) -> int: return sum(a[i]>a[j] for i in range(3) for j in range(i+1,3))%2

EDGES = ((0,0),(1,1),(2,2),(0,1),(1,2),(0,2))
TRIPLES = tuple((i,j,k) for i in range(3) for j in range(i,3) for k in range(j,3))
FAMILIES = tuple(itertools.product(H,repeat=3))
MASKS = tuple(tuple(i for i in range(3) if m & (1<<i)) for m in range(8))
ENDOS = {
    'identity': {a:a for a in H},
    'trivial': {a:ONE for a in H},
    'conjugation': {a:conj(SWAP,a) for a in H},
    'sign_embedding': {a:SWAP if sign(a) else ONE for a in H},
}

class Audit:
    def __init__(self) -> None:
        self.assertions=0;self.cases=Counter();self.controls=[]
    def check(self, condition: bool, label: str) -> None:
        self.assertions+=1
        if not condition: raise AssertionError(label)
    def reject(self, label: str, false_claim: bool) -> None:
        if false_claim: raise AssertionError('Mutation survived: '+label)
        self.controls.append({'claim':label,'rejected':True})

def run() -> dict:
    a=Audit()
    for table in ENDOS.values():
        for x,y in itertools.product(H,repeat=2):
            a.check(table[mul(x,y)]==mul(table[x],table[y]),'input map is a homomorphism')
    involutions=tuple(p for p in H if mul(p,p)==ONE)
    orbit_reps={min(conj(g,p) for g in H) for p in involutions}
    a.check(len(involutions)==4 and len(orbit_reps)==2,'all C2 to S3 cocycles and their two orbits')
    stabilizers={p:tuple(g for g in H if conj(g,p)==p) for p in involutions}
    for p in involutions:
        a.cases['loop_cocycles']+=1
        a.check((min(conj(g,p) for g in H)==ONE)==(p==ONE),'neutral iff identity involution')
        a.check(len(stabilizers[p])==(6 if p==ONE else 2),'stabilizer cardinality')
        for g,h,k in itertools.product(H,repeat=3):
            a.cases['composable_gauge_triples']+=1
            a.check(conj(h,conj(g,p))==conj(mul(h,g),p),'gauge action order')
            a.check(conj(INV[g],conj(g,p))==p,'gauge inverse')
            a.check(mul(k,mul(h,g))==mul(mul(k,h),g),'groupoid associativity')
        for q in involutions:
            arrows=tuple(g for g in H if conj(g,p)==q)
            if arrows:
                base=arrows[0]
                a.check(set(arrows)=={mul(base,h) for h in stabilizers[p]},'all arrows from source stabilizer')
    for name01,name12 in itertools.product(ENDOS,repeat=2):
        a.cases['coefficient_systems']+=1
        p01,p12=ENDOS[name01],ENDOS[name12]
        pull={(0,0):ENDOS['identity'],(1,1):ENDOS['identity'],(2,2):ENDOS['identity'],
              (0,1):p01,(1,2):p12,(0,2):{x:p01[p12[x]] for x in H}}
        def gauge(g,c):
            return {e:mul(mul(g[e[0]],c[e]),INV[pull[e][g[e[1]]]]) for e in EDGES}
        def coherent(x,c):
            return all(mul(c[i,j],pull[i,j][x[j]])==x[i] for i,j in EDGES)
        def labels(p,q):
            return {(0,0):ONE,(1,1):ONE,(2,2):ONE,(0,1):p,(1,2):q,(0,2):mul(p,p01[q])}
        trivial={e:ONE for e in EDGES}
        inv_groups={U:tuple(g for g in FAMILIES if coherent(g,trivial) and all(g[i]==ONE for i in U)) for U in MASKS}
        based={U:tuple(g for g in FAMILIES if all(g[i]==ONE for i in U)) for U in MASKS}
        for p,q in itertools.product(H,repeat=2):
            a.cases['chain_cocycles']+=1
            c=labels(p,q)
            a.check(all(c[i,k]==mul(c[i,j],pull[i,j][c[j,k]]) for i,j,k in TRIPLES),'all composable cocycle equations')
            globals_=tuple(x for x in FAMILIES if coherent(x,c))
            a.check(len(globals_)==6,'global trivializations parametrized by terminal view')
            for U in MASKS:
                for values in itertools.product(H,repeat=len(U)):
                    data=dict(zip(U,values))
                    if not all(mul(c[i,j],pull[i,j][data[j]])==data[i] for i,j in EDGES if i in data and j in data):continue
                    a.cases['coherent_partial_seeds']+=1
                    raw=tuple(data.get(i,ONE) for i in range(3))
                    normalized=gauge(tuple(INV[x] for x in raw),c)
                    extensions=tuple(x for x in globals_ if all(x[i]==data[i] for i in U))
                    neutral=any(gauge(b,normalized)==trivial for b in based[U])
                    a.check(neutral==bool(extensions),'relative orbit neutrality iff extension')
                    a.check(all(normalized[i,j]==ONE for i,j in EDGES if i in data and j in data),'internal labels normalized')
                    alternative=tuple(data.get(i,CYCLE) for i in range(3))
                    transition=tuple(mul(INV[alternative[i]],raw[i]) for i in range(3))
                    a.check(all(transition[i]==ONE for i in U),'raw extension change is based')
                    a.check(gauge(transition,normalized)==gauge(tuple(INV[x] for x in alternative),c),'normalization independence')
                    if extensions:
                        base=extensions[0]
                        synthesized={tuple(mul(base[i],h[i]) for i in range(3)) for h in inv_groups[U]}
                        a.check(synthesized==set(extensions),'extension fiber all parameters')
                        a.check(len(extensions)==len(inv_groups[U]),'free transitive extension action')
                        for x in extensions:
                            delta=tuple(mul(INV[base[i]],x[i]) for i in range(3))
                            a.check(delta in inv_groups[U],'nonabelian difference is coherent and invisible')
                    a.check((len(extensions)==1)==(neutral and len(inv_groups[U])==1),'unique extension criterion')
    a.reject('nonempty identical local fibers force one cocycle class',len(orbit_reps)==1)
    a.reject('one cocycle has only the identity automorphism',len(stabilizers[ONE])==1)
    a.reject('replace inverse in gauge action by the element itself',mul(CYCLE,CYCLE)==ONE)
    a.reject('gauge composition can be reversed',mul(SWAP,CYCLE)==mul(CYCLE,SWAP))
    return {'status':'PASS','cases':dict(a.cases),'assertions':a.assertions,'negative_controls':a.controls,
            'loop_involutions':len(involutions),'loop_isomorphism_classes':len(orbit_reps),
            'loop_stabilizer_cardinalities':sorted(map(len,stabilizers.values())),
            'arithmetic':'exact permutation tables for S3',
            'bounds':{'group':'all permutations of Fin 3','loop_views':'one object with C2 arrows',
                      'chain_views':3,'coefficient_systems':'all 16 pairs of four listed endomorphisms',
                      'cocycles':'all 36 generator-label pairs per chain system','domains':'all 8 subsets',
                      'partial_seeds':'all internally coherent assignments','gauges':'all based families'},
            'non_claims':['Finite checks do not prove the universally quantified Lean theorems.',
                          'No site descent, stackification, arithmetic correspondence or algorithmic complexity theorem.']}

def main() -> None:
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    started=dt.datetime.now(dt.timezone.utc).isoformat();t=time.monotonic();r=run()
    r.update(started_at_utc=started,runtime_seconds=time.monotonic()-t,script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))
if __name__=='__main__':main()
