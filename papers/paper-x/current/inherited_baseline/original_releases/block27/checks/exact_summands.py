"""Exact bounded audit of averaging and idempotent correction in finite carriers.

No floats or external algebra packages. Matrices act on column vectors; groups
and carriers exist over Z before reduction. Results concern only the enumerated
or seeded inputs, and finite quotient idempotents, not a universal lifting proof.
"""
from fractions import Fraction
from itertools import permutations, product
from pathlib import Path
import argparse
import hashlib
import json
import platform
import random

ROOT = Path(__file__).resolve().parents[1]
SEED = 180091


def need(ok, message):
    if not ok:
        raise AssertionError(message)


def eye(n):
    return tuple(int(i == j) for i in range(n) for j in range(n))


def add(a, b):
    return tuple(x + y for x, y in zip(a, b))


def sub(a, b):
    return tuple(x - y for x, y in zip(a, b))


def scale(c, a):
    return tuple(c * x for x in a)


def mul(a, b, n):
    if n == 2:
        return (a[0]*b[0] + a[1]*b[2], a[0]*b[1] + a[1]*b[3],
                a[2]*b[0] + a[3]*b[2], a[2]*b[1] + a[3]*b[3])
    return tuple(sum(a[i*n+k] * b[k*n+j] for k in range(n))
                 for i in range(n) for j in range(n))


def mod(a, q):
    return tuple(x % q for x in a)


def vanishes(a, q):
    return all(x % q == 0 for x in a)


def congruent(a, b, p, k):
    return all(Fraction(x-y).denominator % p != 0 and
               Fraction(x-y).numerator % p**k == 0 for x, y in zip(a, b))


def residual(a, p, depth):
    q = p**depth
    need(all(Fraction(x).denominator % p != 0 for x in a), 'nonintegral average')
    return tuple((Fraction(x).numerator * pow(Fraction(x).denominator, -1, q)) % q
                 for x in a)


def defect(a, n):
    return sub(mul(a, a, n), a)


def average(a, action, inverses, n):
    total = (0,) * (n*n)
    for r, ri in zip(action, inverses):
        total = add(total, mul(mul(r, a, n), ri, n))
    return scale(Fraction(1, len(action)), total)


def validate_group(action, n):
    need(len(set(action)) == len(action), 'test action must be faithful')
    identity = eye(n)
    need(identity in action, 'missing identity')
    lookup = set(action)
    for a in action:
        for b in action:
            need(mul(a, b, n) in lookup, 'not closed over Z')
    inverses = tuple(next(b for b in action if mul(a, b, n) == identity) for a in action)
    need(all(mul(b, a, n) == identity for a, b in zip(action, inverses)), 'inverse side')
    return inverses


def s3():
    # Basis e0-e2, e1-e2 in the permutation representation's sum-zero lattice.
    out = []
    for g in permutations(range(3)):
        cols = []
        for j in (0, 1):
            v = [0, 0, 0]
            v[g[j]] += 1
            v[g[2]] -= 1
            cols.append(v[:2])
        out.append((cols[0][0], cols[1][0], cols[0][1], cols[1][1]))
    need(any(mul(a,b,2) != mul(b,a,2) for a in out for b in out), 'S3 must not commute')
    return tuple(out)


def valuation(x, p):
    need(x > 0, 'valuation input must be positive')
    count = 0
    while x % p == 0:
        count += 1
        x //= p
    return count


