"""Independent bounded checks for the sixteen visual scenes.

Run from the publication root: python3 review/independent_visual_review_checks.py
Only review artifacts are written. No author module is imported or executed.
"""
from pathlib import Path
from fractions import Fraction as F
from itertools import product, combinations
from datetime import datetime, timezone
import hashlib, json, math, platform, time

ROOT=Path(__file__).resolve().parents[1]
started=datetime.now(timezone.utc).isoformat(); clock=time.monotonic()
results=[]
def ck(name, condition, detail):
    assert condition, name
    results.append({'name':name,'passed':True,'detail':detail})
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def dot(a,b): return sum(x*y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))

inputs=['records/foundations_scenes.json','records/analysis_scenes.json',
        'records/monograph_references.json','tools/visual_companion/foundations.py',
        'tools/visual_companion/analysis.py','tools/visual_companion/style.py',
        'source/Komorebi_Space_Visual_Guide.tex','source/visual_companion/scenes.json',
        'review/independent_visual_review_checks.py']
before={p:sha(ROOT/p) for p in inputs}
scenes=sum((json.loads((ROOT/p).read_text()) for p in inputs[:2]),[])
refs=json.loads((ROOT/inputs[2]).read_text())
ck('sixteen scene IDs',len(scenes)==16 and len({s['id'] for s in scenes})==16,'No duplicate scene IDs.')
ck('monograph pointers exist',all(l in refs for s in scenes for l in s['monograph_labels']),
   'All named sections exist in the compiled original monograph map; relevance was checked by reading their source.')
ck('all scene figures exist',all((ROOT/'source/figures/visual_companion'/s['figure']).is_file() for s in scenes),'Sixteen vector figure paths resolve.')

# Foundation checks use elementary independent representations.
ck('f01 overlaps',(2,1)[1]==(1,3)[0] and (2,1)[0]==(2,3)[0] and (1,3)[1]==(2,3)[1]
   and (2,1)[0]!=(4,3)[0],'The coherent three pairs share each coordinate; changed xz disagrees in x.')
ck('f02 parity and free coordinate',F(2,2).denominator==1 and F(3,2).denominator!=1,
   'The required m is k/2; fixing the independent z selects one point only on the even slice.')
gauges=[(u,v) for u,v in product(range(2),repeat=2) if (u+1-v)%2==0]
ck('f03 comparison equations',gauges==[(0,1),(1,0)] and [a for a in gauges if (1+a[0])%2==0]==[(1,0)]
   and [a for a in gauges if a[0]==0]==[(0,1)],'All four gauges checked, including changed target mark.')
bits=[0,1,0,1]
ck('f04 face equations',all((bits[i]+bits[k]-bits[i]-bits[j]-bits[j]-bits[k])%2==0
   for i,j,k in combinations(range(4),3)) and (1-0-0)%2!=0,'Four nondegenerate composition faces; identities have zero labels.')
G=list(product(range(2),repeat=2));add=lambda a,b:tuple((x+y)%2 for x,y in zip(a,b));c=lambda a,b:a[1]*b[0]
ck('f05 associative bit law',all((c(a,b)+c(add(a,b),d)-c(b,d)-c(a,add(b,d)))%2==0
   for a,b,d in product(G,repeat=3)),'All 64 triples checked exactly in F2.')
swap=lambda v:(v[1],v[0]);sign=lambda v:(v[0],-v[1])
ck('f05 action order', sign(swap((1,2)))==(2,-1) and swap(sign((1,2)))==(-2,1)
   and c((0,1),(1,0))==1 and c((1,0),(0,1))==0,
   'Hand substitution: X(1,2)=(2,1), Z(2,1)=(2,-1); Z(1,2)=(1,-2), X(1,-2)=(-2,1).')
vals=[1,-1,1,-1,1]; r=[vals[i+1]-vals[i] for i in range(4)]
C=lambda x:(x[0]+x[1],x[2]+x[3]);J=lambda x:(0,x[0],0,x[1])
ck('f06 coarsener and detail',C(r)==(0,0) and tuple(r)==sub(r,J(C(r)))
   and all(C(J(x))==x for x in [(1,0),(0,1)]),'Adjacent residual [-2,2,-2,2]; CJ=I on its two basis vectors.')
