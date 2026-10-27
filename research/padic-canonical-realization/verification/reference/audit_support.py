#!/usr/bin/env python3
"""Finite exact tests for support closure; not an executable-refinement proof."""
from __future__ import annotations
import argparse, itertools, json, math, platform, random, time
from collections import Counter, deque
from pathlib import Path
from audit_profiles import Machine, PrunedMachine, DegreePrunedMachine, ProfiledMachine, recurrence_coefficients, digit_word
SEED = 280920

def matvec(m: list[list[int]], x: list[int], modulus: int) -> list[int]:
    return [sum(a*b for a,b in zip(row,x)) % modulus for row in m]

def adjacency(matrices: list[list[list[int]]], n: int) -> list[set[int]]:
    return [{j for j in range(n) if any(m[j][i] for m in matrices)} for i in range(n)]

def least_support(initial: list[int], matrices: list[list[list[int]]]) -> tuple[set[int], list[set[int]]]:
    n=len(initial); edges=adjacency(matrices,n); seed={i for i,x in enumerate(initial) if x}
    current=set(); history=[set()]
    for _ in range(n):
        current=current | seed | set().union(*(edges[i] for i in current)) if current else seed.copy()
        history.append(current.copy())
    return current, history

def support_bfs(initial: list[int], matrices: list[list[list[int]]]) -> set[int]:
    seen={i for i,x in enumerate(initial) if x}; queue=deque(sorted(seen)); n=len(initial)
    while queue:
        i=queue.popleft()
        for j in range(n):
            if j not in seen and any(m[j][i] for m in matrices): seen.add(j); queue.append(j)
    return seen

def invariant(seed:set[int], edges:list[set[int]], candidate:set[int]) -> bool:
    return seed <= candidate and all(edges[i] <= candidate for i in candidate)

class SupportMachine:
    """Direct sparse matrix restriction, independently compared with routed polynomials."""
    def __init__(self, profile: ProfiledMachine):
        self.profile=profile; self.p=profile.p; self.modulus=profile.m
        self.positions=[(i,j) for i,w in enumerate(profile.widths) for j in range(w)]
        self.lookup={pos:k for k,pos in enumerate(self.positions)}; n=len(self.positions)
        self.matrices=[]
        for digit in range(self.p):
            matrix=[[0]*n for _ in range(n)]
            for col,(source,exponent) in enumerate(self.positions):
                # Sum *all* branches into one matrix entry before testing its support.
                for destination,kernel in profile.old.full.kernels[source]:
                    if not any(kernel): continue
                    assert 1 <= destination <= profile.L
                    for degree in range(profile.widths[destination-1]):
                        index=self.p*degree+digit-exponent
                        if 0 <= index < len(kernel):
                            row=self.lookup[destination-1,degree]
                            matrix[row][col]=(matrix[row][col]+kernel[index]) % self.modulus
            self.matrices.append(matrix)
        self.initial_full=self.flatten(profile.initial())
        support,self.history=least_support(self.initial_full,self.matrices)
        self.support=sorted(support)
        self.restricted=[[[m[j][i] for i in self.support] for j in self.support] for m in self.matrices]
    def flatten(self,rows):return [rows[i][j] for i,j in self.positions]
    def rows(self,x):
        out=[[0]*w for w in self.profile.widths]
        for value,(i,j) in zip(x,self.positions):out[i][j]=value
        return out
    def embed(self,x):
        out=[0]*len(self.positions)
        for k,i in enumerate(self.support):out[i]=x[k]
        return out
    def initial(self):return [self.initial_full[i] for i in self.support]
    def step(self,x,d):return matvec(self.restricted[d],x,self.modulus)
    def output(self,x):return self.profile.output(self.rows(self.embed(x)))
    def coefficient(self,n):
        x=self.initial()
        for d in digit_word(self.p,n):x=self.step(x,d)
        return self.output(x)

