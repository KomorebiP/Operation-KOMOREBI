"""Independent Q(i) nodal replay of physical R/L/C graphs. Author: Komorebi P.

No certificate-kernel algebra or synthesis decoder is imported here.
"""
from dataclasses import dataclass
from fractions import Fraction as F


@dataclass(frozen=True)
class C:
    re:F=F(0)
    im:F=F(0)
    def __post_init__(self):
        object.__setattr__(self,'re',F(self.re));object.__setattr__(self,'im',F(self.im))
    @staticmethod
    def make(v):return v if isinstance(v,C) else C(F(v))
    def __add__(self,v):
        v=C.make(v);return C(self.re+v.re,self.im+v.im)
    __radd__=__add__
    def __neg__(self):return C(-self.re,-self.im)
    def __sub__(self,v):return self+-C.make(v)
    def __rsub__(self,v):return C.make(v)+-self
    def __mul__(self,v):
        v=C.make(v);return C(self.re*v.re-self.im*v.im,self.re*v.im+self.im*v.re)
    __rmul__=__mul__
    def conjugate(self):return C(self.re,-self.im)
    def normsq(self):return self.re*self.re+self.im*self.im
    def __truediv__(self,v):
        v=C.make(v);n=v.normsq()
        if not n:raise ZeroDivisionError('Exact zero complex denominator')
        z=self*v.conjugate();return C(z.re/n,z.im/n)
    def __rtruediv__(self,v):return C.make(v)/self
    def __bool__(self):return bool(self.re or self.im)


def solve(A,b):
    rows=[list(row)+[value] for row,value in zip(A,b)];n=len(rows)
    for column in range(n):
        pivot=next((j for j in range(column,n) if rows[j][column]),None)
        if pivot is None:raise ValueError('Singular exact nodal system')
        rows[column],rows[pivot]=rows[pivot],rows[column]
        a=rows[column][column];rows[column]=[v/a for v in rows[column]]
        for j in range(n):
            if j!=column:
                a=rows[j][column];rows[j]=[v-a*w for v,w in zip(rows[j],rows[column])]
    return [row[-1] for row in rows]


def from_checked_graph(graph):
    rows=[]
    for branch in graph['branches']:
        coefficient=branch['coefficient']
        if coefficient['kind']!='rational':raise ValueError('Only exact rational branches in this independent replay')
        kind={'g':'R','h':'L','c':'C'}[branch['type']]
        value=F(coefficient['value']);value=value if kind=='C' else 1/value
        u,v=branch['nodes'];rows.append((kind,u,v,value))
    return rows


def response(edges,s):
    s=C.make(s)
    reached={1}
    while True:
        more=reached|{v for _,u,v,_ in edges if u in reached}|{u for _,u,v,_ in edges if v in reached}
        if more==reached:break
        reached=more
    if 0 not in reached:return {'gamma':C(1),'voltages':{},'currents':[]}
    nodes=sorted(reached-{0});index={v:j for j,v in enumerate(nodes)}
    A=[[C() for _ in nodes] for _ in nodes];rhs=[C() for _ in nodes]
    admittances=[]
    for kind,u,v,value in edges:
        y=C(1/value) if kind=='R' else s*value if kind=='C' else 1/(s*value)
        admittances.append(y)
        if u not in reached or v not in reached:continue
        for a,b in ((u,v),(v,u)):
            if a in index:
                A[index[a]][index[a]]+=y
                if b in index:A[index[a]][index[b]]-=y
    A[index[1]][index[1]]+=1;rhs[index[1]]=C(1)
    solution=solve(A,rhs);voltages={0:C(),**{v:solution[j] for v,j in index.items()}}
    currents=[y*(voltages.get(u,C())-voltages.get(v,C())) for y,(_,u,v,_) in zip(admittances,edges)]
    return {'gamma':2*voltages[1]-1,'voltages':voltages,'currents':currents}


def target_gamma(P,Q,s):
    def value(poly):
        out=C()
        for coefficient in reversed(poly):out=out*s+F(coefficient)
        return out
    p,q=value(P),value(Q)
    return (p-q)/(p+q)