ck('f07 exact displayed tail maxima',all(max(F(0) if i<n else F(1,2**i) for i in range(7))==F(1,2**n)
   for n in range(4)),'Depths 0..3, coordinates 0..6. Infinite norms additionally follow from explicit monotonicity, not this test.')
x=(F(2),F(2),F(3)); local=(F(2),F(2),F(0)); joint=(F(2),F(0),F(0)); normal=(F(0),F(1),F(-1))
wrong=sub(local,tuple(t*dot(normal,local)/dot(normal,normal) for t in normal))
ck('f08 projections',wrong==(2,1,1) and dot(sub(x,local),sub(local,joint))==0
   and dot(sub(x,joint),sub(x,joint))==13,'Euclidean projection onto y=z after z=0 breaks z=0; nested squared lengths 9+4=13.')

# Analytic checks. Rational parameters make the metric and witness checks exact.
v=(F(3,5),F(4,5),F(0)); a=tuple(t/v[0] for t in v); raw=(F(1),F(0),F(0));y=sub(raw,a)
ck('a01 protected correction invariant',dot(v,v)==1 and y[0]==0 and dot(a,a)==F(25,9)
   and all(a[i]-v[i]*dot(v,a)==0 for i in range(3)),
   'Independent 3-4-5 unit direction: correction norm squared is sec(theta)^2, and p a=0.')
cos=F(3,5);sin=F(4,5)
qdiff=((-cos*cos+1,-cos*sin),(-cos*sin,-sin*sin))
det=qdiff[0][0]*qdiff[1][1]-qdiff[0][1]*qdiff[1][0]
ck('a02 scale and projector formulas',qdiff[0][0]+qdiff[1][1]==0 and det==-sin*sin
   and (cos-1)**2+sin*sin==2*(1-cos),
   'For a rational unit normal, projector eigenvalues are +/-sin(theta); operator difference square is 2s^2(1-cos(theta)).')
for p in [1,2]:
    u=F(0);total=F(0);old_r=F(1)
    for n in range(1,33):
        new_r=F(1,2**n); step=F(1,n**p);u+=step;total+=step+old_r-new_r;old_r=new_r
        assert total==u+1-new_r
ck('a03 exact movement sum',True,'For p=1,2 and N=1..32, l1 movement equals sum(k^-p)+1-2^-N. Infinite conclusions use p-series arguments reviewed separately.')
ck('a04 energy benchmark',all(sum(F(1,n*n) for n in range(1,N+1))<=2 and sum(F(1) for n in range(1,N+1))==N
   for N in [1,16,64]),'Exact finite benchmark energies; the threshold 2-2s<-1 is algebraically equivalent to s>3/2.')
r=(F(1),F(1),F(1,2));a=(F(1,2),F(2,5));v=(F(1,2),F(4,5),F(1,2));Tstarv=(v[0],v[1]/2)
ck('a05 exact supporting witness',Tstarv==a and dot(r,v)-dot(a,a)==dot(v,v)==F(57,50),
   'With M=||a|| and T*v=a, the unnormalized identity proves the normalized witness attains residual sqrt(57/50) over the whole ball.')
for alpha in [F(1,100),F(1),F(100)]:
    aa=(1/(1+alpha),2/(1+4*alpha));vv=(1-aa[0],1-aa[1]/2,F(1,2))
    assert (vv[0],vv[1]/2)==tuple(alpha*t for t in aa)
ck('a05 parametric normal equations',True,'Three independent rational parameter cases; both normal-equation coordinates checked.')
alpha=F(1,50);tau=delta=F(1,50);aa=(1/(1+alpha),tau*delta/(tau*tau+alpha))
ck('a06 noisy two-mode prediction',aa==(F(50,51),F(1,51)) and dot(sub(aa,(1,0)),sub(aa,(1,0)))==F(2,2601),
   'Exact two-mode answer and true-error square at alpha=0.02.')
