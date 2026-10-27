#!/usr/bin/env python3
"""Definition-first exact checks for thirteen v0.4 lessons; no author imports.

The formulas being checked were independently implemented before reading the
three new author generators. Finite results supplement the separate elementary
reductions in v04_independent_audit.md; they do not prove universal statements.
"""
from fractions import Fraction as Q
from math import comb, factorial
from pathlib import Path
import argparse
import hashlib
import json
import platform

def conv(a, b):
    if not a or not b:
        return []
    out = [Q(0) for _ in range(len(a) + len(b) - 1)]
    for i, ai in enumerate(a):
        for j, bj in enumerate(b):
            out[i+j] += ai*bj
    return out

def pad(a, n):
    return list(a[:n]) + [Q(0)]*max(0, n-len(a))

def fib_seeds(a, b, n):
    if n == 0:
        return []
    out=[Q(a)]
    if n > 1:
        out.append(Q(b))
    while len(out) < n:
        out.append(out[-1]+out[-2])
    return out

def recurrence(a, b, n):
    out=[Q(a), Q(b)]
    while len(out)<n:
        out.append(3*out[-1]-2*out[-2])
    return out[:n]

def trim(a):
    while len(a)>1 and a[-1] == 0:
        a.pop()
    return a

def bank_apply(channels, u_mat):
    out=[]
    for row in u_mat:
        terms=[conv(poly, stream) for poly,stream in zip(row,channels)]
        n=max(map(len,terms))
        out.append(trim([sum(pad(t,n)[j] for t in terms) for j in range(n)]))
    return out

def stream_fir(data, kernel, chunks, modulus):
    """Unit delay state consists only of K-1 last samples and n mod M."""
    history=[Q(0)]*(len(kernel)-1)
    clock=0
    pos=0
    emitted=[]
    phase_outputs=[[] for _ in range(modulus)]
    snapshots=[]
    def one(value):
        nonlocal history, clock
        y=sum(kernel[k]*(value if k==0 else history[-k]) for k in range(len(kernel)))
        emitted.append(y)
        phase_outputs[clock].append(y)
        history=(history+[value])[-(len(kernel)-1):] if len(kernel)>1 else []
        clock=(clock+1)%modulus
    for length in chunks:
        for value in data[pos:pos+length]:
            one(value)
        pos+=length
        snapshots.append({'consumed':pos,'history':list(history),'phase_clock':clock})
    assert pos==len(data)
    for _ in range(len(kernel)-1):
        one(Q(0))
    return emitted,phase_outputs,snapshots

def serial(obj):
    if isinstance(obj,Q):
        return obj.numerator if obj.denominator==1 else f'{obj.numerator}/{obj.denominator}'
    if isinstance(obj,dict):
        return {k:serial(v) for k,v in obj.items()}
    if isinstance(obj,(list,tuple)):
        return [serial(v) for v in obj]
    return obj

