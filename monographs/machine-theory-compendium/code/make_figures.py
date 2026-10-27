"""Analytical editorial diagrams; Matplotlib defaults, no generated pictorial assets."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures';OUT.mkdir(exist_ok=True)
def box(ax,x,y,w,h,head,body=None):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.04',fill=False,linewidth=1.1))
    if body:
        ax.text(x+w/2,y+h*.68,head,ha='center',va='center',fontsize=11.5,fontweight='bold')
        ax.text(x+w/2,y+h*.28,body,ha='center',va='center',fontsize=9.5)
    else:ax.text(x+w/2,y+h/2,head,ha='center',va='center',fontsize=11)
def arrow(ax,a,b,label=None):
    ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':1.2})
    if label:ax.text((a[0]+b[0])/2,(a[1]+b[1])/2+.16,label,ha='center',fontsize=9)
def save(fig,name):
    for ext in ('pdf','svg','png'):
        fig.savefig(OUT/f'{name}.{ext}',bbox_inches='tight',pad_inches=.12,dpi=160)
    plt.close(fig)
def main():
    fig,ax=plt.subplots(figsize=(10,6.2));ax.set(xlim=(0,10),ylim=(0,6.2));ax.axis('off')
    rows=[('Evidence and grounding','GA · accessible distinctions and initialization'),('Representation and prediction','SR / SU / LSM / PRIQ · closure and typed uncertainty'),('Executable methods and correction','MU / OSL / NEU / CBI · operations and recipients'),('Discovery and retained knowledge','SII / AVOC / PPT / KPP · acquisition, cost and evidence'),('Relational and institutional organization','SRWT / MS · shared state, authority and continuity')]
    for i,(h,b) in enumerate(rows):
        y=5.12-i*1.05;box(ax,1,y,8,.78,h,b)
        if i<4:arrow(ax,(5,y-.04),(5,y-.26))
    ax.text(5,.05,'PRISM: execution target   |   Circuit Obstructions: scoped limits',ha='center',fontsize=10)
    save(fig,'connected_layers')
    dat=json.loads((ROOT/'validation'/'connection_checks.json').read_text())['resource_example']
    fig,ax=plt.subplots(figsize=(8.7,4.3))
    vals=dat['savings'];labs=['Reads + additions\n+ comparisons','Reads + comparisons','Comparisons only']
    bars=ax.bar(labs,vals,width=.58)
    ax.axhline(0,linewidth=.8)
    ax.set_ylabel('Old minus new priced work')
    ax.set_title('One workflow can save or lose under different prices',pad=18)
    ax.set_ylim(-2250,1800)
    for bar,v in zip(bars,vals):ax.annotate(f'{v:+,}',(bar.get_x()+bar.get_width()/2,v),xytext=(0,8 if v>=0 else -16),textcoords='offset points',ha='center',fontsize=12,fontweight='bold')
    fig.text(.5,.01,'Declared event vector: (1,552 reads, 1,552 additions, −1,868 comparisons). Not CPU timings.',ha='center',fontsize=9)
    fig.subplots_adjust(bottom=.22,top=.82,left=.14,right=.97)
    save(fig,'resource_prices')
    fig,ax=plt.subplots(figsize=(10,5.5));ax.set(xlim=(0,10),ylim=(0,5.5));ax.axis('off')
    box(ax,.18,3.7,2.6,1.05,'World (b, θ, u)','u is irrelevant to this contract')
    box(ax,3.6,4.12,2.45,.9,'Agent A: read s','s = b XOR θ')
    box(ax,3.6,2.55,2.45,.9,'Agent B: calibrate','receives θ')
    box(ax,7,3.32,2.75,1.12,'Joint repair information','b = s XOR θ')
    box(ax,7,.85,2.75,1.15,'Action admission','request R_b; check authority')
    box(ax,.55,.65,5.5,1.15,'Retain the association','Current marginals can erase a future correction')
    arrow(ax,(2.85,4.45),(3.52,4.57));arrow(ax,(2.8,3.82),(3.53,3.05))
    arrow(ax,(6.12,4.56),(6.9,4.14));arrow(ax,(6.12,3),(6.9,3.68))
    arrow(ax,(8.4,3.25),(8.4,2.08))
    ax.text(8.58,2.72,'decision',ha='left',fontsize=9)
    ax.text(5,5.35,'Supplied finite semantics; functional roles, not measured neural modules',ha='center',fontsize=10)
    ax.text(3.8,2.12,'Messages need current scope and provenance, not only a data bit.',ha='center',fontsize=9.5)
    save(fig,'sensor_interfaces')
    fig,ax=plt.subplots(figsize=(10,5.2));ax.set(xlim=(0,10),ylim=(0,5.2));ax.axis('off')
    box(ax,.3,3.65,3.8,.9,'Unchanged sensor model','normal reading and calibration')
    box(ax,5.8,3.65,3.8,.9,'Revised repair language','new repair succeeds in all cases')
    box(ax,.3,1.8,3.8,.9,'Display predictor','remains applicable')
    box(ax,5.8,1.8,3.8,.9,'Old identification requirement','application is stale')
    box(ax,5.8,.15,3.8,.9,'Old performance comparison','must be recomputed')
    arrow(ax,(2.2,3.55),(2.2,2.82));arrow(ax,(7.7,3.55),(7.7,2.82));arrow(ax,(7.7,1.7),(7.7,1.17))
    ax.text(2.2,.8,'A theorem can remain true\nwhile its old application fails.',ha='center',fontsize=11)
    ax.text(5,4.95,'Invalidate the affected dependencies, not every result',ha='center',fontsize=13,fontweight='bold')
    save(fig,'selective_invalidation')
    print('Generated four analytical figures as PDF, SVG and PNG.')
if __name__=='__main__':main()