def correct(a, action, inverses, p, k, n, depth):
    e = valuation(len(action), p)
    q = p**(e+k)
    need(vanishes(defect(a, n), q), 'input not an idempotent at required precision')
    need(all(vanishes(sub(mul(r,a,n),mul(a,r,n)), q) for r in action), 'input not equivariant')
    averaged = average(a, action, inverses, n)
    need(congruent(averaged, a, p, k), 'averaging lost more than e digits')
    need(all(mul(r,averaged,n) == mul(averaged,r,n) for r in action), 'exact average not equivariant')
    x = residual(averaged, p, depth)
    modulus = p**depth
    precision = min(k, depth)
    iterations = 0
    first_was_idempotent = defect(averaged,n) == (0,) * (n*n)
    while precision < depth:
        need(vanishes(defect(x,n), p**precision), 'initial defect precision')
        x2 = mul(x,x,n)
        y = mod(sub(scale(3,x2),scale(2,mul(x2,x,n))),modulus)
        d = defect(x,n)
        # Independent exact polynomial factorization of the new defect.
        expected = mul(mul(d,d,n),sub(scale(4,d),scale(3,eye(n))),n)
        need(vanishes(sub(defect(y,n),expected),modulus), 'Newton defect identity')
        need(vanishes(sub(y,x),p**precision), 'Newton changed retained precision')
        precision = min(2*precision,depth)
        need(vanishes(defect(y,n),p**precision), 'Newton defect did not double')
        x = y
        iterations += 1
    need(vanishes(defect(x,n),modulus), 'final finite idempotence')
    need(all(vanishes(sub(mul(r,x,n),mul(x,r,n)),modulus) for r in action), 'final equivariance')
    need(congruent(x,a,p,k), 'final retained matrix')
    return x, iterations, first_was_idempotent


def splitting_check(x, p, n):
    """Exhaust all vectors modulo p^2, independently enumerate image and kernel."""
    q = p**2
    x = mod(x,q)
    vectors = tuple(product(range(q),repeat=n))
    def act(a,v):
        return tuple(sum(a[i*n+j]*v[j] for j in range(n))%q for i in range(n))
    im = {act(x,v) for v in vectors}
    ker = {v for v in vectors if act(x,v) == (0,)*n}
    need(im & ker == {(0,)*n}, 'image/kernel intersect nontrivially')
    need(len(im)*len(ker) == q**n, 'image/kernel sizes do not multiply')
    complement = sub(eye(n),x)
    for v in vectors:
        u,w = act(x,v),act(complement,v)
        need(u in im and w in ker and tuple((a+b)%q for a,b in zip(u,w)) == v,
             'idempotent splitting reconstruction')
    return len(vectors)


def exhaustive_family(label,action,p,k):
    inverses = validate_group(action,2)
    e = valuation(len(action),p)
    q = p**(e+k)
    depth = max(8,e+k+3)
    tested = equivariant = admissible = corrected = steps = splitting_vectors = non_idempotent_averages = 0
    for a in product(range(q),repeat=4):
        tested += 1
        if not all(vanishes(sub(mul(r,a,2),mul(a,r,2)),q) for r in action):
            continue
        equivariant += 1
        if not vanishes(defect(a,2),q):
            continue
        admissible += 1
        for delta in ((0,0,0,0),(1,-2,3,-1)):
            lifted = add(a,scale(q,delta))
            x,iters,was_idempotent = correct(lifted,action,inverses,p,k,2,depth)
            corrected += 1
            steps += iters
            non_idempotent_averages += not was_idempotent
            if admissible <= 4 and delta == (0,0,0,0):
                splitting_vectors += splitting_check(x,p,2)
    need(tested == q**4,'exhaustive matrix count mismatch')
    return dict(family=label,rank=2,p=p,group_order=len(action),e=e,k=k,
                input_depth=e+k,input_modulus=q,target_depth=depth,
                all_matrices_enumerated=tested,equivariant_matrices=equivariant,
                equivariant_idempotents=admissible,integral_lifts_corrected=corrected,
                newton_iterations=steps,non_idempotent_exact_averages=non_idempotent_averages,
                finite_splitting_vectors_enumerated=splitting_vectors)


def rank_three_samples():
    rng = random.Random(SEED)
    # Fixed unimodular basis mixing all three character lines.
    w=(1,1,0,0,1,1,0,0,1)
    wi=(1,-1,1,0,1,-1,0,0,1)
    need(mul(w,wi,3)==eye(3),'frame inverse')
    diagonal=tuple((1,0,0,0,s,0,0,0,t) for s,t in product((-1,1),repeat=2))
    action=tuple(mul(mul(w,r,3),wi,3) for r in diagonal)
    inverses=validate_group(action,3)
    records=[]
    for k in (1,2,3):
        e=2
        q=2**(e+k)
        count=steps=non_idempotent=0
        for mask in product((0,1),repeat=3):
            d=tuple(mask[i] if i==j else 0 for i in range(3) for j in range(3))
            for _ in range(6):
                i,j=rng.sample(range(3),2)
                elementary=tuple(int(a==i and b==j) for a in range(3) for b in range(3))
                u=add(eye(3),scale(2**(e+k-1),elementary))
                ui=sub(eye(3),scale(2**(e+k-1),elementary))
                perturbed=mul(mul(u,d,3),ui,3)
                need(defect(perturbed,3)==(0,)*9,'sample seed projector')
                a=mul(mul(w,perturbed,3),wi,3)
                a=add(a,scale(q,tuple(rng.randint(-3,3) for _ in range(9))))
                x,iters,was_idempotent=correct(a,action,inverses,2,k,3,10)
                count+=1
                steps+=iters
                non_idempotent+=not was_idempotent
        need(count==48,'seeded sample count')
        records.append(dict(family='Klein four, three integral characters, mixed basis',
                            rank=3,p=2,group_order=4,e=e,k=k,input_depth=e+k,
                            input_modulus=q,target_depth=10,seeded_constructed_samples=count,
                            newton_iterations=steps,non_idempotent_exact_averages=non_idempotent))
    return records


