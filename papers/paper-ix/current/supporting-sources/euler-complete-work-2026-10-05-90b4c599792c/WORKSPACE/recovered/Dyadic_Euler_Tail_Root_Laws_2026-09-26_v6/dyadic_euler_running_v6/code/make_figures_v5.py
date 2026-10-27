#!/usr/bin/env python3
"""Generate proof-linked plots. Scientific data are exact; plotting is illustrative."""
from pathlib import Path
from fractions import Fraction
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import dyadic_modular as d
from certificates_v5 import survival
ROOT=Path(__file__).resolve().parents[1]
FIG=ROOT/'figures';FIG.mkdir(exist_ok=True)

def save(fig,name):
    fig.tight_layout(pad=1.4)
    fig.savefig(FIG/(name+'.png'),dpi=220,bbox_inches='tight')
    fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight')
    plt.close(fig)

N=512
rs=list(range(1,N+1))
carry=[r.bit_count()+(N-r).bit_count()-N.bit_count() for r in rs]
fig,ax=plt.subplots(figsize=(9.0,4.2))
ax.plot(rs,carry,linewidth=.9,marker='.',markersize=3)
ax.set(xlabel='Reconstruction depth r',ylabel='Carry contribution',
       title=r'After subtracting the kernel: $w_r(512)-(4r-1)$')
ax.set_yticks(range(10));ax.grid(axis='y',alpha=.2)
for r in (16,32,64,128,256,512):
    ax.annotate(str(r),(r,carry[r-1]),xytext=(0,-16),textcoords='offset points',
                ha='center',fontsize=8)
ax.set_ylim(-1.5,9.6)
save(fig,'01_carry_residual')

rs=list(range(506,513));weights=[4*r-1+r.bit_count()+(N-r).bit_count()-N.bit_count() for r in rs]
fig,ax=plt.subplots(figsize=(9.0,4.2));ax.plot(rs,weights,marker='o',linewidth=1.7)
ax.set(xlabel='Reconstruction depth r',ylabel=r'Exact term weight $w_r(512)$',
       title='A nonadjacent collision at the binary boundary')
ax.set_xticks(rs);ax.ticklabel_format(axis='y',style='plain',useOffset=False)
for r in (510,511,512):
    w=weights[rs.index(r)]
    ax.annotate(f'({r}, {w})',(r,w),xytext=(-14,12 if r==511 else -20),
                textcoords='offset points',ha='center',fontsize=10)
ax.margins(x=.08,y=.2);ax.grid(axis='y',alpha=.2)
save(fig,'02_nonadjacent_collision')

for j,left,right,name in ((33,20,39,'03_irregular_33'),(49,35,55,'04_irregular_49')):
    data=json.loads((ROOT/'results'/f'IRREGULAR_{j}_V5.json').read_text())
    vals={a['delta']:a['roots'] for a in data['records']}
    xs=list(range(left,right+1));ys=[vals.get(x,j) for x in xs]
    fig,ax=plt.subplots(figsize=(9.0,4.5))
    ax.step(xs,ys,where='post',linewidth=1.7);ax.plot(xs,ys,'o',markersize=4)
    ax.set(xlabel=r'Wall distance $\delta$',ylabel='Number of dyadic roots',
           title=f'Irregular wall j = {j}: certified complete root counts')
    ax.set_xticks(list(range(left,right+1,2)));ax.grid(axis='y',alpha=.2)
    if j==33:
        ax.annotate('One root, then none, then two',xy=(27,0),xytext=(21,10),
                    arrowprops={'arrowstyle':'->'},fontsize=10)
    ax.set_ylim(-2,j+3)
    save(fig,name)

r=(1<<23)-5;dat=d.tail_polynomial(r,48);atlas=d.root_atlas(dat)
xs=list(range(0,21));probs=[survival(atlas,h) for h in xs]
fig,ax=plt.subplots(figsize=(9.0,4.5))
ax.plot(xs,[float(p) for p in probs],marker='o',markersize=4,label='Exact Haar fraction')
ax.plot(xs[6:],[24/(1<<h) for h in xs[6:]],linestyle='--',linewidth=1.6,
        label=r'$24\,2^{-h}$ for $h\geq6$')
ax.set_yscale('log',base=2)
ax.set(xlabel=r'Required residual valuation $h$',ylabel=r'Fraction with $v_2(G_r)\geq h$',
       title=r'Five separated roots: an exact precision-frequency law')
ax.set_xticks(range(0,21,2));ax.grid(alpha=.2);ax.legend(frameon=False,fontsize=10)
save(fig,'05_precision_survival')

xs=list(range(64));ys=[int(d.v2(d.evaluate(dat['coefficients'],x,1<<48))) for x in xs]
fig,ax=plt.subplots(figsize=(9.0,4.4));ax.plot(xs,ys,marker='o',markersize=3,linewidth=.9)
ax.set(xlabel=r'Offset $x=N-r$ in ordinary integer order',ylabel=r'Exact $v_2(G_r(x))$',
       title=r'Five-root wall at $\delta=6$: root-distance gains')
ax.grid(axis='y',alpha=.2);ax.set_xticks(range(0,64,8));save(fig,'06_residual_valuations')

xs=list(range(0,9));ys=[0,0,0,2,3,3,5,5,5]
fig,ax=plt.subplots(figsize=(9.0,4.0));ax.step(xs,ys,where='post',linewidth=1.8)
ax.plot(xs,ys,'o');ax.set_xticks(xs);ax.set_yticks(range(6))
ax.set(xlabel=r'Wall distance $\delta$',ylabel='Number of dyadic roots',
       title='Regular five-root wall: exact emergence at distances 3, 4, and 6')
ax.grid(axis='y',alpha=.2);save(fig,'07_regular_five_root')
print('Created seven proof-linked figures, each as PNG and PDF.')
