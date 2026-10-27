"""Reproduce mathematical vector figures from declared finite models."""
from pathlib import Path
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, FancyArrowPatch
import numpy as np
O=Path(__file__).resolve().parent
INK='#18363B'; TEAL='#236A72'; COPPER='#B47B43'; MUTED='#61747A'; LIGHT='#E8F1EE'; PALE='#F7F8F7'
plt.rcParams.update({'font.family':'DejaVu Sans','pdf.fonttype':42,'axes.edgecolor':INK,'text.color':INK,'font.size':11})

fig,ax=plt.subplots(figsize=(9.4,3.8));fig.patch.set_facecolor('white');ax.set_facecolor('white');ax.set_xlim(0,10);ax.set_ylim(0,4);ax.axis('off')
points={'u':(1.9,2.35),'z':(5.5,3.0),'g':(5.5,0.95)}
style={'u':('#F5E9D9',COPPER),'z':('#EFEFEF',MUTED),'g':(LIGHT,TEAL)}
for key,(x,y) in points.items():
 face,edge=style[key];ax.add_patch(Circle((x,y),.42,facecolor=face,edgecolor=edge,lw=2,zorder=5));ax.text(x,y,key,va='center',ha='center',fontsize=17,weight='semibold',zorder=6)
def arrow(a,b,label,color,rad=0):
 a0=np.array(points[a]);b0=np.array(points[b]);vec=b0-a0;u=vec/np.linalg.norm(vec)
 arr=FancyArrowPatch(a0+.48*u,b0-.50*u,connectionstyle=f'arc3,rad={rad}',arrowstyle='-|>',lw=2,mutation_scale=17,color=color,zorder=4)
 ax.add_patch(arr);m=.5*(a0+b0);ax.text(m[0]+.05,m[1]+.3,label,color=color,ha='center',fontsize=10)
arrow('u','z','run',COPPER,.0)
arrow('u','g','end',TEAL,.0)
for q,ty,col in [('z',3.0,MUTED),('g',.95,TEAL)]:
 x,y=points[q];a=FancyArrowPatch((x+.10,y+.42),(x+.53,y+.25),connectionstyle='arc3,rad=-1.5',arrowstyle='-|>',color=col,lw=1.8,mutation_scale=13);ax.add_patch(a)
ax.text(5.5,3.7,'safe idle',color=MUTED,ha='center',fontsize=10)
ax.text(5.5,.1,'safe hold',color=TEAL,ha='center',fontsize=10)
ax.text(7.3,3.15,r'$S=\{u,z,g\}$',fontsize=13)
ax.text(7.3,2.53,r'$G=\{g\}$',fontsize=13)
ax.text(7.3,1.91,r'$T_*=\{u,g\}$',fontsize=13,color=TEAL)
ax.text(7.3,1.29,r'$L_*=\{g\}$',fontsize=13,color=COPPER)
ax.text(7.3,.58,'Running at u loses the option to end.',fontsize=9.7,color=MUTED)
fig.subplots_adjust(left=.02,right=.98,top=.98,bottom=.02)
fig.savefig(O/'safe_ending_kernel.pdf',transparent=False,bbox_inches='tight',pad_inches=.12)
fig.savefig(O/'safe_ending_kernel.png',dpi=180,bbox_inches='tight',pad_inches=.12)
plt.close(fig)

fig,axs=plt.subplots(1,2,figsize=(8.5,3.4))
for ax,mat,title in zip(axs, [np.array([[.5,0],[0,.5]]),np.array([[0,.5],[.5,0]])],['Fine state x₀','Fine state x₁']):
 im=ax.imshow(mat,cmap='BuGn',vmin=0,vmax=.6)
 ax.set_title(title,pad=11,fontsize=13,weight='semibold')
 ax.set_xticks([0,1],['report 0','report 1']);ax.set_yticks([0,1],['next 0','next 1'])
 for i in range(2):
  for j in range(2):ax.text(j,i,'½' if mat[i,j] else '0',ha='center',va='center',fontsize=17,color='white' if mat[i,j] else INK)
 ax.tick_params(length=0)
 for sp in ax.spines.values():sp.set_visible(False)
fig.suptitle('Equal marginals, incompatible joint instruments',y=1.05,fontsize=14,weight='semibold')
fig.text(.5,-.035,'Both states have uniform next-state and report marginals, but opposite correlations.',ha='center',fontsize=10,color=MUTED)
fig.tight_layout()
fig.savefig(O/'joint_instrument_obstruction.pdf',bbox_inches='tight',pad_inches=.14)
fig.savefig(O/'joint_instrument_obstruction.png',dpi=180,bbox_inches='tight',pad_inches=.14)
plt.close(fig)
print('Wrote two source-generated vector figures')
