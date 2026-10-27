#!/usr/bin/env python3
"""Deterministic mathematical diagrams from exact integers."""
from pathlib import Path
from math import log10
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.titlesize':15,'axes.labelsize':11,'figure.dpi':130,'savefig.dpi':200})
fig,ax=plt.subplots(figsize=(9,5.3),layout='constrained')
for L,desc in [(1,'mod 8 (L=1)'),(2,'mod 12 (L=2)'),(4,'mod 40 (L=4)'),(12,'mod 360 (L=12)')]:
  p,q=2,3
  U,V=p**L,q**L
  ys=[log10(q**k*(V-1)*(V-U))-log10(2*(U+1)) for k in range(3,19)]
  ax.plot(list(range(3,19)),ys,marker='o',markersize=3,linewidth=1.8,label=desc)
ax.set_title('Finite modular observation: unavoidable reconstruction cost',loc='left',pad=12)
ax.set_xlabel('Starting depth k in powers 2ᵏ')
ax.set_ylabel('log₁₀ of sharp three-shell error')
ax.grid(True,alpha=.25)
ax.legend(title='Finite observation')
ax.text(.01,-.18,'Transport 2 → 3. Each curve uses shells k, k+L, k+2L with identical finite observations.',
        transform=ax.transAxes,fontsize=8.5)
fig.savefig(ROOT/'figures/finite_observation_error.png',bbox_inches='tight')
plt.close(fig)

p=7;N=2
T=lambda x:pow(x,p,p**N)
carry=lambda x,y:((T(x)+T(y)-T((x+y)%p))%(p**N))//p
heat=np.array([[carry(x,y) for y in range(p)] for x in range(p)])
fig,ax=plt.subplots(figsize=(7.1,6.15),layout='constrained')
im=ax.imshow(heat,interpolation='nearest',cmap='viridis',origin='upper',aspect='equal')
for x in range(p):
 for y in range(p):ax.text(y,x,str(heat[x,y]),ha='center',va='center',fontsize=10,
       color='white' if heat[x,y]<2 or heat[x,y]>5 else 'black')
ax.set_title('Local arithmetic reconstruction: Teichmüller carries',loc='left',pad=12)
ax.set_xlabel('Input residue y modulo 7')
ax.set_ylabel('Input residue x modulo 7')
ax.set_xticks(range(p));ax.set_yticks(range(p))
fig.colorbar(im,ax=ax,label='Carry coefficient modulo 7',shrink=.75)
fig.savefig(ROOT/'figures/witt_carry_matrix_p7.png',bbox_inches='tight')
plt.close(fig)
print('PASS: two mathematically generated figures')
