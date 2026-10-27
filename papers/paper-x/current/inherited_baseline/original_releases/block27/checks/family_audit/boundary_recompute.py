"""Independent exact arithmetic for the two named audit fixtures only."""
from pathlib import Path
import json

def mm(a,b):return [[sum(x*y for x,y in zip(row,col)) for col in zip(*b)] for row in a]
def add(a,b):return [[x+y for x,y in zip(r,s)] for r,s in zip(a,b)]
def sub(a,b):return [[x-y for x,y in zip(r,s)] for r,s in zip(a,b)]
def zero(n):return [[0]*n for _ in range(n)]
def eye(n):return [[int(i==j) for j in range(n)] for i in range(n)]
def summ(xs):
    z=zero(len(xs[0]))
    for x in xs:z=add(z,x)
    return z
E=[[1,0],[0,0]];P=[[0,2],[0,1]]
assert mm(E,E)==E and mm(P,P)==P
assert mm(E,P)==[[0,2],[0,0]] and mm(E,P)!=zero(2)
F=[[[1,-2],[0,0]],P];B=[E,[[0,0],[0,1]]]
U=summ([mm(f,b) for f,b in zip(F,B)])
assert U==[[1,2],[0,1]]
Ui=[[1,-2],[0,1]]
assert mm(U,Ui)==eye(2)==mm(Ui,U)
assert all(mm(mm(U,b),Ui)==f for b,f in zip(B,F))
D=[[1,0,0],[0,-1,0],[0,0,1]]
Q=[[[1,-2,0],[0,0,0],[0,0,0]],[[0,2,0],[0,1,0],[0,0,0]],[[0,0,0],[0,0,0],[0,0,1]]]
assert summ(Q)==eye(3)
assert all(mm(x,y)==(x if i==j else zero(3)) for i,x in enumerate(Q) for j,y in enumerate(Q))
comm=[sub(mm(D,q),mm(q,D)) for q in Q]
assert all(all(x%4==0 for r in c for x in r) for c in comm)
assert any(c!=zero(3) for c in comm)
T=[[[int(a==i and b==i) for b in range(3)] for a in range(3)] for i in range(3)]
assert all(mm(D,t)==mm(t,D) for t in T)
assert all(all((x-y)%2==0 for r,s in zip(q,t) for x,y in zip(r,s)) for q,t in zip(Q,T))
Path(__file__).with_name('boundary_recompute.json').write_text(json.dumps({'status':'passed',
    'domain':'exact integer matrix identities, inherited by Z_2','independent_product':mm(E,P),
    'comparison_matrix':U,'three_projector_commutators':comm,'three_corrected_projectors':T,
    'scope':'two explicit fixtures only; no exhaustive or universal computational claim'},indent=2)+'\n')
print('Exact independent boundary fixtures passed')