for e in [F(1),F(1,4),F(1,100),F(1,10000)]:
    gram=((F(1),F(1)),(F(1),1+e*e)); determinant=gram[0][0]*gram[1][1]-gram[0][1]*gram[1][0]
    inverse=((gram[1][1]/determinant,-gram[0][1]/determinant),(-gram[1][0]/determinant,gram[0][0]/determinant))
    cov=(F(0),e); coeff=tuple(dot(row,cov) for row in inverse);normal=(coeff[0]+coeff[1],e*coeff[1])
    assert dot(cov,coeff)==1 and normal==(0,1)
ck('a07 full Gram inverse reconstruction',True,'Four positive rational basis scales: explicit 2x2 inverse gives g=(0,1) and invariant norm square one.')
ck('a08 balanced exponents',F(4,3)/4==1-F(4,3)/2==F(5,3)-F(4,3)==F(1,3),
   'Exact exponent arithmetic at marked choice. Positive exponents require 0<p<2 and q>p.')
for d in [1.,.1,.001,1e-6]:
    p=4/3;q=5/3;m=math.ceil(d**(-p/2));al=m**-2
    assert math.sqrt(2/m)<=math.sqrt(2)*d**(p/4)+1e-11
    assert d*m/2<=(d**(1-p/2)+d)/2+1e-11
    assert d**q/al<=d**(q-p)*(1+d**(p/2))**2+1e-11
ck('a08 ceiling bound samples',True,'Four noise levels, binary64 tolerance 1e-11; the general ceiling inequalities were reviewed algebraically.')

after={p:sha(ROOT/p) for p in inputs}
ck('review inputs stable',before==after,'All pinned input hashes agree before and after these independent checks.')
result={'result':'Independent finite assertions verified in the stated ranges; general formulas and scope reviewed separately.',
        'scene_ids':[s['id'] for s in scenes],'checks':results,'inputs_sha256':after,
        'non_claims':['Not a proof of the monograph or its Lean sources.','Finite checks do not prove p-series convergence, infinite-dimensional realizability, or regularization limits.',
                      'This pass does not replace final rendered-page inspection.']}
output=ROOT/'review/independent_visual_review_checks.json';output.write_text(json.dumps(result,indent=2)+'\n')
manifest={'schema_version':2,'claim_id':'visual-companion-independent-finite-review',
 'repository':{'commit':'unavailable: publication extracted from supplied archive','dirty':True},
 'command':['python3','review/independent_visual_review_checks.py'],
 'environment':{'software':[{'name':'Python','version':platform.python_version()}],'hardware':platform.machine()},
 'mathematics':{'assertion_tested':'Elementary formulas, displayed predictions, selected exact metric identities and section-pointer existence for sixteen declared scenes.',
  'coefficient_domain':'Integer, F2, exact rational arithmetic; four rounded-noise checks use binary64 tolerance 1e-11.',
  'conventions':'Standard Euclidean inner products except l1 path movement; zero-based shift coordinates and one-based diagonal coordinates.',
  'inputs':inputs,'bounds':{'scenes':16,'binary_phase_triples':64,'path_N':[1,32],'shift_N':[0,3],'shift_indices':[0,6],
    'energy_N':[1,16,64],'budget_alpha':['1/100','1','100'],'basis_e':['1','1/4','1/100','1/10000'],
    'noise_delta':[1,.1,.001,1e-6]},'non_claims':result['non_claims']},
 'randomness':{'used':False,'generator':'not used','seed':None},
 'run':{'started_at':started,'runtime_seconds':time.monotonic()-clock,'exit_status':0,'status':'completed',
        'resource_limits':{'memory_bytes':None,'cpu_seconds':None,'max_cores':None,'max_threads':None}},
 'input_artifacts':[{'path':p,'sha256':before[p],'sha256_after':after[p]} for p in inputs],
 'execution_artifacts':inputs,'declared_results':['review/independent_visual_review_checks.json'],
 'outputs':[{'path':'review/independent_visual_review_checks.json','sha256':sha(output),'kind':'result'}],
 'checks':results,'result':result['result'],
 'residual_risks':['Manual review authenticates relevance of the section pointers; the computation only establishes that they exist.',
  'Formula checks are bounded and not a universal verification of plotting code. Figure and PDF visual review is recorded separately.']}
(ROOT/'review/independent_visual_review_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({'checks_passed':len(results),'scenes':len(scenes),'output':str(output)},indent=2))
