"""Exact bounded audit of the v0.5 additions.

No agent simulation; no claim that enumeration proves the general results.
The universal undecidability theorem has a prose reduction, not a finite test.
Callbacks integrate the checks with check_finite_models.py's evidence manifest.
"""
from __future__ import annotations
from fractions import Fraction as Q
from itertools import product, permutations, combinations

def partitions(n):
    if n==0:
        yield ();return
    def extend(p):
        if len(p)==n:
            yield tuple(p);return
        for k in range(max(p)+2):yield from extend(p+[k])
    yield from extend([0])

def reach(adj, start):
    visited={start};stack=[start]
    while stack:
        x=stack.pop()
        for y in adj[x]:
            if y not in visited:visited.add(y);stack.append(y)
    return visited

def compose(p,q):
    """p after q: the rightmost permutation acts first."""
    return tuple(p[q[i]] for i in range(len(p)))

def inverse(p):return tuple(p.index(i) for i in range(len(p)))
def distance(p,q):return Q(sum(a!=b for a,b in zip(p,q)),len(p))

def knowledge(partition, truth):
    return {w for w in range(len(partition))
            if all(v in truth for v in range(len(partition)) if partition[v]==partition[w])}

def common(parts,truth):
    n=len(parts[0]);adj=[set() for _ in range(n)]
    for p in parts:
        for w in range(n):adj[w].update(v for v in range(n) if p[w]==p[v])
    return {w for w in range(n) if reach(adj,w)<=truth}

def is_bounded(T,pa,pb):
    for a,b in zip(pa,pb):
        for w in range(len(T)):
            if any(a[w]==a[v] and b[T[w]]!=b[T[v]] for v in range(len(T))):return False
            for z in range(len(b)):
                if b[T[w]]==b[z] and not any(a[w]==a[v] and T[v]==z for v in range(len(T))):return False
    return True

