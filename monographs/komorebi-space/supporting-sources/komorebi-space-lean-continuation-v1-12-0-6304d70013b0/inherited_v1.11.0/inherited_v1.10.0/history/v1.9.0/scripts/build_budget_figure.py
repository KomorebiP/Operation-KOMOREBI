#!/usr/bin/env python3
"""Rebuild only plate 32, preserving the inherited geometry and correcting its legend.

Extracted from the v1.7.0 checks/build_regularization_figures.py figure-32 block.
Inherited source SHA256: 6b32b6d7ee5033fc034e0ba129b5d090cd424e681f4275bf580d33d40d6e0da6.
The only plotted-content change is 'Reachable residuals' -> 'Reachable images'.
The output PDF omits volatile date metadata for reproducible builds.
"""
from pathlib import Path
import math
import numpy as np
import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
plt.rcParams.update({'font.family':'STIXGeneral','mathtext.fontset':'stix','font.size':12,
                     'axes.labelsize':12,'legend.fontsize':10.5,'pdf.fonttype':42,'ps.fonttype':42})

fig,ax=plt.subplots(figsize=(7.5,4.0))
M=math.sqrt(41)/10;theta=np.linspace(0,2*math.pi,600)
x=M*np.cos(theta);y=M/2*np.sin(theta)
ax.fill(x,y,alpha=.10);ax.plot(x,y,lw=1.6,label='Reachable images at the fixed budget')
q=np.array([.5,.2]);r=np.array([1.,1.]);v=r-q
s=np.linspace(-.63,.65,100);line=q[:,None]+np.array([.8,-.5])[:,None]*s
ax.plot(line[0],line[1],'--',lw=1.2,label='Supporting line')
ax.annotate('',xy=r,xytext=q,arrowprops={'arrowstyle':'->','lw':1.8})
ax.plot([0,q[0],r[0]],[0,q[1],r[1]],'o',ms=4)
ax.annotate(r'$Ta=(1/2,1/5)$',xy=q,xytext=(.73,-.30),
            arrowprops={'arrowstyle':'-','lw':.7},fontsize=12)
ax.text(1.04,1.02,r'$r=(1,1)$',fontsize=12)
ax.text(.95,.55,r'$v=(1/2,4/5)$',fontsize=12)
ax.text(-.24,-.13,'0',fontsize=11)
ax.set_aspect('equal');ax.set(xlim=(-.85,1.62),ylim=(-.66,1.3),xlabel='Residual coordinate 1',ylabel='Residual coordinate 2')
ax.legend(loc='upper left',frameon=False,fontsize=10)

output = ROOT / 'source/figures/32_budget_certificate.pdf'
fig.savefig(output,bbox_inches='tight',pad_inches=.12,
            metadata={'CreationDate':None,'ModDate':None})
plt.close(fig)
print(f'Generated only {output}')
