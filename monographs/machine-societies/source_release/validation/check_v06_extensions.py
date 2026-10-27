"""Exact, explicitly bounded v0.6 mathematical regressions and negative controls.

All probabilities are fractions.Fraction. No random sampling or learned agents.
The exhaustive staffing test compares subset inequalities with independent search.
"""
from collections import defaultdict
from fractions import Fraction as Q
from itertools import product, permutations, combinations
from math import comb


def tv(p,q): return sum((abs(a-b) for a,b in zip(p,q)),Q(0))/2

def row(v,M): return tuple(sum((v[i]*M[i][j] for i in range(len(v))),Q(0)) for j in range(len(M[0])))

def mm(A,B): return tuple(row(a,B) for a in A)

def power(M,m):
    out=tuple(tuple(Q(i==j) for j in range(len(M))) for i in range(len(M)))
    for _ in range(m):out=mm(out,M)
    return out

def probs2(den):return [(Q(i,den),Q(den-i,den)) for i in range(den+1)]

def capped_opt(pc,pd,alpha):
    """Enumerate every vertex of [0,1]^2 intersect {pc.s <= alpha}."""
    points=set(product((Q(0),Q(1)),repeat=2))
    for fixed in (Q(0),Q(1)):
        if pc[1]:points.add((fixed,(alpha-pc[0]*fixed)/pc[1]))
        if pc[0]:points.add(((alpha-pc[1]*fixed)/pc[0],fixed))
    feasible=[s for s in points if all(0<=t<=1 for t in s) and sum(pc[i]*s[i] for i in range(2))<=alpha]
    return max(sum((pd[i]-pc[i])*s[i] for i in range(2)) for s in feasible)


