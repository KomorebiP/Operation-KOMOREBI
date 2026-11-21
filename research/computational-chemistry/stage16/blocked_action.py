"""Apply the same spin-free operator with bounded contraction buffers.

E_pq is a sum of two signed partial permutations. Each output component of
the final accumulation receives at most 2*n*n additions, independent of block
order. Thus the Stage 15 normwise operation-count enclosure applies unchanged.
"""
from fractions import Fraction as F
import numpy as np

def prepare(model):
    model.prepare_float()
    if hasattr(model,'_blocked_links'):return
    records=[]
    for alpha,beta in model.links:
        spin=[]
        for links,size in [(alpha,len(model.alpha)),(beta,len(model.beta))]:
            src,dst,sgn=links
            assert len(set(map(int,dst)))==len(dst)
            forward=np.full(size,-1,dtype=int);reverse=np.full(size,-1,dtype=int);fs=np.zeros(size);rs=np.zeros(size)
            forward[src]=dst;fs[src]=sgn;reverse[dst]=src;rs[dst]=sgn
            spin.append((forward,reverse,fs,rs))
        records.append(spin)
    model._blocked_links=records

def apply(model,vector,block=4096):
    prepare(model)
    if np.iscomplexobj(vector):raise ValueError('Real action vector required')
    vector=np.asarray(vector,dtype=float)
    if vector.shape!=(model.dimension,) or not np.isfinite(vector).all() or np.max(np.abs(vector),initial=0)>2**20:raise ValueError('Action vector outside the proved range')
    exponent=max((F(float(x)).denominator.bit_length()-1 for x in vector.flat),default=0)
    if exponent+model.coefficient_denominator_exponent+1>=1000:raise ValueError('Cannot exclude action underflow')
    if not 1<=block<=4096:raise ValueError('Contraction block must lie in 1..4096')
    N=model.dimension;nb=len(model.beta);m=model.n*model.n;one=np.empty(N);two=np.zeros(N)
    for start in range(0,N,block):
        stop=min(N,start+block);ids=np.arange(start,stop);a,b=ids//nb,ids%nb;T=np.zeros((m,stop-start))
        for k,((fa,ra,sa,sra),(fb,rb,sb,srb)) in enumerate(model._blocked_links):
            valid=ra[a]>=0;T[k,valid]=sra[a[valid]]*vector[ra[a[valid]]*nb+b[valid]]
            valid=rb[b]>=0;T[k,valid]+=srb[b[valid]]*vector[a[valid]*nb+rb[b[valid]]]
        W=model.gf@T;one[start:stop]=model.hf@T
        for k,((fa,ra,sa,sra),(fb,rb,sb,srb)) in enumerate(model._blocked_links):
            valid=fa[a]>=0;targets=fa[a[valid]]*nb+b[valid];two[targets]+=sa[a[valid]]*W[k,valid]
            valid=fb[b]>=0;targets=a[valid]*nb+fb[b[valid]];two[targets]+=sb[b[valid]]*W[k,valid]
    result=one+two/2
    if not np.isfinite(result).all():raise ValueError('Nonfinite action')
    return result
