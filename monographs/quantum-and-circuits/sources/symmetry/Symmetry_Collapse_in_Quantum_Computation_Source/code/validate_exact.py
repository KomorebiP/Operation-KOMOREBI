"""Exact finite controls over Q. No floating arithmetic or universal claims."""
from fractions import Fraction as F
from math import comb
import json
from symmetry_packets import weight_basis, qubit_commutant_parameter_count


def mul(a, b):
    return [[sum((x*y for x,y in zip(row,col)), F(0)) for col in zip(*b)] for row in a]


def transpose(a):
    return list(map(list, zip(*a)))


def identity(n):
    return [[F(i == j) for j in range(n)] for i in range(n)]


def norm2(v):
    return sum((row[0]**2 for row in v), F(0))


def main():
    count = 0
    def check(condition):
        nonlocal count
        assert condition
        count += 1
    # Independent bit-count enumeration versus subset-based API indexing.
    for n in range(13):
        for k in range(n+1):
            check(sorted(weight_basis(n,k)) == [x for x in range(1<<n) if x.bit_count() == k])
        check(qubit_commutant_parameter_count(n) == comb(n+3,3))
    # Orthogonal rational exchange: a structurally number-preserving rotation.
    rotation = [[F(3,5), -F(4,5)], [F(4,5), F(3,5)]]
    check(mul(transpose(rotation), rotation) == identity(2))
    circuit_instances = 0
    for n in range(1,7):
        size = 1<<n
        gates=[]
        for q in range(n-1):
            g=identity(size)
            mask=(1<<q)|(1<<(q+1))
            for x in range(size):
                if (x & mask)==(1<<q):
                    y=x^mask
                    for i,a in enumerate([x,y]):
                        for j,b in enumerate([x,y]):
                            g[a][b]=rotation[i][j]
            gates.append(g)
        for k in range(n+1):
            basis=weight_basis(n,k)
            initial=[[F(i+1,len(basis)+1)] for i in range(len(basis))]
            reduced=initial
            full=[[F(0)] for _ in range(size)]
            for i,x in enumerate(basis):full[x]=initial[i]
            for g in gates:
                full=mul(g,full)
                restricted=[[g[x][y] for y in basis] for x in basis]
                reduced=mul(restricted,reduced)
                check([full[x] for x in basis]==reduced)
                check(all(full[x]==[F(0)] for x in range(size) if x not in basis))
            check(norm2(full)==norm2(initial))
            circuit_instances+=1
    # Adaptive-projection example from the written theorem, with exact tail norms.
    initial=[[F(1)],[F(0)]]
    p=[[F(1),F(0)],[F(0),F(0)]]
    exact=initial
    approx=initial
    tails=[]
    for _ in range(2):
        exact=mul(rotation,exact)
        unprojected=mul(rotation,approx)
        approx=mul(p,unprojected)
        tails.append(abs(unprojected[1][0]))
    check(tails==[F(4,5),F(12,25)])
    check(approx==[[F(9,25)],[F(0)]])
    check(exact==[[F(-7,25)],[F(24,25)]])
    error2=norm2([[a[0]-b[0]] for a,b in zip(exact,approx)])
    check(error2 <= sum(tails)**2)
    effect_difference=abs(exact[0][0]**2-approx[0][0]**2)
    check(effect_difference <= 2*sum(tails))
    # Negative control: renormalization is excluded by the theorem.
    renormalized=[[F(1)],[F(0)]]
    check(renormalized != approx)
    print(json.dumps({'status':'PASS','domain':'rational/integer exact','assertions':count,
                      'fixed_weight_instances':circuit_instances,'qubits':{'min':1,'max':6},
                      'dimension_count_n':{'min':0,'max':12},
                      'adaptive_tails':[str(x) for x in tails],
                      'adaptive_error_squared':str(error2),
                      'non_claims':['No universal theorem follows from finite checks.','No timing benchmark was rerun.']}))

if __name__=='__main__':main()
