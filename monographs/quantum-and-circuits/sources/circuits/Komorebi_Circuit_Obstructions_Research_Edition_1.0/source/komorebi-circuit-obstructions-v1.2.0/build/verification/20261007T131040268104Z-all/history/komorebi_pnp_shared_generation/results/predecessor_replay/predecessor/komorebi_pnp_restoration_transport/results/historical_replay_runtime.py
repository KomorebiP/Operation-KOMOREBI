from itertools import product
import random, json

def eval_gate(g, vals):
    op,*args=g
    if op=='AND': return vals[args[0]] & vals[args[1]]
    if op=='OR': return vals[args[0]] | vals[args[1]]
    if op=='NOT': return 1 ^ vals[args[0]]
    raise ValueError(op)

def eval_circuit(n,gates,x):
    vals=list(x)
    for g in gates:
        vals.append(eval_gate(g,vals))
    return vals[-1] if gates else vals[-1]

def reversible_compile(n,gates):
    # wires: original inputs 0..n-1, one fresh wire per source gate, output wire last.
    ops=[]
    sigwire=list(range(n))
    nextwire=n
    gate_out=[]
    for gi,g in enumerate(gates):
        op,*args=g
        # source args index signals among input+prior gate outputs
        def wire_of(idx):
            if idx<n: return idx
            return gate_out[idx-n]
        t=nextwire; nextwire+=1
        if op=='AND':
            a,b=map(wire_of,args); ops.append(('TOF',a,b,t))
        elif op=='OR':
            a,b=map(wire_of,args); ops += [('CNOT',a,t),('CNOT',b,t),('TOF',a,b,t)]
        elif op=='NOT':
            a=wire_of(args[0]); ops += [('NOT',t),('CNOT',a,t)]
        gate_out.append(t)
    outwire=nextwire; nextwire+=1
    compute=list(ops)
    if gates:
        ops.append(('CNOT',gate_out[-1],outwire))
    else:
        ops.append(('CNOT',n-1,outwire))
    def inv(op): return op # all chosen gates involutions
    ops += [inv(op) for op in reversed(compute)]
    return ops, nextwire

def apply_rev(ops,state):
    s=list(state)
    for op in ops:
        typ=op[0]
        if typ=='NOT': s[op[1]] ^= 1
        elif typ=='CNOT': s[op[2]] ^= s[op[1]]
        elif typ=='TOF': s[op[3]] ^= s[op[1]] & s[op[2]]
        else: raise ValueError(typ)
    return tuple(s)

def exists_elim(table,n,i):
    # table dict tuple->bit; return on n-1 vars in natural order without i
    out={}
    keep=[j for j in range(n) if j!=i]
    for y in product([0,1], repeat=n-1):
        x0=[0]*n; x1=[0]*n
        for jj,v in zip(keep,y): x0[jj]=x1[jj]=v
        x1[i]=1
        out[y]=table[tuple(x0)]|table[tuple(x1)]
    return out

def k_control_ops(k):
    # inputs 0..k-1, ancillas k..2k-3 (k-2 anc), output 2k-2
    if k==1: return [('CNOT',0,1)],2
    if k==2: return [('TOF',0,1,2)],3
    anc=list(range(k,2*k-2))
    out=2*k-2
    ops=[]
    ops.append(('TOF',0,1,anc[0]))
    for j in range(2,k-1):
        ops.append(('TOF',anc[j-2],j,anc[j-1]))
    ops.append(('TOF',anc[-1],k-1,out))
    # uncompute anc chain
    for j in reversed(range(2,k-1)):
        ops.append(('TOF',anc[j-2],j,anc[j-1]))
    ops.append(('TOF',0,1,anc[0]))
    return ops,out+1

random.seed(7)
report={}
# random circuit reversible checks
cases=0
max_ratio=0
for n in range(2,5):
    for s in range(1,8):
        for rep in range(30):
            gates=[]
            total=n
            for _ in range(s):
                op=random.choice(['AND','OR','NOT'])
                if op=='NOT':
                    a=random.randrange(total); g=(op,a)
                else:
                    a=random.randrange(total); b=random.randrange(total); g=(op,a,b)
                gates.append(g); total+=1
            rops,N=reversible_compile(n,gates)
            assert len(rops) <= 6*s+1
            max_ratio=max(max_ratio,len(rops)/(s or 1))
            for x in product([0,1], repeat=n):
                st=tuple(x)+(0,)*(N-n)
                end=apply_rev(rops,st)
                f=eval_circuit(n,gates,x)
                # gate ancillas restored, last is output
                assert end[:n]==tuple(x)
                assert all(v==0 for v in end[n:-1])
                assert end[-1]==f
                cases+=1
report['reversible_random_input_checks']=cases
report['max_reversible_ops_per_source_gate_observed']=max_ratio
# exact existential commutation all truth tables n<=4
comm=0
for n in range(2,5):
    m=1<<n
    for mask in range(1<<m):
        table={x:(mask>>sum(bit<<j for j,bit in enumerate(x)))&1 for x in product([0,1], repeat=n)}
        # only test pair 0,1; after eliminate 0, original 1 becomes index0
        e0=exists_elim(table,n,0)
        e01=exists_elim(e0,n-1,0)
        e1=exists_elim(table,n,1)
        e10=exists_elim(e1,n-1,0)
        assert e01==e10
        comm+=1
report['existential_commutation_truth_tables']=comm
# k-control exact checks
kc=[]
for k in range(2,9):
    ops,N=k_control_ops(k)
    for x in product([0,1], repeat=k):
        st=tuple(x)+(0,)*(N-k)
        end=apply_rev(ops,st)
        assert end[:k]==tuple(x)
        assert all(v==0 for v in end[k:-1])
        assert end[-1]==int(all(x))
    kc.append({'k':k,'gates':len(ops),'expected':2*k-3})
report['k_control']=kc
print(json.dumps(report,indent=2))
open('/mnt/data/komorebi_pnp_restoration_transport/results/predecessor_replay.json','w').write(json.dumps(report,indent=2)+'\n')