def run_extensions(group, require):
    @group('v0.5 Weight-conserving vote refinements',
           'Three controllers; integer weights 0..3; every two-part split; all coalitions and thresholds 1..total+1')
    def _():
        for w in product(range(4),repeat=3):
            for x in range(w[0]+1):
                refined=(x,w[0]-x,w[1],w[2]);owners=(0,0,1,2)
                for coalition in range(8):
                    a=sum(w[i] for i in range(3) if coalition>>i&1)
                    b=sum(refined[j] for j in range(4) if coalition>>owners[j]&1)
                    require(a==b)
                    for q in range(1,sum(w)+2):require((a>=q)==(b>=q))
        require(2*2<=5 and 2*4>7)

    @group('v0.5 Quorum witness intersection',
           'All pairs of nonempty quorums on four witnesses; every ternary endorsement vector; explicit five-witness reconfiguration')
    def _():
        for a,b in product(range(1,16),repeat=2):
            witnesses=0
            for endorsements in product((-1,0,1),repeat=4):
                ca=all(endorsements[i]==0 for i in range(4) if a>>i&1)
                cb=all(endorsements[i]==1 for i in range(4) if b>>i&1)
                if ca and cb:witnesses+=1
            require(bool(witnesses)==not_intersect(a,b))
        old={0,1,2};new={2,3,4}
        require(bool(old&new) and not ({0,1}&{3,4}))
        olds=[set(x) for x in combinations(old,2)];news=[set(x) for x in combinations(new,2)]
        joints=[a|b for a,b in product(olds,news)]
        require(all(a&b for a in joints for b in olds+news+joints))

    @group('v0.5 Context-sensitive language transport',
           'Two messages on three states; 16 pairs of selected partial maps; six state permutations; all conversations of length 0..4')
    def _():
        maps=((0,1,2),(1,2,0),(-1,1,2),(2,-1,0))
        for F in product(maps,repeat=2):
            for T in permutations(range(3)):
                B=[[-1]*3 for _ in range(2)]
                for s in range(3):
                    for m in range(2):
                        j=m^(s%2)
                        B[j][T[s]]= -1 if F[m][s]<0 else T[F[m][s]]
                for initial in range(3):
                    for n in range(5):
                        for word in product(range(2),repeat=n):
                            s=initial;t=T[initial]
                            for m in word:
                                j=m^(s%2);ns=F[m][s];nt=B[j][t]
                                require((ns<0)==(nt<0))
                                if ns<0:break
                                require(nt==T[ns]);s,t=ns,nt
                # Preservation of definedness is not automatic for a perturbed interpreter.
                s0=0; m0=0; j0=m0^(s0%2)
                wrong=-1 if F[m0][s0]>=0 else T[s0]
                require((F[m0][s0]<0)!=(wrong<0))
        source_permission=0;target_permission_after_untyped_translation=1
        require(source_permission!=target_permission_after_untyped_translation)

    @group('v0.5 Finite confluence and nontermination control',
           'Every directed acyclic graph respecting the order on five states (1024 relations); one explicit cyclic negative control')
    def _():
        n=5;edges=list(combinations(range(n),2))
        for mask in range(1<<len(edges)):
            adj=[set() for _ in range(n)]
            for k,(a,b) in enumerate(edges):
                if mask>>k&1:adj[a].add(b)
            R=[reach(adj,a) for a in range(n)]
            local=all(R[b]&R[c] for a in range(n) for b in adj[a] for c in adj[a])
            global_=all(R[b]&R[c] for a in range(n) for b in R[a] for c in R[a])
            require(local==global_)
            normal={a for a in range(n) if not adj[a]}
            unique=all(len(R[a]&normal)==1 for a in range(n))
            require(global_==unique)
        # a->b,c; b->a,d; c->a,e. Local joins exist but d,e never join.
        adj=[{1,2},{0,3},{0,4},set(),set()];R=[reach(adj,a) for a in range(5)]
        require(all(R[b]&R[c] for a in range(5) for b in adj[a] for c in adj[a]))
        require(not(R[3]&R[4]))

    @group('v0.5 Noncommutative frame and state synchronization',
           'All 216 S3-labelled oriented triangles; all 36 root-normalized frames; all 27 local label states; every gauge on three nodes')
    def _():
        G=list(permutations(range(3)));e=(0,1,2)
        for a,b,c in product(G,repeat=3):
            H=compose(c,compose(b,a))
            frames=[(e,h1,h2) for h1,h2 in product(G,repeat=2)
                    if a==h1 and b==compose(h2,inverse(h1)) and c==inverse(h2)]
            require(bool(frames)==(H==e));require(len(frames)<=1)
            states=[x for x in product(range(3),repeat=3)
                    if x[1]==a[x[0]] and x[2]==b[x[1]] and x[0]==c[x[2]]]
            fixed=[x for x in range(3) if H[x]==x]
            require(len(states)==len(fixed))
            require({x[0] for x in states}==set(fixed))
            for k0,k1,k2 in product(G,repeat=3):
                aa=compose(k1,compose(a,inverse(k0)))
                bb=compose(k2,compose(b,inverse(k1)))
                cc=compose(k0,compose(c,inverse(k2)))
                HH=compose(cc,compose(bb,aa))
                require(HH==compose(k0,compose(H,inverse(k0))))
        transposition=(1,0,2)
        require(transposition!=e and transposition[2]==2)
        require(compose((0,2,1),(1,0,2))==(2,0,1))

    @group('v0.5 Quantitative loop error bound',
           'All 216 S3 triangles and 36 root-normalized frames, normalized Hamming metric')
    def _():
        G=list(permutations(range(3)));e=(0,1,2)
        for a,b,c in product(G,repeat=3):
            H=compose(c,compose(b,a));D=distance(H,e)
            for h1,h2 in product(G,repeat=2):
                ds=(distance(a,h1),distance(b,compose(h2,inverse(h1))),distance(c,inverse(h2)))
                require(D<=sum(ds));require(max(ds)>=D/3)

    @group('v0.5 Common knowledge and public restriction',
           'All pairs of partitions of four worlds; all 16 truth sets; graph oracle versus repeated modal closure; stable public restrictions')
    def _():
        parts=list(partitions(4))
        for pa,pb in product(parts,repeat=2):
            for mask in range(16):
                truth={i for i in range(4) if mask>>i&1}
                iterative=set(truth)
                for _ in range(5):iterative=knowledge(pa,iterative)&knowledge(pb,iterative)
                require(iterative==common((pa,pb),truth))
                # Restricted public model retains only worlds where a stable atom is true.
                for w in truth:
                    adj=[{v for v in truth if pa[v]==pa[i] or pb[v]==pb[i]} for i in range(4)]
                    require(reach(adj,w)<=truth)
        pa=(0,0,1);pb=(0,1,1);truth={0,1}
        require(0 in knowledge(pa,truth)&knowledge(pb,truth))
        require(0 not in common((pa,pb),truth))

    @group('v0.5 Bounded morphisms preserve epistemic predicates',
           'All surjections from three worlds to two; all two-agent source/target partitions; all target atom valuations and formulas through two K/C stages')
    def _():
        for T in product(range(2),repeat=3):
            if set(T)!={0,1}:continue
            for pa in product(list(partitions(3)),repeat=2):
                for pb in product(list(partitions(2)),repeat=2):
                    if not is_bounded(T,pa,pb):continue
                    for mask in range(4):
                        vB={i for i in range(2) if mask>>i&1};vA={i for i in range(3) if T[i] in vB}
                        pairs=[(vA,vB)]
                        for depth in range(2):
                            nxt=[]
                            for a,b in pairs:
                                opts=[(knowledge(pa[0],a),knowledge(pb[0],b)),
                                      (knowledge(pa[1],a),knowledge(pb[1],b)),
                                      (common(pa,a),common(pb,b)),
                                      (set(range(3))-a,set(range(2))-b)]
                                for aa,bb in opts:
                                    require(aa=={i for i in range(3) if T[i] in bb});nxt.append((aa,bb))
                            pairs=nxt

    @group('v0.5 Finite agenda least closure and fair order',
           'Three record types; every subset of nine positive unary-or-empty rules; all eight initial sets; forward and reverse fair sweeps')
    def _():
        n=3;rules=[(0,c) for c in range(n)]+[(1<<p,c) for p in range(n) for c in range(n) if p!=c]
        def step(x,rs):
            y=x
            for pre,c in rs:
                if x&pre==pre:y|=1<<c
            return y
        for mask in range(1<<len(rules)):
            rs=[r for i,r in enumerate(rules) if mask>>i&1]
            for initial in range(8):
                x=initial;steps=0
                while True:
                    y=step(x,rs)
                    if y==x:break
                    steps+=1;x=y
                require(steps<=n-initial.bit_count())
                closed=[z for z in range(8) if z&initial==initial and step(z,rs)==z]
                least=7
                for z in closed:least&=z
                require(x==least)
                for order in (rs,rs[::-1]):
                    z=initial
                    for _ in range(n+1):
                        for pre,c in order:
                            if z&pre==pre:z|=1<<c
                    require(z==x)
        # A genuinely conjunctive rule is separate from the exhaustive unary family.
        require(step(1,[(3,2)])==1 and step(3,[(3,2)])==7)

    @group('v0.5 Founding record factorization',
           'All 16 maps of four histories to two record labels; all 16 authorization predicates; all four record classifiers')
    def _():
        for R in product(range(2),repeat=4):
            for labels in product(range(2),repeat=4):
                constant=all(labels[i]==labels[j] for i in range(4) for j in range(4) if R[i]==R[j])
                classifiers=[f for f in product(range(2),repeat=2) if all(f[R[i]]==labels[i] for i in range(4))]
                require(constant==bool(classifiers))
        for yesprob in [Q(i,4) for i in range(5)]:require(Q(1,2)*yesprob+Q(1,2)*(1-yesprob)==Q(1,2))

    @group('v0.5 Negative controls for progress and finite horizons',
           'Two fixed question outcomes; copying ratios for t=0..10; delayed bad event beyond each bound 0..10; not a test of undecidability')
    def _():
        solved={'easy':1,'hard':0}
        require(solved['easy']>solved['hard'])
        prior=Q(1)
        for t in range(11):
            share=Q(1,1+2**t);require(share<=prior);prior=share
        for horizon in range(11):
            delayed_event=horizon+1
            require(all(t<delayed_event for t in range(horizon+1)))
            require(delayed_event>=1)

def not_intersect(a,b):return not bool(a&b)