def repeated_s3_samples():
    rng = random.Random(SEED+1)
    n=4
    upper=tuple(int(j==i+1) for i in range(n) for j in range(n))
    w=add(eye(n),upper)
    upper2=mul(upper,upper,n)
    wi=sub(add(sub(eye(n),upper),upper2),mul(upper2,upper,n))
    need(mul(w,wi,n)==eye(n),'rank-four frame inverse')
    base=tuple(tuple(r[(i%2)*2+j%2] if i//2==j//2 else 0
                     for i in range(n) for j in range(n)) for r in s3())
    action=tuple(mul(mul(w,r,n),wi,n) for r in base)
    inverses=validate_group(action,n)
    need(any(mul(a,b,n)!=mul(b,a,n) for a in action for b in action),
         'rank-four S3 action must remain noncommutative')
    records=[]
    for p,k in product((2,3,5),(1,2)):
        e=valuation(6,p)
        q=p**(e+k)
        count=steps=non_idempotent=0
        for _ in range(12):
            # A genuine rank-two projector in the direct sum of two standard carriers.
            d=tuple(int(i==j and i<2) for i in range(n) for j in range(n))
            shear=tuple(int(i<2 and j==i+2) for i in range(n) for j in range(n))
            t=rng.choice((-3,-2,-1,1,2,3))
            u=add(eye(n),scale(t,shear))
            ui=sub(eye(n),scale(t,shear))
            a=mul(mul(w,mul(mul(u,d,n),ui,n),n),wi,n)
            need(defect(a,n)==(0,)*(n*n),'repeated carrier seed idempotence')
            need(all(mul(r,a,n)==mul(a,r,n) for r in action),'repeated carrier seed equivariance')
            a=add(a,scale(q,tuple(rng.randint(-3,3) for _ in range(n*n))))
            x,iters,was_idempotent=correct(a,action,inverses,p,k,n,8)
            # Trace detects the rank-two residue, excluding scalar endpoints.
            need(sum(x[i*n+i] for i in range(n))%p**8==2,'corrected projector rank-two trace')
            count+=1
            steps+=iters
            non_idempotent+=not was_idempotent
        records.append(dict(family='S3, two copies of sum-zero lattice, mixed basis',
                            rank=n,p=p,group_order=6,e=e,k=k,input_depth=e+k,
                            input_modulus=q,target_depth=8,seeded_constructed_samples=count,
                            newton_iterations=steps,non_idempotent_exact_averages=non_idempotent,
                            corrected_trace_mod_target=2))
    return records


