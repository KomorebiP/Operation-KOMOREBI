"""Independent exact F2 checks for the two-qubit analytic cost theorem.

No imports from the catalytic atlas. Coordinates: (x0,x1,z0,z1).
The unbounded lower-bound arguments are in the theorem and audit report.
"""
from itertools import product
import json

def identity(n):
    return [[int(i == j) for j in range(n)] for i in range(n)]

def mul(a, b):
    return [[sum(x*y for x,y in zip(row,col)) % 2 for col in zip(*b)] for row in a]

def hadamard(i):
    a = identity(4)
    a[i], a[2+i] = a[2+i], a[i]
    return a

def phase(i):
    a = identity(4)
    a[2+i][i] = 1
    return a

def cnot(c, t):
    a = identity(4)
    a[t][c] = 1
    a[2+c][2+t] = 1
    return a

def word(gates):
    a = identity(4)
    for g in gates:
        a = mul(g, a)
    return a

def target(d):
    return [[0,1,0,0],[1,0,0,0],[1,d[0],0,1],[d[1],1,1,0]]

def main():
    base = [hadamard(1), cnot(1,0), cnot(0,1), hadamard(0)]
    restricted = [cnot(0,1), phase(1), cnot(1,0), cnot(0,1)]
    assert word(base) == target((0,0))
    assert word(restricted) == target((1,1))
    targets = []
    for d in product(range(2), repeat=2):
        t = target(d)
        assert word(base + [phase(i) for i in range(2) if d[i]]) == t
        assert word(restricted + [phase(i) for i in range(2) if d[i] != 1]) == t
        for i in range(2):
            assert [[t[j][k] for k in [i,i+2]] for j in [i,i+2]] == [[0,0],[1,0]]
        targets.append(t)
    assert len({str(t) for t in targets}) == 4
    lo = [[1,0],[1,1]]
    up = [[1,1],[0,1]]
    swap = [[0,1],[1,0]]
    assert swap not in [identity(2),lo,up,mul(lo,lo),mul(up,up),mul(lo,up),mul(up,lo)]
    print(json.dumps({'status':'PASS','arithmetic':'F2','target_count':4,
                      'scope':'witness products, distinct orbit, diagonal block ranks, and length-at-most-two A-block products'}))

if __name__ == '__main__':
    main()
