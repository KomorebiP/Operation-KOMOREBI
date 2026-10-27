"""Four separate analytical figures. No generative imagery or empirical traces."""
from pathlib import Path
from fractions import Fraction
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'figures'
OUT.mkdir(exist_ok=True)


def canvas(w,h):
    fig=plt.figure(figsize=(w,h))
    ax=fig.add_axes((.04,.06,.92,.88))
    return fig,ax


def save(fig,name):
    fig.savefig(OUT/f'{name}.pdf',bbox_inches='tight',pad_inches=.12)
    fig.savefig(OUT/f'{name}.svg',bbox_inches='tight',pad_inches=.12)
    fig.savefig(OUT/f'{name}.png',dpi=180,bbox_inches='tight',pad_inches=.12)
    plt.close(fig)


def box(ax,x,y,w,h,text,fontsize=12,ls='-'):
    ax.add_patch(Rectangle((x-w/2,y-h/2),w,h,fill=False,linewidth=1.1,linestyle=ls))
    ax.text(x,y,text,ha='center',va='center',fontsize=fontsize,linespacing=1.5)


def arrow(ax,p,q,label=None,offset=(0,.16),ls='-'):
    ax.add_patch(FancyArrowPatch(p,q,arrowstyle='-|>',mutation_scale=13,linewidth=1.2,linestyle=ls))
    if label:
        ax.text((p[0]+q[0])/2+offset[0],(p[1]+q[1])/2+offset[1],label,
                ha='center',va='bottom',fontsize=10)


def main():
    data=json.loads((ROOT/'data'/'illustrations.json').read_text())
    fig,ax=canvas(8.8,4.4);ax.set(xlim=(0,9),ylim=(0,4.5));ax.axis('off')
    ax.text(4.5,4.12,'Different questions require different distinctions',ha='center',fontsize=15)
    box(ax,1.5,2.82,2.25,1.40,'Display + flip\n2 behavioral states\n'+r'$z=y$')
    box(ax,4.5,2.82,2.50,1.40,'Add the physical bit\n4 behavioral states\n'+r'$z=(y,\theta)$')
    box(ax,7.65,2.82,2.18,1.40,'Complete world\n8 hidden cases\n'+r'$(s,\theta,k)$',ls='--')
    arrow(ax,(2.64,2.82),(3.23,2.82))
    ax.text(3.0,3.62,'Reference\nmeasurement',ha='center',fontsize=10,linespacing=1.3)
    ax.plot([5.79,6.52],[2.82,2.82],linestyle='--',linewidth=1)
    ax.plot([6.09,6.23],[2.72,2.92],linewidth=1.4)
    ax.plot([6.09,6.23],[2.92,2.72],linewidth=1.4)
    ax.text(6.17,3.62,'No channel\nreveals k',ha='center',fontsize=10,linespacing=1.3)
    box(ax,4.5,.89,8.32,.98,'Reset reports the convention only after setting the physical bit to zero.\nRecovering the old bit also requires the retained old display.',fontsize=12)
    save(fig,'sensor_grounding')

    fig,ax=canvas(8.4,4.2);ax.set(xlim=(-.7,4.7),ylim=(-.9,2.1));ax.axis('off')
    for shift,title in [(0,r'$V_0$: earlier display 0'),(3,r'$V_1$: earlier display 1')]:
        for t,s in [(0,0),(0,1),(1,0),(1,1)]:
            ax.add_patch(Rectangle((shift+t-.36,s-.36),.72,.72,fill=False,linewidth=.9))
        ax.text(shift+.5,1.82,title,ha='center',fontsize=13)
        for t in (0,1):ax.text(shift+t,1.46,r'$\theta='+str(t)+'$',ha='center',fontsize=12)
        ax.add_patch(Rectangle((shift-.42,-.42),.84,1.84,fill=False,linestyle='--',linewidth=1))
    ax.scatter([0,1,3,4],[0,1,1,0],s=200,marker='o')
    ax.text(-.56,0,r'$s=0$',ha='right',va='center',fontsize=12)
    ax.text(-.56,1,r'$s=1$',ha='right',va='center',fontsize=12)
    ax.text(.5,-.67,r'After $\theta=0$: $s=0$',ha='center',fontsize=12)
    ax.text(3.5,-.67,r'After $\theta=0$: $s=1$',ha='center',fontsize=12)
    ax.text(2,1.00,'Same marginals\nDifferent association',ha='center',va='center',fontsize=11,linespacing=1.5)
    save(fig,'correction_association')

    fig=plt.figure(figsize=(8.4,4.3));ax=fig.add_axes((.13,.17,.83,.77))
    ns=[r['n'] for r in data['noisy_majority']]
    err=[float(Fraction(r['error'])) for r in data['noisy_majority']]
    ax.semilogy(ns,err,marker='o',linewidth=1.6)
    ax.set_xlabel('Fresh independent observations',fontsize=12)
    ax.set_ylabel('Error probability (log scale)',fontsize=12)
    ax.set_xticks(ns);ax.tick_params(labelsize=10)
    ax.grid(True,axis='y',linestyle=':',alpha=.45)
    ax.annotate(r'$e_1=1/4$',xy=(1,err[0]),xytext=(3,.26),fontsize=12,
                arrowprops={'arrowstyle':'->'})
    ax.annotate(r'$e_5=53/512$',xy=(5,err[2]),xytext=(7,.12),fontsize=12,
                arrowprops={'arrowstyle':'->'})
    ax.text(11,.055,'Every finite transcript is still\npossible in both worlds.',fontsize=12,linespacing=1.5)
    ax.set_ylim(min(err)*.70,.42)
    save(fig,'noisy_identification')

    fig,ax=canvas(8.8,4.8);ax.set(xlim=(0,9),ylim=(0,4.8));ax.axis('off')
    ax.add_patch(Rectangle((.20,.98),3.25,3.38,fill=False,linestyle='--',linewidth=1.0))
    ax.text(1.83,4.56,r'Calibrated inputs: $U=\mathrm{span}(e_1,e_2)$',ha='center',fontsize=11)
    box(ax,1.83,3.36,1.50,.80,r'$e_1$')
    box(ax,1.83,1.88,1.50,.80,r'$e_2$')
    box(ax,5.05,3.36,1.48,.80,r'$e_1$')
    box(ax,5.05,1.88,1.48,.80,r'$e_3$')
    arrow(ax,(2.58,3.36),(4.28,3.36),'Known',offset=(.45,.16))
    arrow(ax,(2.58,1.88),(4.28,1.88),'Known',offset=(.45,.16))
    arrow(ax,(5.80,3.36),(7.24,3.36))
    ax.text(7.70,3.36,r'$e_1$ forever',ha='center',va='center',fontsize=12)
    arrow(ax,(5.80,1.88),(7.10,2.37),'Unknown',offset=(.12,.25),ls='--')
    arrow(ax,(5.80,1.88),(7.10,1.35),ls='--')
    ax.text(7.50,2.37,'0',ha='center',va='center',fontsize=13)
    ax.text(7.50,1.35,r'$e_1$',ha='center',va='center',fontsize=13)
    ax.text(8.22,1.84,'Two valid\ncompletions',ha='center',va='center',fontsize=10,linespacing=1.4)
    ax.text(4.5,.36,'Known one-step domain: dimension 2.  Identifiable all-word core: dimension 1.',
            ha='center',fontsize=12)
    save(fig,'calibrated_core')
    print('Generated four analytical figures as PDF, SVG, and PNG.')


if __name__=='__main__':main()