def boundary_checks():
    action=(eye(2),(1,0,0,-1))
    inverses=validate_group(action,2)
    b=(1,1,0,0)
    need(defect(b,2)==(0,0,0,0),'boundary B idempotence')
    need(all(vanishes(sub(mul(r,b,2),mul(b,r,2)),2) for r in action),'boundary mod2 equivariance')
    lifts=[add(b,scale(2,v)) for v in product((0,1),repeat=4)]
    equivariant=sum(all(vanishes(sub(mul(r,a,2),mul(a,r,2)),4) for r in action) for a in lifts)
    need(equivariant==0,'mod2 no-lift boundary must fail already mod4')
    naive_average=average(b,action,inverses,2)
    need(not congruent(naive_average,b,2,1),'naive average must lose mod2 matrix')
    # An exactly idempotent integral matrix whose exact group average is not idempotent.
    a=(4,2,-6,-3)
    need(defect(a,2)==(0,0,0,0),'non-idempotent averaging example starts idempotent')
    need(all(vanishes(sub(mul(r,a,2),mul(a,r,2)),4) for r in action),'example not equivariant mod4')
    averaged=average(a,action,inverses,2)
    need(averaged==(4,0,0,-3) and defect(averaged,2)==(12,0,0,12),'averaging boundary value')
    corrected,iters,_=correct(a,action,inverses,2,1,2,10)
    need(corrected==(0,0,0,1),'Newton correction boundary endpoint')
    return dict(insufficient_precision=dict(p=2,group_order=2,e=1,
                    B_mod2=list(b),lifts_mod4_exhausted=len(lifts),equivariant_lifts_mod4=equivariant,
                    conclusion='No integral equivariant lift preserving B mod2, already obstructed mod4.'),
                average_not_idempotent=dict(A=list(a),exact_average=[str(x) for x in averaged],
                    exact_average_defect=[12,0,0,12],corrected_mod1024=list(corrected),
                    iterations=iters,conclusion='Averaging alone does not preserve idempotence, even for an exact input idempotent.'))


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,default=ROOT/'exact_summands.json')
    args=parser.parse_args()
    c2=(eye(2),(1,0,0,-1))
    c4=(eye(2),(0,-1,1,0),(-1,0,0,-1),(0,1,-1,0))
    specs=[('C2 split',c2,2,k) for k in (1,2,3)]
    specs += [('C2 split',c2,3,k) for k in (1,2)]
    specs += [('S3 sum-zero lattice',s3(),p,1) for p in (2,3,5)]
    specs += [('C4 rotation lattice',c4,2,k) for k in (1,2)]
    exhaustive=[exhaustive_family(*spec) for spec in specs]
    rank_three=rank_three_samples()
    rank_four=repeated_s3_samples()
    sampled=rank_three+rank_four
    boundary=boundary_checks()
    totals=dict(exhaustive_families=len(exhaustive),
                quotient_matrices_enumerated=sum(r['all_matrices_enumerated'] for r in exhaustive),
                equivariant_quotient_matrices=sum(r['equivariant_matrices'] for r in exhaustive),
                equivariant_quotient_idempotents=sum(r['equivariant_idempotents'] for r in exhaustive),
                integral_lifts_from_exhaustive_families=sum(r['integral_lifts_corrected'] for r in exhaustive),
                seeded_rank_three_samples=sum(r['seeded_constructed_samples'] for r in rank_three),
                seeded_rank_four_samples=sum(r['seeded_constructed_samples'] for r in rank_four),
                correction_cases=sum(r['integral_lifts_corrected'] for r in exhaustive)+sum(r['seeded_constructed_samples'] for r in sampled)+1,
                newton_iterations=sum(r['newton_iterations'] for r in exhaustive)+sum(r['newton_iterations'] for r in sampled)+boundary['average_not_idempotent']['iterations'],
                finite_splitting_vectors=sum(r['finite_splitting_vectors_enumerated'] for r in exhaustive))
    report=dict(status='PASS: finite assertion verified in stated range',
                schema_version=1,python=platform.python_version(),
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                coefficient_domain='Exact Z and Q; p-integral fractions reduced modulo p^d by unit inversion.',
                convention='Column-vector actions; averaging sum rho(g) A rho(g)^(-1); Newton 3A^2-2A^3.',
                randomness=dict(used=True,generator='Python random.Random (MT19937)',seeds=[SEED,SEED+1]),
                exhaustive=exhaustive,constructed_samples=sampled,boundaries=boundary,totals=totals,
                non_claims=['Does not prove general lifting, convergence in Z_p, or Lean kernel correctness.',
                            'Finite Newton endpoints are exact idempotents only in the stated quotient rings.',
                            'Does not identify arithmetic packets, Weil-Deligne attachments, or Hodge-Tate data.',
                            'Constructed rank-three and rank-four samples do not exhaust all quotient idempotents.'])
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2)+'\n')
    need(json.loads(args.output.read_text())==report,'JSON serialization roundtrip')
    print(json.dumps(dict(status=report['status'],totals=totals),sort_keys=True))


if __name__=='__main__':
    main()
