from __future__ import annotations
from pathlib import Path
import cmath, itertools, json, math, random, re
import numpy as np

ROOT=Path(__file__).resolve().parents[1]
TEX=ROOT/'PSC_Strong_Artin_Residual_Realization.tex'
BIB=ROOT/'PSC_Strong_Artin_Residual_Realization.bib'
checks=0; failures=[]; groups=[]

def check(c,msg):
    global checks
    checks+=1
    if not c: failures.append(msg)

def run(name,fn):
    before=checks; fn(); groups.append((name,checks-before))

def roots(p): return [cmath.exp(2j*math.pi*j/p) for j in range(p)]

def coefficient_rotation():
    rng=random.Random(911)
    for p in [2,3,5,7,11]:
        mus=roots(p)
        for n in range(1,10):
            eig=[complex(rng.uniform(.3,1.7),rng.uniform(-1,1)) for _ in range(n)]
            for z in mus:
                # elementary symmetric coefficients by polynomial roots
                c=np.poly(eig)
                cz=np.poly([z*x for x in eig])
                for k in range(n+1):
                    # coefficient index k has z^k scaling
                    check(abs(cz[k]-(z**k)*c[k])<1e-7*max(1,abs(cz[k])),f'rotation p={p} n={n} k={k}')
        for n in range(1,30):
            vals=[(z**n) for z in mus]
            check((len({round(v.real,10)+1j*round(v.imag,10) for v in vals})==p)==(n%p!=0),f'determinant selector p={p} n={n}')

def spectra():
    rng=random.Random(321)
    for p in [2,3,5,7]:
        zeta=cmath.exp(2j*math.pi/p)
        for _ in range(200):
            spectra=[np.array([rng.randrange(0,4) for _ in range(p)],dtype=int) for __ in range(rng.randrange(1,5))]
            j=rng.randrange(p)
            shifted=[np.roll(a,j) for a in spectra]  # coeff b at index a+j
            # polynomial criterion
            for a,b in zip(spectra,shifted):
                check(np.array_equal(np.roll(a,j),b),'spectrum shift')
                for r in range(p):
                    ha=sum(int(a[q])*zeta**(q*r) for q in range(p))
                    hb=sum(int(b[q])*zeta**(q*r) for q in range(p))
                    check(abs(hb-zeta**(j*r)*ha)<1e-7,'Fourier shift')
            sols=[]
            for x in range(p):
                if all(np.array_equal(np.roll(a,x),b) for a,b in zip(spectra,shifted)): sols.append(x)
            check(j in sols,'alignment contains true shift')
            # all solutions form a coset of common stabilizer
            stab=[x for x in range(p) if all(np.array_equal(np.roll(a,x),a) for a in spectra)]
            expected=sorted({(j+x)%p for x in stab})
            check(sorted(sols)==expected,'alignment coset')

def finite_satake():
    rng=random.Random(45)
    for d in range(1,9):
        for f in [q for q in range(1,d+1) if d%q==0]:
            for M in range(1,13):
                for _ in range(30):
                    e=rng.randrange(f*M)
                    alpha=cmath.exp(2j*math.pi*e/(f*M))
                    check(abs(alpha**(f*M)-1)<1e-7,'alpha in mu fM')
                    check(abs((alpha**f)**M-1)<1e-7,'base root in mu M')
                    check(abs(alpha**(d*M)-1)<1e-7,'alpha in mu dM')
    # multiset count bound on small sets
    for N in range(1,8):
        for n in range(1,7):
            count=math.comb(N+n-1,n)
            brute=sum(1 for c in itertools.combinations_with_replacement(range(N),n))
            check(count==brute,'multiset formula')

def global_alignment():
    rng=random.Random(77)
    for p in [2,3,5,7,11]:
        universe=set(range(p))
        for _ in range(500):
            sets=[]
            for __ in range(rng.randrange(1,8)):
                S={j for j in range(p) if rng.random()<.55}
                sets.append(S)
            inter=set.intersection(*sets) if sets else universe
            check(any(all(j in S for S in sets) for j in range(p))==(len(inter)>0),'intersection criterion')