def run():
    records=[]
    def record(id,checks,scope,examples):
        records.append({'id':id,'status':'PASS','assertions':checks,'scope':scope,'examples':serial(examples)})

    # B01: seeds, OGF coefficient comparison, and polynomial cancellation.
    checks=0
    for a in range(-4,5):
        for b in range(-4,5):
            seq=recurrence(a,b,32)
            assert seq==[Q(2*a-b+(b-a)*2**n) for n in range(32)]
            assert pad(conv(seq,[1,-3,2]),32)==[Q(a),Q(b-3*a)]+[Q(0)]*30
            num=[a,b-3*a]
            assert (sum(num)==0)==(b==2*a)
            assert (num[0]+num[1]*Q(1,2)==0)==(b==a)
            checks+=4
    record('B01',checks,'81 integral seed pairs; 32 recurrence coefficients; exact evaluations at 1 and 1/2',
           {'a=b=1':recurrence(1,1,8),'a=1,b=2':recurrence(1,2,8),'a=1,b=3':recurrence(1,3,8)})

    # B02: same transfer polynomial modulo the Fibonacci annihilator.
    f=fib_seeds(0,1,32)
    d=[1,-1,-1]
    h=[1,2,1]
    hf=pad(conv(h,f),32)
    reduced=[2*f[n]+(f[n-1] if n else 0)-(1 if n==1 else 0) for n in range(32)]
    assert hf==reduced
    assert pad(conv(d,f),32)==[Q(0),Q(1)]+[Q(0)]*30
    assert [2,1,0]==[h[k]+d[k] for k in range(3)]
    # For arbitrary seeds, the boundary numerator is a+(b-a)z.
    for a in range(-3,4):
        for b in range(-3,4):
            x=fib_seeds(a,b,32)
            boundary=[Q(a),Q(b-a)]+[Q(0)]*30
            assert pad(conv(d,x),32)==boundary
            assert pad(conv(h,x),32)==[2*x[n]+(x[n-1] if n else 0)-boundary[n] for n in range(32)]
    record('B02',101,'32 coefficients, Fibonacci seed and 49 arbitrary seed pairs; causally retained seed residual',
           {'FIR_h':h,'D':d,'hF_first8':hf[:8],'D_F_first8':pad(conv(d,f),8)})

    # B03: formal reciprocal all r; exact finite l1 partial sums do not decide stability.
    checks=0
    examples={}
    for r in [Q(-2),Q(-1),Q(-1,2),Q(0),Q(1,2),Q(1),Q(2)]:
        g=[r**n for n in range(24)]
        assert pad(conv([1,-r],g),24)==[Q(1)]+[Q(0)]*23
        checks+=1
        if r in [Q(1,2),Q(2)]:
            sums=[sum(abs(r**n) for n in range(N)) for N in [1,2,4,8]]
            assert sums==([Q(1),Q(3,2),Q(15,8),Q(255,128)] if r==Q(1,2) else [Q(1),Q(3),Q(15),Q(255)])
            examples[str(r)]={'g_first8':g[:8],'l1_partial_sums_N1_2_4_8':sums}
    record('B03',checks+2,'7 exact rational r; 24 coefficients; partial sums at N=1,2,4,8',examples)

    # B04: central-binomial coefficient division, formal integration and Catalan equation.
    B=[Q(comb(2*n,n)) for n in range(25)]
    C=[B[n]/(n+1) for n in range(25)]
    assert all(c.denominator==1 for c in C)
    CC=conv(C,C)
    assert C[0]==1 and all(C[n]==CC[n-1] for n in range(1,25))
    assert all((n+1)*C[n]==B[n] for n in range(25))
    record('B04',75,'degrees 0..24 over Q; integrality, integrated coefficients, Catalan convolution',
           {'central_binomial':B[:8],'Catalan':C[:8]})

    # O01: N(a)_n=a_n/n!: N^-1 H N and N H N^-1 are distinct conjugations.
    checks=0
    kernels=[[1,-1],[2,3,-1],[0,1],[1,0,0,-2]]
    basis_vectors=[]
    for j in range(12):
        basis_vectors.append([Q(int(n==j)) for n in range(16)])
    basis_vectors.append([Q((-1)**n*(n*n+1)) for n in range(16)])
    for raw in basis_vectors:
        tay=[raw[n]/factorial(n) for n in range(16)]
        for kernel in kernels:
            target_count=[factorial(n)*pad(conv(kernel,tay),16)[n] for n in range(16)]
            weighted_count=[sum(kernel[k]*Q(factorial(n),factorial(n-k))*raw[n-k]
                               for k in range(min(n,len(kernel)-1)+1)) for n in range(16)]
            assert target_count==weighted_count
            target_taylor=[pad(conv(kernel,raw),16)[n]/factorial(n) for n in range(16)]
            weighted_taylor=[sum(kernel[k]*Q(factorial(n-k),factorial(n))*tay[n-k]
                                for k in range(min(n,len(kernel)-1)+1)) for n in range(16)]
            assert target_taylor==weighted_taylor
            checks+=2
    exp_counts=[Q(1)]*16
    exp_taylor=[Q(1,factorial(n)) for n in range(16)]
    exp_pullback=[factorial(n)*pad(conv([1,-1],exp_taylor),16)[n] for n in range(16)]
    assert exp_pullback==[Q(1-n) for n in range(16)]
    record('O01',checks+1,'13 exact vectors (12 basis vectors plus one signed polynomial) x 4 FIR kernels; 16 coefficients; both conjugation directions',
           {'exp_counts_input':exp_counts[:8],'Taylor_H=1-z_count_pullback':exp_pullback[:8]})

    # O02: Bernoulli translation is argument shift, not sequence delay.
    def B4(x):
        return x**4-2*x**3+x**2-Q(1,30)
    checks=0
    for x in [Q(n,3) for n in range(-15,16)]:
        assert B4(x+1)-B4(x)==4*x**3
        checks+=1
    S=[]
    for N in range(25):
        anti=(B4(Q(N))-B4(Q(0)))/4
        assert anti==sum(Q(k**3) for k in range(N))
        assert anti==Q((N*(N-1)//2)**2)
        S.append(anti)
        checks+=2
    record('O02',checks,'31 rational translation arguments; sums N=0..24; exact polynomial antiderivative and cube sum',
           {'S_N0_5':S[:6],'jumps_k0_4':[k**3 for k in range(5)]})

    # O03: causal truncated difference versus four-periodic difference.
    checks=0
    for v in basis_vectors[:4]+[[Q(-2),Q(5),Q(0),Q(3)]]:
        x=v[:4]
        causal=[x[n]-(x[n-1] if n else 0) for n in range(4)]
        assert [sum(causal[:n+1]) for n in range(4)]==x
        periodic=[x[n]-x[(n-1)%4] for n in range(4)]
        assert sum(periodic)==0
        checks+=2
    for c in range(-3,4):
        assert [Q(c)-Q(c) for _ in range(4)]==[0]*4
        checks+=1
    for a in range(-2,3):
        for b in range(-2,3):
            for c in range(-2,3):
                y=[Q(a),Q(b),Q(c),Q(-a-b-c)]
                x=[Q(0),Q(b),Q(b+c),Q(-a)]
                assert [x[n]-x[(n-1)%4] for n in range(4)]==y
                checks+=1
    # Full finite causal difference retains a final tail and sums to zero.
    assert conv([1,-1],[1,1,1,1])==[1,0,0,0,-1]
    record('O03',checks+1,'4-prefix causal and periodic spaces; 125 zero-sum targets; explicit terminal tail',
           {'causal_prefix_delta_of_ones':[1,0,0,0],'full_zero_extended_delta_of_ones':[1,0,0,0,-1],'periodic_delta_of_ones':[0,0,0,0]})

    # C01: finite P8: seed defect and both terminal defects are retained.
    p8=fib_seeds(0,1,8)
    residual=conv(d,p8)
    assert residual==[0,1,0,0,0,0,0,0,-21,-13]
    # All prefix lengths >=2, not just eight, have this symbolic boundary pattern.
    for N in range(2,25):
        x=fib_seeds(0,1,N)
        expect=[Q(0)]*(N+2)
        expect[1]=1
        expect[N]=-(x[-1]+x[-2])
        expect[N+1]=-x[-1]
        assert conv(d,x)==expect
    record('C01',24,'P8 and every Fibonacci prefix length 2..24; complete FIR tails',
           {'P8':p8,'A_P8':residual})

    # C02: three-phase matrix independently formed from channel delay definition.
    bank=[[[1],[0,-1],[0,-1]],[[-1],[1],[0,-1]],[[-1],[-1],[1]]]
    phases=[p8[r::3] for r in range(3)]
    bank_res=bank_apply(phases,bank)
    direct=[trim(residual[r::3]) for r in range(3)]
    assert bank_res==direct
    checks=1
    for N in range(1,33):
        x=[Q((-1)**n*(n+1)) for n in range(N)]
        out=conv(d,x)
        assert bank_apply([x[r::3] for r in range(3)],bank)==[trim(out[r::3]) for r in range(3)]
        checks+=1
    record('C02',checks,'all input lengths 1..32 plus P8; exact polynomial matrix and full causal tails',
           {'phase_inputs':phases,'A(C3)':bank,'phase_residuals':bank_res})

    # C03: one-sample perturbation residual stencil is causal and local.
    perturbed=list(p8)
    perturbed[5]+=1
    pert_res=conv(d,perturbed)
    difference=[a-b for a,b in zip(pert_res,residual)]
    assert difference==[0,0,0,0,0,1,-1,-1,0,0]
    for j in range(16):
        impulse=[Q(0)]*18
        impulse[j]=1
        expected=[Q(0)]*20
        expected[j:j+3]=d
        assert conv(d,impulse)==expected
    record('C03',17,'P8 perturbation x5+=1 and impulse positions 0..15',
           {'perturbed':perturbed,'residual_change':difference})

    # C04: no generic even-only closure for E A; witness is delta1.
    witness=[0,1,0,0,0,0,0,0]
    witness_res=conv(d,witness)
    assert witness[::2]==[0,0,0,0]
    assert witness_res[::2]==[0,-1,0,0,0]
    assert [a+b for a,b in zip(p8,witness)][::2]==p8[::2]
    assert conv(d,[a+b for a,b in zip(p8,witness)])[::2]!=residual[::2]
    bank2=[[[1,-1],[0,-1]],[[-1],[1,-1]]]
    assert bank_apply([p8[0::2],p8[1::2]],bank2)==[trim(residual[0::2]),trim(residual[1::2])]
    assert perturbed[::2]==p8[::2]
    assert pert_res[::2]==[0,0,0,-1,-21]
    assert residual[::2]==[0,0,0,0,-21]
    record('C04',8,'delta1 smallest omitted-channel witness; P8 plus x5 perturbation pair; exact two-phase dependence',
           {'witness_even':witness[::2],'E_A_witness':witness_res[::2],'A(C2)':bank2,
            'P8_even_output':residual[::2],'Q_even_output':pert_res[::2]})

    # C05: model repair is unique under recurrence and only when even data agree.
    checks=0
    for a in range(-4,5):
        for b in range(-4,5):
            x=fib_seeds(a,b,8)
            e=x[::2]
            a_hat=e[0]
            b_hat=e[1]-e[0]
            assert (a_hat,b_hat)==(Q(a),Q(b))
            assert e[2]==3*e[1]-e[0] and e[3]==3*e[2]-e[1]
            assert fib_seeds(a_hat,b_hat,8)==x
            checks+=3
            for pos in [2,3]:
                for increment in [-1,1]:
                    bad=list(e)
                    bad[pos]+=increment
                    assert not (bad[2]==3*bad[1]-bad[0] and bad[3]==3*bad[2]-bad[1])
                    checks+=1
    wrong=list(p8[::2]); wrong[2]+=1
    assert wrong[2]!=3*wrong[1]-wrong[0]
    record('C05',checks+1,'81 seed pairs; exact repair and 2 consistency equations; 324 rejected E2/E3 +/-1 perturbations plus one displayed inconsistent vector',
           {'P8_even':p8[::2],'reconstructed_seeds':[0,1],'inconsistent_even':wrong})

    # C06: chunks preserve two-sample state and three-phase clock, then flush2.
    emitted,phase_outputs,snapshots=stream_fir(p8,d,[2,3,3],3)
    assert emitted==residual
    assert [trim(y) for y in phase_outputs]==direct
    assert snapshots==[{'consumed':2,'history':[Q(0),Q(1)],'phase_clock':2},
                       {'consumed':5,'history':[Q(2),Q(3)],'phase_clock':2},
                       {'consumed':8,'history':[Q(8),Q(13)],'phase_clock':2}]
    checks=3
    # Independent cut-set enumeration, unlike the author's recursive composition iterator.
    partitions=0
    for mask in range(1<<7):
        cuts=[0]+[j for j in range(1,8) if mask & (1<<(j-1))]+[8]
        sizes=[b-a for a,b in zip(cuts,cuts[1:])]
        y,streams,states=stream_fir(p8,d,sizes,3)
        assert y==residual
        assert streams==[residual[r::3] for r in range(3)]
        assert states[-1]['history']==[8,13] and states[-1]['phase_clock']==2
        checks+=3
        partitions+=1
    assert partitions==128
    checks+=1
    for N in range(1,33):
        x=[Q((n*n+3*n)%11-5) for n in range(N)]
        for chunk in range(1,8):
            sizes=[chunk]*(N//chunk)+([N%chunk] if N%chunk else [])
            y,streams,_=stream_fir(x,d,sizes,3)
            target=conv(d,x)
            assert y==target
            assert [trim(s) for s in streams]==[trim(target[r::3]) for r in range(3)]
            checks+=2
    record('C06',checks,'P8 chunks(2,3,3); all128 P8 cut-set partitions; lengths1..32 and chunk sizes1..7; history2, clockmod3, flush2',
           {'boundary_states':snapshots,'flushed_outputs':emitted,'flushed_phases':phase_outputs})

    return {'status':'PASS','method':'definition-first independent exact implementation; standard library only; no author-generator imports',
            'lesson_contract_families':len(records),'assertion_count':sum(r['assertions'] for r in records),
            'domain':'Z and Q exact arithmetic; polynomial convolutions; causal zero extension; explicitly truncated causal-prefix comparison',
            'records':records,'python':platform.python_version(),
            'non_claims':['The finite tested range is not a universal proof. Universal elementary reductions are recorded separately.',
                          'No Lean certificate or global novelty claim. No numerical stability or signal reconstruction accuracy certificate.']}

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    result=run()
    result['implementation_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(f"PASS: {result['lesson_contract_families']} lesson contracts, {result['assertion_count']} exact assertions")

if __name__=='__main__':
    main()
