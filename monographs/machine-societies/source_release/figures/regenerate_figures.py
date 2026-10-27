from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle, FancyBboxPatch
out = Path(__file__).resolve().parent; out.mkdir(parents=True,exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','pdf.fonttype':42,'savefig.transparent':False})
navy='#172A44'; blue='#426A96'; grey='#5B6778'; line='#C9D2DD'; pale='#F3F6FA'; teal='#2C7D7D'

fig, ax = plt.subplots(figsize=(8.5,5.25))
fig.patch.set_facecolor('white'); ax.set_facecolor('white')
ax.set_xlim(0,1); ax.set_ylim(0,1)
for x in (0,0.5):
 for y in (0,0.5):
  ax.add_patch(Rectangle((x,y),.5,.5,facecolor=(pale if (x+y)<0.5 else '#F8FAFC'),edgecolor=line,linewidth=1.1))
ax.axvline(.5,color='#9DAAB9',linewidth=1.4);ax.axhline(.5,color='#9DAAB9',linewidth=1.4)
cells=[(.25,.76,'Unitary service','Single policy, limited\ninstitutional plurality'),(.75,.76,'Federated coordination','Plural decision centers\nwith collective action'),(.25,.25,'Transient interaction','Coordination without\ndurable institutions'),(.75,.25,'Plural machine society','Durable rules and records\nwithout one group mind')]
for x,y,t,d in cells:
 ax.text(x,y,t,ha='center',va='center',color=navy,weight='bold',fontsize=11)
 ax.text(x,y-.12,d,ha='center',va='center',color=grey,fontsize=9.1,linespacing=1.45)
ax.set_xlabel('Institutional plurality and persistence $\\longrightarrow$',fontsize=10,color=navy,labelpad=15)
ax.set_ylabel('Collective policy closure $\\longrightarrow$',fontsize=10,color=navy,labelpad=15)
ax.set_xticks([]);ax.set_yticks([])
for s in ax.spines.values():s.set_visible(False)
fig.tight_layout(pad=1.8)
fig.savefig(out/'society_versus_agency.pdf',bbox_inches='tight'); plt.close(fig)

fig,ax=plt.subplots(figsize=(9,5.7)); fig.patch.set_facecolor('white');ax.set_xlim(0,10);ax.set_ylim(0,6);ax.axis('off')
components=[(1.3,4.55,'Agent A'),(5,4.55,'Agent B'),(8.7,4.55,'Agent C')]
for x,y,t in components:
 ax.add_patch(FancyBboxPatch((x-1.05,y-.40),2.1,.82,boxstyle='round,pad=0.13,rounding_size=0.1',facecolor='#EDF3F9',edgecolor=blue,lw=1.3))
 ax.text(x,y,t,ha='center',va='center',fontsize=11,weight='bold',color=navy)
for x,t in [(2.1,'Protocol and\npermission rules'),(5,'Shared records\nand provenance'),(7.9,'Resource and\nconflict procedures')]:
 ax.add_patch(FancyBboxPatch((x-1.22,2.0),2.44,1.12,boxstyle='round,pad=0.12',facecolor='#F6F7FA',edgecolor='#8898A9',lw=1.1))
 ax.text(x,2.58,t,ha='center',va='center',fontsize=9.4,color=navy)
for a,b in [((1.3,4.12),(2.1,3.26)),((5,4.12),(5,3.26)),((8.7,4.12),(7.9,3.26))]:
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle='<->',mutation_scale=11,color=teal,lw=1.6))
ax.add_patch(FancyBboxPatch((3.16,.27),3.68,.8,boxstyle='round,pad=0.12',facecolor='#E9F4F2',edgecolor=teal,lw=1.4))
ax.text(5,.67,'Institutional revision and audit',ha='center',va='center',fontsize=10,weight='bold',color=navy)
for x in (2.1,5,7.9):ax.add_patch(FancyArrowPatch((x,1.98),(5,1.08),arrowstyle='<->',mutation_scale=9,color='#8A9BAB',lw=1.1,connectionstyle='arc3,rad=0.09'))
ax.text(5,5.55,'Multiple decision centers',ha='center',fontsize=12,weight='bold',color=navy)
fig.tight_layout(pad=1.1);fig.savefig(out/'institutional_layers.pdf',bbox_inches='tight');plt.close(fig)

fig,ax=plt.subplots(figsize=(8.6,4.8));fig.patch.set_facecolor('white');ax.set_xlim(-.8,8.8);ax.set_ylim(-.4,5.0);ax.axis('off')
positions={'1':(1.0,3.8),'2':(6.5,3.8),'3':(3.75,.58)}
edges=[('1','2',r'$x_1\oplus x_2 = 0$',(3.75,4.35)),('2','3',r'$x_2\oplus x_3 = 0$',(6.0,1.95)),('3','1',r'$x_3\oplus x_1 = 1$',(1.4,1.95))]
for a,b,label,labpos in edges:
 xs=[positions[a][0],positions[b][0]];ys=[positions[a][1],positions[b][1]]
 ax.plot(xs,ys,c=blue,lw=1.65,zorder=1)
 ax.text(*labpos,label,fontsize=13,ha='center',va='center',color=navy)
for i,(x,y) in positions.items():
 ax.add_patch(Circle((x,y),.31,facecolor='#E9F4F2',edgecolor=teal,lw=1.4,zorder=2))
 ax.text(x,y,rf'$x_{i}$',ha='center',va='center',fontsize=13,color=navy,zorder=3)
ax.text(7.1,.65,r'Cycle parity: $0\oplus 0\oplus 1=1$',ha='center',fontsize=10,color=grey)
fig.tight_layout(pad=1.0);fig.savefig(out/'cycle_obstruction.pdf',bbox_inches='tight');plt.close(fig)
print('Generated',*[str(p) for p in out.glob('*.pdf')],sep='\n')