def run_extensions(group, require):
    @group('v06 Join algebra and fixed-contribution convergence', 'All triples of subsets of three events; all orders of four deliveries including a duplicate; unions of downward-closed sets in a three-event chain')
    def _():
        U=range(8)
        for a,b,c in product(U,repeat=3):
            require((a|b)|c==a|(b|c));require(a|b==b|a);require(a|a==a)
        for deliveries in permutations((1,2,4,2)):
            state=0
            for d in deliveries:state|=d
            require(state==7)
        down=(0,1,3,7)
        for a,b in product(down,repeat=2):require(a|b in down)

    @group('v06 Merge validity and exclusive-service obstruction', 'All local decision functions on two request bits; two-grantee singleton/union records; all downward-closed initial/update subset records on three tokens')
    def _():
        valid=lambda s:s.bit_count()<=1
        require(valid(1) and valid(2) and not valid(1|2))
        require((1|2)==(2|1))
        feasible=0
        for f,g in product(list(product((0,1),repeat=2)),repeat=2):
            singleton=(f[1]==1 and g[1]==1)
            exclusive=(f[1]+g[1]<=1)
            require(not(singleton and exclusive));feasible+=bool(singleton and exclusive)
        require(feasible==0)
        for allowed in range(8):
            safe=[s for s in range(8) if s&allowed==s]
            for a,b in product(safe,repeat=2):require(a|b in safe)

    @group('v06 Exact total-variation sanction optimum', 'Every three-outcome law with denominator four, every pair, all eight deterministic sanctions and all 27 half-grid sanctions')
    def _():
        laws=[tuple(Q(i,4) for i in p) for p in product(range(5),repeat=3) if sum(p)==4]
        for pc,pd in product(laws,repeat=2):
            differences=[sum((pd[i]-pc[i])*s[i] for i in range(3)) for s in product((Q(0),Q(1)),repeat=3)]
            d=tv(pc,pd);require(max(differences)==d)
            require(sum(max(Q(0),pd[i]-pc[i]) for i in range(3))==d)
            for s in product((Q(0),Q(1,2),Q(1)),repeat=3):
                require(sum((pd[i]-pc[i])*s[i] for i in range(3))<=d)
            for gain in (Q(1,4),Q(1,2),Q(3,4),Q(1)):
                require(any(gain<=v for v in differences)==(gain<=d))
                require(any(gain<v for v in differences)==(gain<d))

    @group('v06 False-positive constraints and conflicting deviations', 'Binary quarter-grid observation laws and false-positive caps; exact two-dimensional LP vertices; two opposed deviations and all quarter-grid sanctions')
    def _():
        for pc,pd in product(probs2(4),repeat=2):
            previous=Q(-1)
            for alpha in (Q(i,4) for i in range(5)):
                value=capped_opt(pc,pd,alpha)
                require(0<=value<=tv(pc,pd));require(value>=previous);previous=value
            require(capped_opt(pc,pd,Q(1))==tv(pc,pd))
        pc=(Q(3,4),Q(1,4));pd=tuple(reversed(pc))
        require(capped_opt(pc,pd,Q(1,10))==Q(1,5))
        for s in product([Q(i,4) for i in range(5)],repeat=2):
            d1=(s[0]-s[1])/2;d2=-d1
            require(d1+d2==0);require(not(d1>0 and d2>0))

    @group('v06 Sanction garbling and protected discrimination', 'All binary quarter-grid laws and all binary half-grid channels; deterministic coarse sanctions; caps 0, 1/2, 1 with LP vertex evaluation')
    def _():
        channels=list(product(probs2(2),repeat=2))
        for pc,pd in product(probs2(4),repeat=2):
            for B in channels:
                qc,qd=row(pc,B),row(pd,B)
                require(tv(qc,qd)<=tv(pc,pd))
                for alpha in (Q(0),Q(1,2),Q(1)):
                    require(capped_opt(qc,qd,alpha)<=capped_opt(pc,pd,alpha))
                for t in product((Q(0),Q(1)),repeat=2):
                    s=tuple(sum(B[i][j]*t[j] for j in range(2)) for i in range(2))
                    for p,q in ((pc,qc),(pd,qd)):
                        require(sum(p[i]*s[i] for i in range(2))==sum(q[j]*t[j] for j in range(2)))

    @group('v06 Refresh kernels and uniform mixing', 'Binary stationary laws on quarter grid, refresh probabilities 1/4, 1/2, 3/4, 1, powers m=1..8')
    def _():
        for mu in probs2(4):
            for beta in (Q(1,4),Q(1,2),Q(3,4),Q(1)):
                K=tuple(tuple((1-beta)*Q(i==j)+beta*mu[j] for j in range(2)) for i in range(2))
                require(row(mu,K)==mu)
                for m in range(1,9):
                    P=power(K,m);a=(1-beta)**m
                    for i in range(2):
                        require(P[i]==tuple(a*Q(i==j)+(1-a)*mu[j] for j in range(2)))
                        require(tv(P[i],mu)==a*(1-mu[i]))
        require(Q(20,512)==Q(5,128))

    @group('v06 Institutional path averaging with dependent resets', 'Two institutions and two fast states; four endpoint revision pairs; three deterministic reset rules; block lengths 1..4, horizons 0..5, both initial fast states')
    def _():
        mus=((Q(1,2),Q(1,2)),(Q(1,3),Q(2,3)))
        Ks=tuple(tuple(tuple(Q(1,2)*Q(x==y)+Q(1,2)*mu[y] for y in range(2)) for x in range(2)) for mu in mus)
        identity=((Q(1),Q(0)),(Q(0),Q(1)))
        flip=tuple(reversed(identity)); noisy=((Q(3,4),Q(1,4)),(Q(1,4),Q(3,4)))
        for Rs in ((identity,identity),(identity,flip),(noisy,identity),(noisy,flip)):
            avg=tuple(row(mus[i],Rs[i]) for i in range(2))
            for m in range(1,5):
                Ps=tuple(power(K,m) for K in Ks)
                eps=max(tv(Ps[i][x],mus[i]) for i,x in product(range(2),repeat=2))
                for reset in range(3):
                    for x0 in range(2):
                        actual={((0,),x0):Q(1)};reduced={(0,):Q(1)}
                        for T in range(6):
                            marginal=defaultdict(Q)
                            for (h,x),w in actual.items():marginal[h]+=w
                            allh=set(marginal)|set(reduced)
                            d=sum(abs(marginal[h]-reduced.get(h,Q(0))) for h in allh)/2
                            require(sum(actual.values())==sum(reduced.values())==1)
                            require(d<=1-(1-eps)**T<=min(Q(1),T*eps))
                            if T==5:break
                            new=defaultdict(Q)
                            for (h,x),w in actual.items():
                                i=h[-1]
                                for y,j in product(range(2),repeat=2):
                                    xp=(y if reset==0 else j if reset==1 else y^j)
                                    new[(h+(j,),xp)]+=w*Ps[i][x][y]*Rs[i][y][j]
                            actual=dict(new);newr=defaultdict(Q)
                            for h,w in reduced.items():
                                for j in range(2):newr[h+(j,)]+=w*avg[h[-1]][j]
                            reduced=dict(newr)

    @group('v06 Adaptive review bias and nonmixing negative controls', 'All fair bit strings at caps M=2..10; all binary quarter-grid candidate averages for the identity kernel')
    def _():
        for M in range(2,11):
            ones=0
            for bits in product(range(2),repeat=M):
                stop=next((i for i,b in enumerate(bits) if b),M-1)
                ones+=bits[stop]
            require(Q(ones,2**M)==1-Q(1,2**M))
            require(abs(Q(ones,2**M)-Q(1,2))==Q(1,2)-Q(1,2**M))
        for mu in probs2(4):require(max(tv((Q(1),Q(0)),mu),tv((Q(0),Q(1)),mu))>=Q(1,2))

    @group('v06 Reduced-model robust enforcement margins', 'Every quadruple of binary quarter-grid true/reduced laws; gains 1/4, 1/2, 3/4; F=1; exact attained errors')
    def _():
        for pc,pd,bc,bd in product(probs2(4),repeat=4):
            ec,ed=tv(pc,bc),tv(pd,bd);dbar=tv(bc,bd)
            s=tuple(Q(bd[i]>bc[i]) for i in range(2))
            delta=sum((pd[i]-pc[i])*s[i] for i in range(2))
            require(delta>=dbar-ec-ed)
            require(tv(pc,pd)<=min(Q(1),dbar+ec+ed))
            require(sum(pc[i]*s[i] for i in range(2))<=sum(bc[i]*s[i] for i in range(2))+ec)
            for gain in (Q(1,4),Q(1,2),Q(3,4)):
                if gain<=dbar-ec-ed:require(gain<=delta)
                if gain>min(Q(1),dbar+ec+ed):require(gain>tv(pc,pd))

    @group('v06 Bayesian histories versus cascade closed forms', 'Exact action-history Bayesian recursion, depths 1..10, p=2/3, 3/4, 4/5; private-signal tie rule, fair prior')
    def _():
        for p in (Q(2,3),Q(3,4),Q(4,5)):
            q=1-p;lam=p/q;eta=q*q/(p*p+q*q);a=2*p*q
            histories={(): (Q(1),Q(1))}
            for n in range(1,11):
                nh={}
                for h,(w0,w1) in histories.items():
                    for sig in range(2):
                        v0=w0*(p if sig==0 else q);v1=w1*(p if sig==1 else q)
                        action=1 if v1>v0 else 0 if v0>v1 else sig
                        key=h+(action,)
                        old=nh.get(key,(Q(0),Q(0)))
                        nh[key]=(old[0]+v0,old[1]+v1)
                histories=nh
                require(sum(w[0] for w in histories.values())==sum(w[1] for w in histories.values())==1)
                error=sum(w0 if h[-1] else w1 for h,(w0,w1) in histories.items())/2
                require(error==eta+(q-eta)*a**((n-1)//2))
                unlocked=Q(0)
                for h,(w0,w1) in histories.items():
                    z=0
                    for action in h:
                        if abs(z)<2:z+=1 if action else -1
                    require(w1/w0==lam**z)
                    if abs(z)<2:unlocked+=(w0+w1)/2
                if n%2==0:require(unlocked==a**(n//2))
            require(eta>0)
        require(Q(1,4)**2/(Q(3,4)**2+Q(1,4)**2)==Q(1,10))

    @group('v06 Evidence majority and exact figure probabilities', 'p=2/3, 3/4, 4/5; n=1..41; fixed zero tie with fair prior; independent binomial tails and variance bound')
    def _():
        for p in (Q(2,3),Q(3,4),Q(4,5)):
            q=1-p
            for n in range(1,42):
                error=sum(Q(comb(n,j))*p**j*q**(n-j) for j in range((n+1)//2))
                if n%2==0:error+=Q(1,2)*comb(n,n//2)*p**(n//2)*q**(n//2)
                require(error<=min(Q(1),p*q/(n*(p-Q(1,2))**2)))
                if n==1:require(error==q)
                if n>2 and n%2==1:require(error<previous_odd)
                if n%2==1:previous_odd=error
                require(sum(Q(comb(n,j))*p**j*q**(n-j) for j in range(n+1))==1)

    @group('v06 Robust staffing: subset certificate versus independent assignments', 'Every bipartite graph with 1..3 roles and 1..4 agents; all erasure sets and budgets k=0..number of agents; unit capacities')
    def _():
        for nr in range(1,4):
            for na in range(1,5):
                full=(1<<na)-1
                for graph in range(1<<(nr*na)):
                    ns=tuple((graph>>(j*na))&full for j in range(nr))
                    def possible(survive):
                        def match(j,used):
                            if j==nr:return True
                            avail=ns[j]&survive&~used
                            while avail:
                                bit=avail&-avail;avail-=bit
                                if match(j+1,used|bit):return True
                            return False
                        return match(0,0)
                    ok={f:possible(full^f) for f in range(1<<na)}
                    slack=na
                    for subset in range(1,1<<nr):
                        union=0
                        for j in range(nr):
                            if subset>>j&1:union|=ns[j]
                        slack=min(slack,union.bit_count()-subset.bit_count())
                    for k in range(na+1):
                        brute=all(ok[f] for f in range(1<<na) if f.bit_count()<=k)
                        require(brute==(slack>=k),f'graph={graph},roles={nr},agents={na},k={k}')

    @group('v06 Collective backups and temporal evidence routes', 'Two-role backup counterexample; all single failures in the three-role/four-agent example; both private bit values for two message orders')
    def _():
        ns=(0b0011,0b0110,0b1100)
        for lost in range(4):
            assignments=[a for a in permutations(range(4),3) if lost not in a and all(ns[j]>>a[j]&1 for j in range(3))]
            require(bool(assignments))
        for lost in range(2):
            require(not any(lost not in a for a in permutations(range(2),2)))
        reverse=[];forward=[]
        for bit in range(2):
            A=bit;B=None;C=None
            C=B;B=A;reverse.append(C)
            B=None;C=None;B=A;C=B;forward.append(C)
        require(reverse[0]==reverse[1]);require(forward==[0,1])
        for constant_guess in range(2):require(Q(sum(constant_guess==bit for bit in range(2)),2)==Q(1,2))