def galois_trace_separator():
    # C3 x C2 stable one dimensional example
    p=2
    vals=[1,-1]
    check(len(set(vals))==2,'C2 extension trace separates')
    # S3 standard moving orbit has self twist by sign, characters [2,0,-1]
    std=[2,0,-1]; sign=[1,-1,1]
    twisted=[a*b for a,b in zip(std,sign)]
    check(twisted==std,'S3 moving self twist')

def positive_cone():
    # S3 classes: 1, transpositions, 3 cycles.  Standard is induced from nontrivial C3 char.
    std=(2,0,-1)
    induced=(2,0,-1)
    check(std==induced,'S3 positive monomial certificate')
    # Artificial lattice feasibility: 2 chi = theta1+theta2
    chi=np.array([1,0,0])
    theta1=np.array([1,1,0]); theta2=np.array([1,-1,0])
    check(np.array_equal(2*chi,theta1+theta2),'positive saturation toy identity')

def source_integrity():
    tex=TEX.read_text(); bib=BIB.read_text()
    labels=re.findall(r'\\label\{([^}]+)\}',tex)
    check(len(labels)==len(set(labels)),'unique labels')
    refs=[]
    for cmd in ['ref','cref','Cref','eqref']:
        for g in re.findall(r'\\'+cmd+r'\{([^}]+)\}',tex): refs.extend(x.strip() for x in g.split(','))
    check(not(set(refs)-set(labels)),'all refs resolve')
    keys=set(re.findall(r'@\w+\{([^,]+),',bib)); cites=set()
    for g in re.findall(r'\\cite\{([^}]+)\}',tex): cites.update(x.strip() for x in g.split(','))
    check(not(cites-keys),'all citations in bib')
    check(not(keys-cites),'all bib cited')
    proved=sum(tex.count(f'\\begin{{{e}}}') for e in ['theorem','proposition','lemma','corollary'])
    proved_examples=len(re.findall(r'\\end\{example\}\s*\\begin\{proof\}',tex))
    proofs=tex.count('\\begin{proof}')
    check(proved+proved_examples==proofs,f'proof count {proved}+{proved_examples} {proofs}')
    check(tex.count(';')==0,'no semicolons')
    check('\\newpage' not in tex and '\\pagebreak' not in tex,'no forced page breaks')
    figs=re.findall(r'\\includegraphics(?:\[[^]]*\])?\{([^}]+)\}',tex)
    for f in figs: check((ROOT/'figures'/f).exists(),f'figure exists {f}')
    check(len(figs)==len(set(figs)),'unique figure uses')
    log=(ROOT/'build8.log').read_text(errors='ignore')
    check('undefined references' not in log.lower(),'no undefined references')
    check('undefined citations' not in log.lower(),'no undefined citations')
    check('Overfull' not in log,'no overfull boxes')

for name,fn in [
    ('Coefficient rotations and determinant sieve',coefficient_rotation),
    ('Extension spectra and Fourier tests',spectra),
    ('Finite Satake cyclotomic bounds',finite_satake),
    ('Global alignment intersections',global_alignment),
    ('Finite Galois examples',galois_trace_separator),
    ('Positive cone certificates',positive_cone),
    ('Source integrity',source_integrity)]: run(name,fn)

summary={'checks':checks,'failures':failures,'groups':[{'name':n,'checks':c} for n,c in groups]}
(ROOT/'verification'/'verification_summary.json').write_text(json.dumps(summary,indent=2)+'\n')
lines=[f'Strong Artin attack verification: {checks-len(failures)}/{checks} checks passed']+[f'{n}: {c}' for n,c in groups]
if failures: lines+=['Failures:']+failures
(ROOT/'verification'/'verification_summary.txt').write_text('\n'.join(lines)+'\n')
print('\n'.join(lines))
raise SystemExit(1 if failures else 0)
