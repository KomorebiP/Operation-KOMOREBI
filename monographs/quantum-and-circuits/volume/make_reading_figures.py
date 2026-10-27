from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch,FancyArrowPatch
from matplotlib.path import Path as MPath
ROOT=Path(__file__).resolve().parent
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'pdf.fonttype':42,'axes.unicode_minus':False})
fig,ax=plt.subplots(figsize=(9,4.8));ax.set(xlim=(-.15,10.15),ylim=(-.75,4.8));ax.axis('off')
ax.add_patch(FancyBboxPatch((0,0),10,4.5,boxstyle='round,pad=.02,rounding_size=.1',facecolor='#f5f7f8',edgecolor='#71818b',lw=1.1))
ax.text(.35,4.1,'Ambient model G',weight='bold',color='#183247',fontsize=13)
ax.add_patch(FancyBboxPatch((.55,.4),5.25,2.55,boxstyle='round,pad=.02,rounding_size=.1',facecolor='#e7f1ee',edgecolor='#39766e',lw=1.1))
ax.text(.85,2.6,'Restricted model H',weight='bold',color='#39766e',fontsize=12)
ax.text(.85,2.16,'The target U belongs to H.',fontsize=10,color='#183247')
a=(1.25,1.05);b=(4.8,1.05)
ax.plot([a[0],b[0]],[a[1],b[1]],'o',color='#183247',ms=5,zorder=4)
ax.text(a[0]-.2,.6,'e',fontsize=13);ax.text(b[0],.6,'U',fontsize=13)
ax.add_patch(FancyArrowPatch(a,b,connectionstyle='arc3,rad=-.15',arrowstyle='-|>',mutation_scale=14,color='#39766e',lw=2))
ax.text(2.5,1.08,'restricted path',fontsize=10,color='#39766e',ha='center')
path=MPath([a,(3,1.75),(5.5,3.75),(8.2,2.9),(9,.5),(6.35,.1),b],[MPath.MOVETO,MPath.CURVE4,MPath.CURVE4,MPath.CURVE4,MPath.CURVE4,MPath.CURVE4,MPath.CURVE4])
ax.add_patch(FancyArrowPatch(path=path,arrowstyle='-|>',mutation_scale=14,color='#b66151',lw=2))
ax.text(7.45,2.1,'ambient path\nmay leave H\nand return',ha='center',va='center',color='#a15345',fontsize=11)
ax.text(5,-.35,r'Nested gate alphabets and fixed costs give $\ell_{\rm amb}(U)\leq\ell_{\rm res}(U)$.',ha='center',fontsize=10,color='#183247')
ax.text(5,-.66,'Path geometry is schematic and does not measure gate count.',ha='center',fontsize=9,color='#596773')
fig.tight_layout(pad=.4)
fig.savefig(ROOT/'assets/g_gate_hierarchy.pdf',bbox_inches='tight');fig.savefig(ROOT/'qa/g_gate_hierarchy.png',dpi=150,bbox_inches='tight');plt.close(fig)

# Preserve the exact census data, while keeping the SWAP note in the caption.
import json
source=ROOT.parent/'sources/catalytic/Catalytic_Gate_Set_Distortion_Monograph_Source/results/atlas_results.json'
data=json.loads(source.read_text())
rows=[e for e in data['clifford'] if e['qubits'] in (2,3) and not e['include_swap']]
labels=[f"n = {e['qubits']}\n"+('primitive count' if e['metric']=='total' else 'entangling count') for e in rows]
values=[e['defect_count'] for e in rows]
colors=['#355C7D' if e['metric']=='total' else '#C06C84' for e in rows]
fig,ax=plt.subplots(figsize=(8.5,4.9))
bars=ax.bar(range(len(rows)),values,color=colors,edgecolor='#183247',width=.68,zorder=3)
ax.set_xticks(range(len(rows)),labels)
ax.set_yscale('symlog',linthresh=1)
ax.set_ylim(0,max(values)*2)
ax.set_ylabel('Defective parabolic targets (symlog scale)')
ax.set_title('Exact Clifford defects depend on the cost model',fontsize=13,pad=12)
for bar,v in zip(bars,values):ax.annotate(str(v),(bar.get_x()+bar.get_width()/2,v),xytext=(0,6),textcoords='offset points',ha='center',va='bottom',fontsize=11)
ax.grid(axis='y',alpha=.22,zorder=0);ax.spines[['top','right']].set_visible(False)
fig.tight_layout(pad=1.0)
fig.savefig(ROOT/'assets/g_clifford_census.pdf',bbox_inches='tight');fig.savefig(ROOT/'qa/g_clifford_census.png',dpi=150,bbox_inches='tight');plt.close(fig)
(ROOT/'qa/census_plot_data.json').write_text(json.dumps({'source':str(source.relative_to(ROOT.parent)),'rows':rows,'values':values,'note':'No numerical values changed; internal SWAP annotation moved to the book caption.'},indent=2))
