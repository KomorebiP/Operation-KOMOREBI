"""Shared exact-figure style for the Special Functions visual guide."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent
FIGURES = ROOT / 'figures'
COLORS = ['#226B66', '#C85D3A', '#5267A8', '#936A9E', '#BC8E35', '#407D9B']
INK = '#20303A'
MUTED = '#637680'
PALE = '#EAF2F1'

def apply_style():
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'axes.labelsize':13,
        'axes.titlesize':14,'xtick.labelsize':11,'ytick.labelsize':11,'legend.fontsize':11,
        'axes.prop_cycle':matplotlib.cycler(color=COLORS),'axes.spines.top':False,
        'axes.spines.right':False,'axes.edgecolor':MUTED,'text.color':INK,
        'axes.labelcolor':INK,'xtick.color':MUTED,'ytick.color':MUTED,
        'figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white',
        'pdf.fonttype':42,'ps.fonttype':42,'lines.linewidth':2.1,
        'grid.alpha':0.2,'grid.linewidth':0.6})

def save_figure(fig, stem):
    FIGURES.mkdir(parents=True,exist_ok=True)
    fig.savefig(FIGURES/(stem+'.pdf'),bbox_inches='tight',pad_inches=0.12)
    fig.savefig(FIGURES/(stem+'.png'),dpi=170,bbox_inches='tight',pad_inches=0.12)
    plt.close(fig)

def finish(fig, stem):
    save_figure(fig, stem)

def mobius_sieve(n):
    """Exact integer Möbius values for 0..n using a linear prime sieve."""
    mu=np.zeros(n+1,dtype=np.int8);mu[1]=1
    composite=np.zeros(n+1,dtype=bool);primes=[]
    for i in range(2,n+1):
        if not composite[i]:primes.append(i);mu[i]=-1
        for p in primes:
            j=i*p
            if j>n:break
            composite[j]=True
            if i%p==0:mu[j]=0;break
            mu[j]=-mu[i]
    return mu

apply_style()