def audit():
    start=time.monotonic(); rng=random.Random(SEED); counts=Counter(); generic=0
    def check(ok,kind,detail=None):
        counts[kind]+=1
        if not ok:raise AssertionError((kind,detail))
    for n in range(6):
      for modulus in (2,4,5,9):
       for alphabet in (0,1,2):
        for _ in range(3):
          initial=[rng.randrange(modulus) for i in range(n)]
          matrices=[[[rng.choice([0,0,rng.randrange(modulus)]) for i in range(n)] for j in range(n)] for d in range(alphabet)]
          S,hist=least_support(initial,matrices); seed={i for i,x in enumerate(initial) if x}; edges=adjacency(matrices,n)
          check(invariant(seed,edges,S),'generic_fixed_point')
          check(S==support_bfs(initial,matrices),'generic_independent_bfs')
          for a,b in zip(hist,hist[1:]):check(a<=b,'generic_inflation')
          for bits in itertools.product((False,True),repeat=n):
              T={i for i,b in enumerate(bits) if b}
              if invariant(seed,edges,T):check(S<=T,'exhaustive_coordinate_minimality')
          order=sorted(S);x=[rng.randrange(modulus) for i in order];padded=[0]*n
          for i,v in zip(order,x):padded[i]=v
          for matrix in matrices:
              full=matvec(matrix,padded,modulus);small=matvec([[matrix[j][i] for i in order] for j in order],x,modulus)
              lift=[0]*n
              for i,v in zip(order,small):lift[i]=v
              check(lift==full,'generic_restricted_transition')
          generic+=1
    cases=[]
    for p in (2,3,5):
      for r in range(1,5):
        masks=[([1],[1,-1]),([1],[1,p*p]),([1],[1,p**4]),([1,1],[1]),
               ([1],[1,0,-1]),([1,0,1],[1,1]),([1,1],[1,1]),([1+p**r,1],[1,p*p])]
        for _ in range(2):
          c=rng.choice([x for x in (-2,-1,1,2,3) if x%p])
          masks.append(([c,rng.randrange(-2,3),rng.randrange(-2,3)],[c,rng.randrange(-2,3),rng.randrange(-2,3)]))
        cases.extend((p,r,a,b) for a,b in masks)
    cases.extend([(2,8,[1],[1,-1]),(2,8,[1],[1,16]),(3,6,[1],[1,81]),(2,4,[1],[1,4])])
    examples=[];strict=0
    for p,r,a,b in cases:
      original=Machine(p,r,a,b);degree=DegreePrunedMachine(PrunedMachine(original));profile=ProfiledMachine(degree);machine=SupportMachine(profile)
      S=set(machine.support);N=len(machine.positions);edges=adjacency(machine.matrices,N);seed={i for i,v in enumerate(machine.initial_full) if v}
      check(invariant(seed,edges,S),'mask_closed')
      check(S==support_bfs(machine.initial_full,machine.matrices),'mask_bfs')
      check(len(S)<=sum(profile.widths),'mask_slot_bound'); strict+=len(S)<N
      check(machine.embed(machine.initial())==machine.initial_full,'mask_initial_embedding')
      for column in range(N):
        basis=[0]*N;basis[column]=1
        for digit in range(p):
          oracle=machine.flatten(profile.step(machine.rows(basis),digit))
          got=[row[column] for row in machine.matrices[digit]]
          check(got==oracle,'all_columns_vs_routed_polynomials',(p,r,a,b,column,digit))
      if N<=8:
        for bits in itertools.product((False,True),repeat=N):
          T={i for i,v in enumerate(bits) if v}
          if invariant(seed,edges,T):check(S<=T,'exhaustive_small_mask_minimality')
      x=[rng.randrange(machine.modulus) for i in machine.support]
      y=[rng.randrange(machine.modulus) for i in machine.support]
      for digit in range(p):
        got=machine.step(x,digit)
        check(machine.embed(got)==machine.flatten(profile.step(machine.rows(machine.embed(x)),digit)),'arbitrary_coordinate_embedding')
        xy=[(xx+yy)%machine.modulus for xx,yy in zip(x,y)]
        check(machine.step(xy,digit)==[(xx+yy)%machine.modulus for xx,yy in zip(got,machine.step(y,digit))],'restricted_additivity')
      oracle=recurrence_coefficients(p,machine.modulus,a,b,40)
      for n,want in enumerate(oracle):
        value=machine.coefficient(n)
        check(value==want,'coefficients_vs_direct_recurrence',(p,r,a,b,n))
        check(value==profile.coefficient(n),'coefficients_vs_profile')
        check(value==original.coefficient(n),'coefficients_vs_original')
      if (p,r,a,b) in [(2,4,[1],[1,4]),(2,8,[1],[1,-1]),(2,8,[1],[1,16]),(3,6,[1],[1,81])]:
        examples.append({'p':p,'r':r,'A':a,'B':b,'profile_slots':N,'support_slots':len(S),
         'profile_capacities':profile.widths,'kept_positions':[[i+1,j] for t,(i,j) in enumerate(machine.positions) if t in S],
         'removed_positions':[[i+1,j] for t,(i,j) in enumerate(machine.positions) if t not in S],'first16':oracle[:16]})
    # A sum of opposite columns is zero: branchwise-union closure is not minimal.
    initial=[1,0]; combined=[[[0,0],[0,0]]]
    check(least_support(initial,combined)[0]=={0},'intra_column_cancellation')
    check(least_support([1,1,0],[[[0,0,0],[0,0,0],[1,4,0]]])[0]=={0,1,2},'correlated_support_full')
    check(matvec([[0,0,0],[0,0,0],[1,4,0]],[1,1,0],5)==[0,0,0],'correlated_orbit_vanishes')
    check(least_support([2,0],[[[0,0],[2,0]]])[0]=={0,1},'zero_divisor_support_full')
    check(matvec([[0,0],[2,0]],[2,0],4)==[0,0],'zero_divisor_orbit_vanishes')
    return {'status':'PASS','assertions':sum(counts.values()),'counts':dict(counts),'generic_systems':generic,
      'mask_cases':len(cases),'strict_support_reductions':strict,'examples':examples,'seed':SEED,'python':platform.python_version(),
      'seconds':time.monotonic()-start,'failures':[],
      'non_claims':['Finite tests do not prove universal correctness','Python is not formally refined to Lean',
        'Least coordinate box is not least invariant submodule or reachable automaton','No runtime or memory benchmark']}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    result=audit();args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
