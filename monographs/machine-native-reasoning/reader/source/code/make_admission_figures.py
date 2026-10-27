"""Three analytical Matplotlib figures from the six admission examples.
Each figure is a separate chart. No fitted, sampled, or neural values are used.
"""
from pathlib import Path
from fractions import Fraction
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'

def save(fig,name):
    for ext in ('pdf','svg','png'):
        kwargs={'dpi':180} if ext=='png' else {}
        fig.savefig(OUT/f'{name}.{ext}',bbox_inches='tight',pad_inches=.12,**kwargs)
    plt.close(fig)

def main():
    DATA=json.loads((ROOT/'evidence/admission_examples.json').read_text())
    OUT.mkdir(exist_ok=True)
    fig,ax=plt.subplots(figsize=(8.7,3.8))
    for k,key in enumerate(('belief','average','detail')):
        x=[i+(k-1)*.24 for i in (0,1)]
        bars=ax.bar(x,[float(Fraction(v)) for v in DATA['packets'][key]],width=.22,label=key.title())
        for b,val in zip(bars,DATA['packets'][key]):
            ax.annotate(val,(b.get_x()+b.get_width()/2,b.get_height()),xytext=(0,5 if b.get_height()>=0 else -14),textcoords='offset points',ha='center',fontsize=11)
    ax.axhline(0,linewidth=.8)
    ax.set_xticks([0,1],['Coordinate 0','Coordinate 1']);ax.set_ylabel('Exact component value')
    ax.set_ylim(-.40,.94);ax.legend(loc='upper right',frameon=False,ncol=3)
    ax.set_title('Average + signed detail reconstructs the belief',pad=13)
    fig.tight_layout();save(fig,'signed_packets')

    fig,ax=plt.subplots(figsize=(8.7,3.8))
    ds=[Fraction(x) for x in DATA['rare_event']['masses']]
    xs=[float(x) for x in ds]
    ax.plot(xs,xs,'o-',label='Whole-law distance')
    ax.plot(xs,[1]*len(xs),'s--',label='Distance after the rare report')
    ax.set_xscale('log',base=2);ax.invert_xaxis();ax.set_xticks(xs,[str(x) for x in ds])
    ax.set_ylim(0,1.17);ax.set_xlabel('Probability of the specified rare report');ax.set_ylabel('Total variation distance')
    ax.legend(loc='center right',frameon=False)
    ax.set_title('Small global error does not bound every posterior',pad=13)
    fig.tight_layout();save(fig,'rare_history')

    fig,ax=plt.subplots(figsize=(9.2,5.9))
    ax.set(xlim=(0,10),ylim=(0,8.2));ax.axis('off')
    def node(x,y,w,h,text):
        ax.add_patch(FancyBboxPatch((x-w/2,y-h/2),w,h,boxstyle='round,pad=.10',fill=False,linewidth=1))
        ax.text(x,y,text,ha='center',va='center',fontsize=11,linespacing=1.3)
    def arrow(a,b,label=None,offset=(0,0)):
        ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','linewidth':1.2})
        if label:ax.text((a[0]+b[0])/2+offset[0],(a[1]+b[1])/2+offset[1],label,ha='center',va='center',fontsize=10)
    node(5,7.3,5.4,.8,'Uniform target prior. Take the first calibration.');
    node(5,5.8,5.4,1.05,'The reported bit now has probability 3/4.\nWith two reports left, calibrate again.')
    node(2.45,3.7,4.15,1.2,'Reports agree: probability 5/8\nFavored bit has posterior 9/10\nSTOP')
    node(7.55,3.7,4.15,1.2,'Reports disagree: probability 3/8\nTarget posterior returns to 1/2\nTake one final calibration')
    node(7.55,1.8,4.15,.9,'Third report gives posterior 3/4\nSTOP')
    arrow((5,6.8),(5,6.43));arrow((4.0,5.17),(2.45,4.4));arrow((6.0,5.17),(7.55,4.4));arrow((7.55,3.02),(7.55,2.36))
    ax.text(2.65,1.65,'Expected reports: 19/8\nExpected report charge: 19/160\nFinal error probability: 5/32',ha='center',va='center',fontsize=11,linespacing=1.6)
    ax.text(5,.35,'Expected charge + error = 11/40.  Each report costs 1/20.',ha='center',va='center',fontsize=11)
    fig.tight_layout();save(fig,'calibration_policy')
    print('Generated three analytical figures as PDF, SVG, and PNG.')

if __name__=='__main__':main()
