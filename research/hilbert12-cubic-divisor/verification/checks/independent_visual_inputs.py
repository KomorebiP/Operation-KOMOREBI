#!/usr/bin/env python3
"""Read-only independent input checks for the H12 visual release.

Does not import or execute the author's generator. Finite exact comparisons
use Python integers/Fraction. Coordinates use mpmath at 110 digits solely as
an independent floating diagnostic, with absolute tolerance 1e-76.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
import hashlib, json, sys, platform, time
import mpmath as mp

ROOT = Path(__file__).resolve().parents[2]
CONTROL = ROOT / 'visual/finite_control.json'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
started = time.monotonic()
record = json.loads(CONTROL.read_text())
checks = record['checks']
assert sha(ROOT/'visual/generate_figures.py') == record['script_sha256']
for row in record['figure_files']:
    assert sha(ROOT/'visual'/row['path']) == row['sha256']

def ceil_fraction(x):
    q, r = divmod(x.numerator, x.denominator)
    return q + bool(r)

def coeff(a,b,c):
    pivot = ceil_fraction(Fraction(3*c-2*b,7))
    w = 5*int(c % 5 == 0)-1
    return w*(int(pivot>0)-int(2*pivot-a>0)-int(a>0)+int(b>0))

count = 0
for a in range(-6,7):
    for b in range(-6,7):
        for c in range(-6,7):
            lifts = []
            for k in range(7):
                xyz = (Fraction(-2*b+3*c+k,7),
                       Fraction(-7*a-4*b+6*c+2*k,7),
                       Fraction(-5*b+4*c+20*k,7))
                if all(x.denominator==1 for x in xyz):
                    lifts.append(tuple(int(x) for x in xyz))
            assert len(lifts)==1
            aa,bb,cc=lifts[0]
            numerator=(5*int(cc%5==0)-1)*(int(aa>0)-int(bb>0))
            denominator=(5*int(c%5==0)-1)*(int(a>0)-int(b>0))
            assert coeff(a,b,c)==numerator-denominator
            assert coeff(a,b,c) in {-4,-1,0,1,4}
            count+=1
assert checks['fraction_lift_comparison']=={'box':[-6,6],'triples':count,'all_seven_lifts':True}

def families(n):
    zs=set(); ps=set()
    for a in range(-n,0):
        for b in range(1,n+1):
            for c in range(5*n+1,10*n+1):
                if c%5==0:zs.add((a,b,c))
                else:ps.add((a,b,c))
    return zs,ps

families_checked=0
for row in checks['family_counts']:
    n=row['n']; z,p=families(n)
    assert len(z)==n**3 and len(p)==4*n**3 and not z&p
    assert all(coeff(*v)==4 for v in z)
    assert all(coeff(*v)==-1 for v in p)
    assert all(-n<=a<0 and 0<b<=n and 0<c<=10*n for a,b,c in z|p)
    assert row=={'n':n,'distinct_zeros':n**3,'distinct_poles':4*n**3,
                 'zero_multiplicity':4*n**3,'pole_multiplicity':4*n**3}
    families_checked+=len(z)+len(p)
assert [r['n'] for r in checks['family_counts']]==list(range(1,17))

line_sets=[{(0,0),(1,0),(2,0)}, {(0,0),(0,1),(0,2)},
           {(0,0),(1,1),(2,2)}, {(0,0),(1,2),(2,1)}]
assert [set(map(tuple,x)) for x in checks['four_norm_lines']['lines']]==line_sets
assert checks['four_norm_lines']['incidence']=={
    f'{a},{b}':sum((a,b) in line for line in line_sets) for a in range(3) for b in range(3)}
assert checks['four_norm_lines']['incidence']['0,0']==4
for cycle in checks['seven_action']['cycles']:
    assert all((4*cycle[k])%7==cycle[(k+1)%len(cycle)] for k in range(len(cycle)))
assert sorted(sum(checks['seven_action']['cycles'],[]))==list(range(7))

digit_counts=Counter()
for b in range(-8,9):
    for c in range(-8,9):
        j=ceil_fraction(Fraction(3*c-2*b,7)); digit=7*j+2*b-3*c
        assert 0<=digit<7
        digit_counts[digit]+=1
assert checks['ceiling_plot']=={'b':[-8,8],'c':[-8,8],
                               'digit_counts':[digit_counts[k] for k in range(7)]}
expected_jets=[[str(Fraction(0) if k<=g else Fraction(-1,k)) for k in range(1,5)] for g in range(4)]
assert checks['canonical_local_log_coefficients']==expected_jets
assert checks['polynomial_reconstruction']=={
    'reflection_z2':['0','2','0'],'transition_second_derivative':['0','0','6'],
    'cube_exponents':[str(3*Fraction(1,3)**k-1) for k in range(1,4)]}
assert coeff(-1,1,11)!=4 and coeff(-1,-1,10)==0
assert Fraction(expected_jets[2][2])!=0 and Fraction(-2,3)!=Fraction(-1,3)
assert all(checks['negative_controls'].values())

def matmul(a,b):
    return [[sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]
def det(a):
    return (a[0][0]*(a[1][1]*a[2][2]-a[1][2]*a[2][1])
            -a[0][1]*(a[1][0]*a[2][2]-a[1][2]*a[2][0])
            +a[0][2]*(a[1][0]*a[2][1]-a[1][1]*a[2][0]))
mat=checks['principal_matrices'];I=[[int(i==j) for j in range(3)] for i in range(3)]
assert mat['N']==[[2,-1,0],[4,0,-15],[1,0,-2]]
assert mat['N5']==[[2,-1,0],[4,0,-3],[5,0,-2]]
assert mat['M']==[[2*I[i][j]-mat['N'][i][j] for j in range(3)] for i in range(3)]
for name in ('N','N5'):
    assert det(mat[name])==7
    assert matmul(matmul(mat[name],mat[name]),mat[name])==[[7*x for x in r] for r in I]
assert det(mat['M'])==1

mp.mp.dps=110
beta=mp.root(7,3)*mp.exp(-2*mp.pi*mp.j/3)
tau=(beta**2+2*beta)/15;s=-(beta+2)/15;t=-tau;delta=(tau+2*s+4)/7
expected_periods={'beta':beta,'tau':tau,'t':t,'s':s,'delta':delta}
assert beta.imag<0 and t.imag>0 and s.imag>0 and delta.imag>0
assert abs(beta*tau-(2*tau+4*s+1))<mp.mpf('1e-105')
assert abs(beta*s+tau)<mp.mpf('1e-105')
assert abs(beta*delta+8*s+1)<mp.mpf('1e-105')
period_error=mp.mpf(0);coordinate_error=mp.mpf(0);coordinate_count=0
for name,val in expected_periods.items():
    row=checks['fixed_periods_numerical'][name]
    got=mp.mpc(row['real'],row['imag']);period_error=max(period_error,abs(got-val))
    assert abs(got-val)<mp.mpf('1e-76')
for n in (2,3):
    zs,ps=families(n)
    for label,family in [('zeros',zs),('poles',ps)]:
        rows=checks['plotted_embeddings'][str(n)][label]
        assert {tuple(row['triple']) for row in rows}==family
        assert len(rows)==len(family)
        for row in rows:
            a,b,c=row['triple'];expected=(a*tau+b*s+mp.mpf(c)/5)/beta
            got=mp.mpc(row['coordinate']['real'],row['coordinate']['imag'])
            assert row['order']==coeff(a,b,c)
            coordinate_error=max(coordinate_error,abs(got-expected));coordinate_count+=1
            assert abs(got-expected)<mp.mpf('1e-76')

out={'verdict':'implementation and finite assertion verified in the stated range',
     'scope':'Read-only independent exact controls and separately implemented coordinate diagnostic; not a universal analytic proof or interval certificate.',
     'author_generator_imported_or_executed':False,
     'exact_fraction_triples':count,'seven_lifts_per_triple':7,
     'family_parameter_range':[1,16],'family_points':families_checked,
     'coordinate_points':coordinate_count,'coordinate_mpmath_digits':110,
     'coordinate_absolute_tolerance':'1e-76','maximum_period_error':str(period_error),
     'maximum_coordinate_error':str(coordinate_error),
     'inputs':{'visual/finite_control.json':sha(CONTROL),
               'visual/generate_figures.py':sha(ROOT/'visual/generate_figures.py')},
     'command':'PYTHONPATH=/workspace/scratch/1633631fc4bd/work/validation/dependencies "$CODEX_PRIMARY_RUNTIME_PYTHON" verification/checks/independent_visual_inputs.py',
     'software':{'Python':sys.version.split()[0],'mpmath':mp.__version__},
     'elapsed_seconds':time.monotonic()-started,
     'nonclaims':['no elliptic gamma evaluation','no infinite canonical product evaluation',
                  'no directed intervals','no arithmetic phase equality','no universal complex Lean result']}
print(json.dumps(out,indent=2))
if len(sys.argv)>1:
    Path(sys.argv[1]).write_text(json.dumps(out,indent=2)+'\n')
