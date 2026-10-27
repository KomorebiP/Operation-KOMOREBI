from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
out=Path(__file__).resolve().parents[2]/'source/monographs/figures'
fig=plt.figure(figsize=(8.5,4.5));ax=fig.add_axes([.01,.01,.98,.98]);ax.set_xlim(0,10);ax.set_ylim(0,6);ax.axis('off')
rows=[(4.12,'FORMAL SOURCE COVERAGE','Unitary coefficient and torus evolution','Self-adjoint Hamiltonian and exact domain','#078A98'),(2.13,'WRITTEN MATHEMATICAL PROOFS','Full generator domain and spectral evolution','Centered resolvents and regularity-based rates','#173F5A'),(.14,'SEPARATE PHYSICAL COMPARISONS','Sampled grids and background coupling','Dynamical fields and controlled production','#A66B2B')]
for y,title,left,right,col in rows:
 ax.text(.3,y+1.4,title,fontsize=11,weight='bold',color=col,va='center')
 for x,txt in [(0.3,left),(5.15,right)]:
  ax.add_patch(FancyBboxPatch((x,y),4.55,1.03,boxstyle='round,pad=0.08,rounding_size=.09',facecolor='#F0F5F6',edgecolor=col,linewidth=1.1))
  # split at thematic boundaries to preserve unclipped text
  split={'Unitary coefficient and torus evolution':'Unitary group and Hamiltonian\non physical torus fields','Self-adjoint Hamiltonian and exact domain':'Exact generator domain\nand strong Schrödinger equation','Full generator domain and spectral evolution':'Spectral-functional-calculus\nidentification','Centered resolvents and regularity-based rates':'Centered resolvent limits\nand regularity-based rates','Sampled grids and background coupling':'Sampled spatial grids\nand background coupling','Dynamical fields and controlled production':'Dynamical fields\nand controlled production'}
  ax.text(x+2.275,y+.515,split[txt],ha='center',va='center',fontsize=11.5,color='#1C3445',linespacing=1.4)
fig.savefig(out/'12_frontier.pdf',bbox_inches='tight',pad_inches=.03)
fig.savefig(out/'12_frontier.png',dpi=170,bbox_inches='tight',pad_inches=.03)
plt.close(fig)
