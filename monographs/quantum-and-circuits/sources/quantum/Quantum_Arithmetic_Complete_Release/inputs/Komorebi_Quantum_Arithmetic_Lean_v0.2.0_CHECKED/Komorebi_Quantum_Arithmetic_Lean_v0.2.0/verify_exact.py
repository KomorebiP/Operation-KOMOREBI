from fractions import Fraction as Q

N=12
RAM=[Q(x) for x in [4,0,2,0,-2,0,-4,0,-2,0,2,0]]
NOISE=[Q(x) for x in [5,2,-1,2,5,2,-1,2,5,2,-1,2]]
TEST=[RAM[i]+NOISE[i] for i in range(N)]
P=[[RAM[(i-j)%N]/N for j in range(N)] for i in range(N)]

def mm(A,B):
    return [[sum(A[i][k]*B[k][j] for k in range(N)) for j in range(N)] for i in range(N)]

def mv(A,v):
    return [sum(A[i][j]*v[j] for j in range(N)) for i in range(N)]

def dot(x,y): return sum(a*b for a,b in zip(x,y))
assert mm(P,P)==P
assert [[P[j][i] for j in range(N)] for i in range(N)]==P
assert mv(P,RAM)==RAM
assert mv(P,NOISE)==[Q(0)]*N
assert mv(P,TEST)==RAM
assert dot(RAM,RAM)==48
assert dot(NOISE,NOISE)==102
assert dot(TEST,TEST)==150

# exact Q(sqrt(3), i), tuple = a + b sqrt3 + i(c + d sqrt3)
def add(x,y): return tuple(x[i]+y[i] for i in range(4))
def mul(x,y):
    a,b,c,d=x;e,f,g,h=y
    return (a*e+3*b*f-c*g-3*d*h,
            a*f+b*e-c*h-d*g,
            a*g+3*b*h+c*e+3*d*f,
            a*h+b*g+c*f+d*e)
def power(x,n):
    r=(Q(1),Q(0),Q(0),Q(0))
    for _ in range(n): r=mul(r,x)
    return r
def summ(xs):
    r=(Q(0),Q(0),Q(0),Q(0))
    for x in xs:r=add(r,x)
    return r
def qr(x):return (Q(x),Q(0),Q(0),Q(0))

z=(Q(0),Q(1,2),Q(1,2),Q(0))
zi=(Q(0),Q(1,2),Q(-1,2),Q(0))
ONE=qr(1)
assert power(z,12)==ONE
assert mul(z,zi)==ONE
U=[1,5,7,11]
def ramc(n):return summ(power(z,a*n) for a in U)
rv=[ramc(n) for n in range(N)]
assert rv==[qr(x) for x in RAM]
def dft(v,k):return summ(mul(v[n],power(zi,k*n)) for n in range(N))
assert [dft(rv,k) for k in range(N)]==[qr(x) for x in [0,12,0,0,0,12,0,12,0,0,0,12]]
absrv=[qr(abs(int(x))) for x in RAM]
assert [dft(absrv,k) for k in range(N)]==[qr(x) for x in [16,0,4,0,4,0,16,0,4,0,4,0]]
assert Q(12**2,48*12)==Q(1,4)
print('PASS: all exact rational/cyclotomic bridge checks')
